"""Endpoints scoped to the current user.

  GET /me               signed-in user profile.
  GET /me/dashboard     student dashboard (S25).
  GET /users/{id}       owner-only profile read.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, is_owner
from app.api.courses import compute_progress
from app.db.session import get_db
from app.models.course import Course, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentStatus
from app.models.gamification import Gamification
from app.models.lesson_progress import LessonProgress
from app.models.user import User
from app.schemas.dashboard import (
    ContinueLearning,
    CourseProgress,
    DashboardResponse,
    LeaderboardEntry,
)
from app.schemas.user import UserResponse

router = APIRouter(tags=["me"])


# ─────────────────────────────────────────────────────────────
# GET /me
# ─────────────────────────────────────────────────────────────


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)) -> User:
    """Return the currently-signed-in user."""
    return user


# ─────────────────────────────────────────────────────────────
# GET /me/dashboard  (S25)
# ─────────────────────────────────────────────────────────────


@router.get("/me/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    """Return everything the student portal needs in one call.

    Reads only from existing single-source-of-truth tables:
      gamification  → xp, level, streak_days, badges.
      enrolments    → active course list.
      lesson_progress + compute_progress() → progress per course.
      gamification (all learners) → top-5 XP leaderboard.
    """
    # ── Gamification stats ───────────────────────────────────
    g = db.get(Gamification, current_user.id)
    xp = g.xp if g else 0
    level = g.level if g else 1
    streak_days = g.streak_days if g else 0
    badges: List[str] = list(g.badges) if g else []

    # ── Active enrolments ────────────────────────────────────
    enrolments = (
        db.query(Enrolment)
        .filter(Enrolment.learner_id == current_user.id)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .all()
    )

    # ── Per-course progress + next incomplete lesson ─────────
    course_items: List[CourseProgress] = []
    continue_learning: Optional[ContinueLearning] = None

    for enrolment in enrolments:
        course = db.get(Course, enrolment.course_id)
        if course is None:
            continue

        progress = compute_progress(db, current_user.id, course.id)
        next_lesson = _first_incomplete_lesson(db, current_user.id, course.id)

        course_items.append(
            CourseProgress(
                id=course.id,
                slug=course.slug,
                title=course.title,
                level=course.level,
                type=course.type.value,
                progress_percent=progress,
                next_lesson_id=next_lesson.id if next_lesson else None,
            )
        )

        # "Continue learning" = first incomplete lesson across all courses
        # (first enrolment with an incomplete lesson wins).
        if continue_learning is None and next_lesson is not None:
            continue_learning = ContinueLearning(
                course_id=course.id,
                course_title=course.title,
                lesson_id=next_lesson.id,
                lesson_title=next_lesson.title,
            )

    # ── Top-5 XP leaderboard ────────────────────────────────
    top_rows = (
        db.query(Gamification, User)
        .join(User, User.id == Gamification.learner_id)
        .order_by(Gamification.xp.desc())
        .limit(5)
        .all()
    )
    leaderboard: List[LeaderboardEntry] = [
        LeaderboardEntry(
            rank=rank,
            learner_name=user.name,
            xp=gam.xp,
            is_me=(user.id == current_user.id),
        )
        for rank, (gam, user) in enumerate(top_rows, start=1)
    ]

    return DashboardResponse(
        xp=xp,
        level=level,
        streak_days=streak_days,
        badges=badges,
        active_courses_count=len(enrolments),
        courses=course_items,
        continue_learning=continue_learning,
        leaderboard=leaderboard,
    )


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _first_incomplete_lesson(
    db: Session, learner_id: uuid.UUID, course_id: uuid.UUID
) -> Optional[Lesson]:
    """Return the first lesson in the course the learner hasn't completed.

    Lessons are ordered by (module.sort_order, lesson.sort_order) to
    match the ordering the learner sees in the course detail view.
    """
    completed_ids = {
        row[0]
        for row in (
            db.query(LessonProgress.lesson_id)
            .join(Lesson, Lesson.id == LessonProgress.lesson_id)
            .join(Module, Module.id == Lesson.module_id)
            .filter(Module.course_id == course_id)
            .filter(LessonProgress.learner_id == learner_id)
            .all()
        )
    }

    all_lessons = (
        db.query(Lesson)
        .join(Module, Module.id == Lesson.module_id)
        .filter(Module.course_id == course_id)
        .order_by(Module.sort_order, Lesson.sort_order)
        .all()
    )

    for lesson in all_lessons:
        if lesson.id not in completed_ids:
            return lesson
    return None


# ─────────────────────────────────────────────────────────────
# GET /users/{user_id}
# ─────────────────────────────────────────────────────────────


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: uuid.UUID,
    current: User = Depends(get_current_user),
) -> User:
    """Owner-only read."""
    if not is_owner(current, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    return current
