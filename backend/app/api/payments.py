"""Paystack-backed payment endpoints (S11).

Two endpoints:

  POST /payments/initialize   auth   create a pending Payment row,
                                     return reference + public key.
  POST /payments/verify       auth   confirm via Paystack and update
                                     the Payment row (idempotent).

Money is never trusted from the client. The amount is looked up
server-side via :mod:`app.services.fees`. On verify, the amount Paystack
confirms is compared to the server-recorded amount; any mismatch
transitions the row to ``failed`` and access is not granted.
"""

import json
import secrets
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, is_owner
from app.core.config import settings
from app.db.session import get_db
from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.models.user import User
from app.schemas.payment import (
    PaymentInitializeRequest,
    PaymentInitializeResponse,
    PaymentResponse,
    PaymentVerifyRequest,
)
from app.services import paystack
from app.services.fees import UnknownTargetError, compute_amount_kobo
from app.services.paystack import PaystackError

router = APIRouter(prefix="/payments", tags=["payments"])


def _make_reference() -> str:
    """Server-generated, unique payment reference."""
    return f"TCS-{secrets.token_urlsafe(12)}"


def _apply_paystack_result(payment: Payment, body: dict[str, Any]) -> None:
    """Update a Payment from a Paystack verify-response or webhook body.

    Idempotent: if ``payment.status`` is already ``success`` this is a
    no-op (no DB writes, no timestamp churn, no raw_response overwrite).

    Otherwise: sets ``verified_at`` to now, stores the raw response, and
    transitions ``status``:
      - Paystack reports ``data.status == "success"`` AND amount matches
        the server-recorded ``amount_kobo`` → ``success``.
      - Anything else (Paystack-failed, partial pay, missing fields) →
        ``failed``. Access is never granted on ``failed``.
    """
    if payment.status is PaymentStatus.success:
        return

    data = body.get("data") or {}
    paystack_status = data.get("status")
    paystack_amount = data.get("amount")

    payment.raw_response = body
    payment.verified_at = datetime.now(tz=timezone.utc)

    if (
        paystack_status == "success"
        and isinstance(paystack_amount, int)
        and paystack_amount == payment.amount_kobo
    ):
        payment.status = PaymentStatus.success
    else:
        payment.status = PaymentStatus.failed


# ─────────────────────────────────────────────────────────────
# POST /payments/initialize
# ─────────────────────────────────────────────────────────────


@router.post(
    "/initialize",
    response_model=PaymentInitializeResponse,
    status_code=status.HTTP_201_CREATED,
)
def initialize_payment(
    payload: PaymentInitializeRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentInitializeResponse:
    """Create a pending Payment row and return data for the Paystack widget.

    Steps:
      1. Look up the canonical amount from the server-side fee table.
         The client cannot supply the amount.
      2. Insert a Payment row with status=pending and a fresh reference.
      3. Return reference + amount + public_key + payer_email — exactly
         what the Paystack inline widget needs to set up.
    """
    try:
        amount_kobo = compute_amount_kobo(payload.purpose, payload.target)
    except UnknownTargetError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    payment = Payment(
        payer_id=current_user.id,
        reference=_make_reference(),
        amount_kobo=amount_kobo,
        purpose=payload.purpose,
        target=payload.target if payload.purpose is PaymentPurpose.programme
        else None,
        status=PaymentStatus.pending,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentInitializeResponse(
        reference=payment.reference,
        amount_kobo=payment.amount_kobo,
        public_key=settings.PAYSTACK_PUBLIC_KEY,
        payer_email=current_user.email,
        purpose=payment.purpose,
        target=payment.target,
    )


# ─────────────────────────────────────────────────────────────
# POST /payments/verify
# ─────────────────────────────────────────────────────────────


_GENERIC_VERIFY_FAILURE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="That payment could not be verified.",
)


@router.post(
    "/verify",
    response_model=PaymentResponse,
)
def verify_payment(
    payload: PaymentVerifyRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Payment:
    """Verify a pending Payment with Paystack and update its status.

    - Looks up the Payment by reference; 404 if unknown.
    - 403 if the current user isn't the payer.
    - If already ``success``: idempotent — returns the cached state
      without re-contacting Paystack.
    - Otherwise calls Paystack's verify API. On
      Paystack-success + amount-match: status → ``success``, raw
      response stored. On amount-mismatch or Paystack-failed:
      status → ``failed``.
    """
    payment = (
        db.query(Payment)
        .filter(Payment.reference == payload.reference)
        .one_or_none()
    )
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown reference.",
        )
    if not is_owner(current_user, payment.payer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )

    # Idempotency: don't re-hit Paystack on already-success rows.
    if payment.status is PaymentStatus.success:
        return payment

    try:
        body = paystack.verify_transaction(payment.reference)
    except PaystackError:
        # Can't reach Paystack / Paystack rejected the call. Don't
        # leak why; just signal failure to the caller.
        raise _GENERIC_VERIFY_FAILURE

    _apply_paystack_result(payment, body)
    db.commit()
    db.refresh(payment)
    return payment


# ─────────────────────────────────────────────────────────────
# POST /payments/webhook/paystack  (S12)
# ─────────────────────────────────────────────────────────────


@router.post("/webhook/paystack")
async def paystack_webhook(
    request: Request, db: Session = Depends(get_db)
) -> dict:
    """Receive Paystack webhook events (the authoritative status source).

    The synchronous /payments/verify call from the frontend can be
    dropped (user closes tab between charge and verify). The webhook
    cannot — Paystack retries with exponential backoff until we 200.
    So treating the webhook as authoritative makes the whole flow
    self-healing.

    Pipeline:
      1. Read raw body bytes (NOT the parsed Pydantic body — the
         signature is over the bytes Paystack sent).
      2. HMAC-SHA512 against PAYSTACK_SECRET_KEY; reject 401 on
         mismatch.
      3. Parse JSON; reject 400 on malformed.
      4. If event != 'charge.success' → 200 (ack, ignore).
      5. Look up Payment by reference; if unknown → 200 (ack, ignore).
      6. Apply ``_apply_paystack_result`` (idempotent on success).
      7. Always 200 so Paystack doesn't keep retrying.
    """
    body_bytes = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    if not paystack.verify_webhook_signature(body_bytes, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature.",
        )

    try:
        body = json.loads(body_bytes)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body.",
        )

    if body.get("event") != "charge.success":
        return {"ok": True}

    reference = (body.get("data") or {}).get("reference")
    if not reference:
        return {"ok": True}

    payment = (
        db.query(Payment).filter(Payment.reference == reference).one_or_none()
    )
    if payment is None:
        # Paystack could replay an old event we never created a row for;
        # or it could be a delivery for a different tenant's reference.
        # Either way: acknowledge and move on.
        return {"ok": True}

    _apply_paystack_result(payment, body)
    db.commit()
    return {"ok": True}
