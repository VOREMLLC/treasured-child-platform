"""Auth endpoints.

For S7 only the parent self-signup endpoint is exposed:

  POST /auth/register   public   create a new pending Student account.

Login / logout / refresh land in S8; password reset in S9.
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import RegisterRequest, UserResponse
from app.services.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
def register(
    request: Request,  # noqa: ARG001  # required by slowapi for IP key
    payload: RegisterRequest = Body(...),
    db: Session = Depends(get_db),
) -> User:
    """Create a new pending Student account.

    The parent is the account holder; per ``docs/USER_ROLES.md`` §6 the
    v1 ``student`` role bundles Learner + Parent/Guardian. The account
    starts ``pending`` and is activated by the consent gate (later
    slice). Duplicate emails return 409 — error copy stays generic so
    we don't leak which emails are registered.
    """
    user = User(
        email=str(payload.email).lower(),
        name=payload.name.strip(),
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=UserRole.student,
        status=UserStatus.pending,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists.",
        )
    db.refresh(user)
    return user
