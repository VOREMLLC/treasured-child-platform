"""LessonProgress — the canonical 'has the learner completed this lesson?' row.

THE single source of truth for course progress, certificates, and
later gamification. Per ``docs/ENGINEERING_PRINCIPLES.md`` §2 the
percent number every part of the platform shows (catalogue card,
course detail, certificate eligibility, gamification) must come from
the same table — this one — read through one helper
(``compute_progress`` in :mod:`app.api.courses`).

Idempotency is enforced at the DB level via the unique constraint on
``(learner_id, lesson_id)``. A double-click on Mark complete cannot
create a second row; the DB rejects it.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    learner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "lesson_id",
            name="uq_lesson_progress_learner_lesson",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<LessonProgress id={self.id} learner_id={self.learner_id} "
            f"lesson_id={self.lesson_id}>"
        )
