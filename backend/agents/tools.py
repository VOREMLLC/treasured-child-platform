"""Permissioned agent tools (read-only DB access).

These are the only functions the agent runtime may call to read data.
They return plain dicts — no ORM objects cross the boundary — so the
agent layer cannot accidentally mutate the session.

Tools available here:
  get_lesson_context(lesson_id, db)   → {title, body, course_title, level}
  get_learner_progress(learner_id, db) → {xp, level, courses:[{title,progress}]}
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.course import Course, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentStatus
from app.models.gamification import Gamification
from app.services.gamification import get_or_create as _get_gamification


def get_lesson_context(
    lesson_id: uuid.UUID, db: Session
) -> Optional[Dict[str, Any]]:
    """Return lesson display fields needed to build the tutor system prompt.

    Returns None if the lesson does not exist (caller raises 404/403).
    """
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        return None

    module = db.get(Module, lesson.module_id)
    if module is None:
        return None

    course = db.get(Course, module.course_id)
    if course is None:
        return None

    return {
        "lesson_id": str(lesson.id),
        "title": lesson.title,
        "body": lesson.content or "",
        "course_title": course.title,
        "level": course.level,
    }


def get_learner_progress(
    learner_id: uuid.UUID, db: Session
) -> Dict[str, Any]:
    """Return the learner's gamification summary and enrolled-course progress.

    Safe to call even if the learner has no gamification row yet — returns
    defaults.
    """
    g = db.get(Gamification, learner_id)
    xp = g.xp if g else 0
    level = g.level if g else 1

    # Active enrolments with progress.
    enrolments = (
        db.query(Enrolment)
        .filter(Enrolment.learner_id == learner_id)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .all()
    )

    from app.api.courses import compute_progress  # local import avoids circular

    courses: List[Dict[str, Any]] = []
    for enrolment in enrolments:
        course = db.get(Course, enrolment.course_id)
        if course is None:
            continue
        progress = compute_progress(db, learner_id, course.id)
        courses.append({"title": course.title, "progress": progress})

    return {"xp": xp, "level": level, "courses": courses}
