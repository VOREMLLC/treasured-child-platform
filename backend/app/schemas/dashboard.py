"""Pydantic shapes for GET /me/dashboard (S25).

All numbers are read directly from existing single-source-of-truth
tables — no new calculations live here.
"""

import uuid
from typing import List, Optional

from pydantic import BaseModel


class CourseProgress(BaseModel):
    """One active enrolment shown on the dashboard."""

    id: uuid.UUID
    slug: str
    title: str
    level: str
    type: str               # "school" or "online"
    progress_percent: int
    # The first incomplete lesson in this course (null if course is 100 % done).
    next_lesson_id: Optional[uuid.UUID] = None


class ContinueLearning(BaseModel):
    """The single most-actionable next step across all enrolled courses."""

    course_id: uuid.UUID
    course_title: str
    lesson_id: uuid.UUID
    lesson_title: str


class LeaderboardEntry(BaseModel):
    """One row in the top-5 XP leaderboard."""

    rank: int
    learner_name: str
    xp: int
    is_me: bool


class DashboardResponse(BaseModel):
    """Response for GET /me/dashboard."""

    # Gamification stats
    xp: int
    level: int
    streak_days: int
    badges: List[str]

    # Course summary
    active_courses_count: int
    courses: List[CourseProgress]

    # "Resume" shortcut — None when there are no incomplete lessons
    continue_learning: Optional[ContinueLearning] = None

    # Top-5 global XP leaderboard; is_me flags the current learner's row
    leaderboard: List[LeaderboardEntry]
