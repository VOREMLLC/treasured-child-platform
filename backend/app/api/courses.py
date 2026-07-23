"""Student-facing course endpoints (S15, S16, S17, S27).

  GET  /me/courses                       active enrolments + progress %.
  GET  /courses/{course_id}              detail with modules + lessons.
  GET  /courses/{course_id}/lessons/{id} single-lesson view.
  POST /lessons/{lesson_id}/complete     mark lesson done (idempotent).
  GET  /courses/{course_id}/certificate  download certificate (S27).

Per ``docs/USER_ROLES.md`` §3 the student can only see their own
enrolled courses. Every endpoint requires an authenticated session.

The read endpoints return 403 for both 'not enrolled' AND 'unknown
id' (or 'lesson from a different course') so course/lesson UUIDs
can't be enumerated by response code.

Progress percent is computed in exactly one place
(``compute_progress``) — ``docs/ENGINEERING_PRINCIPLES.md`` §2 says
every number comes from one place, and progress is the canonical
example.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.certificate import Certificate
from app.models.course import Course, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentStatus
from app.models.lesson_progress import LessonProgress
from app.models.user import User
from app.schemas.course import (
    CertificateResponse,
    CourseDetail,
    CourseListItem,
    LessonCompleteResponse,
    LessonDetailRead,
)
from app.services import gamification as gamification_svc

router = APIRouter(tags=["courses"])


_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden."
)


# ─────────────────────────────────────────────────────────────
# Shared helpers — single source of truth for progress
# ─────────────────────────────────────────────────────────────


def compute_progress(
    db: Session, learner_id: uuid.UUID, course_id: uuid.UUID
) -> int:
    """Return the learner's progress in this course as 0–100.

    THE single function that turns lesson_progress rows into a
    progress percent. Every endpoint that exposes one calls this.
    """
    total = (
        db.query(Lesson)
        .join(Module, Module.id == Lesson.module_id)
        .filter(Module.course_id == course_id)
        .count()
    )
    if total == 0:
        return 0
    completed = (
        db.query(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .filter(Module.course_id == course_id)
        .filter(LessonProgress.learner_id == learner_id)
        .count()
    )
    return int((completed / total) * 100)


def _completed_lesson_ids_for_course(
    db: Session, learner_id: uuid.UUID, course_id: uuid.UUID
) -> set:
    """All lesson ids the learner has completed inside this course."""
    rows = (
        db.query(LessonProgress.lesson_id)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .filter(Module.course_id == course_id)
        .filter(LessonProgress.learner_id == learner_id)
        .all()
    )
    return {r[0] for r in rows}


def _is_lesson_complete(
    db: Session, learner_id: uuid.UUID, lesson_id: uuid.UUID
) -> bool:
    return (
        db.query(LessonProgress)
        .filter(LessonProgress.learner_id == learner_id)
        .filter(LessonProgress.lesson_id == lesson_id)
        .first()
        is not None
    )


# ─────────────────────────────────────────────────────────────
# GET /me/courses
# ─────────────────────────────────────────────────────────────


@router.get("/me/courses", response_model=List[CourseListItem])
def list_my_courses(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Return the courses the signed-in learner is actively enrolled in."""
    courses = (
        db.query(Course)
        .join(Enrolment, Enrolment.course_id == Course.id)
        .filter(Enrolment.learner_id == current.id)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .order_by(Course.title)
        .all()
    )
    return [
        {
            "id": c.id,
            "slug": c.slug,
            "title": c.title,
            "type": c.type,
            "level": c.level,
            "summary": c.summary,
            "is_paid": c.is_paid,
            "progress_percent": compute_progress(db, current.id, c.id),
        }
        for c in courses
    ]


# ─────────────────────────────────────────────────────────────
# GET /courses/{course_id}
# ─────────────────────────────────────────────────────────────


@router.get("/courses/{course_id}", response_model=CourseDetail)
def get_course_detail(
    course_id: uuid.UUID,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return course detail (modules + lessons) — enrolment-gated.

    A generic 403 is returned for not-enrolled AND for unknown ids,
    so attackers can't enumerate which course UUIDs exist.
    """
    enrolment = (
        db.query(Enrolment)
        .filter(Enrolment.learner_id == current.id)
        .filter(Enrolment.course_id == course_id)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .first()
    )
    if enrolment is None:
        raise _FORBIDDEN

    course = db.get(Course, course_id)
    if course is None:
        raise _FORBIDDEN

    completed_ids = _completed_lesson_ids_for_course(
        db, current.id, course_id
    )

    return {
        "id": course.id,
        "slug": course.slug,
        "title": course.title,
        "type": course.type,
        "level": course.level,
        "summary": course.summary,
        "is_paid": course.is_paid,
        "progress_percent": compute_progress(db, current.id, course_id),
        "modules": [
            {
                "id": module.id,
                "sort_order": module.sort_order,
                "title": module.title,
                "lessons": [
                    {
                        "id": lesson.id,
                        "sort_order": lesson.sort_order,
                        "title": lesson.title,
                        "duration_min": lesson.duration_min,
                        "completed": lesson.id in completed_ids,
                    }
                    for lesson in module.lessons
                ],
            }
            for module in course.modules
        ],
    }


# ─────────────────────────────────────────────────────────────
# GET /courses/{course_id}/lessons/{lesson_id}
# ─────────────────────────────────────────────────────────────


@router.get(
    "/courses/{course_id}/lessons/{lesson_id}",
    response_model=LessonDetailRead,
)
def get_lesson(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return one lesson with content + module/course context + neighbours.

    Same no-leak design as ``GET /courses/{id}``: 403 for not-enrolled,
    unknown lesson, or lesson-in-a-different-course.
    """
    enrolment = (
        db.query(Enrolment)
        .filter(Enrolment.learner_id == current.id)
        .filter(Enrolment.course_id == course_id)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .first()
    )
    if enrolment is None:
        raise _FORBIDDEN

    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise _FORBIDDEN

    module = db.get(Module, lesson.module_id)
    if module is None or module.course_id != course_id:
        raise _FORBIDDEN

    course = db.get(Course, course_id)
    if course is None:
        raise _FORBIDDEN

    sequence = (
        db.query(Lesson)
        .join(Module, Module.id == Lesson.module_id)
        .filter(Module.course_id == course_id)
        .order_by(Module.sort_order, Lesson.sort_order)
        .all()
    )
    idx = next(
        (i for i, ln in enumerate(sequence) if ln.id == lesson_id),
        None,
    )
    prev_lesson = sequence[idx - 1] if idx is not None and idx > 0 else None
    next_lesson = (
        sequence[idx + 1]
        if idx is not None and idx + 1 < len(sequence)
        else None
    )

    return {
        "id": lesson.id,
        "sort_order": lesson.sort_order,
        "title": lesson.title,
        "content": lesson.content,
        "duration_min": lesson.duration_min,
        "media_url": lesson.media_url,
        "completed": _is_lesson_complete(db, current.id, lesson.id),
        "course_id": course.id,
        "course_title": course.title,
        "module_id": module.id,
        "module_title": module.title,
        "prev": (
            {"id": prev_lesson.id, "title": prev_lesson.title}
            if prev_lesson
            else None
        ),
        "next": (
            {"id": next_lesson.id, "title": next_lesson.title}
            if next_lesson
            else None
        ),
    }


# ─────────────────────────────────────────────────────────────
# POST /lessons/{lesson_id}/complete  (S17)
# ─────────────────────────────────────────────────────────────


@router.post(
    "/lessons/{lesson_id}/complete",
    response_model=LessonCompleteResponse,
)
def mark_lesson_complete(
    lesson_id: uuid.UUID,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Mark a lesson as completed by the current user.

    Idempotent at two levels:
      - App: if a LessonProgress row already exists, return it without
        a second insert and return the recomputed progress percent.
      - DB: the unique constraint on (learner_id, lesson_id) hard-
        rejects a second insert under any race, and the
        IntegrityError handler re-queries the existing row.

    Enrolment gate (same generic 403 used by the read endpoints):
      - Lesson must exist.
      - Lesson must belong to a module whose course the user is
        actively enrolled in.
    """
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise _FORBIDDEN
    module = db.get(Module, lesson.module_id)
    if module is None:
        raise _FORBIDDEN

    enrolment = (
        db.query(Enrolment)
        .filter(Enrolment.learner_id == current.id)
        .filter(Enrolment.course_id == module.course_id)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .first()
    )
    if enrolment is None:
        raise _FORBIDDEN

    existing = (
        db.query(LessonProgress)
        .filter(LessonProgress.learner_id == current.id)
        .filter(LessonProgress.lesson_id == lesson_id)
        .first()
    )
    if existing is not None:
        # Idempotent repeat — no XP awarded, no new badges.
        return {
            "lesson_id": lesson.id,
            "completed": True,
            "completed_at": existing.completed_at,
            "course_id": module.course_id,
            "progress_percent": compute_progress(
                db, current.id, module.course_id
            ),
            "xp_awarded": 0,
            "new_badges": [],
        }

    row = LessonProgress(
        learner_id=current.id,
        lesson_id=lesson_id,
        completed_at=datetime.now(tz=timezone.utc),
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        # Race: another concurrent request inserted between our check
        # and our insert. The DB unique constraint kept us safe.
        db.rollback()
        row = (
            db.query(LessonProgress)
            .filter(LessonProgress.learner_id == current.id)
            .filter(LessonProgress.lesson_id == lesson_id)
            .one()
        )
        db.refresh(row)
        return {
            "lesson_id": lesson.id,
            "completed": True,
            "completed_at": row.completed_at,
            "course_id": module.course_id,
            "progress_percent": compute_progress(
                db, current.id, module.course_id
            ),
            "xp_awarded": 0,
            "new_badges": [],
        }
    db.refresh(row)

    progress = compute_progress(db, current.id, module.course_id)
    # Count lesson_progress rows for this learner in this course (badge check).
    total_completed = (
        db.query(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .filter(Module.course_id == module.course_id)
        .filter(LessonProgress.learner_id == current.id)
        .count()
    )
    badges_before = list(
        gamification_svc.get_or_create(current.id, db).badges
    )
    gamification_svc.award_lesson_xp(
        current.id,
        db=db,
        total_lessons_completed=total_completed,
        course_complete=(progress == 100),
    )

    # Issue certificate if this completion pushed progress to 100 % (S27).
    certificate_id: Optional[uuid.UUID] = None
    if progress == 100:
        certificate_id = _issue_certificate_if_complete(
            db, learner_id=current.id, course_id=module.course_id
        )

    db.commit()
    g_row = gamification_svc.get_or_create(current.id, db)
    new_badges = [b for b in g_row.badges if b not in badges_before]

    return {
        "lesson_id": lesson.id,
        "completed": True,
        "completed_at": row.completed_at,
        "course_id": module.course_id,
        "progress_percent": progress,
        "xp_awarded": gamification_svc.XP_LESSON_COMPLETE,
        "new_badges": new_badges,
        "certificate_id": certificate_id,
    }


# ─────────────────────────────────────────────────────────────
# Certificate helpers (S27)
# ─────────────────────────────────────────────────────────────


def _issue_certificate_if_complete(
    db: Session, *, learner_id: uuid.UUID, course_id: uuid.UUID
) -> Optional[uuid.UUID]:
    """Insert a Certificate row if one does not already exist.

    Returns the certificate UUID (new or existing). The unique constraint
    on (learner_id, course_id) is the idempotency backstop; we check
    first to avoid burning a savepoint on the happy path.
    """
    existing = (
        db.query(Certificate)
        .filter(Certificate.learner_id == learner_id)
        .filter(Certificate.course_id == course_id)
        .first()
    )
    if existing is not None:
        return existing.id

    cert = Certificate(learner_id=learner_id, course_id=course_id)
    db.add(cert)
    db.flush()  # populate cert.id before commit
    return cert.id


# ─────────────────────────────────────────────────────────────
# GET /courses/{course_id}/certificate  (S27)
# ─────────────────────────────────────────────────────────────


@router.get(
    "/courses/{course_id}/certificate",
    response_model=CertificateResponse,
)
def get_certificate(
    course_id: uuid.UUID,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CertificateResponse:
    """Return the learner's certificate for a completed course.

    404 if no certificate exists (course not yet completed or not enrolled).
    The same 404 is returned for unknown course IDs to prevent enumeration.
    """
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    cert = (
        db.query(Certificate)
        .filter(Certificate.learner_id == current.id)
        .filter(Certificate.course_id == course_id)
        .first()
    )
    if cert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    return CertificateResponse(
        id=cert.id,
        learner_name=current.name,
        course_title=course.title,
        issued_at=cert.issued_at,
    )
