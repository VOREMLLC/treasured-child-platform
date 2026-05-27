# `courses/` — the course catalogue, modules and lessons

## What it does
Holds the structure and content of every course on the platform: course
record, modules, lessons. Lets a signed-in, enrolled student browse the
catalogue, open a course's lesson list, and read a single lesson. In
v1, courses are **admin-seeded**; the instructor authoring UI is "later"
([feature 30](../docs/PRODUCT_REQUIREMENTS.md)).

## What goes in (input)
- Signed-in student requests for the course catalogue, a course detail, or a lesson body.
- Admin seed scripts that populate `courses`, `modules`, `lessons`.

## What comes out (output)
- The student's course catalogue (only courses they are enrolled in).
- Course detail with the lesson list and completion status.
- A single lesson's body (markdown, plus optional media reference).

## Owns these v1 features
12. Course catalogue · 13. Course detail with lesson list · 14. Lesson
viewer.

## Build slices
S14 (data model + seed), S15 (catalogue + detail), S16 (lesson viewer).

## What does **not** belong here
- Progress tracking, gamification, the VOREM tutor — those live in [`learning/`](../learning/).
- Quizzes and scoring — those live in [`assessment/`](../assessment/).
- Enrolment records — those live in [`enrolment/`](../enrolment/).
- Schema definitions (`Course`, `Module`, `Lesson` ORM models) live in [`data_layer/`](../data_layer/); `courses/` consumes them, doesn't redefine them.

## Safety rules that apply here
- Course content reads are guarded by an **enrolment check** on every request — even for the catalogue.
- Quiz **answer keys** are never exposed by any endpoint in this module.
