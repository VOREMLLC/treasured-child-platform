"""Quiz endpoints (S20 + S21).

  GET  /quizzes/{quiz_id}          auth + enrolment-gated
  POST /quizzes/{quiz_id}/attempt  auth + enrolment-gated

S20 — GET returns quiz title and questions without answer_index.
S21 — POST scores the attempt server-side; client-supplied scores are
      never accepted. Re-attempts are allowed.

Shared enrolment gate (same no-leak design as /courses/{id}):
  - Quiz must exist.
  - Lesson → Module → Course lookup must succeed.
  - Student must have an active Enrolment in that course.
  - A generic 403 is returned for all failure cases so quiz UUIDs
    cannot be enumerated by response code.
"""

import uuid
from typing import Union

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.attempt import QuizAttempt
from app.models.course import Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentStatus
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.quiz import AttemptRequest, AttemptResponse, QuizRead
from app.services import gamification as gamification_svc

router = APIRouter(tags=["quizzes"])

_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Forbidden.",
)


# ─────────────────────────────────────────────────────────────
# Shared helper — resolve quiz + assert enrolment
# ─────────────────────────────────────────────────────────────


def _get_quiz_or_403(
    quiz_id: uuid.UUID, user: User, db: Session
) -> Quiz:
    """Return the Quiz if the user is enrolled in its course, else 403."""
    quiz = db.get(Quiz, quiz_id)
    if quiz is None:
        raise _FORBIDDEN

    lesson = db.get(Lesson, quiz.lesson_id)
    if lesson is None:
        raise _FORBIDDEN

    module = db.get(Module, lesson.module_id)
    if module is None:
        raise _FORBIDDEN

    enrolment = (
        db.query(Enrolment)
        .filter(Enrolment.learner_id == user.id)
        .filter(Enrolment.course_id == module.course_id)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .first()
    )
    if enrolment is None:
        raise _FORBIDDEN

    return quiz


# ─────────────────────────────────────────────────────────────
# GET /quizzes/{quiz_id}  (S20)
# ─────────────────────────────────────────────────────────────


@router.get("/quizzes/{quiz_id}", response_model=QuizRead)
def get_quiz(
    quiz_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Quiz:
    """Return a quiz with questions (no answer keys)."""
    return _get_quiz_or_403(quiz_id, current_user, db)


# ─────────────────────────────────────────────────────────────
# POST /quizzes/{quiz_id}/attempt  (S21)
# ─────────────────────────────────────────────────────────────


@router.post(
    "/quizzes/{quiz_id}/attempt",
    response_model=AttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_attempt(
    quiz_id: uuid.UUID,
    payload: AttemptRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuizAttempt:
    """Score a quiz attempt server-side and store the result.

    The client submits a list of answer indices (one per question, in
    sort_order). The server computes the score by comparing each
    submitted index to the stored answer_index — the client-supplied
    values are only used as answer choices, never as a score.

    Re-attempts are always allowed; every submission creates a new row.

    Validation: the answers list must have exactly as many entries as
    there are questions in the quiz (422 if not).

    xp_awarded is null until S22 (gamification) wires in the rules.
    """
    quiz = _get_quiz_or_403(quiz_id, current_user, db)

    questions = sorted(quiz.questions, key=lambda q: q.sort_order)

    if len(payload.answers) != len(questions):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Expected {len(questions)} answers, "
                f"got {len(payload.answers)}."
            ),
        )

    score = sum(
        1
        for submitted, question in zip(payload.answers, questions)
        if submitted == question.answer_index
    )

    # XP is awarded only on the first attempt (first-attempt-only rule).
    prior_attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == quiz.id)
        .filter(QuizAttempt.learner_id == current_user.id)
        .count()
    )
    is_first_attempt = prior_attempts == 0

    xp_awarded = gamification_svc.award_quiz_xp(
        current_user.id,
        score=score,
        total=len(questions),
        is_first_attempt=is_first_attempt,
        db=db,
    )

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        learner_id=current_user.id,
        answers=payload.answers,
        score=score,
        total=len(questions),
        xp_awarded=xp_awarded,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt
