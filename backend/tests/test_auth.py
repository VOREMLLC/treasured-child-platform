"""Tests for /auth endpoints (S7: register)."""

from app.models.user import User, UserRole, UserStatus
from app.services.security import verify_password


VALID = {
    "name": "Chioma Okafor",
    "email": "chioma@example.com",
    "phone": "+2347035918488",
    "password": "long-enough-pass",
}


def test_valid_register_creates_pending_student(client, db_session):
    response = client.post("/auth/register", json=VALID)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "chioma@example.com"
    assert body["name"] == "Chioma Okafor"
    assert body["role"] == "student"
    assert body["status"] == "pending"
    assert "password" not in body
    assert "password_hash" not in body

    rows = db_session.query(User).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.email == "chioma@example.com"
    assert row.role is UserRole.student
    assert row.status is UserStatus.pending

    # Password is hashed (argon2 PHC format) and verifies correctly.
    assert row.password_hash.startswith("$argon2")
    assert verify_password(row.password_hash, VALID["password"]) is True


def test_duplicate_email_returns_409(client, db_session):
    first = client.post("/auth/register", json=VALID)
    assert first.status_code == 201

    second = client.post("/auth/register", json=VALID)
    assert second.status_code == 409
    assert "already exists" in second.json()["detail"].lower()

    # Still only one row.
    assert db_session.query(User).count() == 1


def test_short_password_returns_422(client, db_session):
    bad = {**VALID, "password": "short"}
    response = client.post("/auth/register", json=bad)
    assert response.status_code == 422
    assert db_session.query(User).count() == 0


def test_invalid_email_returns_422(client, db_session):
    bad = {**VALID, "email": "not-an-email"}
    response = client.post("/auth/register", json=bad)
    assert response.status_code == 422
    assert db_session.query(User).count() == 0
