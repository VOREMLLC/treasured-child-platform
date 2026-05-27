# `enrolment/` — who is in which course

## What it does
Maps students to courses. Two paths in v1:

1. **Free enrolment** — a signed-in student clicks "Enrol" and is added.
2. **Paid enrolment** — gated behind a **server-verified Paystack payment**. Access is granted only after the payment is confirmed by the backend, never on a client claim.

## What goes in (input)
- A signed-in student's enrolment request (`POST /enrolments {course_id}`).
- Payment-success events from the payments flow in [`public_site/`](../public_site/) — webhook or client-side verify, whichever the server confirms first.

## What comes out (output)
- An `enrolments` row (`status=active`, `source=free|paid`, optional `access_expires_at`).
- A 402 `Payment Required` response if the student tries to enrol in a paid course without a verified payment.
- The "this course is now available" experience in the student catalogue.

## Owns these v1 features
15. Self-enrol in a free course · 16. Paid-course enrolment gated by
payment.

## Build slices
S18 (free), S19 (paid + payment gate).

## What does **not** belong here
- The Paystack flow itself — that's in [`public_site/`](../public_site/) (initialize, verify, webhook).
- Course content — that's in [`courses/`](../courses/).
- Receipt emails — those are in [`notifications/`](../notifications/).

## Safety rules that apply here
- **No client-trusted access.** A request that says "I paid" is ignored unless the server has a matching `Payment(status=success, verified_at IS NOT NULL)` for that user + course.
- Enrolment creation is **idempotent**: the same verified payment never creates two enrolment rows for the same student/course pair.
