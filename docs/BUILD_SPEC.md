# BUILD_SPEC — The Complete Detail
**Product:** Treasured Child Platform · This is the master technical brief. With `CLAUDE.md` + `docs/` + this file, an agent can build the app with no guesswork. Read `PRD → URD → SDD → AGENTS`, then this.

---

## 0. How to use this spec
Feed Claude Code one **ticket** at a time (Section 12), in order. For each ticket the agent: reads the referenced sections here, builds only that ticket, writes tests, and stops. Never let it skip ahead. Anything marked **[YOU DECIDE]** is a real-world choice the school must supply (Section 14) — the agent uses the placeholder until you replace it.

---

## 1. Brand & Design System
The look is **academic-premium**: trustworthy, warm, modern. Define these as design tokens (Tailwind theme + CSS variables) once, use everywhere.

### Colour tokens
| Token | Value | Use |
|---|---|---|
| `--green` | `#13563a` | primary brand, buttons, headers |
| `--green-deep` | `#0a2b1c` | dark surfaces, footer, sidebar |
| `--green-light` | `#1c7049` | accents, progress fills |
| `--gold` | `#c2912f` | secondary accent, highlights, CTAs |
| `--gold-light` | `#e3bd62` | on-dark accent text |
| `--cream` | `#fbf8f1` | page background |
| `--paper` | `#f4efe3` | card/surface background |
| `--ink` | `#1b251f` | primary text |
| `--muted` | `#5e6c62` | secondary text |
| `--line` | `#e5ddcc` | borders |
| semantic | success `#1c7049`, danger `#a32d2d`, warning `#854f0b`, info `#185fa5` | states |

### Typography
- Display/headings: **Fraunces** (600/700). Body & UI: **Hanken Grotesk** (400/500). Mono: system mono.
- Scale: h1 40/48, h2 28/34, h3 20/26, body 16/26, small 14/22. Sentence case everywhere. Never ALL CAPS for headings.

### Spacing, radius, elevation
- Spacing scale (px): 4, 8, 12, 16, 24, 32, 48, 64. Radius: sm 8, md 12, lg 16, pill 40. Shadow: one soft elevation `0 20px 50px -24px rgba(12,58,38,.45)` for cards/modals only — flat elsewhere.

### Component inventory (build as reusable components)
Button (gold/green/outline/ghost; sm/md), Card, StatCard, Badge/Pill, Input, Select, Field (label+input+error), Modal, Toast, ProgressBar, Avatar (initials), CourseCard, LessonRow, Nav (public), Sidebar (portal), TopBar (gami chips), Table, EmptyState, Spinner, PaymentSheet, TutorPanel.

### Voice
Warm, plain, encouraging. Nigerian English. No jargon to parents. Naira (₦) formatted with thousands separators.

---

## 2. Information Architecture (routes — Next.js App Router)

**Public**
`/` home · `/about` · `/programmes` · `/programmes/[slug]` · `/results` · `/admissions` · `/apply` (form) · `/pay` (fee payment) · `/contact`

**Auth**
`/login` · `/register` · `/forgot-password`

**Learner / Parent portal** (auth + role)
`/portal` dashboard · `/portal/courses` · `/portal/courses/[id]` · `/portal/courses/[id]/lessons/[lessonId]` · `/portal/courses/[id]/quiz/[quizId]` · `/portal/programmes` (browse/enrol/pay) · `/portal/profile` · `/portal/children` + `/portal/children/[id]` (parent only)

**Teacher** `/teach` · `/teach/courses` · `/teach/grade` · `/teach/authoring`
**Admin** `/admin` · `/admin/applications` · `/admin/users` · `/admin/courses` · `/admin/payments`
**Proprietor** `/admin/reports` (KPIs; read-only)

Every portal/admin route is server-guarded by role (Section 6). Unauthorised → redirect to `/login` or 403.

---

## 3. Screen Specifications
For each screen: **Purpose · Layout · Data · States · Actions · Acceptance criteria (AC)**. States always include loading, empty, error unless trivial.

### 3.1 Home `/`
- Purpose: convert visitors → apply / pay / enter portal.
- Layout: sticky nav; hero (headline, sub, CTAs: Apply, Enter portal; trust stats 18→200, 100% distinction, 3 acres); "Why us" 3 cards; programmes preview (3); results band; admissions CTA; footer.
- Data: programmes list (3 featured), stats (static or `/stats`).
- Actions: Apply → `/apply`; Pay fees → `/pay`; Student portal → `/login`.
- AC: loads < 2s on 3G; all CTAs route correctly; responsive 360–1440px; passes Lighthouse a11y ≥ 90.

### 3.2 Programmes `/programmes` + `/programmes/[slug]`
- Purpose: show academic levels + online programmes; drive enrolment.
- Layout: grid of programme cards (Nursery, Primary, Secondary, BECE/Common Entrance, WAEC/JAMB, AI & Data Analytics). Detail page: description, what's included, price (online ones), CTA.
- Data: `GET /programmes`, `GET /programmes/{slug}`.
- AC: paid programmes show price [YOU DECIDE]; "Enrol" routes to login→checkout if logged out.

### 3.3 Apply `/apply`
- Purpose: capture an admission lead.
- Layout: form — child full name, parent/guardian name, email, phone, class applying for (Nursery/Primary/JSS/SSS), message (optional).
- Validation: required fields; email + Nigerian phone format; client + server.
- Actions: submit → `POST /applications` → success screen ("we'll contact you"). On error, inline messages.
- AC: lead appears in `/admin/applications`; spam-guarded (rate limit, honeypot); no payment here.

### 3.4 Pay fees `/pay` (public) and in-portal
- Purpose: collect school fees online.
- Layout: PaymentSheet — payer email, term/amount [YOU DECIDE fee table], Paystack inline. See Section 7.
- AC: access never granted on client claim; success only after server verify; receipt emailed; `Payment` row recorded with status `success` + `verified_at`.

### 3.5 Login / Register `/login` `/register`
- Login: email + password → JWT (access cookie httpOnly + refresh). Register (parent): name, email, phone, password; learner accounts are created by parent/admin and **consent-gated** (URD §4).
- AC: wrong creds → generic error (no user enumeration); rate-limited; redirect to role home on success.

### 3.6 Learner dashboard `/portal`
- Purpose: orient and motivate.
- Layout: welcome + streak; 3 stat cards (XP, level, active courses); "Continue learning" (next incomplete course, Resume); progress list (all courses with bars); class leaderboard (top 5, learner highlighted).
- Data: `GET /me/dashboard`.
- States: empty (no courses → CTA to Programmes).
- AC: progress bars match server data; "Resume" opens the first incomplete lesson.

### 3.7 My courses `/portal/courses`
- Grid of `CourseCard` (title, level, type badge school/online, progress %). Click → course detail.
- Data: `GET /me/courses`. AC: only enrolled courses shown; paid courses without active access show "Locked → Enrol".

### 3.8 Course detail `/portal/courses/[id]`
- Layout: header (title, level, overall progress); two columns — lesson list (left, completion ticks + duration) and lesson viewer (right: title, video placeholder, body content, "Mark complete (+XP)", "Ask Ada"). If course has a quiz, show a quiz entry.
- Data: `GET /courses/{id}` (lessons, progress).
- Actions: select lesson; `POST /lessons/{id}/complete` → progress + XP update (Section 8); open quiz; open Tutor.
- AC: completing a lesson is idempotent (no double XP); progress recomputes server-side; locked content blocked if no access.

### 3.9 Lesson `/portal/courses/[id]/lessons/[lessonId]`
- Content render (rich text/markdown), media placeholder, prev/next, mark complete. AC: cannot complete a lesson the learner can't access.

### 3.10 Quiz `/portal/courses/[id]/quiz/[quizId]`
- Layout: questions (MCQ), submit, result panel (score X/total, %, XP earned, badge if perfect). **Answer key never sent to client** — scoring server-side via `POST /quizzes/{id}/attempt`.
- AC: score computed on server; XP from Section 8; attempt stored; re-attempts allowed but XP awarded once per best-improvement rule [YOU DECIDE: first-attempt-only vs best].

### 3.11 Programmes & fees (portal) `/portal/programmes`
- Layout: cards (School fees; BECE/Common Entrance; AI & Data Analytics flagship) each with price + Enrol/Pay → PaymentSheet. AC: on verified payment, create `Enrolment` (paid) and grant access; show in My courses.

### 3.12 Profile `/portal/profile`
- Learner info, class, level, badges earned, linked guardian. AC: badges reflect `Gamification.badges`.

### 3.13 Parent: children `/portal/children` `/portal/children/[id]`
- List linked learners; per-child progress + payments; pay fees / enrol child. AC: parent sees only their own children (ownership check).

### 3.14 Teacher `/teach*`
- Dashboard (classes), grade queue (quiz attempts to review), authoring (request AI-drafted quiz/lesson → review → publish). AC: AI drafts never auto-publish; publish is teacher action, audit-logged.

### 3.15 Admin `/admin*`
- Applications queue (review/approve/reject), users & roles (CRUD, role change audit-logged), courses CRUD, payments (list, reconcile, export CSV). AC: default-deny; every mutation audit-logged.

### 3.16 Proprietor reports `/admin/reports`
- KPI dashboard: revenue (fees + programmes), enrolment, weekly active learners, programme completions (PRD §3). Read-only. AC: numbers tie to source tables; date-range filter.

---

## 4. Data Model (field-level)
PostgreSQL via SQLAlchemy. Money in **kobo** (integer). IDs are UUID. Timestamps `created_at`, `updated_at`.

```
User(id, email[unique], password_hash, role[enum: learner|parent|teacher|bursar|admin|proprietor], status[pending|active|suspended], created_at)
Guardian(id, user_id→User, phone, address)
Learner(id, user_id→User, guardian_id→Guardian, dob, class_level, consent_at[nullable], status)
Course(id, slug[unique], title, type[school|online], level, summary, is_paid[bool], price_kobo[nullable], published[bool])
Module(id, course_id→Course, order, title)
Lesson(id, module_id→Module, order, title, content[markdown], media_url[nullable], duration_min)
LessonProgress(id, learner_id→Learner, lesson_id→Lesson, completed_at) [unique(learner,lesson)]
Quiz(id, lesson_id→Lesson[nullable] | course_id, title, pass_mark)
Question(id, quiz_id→Quiz, order, prompt, options[json array], answer_index[int, SERVER ONLY])
Attempt(id, learner_id→Learner, quiz_id→Quiz, answers[json], score, total, taken_at)
Enrolment(id, learner_id→Learner, course_id→Course, status[active|expired], access_expires_at[nullable], source[free|paid])
Payment(id, payer_id→User, reference[unique], amount_kobo, purpose[fees|programme:{course_id}], status[pending|success|failed], verified_at[nullable], raw[json])
Subscription(id, payer_id→User, plan, status, renews_at)   // Phase 3
Gamification(learner_id→Learner[pk], xp, level, streak_days, last_active_date, badges[json array])
Application(id, child_name, guardian_name, email, phone, class_level, message, status[new|contacted|enrolled|rejected], created_at)
AgentRun(id, agent, learner_id[nullable], input, output, tokens, flagged[bool], created_at)
AuditLog(id, actor_id→User, action, target_type, target_id, meta[json], created_at)
```
Constraints: `Question.answer_index` is never serialised to any client schema. `LessonProgress` unique prevents double-credit. `Payment.reference` unique + idempotent verify.

---

## 5. API Contract (representative; all JSON, JWT unless public)
Format: `METHOD path — auth — request → response (errors)`

```
POST /auth/register — public — {name,email,phone,password,role:'parent'} → {user} (409 email exists)
POST /auth/login — public — {email,password} → sets cookies, {user} (401)
POST /auth/refresh — refresh cookie → new access (401)
POST /applications — public(rate-limited) — {child_name,guardian_name,email,phone,class_level,message?} → {id} (422)
GET  /programmes — public → [{slug,title,type,level,is_paid,price_kobo}]
GET  /programmes/{slug} — public → {…detail, modules:[…]}
GET  /me/dashboard — learner → {xp,level,streak,courses:[{id,title,progress}],leaderboard:[…]}
GET  /me/courses — learner → [{id,title,type,progress,locked}]
GET  /courses/{id} — learner(enrolled) → {…, modules:[{lessons:[{id,title,duration_min,completed}]}], quiz?} (403 not enrolled)
POST /lessons/{id}/complete — learner — {} → {progress, xp_awarded} (idempotent; 403)
GET  /quizzes/{id} — learner → {title, questions:[{id,prompt,options}]}  // NO answer_index
POST /quizzes/{id}/attempt — learner — {answers:[index]} → {score,total,xp_awarded,badge?}
POST /enrolments — learner/parent — {course_id} → 402 if paid+unpaid; else {enrolment}
POST /payments/initialize — auth — {purpose, course_id?} → {reference, amount_kobo, public_key}
POST /payments/verify — auth — {reference} → server-verifies w/ Paystack → {status} + grants access
POST /agents/tutor — learner(rate-limited) — {lesson_id, question} → {reply}  // safety-filtered
POST /agents/admissions — public(rate-limited) — {message} → {reply, lead_id?}
GET  /admin/applications — admin → [Application]
PATCH /admin/applications/{id} — admin — {status} → {} (audit-logged)
GET  /reports/kpis — admin|proprietor — {revenue, enrolment, wal, completions}
```
Every endpoint: Pydantic validation, RBAC + ownership, structured errors `{error, code}`, audit on sensitive mutations.

---

## 6. Auth & RBAC
- Passwords argon2. JWT access (15 min, httpOnly cookie) + refresh (30 d, rotated). CSRF protection on cookie auth.
- Middleware resolves `user.role`; each route declares required role(s) and ownership rule. **Default-deny.** Matrix is in `URD.md §3` — implement it exactly.
- Learner activation requires `Learner.consent_at` set by the guardian/admin flow before login is allowed.

---

## 7. Payments Flow (Paystack) — exact sequence
1. Client calls `POST /payments/initialize {purpose, course_id?}`. Server computes `amount_kobo` from the **server-side** fee/price table (never trust client amount), creates a `Payment(status=pending, reference)`, returns `reference` + `public_key`.
2. Client opens Paystack inline with `public_key`, `reference`, `amount`.
3. On Paystack callback, client calls `POST /payments/verify {reference}`.
4. Server calls Paystack verify API with the **secret key**; if `status=success` and amount matches, set `Payment.status=success, verified_at=now`, then grant: fees → mark term paid; programme → create `Enrolment(source=paid, access_expires_at)`.
5. Also handle Paystack **webhook** (idempotent on `reference`) as the source of truth in case the client drops.
- AC: access is granted **only** in step 4/5, never from the client. Re-verifying a reference is idempotent.

---

## 8. Gamification Rules (exact)
- Lesson complete: **+20 XP** (once per lesson, enforced by `LessonProgress` unique).
- Quiz: **+15 XP per correct answer**; **+30 XP** bonus for a perfect score.
- Level: `level = floor(total_xp / 300) + 1`.
- Streak: on a learning action, if `last_active_date == yesterday` → `streak_days += 1`; if `== today` → unchanged; else reset to 1. Update `last_active_date = today`.
- Badges (auto-award, store in `Gamification.badges`): `First Lesson` (1st completion), `7-Day Streak` (streak≥7), `Quiz Master` (any perfect quiz), `Course Complete` (course 100%). Award is idempotent.

---

## 9. AI Agent Tool Contracts (build per `AGENTS.md`)
Agents call only these permissioned, read-mostly tools (no direct DB):
```
get_lesson_context(lesson_id) → {title, body, course_title, class_level}
get_learner_progress(learner_id) → {xp, level, courses:[{title,progress}]}   // guardian/self scope
get_programmes() / get_published_fees() → public catalogue + fee table
create_lead({name,email,phone,message}) → {lead_id}        // admissions only
propose_quiz(course_id, topic) → draft (teacher review required; never publishes)
send_notification(template, guardian_id) → {} (rate-limited; progress agent)
```
Every agent call: input policy filter → scoped tools → output filter → log `AgentRun`. Tutor distress signals → return human-contact prompt, set `flagged=true`. Money/grades/access are **code, never agent**.

---

## 10. Non-Functional Requirements
- Performance: marketing FCP < 2s on 3G; API p95 < 300ms (non-AI); tutor < 6s. Bundle-split portal from marketing.
- Resilience: LMS fully usable if agent runtime is down (graceful degrade). Idempotent payments. Retry/backoff on Paystack.
- Accessibility: WCAG AA; keyboard nav; visible focus; alt text; Lighthouse a11y ≥ 90.
- Security: NDPR — minimise minor data, encrypt PII at rest, consent gate, audit log. No secrets in repo. Server-side validation everywhere.
- i18n/format: Naira, Nigerian phone/date formats. Low-bandwidth: optimise images, lazy-load media.

---

## 11. Environment & Config
Use `.env` (names in `.env.example`): `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY`, `ANTHROPIC_API_KEY`, `AGENT_MODEL`, `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY`. Three environments: dev (local) → staging (Vercel preview + Railway staging) → prod. Migrations via Alembic on deploy. CI: lint + tests on PR; CD on merge to `main`.

---

## 12. Build Sequence — tickets for Claude Code
Give one per session; each ends runnable + tested. Maps to `PWD.md` phases.

**Phase 1 — foundation & cash**
- T1: Scaffold monorepo per `STRUCTURE.md`; design tokens (§1); shared UI components shell. DoD: `npm run dev` + `uvicorn` both boot; tokens applied.
- T2: Public marketing pages (§3.1–3.2) + nav/footer, responsive, a11y ≥ 90.
- T3: Application flow (§3.3) + `POST /applications` + admin queue read (§3.15). DoD: lead round-trips.
- T4: Auth + RBAC (§5,§6) — register/login/refresh, role middleware, default-deny.
- T5: Payments (§7) — initialize/verify + webhook; fee payment screen (§3.4). DoD: verified-only access; idempotent.

**Phase 2 — the LMS**
- T6: Data model + migrations (§4); seed one school course + the AI & Data course.
- T7: Learner dashboard + my courses + course/lesson flow (§3.6–3.9) + lesson complete + gamification (§8).
- T8: Quiz engine (§3.10) with server-side scoring; XP/badges.
- T9: Programmes & paid enrolment (§3.11) gated by verified payment.
- T10: AI Tutor (§9, `AGENTS.md`) with full safety pipeline + `AgentRun` logging.

**Phase 3 — scale & reports**
- T11: Parent portal (§3.13) + progress/nudge agent.
- T12: Teacher authoring (§3.14) — AI draft → review → publish (human-in-loop).
- T13: Proprietor KPI reports (§3.16). T14: subscriptions; T15: multi-tenant groundwork.

---

## 13. Definition of Done & Acceptance (global gates)
A ticket is done only when: maps to a section here; unit + integration tests pass; lint/format pass; app boots; RBAC + validation on every new endpoint; no secret committed; relevant doc updated; for any money/access path, server-side verification proven by a test. Each screen meets its AC and renders loading/empty/error states.

---

## 14. [YOU DECIDE] — real-world inputs to supply
The agent uses placeholders until you replace these:
1. **Fee table** — exact ₦ amounts per class/term, and online-programme prices.
2. **Brand assets** — logo file, 4–6 real campus/classroom photos, school colours if different from §1.
3. **Management bios** — real names, qualifications, roles for `URD`/about page (no invented credentials).
4. **Domain** — e.g. treasuredchild.ng — and email/SMS sender details.
5. **Paystack live keys** — from the school's verified Paystack account.
6. **Curriculum content** — real lessons/quizzes per course (start with 1 school course + the AI & Data course).
7. **Consent & privacy text** — the parental-consent wording and a privacy notice (NDPR).
8. **Quiz re-attempt rule** — first-attempt-only vs best-attempt XP.

Supply these eight and the spec is fully closed — the app builds with zero guesswork.
