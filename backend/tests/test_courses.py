"""Tests for /me/courses and /courses/{course_id} (S15)."""

import uuid

import pytest

from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
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
def other_student(db_session):
    user = User(
        email="other@example.com",
        name="Other Student",
        password_hash=hash_password("other-pw-12345"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def school_course(db_session):
    course = Course(
        slug="jss-1",
        title="Junior secondary 1",
        type=CourseType.school,
        level="Junior secondary",
        summary="JSS 1.",
        is_paid=False,
        published=True,
    )
    db_session.add(course)
    db_session.flush()
    module = Module(course_id=course.id, sort_order=1, title="Mathematics")
    db_session.add(module)
    db_session.flush()
    db_session.add_all([
        Lesson(
            module_id=module.id,
            sort_order=1,
            title="Numbers",
            content="...",
            duration_min=10,
        ),
        Lesson(
            module_id=module.id,
            sort_order=2,
            title="Addition",
            content="...",
            duration_min=15,
        ),
    ])
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def online_course(db_session):
    course = Course(
        slug="ai-data",
        title="AI & data",
        type=CourseType.online,
        level="Online",
        summary="AI.",
        is_paid=True,
        price_kobo=3_500_000,
        published=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def student_client(client, student):
    login = client.post(
        "/auth/login",
        json={"email": "student@example.com", "password": "student-pw-12345"},
    )
    assert login.status_code == 200
    return client


def _enrol(db_session, student, course):
    en = Enrolment(
        learner_id=student.id,
        course_id=course.id,
        status=EnrolmentStatus.active,
        source=EnrolmentSource.free,
    )
    db_session.add(en)
    db_session.commit()
    return en


# ─────────────────────────────────────────────────────────────
# /me/courses
# ─────────────────────────────────────────────────────────────


def test_me_courses_without_session_returns_401(client):
    response = client.get("/me/courses")
    assert response.status_code == 401


def test_me_courses_with_no_enrolments_returns_empty_list(student_client):
    response = student_client.get("/me/courses")
    assert response.status_code == 200
    assert response.json() == []


def test_me_courses_returns_only_active_enrolments(
    student_client, db_session, student, school_course, online_course
):
    _enrol(db_session, student, school_course)
    # Expired enrolment must NOT appear.
    expired = Enrolment(
        learner_id=student.id,
        course_id=online_course.id,
        status=EnrolmentStatus.expired,
        source=EnrolmentSource.paid,
    )
    db_session.add(expired)
    db_session.commit()

    response = student_client.get("/me/courses")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["slug"] == "jss-1"


def test_me_courses_excludes_other_users_enrolments(
    student_client, db_session, student, other_student, school_course
):
    _enrol(db_session, other_student, school_course)

    response = student_client.get("/me/courses")
    assert response.status_code == 200
    assert response.json() == []


# ─────────────────────────────────────────────────────────────
# /courses/{course_id}
# ─────────────────────────────────────────────────────────────


def test_course_detail_without_session_returns_401(
    client, school_course
):
    response = client.get(f"/courses/{school_course.id}")
    assert response.status_code == 401


def test_course_detail_not_enrolled_returns_403(
    student_client, school_course
):
    response = student_client.get(f"/courses/{school_course.id}")
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}


def test_course_detail_enrolled_returns_modules_and_lessons(
    student_client, db_session, student, school_course
):
    _enrol(db_session, student, school_course)

    response = student_client.get(f"/courses/{school_course.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "jss-1"
    assert len(body["modules"]) == 1
    module = body["modules"][0]
    assert module["title"] == "Mathematics"
    assert len(module["lessons"]) == 2
    # Lessons ordered by sort_order.
    titles = [lesson["title"] for lesson in module["lessons"]]
    assert titles == ["Numbers", "Addition"]
    # Every lesson carries the S17 stub.
    for lesson in module["lessons"]:
        assert lesson["completed"] is False
        assert "id" in lesson
        assert "duration_min" in lesson


def test_course_detail_unknown_id_returns_403_same_as_not_enrolled(
    student_client
):
    """No-leak: unknown UUID must not be distinguishable from forbidden."""
    fake_id = uuid.uuid4()
    response = student_client.get(f"/courses/{fake_id}")
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}
