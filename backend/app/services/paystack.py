"""Thin wrapper around Paystack's HTTP API + webhook signature check.

- ``verify_transaction(reference)`` — GET /transaction/verify, used by
  the synchronous /payments/verify endpoint (S11).
- ``verify_webhook_signature(body, header)`` — HMAC-SHA512 against the
  secret key, used by the asynchronous /payments/webhook/paystack
  endpoint (S12).

Both are replaceable by mocks in tests.
"""

import hashlib
import hmac
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


def verify_webhook_signature(
    body_bytes: bytes, signature_header: str
) -> bool:
    """Constant-time HMAC-SHA512 comparison of a Paystack webhook signature.

    Paystack signs every webhook delivery as
    ``hex(HMAC_SHA512(secret_key, raw_body))`` and ships the digest in
    the ``x-paystack-signature`` header. We re-compute and compare.

    ``hmac.compare_digest`` is constant-time, which matters because a
    naive ``==`` would leak timing information.
    """
    if not signature_header:
        return False
    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        body_bytes,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
