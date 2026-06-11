"""Thin wrapper around Paystack's HTTP API.

Only the verify endpoint is needed for S11. Initialize creates a
pending Payment row server-side and lets the frontend Paystack inline
widget set up the actual transaction with the public key.

Replaceable by mocks in tests — see ``backend/tests/test_payments.py``,
which patches ``verify_transaction``.
"""

from typing import Any

import httpx

from app.core.config import settings


class PaystackError(RuntimeError):
    """Raised when Paystack returns an error or the network call fails."""


def verify_transaction(reference: str) -> dict[str, Any]:
    """Call ``GET /transaction/verify/<reference>`` and return the JSON.

    Paystack's success-shape is::

        {"status": true, "message": "Verification successful",
         "data": {"status": "success", "amount": <kobo>, ...}}

    On HTTP error, JSON-decode error, or ``status: false`` body, raises
    :class:`PaystackError`.
    """
    url = f"{settings.PAYSTACK_API_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Cache-Control": "no-cache",
    }
    try:
        response = httpx.get(url, headers=headers, timeout=15.0)
    except httpx.HTTPError as e:
        raise PaystackError(f"Paystack request failed: {e}") from e

    if response.status_code >= 400:
        raise PaystackError(
            f"Paystack returned HTTP {response.status_code}: "
            f"{response.text[:200]}"
        )

    try:
        body = response.json()
    except ValueError as e:
        raise PaystackError(
            f"Paystack returned non-JSON body: {response.text[:200]}"
        ) from e

    if not body.get("status"):
        raise PaystackError(
            f"Paystack rejected the call: {body.get('message')!r}"
        )

    return body
