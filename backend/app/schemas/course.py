"""Pydantic shapes for the student-facing /me/courses and /courses/{id}."""

import uuid
from typing import List

from pydantic import BaseModel, ConfigDict

from app.models.course import CourseType


class LessonRead(BaseModel):
    """One lesson row in the detail view's lesson list.

    ``completed`` is always False in S15; S17 wires it through from the
    lesson_progress table without changing the schema.
    """

    id: uuid.UUID
    sort_order: int
    title: str
    duration_min: int
    completed: bool


class ModuleRead(BaseModel):
    id: uuid.UUID
    sort_order: int
    title: str
    lessons: List[LessonRead]


class CourseListItem(BaseModel):
    """One card in /me/courses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    type: CourseType
    level: str
    summary: str
    is_paid: bool


class CourseDetail(BaseModel):
    """Full detail page payload for /courses/{id}."""

    id: uuid.UUID
    slug: str
    title: str
    type: CourseType
    level: str
    summary: str
    is_paid: bool
    modules: List[ModuleRead]
