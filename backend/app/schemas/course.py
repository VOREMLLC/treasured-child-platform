"""Pydantic shapes for the student-facing /me/courses and /courses/{id}."""

import uuid
from typing import List, Optional

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


# ─────────────────────────────────────────────────────────────
# /courses/{course_id}/lessons/{lesson_id} — S16
# ─────────────────────────────────────────────────────────────


class LessonNeighbor(BaseModel):
    """Pointer to the previous or next lesson in linear course order."""

    id: uuid.UUID
    title: str


class LessonDetailRead(BaseModel):
    """Single-lesson view: content + course/module context + neighbours.

    ``completed`` is always False in S16. S17 wires it through the same
    field with no schema change.
    """

    id: uuid.UUID
    sort_order: int
    title: str
    content: str
    duration_min: int
    media_url: Optional[str]
    completed: bool

    # Surrounding context, used for breadcrumbs in the viewer.
    course_id: uuid.UUID
    course_title: str
    module_id: uuid.UUID
    module_title: str

    # Linear navigation. None at the start / end of the course.
    prev: Optional[LessonNeighbor]
    next: Optional[LessonNeighbor]
