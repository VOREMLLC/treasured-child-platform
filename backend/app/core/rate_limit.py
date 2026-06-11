"""Shared SlowAPI rate limiter.

Defined in its own module so any router can decorate its endpoints
with ``@limiter.limit(...)`` without circular-importing through
``app.main``. ``app.main`` registers the limiter on ``app.state`` and
the exception handler.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
