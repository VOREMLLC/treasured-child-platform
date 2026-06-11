"""Tests for /auth/forgot-password and /auth/reset-password (S9)."""

import re
from datetime import datetime, timedelta, timezone

import pytest

from app.models.password_reset import PasswordResetToken
from app.models.user import User, UserRole, UserStatus
from app.services import email as email_service
from app.services.security import (
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)


# Capture token from the email body, e.g.
# "...localhost:3000/reset-password?token=<43chars>\n..."
_TOKEN_RE = re.compile(r"reset-password\?token=([A-Za-z0-9_\-]+)")


@pytest.fixture
def known_user(db_session):
    user = User(
        email="active@example.com",
        name="Active User",
        password_hash=hash_password("old-password"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ─────────────────────────────────────────────────────────────
# /auth/forgot-password
# ─────────────────────────────────────────────────────────────


def test_forgot_password_for_known_email_sends_email_and_creates_token(
    client, db_session, known_user
):
    response = client.post(
        "/auth/forgot-password",
        json={"email": "active@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "detail": (
            "If that email is registered, a reset link is on its way."
        ),
    }

    outbox = email_service.get_outbox()
    assert len(outbox) == 1
    assert outbox[0].to == "active@example.com"
    assert "reset-password?token=" in outbox[0].body

    rows = db_session.query(PasswordResetToken).all()
    assert len(rows) == 1
    assert rows[0].user_id == known_user.id
    assert rows[0].consumed_at is None


def test_forgot_password_for_unknown_email_returns_identical_response(
    client, db_session
):
    response = client.post(
        "/auth/forgot-password",
        json={"email": "nobody@example.com"},
    )

    assert response.status_code == 200
    # Body must be byte-for-byte identical to the known-email case so
    # an attacker can't tell from response alone whether the email is
    # registered.
    assert response.json() == {
        "ok": True,
        "detail": (
            "If that email is registered, a reset link is on its way."
        ),
    }

    # No email sent, no token row written.
    assert email_service.get_outbox() == []
    assert db_session.query(PasswordResetToken).count() == 0


# ─────────────────────────────────────────────────────────────
# /auth/reset-password
# ─────────────────────────────────────────────────────────────


def test_reset_with_valid_token_changes_password_and_consumes_token(
    client, db_session, known_user
):
    # Trigger the reset email to obtain a token via the stubbed sender.
    client.post(
        "/auth/forgot-password",
        json={"email": "active@example.com"},
    )
    body = email_service.get_outbox()[0].body
    match = _TOKEN_RE.search(body)
    assert match is not None
    plaintext_token = match.group(1)

    # Reset.
    response = client.post(
        "/auth/reset-password",
        json={"token": plaintext_token, "new_password": "brand-new-password"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # The user's password_hash now verifies the NEW password and not the old.
    db_session.refresh(known_user)
    assert verify_password(known_user.password_hash, "brand-new-password")
    assert not verify_password(known_user.password_hash, "old-password")

    # The token row is now consumed.
    row = db_session.query(PasswordResetToken).one()
    assert row.consumed_at is not None


def test_reset_with_consumed_token_returns_generic_400(
    client, db_session, known_user
):
    client.post(
        "/auth/forgot-password",
        json={"email": "active@example.com"},
    )
    plaintext_token = _TOKEN_RE.search(
        email_service.get_outbox()[0].body
    ).group(1)

    # First use succeeds.
    first = client.post(
        "/auth/reset-password",
        json={"token": plaintext_token, "new_password": "first-new-password"},
    )
    assert first.status_code == 200

    # Second use fails generically.
    second = client.post(
        "/auth/reset-password",
        json={"token": plaintext_token, "new_password": "second-attempt-ok"},
    )
    assert second.status_code == 400
    assert second.json() == {
        "detail": "That reset link is invalid or has expired."
    }


def test_reset_with_expired_token_returns_generic_400(
    client, db_session, known_user
):
    # Insert an expired token directly.
    plaintext = generate_reset_token()
    row = PasswordResetToken(
        user_id=known_user.id,
        token_hash=hash_reset_token(plaintext),
        expires_at=datetime.now(tz=timezone.utc) - timedelta(minutes=1),
    )
    db_session.add(row)
    db_session.commit()

    response = client.post(
        "/auth/reset-password",
        json={"token": plaintext, "new_password": "doesnt-matter-here"},
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "That reset link is invalid or has expired."
    }


def test_reset_with_unknown_token_returns_generic_400(client, db_session):
    response = client.post(
        "/auth/reset-password",
        json={
            "token": "not-a-real-token-just-random-chars",
            "new_password": "doesnt-matter-here",
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "That reset link is invalid or has expired."
    }
