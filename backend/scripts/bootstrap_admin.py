"""Create the first admin account on deploy.

Runs as part of Railway's pre-deploy step. Every self-registered account
starts ``pending`` and only an admin can activate it, so production needs
one admin to exist before anyone can log in.

Reads ``BOOTSTRAP_ADMIN_EMAIL`` / ``BOOTSTRAP_ADMIN_PASSWORD``. Does
nothing if either is unset or an admin already exists, so it is safe on
every deploy and never resets a password that was changed later.

    python -m scripts.bootstrap_admin
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password

MIN_PASSWORD_LENGTH = 12


def bootstrap_admin(db: Session, email: str, password: str) -> str:
    """Create the admin if needed; return a short status message."""
    email = email.strip().lower()
    if not email or not password:
        return "skipped: BOOTSTRAP_ADMIN_EMAIL/PASSWORD not set"
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"skipped: BOOTSTRAP_ADMIN_PASSWORD shorter than {MIN_PASSWORD_LENGTH}"

    if db.scalar(select(User).where(User.role == UserRole.admin)) is not None:
        return "skipped: an admin already exists"
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        existing.role = UserRole.admin
        existing.status = UserStatus.active
    else:
        db.add(
            User(
                email=email,
                name="Administrator",
                password_hash=hash_password(password),
                role=UserRole.admin,
                status=UserStatus.active,
            )
        )
    db.commit()
    return f"created admin {email}"


if __name__ == "__main__":
    with SessionLocal() as session:
        result = bootstrap_admin(
            session, settings.BOOTSTRAP_ADMIN_EMAIL, settings.BOOTSTRAP_ADMIN_PASSWORD
        )
    print(f"[bootstrap_admin] {result}", flush=True)
