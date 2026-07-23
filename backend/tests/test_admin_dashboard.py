"""Tests for S26 — Admin dashboard endpoints.

Covers:
  - All endpoints return 401 without a session.
  - All endpoints return 403 for non-admin users (student).
  - GET /admin/applications — lists all, filters by status.
  - PATCH /admin/applications/{id} — flips status, writes AuditLog.
  - GET /admin/users — lists users, filters by role.
  - PATCH /admin/users/{id} — changes user status, writes AuditLog.
  - GET /admin/courses — lists courses with enrolment_count.
  - GET /admin/payments — lists payments with payer_email.
  - GET /admin/kpis — revenue, enrolments, WAL, completions.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.application import Application, ApplicationStatus, ClassLevel
from app.models.audit_log import AuditLog
from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.lesson_progress import LessonProgress
from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _make_user(db, email: str, role: UserRole = UserRole.student) -> User:
    u = User(
        email=email,
        name=f"Test {role.value}",
        password_hash=hash_password("pw-test-1234"),
        role=role,
        status=UserStatus.active,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _login(client, email: str) -> None:
    r = client.post("/auth/login", json={"email": email, "password": "pw-test-1234"})
    assert r.status_code == 200, r.text


def _make_application(db, status: ApplicationStatus = ApplicationStatus.new) -> Application:
    a = Application(
        child_name="Timi Obi",
        guardian_name="Mrs Obi",
        email=f"obi-{uuid.uuid4().hex[:6]}@example.com",
        phone="08012345678",
        class_level=ClassLevel.primary,
        status=status,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _make_course(db, *, n_lessons: int = 2, is_paid: bool = False) -> tuple:
    course = Course(
        slug=f"admin-course-{uuid.uuid4().hex[:6]}",
        title="Admin Test Course",
        type=CourseType.online,
        level="SS 1",
        summary=".",
        is_paid=is_paid,
        published=True,
    )
    db.add(course)
    db.flush()
    module = Module(course_id=course.id, sort_order=1, title="M1")
    db.add(module)
    db.flush()
    lessons = []
    for i in range(1, n_lessons + 1):
        l = Lesson(module_id=module.id, sort_order=i, title=f"L{i}", content=".", duration_min=5)
        db.add(l)
        lessons.append(l)
    db.commit()
    for l in lessons:
        db.refresh(l)
    db.refresh(course)
    return course, lessons


def _make_payment(db, payer_id, *, amount_kobo: int = 1000_000,
                  status: PaymentStatus = PaymentStatus.success) -> Payment:
    p = Payment(
        payer_id=payer_id,
        reference=f"ref-{uuid.uuid4().hex[:10]}",
        amount_kobo=amount_kobo,
        purpose=PaymentPurpose.fees,
        status=status,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def admin(db_session):
    return _make_user(db_session, "admin@tc.edu", UserRole.admin)


@pytest.fixture
def student(db_session):
    return _make_user(db_session, "student@tc.edu", UserRole.student)


@pytest.fixture
def admin_client(client, admin):
    _login(client, "admin@tc.edu")
    return client


@pytest.fixture
def student_client(client, student):
    _login(client, "student@tc.edu")
    return client


# ─────────────────────────────────────────────────────────────
# Auth + RBAC guards on every admin endpoint
# ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("method,path", [
    ("GET",   "/admin/applications"),
    ("GET",   "/admin/users"),
    ("GET",   "/admin/courses"),
    ("GET",   "/admin/payments"),
    ("GET",   "/admin/kpis"),
])
def test_admin_endpoints_require_session(client, method, path):
    r = getattr(client, method.lower())(path)
    assert r.status_code == 401


@pytest.mark.parametrize("method,path", [
    ("GET",   "/admin/applications"),
    ("GET",   "/admin/users"),
    ("GET",   "/admin/courses"),
    ("GET",   "/admin/payments"),
    ("GET",   "/admin/kpis"),
])
def test_admin_endpoints_require_admin_role(student_client, method, path):
    r = getattr(student_client, method.lower())(path)
    assert r.status_code == 403


# ─────────────────────────────────────────────────────────────
# Applications queue
# ─────────────────────────────────────────────────────────────


def test_list_applications_returns_all(admin_client, db_session):
    _make_application(db_session, ApplicationStatus.new)
    _make_application(db_session, ApplicationStatus.contacted)
    r = admin_client.get("/admin/applications")
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_list_applications_filters_by_status(admin_client, db_session):
    _make_application(db_session, ApplicationStatus.new)
    _make_application(db_session, ApplicationStatus.enrolled)
    r = admin_client.get("/admin/applications?status=new")
    assert r.status_code == 200
    statuses = {item["status"] for item in r.json()}
    assert statuses == {"new"}


def test_update_application_status_flips_status(admin_client, db_session):
    app = _make_application(db_session, ApplicationStatus.new)
    r = admin_client.patch(
        f"/admin/applications/{app.id}",
        json={"status": "contacted"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "contacted"


def test_update_application_status_writes_audit_log(admin_client, db_session, admin):
    app = _make_application(db_session, ApplicationStatus.new)
    admin_client.patch(f"/admin/applications/{app.id}", json={"status": "enrolled"})

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.resource_type == "application")
        .filter(AuditLog.resource_id == str(app.id))
        .first()
    )
    assert log is not None
    assert log.action == "update_application_status"
    assert log.actor_id == admin.id
    assert "new" in log.notes
    assert "enrolled" in log.notes


def test_update_application_status_unknown_id_returns_404(admin_client):
    r = admin_client.patch(
        f"/admin/applications/{uuid.uuid4()}",
        json={"status": "contacted"},
    )
    assert r.status_code == 404


# ─────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────


def test_list_users_returns_all(admin_client, db_session, admin, student):
    r = admin_client.get("/admin/users")
    assert r.status_code == 200
    emails = {u["email"] for u in r.json()}
    assert admin.email in emails
    assert student.email in emails


def test_list_users_filters_by_role(admin_client, db_session, admin, student):
    r = admin_client.get("/admin/users?role=student")
    assert r.status_code == 200
    roles = {u["role"] for u in r.json()}
    assert roles == {"student"}


def test_update_user_status_suspends_user(admin_client, db_session, student):
    r = admin_client.patch(
        f"/admin/users/{student.id}",
        json={"status": "suspended"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "suspended"


def test_update_user_status_writes_audit_log(admin_client, db_session, admin, student):
    admin_client.patch(f"/admin/users/{student.id}", json={"status": "suspended"})

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.resource_type == "user")
        .filter(AuditLog.resource_id == str(student.id))
        .first()
    )
    assert log is not None
    assert log.action == "update_user_status"
    assert log.actor_id == admin.id
    assert "active" in log.notes
    assert "suspended" in log.notes


def test_update_user_unknown_id_returns_404(admin_client):
    r = admin_client.patch(f"/admin/users/{uuid.uuid4()}", json={"status": "active"})
    assert r.status_code == 404


# ─────────────────────────────────────────────────────────────
# Courses
# ─────────────────────────────────────────────────────────────


def test_list_courses_shows_enrolment_count(admin_client, db_session, student):
    course, _ = _make_course(db_session)
    db_session.add(Enrolment(
        learner_id=student.id,
        course_id=course.id,
        status=EnrolmentStatus.active,
        source=EnrolmentSource.free,
    ))
    db_session.commit()

    r = admin_client.get("/admin/courses")
    assert r.status_code == 200
    found = next((c for c in r.json() if c["id"] == str(course.id)), None)
    assert found is not None
    assert found["enrolment_count"] == 1


def test_list_courses_expired_enrolments_not_counted(admin_client, db_session, student):
    course, _ = _make_course(db_session)
    db_session.add(Enrolment(
        learner_id=student.id,
        course_id=course.id,
        status=EnrolmentStatus.expired,
        source=EnrolmentSource.free,
    ))
    db_session.commit()

    r = admin_client.get("/admin/courses")
    found = next((c for c in r.json() if c["id"] == str(course.id)), None)
    assert found["enrolment_count"] == 0


# ─────────────────────────────────────────────────────────────
# Payments
# ─────────────────────────────────────────────────────────────


def test_list_payments_includes_payer_email(admin_client, db_session, student):
    _make_payment(db_session, student.id, amount_kobo=500_000)
    r = admin_client.get("/admin/payments")
    assert r.status_code == 200
    assert any(p["payer_email"] == student.email for p in r.json())


def test_list_payments_shows_status(admin_client, db_session, student):
    _make_payment(db_session, student.id, status=PaymentStatus.failed)
    r = admin_client.get("/admin/payments")
    assert any(p["status"] == "failed" for p in r.json())


# ─────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────


def test_kpis_revenue_sums_successful_payments(admin_client, db_session, student):
    _make_payment(db_session, student.id, amount_kobo=1_000_000, status=PaymentStatus.success)
    _make_payment(db_session, student.id, amount_kobo=500_000, status=PaymentStatus.success)
    _make_payment(db_session, student.id, amount_kobo=200_000, status=PaymentStatus.failed)

    r = admin_client.get("/admin/kpis")
    assert r.status_code == 200
    assert r.json()["total_revenue_kobo"] == 1_500_000


def test_kpis_revenue_is_zero_when_no_payments(admin_client):
    r = admin_client.get("/admin/kpis")
    assert r.json()["total_revenue_kobo"] == 0


def test_kpis_enrolment_count_matches_active_enrolments(admin_client, db_session, student):
    course, _ = _make_course(db_session)
    db_session.add(Enrolment(
        learner_id=student.id,
        course_id=course.id,
        status=EnrolmentStatus.active,
        source=EnrolmentSource.free,
    ))
    db_session.commit()

    r = admin_client.get("/admin/kpis")
    assert r.json()["total_enrolments"] >= 1


def test_kpis_weekly_active_learners_counts_recent_activity(
    admin_client, db_session, student
):
    course, lessons = _make_course(db_session)
    db_session.add(LessonProgress(
        learner_id=student.id,
        lesson_id=lessons[0].id,
        completed_at=datetime.now(tz=timezone.utc),
    ))
    db_session.commit()

    r = admin_client.get("/admin/kpis")
    assert r.json()["weekly_active_learners"] >= 1


def test_kpis_weekly_active_learners_excludes_old_activity(
    admin_client, db_session, student
):
    course, lessons = _make_course(db_session)
    db_session.add(LessonProgress(
        learner_id=student.id,
        lesson_id=lessons[0].id,
        completed_at=datetime.now(tz=timezone.utc) - timedelta(days=10),
    ))
    db_session.commit()

    r = admin_client.get("/admin/kpis")
    # This learner's old activity should NOT count toward WAL
    wal = r.json()["weekly_active_learners"]
    assert wal == 0


def test_kpis_course_completions_counts_100_percent_courses(
    admin_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=2)
    db_session.add(Enrolment(
        learner_id=student.id,
        course_id=course.id,
        status=EnrolmentStatus.active,
        source=EnrolmentSource.free,
    ))
    for l in lessons:
        db_session.add(LessonProgress(
            learner_id=student.id,
            lesson_id=l.id,
            completed_at=datetime.now(tz=timezone.utc),
        ))
    db_session.commit()

    r = admin_client.get("/admin/kpis")
    assert r.json()["course_completions"] >= 1


def test_kpis_course_completions_excludes_partial_completion(
    admin_client, db_session, student
):
    course, lessons = _make_course(db_session, n_lessons=3)
    db_session.add(Enrolment(
        learner_id=student.id,
        course_id=course.id,
        status=EnrolmentStatus.active,
        source=EnrolmentSource.free,
    ))
    # Complete only 1 of 3 lessons
    db_session.add(LessonProgress(
        learner_id=student.id,
        lesson_id=lessons[0].id,
        completed_at=datetime.now(tz=timezone.utc),
    ))
    db_session.commit()

    r = admin_client.get("/admin/kpis")
    assert r.json()["course_completions"] == 0
