"""Endpoints scoped to the current user.

``/me`` returns the signed-in user's profile (used by the frontend
header avatar and the future portal dashboard). ``/users/{user_id}`` is
owner-only — it demonstrates the ``is_owner`` helper and gives the
frontend a single endpoint shape for "look up this user, if you may".
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, is_owner
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(tags=["me"])


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)) -> User:
    """Return the currently-signed-in user."""
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: uuid.UUID,
    current: User = Depends(get_current_user),
) -> User:
    """Owner-only read.

    Even authenticated users cannot read another user's record through
    this endpoint — they get a generic 403 regardless of whether the
    other user exists. The lookup never touches the DB if the caller
    isn't the owner, so existence isn't leaked either.
    """
    if not is_owner(current, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    return current
