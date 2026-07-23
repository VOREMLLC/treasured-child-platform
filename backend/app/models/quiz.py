"""Quiz and Question models (S20).

A Quiz is attached to a Lesson (one quiz per lesson in v1).
A Question belongs to a Quiz and carries an answer_index that stores
the correct option. This field is NEVER serialised into any Pydantic
response shape — only server-side scoring logic in S21 reads it.

Data shape:
  Quiz       → id, lesson_id, title
  Question   → id, quiz_id, sort_order, prompt, options (JSON list),
               answer_index (server-only int)

Security invariant (enforced by schema design, not runtime guards):
  answer_index is not present in any schema in app/schemas/quiz.py.
  The test in test_quiz.py asserts the raw JSON response body never
  contains the string "answer_index".
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,  # one quiz per lesson in v1
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
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

    questions: Mapped[List["Question"]] = relationship(
        "Question",
        order_by="Question.sort_order",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Quiz id={self.id} lesson_id={self.lesson_id} title={self.title!r}>"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    # List of option strings, e.g. ["True", "False"] or ["A", "B", "C", "D"].
    options: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    # Index into options[] of the correct answer. SERVER-ONLY — never
    # included in any Pydantic response schema.
    answer_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Question id={self.id} quiz_id={self.quiz_id} "
            f"sort_order={self.sort_order}>"
        )
