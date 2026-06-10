"""User model — the canonical account record.

Owns identity (email + password hash), role, and lifecycle status. The
sign-up logic that populates this table comes in slice S7; this module
only defines the shape so the table exists and Alembic can manage it.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserRole(str, enum.Enum):
    """The three v1 roles stored against a User row.

    "Visitor" from docs/USER_ROLES.md is *not* stored: it is the
    no-session state for anyone hitting a public route without a
    session cookie.
    """

    admin = "admin"
    instructor = "instructor"
    student = "student"


class UserStatus(str, enum.Enum):
    """Account lifecycle status.

    New student accounts start as ``pending`` and must be activated by
    the parental-consent gate (wired in S7) before they can sign in.
    """

    pending = "pending"
    active = "active"
    suspended = "suspended"


class User(Base):
    """A user account."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"),
        nullable=False,
        default=UserStatus.pending,
        server_default=UserStatus.pending.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role.value}>"
