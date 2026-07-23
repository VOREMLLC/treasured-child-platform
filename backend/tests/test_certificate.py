"""Tests for S27 — Certificate of completion.

Acceptance criteria:
  - Completing the last lesson of a course issues a Certificate row.
  - The certificate_id field in the lesson-complete response is populated.
  - Completing the same course again (all lessons already done) does NOT
    issue a second certificate — idempotent at the app level.
  - GET /courses/{id}/certificate returns learner_name, course_title, issued_at.
  - GET /courses/{id}/certificate returns 401 without a session.
  - GET /courses/{id}/certificate returns 404 when the course is not yet complete.
  - GET /courses/{id}/certificate returns 404 for an unknown course id.
  - Completing a partial course (not 100%) does NOT issue a certificate.
"""

import uuid
from datetime import datetime, timezone

import pytest

from app.models.certificate import Certificate
from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.lesson_progress import LessonProgress
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _make_student(db, email: str = "cert-student@example.com") -> User:
    u = User(
        email=email,
        name="Cert Student",
        password_hash=hash_password("cert-pw-5678"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _login(client, email: str) -> None:
    r = client.post("/auth/login", json={"email": email, "password": "cert-pw-5678"})
    assert r.status_code == 200, r.text


def _make_course(db, *, n_lessons: int = 2, enroll_user=None):
    course = Course(
        slug=f"cert-course-{uuid.uuid4().hex[:6]}",
        title="Certificate Test Course",
        type=CourseType.online,
        level="JSS 2",
        summary=".",
        is_paid=False,
        published=True,
    )
    db.add(course)
    db.flush()
    module = Module(course_id=course.id, sort_order=1, title="M1")
    db.add(module)
    db.flush()
    lessons = []
    for i in range(1, n_lessons + 1):
        l = Lesson(
            module_id=module.id, sort_order=i, title=f"L{i}",
            content=".", duration_min=5,
        )
        db.add(l)
        lessons.append(l)
    if enroll_user:
        db.add(Enrolment(
            learner_id=enroll_user.id,
            course_id=course.id,
            status=EnrolmentStatus.active,
            source=EnrolmentSource.free,
        ))
    db.commit()
    for l in lessons:
        db.refresh(l)
    db.refresh(course)
    return course, lessons


@pytest.fixture
def student(db_session):
    return _make_student(db_session)


@pytest.fixture
def student_client(client, student):
    _login(client, "cert-student@example.com")
    return client


# ─────────────────────────────────────────────────────────────
# Certificate issuance on lesson-complete
# ─────────────────────────────────────────────────────────────


def test_completing_last_lesson_issues_certificate(
    student_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=2, enroll_user=student)

    # Complete lesson 1
    student_client.post(f"/lessons/{lessons[0].id}/complete")
    # Complete lesson 2 — this pushes progress to 100
    r = student_client.post(f"/lessons/{lessons[1].id}/complete")
    assert r.status_code == 200
    body = r.json()
    assert body["progress_percent"] == 100
    assert body["certificate_id"] is not None

    cert = db_session.query(Certificate).filter(
        Certificate.learner_id == student.id,
        Certificate.course_id == course.id,
    ).first()
    assert cert is not None
    assert str(cert.id) == body["certificate_id"]


def test_completing_partial_course_does_not_issue_certificate(
    student_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=3, enroll_user=student)

    r = student_client.post(f"/lessons/{lessons[0].id}/complete")
    assert r.status_code == 200
    assert r.json()["certificate_id"] is None

    count = db_session.query(Certificate).filter(
        Certificate.learner_id == student.id,
        Certificate.course_id == course.id,
    ).count()
    assert count == 0


def test_completing_course_twice_issues_one_certificate(
    student_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=1, enroll_user=student)

    # Complete the single lesson → cert issued
    r1 = student_client.post(f"/lessons/{lessons[0].id}/complete")
    assert r1.json()["certificate_id"] is not None

    # Mark complete again (idempotent path) → no second cert
    r2 = student_client.post(f"/lessons/{lessons[0].id}/complete")
    assert r2.status_code == 200

    count = db_session.query(Certificate).filter(
        Certificate.learner_id == student.id,
        Certificate.course_id == course.id,
    ).count()
    assert count == 1


# ─────────────────────────────────────────────────────────────
# GET /courses/{id}/certificate
# ─────────────────────────────────────────────────────────────


def test_get_certificate_without_session_returns_401(client, db_session):
    course, _ = _make_course(db_session)
    r = client.get(f"/courses/{course.id}/certificate")
    assert r.status_code == 401


def test_get_certificate_when_not_complete_returns_404(
    student_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=2, enroll_user=student)
    # Complete only 1 of 2 lessons
    student_client.post(f"/lessons/{lessons[0].id}/complete")

    r = student_client.get(f"/courses/{course.id}/certificate")
    assert r.status_code == 404


def test_get_certificate_for_unknown_course_returns_404(student_client):
    r = student_client.get(f"/courses/{uuid.uuid4()}/certificate")
    assert r.status_code == 404


def test_get_certificate_returns_correct_fields(
    student_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=1, enroll_user=student)
    student_client.post(f"/lessons/{lessons[0].id}/complete")

    r = student_client.get(f"/courses/{course.id}/certificate")
    assert r.status_code == 200
    body = r.json()
    assert body["learner_name"] == student.name
    assert body["course_title"] == course.title
    assert body["issued_at"] is not None
    assert body["id"] is not None


def test_get_certificate_id_matches_db(student_client, db_session, student):
    course, lessons = _make_course(db_session, n_lessons=1, enroll_user=student)
    student_client.post(f"/lessons/{lessons[0].id}/complete")

    r = student_client.get(f"/courses/{course.id}/certificate")
    cert_in_db = db_session.query(Certificate).filter(
        Certificate.learner_id == student.id,
        Certificate.course_id == course.id,
    ).first()
    assert r.json()["id"] == str(cert_in_db.id)


def test_get_certificate_for_different_learner_returns_404(
    client, db_session
):
    # Two separate learners; only learner A completes the course.
    learner_a = _make_student(db_session, "a@example.com")
    learner_b = _make_student(db_session, "b@example.com")
    course, lessons = _make_course(db_session, enroll_user=learner_a)

    # Log in as A, complete the course
    _login(client, "a@example.com")
    client.post(f"/lessons/{lessons[0].id}/complete")
    client.post(f"/lessons/{lessons[1].id}/complete")

    # Log in as B — should get 404 (no cert for B)
    r_b_login = client.post("/auth/login", json={"email": "b@example.com", "password": "cert-pw-5678"})
    assert r_b_login.status_code == 200

    r = client.get(f"/courses/{course.id}/certificate")
    assert r.status_code == 404
