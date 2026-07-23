"""Pydantic shapes for quiz endpoints (S20 + S21).

SECURITY INVARIANT: answer_index is NOT present in any class here.
The test suite asserts the raw JSON response body never contains
the string "answer_index". Do not add it — not even as Optional or
with exclude=True. The field must simply not exist in these schemas.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuestionRead(BaseModel):
    """One question as served to the student.

    Contains only the display fields — prompt and the list of option
    strings. The correct answer (answer_index) is intentionally absent.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sort_order: int
    prompt: str
    options: List[str]


class QuizRead(BaseModel):
    """Full quiz payload returned by GET /quizzes/{id}."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lesson_id: uuid.UUID
    title: str
    questions: List[QuestionRead]


# ─────────────────────────────────────────────────────────────
# S21 — attempt request / response
# ─────────────────────────────────────────────────────────────


class AttemptRequest(BaseModel):
    """Body for POST /quizzes/{id}/attempt.

    ``answers`` is a list of integer indices — one per question, in
    the same order as GET /quizzes/{id} returns them (sort_order).
    The list length must equal the number of questions in the quiz.
    The server ignores any other field; a client-supplied score is
    never accepted.
    """

    answers: List[int] = Field(
        ...,
        description="Answer index per question, in question sort_order.",
    )


class AttemptResponse(BaseModel):
    """Returned by POST /quizzes/{id}/attempt."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    quiz_id: uuid.UUID
    score: int
    total: int
    # null until S22 (gamification) wires in XP rules.
    xp_awarded: Optional[int]
    created_at: datetime
