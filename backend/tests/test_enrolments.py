"""Tests for POST /enrolments — S18 (free) and S19 (paid, payment-gated).

S18 acceptance criteria
  - Enrol in a free course → 201, Enrolment row in DB.
  - Same student enrols twice → 409, only one row.
  - Unknown course → 404.
  - Unpublished course → 404.
  - Unauthenticated → 401.

S19 acceptance criteria
  - Enrol in a paid course without any payment → 402, no row.
  - Enrol with a pending (unverified) payment → 402, no row.
  - Enrol after a successful payment → 201, Enrolment row with source=paid.
  - Tampered client claim (no matching server payment) → 402.
  - Payment-success path (verify) auto-creates Enrolment server-side
    — calling POST /enrolments after that returns 409 (already enrolled).
  - Webhook path also auto-creates Enrolment server-side.
"""

import uuid
from unittest.mock import patch

import pytest

from app.models.course import Course, CourseType
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.models.user import User, UserRole, UserStatus
from app.services.security import hash_password


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def student(db_session):
    user = User(
        email="student@enrol.example.com",
        name="Enrol Student",
        password_hash=hash_password("pass-12345"),
        role=UserRole.student,
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_client(client, student):
    resp = client.post(
        "/auth/login",
        json={"email": "student@enrol.example.com", "password": "pass-12345"},
    )
    assert resp.status_code == 200
    return client


@pytest.fixture
def free_course(db_session):
    course = Course(
        slug="jss-1-enrol",
        title="JSS 1",
        type=CourseType.school,
        level="JSS",
        summary="Free school course.",
        is_paid=False,
        published=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def paid_course(db_session):
    course = Course(
        slug="ai-data",
        title="AI & data analytics",
        type=CourseType.online,
        level="Online",
        summary="Paid online course.",
        is_paid=True,
        price_kobo=3_500_000,
        published=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def unpublished_course(db_session):
    course = Course(
        slug="draft-course",
        title="Draft",
        type=CourseType.online,
        level="Online",
        summary="Not published.",
        is_paid=False,
        published=False,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def _make_success_payment(db_session, payer, course_slug: str) -> Payment:
    """Insert a verified programme payment directly into the DB."""
    p = Payment(
        payer_id=payer.id,
        reference=f"TCS-{uuid.uuid4().hex[:12]}",
        amount_kobo=3_500_000,
        purpose=PaymentPurpose.programme,
        target=course_slug,
        status=PaymentStatus.success,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


def _paystack_success_body(reference: str, amount: int) -> dict:
    return {
        "status": True,
        "message": "Verification successful",
        "data": {
            "status": "success",
            "amount": amount,
            "reference": reference,
            "paid_at": "2026-06-13T10:00:00Z",
            "channel": "card",
            "currency": "NGN",
        },
    }


# ─────────────────────────────────────────────────────────────
# S18 — free-course enrolment
# ─────────────────────────────────────────────────────────────


def test_enrol_without_session_returns_401(client, free_course):
    resp = client.post("/enrolments", json={"course_id": str(free_course.id)})
    assert resp.status_code == 401


def test_enrol_free_course_creates_enrolment(
    student_client, db_session, student, free_course
):
    resp = student_client.post(
        "/enrolments", json={"course_id": str(free_course.id)}
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["course_id"] == str(free_course.id)
    assert body["learner_id"] == str(student.id)
    assert body["source"] == "free"
    assert body["status"] == "active"

    row = (
        db_session.query(Enrolment)
        .filter(Enrolment.learner_id == student.id)
        .filter(Enrolment.course_id == free_course.id)
        .first()
    )
    assert row is not None
    assert row.source is EnrolmentSource.free


def test_enrol_free_course_twice_returns_409(
    student_client, db_session, student, free_course
):
    student_client.post("/enrolments", json={"course_id": str(free_course.id)})
    resp = student_client.post(
        "/enrolments", json={"course_id": str(free_course.id)}
    )
    assert resp.status_code == 409

    count = (
        db_session.query(Enrolment)
        .filter(Enrolment.learner_id == student.id)
        .filter(Enrolment.course_id == free_course.id)
        .count()
    )
    assert count == 1


def test_enrol_unknown_course_returns_404(student_client):
    resp = student_client.post(
        "/enrolments", json={"course_id": str(uuid.uuid4())}
    )
    assert resp.status_code == 404


def test_enrol_unpublished_course_returns_404(
    student_client, unpublished_course
):
    resp = student_client.post(
        "/enrolments", json={"course_id": str(unpublished_course.id)}
    )
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────
# S19 — paid-course enrolment gated by verified payment
# ─────────────────────────────────────────────────────────────


def test_enrol_paid_course_without_payment_returns_402(
    student_client, paid_course
):
    resp = student_client.post(
        "/enrolments", json={"course_id": str(paid_course.id)}
    )
    assert resp.status_code == 402


def test_enrol_paid_course_with_pending_payment_returns_402(
    student_client, db_session, student, paid_course
):
    p = Payment(
        payer_id=student.id,
        reference="TCS-pending-ref",
        amount_kobo=3_500_000,
        purpose=PaymentPurpose.programme,
        target=paid_course.slug,
        status=PaymentStatus.pending,
    )
    db_session.add(p)
    db_session.commit()

    resp = student_client.post(
        "/enrolments", json={"course_id": str(paid_course.id)}
    )
    assert resp.status_code == 402


def test_enrol_paid_course_after_verified_payment_returns_201(
    student_client, db_session, student, paid_course
):
    _make_success_payment(db_session, student, paid_course.slug)

    resp = student_client.post(
        "/enrolments", json={"course_id": str(paid_course.id)}
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["source"] == "paid"
    assert body["status"] == "active"

    row = (
        db_session.query(Enrolment)
        .filter(Enrolment.learner_id == student.id)
        .filter(Enrolment.course_id == paid_course.id)
        .first()
    )
    assert row is not None
    assert row.source is EnrolmentSource.paid


def test_enrol_paid_course_wrong_slug_returns_402(
    student_client, db_session, student, paid_course
):
    """Payment for a DIFFERENT programme does not unlock this course."""
    p = Payment(
        payer_id=student.id,
        reference="TCS-wrong-slug",
        amount_kobo=2_000_000,
        purpose=PaymentPurpose.programme,
        target="bece-prep",          # different programme
        status=PaymentStatus.success,
    )
    db_session.add(p)
    db_session.commit()

    resp = student_client.post(
        "/enrolments", json={"course_id": str(paid_course.id)}
    )
    assert resp.status_code == 402


# ─────────────────────────────────────────────────────────────
# S19 — auto-enrol on payment verify (server-side grant)
# ─────────────────────────────────────────────────────────────


def test_verify_success_auto_creates_enrolment(
    student_client, db_session, student, paid_course
):
    """POST /payments/verify on a programme payment auto-creates Enrolment."""
    pending = Payment(
        payer_id=student.id,
        reference="TCS-auto-enrol-verify",
        amount_kobo=3_500_000,
        purpose=PaymentPurpose.programme,
        target=paid_course.slug,
        status=PaymentStatus.pending,
    )
    db_session.add(pending)
    db_session.commit()

    with patch(
        "app.api.payments.paystack.verify_transaction",
        return_value=_paystack_success_body(
            "TCS-auto-enrol-verify", 3_500_000
        ),
    ):
        resp = student_client.post(
            "/payments/verify",
            json={"reference": "TCS-auto-enrol-verify"},
        )

    assert resp.status_code == 200, resp.text

    enrolment = (
        db_session.query(Enrolment)
        .filter(Enrolment.learner_id == student.id)
        .filter(Enrolment.course_id == paid_course.id)
        .first()
    )
    assert enrolment is not None
    assert enrolment.source is EnrolmentSource.paid
    assert enrolment.status is EnrolmentStatus.active


def test_verify_auto_enrol_then_post_enrolments_returns_409(
    student_client, db_session, student, paid_course
):
    """After auto-enrol via verify, POST /enrolments returns 409 — not 402."""
    pending = Payment(
        payer_id=student.id,
        reference="TCS-double-check",
        amount_kobo=3_500_000,
        purpose=PaymentPurpose.programme,
        target=paid_course.slug,
        status=PaymentStatus.pending,
    )
    db_session.add(pending)
    db_session.commit()

    with patch(
        "app.api.payments.paystack.verify_transaction",
        return_value=_paystack_success_body("TCS-double-check", 3_500_000),
    ):
        student_client.post(
            "/payments/verify", json={"reference": "TCS-double-check"}
        )

    # Now try to enrol manually — must 409, not 402, since already enrolled.
    resp = student_client.post(
        "/enrolments", json={"course_id": str(paid_course.id)}
    )
    assert resp.status_code == 409


def test_verify_idempotent_does_not_double_enrol(
    student_client, db_session, student, paid_course
):
    """Re-verifying an already-success payment must not create two enrolments."""
    pending = Payment(
        payer_id=student.id,
        reference="TCS-idempotent-enrol",
        amount_kobo=3_500_000,
        purpose=PaymentPurpose.programme,
        target=paid_course.slug,
        status=PaymentStatus.pending,
    )
    db_session.add(pending)
    db_session.commit()

    success_body = _paystack_success_body("TCS-idempotent-enrol", 3_500_000)
    with patch(
        "app.api.payments.paystack.verify_transaction",
        return_value=success_body,
    ):
        student_client.post(
            "/payments/verify", json={"reference": "TCS-idempotent-enrol"}
        )
        # Second verify — idempotent path (payment already success)
        student_client.post(
            "/payments/verify", json={"reference": "TCS-idempotent-enrol"}
        )

    count = (
        db_session.query(Enrolment)
        .filter(Enrolment.learner_id == student.id)
        .filter(Enrolment.course_id == paid_course.id)
        .count()
    )
    assert count == 1


# ─────────────────────────────────────────────────────────────
# S19 — auto-enrol on webhook (server-side grant)
# ─────────────────────────────────────────────────────────────


def test_webhook_success_auto_creates_enrolment(
    client, db_session, student, paid_course
):
    """Paystack webhook charge.success auto-creates Enrolment."""
    import hashlib
    import hmac
    import json

    from app.core.config import settings

    pending = Payment(
        payer_id=student.id,
        reference="TCS-webhook-enrol",
        amount_kobo=3_500_000,
        purpose=PaymentPurpose.programme,
        target=paid_course.slug,
        status=PaymentStatus.pending,
    )
    db_session.add(pending)
    db_session.commit()

    payload = {
        "event": "charge.success",
        "data": {
            "reference": "TCS-webhook-enrol",
            "status": "success",
            "amount": 3_500_000,
            "currency": "NGN",
        },
    }
    body_bytes = json.dumps(payload).encode()
    sig = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(), body_bytes, hashlib.sha512
    ).hexdigest()

    resp = client.post(
        "/payments/webhook/paystack",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "x-paystack-signature": sig,
        },
    )
    assert resp.status_code == 200, resp.text

    enrolment = (
        db_session.query(Enrolment)
        .filter(Enrolment.learner_id == student.id)
        .filter(Enrolment.course_id == paid_course.id)
        .first()
    )
    assert enrolment is not None
    assert enrolment.source is EnrolmentSource.paid


def test_webhook_idempotent_does_not_double_enrol(
    client, db_session, student, paid_course
):
    """Replaying the same webhook must not create two enrolment rows."""
    import hashlib
    import hmac
    import json

    from app.core.config import settings

    pending = Payment(
        payer_id=student.id,
        reference="TCS-webhook-idempotent",
        amount_kobo=3_500_000,
        purpose=PaymentPurpose.programme,
        target=paid_course.slug,
        status=PaymentStatus.pending,
    )
    db_session.add(pending)
    db_session.commit()

    payload = {
        "event": "charge.success",
        "data": {
            "reference": "TCS-webhook-idempotent",
            "status": "success",
            "amount": 3_500_000,
            "currency": "NGN",
        },
    }
    body_bytes = json.dumps(payload).encode()
    sig = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(), body_bytes, hashlib.sha512
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "x-paystack-signature": sig,
    }
    client.post("/payments/webhook/paystack", content=body_bytes, headers=headers)
    client.post("/payments/webhook/paystack", content=body_bytes, headers=headers)

    count = (
        db_session.query(Enrolment)
        .filter(Enrolment.learner_id == student.id)
        .filter(Enrolment.course_id == paid_course.id)
        .count()
    )
    assert count == 1
