# Build plan — the v1 slice list

> **Relationship to existing docs.** [PWD.md](PWD.md) is the high-level
> three-phase delivery plan; [BUILD_SPEC.md](BUILD_SPEC.md) is the deep
> engineering brief. **This file** is the proprietor's tracker: every v1
> feature broken into **small, ordered, independently testable slices**,
> each with exactly three lines you can audit — what it builds, how you
> test it, and the git commit message that closes it. If any of these
> three files drift, this one wins on **slice order and definition of
> done** until updated.

---

## How to use this file

1. **Work top to bottom.** Slices are ordered so each one only depends on the ones above it. Skipping a slice will usually break a later one.
2. **One slice per session.** Open a slice, build it, run its test, commit with the listed message. Then stop and tick the slice off.
3. **Definition of done for every slice.**
   - The slice's test passes.
   - `npm run lint` / `ruff check` / `black --check` all pass.
   - The app still boots (`npm run dev` for the frontend, `uvicorn app.main:app --reload` for the backend).
   - No secret is committed.
   - If the slice unlocks a real user-visible feature, the corresponding row is added to [WHAT_WORKS.md](../WHAT_WORKS.md) in the same commit.
4. **Checkpoint first.** Before starting a slice, the working tree must be clean (`git status` shows no changes). See [HARDENING_RULES.md](../HARDENING_RULES.md).
5. **Commit messages are not optional.** Use the exact `feat(...)` / `fix(...)` / `docs(...)` strings listed — they're how we read the history at a glance later.

---

## Slice format

Each slice below has the same five fields:

- **ID & name** — short, memorable, used in commit messages.
- **Why it goes here** — what earlier slices it depends on, and why this is the next-smallest useful thing.
- **What it builds** — concrete files and behaviours, no hand-waving.
- **How you test it** — exact steps a non-coder can run.
- **Commit message** — the literal string to use when closing the slice.

---

## 0. Foundation slices (before any feature)

### S0.1 — Repo skeleton with module folders
- **Why now.** Every later slice puts files into one of these folders. They must exist first.
- **Builds.** The module folders listed in `ARCHITECTURE.md` (`public_site/`, `auth/`, `courses/`, `enrolment/`, `learning/`, `assessment/`, `certificates/`, `dashboard/`, `notifications/`, `data_layer/`), each with its own `README.md` (one paragraph: what it does, what goes in, what comes out), an empty `__init__.py`, and an empty `tests/` subfolder. **(This is Phase 3 of the project plan.)**
- **Test.** `ls` each new folder; open one README and confirm it states purpose, input, output. `pytest` runs and reports "no tests" without errors.
- **Commit.** `chore(scaffold): add module folders with READMEs and empty test dirs`

### S0.2 — Design system + dark dashboard tokens
- **Why now.** Every page from here on uses these tokens. Defining them once means the whole site stays consistent. **(This is Phase 4.)**
- **Builds.** A `docs/DESIGN_SYSTEM.md` describing colour, type, spacing, radius, components. A shared CSS file (or Tailwind config) with the dark-dashboard tokens. One sample homepage shell at `frontend/src/app/page.tsx` (or the static equivalent) that visibly uses the tokens.
- **Test.** Run the frontend. The homepage opens in the browser and visibly shows: dark background, light text, rounded cards, tidy nav tabs, generous spacing, mobile-friendly at 360 px width. No clutter.
- **Commit.** `feat(design-system): add dark dashboard tokens and homepage shell`

---

## 1. Public website slices

### S1 — Static home page
- **Why now.** Highest-traffic page; it's the storefront. Static (no DB) means no risk.
- **Builds.** The home route showing: hero with school story, three "why us" cards, three featured programmes, two CTAs ("Apply", "Enter portal"), footer.
- **Test.** Visit `/`. All CTAs route correctly (Apply → `/apply`; Enter portal → `/login`). Responsive at 360, 768, 1280 px. Lighthouse accessibility ≥ 90.
- **Commit.** `feat(public-site): add home page`

### S2 — About / our school page
- **Why now.** Cheap, static, supports the application flow. No deps beyond S0.2.
- **Builds.** The `/about` route with school story, leadership team (real names from the proprietor — placeholder until supplied), contact CTA.
- **Test.** Visit `/about`. Content renders; no invented credentials are visible.
- **Commit.** `feat(public-site): add about page`

### S3 — Programmes catalogue and detail
- **Why now.** Drives the apply / enrol decision; still static.
- **Builds.** `/programmes` listing all programmes (school + online) as cards; `/programmes/[slug]` detail page per programme with description, what's included, price (if paid), CTA.
- **Test.** Visit `/programmes`. Click a card → detail opens. CTAs route correctly (Apply → `/apply`; Enrol online → `/login?redirect=...`).
- **Commit.** `feat(public-site): add programmes catalogue and detail pages`

### S4 — Contact page
- **Why now.** Closes the static-public set so the rest of the public site has only the application + payment to wire up.
- **Builds.** `/contact` with address, phone, email, short message form (client-only at this stage), map placeholder.
- **Test.** Visit `/contact`. Contact details show. The form has client validation; submit is disabled until S6 lands.
- **Commit.** `feat(public-site): add contact page`

---

## 2. Backend foundation slices

### S5 — Database, base config, and User model
- **Why now.** Application form needs a place to store leads; auth needs a User table.
- **Builds.** SQLAlchemy + Alembic set up; `.env.example` augmented with `DATABASE_URL`; first migration adding `users` table (id, email, password_hash, role, status, timestamps). `app/main.py` boots and exposes `/healthz`.
- **Test.** Start the backend. `GET /healthz` returns `{"ok": true}`. Run `alembic upgrade head` against a local Postgres; `users` table exists.
- **Commit.** `feat(backend): add database, base config, and User model`

### S6 — Application form (frontend + backend + email)
- **Why now.** First end-to-end write. Smallest possible round-trip.
- **Builds.** `/apply` page with form and validation; `POST /applications` endpoint with Pydantic validation and rate-limit; `applications` table; confirmation email to parent + notification email to admissions inbox. Use a stubbed email sender for now (logs to console).
- **Test.** Submit a valid application. Database has a new row. Console shows two emails. Submit an invalid one → inline errors, no row written.
- **Commit.** `feat(public-site): add application form and POST /applications`

---

## 3. Auth slices

### S7 — Sign up (parent self-signup)
- **Why now.** Required before any portal route.
- **Builds.** `/register` page; `POST /auth/register` creating a User with role `parent` (or, for v1's 4-role model, role `student` only when a parent later activates a Student — for this slice, only "self-signup" is enabled). Password hashed with argon2.
- **Test.** Register a new account. `users` has a new row with `status=pending`. Same email twice → 409.
- **Commit.** `feat(auth): add parent self-signup`

### S8 — Log in / log out and session cookies
- **Why now.** Without sessions, every portal route is impossible.
- **Builds.** `/login`, `/logout`. `POST /auth/login` returns JWT access (httpOnly cookie, short TTL) + refresh (httpOnly, longer TTL). `POST /auth/refresh` rotates the access token. `POST /auth/logout` clears cookies.
- **Test.** Wrong password → generic error, no leak. Right password → cookies set, redirect to a placeholder portal page. Log out → cookies cleared. Refresh works after access expires.
- **Commit.** `feat(auth): add login, logout, and session refresh`

### S9 — Password reset
- **Why now.** Real users forget passwords. Cheap to add now and avoids a v1 emergency later.
- **Builds.** `/forgot-password` page; `POST /auth/forgot-password` issues a single-use, time-limited token; reset page accepts it and lets the user set a new password.
- **Test.** Request a reset for a real email → console shows a reset link. Open it → set new password → log in works. Token can't be re-used.
- **Commit.** `feat(auth): add password reset`

### S10 — Role-based access middleware (default deny) + tests
- **Why now.** Every later endpoint depends on this. Building it without features first means we can test it in isolation.
- **Builds.** A backend middleware that decorates routes with `requires(role, ownership?)`; default-deny rule on unknown routes. Helper for ownership checks (`is_owner(user, resource)`). A small `auth/tests/` suite that asserts: unauthenticated → 401; wrong role → 403; right role wrong owner → 403; right role right owner → 200.
- **Test.** Run `pytest auth/tests/`. All four cases pass. Add a `/admin/ping` route guarded by `admin`; hit it as a parent → 403.
- **Commit.** `feat(auth): add role-based access middleware with default-deny`

---

## 4. Payments slices

### S11 — Paystack initialize + verify (manual flow)
- **Why now.** The single highest-risk part of v1. Build it in isolation **before** anything depends on it.
- **Builds.** Server-side fee/price table (hard-coded for v1, then [YOU DECIDE]); `POST /payments/initialize` computes `amount_kobo` from the table (never trusts client amount), creates a `Payment(status=pending, reference)`; `POST /payments/verify` calls Paystack's verify API with the secret key and updates the Payment status. A `/pay` page wires up the Paystack inline widget.
- **Test.** Use Paystack **test** keys. Submit a test card; payment row goes `pending → success`. Tamper with the amount client-side → server rejects (amount mismatch). Re-verifying the same reference is idempotent.
- **Commit.** `feat(payments): add Paystack initialize and verify`

### S12 — Paystack webhook (idempotent fallback)
- **Why now.** If the client drops between payment and verify, the webhook is what saves the user. Webhook is the source of truth for status.
- **Builds.** `POST /payments/webhook/paystack` validating Paystack's signature; updates Payment by reference; idempotent.
- **Test.** Use Paystack's test webhook tool. A successful event marks the Payment success even if `/payments/verify` was never called. Sending the same event twice doesn't double-grant anything.
- **Commit.** `feat(payments): add Paystack webhook with signature verification`

### S13 — Receipt email on verified payment
- **Why now.** A real user expects a receipt within seconds. Pulled out of S11 so the payment slice stays small.
- **Builds.** On Payment status transition to `success` (whether via S11 or S12), send a receipt email with date, ₦ amount, purpose, reference.
- **Test.** Make a test payment. Console shows one receipt email per Payment success, never two.
- **Commit.** `feat(notifications): send receipt email on verified payment`

---

## 5. Course content slices

### S14 — Course / Module / Lesson data model + admin seed
- **Why now.** Every later student-facing slice needs at least one course in the database.
- **Builds.** Migration adding `courses`, `modules`, `lessons` tables. A `seed_demo.py` script that inserts one school course and one online course (AI & Data Analytics) with two modules and four lessons each.
- **Test.** Run the seed. `SELECT count(*) FROM lessons` returns 16 (4 lessons × 2 modules × 2 courses). Re-running the seed is idempotent (no duplicates).
- **Commit.** `feat(courses): add Course/Module/Lesson model and demo seed`

### S15 — Course catalogue (enrolled view) and course detail page
- **Why now.** The first student-facing screen. Read-only; safe.
- **Builds.** `/portal/courses` listing courses the student is enrolled in (after S17 there will be enrolments; for this slice, hard-grant the seed user access to one course for testing). `/portal/courses/[id]` showing modules + lesson list with completion ticks. `GET /courses/{id}` enforces enrolment (403 if not enrolled).
- **Test.** Sign in as the seeded student. Catalogue shows one course. Open the detail page; the lesson list renders. Try to open a course you're not enrolled in → 403.
- **Commit.** `feat(courses): add course catalogue and detail pages`

### S16 — Lesson viewer
- **Why now.** Required by every subsequent learning slice (complete, quiz, tutor).
- **Builds.** `/portal/courses/[id]/lessons/[lessonId]` showing the lesson body (markdown render), optional media placeholder, prev / next links, a non-functional "Mark complete" button (functional in S17), and an empty placeholder panel for the tutor (functional in S22).
- **Test.** Open a lesson; content renders; prev/next navigates correctly; "Mark complete" is visible but does nothing yet.
- **Commit.** `feat(courses): add lesson viewer`

### S17 — Mark lesson complete (with unique constraint)
- **Why now.** The simplest write inside a course; everything else (progress %, XP, certificate) reads from this table.
- **Builds.** `lesson_progress` table with `unique(learner_id, lesson_id)`. `POST /lessons/{id}/complete` is idempotent. The detail page recomputes course progress server-side after this call (single source of truth — see `ENGINEERING_PRINCIPLES §2`).
- **Test.** Click "Mark complete". Row appears, progress bar moves. Click again — no duplicate row, no double progress.
- **Commit.** `feat(learning): add mark-lesson-complete with idempotent progress`

---

## 6. Enrolment slices

### S18 — Self-enrol in a free course
- **Why now.** Smaller than paid enrolment. No payment dep.
- **Builds.** `POST /enrolments {course_id}` for free courses (`is_paid=false`). Catches double-enrolment. UI button on `/programmes/[slug]` for free programmes.
- **Test.** Click "Enrol" on a free course → it appears in the student catalogue. Click again → no duplicate row.
- **Commit.** `feat(enrolment): add self-enrol in free courses`

### S19 — Paid enrolment gated by verified payment
- **Why now.** Now that S11–S13 are stable, this becomes safe to wire up. **No access is granted from the client.**
- **Builds.** `POST /enrolments {course_id}` for paid courses returns `402 Payment Required` unless a `Payment` with matching purpose and `status=success` exists for this user. The Payment-success path (S11/S12) automatically creates the enrolment server-side.
- **Test.** Try to enrol in a paid course without paying → 402, no enrolment. Pay (test card) → enrolment row exists; the paid course appears in the student catalogue. Tampered "I paid" claim from the client → 402.
- **Commit.** `feat(enrolment): gate paid enrolment behind verified payment`

---

## 7. Assessment slices

### S20 — Quiz model and read endpoint (no answer keys to client)
- **Why now.** Needed before any quiz UI.
- **Builds.** `quizzes`, `questions` tables. `GET /quizzes/{id}` returns `{title, questions:[{id, prompt, options}]}` only — the `answer_index` field is **never serialised** to any client schema. A second seeded quiz attached to one of the lessons from S14.
- **Test.** Hit `GET /quizzes/{id}` as the seeded student. JSON does not contain `answer_index` anywhere. Decode the network response in browser devtools — still no answer key.
- **Commit.** `feat(assessment): add quiz model and read endpoint`

### S21 — Quiz attempt with server-side scoring
- **Why now.** The first place where "trust the client" would be a bug. Done correctly in isolation here.
- **Builds.** `POST /quizzes/{id}/attempt {answers:[index]}` computes the score on the server, stores an `attempts` row, returns `{score, total, xp_awarded?}`. Re-attempts allowed; XP from S22's rules.
- **Test.** Submit answers; the server-returned score matches a hand calculation. Manually edit the request to claim a higher score → ignored, server score wins.
- **Commit.** `feat(assessment): add quiz attempt with server-side scoring`

---

## 8. Gamification slice

### S22 — XP, levels, streaks, badges
- **Why now.** Lesson-complete (S17) and quiz-attempt (S21) both need to award XP; building it once here means both paths share one source of truth.
- **Builds.** A `gamification` row per learner. Functions that award XP / update streak / award badges following the rules in `BUILD_SPEC.md §8`. Idempotent (the same lesson never awards twice). Wired into S17 and S21.
- **Test.** Complete a lesson → +20 XP. Complete the same lesson again → no change. Get a perfect quiz → +bonus XP and a `Quiz Master` badge. Take seven days of activity (or fake `last_active_date` for the test) → `7-Day Streak` badge.
- **Commit.** `feat(learning): add gamification (XP, levels, streaks, badges)`

---

## 9. VOREM agentic tutor slices

### S23 — VOREM tutor MVP, bound to a single lesson
- **Why now.** All prerequisites (lessons, progress, auth) are in place.
- **Builds.** `POST /agents/tutor {lesson_id, question}` calling the Anthropic Claude API with a system prompt that enforces the VOREM loop: **explain the concept simply → check understanding with one question → adapt to the level → encourage and record progress.** Tutor is scoped to `lesson_id` content only. Every call writes an `agent_runs` row.
- **Test.** From a lesson, ask "explain it again, simpler". Tutor responds within ~6 s, in plain English, on-topic, and ends with one check question. Ask "tell me about another subject" → tutor stays on the lesson.
- **Commit.** `feat(learning): add VOREM tutor MVP bound to lesson`

### S24 — Child-safety guardrails (input + output filter, distress signal)
- **Why now.** Tutor cannot ship to v1 without these. Built immediately after S23 so the tutor is never live without them.
- **Builds.** Two filter passes per tutor call: (1) input policy filter (rate limit, banned topics, PII requests); (2) output policy filter (no unsafe / romantic / sexual content, no requests for personal contact details). Distress phrases trigger a "talk to a trusted adult" reply and set `agent_runs.flagged=true`.
- **Test.** Ask the tutor for personal contact details → safe refusal. Send a distress phrase → guarded reply + `agent_runs.flagged=true` in DB. Try a banned topic → safe refusal.
- **Commit.** `feat(learning): add child-safety guardrails on tutor calls`

---

## 10. Dashboard slices

### S25 — Student dashboard
- **Why now.** Pulls together everything the student has so far: courses, progress, XP, streak, badges, "continue learning".
- **Builds.** `/portal` reading from `GET /me/dashboard` which **only** reads the existing single-source-of-truth tables (`enrolments`, `lesson_progress`, `gamification`). No new calculations.
- **Test.** Sign in as the seeded student. Three stat cards (XP, level, active courses) match what's in the DB. "Continue learning" links to the first incomplete lesson. Progress bars match the lesson-list ticks on the course page (one source of truth).
- **Commit.** `feat(dashboard): add student dashboard`

### S26 — Admin dashboard (applications, users, courses, payments, KPIs)
- **Why now.** Admin needs visibility before v1 ships to real users.
- **Builds.** `/admin` with tabs: applications queue, users & roles, courses, payments, KPIs (revenue, enrolment count, weekly active learners, course completions). All numbers read from the same tables the student dashboard reads. Role-guarded `admin` only.
- **Test.** Sign in as admin. Each tab loads. Approve an application → the applicant's status flips and an audit-log row is written. KPIs match a manual `SELECT count(*)` on each underlying table.
- **Commit.** `feat(dashboard): add admin dashboard with audit-logged actions`

---

## 11. Certificate slice

### S27 — Certificate of completion at 100%
- **Why now.** Final v1 slice; ties off the learner journey.
- **Builds.** When a learner's `course_progress` hits 100% (computed from `lesson_progress` per S17), issue a `certificates` row and expose a download button on the course detail page. Certificate is generated server-side (HTML → PDF or printable HTML).
- **Test.** Complete every lesson in a seeded course. Certificate appears on the course page and downloads with the learner's name, the course title, and today's date. Completing the same course twice doesn't issue two certificates.
- **Commit.** `feat(certificates): issue certificate of completion at 100% progress`

---

## 12. Notifications wrap-up slice

### S28 — Welcome email on sign-up
- **Why now.** Not on the revenue path, but cheap; finishes the v1 notification trio (welcome, application receipt, payment receipt).
- **Builds.** On verified sign-up, send a friendly welcome email with portal link.
- **Test.** Register a new account; console shows one welcome email. Re-verify the same email → no duplicate.
- **Commit.** `feat(notifications): send welcome email on sign-up`

---

## What "v1 done" means

V1 ships when slices **S0.1 through S28** are all green in
[WHAT_WORKS.md](../WHAT_WORKS.md), the app boots, the full test suite
passes, no secret is in git, and the proprietor can:

1. Visit the home page, browse programmes, apply.
2. Sign up, pay a fee with a verified Paystack test card, receive a receipt.
3. Enrol in a paid course, take a lesson, get a server-scored quiz, see XP rise.
4. Reach 100% on a course and download a certificate.
5. Sign in as admin and see the same numbers in the admin dashboard that the student sees in theirs.

Nothing on the **"later"** list in
[PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md) is required for v1.

---

## After v1 — the "later" lane

Once v1 is green, the next ordered slices come from the **later**
features in `PRODUCT_REQUIREMENTS.md §4`: instructor authoring,
parent portal, AI-assisted quiz authoring, recurring subscriptions,
certificate verification, news / blog, lesson reminders, multi-tenancy,
mobile apps. Those slices will be drafted into this file at the same
granularity once v1 is shipped — **not before**.
