# User roles — who can do what

> **Relationship to existing docs.** This file is the **v1 source of
> truth** on roles and permissions: four roles, in plain English. The
> older [URD.md](URD.md) defines a richer seven-role model (Visitor,
> Learner, Parent/Guardian, Teacher, Bursar, Admin, Proprietor) which is
> the **later** target. Section 6 below shows exactly how the four v1
> roles will split into the seven later roles, so the migration is a
> known shape, not a guess.
>
> If this file and `URD.md` ever disagree on **v1 scope**, this file
> wins until updated.

---

## 1. The four roles, in one sentence each

| Role | One-sentence definition |
|---|---|
| **Visitor** | Any person who has not signed in. Sees only the public website. |
| **Student** | A signed-in learner. Enrols in courses, takes lessons and quizzes, sees only their own progress. |
| **Instructor** | A signed-in teacher. Owns specific courses, can see the students enrolled in **their** courses, marks their work. |
| **Admin** | The platform operator. Full control across the system: users, courses, applications, payments, KPIs. |

There are **no other roles in v1.** The platform is default-deny: any
request that does not match a role + ownership rule is rejected.

---

## 2. Each role in detail

### 2.1 Visitor

- **Who they are.** A prospective parent, alumnus, or any unauthenticated visitor.
- **What they want.** Evaluate the school, learn about programmes, apply for a place, pay fees online, or contact the school.
- **Key journeys.**
  - Land → browse programmes → apply → become a Student account (after the parent's account is created).
  - Land → pay fees online (identified by email; no portal access granted until they sign in).
- **What they can do.**
  - Read every public website page (`public_site/`).
  - Submit one application via the public form.
  - Pay fees via the public payment page (Paystack).
  - Submit a contact-form message.
- **What they cannot do.**
  - See any course content, any other person's data, any dashboard, or any admin surface.
  - View prices for unpublished programmes, or any learner record.

### 2.2 Student

- **Who they are.** A signed-in learner enrolled in one or more courses. Often a minor — child-safety guardrails apply to everything they see and to every AI reply.
- **What they want.** Take their courses, see their progress, earn XP and badges, ask the VOREM tutor for help, download a certificate when they finish.
- **Key journeys.**
  - Sign in → student dashboard → "continue learning" → lesson → mark complete → quiz → score + XP.
  - Open a programme → enrol (free) or pay (paid) → start learning.
  - Reach 100% on a course → download a certificate.
- **What they can do.**
  - See their **own** courses, **own** progress, **own** XP/level/streak/badges, **own** certificates.
  - Enrol in a free course; pay to enrol in a paid course; **only after server-verified payment** does access unlock.
  - Mark a lesson complete (idempotent — never awards XP twice).
  - Attempt a quiz; receive a server-computed score.
  - Talk to the VOREM tutor inside a lesson, subject to safety guardrails.
- **What they cannot do.**
  - See another student's progress, name, email, or quiz answers.
  - Edit course content, quiz questions, or their own grades.
  - Use the tutor outside of lessons or have it disclose other learners' data.

### 2.3 Instructor

- **Who they are.** A teacher who owns one or more courses on the platform.
- **What they want.** See who is enrolled in their courses and how their students are doing; in **later** versions, author and update their own course content and AI-drafted quizzes (gated by their own publish action).
- **Key journeys.** (v1 only)
  - Sign in → see the courses they own → see the list of students enrolled in those courses and each student's progress.
  - Sign in → mark a quiz attempt manually if needed (instructor-graded items, when present).
- **What they can do (v1).**
  - See the **roster** and **progress** of students enrolled in **their own** courses.
  - Read lesson and quiz content for their own courses (they own them, so they can see the answer keys server-side; the keys never reach the client).
  - View their own profile.
- **What they cannot do (v1).**
  - See or touch courses they do not own.
  - See any student not enrolled in their courses.
  - See payments, applications, audit logs, or KPIs.
  - Change another user's role or content.
- **What an instructor will be able to do later.**
  - Author courses, lessons and quizzes (`later` feature 30).
  - Request AI-drafted quizzes and publish them after review (`later` feature 33).

### 2.4 Admin

- **Who they are.** The platform operator(s). In v1, the school proprietor and any operator they trust with the keys.
- **What they want.** Run the platform end to end: applications, users and roles, courses, payments, KPIs.
- **Key journeys.**
  - Sign in → admin dashboard → applications queue → review and approve.
  - Sign in → admin dashboard → users → change a role, deactivate an account.
  - Sign in → admin dashboard → courses → create / publish / archive.
  - Sign in → admin dashboard → payments → reconcile, export.
  - Sign in → admin dashboard → KPIs → revenue, enrolment, weekly-active learners, programme completions.
- **What they can do.**
  - Read and write across **every** module. The only constraint is the audit log: every sensitive action (role change, content publish, refund, manual access grant) writes an immutable `audit_log` row.
- **What they cannot do.**
  - Bypass the safety guardrails on AI replies. Admins read flagged runs but do not turn the safety filter off.
  - Edit the answer key of a quiz a student has already taken without leaving an audit trail.
  - See real plaintext passwords (passwords are hashed at rest — they only ever exist as hashes after sign-up).

---

## 3. The permissions matrix (one source of truth)

Read this row by row. `C` = create, `R` = read, `U` = update, `D` =
delete, `—` = no access. **Read is always scoped to your own data
unless the cell says `(all)`.**

| Resource | Visitor | Student | Instructor | Admin |
|---|---|---|---|---|
| Public website pages | R | R | R | R |
| Application form | C | — | — | R `(all)` + U |
| Contact form | C | C | C | R `(all)` |
| Own account | — | R + U | R + U | R + U |
| Other users' accounts | — | — | — | C R U D `(all)` |
| Payments | C (own) | C R (own) | — | R `(all)` |
| Course catalogue (public list) | R | R | R | R |
| Course content (read) | — | R (enrolled) | R (own courses) | R `(all)` |
| Course content (edit) | — | — | — *(v1)* | C R U D `(all)` |
| Lesson progress | — | C R (own) | R (own students) | R `(all)` |
| Quiz questions (without answers) | — | R (enrolled) | R (own courses) | R `(all)` |
| Quiz **answer key** | — | — | server-side only | server-side only |
| Quiz attempts | — | C R (own) | R (own students) | R `(all)` |
| Enrolments | — | C (free) / C-via-payment | R (own students) | C R U D `(all)` |
| Certificates | — | R + download (own) | R (own students) | R `(all)` |
| Notifications (system → user) | — | R (own inbox) | R (own inbox) | R `(all)` |
| KPIs / reports | — | — | — *(v1)* | R `(all)` |
| Audit log | — | — | — | R `(all)` |
| Role assignment | — | — | — | C U D `(all)` |
| AI tutor | — | use (rate-limited) | — *(v1)* | use |

Two rules govern this whole table:

1. **Default deny.** A request that does not match a row above is rejected with `403`.
2. **Ownership.** Where a cell says "(own)", the server confirms the resource belongs to the requester before responding. Ownership is checked **server-side**, never inferred from a client claim.

---

## 4. Account creation, consent and audit

- **Visitor → Student.** A parent / guardian creates the account on the student's behalf and supplies the consent. Until consent is recorded (a timestamped `consent_at` field on the student record), the account is `pending` and cannot sign in. This is non-negotiable because learners are often minors.
- **Instructor accounts** are created by an Admin (invite link). Self-signup as an instructor is disabled in v1.
- **Admin accounts** are created by another Admin only. The first admin is bootstrapped by the proprietor at initial setup. No self-signup path exists for admins, ever.
- **Audit log.** Every role change, every manual access grant, every refund, every publish action writes a row in `audit_log` with actor, action, target, and timestamp. The log is append-only and viewable by Admins.

---

## 5. Default-deny rules baked into every endpoint

Every backend endpoint, on every request, runs these checks in order
and returns the first failure it finds:

1. **Authenticated?** If the endpoint requires a session, no session → `401`.
2. **Role allowed?** Does the requester's role appear in the endpoint's allow-list (Section 3)? No → `403`.
3. **Ownership satisfied?** If the rule says "(own)", does the resource belong to the requester? No → `403`.
4. **Input valid?** Does the request body match the expected schema? No → `422`.
5. **Rate limit OK?** Public endpoints (application form, tutor) are rate-limited. Over the limit → `429`.

If a developer adds a new endpoint, those five checks are the first
thing reviewed in code review. **An endpoint without explicit RBAC is
considered a bug, not a missing feature.**

---

## 6. Mapping: four v1 roles → seven later roles in URD.md

| v1 role (this file) | Future split (URD.md) | When the split happens |
|---|---|---|
| Visitor | Visitor | unchanged |
| Student | Learner (minor) + Parent/Guardian | when the **parent portal** ships (feature 32 in `PRODUCT_REQUIREMENTS.md`) |
| Instructor | Teacher | unchanged in name; expanded permissions when **instructor authoring** ships (feature 30) |
| Admin | Admin + Bursar + Proprietor | when finance separation and KPI-only read access matter — likely after the platform has real volume |

So nothing in URD.md is thrown away — it is the **target shape** for
later phases. The migration is a **split**, not a rewrite: every later
role is a narrower slice of an existing v1 role.

---

## 7. Quick checklist for any new endpoint or page

Before merging a change that adds an endpoint or a page, the change is
not done until each of these is true:

- [ ] The page or endpoint is listed in the permissions matrix above (or this file is updated in the same change).
- [ ] The endpoint enforces the five default-deny checks in Section 5.
- [ ] Ownership is checked **server-side** for every `(own)` row touched.
- [ ] Sensitive mutations write an `audit_log` entry.
- [ ] A test exercises both the allowed and the denied case (a Student cannot read another Student's record; a Visitor cannot access a Student endpoint; etc.).
- [ ] No secret, key or password appears in the code path.
