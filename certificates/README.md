# `certificates/` — certificates of completion

## What it does
Issues a downloadable certificate when a student reaches 100% on a
course. Stores the issued certificate so the student can re-download it
later.

## What goes in (input)
- A trigger from [`learning/`](../learning/) when `course_progress == 100%` for a learner / course pair (computed from `lesson_progress`, the single source of truth).

## What comes out (output)
- A `certificates` row (`learner_id`, `course_id`, `issued_at`, optional `verification_code`).
- A generated certificate file: server-rendered HTML, optionally converted to PDF.
- A "Download certificate" button on the course detail page once issued.

## Owns these v1 features
28. Certificate of completion.

## Build slices
S27.

## What does **not** belong here
- Progress calculation — that lives in [`learning/`](../learning/) and reads from `data_layer/`.
- Public certificate verification by code — that's "later" ([feature 34](../docs/PRODUCT_REQUIREMENTS.md)).
- Email delivery of the certificate — that's in [`notifications/`](../notifications/) when added.

## Safety rules that apply here
- A certificate is **never issued twice** for the same `(learner, course)` pair — idempotent on `course_progress == 100%`.
- The learner's name on the certificate comes from the **authoritative** user record (`data_layer/`), never from a client input.
