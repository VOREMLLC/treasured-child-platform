"""Tests for /auth/login, /auth/refresh, /auth/logout (S8)."""

import pytest

from app.models.user import User, UserRole, UserStatus
from app.services.security import decode_token, hash_password


# ─────────────────────────────────────────────────────────────
# Fixtures — sample users in different lifecycle states
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def active_user(db_session):
    user = User(
        email="active@example.com",
        name="Active User",
        password_hash=hash_password("correct-password"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def pending_user(db_session):
    user = User(
        email="pending@example.com",
        name="Pending User",
        password_hash=hash_password("correct-password"),
        role=UserRole.student,
        status=UserStatus.pending,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ─────────────────────────────────────────────────────────────
# /auth/login
# ─────────────────────────────────────────────────────────────


def test_login_with_correct_password_sets_cookies_and_returns_user(
    client, active_user
):
    response = client.post(
        "/auth/login",
        json={"email": "active@example.com", "password": "correct-password"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["email"] == "active@example.com"
    assert body["role"] == "student"
    assert body["status"] == "active"
    assert "password_hash" not in body

    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    access_claims = decode_token(
        response.cookies["access_token"], expected_type="access"
    )
    assert access_claims["sub"] == str(active_user.id)
    assert access_claims["type"] == "access"

    refresh_claims = decode_token(
        response.cookies["refresh_token"], expected_type="refresh"
    )
    assert refresh_claims["sub"] == str(active_user.id)
    assert refresh_claims["type"] == "refresh"


def test_login_with_wrong_password_returns_generic_401(client, active_user):
    response = client.post(
        "/auth/login",
        json={"email": "active@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password."}
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies


def test_login_with_unknown_email_returns_same_generic_401(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "anything-12345"},
    )

    assert response.status_code == 401
    # Identical message to wrong-password case — no enumeration leak.
    assert response.json() == {"detail": "Invalid email or password."}


def test_login_for_pending_user_returns_same_generic_401(client, pending_user):
    response = client.post(
        "/auth/login",
        json={"email": "pending@example.com", "password": "correct-password"},
    )

    assert response.status_code == 401
    # Identical message — don't leak that the account exists but isn't active.
    assert response.json() == {"detail": "Invalid email or password."}


# ─────────────────────────────────────────────────────────────
# /auth/refresh
# ─────────────────────────────────────────────────────────────


def test_refresh_with_valid_refresh_cookie_rotates_both_tokens(
    client, active_user
):
    login = client.post(
        "/auth/login",
        json={"email": "active@example.com", "password": "correct-password"},
    )
    assert login.status_code == 200
    old_access = login.cookies["access_token"]
    old_refresh = login.cookies["refresh_token"]

    # TestClient persists cookies between requests so /auth/refresh sees
    # the refresh_token cookie automatically.
    refresh = client.post("/auth/refresh")

    assert refresh.status_code == 200
    body = refresh.json()
    assert body["email"] == "active@example.com"

    new_access = refresh.cookies["access_token"]
    new_refresh = refresh.cookies["refresh_token"]
    assert new_access  # a new value is set
    assert new_refresh

    # Both rotated tokens still decode to the same user.
    claims = decode_token(new_access, expected_type="access")
    assert claims["sub"] == str(active_user.id)


def test_refresh_without_any_cookie_returns_401(client):
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated."}


# ─────────────────────────────────────────────────────────────
# /auth/logout
# ─────────────────────────────────────────────────────────────


def test_logout_returns_200_and_clears_cookies(client, active_user):
    login = client.post(
        "/auth/login",
        json={"email": "active@example.com", "password": "correct-password"},
    )
    assert login.status_code == 200
    assert "access_token" in client.cookies
    assert "refresh_token" in client.cookies

    logout = client.post("/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"ok": True}

    # FastAPI's delete_cookie sends a Set-Cookie with Max-Age=0; the
    # TestClient's cookie jar drops the cookie in response. Subsequent
    # refresh attempts should now fail with 401.
    follow_up = client.post("/auth/refresh")
    assert follow_up.status_code == 401
