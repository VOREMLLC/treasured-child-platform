"""Tests for /payments/initialize and /payments/verify (S11)."""

from unittest.mock import patch

import pytest

from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.models.user import User, UserRole, UserStatus
from app.services.fees import FEES_KOBO, PROGRAMME_PRICES_KOBO
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
def payer_client(client, payer):
    login = client.post(
        "/auth/login",
        json={"email": "payer@example.com", "password": "payer-pw-12345"},
    )
    assert login.status_code == 200
    return client


def _paystack_success(reference: str, amount: int) -> dict:
    """Shape Paystack returns on a successful verify."""
    return {
        "status": True,
        "message": "Verification successful",
        "data": {
            "status": "success",
            "amount": amount,
            "reference": reference,
            "paid_at": "2026-06-11T12:00:00Z",
            "channel": "card",
            "currency": "NGN",
        },
    }


# ─────────────────────────────────────────────────────────────
# /payments/initialize
# ─────────────────────────────────────────────────────────────


def test_initialize_without_session_returns_401(client):
    response = client.post(
        "/payments/initialize", json={"purpose": "fees"}
    )
    assert response.status_code == 401


def test_initialize_fees_creates_pending_payment_with_canonical_amount(
    payer_client, db_session, payer
):
    response = payer_client.post(
        "/payments/initialize", json={"purpose": "fees"}
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["amount_kobo"] == FEES_KOBO
    assert body["payer_email"] == "payer@example.com"
    assert body["purpose"] == "fees"
    assert body["target"] is None
    assert body["reference"].startswith("TCS-")

    rows = db_session.query(Payment).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.payer_id == payer.id
    assert row.amount_kobo == FEES_KOBO
    assert row.status is PaymentStatus.pending
    assert row.purpose is PaymentPurpose.fees


def test_initialize_programme_uses_programme_price(
    payer_client, db_session
):
    response = payer_client.post(
        "/payments/initialize",
        json={"purpose": "programme", "target": "bece-prep"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["amount_kobo"] == PROGRAMME_PRICES_KOBO["bece-prep"]
    assert body["target"] == "bece-prep"

    row = db_session.query(Payment).one()
    assert row.target == "bece-prep"
    assert row.amount_kobo == PROGRAMME_PRICES_KOBO["bece-prep"]


def test_initialize_programme_without_target_returns_422(payer_client):
    response = payer_client.post(
        "/payments/initialize", json={"purpose": "programme"}
    )
    assert response.status_code == 422


def test_initialize_programme_with_unknown_target_returns_422(
    payer_client, db_session
):
    response = payer_client.post(
        "/payments/initialize",
        json={"purpose": "programme", "target": "does-not-exist"},
    )
    assert response.status_code == 422
    # No row written.
    assert db_session.query(Payment).count() == 0


def test_initialize_ignores_client_supplied_amount(
    payer_client, db_session
):
    """Even if the client sneaks an 'amount_kobo' in, the server overwrites."""
    response = payer_client.post(
        "/payments/initialize",
        json={"purpose": "fees", "amount_kobo": 100},  # client lie
    )
    assert response.status_code == 201
    body = response.json()
    assert body["amount_kobo"] == FEES_KOBO  # server price, not 100

    row = db_session.query(Payment).one()
    assert row.amount_kobo == FEES_KOBO


# ─────────────────────────────────────────────────────────────
# /payments/verify
# ─────────────────────────────────────────────────────────────


def test_verify_unknown_reference_returns_404(payer_client):
    response = payer_client.post(
        "/payments/verify", json={"reference": "TCS-does-not-exist"}
    )
    assert response.status_code == 404


@patch("app.api.payments.paystack.verify_transaction")
def test_verify_with_paystack_success_marks_payment_success(
    mock_verify, payer_client, db_session
):
    init = payer_client.post(
        "/payments/initialize", json={"purpose": "fees"}
    )
    ref = init.json()["reference"]
    mock_verify.return_value = _paystack_success(ref, FEES_KOBO)

    response = payer_client.post(
        "/payments/verify", json={"reference": ref}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["verified_at"] is not None
    mock_verify.assert_called_once_with(ref)

    row = db_session.query(Payment).filter(Payment.reference == ref).one()
    assert row.status is PaymentStatus.success
    assert row.raw_response["data"]["amount"] == FEES_KOBO


@patch("app.api.payments.paystack.verify_transaction")
def test_verify_with_amount_mismatch_marks_payment_failed(
    mock_verify, payer_client, db_session
):
    init = payer_client.post(
        "/payments/initialize", json={"purpose": "fees"}
    )
    ref = init.json()["reference"]
    # Server expects FEES_KOBO but Paystack reports something smaller.
    mock_verify.return_value = _paystack_success(ref, amount=100)

    response = payer_client.post(
        "/payments/verify", json={"reference": ref}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"

    row = db_session.query(Payment).filter(Payment.reference == ref).one()
    assert row.status is PaymentStatus.failed


@patch("app.api.payments.paystack.verify_transaction")
def test_verify_is_idempotent_on_already_success(
    mock_verify, payer_client, db_session
):
    init = payer_client.post(
        "/payments/initialize", json={"purpose": "fees"}
    )
    ref = init.json()["reference"]
    mock_verify.return_value = _paystack_success(ref, FEES_KOBO)

    first = payer_client.post(
        "/payments/verify", json={"reference": ref}
    )
    assert first.status_code == 200
    assert first.json()["status"] == "success"
    assert mock_verify.call_count == 1

    second = payer_client.post(
        "/payments/verify", json={"reference": ref}
    )
    assert second.status_code == 200
    assert second.json()["status"] == "success"
    # The mock is NOT called a second time — idempotent.
    assert mock_verify.call_count == 1
