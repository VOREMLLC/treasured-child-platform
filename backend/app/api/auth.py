"""Auth endpoints.

Currently exposed:

  POST /auth/register   public        new pending Student account (S7).
  POST /auth/login      public        issues access + refresh cookies.
  POST /auth/refresh    cookie-auth   rotates access + refresh cookies.
  POST /auth/logout     public        clears auth cookies.

Login / logout / refresh use httpOnly cookies so the JS layer can never
read the JWTs. SameSite=lax mitigates most CSRF; production also turns
on Secure (set ``COOKIE_SECURE`` to True in the environment).
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import (
    APIRouter,
    Body,
    Cookie,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.password_reset import PasswordResetToken
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
)
from app.services import email as email_service
from app.services.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ─────────────────────────────────────────────────────────────
# POST /auth/register  (S7)
# ─────────────────────────────────────────────────────────────


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

    Per ``docs/USER_ROLES.md`` §6 the v1 ``student`` role bundles
    Learner + Parent/Guardian into one account; this row represents the
    parent who registered. Duplicate emails return 409 with a generic
    message so we don't leak which emails are registered.
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


# ─────────────────────────────────────────────────────────────
# POST /auth/login  (S8)
# ─────────────────────────────────────────────────────────────


_GENERIC_LOGIN_FAILURE = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid email or password.",
)


def _set_auth_cookies(
    response: Response, access_token: str, refresh_token: str
) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # TODO production: flip to True via env-driven flag
        max_age=settings.JWT_ACCESS_TTL_MIN * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.JWT_REFRESH_TTL_DAYS * 24 * 60 * 60,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


@router.post("/login", response_model=UserResponse)
@limiter.limit("10/minute")
def login(
    request: Request,  # noqa: ARG001
    response: Response,
    payload: LoginRequest = Body(...),
    db: Session = Depends(get_db),
) -> User:
    """Issue access + refresh cookies for an active account.

    Every failure path returns the same generic 401 so an attacker
    can't tell apart wrong-password, unknown-email, and not-yet-active
    cases.
    """
    user = db.execute(
        select(User).where(User.email == str(payload.email).lower())
    ).scalar_one_or_none()

    if user is None:
        raise _GENERIC_LOGIN_FAILURE

    if not verify_password(user.password_hash, payload.password):
        raise _GENERIC_LOGIN_FAILURE

    if user.status is not UserStatus.active:
        raise _GENERIC_LOGIN_FAILURE

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    _set_auth_cookies(response, access, refresh)

    return user


# ─────────────────────────────────────────────────────────────
# POST /auth/refresh  (S8)
# ─────────────────────────────────────────────────────────────


@router.post("/refresh", response_model=UserResponse)
def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Rotate access + refresh cookies from a valid refresh JWT.

    Both cookies are reissued on every successful refresh (per
    BUILD_SPEC §6 'refresh rotated'). The old refresh token would still
    be honoured until it expires naturally; a revocation list is out of
    scope for v1.
    """
    failure = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated.",
    )

    if not refresh_token:
        raise failure

    try:
        claims = decode_token(refresh_token, expected_type="refresh")
    except InvalidTokenError:
        raise failure

    sub = claims.get("sub")
    if not sub:
        raise failure

    try:
        user_id = uuid.UUID(sub)
    except (TypeError, ValueError):
        raise failure

    user = db.get(User, user_id)
    if user is None or user.status is not UserStatus.active:
        raise failure

    _set_auth_cookies(
        response,
        create_access_token(user.id),
        create_refresh_token(user.id),
    )
    return user


# ─────────────────────────────────────────────────────────────
# POST /auth/logout  (S8)
# ─────────────────────────────────────────────────────────────


@router.post("/logout")
def logout(response: Response) -> dict:
    """Clear access + refresh cookies. Always returns 200."""
    _clear_auth_cookies(response)
    return {"ok": True}


# ─────────────────────────────────────────────────────────────
# POST /auth/forgot-password  (S9)
# ─────────────────────────────────────────────────────────────


_GENERIC_FORGOT_RESPONSE = {
    "ok": True,
    "detail": (
        "If that email is registered, a reset link is on its way."
    ),
}


@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(
    request: Request,  # noqa: ARG001
    payload: ForgotPasswordRequest = Body(...),
    db: Session = Depends(get_db),
) -> dict:
    """Issue a single-use, time-limited password-reset token.

    Always returns the same generic 200 body so an attacker cannot
    enumerate registered emails. If the email matches an active or
    pending account, a row is inserted into password_reset_tokens
    (storing only the SHA-256 hash of the token) and an email is sent
    via the stubbed sender with the plaintext token in the URL.
    """
    user = db.execute(
        select(User).where(User.email == str(payload.email).lower())
    ).scalar_one_or_none()

    if user is not None:
        token = generate_reset_token()
        row = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_reset_token(token),
            expires_at=datetime.now(tz=timezone.utc)
            + timedelta(minutes=settings.RESET_TOKEN_TTL_MIN),
        )
        db.add(row)
        db.commit()

        reset_link = (
            f"{settings.FRONTEND_URL}/reset-password?token={token}"
        )
        email_service.send_email(
            to=user.email,
            subject="Treasured Child School — reset your password",
            body=(
                f"Hi {user.name},\n\n"
                f"Use the link below to reset your password. It expires "
                f"in {settings.RESET_TOKEN_TTL_MIN} minutes.\n\n"
                f"{reset_link}\n\n"
                f"If you didn't request this, you can ignore this email "
                f"— your password is unchanged.\n\n"
                f"— Treasured Child School\n"
            ),
        )

    return _GENERIC_FORGOT_RESPONSE


# ─────────────────────────────────────────────────────────────
# POST /auth/reset-password  (S9)
# ─────────────────────────────────────────────────────────────


_GENERIC_RESET_FAILURE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="That reset link is invalid or has expired.",
)


@router.post("/reset-password")
@limiter.limit("10/minute")
def reset_password(
    request: Request,  # noqa: ARG001
    payload: ResetPasswordRequest = Body(...),
    db: Session = Depends(get_db),
) -> dict:
    """Consume a reset token and set a new password.

    Every failure path (bad token, expired token, already consumed)
    returns the same generic 400 — no information about what went
    wrong leaks to the caller.
    """
    token_hash = hash_reset_token(payload.token)
    now = datetime.now(tz=timezone.utc)

    row = db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )
    ).scalar_one_or_none()

    if row is None or row.consumed_at is not None:
        raise _GENERIC_RESET_FAILURE

    # SQLite drops the tz on read; coerce to aware for comparison.
    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        raise _GENERIC_RESET_FAILURE

    user = db.get(User, row.user_id)
    if user is None:
        raise _GENERIC_RESET_FAILURE

    user.password_hash = hash_password(payload.new_password)
    row.consumed_at = now
    db.commit()

    return {"ok": True}
