"""Enrolment endpoint (S18 + S19).

POST /enrolments  {course_id}

  S18 — free course (is_paid=False):
    Creates an Enrolment immediately. Returns 201.

  S19 — paid course (is_paid=True):
    Returns 402 Payment Required unless a Payment row with
    purpose=programme, target=course.slug, status=success already
    exists for this user.  The typical path is that the Payment-success
    path (verify / webhook) has already auto-created the Enrolment
    server-side, so calling this endpoint after paying will hit the
    409 double-enrolment guard — which is fine; the client can treat
    both 201 and 409 as "enrolled".

  Double-enrolment (either kind) → 409 Conflict.
  Unknown or unpublished course → 404.
  Unauthenticated → 401 (from get_current_user).

Design notes
  - Money is never trusted from the client.  The endpoint only checks
    whether a server-verified Payment exists — it never accepts a
    "payment_reference" argument.
  - The unique(learner_id, course_id) DB constraint is the hard
    safety net; the prior query is a fast-path early-exit.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.course import Course
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.models.user import User
from app.schemas.enrolment import EnrolmentRequest, EnrolmentResponse

router = APIRouter(prefix="/enrolments", tags=["enrolments"])

_ALREADY_ENROLLED = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Already enrolled in this course.",
)
_PAYMENT_REQUIRED = HTTPException(
    status_code=status.HTTP_402_PAYMENT_REQUIRED,
    detail="A verified payment is required to enrol in this course.",
)


@router.post("", response_model=EnrolmentResponse, status_code=201)
def enrol(
    payload: EnrolmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Enrolment:
    """Enrol the authenticated user in a course.

    - Free course → instant enrolment.
    - Paid course → requires a prior successful payment; returns 402
      if none exists.
    - Duplicate → 409 (both the pre-check and the DB constraint).
    """
    course = db.get(Course, payload.course_id)
    if course is None or not course.published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )

    # Fast-path duplicate check (the DB unique constraint is the safety
    # net for the concurrent case).
    existing = (
        db.query(Enrolment)
        .filter(Enrolment.learner_id == current_user.id)
        .filter(Enrolment.course_id == course.id)
        .first()
    )
    if existing is not None:
        raise _ALREADY_ENROLLED

    if course.is_paid:
        payment = (
            db.query(Payment)
            .filter(Payment.payer_id == current_user.id)
            .filter(Payment.purpose == PaymentPurpose.programme)
            .filter(Payment.target == course.slug)
            .filter(Payment.status == PaymentStatus.success)
            .first()
        )
        if payment is None:
            raise _PAYMENT_REQUIRED
        source = EnrolmentSource.paid
    else:
        source = EnrolmentSource.free

    row = Enrolment(
        learner_id=current_user.id,
        course_id=course.id,
        status=EnrolmentStatus.active,
        source=source,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        # Concurrent request beat us to the insert; the DB constraint
        # kept state consistent.
        db.rollback()
        raise _ALREADY_ENROLLED

    db.refresh(row)
    return row
