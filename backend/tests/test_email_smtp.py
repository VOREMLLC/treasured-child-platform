"""SMTP delivery mode of the email service."""

from __future__ import annotations

import smtplib
from unittest.mock import MagicMock, patch

import pytest

from app.core.config import settings
from app.services import email as email_service


@pytest.fixture
def smtp_settings(monkeypatch):
    monkeypatch.setattr(settings, "SMTP_HOST", "mail.example.ng")
    monkeypatch.setattr(settings, "SMTP_PORT", 465)
    monkeypatch.setattr(settings, "SMTP_USERNAME", "admissions@example.ng")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "secret")
    monkeypatch.setattr(settings, "EMAIL_FROM", "School <admissions@example.ng>")
    monkeypatch.setattr(email_service, "SEND_IN_BACKGROUND", False)


def test_smtp_sends_via_ssl_and_skips_outbox(smtp_settings):
    server = MagicMock()
    with patch.object(smtplib, "SMTP_SSL", return_value=server) as ssl_cls:
        email_service.send_email("parent@example.ng", "Receipt", "Thanks")

    ssl_cls.assert_called_once()
    server.login.assert_called_once_with("admissions@example.ng", "secret")
    sent = server.send_message.call_args.args[0]
    assert sent["To"] == "parent@example.ng"
    assert sent["From"] == "School <admissions@example.ng>"
    assert email_service.get_outbox() == []


def test_smtp_failure_never_raises(smtp_settings):
    with patch.object(smtplib, "SMTP_SSL", side_effect=OSError("down")):
        email_service.send_email("parent@example.ng", "Receipt", "Thanks")
