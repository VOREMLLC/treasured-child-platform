# PWD — Product Work Document
**Product:** Treasured Child Platform · Translates the PRD into a sequenced, buildable delivery plan.

## 1. Delivery principle
Ship the **revenue-proven** layer first. Each phase is independently valuable and de-risks the next. Mapped to the 3-layer digital strategy.

## 2. Phases

### Phase 1 — Foundation & Cash (Weeks 1–3) · *Layer 1*
**Outcome:** the school is online and collecting fees.
- Marketing site (F1) live on Vercel.
- Application form (F2) → admin queue.
- Paystack fee payment with server verification (F3).
- Auth + RBAC skeleton (F4).
- **Definition of Done:** a parent can find the school, apply, and pay a fee online; payment verified server-side; admin sees the application.

### Phase 2 — The LMS (Weeks 4–7) · *Layer 2*
**Outcome:** learners learn online; first paid programme earns.
- Learner dashboard + gamification (F5).
- Course → lesson → quiz engine (F6).
- Paid programme enrolment + access gating (F7).
- AI Tutor v1, child-safe (F8).
- **DoD:** a learner enrols in the AI & Data course, completes a lesson + quiz, earns XP, and gets safe AI help.

### Phase 3 — Scale & Reports (Weeks 8–12) · *Layer 2→3*
**Outcome:** retention, parent trust, repeatability.
- Parent portal + progress nudges (F9, Progress agent).
- Teacher AI authoring tools (F10, Curriculum agent).
- Subscriptions (F11).
- Multi-tenant groundwork for white-label (F12).
- **DoD:** parents receive progress reports; teachers publish AI-drafted quizzes after review; recurring billing works.

## 3. Epics → sample stories

| Epic | Story | Phase |
|---|---|---|
| Online fees | *As a parent, I pay school fees online and get a receipt.* | 1 |
| Admissions | *As an admin, I review applications in a queue.* | 1 |
| Learning | *As a learner, I complete a lesson and see my progress rise.* | 2 |
| Assessment | *As a learner, I take a quiz and get an instant score + XP.* | 2 |
| Monetisation | *As a parent, I enrol my child in a paid programme.* | 2 |
| AI Tutor | *As a learner, I ask the tutor to explain a concept simply.* | 2 |
| Reporting | *As a proprietor, I see revenue & enrolment on a dashboard.* | 3 |

## 4. Dependencies & risks
- F3 (payments) blocks F7 (paid programmes). Build payment verification first.
- F4 (RBAC) blocks every portal feature. Land auth early.
- AI Tutor (F8) depends on guardrails in `AGENTS.md` — safety review before launch.

## 5. Cadence & quality gates
Weekly increments; every increment runnable + tested. No phase closes until its DoD passes and docs are updated. Demo to proprietor at the end of each phase.
