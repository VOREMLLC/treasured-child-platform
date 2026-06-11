"""Tests for the demo seed (S14).

BUILD_PLAN S14 mandates:
  - First run: 2 courses × 2 modules × 4 lessons = 16 lessons total.
  - Second run: idempotent, no duplicates.
"""

from app.models.course import Course, CourseType, Lesson, Module
from scripts.seed_demo import seed


def test_seed_inserts_two_courses_four_modules_sixteen_lessons(db_session):
    inserted = seed(db_session)

    assert inserted == {"courses": 2, "modules": 4, "lessons": 16}
    assert db_session.query(Course).count() == 2
    assert db_session.query(Module).count() == 4
    assert db_session.query(Lesson).count() == 16


def test_seed_is_idempotent_no_duplicates(db_session):
    """Re-running the seed must NOT add a second copy of anything."""
    first = seed(db_session)
    assert first["courses"] == 2

    second = seed(db_session)
    assert second == {"courses": 0, "modules": 0, "lessons": 0}

    # Totals unchanged.
    assert db_session.query(Course).count() == 2
    assert db_session.query(Module).count() == 4
    assert db_session.query(Lesson).count() == 16


def test_seed_school_course_is_jss_1(db_session):
    seed(db_session)
    course = db_session.query(Course).filter_by(slug="jss-1").one()
    assert course.type is CourseType.school
    assert course.is_paid is False
    assert course.price_kobo is None
    assert course.published is True
    assert course.level == "Junior secondary"


def test_seed_online_course_is_ai_data_paid(db_session):
    seed(db_session)
    course = db_session.query(Course).filter_by(slug="ai-data").one()
    assert course.type is CourseType.online
    assert course.is_paid is True
    # Same price as services/fees.py — single source of truth.
    assert course.price_kobo == 3_500_000
    assert course.published is True
