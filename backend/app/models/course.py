"""Course / Module / Lesson models.

The core LMS content hierarchy. A Course contains ordered Modules; each
Module contains ordered Lessons. Lesson content is markdown; per
BUILD_SPEC §4 media is referenced by URL, not stored inline.

``sort_order`` is used instead of ``order`` because ORDER is a SQL
reserved word — avoiding it sidesteps quoting noise across dialects.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CourseType(str, enum.Enum):
    school = "school"
    online = "online"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(
        String(80), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[CourseType] = mapped_column(
        Enum(CourseType, name="course_type"), nullable=False
    )
    level: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    summary: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=""
    )
    is_paid: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0", default=False
    )
    price_kobo: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0", default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Course id={self.id} slug={self.slug!r} "
            f"type={self.type.value}>"
        )


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Module id={self.id} course_id={self.course_id} "
            f"sort_order={self.sort_order}>"
        )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=""
    )
    media_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )
    duration_min: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="10", default=10
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Lesson id={self.id} module_id={self.module_id} "
            f"sort_order={self.sort_order} title={self.title!r}>"
        )
