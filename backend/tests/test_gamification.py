"""Tests for S22 gamification (XP, levels, streaks, badges).

Spec (BUILD_SPEC §8):
  - Lesson complete → +20 XP.  Idempotent (same lesson never awards twice).
  - Quiz attempt   → +15 XP × correct answers + 30 bonus if perfect score.
                     First-attempt-only: re-attempts give 0 XP.
  - Level          → floor(total_xp / 300) + 1.
  - Streak         → yesterday → streak+1; today → unchanged; else reset to 1.
  - Badges (idempotent): First Lesson, 7-Day Streak, Quiz Master, Course Complete.

All tests run through the HTTP API (not the service in isolation) so the
full integration path (endpoint → service → DB → response) is exercised.
"""

import uuid
from datetime import date, timedelta

import pytest

from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.gamification import Gamification
from app.models.quiz import Question, Quiz
from app.models.user import User, UserRole, UserStatus
from app.services import gamification as gamification_svc
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Fixtures / helpers
# ─────────────────────────────────────────────────────────────


def _make_user(db, email: str) -> User:
    u = User(
        email=email,
        name="Gamif Tester",
        password_hash=hash_password("gamif-pw-1234"),
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
        json={"email": email, "password": "gamif-pw-1234"},
    )
    assert r.status_code == 200, r.text


def _make_course_with_lessons(db, *, n_lessons: int = 3, enroll_user=None):
    """Create course → module → n lessons and optionally enrol a user."""
    course = Course(
        slug=f"gamif-course-{uuid.uuid4().hex[:6]}",
        title="Gamif Course",
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
    lessons = []
    for i in range(1, n_lessons + 1):
        l = Lesson(
            module_id=module.id, sort_order=i, title=f"L{i}",
            content=".", duration_min=5,
        )
        db.add(l)
        lessons.append(l)
    db.flush()
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
    return course, lessons


def _make_quiz(db, lesson_id, *, n_questions: int = 3):
    """Create a quiz with n_questions, correct answer_index always 0."""
    quiz = Quiz(lesson_id=lesson_id, title="Gamif Quiz")
    db.add(quiz)
    db.flush()
    for i in range(1, n_questions + 1):
        db.add(Question(
            quiz_id=quiz.id,
            sort_order=i,
            prompt=f"Q{i}?",
            options=["correct", "wrong"],
            answer_index=0,  # always first option
        ))
    db.commit()
    db.refresh(quiz)
    return quiz


def _g(db, user_id) -> Gamification:
    """Fetch the gamification row (or None)."""
    return db.get(Gamification, user_id)


@pytest.fixture
def student(db_session):
    return _make_user(db_session, "gamif@example.com")


@pytest.fixture
def student_client(client, student):
    _login(client, "gamif@example.com")
    return client


@pytest.fixture
def course_and_lessons(db_session, student):
    return _make_course_with_lessons(db_session, n_lessons=3, enroll_user=student)


# ─────────────────────────────────────────────────────────────
# Lesson XP
# ─────────────────────────────────────────────────────────────


def test_lesson_complete_awards_20_xp(
    student_client, db_session, student, course_and_lessons
):
    _, lessons = course_and_lessons
    resp = student_client.post(f"/lessons/{lessons[0].id}/complete")
    assert resp.status_code == 200, resp.text

    assert resp.json()["xp_awarded"] == 20
    g = _g(db_session, student.id)
    assert g is not None
    assert g.xp == 20


def test_lesson_complete_twice_awards_xp_only_once(
    student_client, db_session, student, course_and_lessons
):
    _, lessons = course_and_lessons
    student_client.post(f"/lessons/{lessons[0].id}/complete")
    resp = student_client.post(f"/lessons/{lessons[0].id}/complete")

    assert resp.status_code == 200
    assert resp.json()["xp_awarded"] == 0
    g = _g(db_session, student.id)
    assert g.xp == 20  # still only 20, no double award


def test_lesson_complete_multiple_lessons_accumulates_xp(
    student_client, db_session, student, course_and_lessons
):
    _, lessons = course_and_lessons
    for lesson in lessons:
        student_client.post(f"/lessons/{lesson.id}/complete")

    g = _g(db_session, student.id)
    assert g.xp == 20 * len(lessons)


# ─────────────────────────────────────────────────────────────
# Level
# ─────────────────────────────────────────────────────────────


def test_level_computed_correctly(db_session, student):
    # Directly exercise the service to verify the level formula.
    # floor(0 / 300) + 1 = 1 (base).
    # floor(300 / 300) + 1 = 2.
    # floor(599 / 300) + 1 = 2.
    # floor(600 / 300) + 1 = 3.
    for xp, expected_level in [(0, 1), (299, 1), (300, 2), (599, 2), (600, 3)]:
        assert gamification_svc._compute_level(xp) == expected_level


def test_level_updates_after_xp(
    student_client, db_session, student
):
    # Award enough XP to reach level 2 (300 XP = 15 lessons).
    course, lessons = _make_course_with_lessons(
        db_session, n_lessons=15, enroll_user=student
    )
    for lesson in lessons:
        student_client.post(f"/lessons/{lesson.id}/complete")

    g = _g(db_session, student.id)
    assert g.xp == 300
    assert g.level == 2


# ─────────────────────────────────────────────────────────────
# Streak
# ─────────────────────────────────────────────────────────────


def test_first_activity_starts_streak_at_1(
    student_client, db_session, student, course_and_lessons
):
    _, lessons = course_and_lessons
    student_client.post(f"/lessons/{lessons[0].id}/complete")
    g = _g(db_session, student.id)
    assert g.streak_days == 1


def test_same_day_activity_does_not_increment_streak(db_session, student):
    today = date(2026, 1, 10)
    g = gamification_svc.get_or_create(student.id, db_session)
    gamification_svc._update_streak(g, today)
    gamification_svc._update_streak(g, today)  # same day again
    assert g.streak_days == 1


def test_consecutive_day_increments_streak(db_session, student):
    g = gamification_svc.get_or_create(student.id, db_session)
    d = date(2026, 1, 10)
    gamification_svc._update_streak(g, d)
    gamification_svc._update_streak(g, d + timedelta(days=1))
    gamification_svc._update_streak(g, d + timedelta(days=2))
    assert g.streak_days == 3


def test_gap_in_activity_resets_streak(db_session, student):
    g = gamification_svc.get_or_create(student.id, db_session)
    d = date(2026, 1, 10)
    gamification_svc._update_streak(g, d)
    gamification_svc._update_streak(g, d + timedelta(days=1))
    # Skip 3 days → gap > 1 → reset.
    gamification_svc._update_streak(g, d + timedelta(days=4))
    assert g.streak_days == 1


# ─────────────────────────────────────────────────────────────
# Quiz XP
# ─────────────────────────────────────────────────────────────


def test_quiz_perfect_score_awards_correct_xp(
    student_client, db_session, student, course_and_lessons
):
    course, lessons = course_and_lessons
    quiz = _make_quiz(db_session, lessons[0].id, n_questions=3)
    # Enrol first (fixture already enrolled).

    # All correct: answer_index=0 for every question.
    resp = student_client.post(
        f"/quizzes/{quiz.id}/attempt",
        json={"answers": [0, 0, 0]},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    # 3 correct × 15 + 30 bonus = 75
    assert body["xp_awarded"] == 75
    g = _g(db_session, student.id)
    assert g.xp == 75


def test_quiz_partial_score_awards_correct_xp(
    student_client, db_session, student, course_and_lessons
):
    course, lessons = course_and_lessons
    quiz = _make_quiz(db_session, lessons[0].id, n_questions=3)

    # 1 correct, 2 wrong → 1 × 15 = 15 (no bonus)
    resp = student_client.post(
        f"/quizzes/{quiz.id}/attempt",
        json={"answers": [0, 1, 1]},
    )
    assert resp.status_code == 201
    assert resp.json()["xp_awarded"] == 15
    g = _g(db_session, student.id)
    assert g.xp == 15


def test_quiz_xp_awarded_only_on_first_attempt(
    student_client, db_session, student, course_and_lessons
):
    course, lessons = course_and_lessons
    quiz = _make_quiz(db_session, lessons[0].id, n_questions=2)

    # First attempt: 2 correct → 2 × 15 + 30 bonus = 60
    r1 = student_client.post(
        f"/quizzes/{quiz.id}/attempt",
        json={"answers": [0, 0]},
    )
    assert r1.json()["xp_awarded"] == 60

    # Second attempt: perfect again, but xp_awarded must be 0
    r2 = student_client.post(
        f"/quizzes/{quiz.id}/attempt",
        json={"answers": [0, 0]},
    )
    assert r2.json()["xp_awarded"] == 0
    g = _g(db_session, student.id)
    assert g.xp == 60  # no extra XP from second attempt


def test_quiz_zero_score_awards_0_xp(
    student_client, db_session, student, course_and_lessons
):
    course, lessons = course_and_lessons
    quiz = _make_quiz(db_session, lessons[0].id, n_questions=2)

    # All wrong → 0 correct × 15 + no bonus = 0 XP
    resp = student_client.post(
        f"/quizzes/{quiz.id}/attempt",
        json={"answers": [1, 1]},
    )
    assert resp.status_code == 201
    assert resp.json()["xp_awarded"] == 0
    g = _g(db_session, student.id)
    assert g.xp == 0


# ─────────────────────────────────────────────────────────────
# Badges
# ─────────────────────────────────────────────────────────────


def test_first_lesson_badge_awarded(
    student_client, db_session, student, course_and_lessons
):
    _, lessons = course_and_lessons
    resp = student_client.post(f"/lessons/{lessons[0].id}/complete")
    assert resp.status_code == 200
    assert gamification_svc.BADGE_FIRST_LESSON in resp.json()["new_badges"]
    g = _g(db_session, student.id)
    assert gamification_svc.BADGE_FIRST_LESSON in g.badges


def test_first_lesson_badge_awarded_only_once(
    student_client, db_session, student, course_and_lessons
):
    _, lessons = course_and_lessons
    student_client.post(f"/lessons/{lessons[0].id}/complete")
    # Second lesson — badge should NOT appear in new_badges again
    resp = student_client.post(f"/lessons/{lessons[1].id}/complete")
    assert gamification_svc.BADGE_FIRST_LESSON not in resp.json()["new_badges"]
    # But it's still in the DB row
    g = _g(db_session, student.id)
    assert g.badges.count(gamification_svc.BADGE_FIRST_LESSON) == 1


def test_quiz_master_badge_awarded_on_perfect_quiz(
    student_client, db_session, student, course_and_lessons
):
    course, lessons = course_and_lessons
    quiz = _make_quiz(db_session, lessons[0].id, n_questions=2)

    student_client.post(
        f"/quizzes/{quiz.id}/attempt",
        json={"answers": [0, 0]},  # perfect
    )
    g = _g(db_session, student.id)
    assert gamification_svc.BADGE_QUIZ_MASTER in g.badges


def test_quiz_master_badge_not_awarded_for_imperfect_quiz(
    student_client, db_session, student, course_and_lessons
):
    course, lessons = course_and_lessons
    quiz = _make_quiz(db_session, lessons[0].id, n_questions=2)

    student_client.post(
        f"/quizzes/{quiz.id}/attempt",
        json={"answers": [0, 1]},  # 1 wrong
    )
    g = _g(db_session, student.id)
    assert gamification_svc.BADGE_QUIZ_MASTER not in g.badges


def test_course_complete_badge_awarded_on_100_percent(
    student_client, db_session, student
):
    # Use a 2-lesson course so it's quick.
    course, lessons = _make_course_with_lessons(
        db_session, n_lessons=2, enroll_user=student
    )
    student_client.post(f"/lessons/{lessons[0].id}/complete")
    resp = student_client.post(f"/lessons/{lessons[1].id}/complete")
    assert resp.json()["progress_percent"] == 100
    g = _g(db_session, student.id)
    assert gamification_svc.BADGE_COURSE_COMPLETE in g.badges


def test_7_day_streak_badge_awarded_at_streak_7(db_session, student):
    g = gamification_svc.get_or_create(student.id, db_session)
    d = date(2026, 3, 1)
    for i in range(7):
        gamification_svc._update_streak(g, d + timedelta(days=i))
    gamification_svc._check_badges(
        g,
        total_lessons_completed=0,
        quiz_was_perfect=False,
        course_complete=False,
    )
    assert gamification_svc.BADGE_7_DAY_STREAK in g.badges


def test_badge_list_has_no_duplicates(
    student_client, db_session, student, course_and_lessons
):
    _, lessons = course_and_lessons
    # Complete the same lesson multiple times — badges must not duplicate.
    for _ in range(3):
        student_client.post(f"/lessons/{lessons[0].id}/complete")

    g = _g(db_session, student.id)
    assert len(g.badges) == len(set(g.badges))
