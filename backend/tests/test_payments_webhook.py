"""Tests for /payments/webhook/paystack (S12)."""

import hashlib
import hmac
import json
from typing import Optional

import pytest

from app.core.config import settings
from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.models.user import User, UserRole, UserStatus
from app.services import email as email_service
from app.services.fees import FEES_KOBO
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def payer(db_session):
    user = User(
        email="payer@example.com",
        name="Payer",
        password_hash=hash_password("payer-pw-12345"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def pending_payment(db_session, payer):
    payment = Payment(
        payer_id=payer.id,
        reference="TCS-webhook-test-ref",
        amount_kobo=FEES_KOBO,
        purpose=PaymentPurpose.fees,
        target=None,
        status=PaymentStatus.pending,
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    return payment


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _sign(body_bytes: bytes) -> str:
    return hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        body_bytes,
        hashlib.sha512,
    ).hexdigest()


def _build_event_body(
    reference: str,
    amount: int,
    paystack_status: str = "success",
    event: str = "charge.success",
) -> dict:
    return {
        "event": event,
        "data": {
            "id": 302961,
            "reference": reference,
            "status": paystack_status,
            "amount": amount,
            "currency": "NGN",
            "channel": "card",
            "paid_at": "2026-06-11T12:00:00Z",
        },
    }


def _post_webhook(
    client,
    body_dict: dict,
    signature_override: Optional[str] = None,
):
    body_bytes = json.dumps(body_dict).encode("utf-8")
    signature = (
        signature_override
        if signature_override is not None
        else _sign(body_bytes)
    )
    return client.post(
        "/payments/webhook/paystack",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "x-paystack-signature": signature,
        },
    )


# ─────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────


def test_webhook_valid_signature_charge_success_marks_payment_success(
    client, db_session, pending_payment
):
    body = _build_event_body(pending_payment.reference, FEES_KOBO)

    response = _post_webhook(client, body)

    assert response.status_code == 200
    assert response.json() == {"ok": True}

    db_session.refresh(pending_payment)
    assert pending_payment.status is PaymentStatus.success
    assert pending_payment.verified_at is not None
    assert pending_payment.raw_response["event"] == "charge.success"


def test_webhook_invalid_signature_returns_401(
    client, db_session, pending_payment
):
    body = _build_event_body(pending_payment.reference, FEES_KOBO)

    response = _post_webhook(client, body, signature_override="0" * 128)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid signature."}

    db_session.refresh(pending_payment)
    assert pending_payment.status is PaymentStatus.pending


def test_webhook_missing_signature_header_returns_401(
    client, db_session, pending_payment
):
    body_bytes = json.dumps(
        _build_event_body(pending_payment.reference, FEES_KOBO)
    ).encode()

    response = client.post(
        "/payments/webhook/paystack",
        content=body_bytes,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 401
    db_session.refresh(pending_payment)
    assert pending_payment.status is PaymentStatus.pending


def test_webhook_idempotent_on_replay(
    client, db_session, pending_payment
):
    """Sending the same event twice doesn't double-update anything."""
    body = _build_event_body(pending_payment.reference, FEES_KOBO)

    first = _post_webhook(client, body)
    assert first.status_code == 200
    db_session.refresh(pending_payment)
    assert pending_payment.status is PaymentStatus.success
    verified_at_after_first = pending_payment.verified_at

    second = _post_webhook(client, body)
    assert second.status_code == 200
    db_session.refresh(pending_payment)
    assert pending_payment.status is PaymentStatus.success
    # The idempotency guarantee: verified_at is NOT re-touched on the
    # second event, so no audit-trail flapping either.
    assert pending_payment.verified_at == verified_at_after_first


def test_webhook_amount_mismatch_marks_payment_failed(
    client, db_session, pending_payment
):
    body = _build_event_body(pending_payment.reference, amount=100)

    response = _post_webhook(client, body)

    assert response.status_code == 200
    db_session.refresh(pending_payment)
    assert pending_payment.status is PaymentStatus.failed


def test_webhook_unknown_reference_acknowledged_no_change(
    client, db_session, pending_payment
):
    body = _build_event_body("TCS-not-in-db", FEES_KOBO)

    response = _post_webhook(client, body)

    # Always 200 so Paystack doesn't retry.
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    db_session.refresh(pending_payment)
    assert pending_payment.status is PaymentStatus.pending


def test_webhook_non_charge_success_event_acknowledged_no_change(
    client, db_session, pending_payment
):
    """Events other than charge.success are 200-acked and ignored."""
    body = _build_event_body(
        pending_payment.reference,
        FEES_KOBO,
        event="charge.dispute.create",
    )

    response = _post_webhook(client, body)

    assert response.status_code == 200
    db_session.refresh(pending_payment)
    assert pending_payment.status is PaymentStatus.pending


# ─────────────────────────────────────────────────────────────
# S13 — receipt email behavior on webhook path
# ─────────────────────────────────────────────────────────────


def test_webhook_success_sends_one_receipt_email(
    client, db_session, pending_payment, payer
):
    body = _build_event_body(pending_payment.reference, FEES_KOBO)

    _post_webhook(client, body)

    outbox = email_service.get_outbox()
    assert len(outbox) == 1
    assert outbox[0].to == payer.email
    assert pending_payment.reference in outbox[0].body


def test_webhook_replayed_does_not_send_duplicate_receipt(
    client, db_session, pending_payment
):
    body = _build_event_body(pending_payment.reference, FEES_KOBO)

    _post_webhook(client, body)
    assert len(email_service.get_outbox()) == 1

    _post_webhook(client, body)
    # Still exactly one — replay is idempotent on email too.
    assert len(email_service.get_outbox()) == 1
