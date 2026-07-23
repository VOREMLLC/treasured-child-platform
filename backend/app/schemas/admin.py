"""Pydantic shapes for admin dashboard endpoints (S26)."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.application import ApplicationStatus
from app.models.user import UserRole, UserStatus


# ─────────────────────────────────────────────────────────────
# Applications
# ─────────────────────────────────────────────────────────────


class ApplicationListItem(BaseModel):
    id: uuid.UUID
    child_name: str
    guardian_name: str
    email: str
    phone: str
    class_level: str
    message: Optional[str] = None
    status: str
    created_at: datetime


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


# ─────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────


class AdminUserItem(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    status: str
    created_at: datetime


class UserStatusUpdate(BaseModel):
    status: UserStatus


# ─────────────────────────────────────────────────────────────
# Courses
# ─────────────────────────────────────────────────────────────


class AdminCourseItem(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    type: str
    level: str
    published: bool
    is_paid: bool
    enrolment_count: int


# ─────────────────────────────────────────────────────────────
# Payments
# ─────────────────────────────────────────────────────────────


class AdminPaymentItem(BaseModel):
    id: uuid.UUID
    payer_email: str
    reference: str
    amount_kobo: int
    purpose: str
    target: Optional[str] = None
    status: str
    created_at: datetime


# ─────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────


class KPIResponse(BaseModel):
    total_revenue_kobo: int
    total_enrolments: int
    weekly_active_learners: int
    course_completions: int
