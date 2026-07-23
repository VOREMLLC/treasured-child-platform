"""Tests for GET /me/dashboard (S25).

Acceptance criteria:
  - 401 without a session.
  - Empty state: no enrolments → courses=[], continue_learning=None.
  - XP, level, streak_days, badges match the gamification table directly.
  - active_courses_count == number of active enrolments.
  - progress_percent for each course matches compute_progress().
  - continue_learning points to the first incomplete lesson (in order).
  - continue_learning is null when all lessons in all courses are done.
  - Leaderboard shows top 5 learners by XP, ordered highest-first.
  - is_me=True for the current learner's entry in the leaderboard.
  - Expired / inactive enrolments are excluded.
"""

import uuid
from datetime import date, datetime, timezone

import pytest

from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.gamification import Gamification
from app.models.lesson_progress import LessonProgress
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Helpers / fixtures
# ─────────────────────────────────────────────────────────────


def _make_user(db, email: str, name: str = "Dashboard User") -> User:
    u = User(
        email=email,
        name=name,
        password_hash=hash_password("dash-pw-1234"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _login(client, email: str) -> None:
    r = client.post("/auth/login", json={"email": email, "password": "dash-pw-1234"})
    assert r.status_code == 200, r.text


def _make_course(db, *, n_lessons: int = 3, enroll_user=None, slug_suffix: str = ""):
    course = Course(
        slug=f"dash-course-{uuid.uuid4().hex[:6]}{slug_suffix}",
        title=f"Dash Course {slug_suffix}",
        type=CourseType.online,
        level="JSS 1",
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
            module_id=module.id, sort_order=i, title=f"Lesson {i}",
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


def _complete_lesson(db, learner_id, lesson_id):
    db.add(LessonProgress(
        learner_id=learner_id,
        lesson_id=lesson_id,
        completed_at=datetime.now(tz=timezone.utc),
    ))
    db.commit()


def _set_gamification(db, learner_id, *, xp=0, level=1, streak_days=0, badges=None):
    g = db.get(Gamification, learner_id)
    if g is None:
        g = Gamification(learner_id=learner_id, xp=xp, level=level,
                         streak_days=streak_days, badges=badges or [],
                         updated_at=datetime.now(tz=timezone.utc))
        db.add(g)
    else:
        g.xp = xp
        g.level = level
        g.streak_days = streak_days
        g.badges = badges or []
    db.commit()
    return g


@pytest.fixture
def student(db_session):
    return _make_user(db_session, "dash@example.com")


@pytest.fixture
def student_client(client, student):
    _login(client, "dash@example.com")
    return client


# ─────────────────────────────────────────────────────────────
# Auth guard
# ─────────────────────────────────────────────────────────────


def test_dashboard_without_session_returns_401(client):
    resp = client.get("/me/dashboard")
    assert resp.status_code == 401


# ─────────────────────────────────────────────────────────────
# Empty state
# ─────────────────────────────────────────────────────────────


def test_dashboard_empty_no_enrolments(student_client):
    resp = student_client.get("/me/dashboard")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["active_courses_count"] == 0
    assert body["courses"] == []
    assert body["continue_learning"] is None


def test_dashboard_defaults_when_no_gamification_row(student_client):
    resp = student_client.get("/me/dashboard")
    body = resp.json()
    assert body["xp"] == 0
    assert body["level"] == 1
    assert body["streak_days"] == 0
    assert body["badges"] == []


# ─────────────────────────────────────────────────────────────
# Gamification stats
# ─────────────────────────────────────────────────────────────


def test_dashboard_xp_matches_gamification_table(
    student_client, db_session, student
):
    _set_gamification(db_session, student.id, xp=350, level=2, streak_days=5)
    resp = student_client.get("/me/dashboard")
    body = resp.json()
    assert body["xp"] == 350
    assert body["level"] == 2
    assert body["streak_days"] == 5


def test_dashboard_badges_match_gamification_table(
    student_client, db_session, student
):
    _set_gamification(db_session, student.id, badges=["First Lesson", "Quiz Master"])
    resp = student_client.get("/me/dashboard")
    assert set(resp.json()["badges"]) == {"First Lesson", "Quiz Master"}


# ─────────────────────────────────────────────────────────────
# Course progress
# ─────────────────────────────────────────────────────────────


def test_dashboard_active_courses_count(student_client, db_session, student):
    _make_course(db_session, n_lessons=2, enroll_user=student)
    _make_course(db_session, n_lessons=2, enroll_user=student)
    resp = student_client.get("/me/dashboard")
    assert resp.json()["active_courses_count"] == 2


def test_dashboard_progress_percent_matches_compute_progress(
    student_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=4, enroll_user=student)
    # Complete 2 of 4 lessons → 50 %
    _complete_lesson(db_session, student.id, lessons[0].id)
    _complete_lesson(db_session, student.id, lessons[1].id)

    resp = student_client.get("/me/dashboard")
    courses = resp.json()["courses"]
    assert len(courses) == 1
    assert courses[0]["progress_percent"] == 50


def test_dashboard_inactive_enrolment_excluded(
    student_client, db_session, student
):
    # Create a course but mark the enrolment as expired (not active).
    course, _ = _make_course(db_session, n_lessons=2)
    db_session.add(Enrolment(
        learner_id=student.id,
        course_id=course.id,
        status=EnrolmentStatus.expired,
        source=EnrolmentSource.free,
    ))
    db_session.commit()

    resp = student_client.get("/me/dashboard")
    assert resp.json()["active_courses_count"] == 0
    assert resp.json()["courses"] == []


# ─────────────────────────────────────────────────────────────
# Continue learning
# ─────────────────────────────────────────────────────────────


def test_dashboard_continue_learning_points_to_first_incomplete(
    student_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=3, enroll_user=student)
    # Complete lesson 1 only — lesson 2 should be next.
    _complete_lesson(db_session, student.id, lessons[0].id)

    resp = student_client.get("/me/dashboard")
    cl = resp.json()["continue_learning"]
    assert cl is not None
    assert cl["course_id"] == str(course.id)
    assert cl["lesson_id"] == str(lessons[1].id)
    assert cl["lesson_title"] == lessons[1].title


def test_dashboard_continue_learning_none_when_all_done(
    student_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=2, enroll_user=student)
    for l in lessons:
        _complete_lesson(db_session, student.id, l.id)

    resp = student_client.get("/me/dashboard")
    assert resp.json()["continue_learning"] is None


def test_dashboard_continue_learning_picks_first_course_with_incomplete(
    student_client, db_session, student
):
    # Two courses: first is 100 % done, second has incomplete lessons.
    course1, lessons1 = _make_course(db_session, n_lessons=2, enroll_user=student)
    course2, lessons2 = _make_course(db_session, n_lessons=2, enroll_user=student)

    for l in lessons1:
        _complete_lesson(db_session, student.id, l.id)
    # course2 has no completed lessons

    resp = student_client.get("/me/dashboard")
    cl = resp.json()["continue_learning"]
    assert cl is not None
    assert cl["course_id"] == str(course2.id)
    assert cl["lesson_id"] == str(lessons2[0].id)


def test_dashboard_next_lesson_id_in_course_list(
    student_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=3, enroll_user=student)
    _complete_lesson(db_session, student.id, lessons[0].id)

    resp = student_client.get("/me/dashboard")
    course_entry = resp.json()["courses"][0]
    assert course_entry["next_lesson_id"] == str(lessons[1].id)


# ─────────────────────────────────────────────────────────────
# Leaderboard
# ─────────────────────────────────────────────────────────────


def test_dashboard_leaderboard_ordered_by_xp_desc(
    student_client, db_session, student
):
    _set_gamification(db_session, student.id, xp=100)

    other_a = _make_user(db_session, "lb-a@example.com", name="Alice")
    other_b = _make_user(db_session, "lb-b@example.com", name="Bob")
    _set_gamification(db_session, other_a.id, xp=300)
    _set_gamification(db_session, other_b.id, xp=200)

    resp = student_client.get("/me/dashboard")
    lb = resp.json()["leaderboard"]
    xp_values = [e["xp"] for e in lb]
    assert xp_values == sorted(xp_values, reverse=True)


def test_dashboard_leaderboard_has_is_me_flag(
    student_client, db_session, student
):
    _set_gamification(db_session, student.id, xp=500)
    resp = student_client.get("/me/dashboard")
    lb = resp.json()["leaderboard"]
    me_entries = [e for e in lb if e["is_me"]]
    assert len(me_entries) == 1
    assert me_entries[0]["xp"] == 500


def test_dashboard_leaderboard_max_5_entries(
    student_client, db_session, student
):
    _set_gamification(db_session, student.id, xp=100)
    for i in range(6):
        u = _make_user(db_session, f"lb-extra-{i}@example.com", name=f"User{i}")
        _set_gamification(db_session, u.id, xp=200 + i * 10)

    resp = student_client.get("/me/dashboard")
    assert len(resp.json()["leaderboard"]) <= 5


def test_dashboard_leaderboard_rank_starts_at_1(student_client, db_session, student):
    _set_gamification(db_session, student.id, xp=50)
    resp = student_client.get("/me/dashboard")
    lb = resp.json()["leaderboard"]
    if lb:
        assert lb[0]["rank"] == 1
