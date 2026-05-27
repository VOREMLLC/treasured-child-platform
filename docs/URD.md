# URD — User Role Document
**Product:** Treasured Child Platform · Defines every actor, their goals, and their permissions (RBAC).

## 1. Roles

| Role | Who | Primary goal |
|---|---|---|
| **Visitor** | Prospective parent (unauthenticated) | Evaluate the school; apply; pay |
| **Learner** | Enrolled student (minor) | Learn, complete courses, earn XP |
| **Parent/Guardian** | Account holder for a learner | Track progress; pay fees & programmes |
| **Teacher** | Instructor | Deliver courses; mark; author content |
| **Bursar** | Finance officer | Manage fees, payments, reconciliation |
| **Admin** | Head of School / platform admin | Manage users, courses, admissions |
| **Proprietor** | Owner / executive | View KPIs & reports; full oversight |
| **AI Agent** | System actor | Tutor, admissions, content, analytics (see AGENTS.md) |

## 2. Key journeys
- **Visitor:** land → view programmes/results → apply (form) → pay fee → become Parent.
- **Learner:** log in → dashboard → open course → lesson → quiz → earn XP/badge → ask AI Tutor.
- **Parent:** log in → view child progress → pay fees / enrol child in online programme.
- **Teacher:** log in → view classes → mark quizzes → generate a quiz with AI (approve before publish).
- **Bursar:** view payments → reconcile → flag unpaid → export.
- **Admin:** approve applications → create courses/programmes → manage users/roles.
- **Proprietor:** open dashboard → revenue, enrolment, engagement KPIs.

## 3. RBAC permissions matrix
`C`=create `R`=read `U`=update `D`=delete `—`=none. Read is own-scope unless noted *(all)*.

| Resource | Visitor | Learner | Parent | Teacher | Bursar | Admin | Proprietor |
|---|---|---|---|---|---|---|---|
| Marketing pages | R | R | R | R | R | RU | R |
| Application | C | — | R | — | R | RU | R*(all)* |
| Payment | C | — | CR | — | R*(all)* | R*(all)* | R*(all)* |
| Own account | — | RU | RU | RU | RU | RU | RU |
| Learner record | — | R | R | R | R | CRUD | R*(all)* |
| Course content | — | R | R | CRU | — | CRUD | R |
| Quiz / attempt | — | CR (attempt) | R | CRU + grade | — | CRUD | R |
| Programme enrolment | — | R | C | R | R | CRUD | R |
| AI Tutor | — | use | — | use | — | use | use |
| KPI dashboard | — | — | — | partial | finance | RU | R*(all)* |
| User & role mgmt | — | — | — | — | — | CRUD | R |

## 4. Auth rules
JWT access (short-lived) + refresh. Default-deny: every endpoint checks role + ownership. Learner accounts require verified Parent/Guardian consent before activation. Sensitive actions (role change, refunds, content publish) are audit-logged.
