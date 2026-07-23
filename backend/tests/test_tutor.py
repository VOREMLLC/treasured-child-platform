"""Tests for POST /agents/tutor (S23).

Acceptance criteria from BUILD_PLAN S23:
  - 401 without a session.
  - 403 if not enrolled in the lesson's course (no lesson-UUID enumeration).
  - 403 for a completely unknown lesson_id (same code — no leak).
  - 200 with a mocked Anthropic response → reply in body, AgentRun row logged.
  - AgentRun row contains: agent="tutor", learner_id, input (the question),
    output (the reply), tokens > 0, flagged=False.
  - 503 when the Anthropic API raises an APIError → run still logged.
  - The system prompt is scoped to the lesson (contains lesson title).
  - The Anthropic API key is NEVER present in the HTTP response.

All tests mock ``agents.tutor.call_tutor`` so no real API calls are made.
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.models.agent_run import AgentRun
from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Helpers / fixtures
# ─────────────────────────────────────────────────────────────

MOCK_REPLY = "Great question! Photosynthesis is how plants make food from sunlight. Can you tell me one thing a plant needs for photosynthesis?"
MOCK_TOKENS = 120


def _make_user(db, email: str) -> User:
    u = User(
        email=email,
        name="Tutor Tester",
        password_hash=hash_password("tutor-pw-1234"),
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
        json={"email": email, "password": "tutor-pw-1234"},
    )
    assert r.status_code == 200, r.text


def _make_lesson(db, *, enroll_user=None):
    """Create course → module → lesson and optionally enrol a user."""
    course = Course(
        slug=f"tutor-course-{uuid.uuid4().hex[:6]}",
        title="Science for Beginners",
        type=CourseType.online,
        level="JSS 1",
        summary=".",
        is_paid=False,
        published=True,
    )
    db.add(course)
    db.flush()
    module = Module(course_id=course.id, sort_order=1, title="Plants")
    db.add(module)
    db.flush()
    lesson = Lesson(
        module_id=module.id,
        sort_order=1,
        title="Photosynthesis",
        content="Plants use sunlight, water, and carbon dioxide to make glucose and oxygen.",
        duration_min=10,
    )
    db.add(lesson)
    db.flush()
    if enroll_user:
        db.add(Enrolment(
            learner_id=enroll_user.id,
            course_id=course.id,
            status=EnrolmentStatus.active,
            source=EnrolmentSource.free,
        ))
    db.commit()
    db.refresh(lesson)
    return course, lesson


def _mock_call_tutor(reply: str = MOCK_REPLY, tokens: int = MOCK_TOKENS):
    """Return a patch context for agents.tutor.call_tutor."""
    return patch(
        "app.api.agents.tutor_agent.call_tutor",
        return_value={"reply": reply, "tokens": tokens},
    )


@pytest.fixture
def student(db_session):
    return _make_user(db_session, "tutor@example.com")


@pytest.fixture
def student_client(client, student):
    _login(client, "tutor@example.com")
    return client


@pytest.fixture
def enrolled_lesson(db_session, student):
    _, lesson = _make_lesson(db_session, enroll_user=student)
    return lesson


@pytest.fixture
def unenrolled_lesson(db_session):
    _, lesson = _make_lesson(db_session)
    return lesson


# ─────────────────────────────────────────────────────────────
# Auth + enrolment guards
# ─────────────────────────────────────────────────────────────


def test_tutor_without_session_returns_401(client, enrolled_lesson):
    resp = client.post(
        "/agents/tutor",
        json={"lesson_id": str(enrolled_lesson.id), "question": "Explain photosynthesis."},
    )
    assert resp.status_code == 401


def test_tutor_not_enrolled_returns_403(student_client, unenrolled_lesson):
    with _mock_call_tutor():
        resp = student_client.post(
            "/agents/tutor",
            json={"lesson_id": str(unenrolled_lesson.id), "question": "Explain it."},
        )
    assert resp.status_code == 403


def test_tutor_unknown_lesson_returns_403(student_client):
    with _mock_call_tutor():
        resp = student_client.post(
            "/agents/tutor",
            json={"lesson_id": str(uuid.uuid4()), "question": "Explain it."},
        )
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────
# Happy path
# ─────────────────────────────────────────────────────────────


def test_tutor_returns_reply(student_client, enrolled_lesson):
    with _mock_call_tutor():
        resp = student_client.post(
            "/agents/tutor",
            json={
                "lesson_id": str(enrolled_lesson.id),
                "question": "Explain photosynthesis in simple terms.",
            },
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["reply"] == MOCK_REPLY
    assert "run_id" in body


def test_tutor_logs_agent_run_row(student_client, db_session, student, enrolled_lesson):
    with _mock_call_tutor():
        student_client.post(
            "/agents/tutor",
            json={
                "lesson_id": str(enrolled_lesson.id),
                "question": "What is glucose?",
            },
        )
    run = db_session.query(AgentRun).filter(AgentRun.learner_id == student.id).first()
    assert run is not None
    assert run.agent == "tutor"
    assert run.input == "What is glucose?"
    assert run.output == MOCK_REPLY
    assert run.tokens == MOCK_TOKENS
    assert run.flagged is False


def test_tutor_run_id_in_response_matches_db(
    student_client, db_session, student, enrolled_lesson
):
    with _mock_call_tutor():
        resp = student_client.post(
            "/agents/tutor",
            json={"lesson_id": str(enrolled_lesson.id), "question": "Describe the process."},
        )
    run_id = uuid.UUID(resp.json()["run_id"])
    run = db_session.get(AgentRun, run_id)
    assert run is not None
    assert run.learner_id == student.id


# ─────────────────────────────────────────────────────────────
# Input validation
# ─────────────────────────────────────────────────────────────


def test_tutor_empty_question_returns_422(student_client, enrolled_lesson):
    resp = student_client.post(
        "/agents/tutor",
        json={"lesson_id": str(enrolled_lesson.id), "question": ""},
    )
    assert resp.status_code == 422


def test_tutor_missing_lesson_id_returns_422(student_client):
    resp = student_client.post(
        "/agents/tutor",
        json={"question": "What is photosynthesis?"},
    )
    assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────
# API failure → 503 + run still logged
# ─────────────────────────────────────────────────────────────


def test_tutor_api_error_returns_503(student_client, db_session, student, enrolled_lesson):
    import anthropic as _anthropic

    with patch(
        "app.api.agents.tutor_agent.call_tutor",
        side_effect=_anthropic.APIConnectionError(request=MagicMock()),
    ):
        resp = student_client.post(
            "/agents/tutor",
            json={"lesson_id": str(enrolled_lesson.id), "question": "Explain it."},
        )
    assert resp.status_code == 503

    # A run row must still be logged even on failure.
    run = db_session.query(AgentRun).filter(AgentRun.learner_id == student.id).first()
    assert run is not None
    assert run.output == ""  # no output on failure


# ─────────────────────────────────────────────────────────────
# Security — API key never in response, system prompt scoped to lesson
# ─────────────────────────────────────────────────────────────


def test_api_key_not_in_response(student_client, enrolled_lesson):
    with _mock_call_tutor():
        resp = student_client.post(
            "/agents/tutor",
            json={"lesson_id": str(enrolled_lesson.id), "question": "Explain it."},
        )
    # The default key is "sk-ant-xxx" — must never appear in any response.
    assert b"sk-ant" not in resp.content


def test_system_prompt_contains_lesson_title(enrolled_lesson):
    """The system prompt builder injects the lesson title."""
    from agents.tutor import build_system_prompt

    prompt = build_system_prompt({
        "title": "Photosynthesis",
        "course_title": "Science for Beginners",
        "level": "JSS 1",
        "body": "Plants convert sunlight...",
    })
    assert "Photosynthesis" in prompt
    assert "Science for Beginners" in prompt
    # Guardrail instruction is present.
    assert "trusted adult" in prompt.lower()
