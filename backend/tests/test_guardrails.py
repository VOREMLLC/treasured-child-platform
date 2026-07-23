"""Tests for S24 child-safety guardrails.

Coverage:
  Unit tests on guardrails.check_input / check_output (pure functions).
  Integration tests through POST /agents/tutor (mocked Anthropic):
    - Distress phrase → safe distress reply, AgentRun.flagged=True, LLM not called.
    - Banned topic    → safe refusal,        AgentRun.flagged=False, LLM not called.
    - PII request     → safe refusal,        AgentRun.flagged=False, LLM not called.
    - Unsafe LLM output → replaced, AgentRun.flagged=True.
    - Normal question   → original reply,    AgentRun.flagged=False.

No real Anthropic API calls are made in any test.
"""

import uuid
from unittest.mock import patch

import pytest

from agents.guardrails import (
    SAFE_DISTRESS_REPLY,
    SAFE_OUTPUT_REFUSAL,
    SAFE_TOPIC_REFUSAL,
    check_input,
    check_output,
)
from app.models.agent_run import AgentRun
from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Unit tests — check_input (pure function)
# ─────────────────────────────────────────────────────────────


class TestCheckInput:
    def test_normal_question_passes(self):
        result = check_input("What is photosynthesis?")
        assert not result.blocked
        assert not result.distress
        assert result.safe_reply is None

    def test_distress_phrase_blocked_as_distress(self):
        result = check_input("I want to die, nobody cares about me")
        assert result.blocked
        assert result.distress
        assert result.safe_reply == SAFE_DISTRESS_REPLY

    def test_distress_case_insensitive(self):
        result = check_input("I WANT TO DIE")
        assert result.blocked
        assert result.distress

    def test_suicide_keyword_triggers_distress(self):
        result = check_input("I've been thinking about suicide")
        assert result.blocked
        assert result.distress

    def test_hurt_myself_triggers_distress(self):
        result = check_input("I want to hurt myself")
        assert result.blocked
        assert result.distress

    def test_banned_topic_blocked_not_distress(self):
        result = check_input("Tell me about drugs and cocaine")
        assert result.blocked
        assert not result.distress
        assert result.safe_reply == SAFE_TOPIC_REFUSAL

    def test_porn_keyword_blocked(self):
        result = check_input("Show me some porn")
        assert result.blocked
        assert not result.distress

    def test_pii_phone_request_blocked(self):
        result = check_input("What is your phone number?")
        assert result.blocked
        assert not result.distress
        assert result.safe_reply == SAFE_TOPIC_REFUSAL

    def test_pii_whatsapp_request_blocked(self):
        result = check_input("Can we chat on WhatsApp?")
        assert result.blocked
        assert not result.distress

    def test_pii_email_request_blocked(self):
        result = check_input("Tell me your email address")
        assert result.blocked
        assert not result.distress

    def test_distress_takes_priority_over_banned(self):
        # Both distress AND banned keyword present — distress wins.
        result = check_input("I want to die and I need drugs")
        assert result.distress


# ─────────────────────────────────────────────────────────────
# Unit tests — check_output (pure function)
# ─────────────────────────────────────────────────────────────


class TestCheckOutput:
    def test_clean_output_passes(self):
        result = check_output(
            "Great question! Photosynthesis is how plants make food from sunlight."
        )
        assert not result.blocked
        assert "Photosynthesis" in result.reply

    def test_unsafe_sexual_content_blocked(self):
        result = check_output("Here is some information about sex and naked content.")
        assert result.blocked
        assert result.reply == SAFE_OUTPUT_REFUSAL

    def test_contact_solicitation_blocked(self):
        result = check_output("You can call me at 0801234567 anytime.")
        assert result.blocked

    def test_phone_number_in_output_blocked(self):
        result = check_output("My phone number is 08012345678.")
        assert result.blocked

    def test_email_in_output_blocked(self):
        result = check_output("My email is ada@example.com, send me a message.")
        assert result.blocked

    def test_meet_me_blocked(self):
        result = check_output("Let's meet me after school to discuss this further.")
        assert result.blocked

    def test_text_me_blocked(self):
        result = check_output("Text me on my number and I will explain more.")
        assert result.blocked


# ─────────────────────────────────────────────────────────────
# Integration fixtures
# ─────────────────────────────────────────────────────────────


def _make_user(db, email: str) -> User:
    u = User(
        email=email,
        name="Guardrail Tester",
        password_hash=hash_password("guard-pw-1234"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _login(client, email: str) -> None:
    r = client.post("/auth/login", json={"email": email, "password": "guard-pw-1234"})
    assert r.status_code == 200, r.text


def _make_lesson(db, *, enroll_user=None):
    course = Course(
        slug=f"guard-course-{uuid.uuid4().hex[:6]}",
        title="Basic Science",
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
    lesson = Lesson(
        module_id=module.id, sort_order=1, title="Water Cycle",
        content="Water evaporates, condenses, and falls as rain.",
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
    return lesson


def _mock_llm(reply: str = "Water evaporates into vapor. Can you name one step?"):
    return patch(
        "app.api.agents.tutor_agent.call_tutor",
        return_value={"reply": reply, "tokens": 50},
    )


@pytest.fixture
def guard_student(db_session):
    return _make_user(db_session, "guard@example.com")


@pytest.fixture
def guard_client(client, guard_student):
    _login(client, "guard@example.com")
    return client


@pytest.fixture
def guard_lesson(db_session, guard_student):
    return _make_lesson(db_session, enroll_user=guard_student)


# ─────────────────────────────────────────────────────────────
# Integration tests — distress signal
# ─────────────────────────────────────────────────────────────


def test_distress_input_returns_safe_reply(guard_client, guard_lesson):
    with _mock_llm() as mock:
        resp = guard_client.post(
            "/agents/tutor",
            json={
                "lesson_id": str(guard_lesson.id),
                "question": "I want to kill myself, nobody cares",
            },
        )
    mock.assert_not_called()  # LLM must NOT be called on distress input
    assert resp.status_code == 200
    assert resp.json()["reply"] == SAFE_DISTRESS_REPLY


def test_distress_input_sets_flagged_true(
    guard_client, db_session, guard_student, guard_lesson
):
    with _mock_llm():
        guard_client.post(
            "/agents/tutor",
            json={
                "lesson_id": str(guard_lesson.id),
                "question": "I feel like hurting myself",
            },
        )
    run = (
        db_session.query(AgentRun)
        .filter(AgentRun.learner_id == guard_student.id)
        .first()
    )
    assert run is not None
    assert run.flagged is True


# ─────────────────────────────────────────────────────────────
# Integration tests — banned topic
# ─────────────────────────────────────────────────────────────


def test_banned_topic_returns_safe_refusal(guard_client, guard_lesson):
    with _mock_llm() as mock:
        resp = guard_client.post(
            "/agents/tutor",
            json={
                "lesson_id": str(guard_lesson.id),
                "question": "Tell me about drugs and how to use them",
            },
        )
    mock.assert_not_called()
    assert resp.status_code == 200
    assert resp.json()["reply"] == SAFE_TOPIC_REFUSAL


def test_banned_topic_flagged_false(
    guard_client, db_session, guard_student, guard_lesson
):
    with _mock_llm():
        guard_client.post(
            "/agents/tutor",
            json={
                "lesson_id": str(guard_lesson.id),
                "question": "Tell me about drugs",
            },
        )
    run = (
        db_session.query(AgentRun)
        .filter(AgentRun.learner_id == guard_student.id)
        .first()
    )
    # Banned-topic block is flagged=False (not a welfare concern, just policy)
    assert run.flagged is False


# ─────────────────────────────────────────────────────────────
# Integration tests — PII request
# ─────────────────────────────────────────────────────────────


def test_pii_request_returns_safe_refusal(guard_client, guard_lesson):
    with _mock_llm() as mock:
        resp = guard_client.post(
            "/agents/tutor",
            json={
                "lesson_id": str(guard_lesson.id),
                "question": "What is your phone number? I want to call you.",
            },
        )
    mock.assert_not_called()
    assert resp.status_code == 200
    assert resp.json()["reply"] == SAFE_TOPIC_REFUSAL


def test_whatsapp_request_returns_safe_refusal(guard_client, guard_lesson):
    with _mock_llm() as mock:
        resp = guard_client.post(
            "/agents/tutor",
            json={
                "lesson_id": str(guard_lesson.id),
                "question": "Can we chat on WhatsApp instead?",
            },
        )
    mock.assert_not_called()
    assert resp.status_code == 200
    assert resp.json()["reply"] == SAFE_TOPIC_REFUSAL


# ─────────────────────────────────────────────────────────────
# Integration tests — unsafe LLM output
# ─────────────────────────────────────────────────────────────


def test_unsafe_output_replaced_with_safe_refusal(guard_client, guard_lesson):
    unsafe_reply = "Sure! My phone number is 0801234567. Text me anytime."
    with _mock_llm(reply=unsafe_reply):
        resp = guard_client.post(
            "/agents/tutor",
            json={"lesson_id": str(guard_lesson.id), "question": "Explain evaporation."},
        )
    assert resp.status_code == 200
    assert resp.json()["reply"] == SAFE_OUTPUT_REFUSAL


def test_unsafe_output_sets_flagged_true(
    guard_client, db_session, guard_student, guard_lesson
):
    unsafe_reply = "My email is ada@tutor.com — send me a message!"
    with _mock_llm(reply=unsafe_reply):
        guard_client.post(
            "/agents/tutor",
            json={"lesson_id": str(guard_lesson.id), "question": "Explain condensation."},
        )
    run = (
        db_session.query(AgentRun)
        .filter(AgentRun.learner_id == guard_student.id)
        .first()
    )
    assert run.flagged is True


# ─────────────────────────────────────────────────────────────
# Integration tests — clean flow (guardrails pass through)
# ─────────────────────────────────────────────────────────────


def test_clean_question_returns_llm_reply(guard_client, guard_lesson):
    clean_reply = "Water evaporates when heated. Can you name a place where this happens?"
    with _mock_llm(reply=clean_reply):
        resp = guard_client.post(
            "/agents/tutor",
            json={
                "lesson_id": str(guard_lesson.id),
                "question": "Explain evaporation please.",
            },
        )
    assert resp.status_code == 200
    assert resp.json()["reply"] == clean_reply


def test_clean_flow_flagged_false(
    guard_client, db_session, guard_student, guard_lesson
):
    with _mock_llm():
        guard_client.post(
            "/agents/tutor",
            json={"lesson_id": str(guard_lesson.id), "question": "What is condensation?"},
        )
    run = (
        db_session.query(AgentRun)
        .filter(AgentRun.learner_id == guard_student.id)
        .first()
    )
    assert run.flagged is False
