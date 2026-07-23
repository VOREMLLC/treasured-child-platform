"""Pydantic shapes for POST /enrolments (S18 + S19)."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enrolment import EnrolmentSource, EnrolmentStatus


class EnrolmentRequest(BaseModel):
    """Body for ``POST /enrolments``."""

    course_id: uuid.UUID


class EnrolmentResponse(BaseModel):
    """Returned on successful enrolment."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    learner_id: uuid.UUID
    course_id: uuid.UUID
    status: EnrolmentStatus
    source: EnrolmentSource
    created_at: datetime
    access_expires_at: Optional[datetime]
