"""ORM models package.

Importing this module registers every model with ``Base.metadata`` so
Alembic and the engine can see the full schema.
"""

from app.models.application import Application, ApplicationStatus, ClassLevel
from app.models.base import Base
from app.models.course import Course, CourseType, Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentSource, EnrolmentStatus
from app.models.password_reset import PasswordResetToken
from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.models.user import User, UserRole, UserStatus

__all__ = [
    "Base",
    "User",
    "UserRole",
    "UserStatus",
    "Application",
    "ApplicationStatus",
    "ClassLevel",
    "PasswordResetToken",
    "Payment",
    "PaymentPurpose",
    "PaymentStatus",
    "Course",
    "CourseType",
    "Module",
    "Lesson",
    "Enrolment",
    "EnrolmentSource",
    "EnrolmentStatus",
]
