"""Tests for POST /lessons/{id}/complete and the progress wiring (S17)."""

import uuid

import pytest

from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.lesson_progress import LessonProgress
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def student(db_session):
    user = User(
        email="student@example.com",
        name="Student User",
        password_hash=hash_password("student-pw-12345"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_client(client, student):
    login = client.post(
        "/auth/login",
        json={"email": "student@example.com", "password": "student-pw-12345"},
    )
    assert login.status_code == 200
    return client


@pytest.fixture
def enrolled_course(db_session, student):
    """An enrolled course with 4 lessons (2 modules × 2 lessons)."""
    course = Course(
        slug="four-lesson",
        title="Four-lesson test course",
        type=CourseType.school,
        level="Test",
        summary="For progress tests.",
        is_paid=False,
        published=True,
    )
    db_session.add(course)
    db_session.flush()

    m1 = Module(course_id=course.id, sort_order=1, title="One")
    m2 = Module(course_id=course.id, sort_order=2, title="Two")
    db_session.add_all([m1, m2])
    db_session.flush()

    lessons = [
        Lesson(module_id=m1.id, sort_order=1, title="L1", content="c1", duration_min=10),
        Lesson(module_id=m1.id, sort_order=2, title="L2", content="c2", duration_min=10),
        Lesson(module_id=m2.id, sort_order=1, title="L3", content="c3", duration_min=10),
        Lesson(module_id=m2.id, sort_order=2, title="L4", content="c4", duration_min=10),
    ]
    db_session.add_all(lessons)

    db_session.add(
        Enrolment(
            learner_id=student.id,
            course_id=course.id,
            status=EnrolmentStatus.active,
            source=EnrolmentSource.free,
        )
    )
    db_session.commit()
    for l in lessons:
        db_session.refresh(l)
    db_session.refresh(course)
    return course, lessons


# ─────────────────────────────────────────────────────────────
# POST /lessons/{id}/complete — gating
# ─────────────────────────────────────────────────────────────


def test_complete_without_session_returns_401(client):
    response = client.post(f"/lessons/{uuid.uuid4()}/complete")
    assert response.status_code == 401


def test_complete_unknown_lesson_returns_403(student_client):
    response = student_client.post(f"/lessons/{uuid.uuid4()}/complete")
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}


def test_complete_not_enrolled_returns_403(
    student_client, db_session
):
    """Lesson exists but the user isn't enrolled in its course."""
    course = Course(
        slug="other",
        title="Other",
        type=CourseType.school,
        level="X",
        summary="",
        is_paid=False,
        published=True,
    )
    db_session.add(course)
    db_session.flush()
    m = Module(course_id=course.id, sort_order=1, title="M")
    db_session.add(m)
    db_session.flush()
    lesson = Lesson(module_id=m.id, sort_order=1, title="L", content="c", duration_min=5)
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)

    response = student_client.post(f"/lessons/{lesson.id}/complete")
    assert response.status_code == 403


# ─────────────────────────────────────────────────────────────
# POST /lessons/{id}/complete — happy path + idempotency
# ─────────────────────────────────────────────────────────────


def test_complete_creates_row_and_returns_progress(
    student_client, db_session, student, enrolled_course
):
    course, lessons = enrolled_course

    response = student_client.post(f"/lessons/{lessons[0].id}/complete")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["completed"] is True
    assert body["lesson_id"] == str(lessons[0].id)
    assert body["course_id"] == str(course.id)
    assert body["progress_percent"] == 25  # 1 of 4

    rows = (
        db_session.query(LessonProgress)
        .filter(LessonProgress.learner_id == student.id)
        .all()
    )
    assert len(rows) == 1


def test_complete_twice_is_idempotent_no_duplicate_no_double_progress(
    student_client, db_session, student, enrolled_course
):
    course, lessons = enrolled_course

    first = student_client.post(f"/lessons/{lessons[0].id}/complete")
    assert first.json()["progress_percent"] == 25
    first_completed_at = first.json()["completed_at"]

    second = student_client.post(f"/lessons/{lessons[0].id}/complete")

    assert second.status_code == 200
    assert second.json()["progress_percent"] == 25  # NOT 50
    # The original completion timestamp is preserved (no flap).
    assert second.json()["completed_at"] == first_completed_at

    # Still exactly one row.
    assert (
        db_session.query(LessonProgress)
        .filter(LessonProgress.learner_id == student.id)
        .count()
        == 1
    )


def test_complete_all_lessons_reaches_100(
    student_client, db_session, student, enrolled_course
):
    course, lessons = enrolled_course

    last_percent = 0
    for i, lesson in enumerate(lessons):
        body = student_client.post(
            f"/lessons/{lesson.id}/complete"
        ).json()
        last_percent = body["progress_percent"]
        assert last_percent == int((i + 1) / len(lessons) * 100)

    assert last_percent == 100


# ─────────────────────────────────────────────────────────────
# Progress propagates to /me/courses, /courses/{id}, /lesson view
# ─────────────────────────────────────────────────────────────


def test_me_courses_includes_progress_percent(
    student_client, db_session, student, enrolled_course
):
    course, lessons = enrolled_course
    student_client.post(f"/lessons/{lessons[0].id}/complete")
    student_client.post(f"/lessons/{lessons[1].id}/complete")

    response = student_client.get("/me/courses")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["progress_percent"] == 50  # 2 of 4


def test_course_detail_reflects_completed_lessons(
    student_client, db_session, student, enrolled_course
):
    course, lessons = enrolled_course
    student_client.post(f"/lessons/{lessons[0].id}/complete")
    student_client.post(f"/lessons/{lessons[2].id}/complete")

    response = student_client.get(f"/courses/{course.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["progress_percent"] == 50
    # Module 1 lesson 1 → True; lesson 2 → False
    assert body["modules"][0]["lessons"][0]["completed"] is True
    assert body["modules"][0]["lessons"][1]["completed"] is False
    # Module 2 lesson 1 → True; lesson 2 → False
    assert body["modules"][1]["lessons"][0]["completed"] is True
    assert body["modules"][1]["lessons"][1]["completed"] is False


def test_lesson_view_reflects_completed_status(
    student_client, db_session, student, enrolled_course
):
    course, lessons = enrolled_course
    student_client.post(f"/lessons/{lessons[0].id}/complete")

    completed = student_client.get(
        f"/courses/{course.id}/lessons/{lessons[0].id}"
    ).json()
    not_completed = student_client.get(
        f"/courses/{course.id}/lessons/{lessons[1].id}"
    ).json()

    assert completed["completed"] is True
    assert not_completed["completed"] is False
