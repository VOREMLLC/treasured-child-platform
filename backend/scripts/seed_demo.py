"""Seed demo course data.

Inserts exactly the two demo courses BUILD_PLAN S14 specifies:
  - jss-1   (school, free) — 2 modules × 4 lessons
  - ai-data (online, paid) — 2 modules × 4 lessons

Total: 2 courses, 4 modules, 16 lessons.

Idempotent at the course level: re-running this script checks whether
a course with the given slug already exists; if so, it skips creating
the whole sub-tree. Course is the unit of "did we seed?".

Run from the backend directory:

    python -m scripts.seed_demo
"""

from __future__ import annotations

from typing import TypedDict

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.course import Course, CourseType, Lesson, Module


# ─────────────────────────────────────────────────────────────
# Demo content
# ─────────────────────────────────────────────────────────────


class LessonSpec(TypedDict):
    title: str
    content: str


class ModuleSpec(TypedDict):
    title: str
    lessons: list[LessonSpec]


class CourseSpec(TypedDict):
    slug: str
    title: str
    type: CourseType
    level: str
    summary: str
    is_paid: bool
    price_kobo: int | None
    published: bool
    modules: list[ModuleSpec]


DEMO: list[CourseSpec] = [
    {
        "slug": "jss-1",
        "title": "Junior secondary 1",
        "type": CourseType.school,
        "level": "Junior secondary",
        "summary": (
            "First year of the JSS national curriculum — core "
            "mathematics, English, and study skills."
        ),
        "is_paid": False,
        "price_kobo": None,
        "published": True,
        "modules": [
            {
                "title": "Introduction to mathematics",
                "lessons": [
                    {
                        "title": "Numbers",
                        "content": (
                            "Whole numbers from 1 to 100. Counting "
                            "forward and backward; place value of tens "
                            "and ones."
                        ),
                    },
                    {
                        "title": "Basic operations",
                        "content": (
                            "Addition, subtraction, multiplication, "
                            "and division with single- and two-digit "
                            "numbers."
                        ),
                    },
                    {
                        "title": "Fractions",
                        "content": (
                            "Halves, quarters and thirds. Reading and "
                            "comparing simple fractions."
                        ),
                    },
                    {
                        "title": "Decimals",
                        "content": (
                            "Tenths and hundredths. Reading decimal "
                            "places; converting between common "
                            "fractions and decimals."
                        ),
                    },
                ],
            },
            {
                "title": "Introduction to English",
                "lessons": [
                    {
                        "title": "Grammar basics",
                        "content": (
                            "Nouns, verbs and adjectives — recognising "
                            "and using each in simple sentences."
                        ),
                    },
                    {
                        "title": "Reading comprehension",
                        "content": (
                            "Reading short passages and answering "
                            "who / what / when / where / why questions."
                        ),
                    },
                    {
                        "title": "Writing skills",
                        "content": (
                            "Sentence structure and forming a "
                            "well-organised paragraph."
                        ),
                    },
                    {
                        "title": "Vocabulary",
                        "content": (
                            "Common English words for everyday "
                            "situations — home, school, market, "
                            "weather."
                        ),
                    },
                ],
            },
        ],
    },
    {
        "slug": "ai-data",
        "title": "AI & data analytics",
        "type": CourseType.online,
        "level": "Online",
        "summary": (
            "An accessible introduction to AI and data for ages 12+. "
            "Project-based, with child-safety guardrails throughout."
        ),
        "is_paid": True,
        "price_kobo": 3_500_000,  # ₦35,000 — matches services/fees.py
        "published": True,
        "modules": [
            {
                "title": "Foundations of data",
                "lessons": [
                    {
                        "title": "What is data?",
                        "content": (
                            "Types of data: numbers, text, images. "
                            "Where data comes from in everyday life."
                        ),
                    },
                    {
                        "title": "Spreadsheets",
                        "content": (
                            "Cells, rows and columns. Basic formulas: "
                            "SUM and AVERAGE."
                        ),
                    },
                    {
                        "title": "Charts",
                        "content": (
                            "Bar charts, line charts, pie charts — "
                            "when to use each."
                        ),
                    },
                    {
                        "title": "Summary statistics",
                        "content": (
                            "Mean, median and mode. What each one "
                            "tells us about a set of numbers."
                        ),
                    },
                ],
            },
            {
                "title": "Introduction to AI",
                "lessons": [
                    {
                        "title": "What is AI?",
                        "content": (
                            "Machines that learn from examples. "
                            "Spotting AI in everyday products."
                        ),
                    },
                    {
                        "title": "Python basics",
                        "content": (
                            "Variables, lists and simple loops. "
                            "Running code in a notebook."
                        ),
                    },
                    {
                        "title": "A simple ML notebook",
                        "content": (
                            "Loading data, making a chart, and "
                            "predicting a value from patterns."
                        ),
                    },
                    {
                        "title": "Safety guardrails",
                        "content": (
                            "Why AI needs guardrails. The rules our "
                            "tutor follows — and the things it will "
                            "refuse to do."
                        ),
                    },
                ],
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────
# Seed
# ─────────────────────────────────────────────────────────────


def seed(db: Session) -> dict[str, int]:
    """Insert the demo data idempotently.

    Returns the number of *new* rows inserted in this call. A second
    call with the same DB returns zeros for everything.
    """
    inserted = {"courses": 0, "modules": 0, "lessons": 0}

    for spec in DEMO:
        existing = (
            db.query(Course).filter(Course.slug == spec["slug"]).first()
        )
        if existing is not None:
            continue

        course = Course(
            slug=spec["slug"],
            title=spec["title"],
            type=spec["type"],
            level=spec["level"],
            summary=spec["summary"],
            is_paid=spec["is_paid"],
            price_kobo=spec["price_kobo"],
            published=spec["published"],
        )
        db.add(course)
        db.flush()
        inserted["courses"] += 1

        for module_idx, module_spec in enumerate(spec["modules"], start=1):
            module = Module(
                course_id=course.id,
                sort_order=module_idx,
                title=module_spec["title"],
            )
            db.add(module)
            db.flush()
            inserted["modules"] += 1

            for lesson_idx, lesson_spec in enumerate(
                module_spec["lessons"], start=1
            ):
                lesson = Lesson(
                    module_id=module.id,
                    sort_order=lesson_idx,
                    title=lesson_spec["title"],
                    content=lesson_spec["content"],
                    duration_min=10,
                )
                db.add(lesson)
                inserted["lessons"] += 1

    db.commit()
    return inserted


def main() -> None:
    db = SessionLocal()
    try:
        inserted = seed(db)
        print(f"Seed complete. Inserted: {inserted}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
