"""Tests for POST /applications."""

from __future__ import annotations

from app.models.application import Application
from app.services import email as email_service


VALID_PAYLOAD = {
    "child_name": "Adaeze Okafor",
    "guardian_name": "Chioma Okafor",
    "email": "chioma@example.com",
    "phone": "+2347035918488",
    "class_level": "junior_secondary",
    "message": "Looking forward to learning more.",
}


def test_valid_application_creates_row_and_sends_two_emails(client, db_session):
    response = client.post("/applications", json=VALID_PAYLOAD)

    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data
    assert data["status"] == "new"

    # Exactly one application row.
    rows = db_session.query(Application).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.child_name == "Adaeze Okafor"
    assert row.guardian_name == "Chioma Okafor"
    assert row.email == "chioma@example.com"
    assert row.phone == "+2347035918488"
    assert row.class_level.value == "junior_secondary"

    # Exactly two emails — one to the guardian, one to the admin inbox.
    outbox = email_service.get_outbox()
    assert len(outbox) == 2
    to_addrs = {e.to for e in outbox}
    assert "chioma@example.com" in to_addrs
    assert any(e.subject.lower().startswith("treasured child") for e in outbox)
    assert any(e.subject.startswith("New application") for e in outbox)


def test_missing_required_field_returns_422_and_writes_nothing(
    client, db_session
):
    bad = {k: v for k, v in VALID_PAYLOAD.items() if k != "child_name"}

    response = client.post("/applications", json=bad)

    assert response.status_code == 422
    assert db_session.query(Application).count() == 0
    assert email_service.get_outbox() == []


def test_invalid_email_returns_422(client, db_session):
    bad = {**VALID_PAYLOAD, "email": "not-an-email"}

    response = client.post("/applications", json=bad)

    assert response.status_code == 422
    assert db_session.query(Application).count() == 0
    assert email_service.get_outbox() == []
