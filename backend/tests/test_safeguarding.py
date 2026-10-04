"""Distress in the AI tutor must reach a human (CLAUDE.md §7)."""

from __future__ import annotations

from app.models.user import User, UserRole, UserStatus
from app.services import email as email_service
from app.services.security import hash_password
from tests.test_tutor import _login, _make_lesson, _make_user


def _ask(client, lesson_id, question: str):
    return client.post(
        "/agents/tutor", json={"lesson_id": str(lesson_id), "question": question}
    )


def test_distress_emails_safeguarding_lead(client, db_session):
    learner = _make_user(db_session, "learner@tc.edu")
    _, lesson = _make_lesson(db_session, enroll_user=learner)
    _login(client, "learner@tc.edu")

    assert _ask(client, lesson.id, "I want to die").status_code == 200

    alerts = [m for m in email_service.get_outbox() if "Safeguarding" in m.subject]
    assert len(alerts) == 1
    assert "learner@tc.edu" in alerts[0].body
    # The child's own words stay in the database, not in the inbox.
    assert "want to die" not in alerts[0].body


def test_normal_blocked_question_does_not_alert(client, db_session):
    learner = _make_user(db_session, "calm@tc.edu")
    _, lesson = _make_lesson(db_session, enroll_user=learner)
    _login(client, "calm@tc.edu")

    _ask(client, lesson.id, "what is your phone number")

    assert not [m for m in email_service.get_outbox() if "Safeguarding" in m.subject]


def test_admin_sees_flagged_runs_and_students_cannot(client, db_session):
    learner = _make_user(db_session, "sad@tc.edu")
    _, lesson = _make_lesson(db_session, enroll_user=learner)
    _login(client, "sad@tc.edu")
    _ask(client, lesson.id, "I want to hurt myself")

    assert client.get("/admin/flagged-runs").status_code == 403

    db_session.add(
        User(
            email="head@tc.edu",
            name="Head",
            password_hash=hash_password("tutor-pw-1234"),
            role=UserRole.admin,
            status=UserStatus.active,
        )
    )
    db_session.commit()
    _login(client, "head@tc.edu")

    rows = client.get("/admin/flagged-runs").json()
    assert len(rows) == 1
    assert rows[0]["learner_email"] == "sad@tc.edu"
    assert "hurt myself" in rows[0]["input"]
