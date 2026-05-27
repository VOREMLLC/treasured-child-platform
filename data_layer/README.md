# `data_layer/` — the single source of truth

## What it does
Owns the **database**: schema, migrations, ORM models, and the
**aggregate read functions** every other module calls when it needs an
authoritative number (XP, lesson progress, enrolment count, payment
status, KPI rollups).

This is the module that enforces
[`ENGINEERING_PRINCIPLES.md §2 — one source of truth`](../ENGINEERING_PRINCIPLES.md).
If two parts of the app disagree on a number, one of them is bypassing
this module — that's the bug.

## What goes in (input)
- SQLAlchemy ORM model definitions (one file per table).
- Alembic migrations.
- Read queries from every other module.
- Tightly-controlled write paths called by the owning module (e.g. `record_payment_verified()` from the payments flow, `record_lesson_complete()` from `learning/`).

## What comes out (output)
- Typed records (Pydantic schemas or ORM rows) returned to the caller.
- Aggregate read functions used by dashboards and reports.
- Migration files describing every schema change in version control.

## Owns
The **schema**, not features. Specifically:
- `users`, `guardians`, `learners`
- `courses`, `modules`, `lessons`, `lesson_progress`
- `quizzes`, `questions` (server-only `answer_index`), `attempts`
- `enrolments`, `payments`, `subscriptions` (later)
- `gamification`, `certificates`
- `applications`, `notification_log`
- `agent_runs`, `audit_log`

## Build slices
S5 (initial schema + Alembic), and a migration added with **every** later slice that introduces a new table or column.

## What does **not** belong here
- Business logic, validation, role checks — those live in the **owning** module that calls this one.
- HTTP routes — those live in their owning module.
- Email or AI calls — those live in [`notifications/`](../notifications/) and [`learning/`](../learning/) respectively.

## **READ-ONLY rule for real user data**
> *Rule 8 in [ENGINEERING_PRINCIPLES.md](../ENGINEERING_PRINCIPLES.md):
> treat any real user data as READ-ONLY unless the proprietor explicitly
> grants write permission for the specific operation.*

This is the module that operationalises that rule:

- **Default = read.** Every function exposed by `data_layer/` is a read function unless a comment at the top of the file explicitly names it a designed write path.
- **Designed write paths only.** New writes (e.g. record a payment, mark a lesson complete) are added one at a time, each with: an owning module, a slice in [`BUILD_PLAN.md`](../docs/BUILD_PLAN.md), and a test that proves idempotence.
- **No ad-hoc writes.** No module is allowed to bypass `data_layer/` and write directly with raw SQL.
- **Real user data in real environments is touched only via documented write paths.** Local development uses **seeded** data; staging and production touch real records only through verified, audit-logged paths.

## Safety rules that apply here
- **Encryption at rest** for PII (names, emails, phone numbers, payment metadata).
- **Argon2** for password hashes — plaintext passwords never persist.
- **Audit log** rows are append-only; no module can update or delete `audit_log` records.
- **Minor data minimisation** — collect the fewest fields about learners necessary to operate.
