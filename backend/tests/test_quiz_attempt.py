"""Tests for POST /quizzes/{id}/attempt (S21).

Acceptance criteria from BUILD_PLAN S21:
  - Without a session → 401.
  - Not enrolled → 403 generic.
  - Unknown quiz UUID → same 403 (no enumeration leak).
  - Submit answers → 201, attempt row stored, score matches hand calc.
  - Wrong-count answers → 422, no row stored.
  - Server score wins: client cannot influence it (all-correct answers
    score max; all-wrong answers score 0; mixed scores correctly).
  - Re-attempts are allowed: two submissions → two rows, each with own score.
  - xp_awarded is null (S22 not yet wired).
  - The raw response body never contains answer_index.
"""

import uuid

import pytest

from app.models.attempt import QuizAttempt
from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.quiz import Question, Quiz
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Helpers / fixtures
# ─────────────────────────────────────────────────────────────


def _make_user(db, email: str) -> User:
    u = User(
        email=email,
        name="Attempt Tester",
        password_hash=hash_password("attempt-pw-1234"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _login(client, email: str) -> None:
    r = client.post(
        "/auth/login",
        json={"email": email, "password": "attempt-pw-1234"},
    )
    assert r.status_code == 200, r.text


def _make_quiz(db, *, enrolled_user=None):
    """Build a minimal course → module → lesson → quiz chain.

    Questions:
      Q1: options [A, B, C], answer_index = 1 (B)
      Q2: options [X, Y],    answer_index = 0 (X)
      Q3: options [T, F],    answer_index = 1 (F)

    Perfect answers: [1, 0, 1]  → score 3/3
    All-wrong:       [0, 1, 0]  → score 0/3
    Mixed:           [1, 1, 0]  → score 1/3
    """
    course = Course(
        slug=f"attempt-course-{uuid.uuid4().hex[:6]}",
        title="Attempt Course",
        type=CourseType.online,
        level="Online",
        summary=".",
        is_paid=False,
        published=True,
    )
    db.add(course)
    db.flush()
    module = Module(course_id=course.id, sort_order=1, title="M1")
    db.add(module)
    db.flush()
    lesson = Lesson(
        module_id=module.id, sort_order=1, title="L1",
        content=".", duration_min=5,
    )
    db.add(lesson)
    db.flush()
    quiz = Quiz(lesson_id=lesson.id, title="Attempt quiz")
    db.add(quiz)
    db.flush()
    specs = [
        ("Q1?", ["A", "B", "C"], 1),
        ("Q2?", ["X", "Y"],      0),
        ("Q3?", ["T", "F"],      1),
    ]
    for i, (prompt, options, answer_index) in enumerate(specs, start=1):
        db.add(Question(
            quiz_id=quiz.id,
            sort_order=i,
            prompt=prompt,
            options=options,
            answer_index=answer_index,
        ))
    if enrolled_user:
        db.add(Enrolment(
            learner_id=enrolled_user.id,
            course_id=course.id,
            status=EnrolmentStatus.active,
            source=EnrolmentSource.free,
        ))
    db.commit()
    db.refresh(quiz)
    return course, lesson, quiz


@pytest.fixture
def student(db_session):
    return _make_user(db_session, "attempt@example.com")


@pytest.fixture
def student_client(client, student):
    _login(client, "attempt@example.com")
    return client


@pytest.fixture
def enrolled_quiz(db_session, student):
    _, _, quiz = _make_quiz(db_session, enrolled_user=student)
    return quiz


@pytest.fixture
def unenrolled_quiz(db_session):
    _, _, quiz = _make_quiz(db_session)
    return quiz


# ─────────────────────────────────────────────────────────────
# Auth + enrolment guards
# ─────────────────────────────────────────────────────────────


def test_attempt_without_session_returns_401(client, enrolled_quiz):
    resp = client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [1, 0, 1]},
    )
    assert resp.status_code == 401


def test_attempt_not_enrolled_returns_403(student_client, unenrolled_quiz):
    resp = student_client.post(
        f"/quizzes/{unenrolled_quiz.id}/attempt",
        json={"answers": [1, 0, 1]},
    )
    assert resp.status_code == 403


def test_attempt_unknown_quiz_returns_403(student_client):
    resp = student_client.post(
        f"/quizzes/{uuid.uuid4()}/attempt",
        json={"answers": [0]},
    )
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────
# Server-side scoring
# ─────────────────────────────────────────────────────────────


def test_perfect_score_returns_3_of_3(
    student_client, db_session, student, enrolled_quiz
):
    resp = student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [1, 0, 1]},   # all correct
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["score"] == 3
    assert body["total"] == 3


def test_all_wrong_returns_0_of_3(
    student_client, db_session, student, enrolled_quiz
):
    resp = student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [0, 1, 0]},   # all wrong
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["score"] == 0


def test_mixed_answers_scores_correctly(
    student_client, db_session, student, enrolled_quiz
):
    # [1, 1, 0] → Q1 correct (1==1), Q2 wrong (1!=0), Q3 wrong (0!=1) → 1/3
    resp = student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [1, 1, 0]},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["score"] == 1


# ─────────────────────────────────────────────────────────────
# Attempt row stored in DB
# ─────────────────────────────────────────────────────────────


def test_attempt_persisted_in_db(
    student_client, db_session, student, enrolled_quiz
):
    student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [1, 0, 1]},
    )
    row = (
        db_session.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == enrolled_quiz.id)
        .filter(QuizAttempt.learner_id == student.id)
        .first()
    )
    assert row is not None
    assert row.score == 3
    assert row.total == 3
    assert row.answers == [1, 0, 1]


def test_xp_awarded_is_populated_by_s22(
    student_client, enrolled_quiz
):
    # All 3 correct (answers [1,0,1] match the quiz fixture) → 3×15 + 30 = 75
    resp = student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [1, 0, 1]},
    )
    assert resp.json()["xp_awarded"] == 75


# ─────────────────────────────────────────────────────────────
# Re-attempts
# ─────────────────────────────────────────────────────────────


def test_re_attempt_creates_second_row(
    student_client, db_session, student, enrolled_quiz
):
    student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [1, 0, 1]},   # perfect
    )
    student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [0, 1, 0]},   # all wrong
    )
    rows = (
        db_session.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == enrolled_quiz.id)
        .filter(QuizAttempt.learner_id == student.id)
        .all()
    )
    assert len(rows) == 2
    scores = sorted(r.score for r in rows)
    assert scores == [0, 3]


# ─────────────────────────────────────────────────────────────
# Input validation
# ─────────────────────────────────────────────────────────────


def test_wrong_answer_count_returns_422(student_client, enrolled_quiz):
    # Quiz has 3 questions; sending 2 answers → 422
    resp = student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [1, 0]},
    )
    assert resp.status_code == 422


def test_wrong_answer_count_stores_no_row(
    student_client, db_session, student, enrolled_quiz
):
    student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [1, 0]},
    )
    count = (
        db_session.query(QuizAttempt)
        .filter(QuizAttempt.learner_id == student.id)
        .count()
    )
    assert count == 0


def test_empty_answers_list_returns_422(student_client, enrolled_quiz):
    resp = student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": []},
    )
    assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────
# Security — answer_index never leaks in attempt response
# ─────────────────────────────────────────────────────────────


def test_answer_index_not_in_attempt_response(
    student_client, enrolled_quiz
):
    resp = student_client.post(
        f"/quizzes/{enrolled_quiz.id}/attempt",
        json={"answers": [1, 0, 1]},
    )
    assert b"answer_index" not in resp.content
