"""Tests for the role-based access dependencies (S10).

Covers all four cases the BUILD_PLAN S10 spec asks for:
  1. unauthenticated         → 401
  2. wrong role              → 403
  3. right role, wrong owner → 403
  4. right role, right owner → 200

Plus a few more around /me to lock the happy path in.
"""

import pytest

from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def admin_user(db_session):
    user = User(
        email="admin@example.com",
        name="Admin User",
        password_hash=hash_password("admin-pw-12345"),
        role=UserRole.admin,
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_user(db_session):
    user = User(
        email="student@example.com",
        name="Student User",
        password_hash=hash_password("student-pw-12345"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_student(db_session):
    user = User(
        email="other@example.com",
        name="Other Student",
        password_hash=hash_password("other-pw-12345"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_client(client, admin_user):
    login = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "admin-pw-12345"},
    )
    assert login.status_code == 200
    return client


@pytest.fixture
def student_client(client, student_user):
    login = client.post(
        "/auth/login",
        json={"email": "student@example.com", "password": "student-pw-12345"},
    )
    assert login.status_code == 200
    return client


# ─────────────────────────────────────────────────────────────
# /admin/ping — admin-only role gate
# ─────────────────────────────────────────────────────────────


def test_admin_ping_unauthenticated_returns_401(client):
    response = client.get("/admin/ping")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated."}


def test_admin_ping_with_student_returns_403(student_client):
    response = student_client.get("/admin/ping")
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}


def test_admin_ping_with_admin_returns_200(admin_client):
    response = admin_client.get("/admin/ping")
    assert response.status_code == 200
    assert response.json() == {"ok": True, "email": "admin@example.com"}


# ─────────────────────────────────────────────────────────────
# /users/{user_id} — owner-only ownership check
# ─────────────────────────────────────────────────────────────


def test_user_lookup_unauthenticated_returns_401(client, student_user):
    response = client.get(f"/users/{student_user.id}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated."}


def test_user_lookup_with_own_id_returns_own_profile(
    student_client, student_user
):
    response = student_client.get(f"/users/{student_user.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "student@example.com"
    assert body["role"] == "student"
    assert "password_hash" not in body


def test_user_lookup_with_other_users_id_returns_403(
    student_client, student_user, other_student
):
    response = student_client.get(f"/users/{other_student.id}")
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}


# ─────────────────────────────────────────────────────────────
# /me — bare authenticated-only route
# ─────────────────────────────────────────────────────────────


def test_me_unauthenticated_returns_401(client):
    response = client.get("/me")
    assert response.status_code == 401


def test_me_with_session_returns_current_user(student_client, student_user):
    response = student_client.get("/me")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(student_user.id)
    assert body["email"] == "student@example.com"
