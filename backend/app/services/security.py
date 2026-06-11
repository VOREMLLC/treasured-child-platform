"""Password hashing and verification.

Uses argon2 (the PHC winner) via argon2-cffi. The defaults from
``PasswordHasher()`` are the OWASP-recommended parameters as of 2024
and are appropriate for v1.

This module is purposefully tiny and dependency-free so it can be
imported by tests, the registration endpoint, and the (future) login
endpoint without bringing the rest of the app along.
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


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
