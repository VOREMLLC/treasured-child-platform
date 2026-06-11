"""Application model — admission application leads.

Each row is a lead submitted via the public /apply form. Lives in the
admin queue until contacted, enrolled, or rejected. Owns no PII beyond
what the parent/guardian supplied.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ApplicationStatus(str, enum.Enum):
    """Lifecycle of an application from submission to outcome."""

    new = "new"
    contacted = "contacted"
    enrolled = "enrolled"
    rejected = "rejected"


class ClassLevel(str, enum.Enum):
    """Level the parent is applying for on behalf of the child."""

    nursery = "nursery"
    primary = "primary"
    junior_secondary = "junior_secondary"
    senior_secondary = "senior_secondary"


class Application(Base):
    """An admission application lead."""

    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    child_name: Mapped[str] = mapped_column(String(200), nullable=False)
    guardian_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    class_level: Mapped[ClassLevel] = mapped_column(
        Enum(ClassLevel, name="class_level"), nullable=False
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        nullable=False,
        default=ApplicationStatus.new,
        server_default=ApplicationStatus.new.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Application id={self.id} email={self.email!r} "
            f"status={self.status.value}>"
        )
