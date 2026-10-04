"""Email sender.

Three modes, chosen by configuration so call sites never change:

- **SMTP** (``SMTP_HOST`` set): real delivery through any SMTP mailbox,
  e.g. the school's cPanel hosting, Zoho, Gmail Workspace, Resend or
  Postmark SMTP. Sent on a background thread so a slow mail server never
  delays or fails a payment, login or application request.
- **Production without SMTP**: logs that an email was dropped, never the
  body (bodies carry reset links and minors' details).
- **Development / tests**: prints to stderr and keeps an in-memory outbox
  so pytest can assert on what was sent.
"""

from __future__ import annotations

import smtplib
import ssl
import sys
import threading
from email.message import EmailMessage
from typing import List, NamedTuple

from app.core.config import settings


class SentEmail(NamedTuple):
    to: str
    subject: str
    body: str


_OUTBOX: List[SentEmail] = []

# Tests flip this to deliver inline and assert on the SMTP call.
SEND_IN_BACKGROUND = True


def _log(message: str) -> None:
    print(f"[email] {message}", flush=True, file=sys.stderr)


def _build_message(to: str, subject: str, body: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    return msg


def _deliver_smtp(msg: EmailMessage) -> None:
    """Send one message; failures are logged, never raised to the caller."""
    context = ssl.create_default_context()
    try:
        if settings.SMTP_PORT == 465:
            server: smtplib.SMTP = smtplib.SMTP_SSL(
                settings.SMTP_HOST, settings.SMTP_PORT, timeout=20, context=context
            )
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20)
            server.starttls(context=context)
        with server:
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        _log(f"delivery failed: subject={msg['Subject']!r} error={type(exc).__name__}")


def send_email(to: str, subject: str, body: str) -> None:
    """Send an email using whichever mode the configuration selects."""
    if settings.SMTP_HOST:
        msg = _build_message(to, subject, body)
        if SEND_IN_BACKGROUND:
            threading.Thread(target=_deliver_smtp, args=(msg,), daemon=True).start()
        else:
            _deliver_smtp(msg)
        return
    if settings.is_production:
        _log(f"not sent (SMTP_HOST unset): subject={subject!r}")
        return
    print(
        f"\n--- EMAIL ---\nTo: {to}\nSubject: {subject}\n\n{body}\n--- END ---\n",
        flush=True,
        file=sys.stderr,
    )
    _OUTBOX.append(SentEmail(to=to, subject=subject, body=body))


def get_outbox() -> List[SentEmail]:
    """Return a copy of the outbox (for tests)."""
    return list(_OUTBOX)


def clear_outbox() -> None:
    """Empty the outbox (for tests)."""
    _OUTBOX.clear()
