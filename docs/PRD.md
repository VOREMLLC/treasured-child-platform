# PRD — Product Requirements Document
**Product:** Treasured Child Platform · **Owner:** Proprietor / Product Lead · **Status:** v1 (MVP)

## 1. Problem
Treasured Child School grew from 18 to 200 learners on reputation alone, but has **no digital presence**: parents can't find it online, fees are collected manually (slow, leaky), and learning stops at the school gate. The school cannot scale enrolment or earn beyond its physical capacity.

## 2. Vision
A platform with two engines: a **brand/admissions website** that converts interest into enrolled, fee-paying students, and an **LMS** that sells education to learners anywhere — making the school a profitable, technology-enabled education brand.

## 3. Goals & success metrics (first 12 months)

| Goal | Metric | Target |
|---|---|---|
| Increase enrolment | Online applications/term | ≥ 60 |
| Capture fees faster | Fees paid online | ≥ 70% of fees |
| New online revenue | Paid online-programme enrolments | ≥ 150 |
| Engagement | Weekly active learners in LMS | ≥ 65% |
| Differentiation | AI & Data Analytics course completions | ≥ 100/yr |

## 4. Users
See `URD.md`. Primary: Prospective Parent, Learner, Parent/Guardian, Teacher, Admin/Bursar, Proprietor. System actors: AI agents (`AGENTS.md`).

## 5. Scope

### MVP (Must)
- Public site: home, programmes, results, admissions, contact.
- Online application form (lead capture) + online **fee payment** (Paystack).
- Auth + RBAC; learner & parent portals.
- LMS: course catalogue, lessons, quizzes, progress tracking.
- One paid online programme live (BECE/Common Entrance prep) + the AI & Data Analytics course.
- Gamification: XP, levels, streaks, badges.
- AI Tutor (safe, in-lesson help).

### Should (Phase 2)
- Parent reports & nudges (Progress agent). Teacher content tools (Curriculum agent). Subscriptions/recurring billing.

### Could (Phase 3)
- White-label tenancy to license the platform to other schools.

### Won't (now)
- Native mobile apps; accredited degree programmes; full SIS/HR suite.

## 6. Feature requirements (MoSCoW)

| ID | Feature | Priority |
|---|---|---|
| F1 | Branded, SEO-ready marketing site | Must |
| F2 | Online application (lead → admin queue) | Must |
| F3 | Paystack fee payment + server verification | Must |
| F4 | Account auth + role-based access | Must |
| F5 | Learner dashboard (courses, progress, XP) | Must |
| F6 | Course → lesson → quiz flow with scoring | Must |
| F7 | Paid online programme enrolment + access gating | Must |
| F8 | AI Tutor (Socratic, child-safe) | Must |
| F9 | Parent portal (child progress, payments) | Should |
| F10 | Teacher curriculum/quiz authoring (AI-assisted) | Should |
| F11 | Recurring subscriptions | Should |
| F12 | White-label multi-tenancy | Could |

## 7. Assumptions & constraints
Low-bandwidth users (optimise payloads, offline-tolerant where possible); intermittent power (no hard real-time deps); Naira pricing; learners are minors (consent + safety mandatory); single school at MVP, multi-tenant-ready in design.

## 8. Out-of-scope risks → mitigations
Payment trust → server-side verify only. Content quality → AI drafts, human approves. Adoption → start with fee payment (proven value) before learning features.
