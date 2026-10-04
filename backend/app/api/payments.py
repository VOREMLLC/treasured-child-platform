"""Paystack-backed payment endpoints (S11 + S19).

Two endpoints:

  POST /payments/initialize   auth   create a pending Payment row,
                                     return reference + public key.
  POST /payments/verify       auth   confirm via Paystack and update
                                     the Payment row (idempotent).

Money is never trusted from the client. The amount is looked up
server-side via :mod:`app.services.fees`. On verify, the amount Paystack
confirms is compared to the server-recorded amount; any mismatch
transitions the row to ``failed`` and access is not granted.

S19 addition: when a programme payment transitions to ``success``
(either via verify or webhook), ``_auto_enrol`` creates the Enrolment
server-side so the learner immediately has access without a second
client call. The insert is wrapped in a savepoint so an IntegrityError
on the unique(learner_id, course_id) constraint (from a concurrent
verify + webhook) rolls back only the enrolment insert and leaves the
payment status update intact.
"""

import json
import secrets
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
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
from app.services import email as email_service
from app.services import paystack
from app.services.fees import (
    UnknownTargetError,
    compute_amount_kobo,
    get_programme_label,
)
from app.services.paystack import PaystackError

router = APIRouter(prefix="/payments", tags=["payments"])


def _make_reference() -> str:
    """Server-generated, unique payment reference."""
    return f"TCS-{secrets.token_urlsafe(12)}"


def _has_published_course(slug: Optional[str], db: Session) -> bool:
    from app.models.course import Course

    if not slug:
        return False
    return (
        db.query(Course.id)
        .filter(Course.slug == slug)
        .filter(Course.published.is_(True))
        .first()
        is not None
    )


def _auto_enrol(payment: Payment, db: Session) -> None:
    """Create an Enrolment when a programme payment succeeds (S19).

    Called exactly once per payment, inside ``_apply_paystack_result``,
    at the moment ``status`` transitions from non-success to ``success``.
    The savepoint means an IntegrityError on the unique(learner_id,
    course_id) constraint rolls back only this insert and leaves the
    enclosing transaction (the payment status update) untouched.
    """
    from app.models.course import Course
    from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus

    if not payment.target:
        return

    course = (
        db.query(Course)
        .filter(Course.slug == payment.target)
        .filter(Course.published.is_(True))
        .first()
    )
    if course is None:
        return

    sp = db.begin_nested()  # savepoint — isolates this insert
    try:
        row = Enrolment(
            learner_id=payment.payer_id,
            course_id=course.id,
            status=EnrolmentStatus.active,
            source=EnrolmentSource.paid,
        )
        db.add(row)
        sp.commit()
    except IntegrityError:
        # Already enrolled (concurrent verify + webhook race).
        sp.rollback()


def _apply_paystack_result(
    payment: Payment, body: dict[str, Any], db: Session
) -> None:
    """Update a Payment from a Paystack verify-response or webhook body.

    Idempotent: if ``payment.status`` is already ``success`` this is a
    no-op (no DB writes, no timestamp churn, no raw_response overwrite,
    no receipt email).

    Otherwise: sets ``verified_at`` to now, stores the raw response, and
    transitions ``status``:
      - Paystack reports ``data.status == "success"`` AND amount matches
        the server-recorded ``amount_kobo`` → ``success``. A receipt
        email is sent (S13).
      - Anything else (Paystack-failed, partial pay, missing fields) →
        ``failed``. Access is never granted on ``failed`` and no email
        is sent.
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
        and data.get("currency") == "NGN"
    ):
        payment.status = PaymentStatus.success
        _send_receipt(payment, db)
        if payment.purpose is PaymentPurpose.programme:
            _auto_enrol(payment, db)
    else:
        payment.status = PaymentStatus.failed


def _send_receipt(payment: Payment, db: Session) -> None:
    """Send one receipt email to the payer.

    Called exactly once per Payment, at the moment ``status``
    transitions from ``pending`` / ``failed`` to ``success``. Because
    :func:`_apply_paystack_result` short-circuits on already-success,
    no duplicate receipt is ever sent for the same Payment row.

    A missing User (shouldn't happen — FK is RESTRICT) silently skips
    the email rather than crashing the verify/webhook path.
    """
    user = db.get(User, payment.payer_id)
    if user is None:
        return

    naira = f"₦{payment.amount_kobo / 100:,.2f}"  # ₦
    if payment.purpose is PaymentPurpose.fees:
        purpose_label = "Term fees"
    else:
        programme_name = get_programme_label(payment.target or "")
        purpose_label = f"Programme: {programme_name}"

    date_str = (
        payment.verified_at.strftime("%d %b %Y, %H:%M UTC")
        if payment.verified_at
        else "—"
    )

    email_service.send_email(
        to=user.email,
        subject=f"Treasured Child School — receipt for {naira}",
        body=(
            f"Hi {user.name},\n\n"
            f"Thank you for your payment.\n\n"
            f"  Amount:    {naira}\n"
            f"  For:       {purpose_label}\n"
            f"  Reference: {payment.reference}\n"
            f"  Date:      {date_str}\n\n"
            f"Keep this reference for your records.\n\n"
            f"— Treasured Child School\n"
        ),
    )


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

    # A priced programme with no published course would take the parent's
    # money and enrol them in nothing (_auto_enrol finds no course).
    if payload.purpose is PaymentPurpose.programme and not _has_published_course(
        payload.target, db
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This programme is not open for enrolment yet.",
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

    _apply_paystack_result(payment, body, db)
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

    _apply_paystack_result(payment, body, db)
    db.commit()
    return {"ok": True}
