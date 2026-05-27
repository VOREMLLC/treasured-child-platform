# `dashboard/` — personalised home pages by role

## What it does
The first page a signed-in user sees. v1 ships two dashboards:

1. **Student dashboard** (`/portal`) — welcome, XP / level / streak, active courses with progress bars, a "continue learning" button to the next incomplete lesson.
2. **Admin dashboard** (`/admin`) — applications queue, users & roles, courses, payments, KPIs (revenue, enrolment count, weekly active learners, course completions).

The Instructor dashboard and the Parent dashboard are **"later"**
([features 31 and 32](../docs/PRODUCT_REQUIREMENTS.md)).

## What goes in (input)
- A signed-in user's `GET /me/dashboard` (or `/admin/reports/kpis` for admin).
- The user's role (used to choose which dashboard view to render).

## What comes out (output)
- An aggregated read-only view assembled from the single-source-of-truth tables in [`data_layer/`](../data_layer/).
- Loading / empty / error states for each panel.

## Owns these v1 features
23. Student dashboard · 24. Admin dashboard.

## Build slices
S25 (student), S26 (admin).

## What does **not** belong here
- Any number **calculation**. Dashboards **only read**; numbers come from `data_layer/` aggregates that other modules write to.
- Business logic about enrolment, payments, progress, grades.

## Safety rules that apply here
- **One source of truth.** A number shown on the student dashboard (e.g. XP) is the same number shown on the admin dashboard for that learner. If they ever differ, one of them is wrong — see [`ENGINEERING_PRINCIPLES.md §2`](../ENGINEERING_PRINCIPLES.md).
- **Ownership on every "(own)" read.** A student requesting another student's dashboard is rejected by the RBAC middleware in [`auth/`](../auth/).
- **No PII of other learners visible to a student**, ever — not even names in a leaderboard column. (Initials or first-name-only only.)
