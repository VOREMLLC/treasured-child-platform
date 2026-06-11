"""Student-facing course endpoints (S15).

  GET /me/courses        active enrolments → catalogue cards.
  GET /courses/{course_id} detail with modules + lessons; enrolment-gated.

Per ``docs/USER_ROLES.md`` §3 the student can only see their own
enrolled courses. Both endpoints require an authenticated session.

The detail endpoint returns 403 for **both** 'not enrolled' and
'unknown id' so course UUIDs can't be enumerated by response code.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.course import Course
from app.models.enrolment import Enrolment, EnrolmentStatus
from app.models.user import User
from app.schemas.course import CourseDetail, CourseListItem

router = APIRouter(tags=["courses"])


@router.get("/me/courses", response_model=List[CourseListItem])
def list_my_courses(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Course]:
    """Return the courses the signed-in learner is actively enrolled in."""
    courses = (
        db.query(Course)
        .join(Enrolment, Enrolment.course_id == Course.id)
        .filter(Enrolment.learner_id == current.id)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .order_by(Course.title)
        .all()
    )
    return courses


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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )

    course = db.get(Course, course_id)
    if course is None:
        # Shouldn't happen — FK protects this — but a defensive 403
        # keeps the no-leak guarantee even on a half-dropped DB.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )

    # Build the response shape explicitly so the `completed` stub
    # slots in. When S17 lands lesson_progress, look it up per
    # (current.id, lesson.id) and replace `False` below.
    return {
        "id": course.id,
        "slug": course.slug,
        "title": course.title,
        "type": course.type,
        "level": course.level,
        "summary": course.summary,
        "is_paid": course.is_paid,
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
                        "completed": False,  # TODO S17
                    }
                    for lesson in module.lessons
                ],
            }
            for module in course.modules
        ],
    }
