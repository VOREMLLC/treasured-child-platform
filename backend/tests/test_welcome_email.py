"""Tests for S28 — Welcome email on sign-up.

Acceptance criteria:
  - POST /auth/register with a valid payload sends exactly one welcome email.
  - The email goes to the registered address.
  - The email subject mentions the academy.
  - The email body contains the registrant's name and a portal reference.
  - Duplicate registration (409) sends no email.
  - The welcome email does not contain secrets (no password, no token).
"""

import pytest

from app.services import email as email_service


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

_VALID_PAYLOAD = {
    "email": "newcomer@example.com",
    "name": "Chidi Okafor",
    "phone": "08099887766",
    "password": "securepass1",
}


# ─────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────


def test_register_sends_one_welcome_email(client):
    client.post("/auth/register", json=_VALID_PAYLOAD)
    outbox = email_service.get_outbox()
    assert len(outbox) == 1


def test_welcome_email_goes_to_registered_address(client):
    client.post("/auth/register", json=_VALID_PAYLOAD)
    outbox = email_service.get_outbox()
    assert outbox[0].to == _VALID_PAYLOAD["email"]


def test_welcome_email_subject_mentions_academy(client):
    client.post("/auth/register", json=_VALID_PAYLOAD)
    subject = email_service.get_outbox()[0].subject.lower()
    assert "treasured child" in subject or "academy" in subject


def test_welcome_email_body_contains_registrant_name(client):
    client.post("/auth/register", json=_VALID_PAYLOAD)
    body = email_service.get_outbox()[0].body
    assert _VALID_PAYLOAD["name"] in body


def test_welcome_email_body_contains_portal_reference(client):
    client.post("/auth/register", json=_VALID_PAYLOAD)
    body = email_service.get_outbox()[0].body.lower()
    assert any(word in body for word in ["portal", "sign in", "learning", "academy"])


def test_duplicate_registration_sends_no_email(client):
    client.post("/auth/register", json=_VALID_PAYLOAD)
    email_service.clear_outbox()

    r = client.post("/auth/register", json=_VALID_PAYLOAD)
    assert r.status_code == 409
    assert email_service.get_outbox() == []


def test_welcome_email_does_not_contain_password(client):
    client.post("/auth/register", json=_VALID_PAYLOAD)
    body = email_service.get_outbox()[0].body
    assert _VALID_PAYLOAD["password"] not in body
