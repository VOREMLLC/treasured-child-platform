"""Shared SlowAPI rate limiter.

Defined in its own module so any router can decorate its endpoints
with ``@limiter.limit(...)`` without circular-importing through
``app.main``. ``app.main`` registers the limiter on ``app.state`` and
the exception handler.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def client_ip(request: Request) -> str:
    """Best guess at the real client IP behind Railway's edge.

    Requests reach us via Railway's proxy and, for browser calls, the
    Next.js ``/api`` rewrite, so the socket address is a proxy shared by
    every user. Keying on it would give the whole school one bucket.
    Railway's edge sets ``X-Real-IP``; fall back to the first
    ``X-Forwarded-For`` hop, then the socket address (tests, local dev).
    """
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=client_ip)
