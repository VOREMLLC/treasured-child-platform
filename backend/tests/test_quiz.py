"""Tests for GET /quizzes/{id} (S20).

Acceptance criteria from BUILD_PLAN S20:
  - GET /quizzes/{id} without a session → 401.
  - GET /quizzes/{id} for a not-enrolled student → 403 generic.
  - GET /quizzes/{id} for an unknown UUID → same generic 403 (no enum leak).
  - GET /quizzes/{id} for an enrolled student → 200 with title + questions.
  - The JSON response body never contains the string "answer_index"
    at any depth — verified against both the parsed object AND the raw
    bytes from the response.
  - Questions are returned in sort_order order.
  - The seed script inserts exactly 2 quizzes (one per course) with
    3 questions each.
"""

import json
import uuid

import pytest

from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.quiz import Question, Quiz
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password
from scripts.seed_demo import seed as seed_demo


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _make_user(db, email: str) -> User:
    u = User(
        email=email,
        name="Quiz Tester",
        password_hash=hash_password("quiz-pw-12345"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _login(client, email: str) -> None:
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": "quiz-pw-12345"},
    )
    assert resp.status_code == 200, resp.text


def _make_course_with_quiz(db, slug: str, paid: bool = False):
    """Create a minimal course → module → lesson → quiz chain."""
    course = Course(
        slug=slug,
        title=slug,
        type=CourseType.online,
        level="Online",
        summary=".",
        is_paid=paid,
        published=True,
    )
    db.add(course)
    db.flush()
    module = Module(course_id=course.id, sort_order=1, title="M1")
    db.add(module)
    db.flush()
    lesson = Lesson(
        module_id=module.id,
        sort_order=1,
        title="L1",
        content=".",
        duration_min=5,
    )
    db.add(lesson)
    db.flush()
    quiz = Quiz(lesson_id=lesson.id, title="Test quiz")
    db.add(quiz)
    db.flush()
    for i in range(1, 4):
        db.add(
            Question(
                quiz_id=quiz.id,
                sort_order=i,
                prompt=f"Question {i}?",
                options=["A", "B", "C"],
                answer_index=0,
            )
        )
    db.commit()
    db.refresh(quiz)
    return course, lesson, quiz


def _enrol(db, user, course):
    en = Enrolment(
        learner_id=user.id,
        course_id=course.id,
        status=EnrolmentStatus.active,
        source=EnrolmentSource.free,
    )
    db.add(en)
    db.commit()


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def student(db_session):
    return _make_user(db_session, "quiz-student@example.com")


@pytest.fixture
def student_client(client, student):
    _login(client, "quiz-student@example.com")
    return client


@pytest.fixture
def course_quiz(db_session):
    """A course + quiz the student is NOT yet enrolled in."""
    course, lesson, quiz = _make_course_with_quiz(
        db_session, "quiz-course-a"
    )
    return course, lesson, quiz


@pytest.fixture
def enrolled_course_quiz(db_session, student):
    """A course + quiz the student IS enrolled in."""
    course, lesson, quiz = _make_course_with_quiz(
        db_session, "quiz-course-b"
    )
    _enrol(db_session, student, course)
    return course, lesson, quiz


# ─────────────────────────────────────────────────────────────
# Auth guard
# ─────────────────────────────────────────────────────────────


def test_get_quiz_without_session_returns_401(client, enrolled_course_quiz):
    _, _, quiz = enrolled_course_quiz
    resp = client.get(f"/quizzes/{quiz.id}")
    assert resp.status_code == 401


# ─────────────────────────────────────────────────────────────
# Enrolment gate
# ─────────────────────────────────────────────────────────────


def test_get_quiz_not_enrolled_returns_403(student_client, course_quiz):
    _, _, quiz = course_quiz
    resp = student_client.get(f"/quizzes/{quiz.id}")
    assert resp.status_code == 403


def test_get_quiz_unknown_uuid_returns_same_403(student_client):
    """Unknown quiz ID returns the identical 403 — no UUID enumeration leak."""
    resp = student_client.get(f"/quizzes/{uuid.uuid4()}")
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────
# Happy path
# ─────────────────────────────────────────────────────────────


def test_get_quiz_enrolled_returns_200(student_client, enrolled_course_quiz):
    _, _, quiz = enrolled_course_quiz
    resp = student_client.get(f"/quizzes/{quiz.id}")
    assert resp.status_code == 200, resp.text


def test_get_quiz_has_title_and_questions(student_client, enrolled_course_quiz):
    _, _, quiz = enrolled_course_quiz
    body = student_client.get(f"/quizzes/{quiz.id}").json()

    assert body["title"] == "Test quiz"
    assert len(body["questions"]) == 3
    for q in body["questions"]:
        assert "prompt" in q
        assert "options" in q
        assert isinstance(q["options"], list)
        assert len(q["options"]) == 3


def test_get_quiz_questions_in_sort_order(student_client, enrolled_course_quiz):
    _, _, quiz = enrolled_course_quiz
    body = student_client.get(f"/quizzes/{quiz.id}").json()
    orders = [q["sort_order"] for q in body["questions"]]
    assert orders == sorted(orders)


# ─────────────────────────────────────────────────────────────
# CRITICAL: answer_index must NEVER appear in the response
# ─────────────────────────────────────────────────────────────


def test_answer_index_not_in_parsed_response(student_client, enrolled_course_quiz):
    """answer_index must be absent from the parsed JSON object at any depth."""
    _, _, quiz = enrolled_course_quiz
    body = student_client.get(f"/quizzes/{quiz.id}").json()

    def _scan(obj) -> bool:
        if isinstance(obj, dict):
            if "answer_index" in obj:
                return True
            return any(_scan(v) for v in obj.values())
        if isinstance(obj, list):
            return any(_scan(item) for item in obj)
        return False

    assert not _scan(body), "answer_index found somewhere in the parsed response!"


def test_answer_index_not_in_raw_response_bytes(student_client, enrolled_course_quiz):
    """answer_index must not appear even in the raw response bytes."""
    _, _, quiz = enrolled_course_quiz
    resp = student_client.get(f"/quizzes/{quiz.id}")
    assert b"answer_index" not in resp.content, (
        "answer_index found in raw HTTP response bytes!"
    )


# ─────────────────────────────────────────────────────────────
# Seed script — S20 adds 2 quizzes, 6 questions total
# ─────────────────────────────────────────────────────────────


def test_seed_inserts_two_quizzes_six_questions(db_session):
    result = seed_demo(db_session)
    assert result["quizzes"] == 2
    assert result["questions"] == 6


def test_seed_quiz_questions_have_no_answer_index_in_schema(db_session):
    """Verify the ORM model has answer_index but the schema strips it."""
    seed_demo(db_session)
    quiz = db_session.query(Quiz).first()
    assert quiz is not None

    # ORM row has it
    q = quiz.questions[0]
    assert hasattr(q, "answer_index")
    assert isinstance(q.answer_index, int)

    # Schema strips it — build the Pydantic model and confirm
    from app.schemas.quiz import QuizRead
    read = QuizRead.model_validate(quiz)
    serialised = read.model_dump()
    def _scan(obj) -> bool:
        if isinstance(obj, dict):
            if "answer_index" in obj:
                return True
            return any(_scan(v) for v in obj.values())
        if isinstance(obj, list):
            return any(_scan(item) for item in obj)
        return False
    assert not _scan(serialised), "answer_index leaked into Pydantic output!"


def test_seed_is_idempotent_for_quizzes(db_session):
    seed_demo(db_session)
    second = seed_demo(db_session)
    assert second["quizzes"] == 0
    assert second["questions"] == 0
    total = db_session.query(Quiz).count()
    assert total == 2
