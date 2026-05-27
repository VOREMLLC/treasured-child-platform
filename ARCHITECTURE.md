# Architecture — the system map

This document describes **what** the platform is and **how its pieces fit
together**. It does not describe technology choices in detail; for that
see [docs/SDD.md](docs/SDD.md).

---

## One paragraph

Treasured Child is a single platform with two engines: a **public website**
that attracts parents, accepts applications and collects fees, and a
**learning management system (LMS)** that delivers paid online courses
using the VOREM Agentic Education System. Both engines share the same
authentication, user records, payments and notifications. Learners are
often children, so child-safety guardrails run across every learning
interaction.

---

## The two engines

```
                         ┌──────────────────────────┐
                         │   Treasured Child        │
                         │   Platform               │
                         └────────────┬─────────────┘
                                      │
              ┌───────────────────────┴────────────────────────┐
              │                                                │
   ┌──────────▼───────────┐                       ┌────────────▼───────────┐
   │  Public website      │                       │  Learning management   │
   │  (Visitors, parents) │                       │  system (Students)     │
   │                      │                       │                        │
   │  • Home, About       │                       │  • Course catalogue    │
   │  • Programmes        │                       │  • Enrolment           │
   │  • Apply & pay       │                       │  • VOREM agentic       │
   │  • News, contact     │                       │    learning            │
   └──────────────────────┘                       │  • Assessment          │
                                                  │  • Certificates        │
                                                  │  • Dashboard           │
                                                  └────────────────────────┘
                                      │
                         ┌────────────▼─────────────┐
                         │  Shared services         │
                         │  • Auth (RBAC)           │
                         │  • Payments (Paystack)   │
                         │  • Notifications         │
                         │  • Data layer (READ-     │
                         │    ONLY for real users)  │
                         └──────────────────────────┘
```

---

## Modules (one module, one job)

Each module is its own folder with its own README, its own tests, and a
single, narrow responsibility. If one breaks, the others keep running.

| Module | Responsibility |
|---|---|
| `public_site/` | Marketing pages, programme info, application form, contact. Read-mostly. |
| `auth/` | Sign-up, login, sessions, password reset, role-based access. |
| `courses/` | Course catalogue, lessons, instructor authoring. |
| `enrolment/` | Student-to-course mapping, payment-gated access, waitlists. |
| `learning/` | **The VOREM agentic education system.** Explains a concept, checks understanding, adapts to the learner's level, encourages and tracks progress. Child-safety guardrails live here. |
| `assessment/` | Quizzes, assignments, grading, exam-prep practice. |
| `certificates/` | Issuing and verifying certificates of completion. |
| `dashboard/` | Personalised views for Admin, Instructor, Student. |
| `notifications/` | Email and in-app messages (welcome, payment receipt, reminders). |
| `data_layer/` | The single source of truth. **Read-only** where it touches real user data, unless write permission is granted explicitly. |

---

## Roles (who can do what)

Detail in [docs/URD.md](docs/URD.md). At a glance:

- **Admin** — full control, all modules.
- **Instructor** — creates and edits their own courses, sees their own students.
- **Student** — enrols, takes courses, sees their own progress only.
- **Visitor** — public website only, no learning content.

---

## Child-safety boundary

Anything that generates language to a learner (the VOREM tutor in
`learning/`, any AI feature) passes through guardrails defined alongside
`learning/`. The rules in [docs/AGENTS.md](docs/AGENTS.md) apply: no
unsafe content, no requests for personal contact details, escalation to
a human on distress. This is the single most important constraint in the
codebase.

---

## Where to look next

- Product surface area → [docs/PRD.md](docs/PRD.md) (existing) / `docs/PRODUCT_REQUIREMENTS.md` (to be written in Phase 2).
- Roles & permissions → [docs/URD.md](docs/URD.md) / `docs/USER_ROLES.md` (Phase 2).
- Build order → [docs/PWD.md](docs/PWD.md) / `docs/BUILD_PLAN.md` (Phase 2).
- Technical detail → [docs/SDD.md](docs/SDD.md).
- AI agents → [docs/AGENTS.md](docs/AGENTS.md).
