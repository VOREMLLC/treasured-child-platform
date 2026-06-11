"""POST /applications — public lead-capture endpoint."""

from fastapi import APIRouter, Body, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.application import Application, ApplicationStatus
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.services import email as email_service

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
def create_application(
    request: Request,  # noqa: ARG001  # required by slowapi for IP key
    payload: ApplicationCreate = Body(...),
    db: Session = Depends(get_db),
) -> Application:
    """Create a new admission application lead.

    Persists the application, sends a confirmation email to the parent,
    and a notification email to the admissions inbox. Both emails use
    the stubbed sender (see ``app.services.email``).
    """
    application = Application(
        child_name=payload.child_name,
        guardian_name=payload.guardian_name,
        email=str(payload.email),
        phone=payload.phone,
        class_level=payload.class_level,
        message=payload.message,
        status=ApplicationStatus.new,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    level_label = application.class_level.value.replace("_", " ")

    # Confirmation to the parent / guardian
    email_service.send_email(
        to=application.email,
        subject="Treasured Child School — application received",
        body=(
            f"Dear {application.guardian_name},\n\n"
            f"Thank you for your application for {application.child_name} "
            f"({level_label}). Our admissions team will be in touch by email "
            f"within 48 hours.\n\n"
            f"— Treasured Child School\n"
        ),
    )

    # Notification to the admissions inbox
    email_service.send_email(
        to=settings.ADMIN_EMAIL,
        subject=f"New application: {application.child_name}",
        body=(
            f"From: {application.guardian_name} <{application.email}>\n"
            f"Phone: {application.phone}\n"
            f"Class: {level_label}\n"
            f"Message: {application.message or '(none)'}\n"
        ),
    )

    return application
