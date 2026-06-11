"""Stubbed email sender.

Prints emails to stderr (so they show up in the uvicorn log) and keeps
an in-memory outbox so pytest can assert on what was sent. Replaced by
a real provider in a later slice; the call sites stay the same.
"""

from __future__ import annotations

import sys
from typing import List, NamedTuple


class SentEmail(NamedTuple):
    to: str
    subject: str
    body: str


_OUTBOX: List[SentEmail] = []


def send_email(to: str, subject: str, body: str) -> None:
    """Send an email (stub: print + record)."""
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
