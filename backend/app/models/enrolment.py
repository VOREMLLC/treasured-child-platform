"""Enrolment model — student↔course relationship.

The table lands in S15 (so the catalogue / detail endpoints have
something to query). The self-enrol endpoint (POST /enrolments for
free courses) lands in S18; the payment-gated paid enrolment lands in
S19. The schema is stable across all three slices.

A learner cannot be enrolled in the same course twice — the
``(learner_id, course_id)`` pair is unique-constrained.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EnrolmentStatus(str, enum.Enum):
    active = "active"
    expired = "expired"


class EnrolmentSource(str, enum.Enum):
    free = "free"
    paid = "paid"


class Enrolment(Base):
    __tablename__ = "enrolments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    learner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[EnrolmentStatus] = mapped_column(
        Enum(EnrolmentStatus, name="enrolment_status"),
        nullable=False,
        default=EnrolmentStatus.active,
        server_default=EnrolmentStatus.active.value,
    )
    source: Mapped[EnrolmentSource] = mapped_column(
        Enum(EnrolmentSource, name="enrolment_source"),
        nullable=False,
    )
    access_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
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

    __table_args__ = (
        UniqueConstraint(
            "learner_id", "course_id", name="uq_enrolment_learner_course"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Enrolment id={self.id} learner_id={self.learner_id} "
            f"course_id={self.course_id} status={self.status.value}>"
        )
