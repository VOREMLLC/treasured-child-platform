"""Admin-gated endpoints (S10 + S26).

S10: GET /admin/ping  — RBAC smoke test.
S26: Applications queue, user management, course list, payments, KPIs.
Safeguarding: tutor conversations flagged by the safety pipeline.

All endpoints require role=admin. The role guard is the ONLY access
control needed here — there is no per-resource ownership check because
admins own everything.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.api.deps import requires_role
from app.db.session import get_db
from app.models.agent_run import AgentRun
from app.models.application import Application, ApplicationStatus
from app.models.audit_log import AuditLog
from app.models.course import Course
from app.models.enrolment import Enrolment, EnrolmentStatus
from app.models.lesson_progress import LessonProgress
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole, UserStatus
from app.schemas.admin import (
    AdminCourseItem,
    AdminPaymentItem,
    AdminUserItem,
    ApplicationListItem,
    FlaggedRunItem,
    ApplicationStatusUpdate,
    KPIResponse,
    UserStatusUpdate,
)

router = APIRouter(prefix="/admin", tags=["admin"])

_admin = Depends(requires_role(UserRole.admin))


# ─────────────────────────────────────────────────────────────
# Ping (S10)
# ─────────────────────────────────────────────────────────────


@router.get("/ping")
def admin_ping(user: User = _admin) -> dict:
    """Liveness check, admin-only."""
    return {"ok": True, "email": user.email}


# ─────────────────────────────────────────────────────────────
# Applications queue
# ─────────────────────────────────────────────────────────────


@router.get("/applications", response_model=List[ApplicationListItem])
def list_applications(
    status: Optional[ApplicationStatus] = Query(default=None),
    actor: User = _admin,
    db: Session = Depends(get_db),
) -> List[Application]:
    q = db.query(Application)
    if status is not None:
        q = q.filter(Application.status == status)
    return q.order_by(Application.created_at.desc()).all()


@router.patch("/applications/{application_id}", response_model=ApplicationListItem)
def update_application_status(
    application_id: uuid.UUID,
    body: ApplicationStatusUpdate,
    actor: User = _admin,
    db: Session = Depends(get_db),
) -> Application:
    app = db.get(Application, application_id)
    if app is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    old_status = app.status.value
    app.status = body.status

    db.add(AuditLog(
        actor_id=actor.id,
        action="update_application_status",
        resource_type="application",
        resource_id=str(application_id),
        notes=f"{old_status} -> {body.status.value}",
    ))
    db.commit()
    db.refresh(app)
    return app


# ─────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────


@router.get("/users", response_model=List[AdminUserItem])
def list_users(
    role: Optional[UserRole] = Query(default=None),
    actor: User = _admin,
    db: Session = Depends(get_db),
) -> List[User]:
    q = db.query(User)
    if role is not None:
        q = q.filter(User.role == role)
    return q.order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}", response_model=AdminUserItem)
def update_user_status(
    user_id: uuid.UUID,
    body: UserStatusUpdate,
    actor: User = _admin,
    db: Session = Depends(get_db),
) -> User:
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    old_status = target.status.value
    target.status = body.status

    db.add(AuditLog(
        actor_id=actor.id,
        action="update_user_status",
        resource_type="user",
        resource_id=str(user_id),
        notes=f"{old_status} -> {body.status.value}",
    ))
    db.commit()
    db.refresh(target)
    return target


# ─────────────────────────────────────────────────────────────
# Courses
# ─────────────────────────────────────────────────────────────


@router.get("/courses", response_model=List[AdminCourseItem])
def list_courses(
    actor: User = _admin,
    db: Session = Depends(get_db),
) -> List[AdminCourseItem]:
    courses = db.query(Course).order_by(Course.title).all()
    items = []
    for course in courses:
        count = (
            db.query(Enrolment)
            .filter(Enrolment.course_id == course.id)
            .filter(Enrolment.status == EnrolmentStatus.active)
            .count()
        )
        items.append(AdminCourseItem(
            id=course.id,
            slug=course.slug,
            title=course.title,
            type=course.type.value,
            level=course.level,
            published=course.published,
            is_paid=course.is_paid,
            enrolment_count=count,
        ))
    return items


# ─────────────────────────────────────────────────────────────
# Payments
# ─────────────────────────────────────────────────────────────


@router.get("/payments", response_model=List[AdminPaymentItem])
def list_payments(
    actor: User = _admin,
    db: Session = Depends(get_db),
) -> List[AdminPaymentItem]:
    rows = (
        db.query(Payment, User)
        .join(User, User.id == Payment.payer_id)
        .order_by(Payment.created_at.desc())
        .limit(200)
        .all()
    )
    return [
        AdminPaymentItem(
            id=payment.id,
            payer_email=user.email,
            reference=payment.reference,
            amount_kobo=payment.amount_kobo,
            purpose=payment.purpose.value,
            target=payment.target,
            status=payment.status.value,
            created_at=payment.created_at,
        )
        for payment, user in rows
    ]


# ─────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────


@router.get("/kpis", response_model=KPIResponse)
def get_kpis(
    actor: User = _admin,
    db: Session = Depends(get_db),
) -> KPIResponse:
    # Revenue: sum of successful payments in kobo
    revenue_result = (
        db.query(sa_func.coalesce(sa_func.sum(Payment.amount_kobo), 0))
        .filter(Payment.status == PaymentStatus.success)
        .scalar()
    )
    total_revenue_kobo = int(revenue_result or 0)

    # Total active enrolments
    total_enrolments = (
        db.query(Enrolment)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .count()
    )

    # Weekly active learners: distinct learners with lesson_progress in last 7 days
    seven_days_ago = datetime.now(tz=timezone.utc) - timedelta(days=7)
    weekly_active_learners = (
        db.query(LessonProgress.learner_id)
        .filter(LessonProgress.completed_at >= seven_days_ago)
        .distinct()
        .count()
    )

    # Course completions: (learner, course) pairs where every lesson is done
    # Strategy: count enrolments where computed progress = 100.
    # Efficient approximation: count distinct (learner_id, course_id) in lesson_progress
    # where lesson count matches total lessons in course.
    # We do this in Python to stay ORM-only and avoid raw SQL.
    from app.api.courses import compute_progress
    from app.models.course import Module, Lesson

    active_enrolments = (
        db.query(Enrolment)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .all()
    )
    course_completions = sum(
        1
        for e in active_enrolments
        if compute_progress(db, e.learner_id, e.course_id) == 100
    )

    return KPIResponse(
        total_revenue_kobo=total_revenue_kobo,
        total_enrolments=total_enrolments,
        weekly_active_learners=weekly_active_learners,
        course_completions=course_completions,
    )


# ─────────────────────────────────────────────────────────────
# Safeguarding queue
# ─────────────────────────────────────────────────────────────


@router.get("/flagged-runs", response_model=List[FlaggedRunItem])
def list_flagged_runs(
    _user: User = _admin,
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
) -> List[FlaggedRunItem]:
    """Tutor conversations the safety pipeline flagged, newest first."""
    rows = (
        db.query(AgentRun, User)
        .outerjoin(User, User.id == AgentRun.learner_id)
        .filter(AgentRun.flagged.is_(True))
        .order_by(AgentRun.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        FlaggedRunItem(
            id=run.id,
            learner_id=run.learner_id,
            learner_name=learner.name if learner else None,
            learner_email=learner.email if learner else None,
            input=run.input,
            output=run.output,
            created_at=run.created_at,
        )
        for run, learner in rows
    ]
