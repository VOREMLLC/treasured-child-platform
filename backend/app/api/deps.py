"""Shared FastAPI dependencies for auth + role-based access.

Per ``docs/USER_ROLES.md`` §5 the platform is default-deny: every
endpoint that touches user-scoped data must declare at least
``Depends(get_current_user)``, and endpoints scoped to a specific role
must declare ``Depends(requires_role(...))``. Endpoints that do NOT
declare either are public by intent (and reviewer responsibility).

Every authentication failure raises the same generic 401; every
authorisation failure raises the same generic 403. No information about
*why* leaks.
"""

import uuid
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole, UserStatus
from app.services.security import decode_token


_AUTH_FAILURE = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated.",
)

_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Forbidden.",
)


def get_current_user(
    access_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated User from the access_token cookie.

    Raises a generic 401 on any failure path:
      - no cookie
      - bad signature / expired / wrong type
      - missing or malformed sub claim
      - user no longer exists
      - user.status is not ``active``
    """
    if not access_token:
        raise _AUTH_FAILURE

    try:
        claims = decode_token(access_token, expected_type="access")
    except InvalidTokenError:
        raise _AUTH_FAILURE

    sub = claims.get("sub")
    if not sub:
        raise _AUTH_FAILURE

    try:
        user_id = uuid.UUID(sub)
    except (TypeError, ValueError):
        raise _AUTH_FAILURE

    user = db.get(User, user_id)
    if user is None or user.status is not UserStatus.active:
        raise _AUTH_FAILURE

    return user


def requires_role(*allowed: UserRole):
    """Dependency factory: require the current user to be in one of these roles.

    Usage::

        @router.get("/admin/ping")
        def admin_ping(user: User = Depends(requires_role(UserRole.admin))):
            ...

    Multiple roles are OR-combined::

        Depends(requires_role(UserRole.admin, UserRole.instructor))
    """
    if not allowed:
        raise ValueError(
            "requires_role() needs at least one UserRole argument."
        )

    def dependency(
        user: User = Depends(get_current_user),
    ) -> User:
        if user.role not in allowed:
            raise _FORBIDDEN
        return user

    return dependency


def is_owner(user: User, owner_id: uuid.UUID) -> bool:
    """Return True if ``user`` owns the resource identified by ``owner_id``.

    Designed for use inside endpoint bodies::

        @router.get("/enrolments/{enrolment_id}")
        def read(... , current: User = Depends(get_current_user), ...):
            enrolment = db.get(Enrolment, enrolment_id)
            if not enrolment or not is_owner(current, enrolment.learner_id):
                raise HTTPException(403, "Forbidden.")
            return enrolment

    Callers pull the owner field (``learner_id`` / ``user_id`` /
    ``owner_id``) off the resource and pass it explicitly — the helper
    stays narrow and unambiguous.
    """
    return user.id == owner_id
