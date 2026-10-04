"""Gamification service (S22).

Single source of truth for all XP, level, streak, and badge logic.
Both the lesson-complete endpoint (S17) and the quiz-attempt endpoint
(S21) call into this module — nothing else.

Rules (BUILD_SPEC §8):
  Lesson complete → +20 XP (idempotent — never re-awarded for the same lesson).
  Quiz attempt    → +15 XP × correct + 30 bonus if perfect.
                    XP awarded only on the learner's FIRST attempt at a quiz.
  Level           → floor(total_xp / 300) + 1.
  Streak          → last_active_date == yesterday  → streak += 1
                    last_active_date == today       → unchanged
                    otherwise                       → reset to 1
                    then last_active_date = today.
  Badges (idempotent sets):
    "First Lesson"    — first ever lesson completion.
    "7-Day Streak"    — streak_days >= 7.
    "Quiz Master"     — any perfect quiz (score == total).
    "Course Complete" — course progress reaches 100 %.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.gamification import Gamification

# ─────────────────────────────────────────────────────────────
# XP / level constants
# ─────────────────────────────────────────────────────────────

XP_LESSON_COMPLETE = 20
XP_PER_CORRECT_ANSWER = 15
XP_PERFECT_QUIZ_BONUS = 30
XP_PER_LEVEL = 300


def _compute_level(xp: int) -> int:
    return (xp // XP_PER_LEVEL) + 1


# ─────────────────────────────────────────────────────────────
# Badge names (constants so typos are caught at import time)
# ─────────────────────────────────────────────────────────────

BADGE_FIRST_LESSON = "First Lesson"
BADGE_7_DAY_STREAK = "7-Day Streak"
BADGE_QUIZ_MASTER = "Quiz Master"
BADGE_COURSE_COMPLETE = "Course Complete"


# ─────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────


def _get_or_create(learner_id: uuid.UUID, db: Session) -> Gamification:
    """Return the learner's Gamification row, creating it if absent."""
    row = db.get(Gamification, learner_id)
    if row is not None:
        return row
    # Concurrent first activity (lesson + quiz) can race to create the row;
    # the savepoint keeps the caller's transaction alive if we lose.
    sp = db.begin_nested()
    try:
        row = Gamification(
            learner_id=learner_id,
            xp=0,
            level=1,
            streak_days=0,
            last_active_date=None,
            badges=[],
        )
        db.add(row)
        db.flush()
        sp.commit()
        return row
    except IntegrityError:
        sp.rollback()
        existing = db.get(Gamification, learner_id, populate_existing=True)
        assert existing is not None
        return existing


def _update_streak(row: Gamification, today: date) -> None:
    """Mutate ``row`` to reflect today's activity."""
    if row.last_active_date is None:
        row.streak_days = 1
    elif row.last_active_date == today:
        pass  # already recorded today — streak unchanged
    else:
        delta = (today - row.last_active_date).days
        if delta == 1:
            row.streak_days += 1
        else:
            row.streak_days = 1
    row.last_active_date = today


def _add_badge(row: Gamification, badge: str) -> None:
    """Idempotently add a badge (no duplicates)."""
    if badge not in row.badges:
        # Reassign list so SQLAlchemy detects the mutation.
        row.badges = row.badges + [badge]


def _check_badges(
    row: Gamification,
    *,
    total_lessons_completed: int,
    quiz_was_perfect: bool,
    course_complete: bool,
) -> None:
    """Award any newly-earned badges (all idempotent)."""
    if total_lessons_completed >= 1:
        _add_badge(row, BADGE_FIRST_LESSON)
    if row.streak_days >= 7:
        _add_badge(row, BADGE_7_DAY_STREAK)
    if quiz_was_perfect:
        _add_badge(row, BADGE_QUIZ_MASTER)
    if course_complete:
        _add_badge(row, BADGE_COURSE_COMPLETE)


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────


def get_or_create(learner_id: uuid.UUID, db: Session) -> Gamification:
    """Return (or lazily create) the learner's Gamification row."""
    return _get_or_create(learner_id, db)


def award_lesson_xp(
    learner_id: uuid.UUID,
    *,
    db: Session,
    total_lessons_completed: int,
    course_complete: bool,
    today: Optional[date] = None,
) -> Gamification:
    """Award +20 XP for completing a lesson.

    This must only be called when a *new* LessonProgress row was just
    created (not when the row already existed — the caller is responsible
    for detecting the idempotent case and not calling this function a
    second time for the same lesson).

    ``total_lessons_completed`` is the count of all lesson_progress rows
    for this learner in this course after the insert — used for badge
    checks.  ``course_complete`` is True when progress_percent == 100.
    """
    today = today or datetime.now(tz=timezone.utc).date()
    row = _get_or_create(learner_id, db)

    row.xp += XP_LESSON_COMPLETE
    row.level = _compute_level(row.xp)
    _update_streak(row, today)
    _check_badges(
        row,
        total_lessons_completed=total_lessons_completed,
        quiz_was_perfect=False,
        course_complete=course_complete,
    )
    row.updated_at = datetime.now(tz=timezone.utc)
    db.flush()
    return row


def award_quiz_xp(
    learner_id: uuid.UUID,
    *,
    score: int,
    total: int,
    is_first_attempt: bool,
    db: Session,
    today: Optional[date] = None,
) -> int:
    """Award quiz XP and return the xp_awarded value.

    XP is only awarded on the learner's *first* attempt at a quiz
    (``is_first_attempt=True``).  Streak and badge checks run regardless
    (the learner was still active today).

    Returns the xp_awarded integer (0 if not the first attempt).
    """
    today = today or datetime.now(tz=timezone.utc).date()
    row = _get_or_create(learner_id, db)

    xp_awarded = 0
    if is_first_attempt:
        xp_awarded = score * XP_PER_CORRECT_ANSWER
        if score == total:
            xp_awarded += XP_PERFECT_QUIZ_BONUS
        row.xp += xp_awarded
        row.level = _compute_level(row.xp)

    _update_streak(row, today)
    _check_badges(
        row,
        total_lessons_completed=0,   # lesson badge not triggered here
        quiz_was_perfect=(score == total),
        course_complete=False,        # course-complete badge via lesson path only
    )
    row.updated_at = datetime.now(tz=timezone.utc)
    db.flush()
    return xp_awarded
