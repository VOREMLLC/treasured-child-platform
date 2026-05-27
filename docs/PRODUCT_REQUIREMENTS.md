# Product requirements — what we are building, in plain language

> **Relationship to existing docs.** This file is the **v1 source of truth**
> for the proprietor's view: every feature, in plain English, with the
> input (what someone gives the system) and the output (what they get
> back). The deeper strategic and engineering views live in
> [PRD.md](PRD.md), [SDD.md](SDD.md) and [BUILD_SPEC.md](BUILD_SPEC.md);
> if those ever disagree with this file on **scope**, this file wins
> until updated.
>
> Every feature has a status: **✅ v1** (we build it now) or **⏳ later**
> (recorded so we don't forget, not built yet).

---

## 1. What this platform is

Treasured Child has two engines that share one login, one user list, one
payments system and one safety boundary.

1. **A public website** — turns interested parents into enrolled,
   fee-paying students of the physical school in Orerokpe.
2. **A learning management system (LMS)** — sells online courses (exam
   prep, AI & Data Analytics) to learners anywhere, and teaches them
   using the VOREM Agentic Education System: **explain a concept simply
   → check understanding → adapt to the learner's level → encourage and
   track progress**, with strict child-safety guardrails because many
   learners are minors.

Revenue comes from two channels: school fees collected online, and paid
online courses.

---

## 2. Features at a glance

| # | Feature | Module | Status |
|---|---|---|---|
| 1 | Home page | `public_site/` | ✅ v1 |
| 2 | About / our school | `public_site/` | ✅ v1 |
| 3 | Programmes catalogue | `public_site/` | ✅ v1 |
| 4 | Programme detail | `public_site/` | ✅ v1 |
| 5 | Contact page | `public_site/` | ✅ v1 |
| 6 | Application form | `public_site/` | ✅ v1 |
| 7 | Online fee payment | `public_site/` + `enrolment/` | ✅ v1 |
| 8 | Sign up | `auth/` | ✅ v1 |
| 9 | Log in / log out | `auth/` | ✅ v1 |
| 10 | Password reset | `auth/` | ✅ v1 |
| 11 | Role-gated access | `auth/` | ✅ v1 |
| 12 | Course catalogue (for enrolled students) | `courses/` | ✅ v1 |
| 13 | Course detail with lesson list | `courses/` | ✅ v1 |
| 14 | Lesson viewer | `courses/` | ✅ v1 |
| 15 | Self-enrol in a free course | `enrolment/` | ✅ v1 |
| 16 | Paid-course enrolment, gated by payment | `enrolment/` | ✅ v1 |
| 17 | VOREM agentic lesson tutor | `learning/` | ✅ v1 |
| 18 | Lesson progress tracking | `learning/` | ✅ v1 |
| 19 | Child-safety guardrails on AI replies | `learning/` | ✅ v1 |
| 20 | Quiz at end of a lesson | `assessment/` | ✅ v1 |
| 21 | Quiz attempt with server-side scoring | `assessment/` | ✅ v1 |
| 22 | XP, levels, streaks, badges | `learning/` | ✅ v1 |
| 23 | Student dashboard | `dashboard/` | ✅ v1 |
| 24 | Admin dashboard | `dashboard/` | ✅ v1 |
| 25 | Welcome email | `notifications/` | ✅ v1 |
| 26 | Payment receipt email | `notifications/` | ✅ v1 |
| 27 | Application received email | `notifications/` | ✅ v1 |
| 28 | Certificate of completion | `certificates/` | ✅ v1 |
| 29 | News / blog | `public_site/` | ⏳ later |
| 30 | Instructor course authoring (UI) | `courses/` | ⏳ later |
| 31 | Instructor dashboard (own students view) | `dashboard/` | ⏳ later |
| 32 | Parent / guardian portal | `dashboard/` | ⏳ later |
| 33 | AI-assisted quiz authoring for instructors | `assessment/` | ⏳ later |
| 34 | Certificate verification by public code | `certificates/` | ⏳ later |
| 35 | Recurring subscriptions | `enrolment/` | ⏳ later |
| 36 | Lesson reminders / nudge emails | `notifications/` | ⏳ later |
| 37 | White-label multi-tenancy | platform-wide | ⏳ later |
| 38 | Native mobile apps | platform-wide | ⏳ later |

For v1, the platform must end-to-end let a Visitor become a paying
Student who completes a lesson, takes a quiz, sees their progress and
earns a certificate.

---

## 3. Each feature in detail

Each entry is a small card with the same four lines: **what it is**,
**input**, **output**, **status**.

---

### Public website

#### 1. Home page
- **What it is.** The front door. Tells parents who Treasured Child is, why to choose us, and where to go next (apply, pay fees, enter portal).
- **Input.** A visitor lands on the page.
- **Output.** A clear, dark-dashboard-styled home page with the school story, three reasons to choose us, three featured programmes, and two big buttons: "Apply" and "Enter portal".
- **Status.** ✅ v1.

#### 2. About / our school
- **What it is.** The school's story, location, achievements (e.g. growth from 18 to 200 learners), values, real photos.
- **Input.** A visitor clicks "About".
- **Output.** A page with the story, the leadership team, and a contact CTA. Uses only real facts and approved photos — no invented credentials.
- **Status.** ✅ v1.

#### 3. Programmes catalogue
- **What it is.** A grid showing every offering: physical school levels (Nursery, Primary, Junior, Senior) and online programmes (e.g. BECE / Common Entrance prep, AI & Data Analytics).
- **Input.** A visitor clicks "Programmes".
- **Output.** A grid of programme cards: title, level, type (school / online), short summary, price for paid programmes, "Learn more" link.
- **Status.** ✅ v1.

#### 4. Programme detail
- **What it is.** A page explaining one programme in full: what's covered, who it's for, what's included, price (if paid), "Apply" or "Enrol" CTA.
- **Input.** Visitor opens a programme by clicking its card.
- **Output.** A full description page with the right CTA (Apply → application form; Enrol on online programme → log in then payment).
- **Status.** ✅ v1.

#### 5. Contact page
- **What it is.** Address, phone, email, a short message form, and a map placeholder.
- **Input.** Visitor opens contact, optionally submits a message.
- **Output.** Visible contact details; on form submit, the school's admin inbox receives the message and the visitor sees a confirmation.
- **Status.** ✅ v1.

#### 6. Application form
- **What it is.** A simple form a parent fills in to apply for a place at the physical school.
- **Input.** Child name, parent / guardian name, email, phone, class applying for, optional message.
- **Output.** A success screen ("we'll be in touch"), a new row in the admin application queue, and a confirmation email to the parent.
- **Status.** ✅ v1.

#### 7. Online fee payment
- **What it is.** A page where a parent pays school fees or programme fees online via Paystack.
- **Input.** Logged-in (or email-identified) payer, a purpose (school fees term / specific online programme), and the Paystack transaction reference returned by the gateway.
- **Output.** Server-verified payment record stored, a receipt email sent, and the matching access granted (term fee marked paid, or programme enrolment activated). **Access is never granted on what the client claims — only on what the server verifies.**
- **Status.** ✅ v1.

---

### Authentication

#### 8. Sign up
- **What it is.** Creating an account. v1 supports two paths: parents create their own account, and admins/instructors are invited.
- **Input.** Name, email, phone, password (parent path). For invites: a single-use invite link.
- **Output.** An account in `pending` status until consent is recorded (for student accounts — see role rules in `USER_ROLES.md`).
- **Status.** ✅ v1.

#### 9. Log in / log out
- **What it is.** Standard email + password sign-in, with a "log out" action that ends the session.
- **Input.** Email and password.
- **Output.** A session cookie (short-lived access + longer-lived refresh). Wrong credentials show a generic error (no information leakage about which accounts exist).
- **Status.** ✅ v1.

#### 10. Password reset
- **What it is.** "I forgot my password" flow.
- **Input.** Email address.
- **Output.** An email with a one-time reset link valid for a short window. Following it lets the user set a new password.
- **Status.** ✅ v1.

#### 11. Role-gated access
- **What it is.** Every page and every API endpoint checks the user's role before responding. Default is **deny**.
- **Input.** A request with an auth token.
- **Output.** Either the requested data (when the role and ownership rule allow it) or a 401 / 403 error. Sensitive actions write an audit log entry.
- **Status.** ✅ v1.

---

### Courses, enrolment and learning

#### 12. Course catalogue (for enrolled students)
- **What it is.** Inside the portal: a list of every course the student is enrolled in.
- **Input.** A logged-in student.
- **Output.** Cards showing course title, type (school / online), and progress percentage. Locked courses (paid, unpaid) show a "locked — enrol" badge.
- **Status.** ✅ v1.

#### 13. Course detail with lesson list
- **What it is.** One course's home page: title, overall progress, list of modules and lessons with completion ticks.
- **Input.** A logged-in student, enrolled in this course.
- **Output.** The lesson list with status icons and a "resume" pointer to the first incomplete lesson.
- **Status.** ✅ v1.

#### 14. Lesson viewer
- **What it is.** The actual page where a student reads / watches a lesson.
- **Input.** A logged-in, enrolled student opens a lesson.
- **Output.** The lesson body (text + optional media), prev / next navigation, a "Mark complete" button, and a panel that opens the VOREM agentic tutor (feature 17).
- **Status.** ✅ v1.

#### 15. Self-enrol in a free course
- **What it is.** Joining a free course in one click.
- **Input.** A logged-in student picks a free course in the catalogue and clicks "Enrol".
- **Output.** A new enrolment record, immediate access, course appears in their catalogue.
- **Status.** ✅ v1.

#### 16. Paid-course enrolment, gated by payment
- **What it is.** Joining a paid course only after a verified Paystack payment.
- **Input.** A logged-in student picks a paid course and goes through the payment flow.
- **Output.** Only after the **server** confirms the payment with Paystack: an `enrolment` row is created, access is granted, and the course unlocks. Failed or unverified payments grant nothing.
- **Status.** ✅ v1.

#### 17. VOREM agentic lesson tutor
- **What it is.** The teaching AI in `learning/`. It follows the pedagogy loop on each lesson: **explain the concept simply → ask a check question → adapt to the learner's level → encourage and record progress.** It is bound to the current lesson; it does not free-roam.
- **Input.** The current lesson's content, the learner's recent answers, the learner's question.
- **Output.** A reply tied to the lesson, age-appropriate, never asking for personal contact details, never producing unsafe content. Distress signals route to a human-contact prompt and flag the run.
- **Status.** ✅ v1.

#### 18. Lesson progress tracking
- **What it is.** Recording that a learner completed a lesson, and recomputing the course's overall progress.
- **Input.** A "mark complete" action by the learner.
- **Output.** A single `lesson_progress` row per learner-lesson pair (prevents double-crediting), recomputed course % progress, and an XP award (feature 22). **One source of truth: the dashboard, the course detail page and the certificate all read this same value.**
- **Status.** ✅ v1.

#### 19. Child-safety guardrails on AI replies
- **What it is.** A safety pipeline that every AI reply passes through, in both directions (input filter and output filter).
- **Input.** The learner's message and the AI's draft reply.
- **Output.** Either the reply (if safe), a softened / on-topic re-draft, or a human-contact prompt on distress signals. Every call writes an `agent_run` log entry; flagged runs are reviewable by admin.
- **Status.** ✅ v1.

#### 20. Quiz at end of a lesson
- **What it is.** A short, multiple-choice quiz attached to a lesson or to a course.
- **Input.** Student opens the quiz and answers each question.
- **Output.** Questions and options sent to the client; **correct-answer keys never leave the server.**
- **Status.** ✅ v1.

#### 21. Quiz attempt with server-side scoring
- **What it is.** Submitting a quiz and getting a score.
- **Input.** The student's chosen answers.
- **Output.** A score computed entirely on the server, an XP award, an optional badge for a perfect score, and a stored attempt record. Re-takes are allowed; the XP rule for retakes is **first-attempt only** unless changed in `BUILD_SPEC §14`.
- **Status.** ✅ v1.

#### 22. XP, levels, streaks, badges (gamification)
- **What it is.** Lightweight motivation: students earn XP for actions, level up at thresholds, keep streaks for daily activity, and earn named badges.
- **Input.** Any qualifying learning action (lesson complete, correct quiz answer, perfect quiz, course complete, daily streak).
- **Output.** Updated `gamification` record (XP, level, streak days, last active date, badge list), idempotent — the same action never awards twice. Rules are defined in `BUILD_SPEC §8`.
- **Status.** ✅ v1.

---

### Dashboards

#### 23. Student dashboard
- **What it is.** The first page a logged-in student sees. Welcoming, motivational, oriented.
- **Input.** A logged-in student.
- **Output.** A dark-dashboard layout showing: welcome + streak; three stat cards (XP, level, active courses); a "continue learning" card (next incomplete lesson with resume button); a list of all enrolled courses with progress bars.
- **Status.** ✅ v1.

#### 24. Admin dashboard
- **What it is.** The first page a logged-in admin sees. The platform's control room.
- **Input.** A logged-in admin.
- **Output.** Tabs / cards for: applications queue, users & roles, courses, payments, KPIs (revenue, enrolment, weekly active learners). Every number is read from the **same** underlying source as the student dashboard — no parallel calculations.
- **Status.** ✅ v1.

---

### Notifications

#### 25. Welcome email
- **What it is.** A short email on first successful sign-up.
- **Input.** A new account is created and verified.
- **Output.** A plain, friendly email with the learner / parent name, what to do next, and a link to the portal.
- **Status.** ✅ v1.

#### 26. Payment receipt email
- **What it is.** Sent immediately after a payment is **server-verified**.
- **Input.** A successful, verified Paystack payment.
- **Output.** An email with the date, amount in Naira, purpose (fees term / programme name), and a reference number. Never sent on an unverified payment.
- **Status.** ✅ v1.

#### 27. Application received email
- **What it is.** Sent when a parent submits the application form.
- **Input.** A new application row is created.
- **Output.** A confirmation email to the parent and a notification to the school's admissions inbox.
- **Status.** ✅ v1.

---

### Certificates

#### 28. Certificate of completion
- **What it is.** A downloadable certificate awarded when a student reaches 100% on a course.
- **Input.** A `course_progress` value of 100% for a given learner and course (computed from feature 18).
- **Output.** A generated certificate (PDF or printable HTML) with the learner's name, the course title, and the date. Stored against the learner so it can be re-downloaded.
- **Status.** ✅ v1.

---

## 4. Features explicitly out of v1 (the "later" list)

These are recorded so the team doesn't forget them, and so the v1 scope
is **honestly** bounded. They are **not** part of the version we ship
first.

| # | Feature | Why later |
|---|---|---|
| 29 | News / blog | Not on the revenue path; adds editorial workload. |
| 30 | Instructor course authoring (UI) | v1 ships with admin-seeded courses; an instructor UI is a separate, larger build. |
| 31 | Instructor dashboard (own students view) | No instructor self-service in v1; same reason as 30. |
| 32 | Parent / guardian portal | A second, parallel portal — significant work. v1 communicates via email. |
| 33 | AI-assisted quiz authoring for instructors | Depends on 30. |
| 34 | Certificate verification by public code | Nice-to-have; not needed to issue certificates in v1. |
| 35 | Recurring subscriptions | One-off payments cover v1 revenue needs. |
| 36 | Lesson reminders / nudge emails | Needs an event/queue system to do well. |
| 37 | White-label multi-tenancy | A platform-wide architectural shift. Design v1 so this is possible later, but do not build it. |
| 38 | Native mobile apps | Web-responsive is enough for v1. |

---

## 5. Definitions used throughout this document

- **v1** — the version of the platform we ship first. Built before any "later" feature is started.
- **Module** — a single folder under the repo root (e.g. `public_site/`, `learning/`). Each module owns its feature surface; see [ARCHITECTURE.md](../ARCHITECTURE.md).
- **VOREM** — the agentic education pedagogy used in the LMS: explain simply → check understanding → adapt → encourage and track. Lives in `learning/`.
- **Server-verified** — confirmed by our backend talking directly to the payment provider, never trusted from the client.
- **Source of truth** — the single place a number is calculated. Every other place that shows that number reads from there, never recomputes it.
