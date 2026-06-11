"""Password hashing and JWT issuance / verification.

Uses argon2 (the PHC winner) via argon2-cffi for password hashes, and
PyJWT for the access + refresh tokens. The defaults from
``PasswordHasher()`` are the OWASP-recommended parameters as of 2024.

This module is purposefully tiny and dependency-free of the rest of the
app so it can be imported by tests, the registration endpoint, the
login endpoint, and (later) the role-based access middleware without
bringing the rest of the app along.
"""

import hashlib
import secrets
import uuid as _uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

_hasher = PasswordHasher()

# JWT algorithm. HS256 with the symmetric JWT_SECRET is appropriate for
# v1 single-service auth; switch to RS256 / asymmetric keys if we ever
# need to verify tokens in a service that does not also issue them.
JWT_ALGORITHM = "HS256"


# ─────────────────────────────────────────────────────────────
# Password hashing
# ─────────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    """Return an argon2id hash of ``plain``.

    The result is a self-contained PHC-format string that encodes the
    algorithm, parameters, salt, and digest, e.g.
    ``$argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>``.
    """
    return _hasher.hash(plain)


def verify_password(hashed: str, plain: str) -> bool:
    """Return True if ``plain`` matches ``hashed``."""
    try:
        return _hasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False


# ─────────────────────────────────────────────────────────────
# JWT
# ─────────────────────────────────────────────────────────────


def create_access_token(user_id: _uuid.UUID) -> str:
    """Issue a short-lived access JWT."""
    return _encode(
        user_id=user_id,
        token_type="access",
        ttl=timedelta(minutes=settings.JWT_ACCESS_TTL_MIN),
    )


def create_refresh_token(user_id: _uuid.UUID) -> str:
    """Issue a longer-lived refresh JWT."""
    return _encode(
        user_id=user_id,
        token_type="refresh",
        ttl=timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
    )


def decode_token(
    token: str, expected_type: Optional[str] = None
) -> dict:
    """Decode and verify a JWT.

    Raises ``InvalidTokenError`` on any failure: bad signature, expired,
    or (if ``expected_type`` is given) wrong type.
    """
    claims = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )
    if expected_type and claims.get("type") != expected_type:
        raise InvalidTokenError(
            f"Wrong token type: expected {expected_type!r}, "
            f"got {claims.get('type')!r}"
        )
    return claims


def _encode(
    user_id: _uuid.UUID, token_type: str, ttl: timedelta
) -> str:
    now = datetime.now(tz=timezone.utc)
    claims = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
        "type": token_type,
    }
    return jwt.encode(claims, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)


# ─────────────────────────────────────────────────────────────
# Password-reset tokens (S9)
# ─────────────────────────────────────────────────────────────


def generate_reset_token() -> str:
    """Return a high-entropy URL-safe token.

    32 bytes → ~256 bits of entropy → 43 url-safe-base64 characters.
    The plaintext goes into the password-reset email URL exactly once;
    the database only ever stores the SHA-256 hash.
    """
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    """SHA-256 hex digest of a reset token, suitable for DB lookup.

    The token is already cryptographically random, so a fast hash is
    appropriate (we don't need to defend against brute-force the way we
    do for user passwords).
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
