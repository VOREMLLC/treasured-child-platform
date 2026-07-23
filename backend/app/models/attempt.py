"""QuizAttempt model (S21).

One row per submission. Re-attempts are allowed — there is no unique
constraint on (learner_id, quiz_id). Every attempt is stored so a
future grade dispute can be reconstructed.

``answers`` is the list the student submitted (list of int indices,
one per question in sort_order). Stored as JSON for audit; the server
re-scores from the canonical answer_index values on every submission
and never trusts a client-supplied score.

``xp_awarded`` is null until S22 wires gamification in.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    learner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Raw answers as submitted — stored for audit only.
    answers: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    # Server-computed; never trusted from the client.
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    # Populated by S22 (gamification); null until then.
    xp_awarded: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<QuizAttempt id={self.id} quiz_id={self.quiz_id} "
            f"score={self.score}/{self.total}>"
        )
