# `public_site/` — the public website

## What it does
Everything a person who is **not signed in** can see and do: home page,
about, programmes catalogue, programme detail, contact, apply, pay.
Read-mostly. No personal learner data lives in this module.

## What goes in (input)
- A visitor's HTTP request (anonymous, no session cookie required).
- Form submissions from the application form, the contact form, and the public payment page.

## What comes out (output)
- Rendered marketing pages (server-rendered React via Next.js).
- A small set of **public** POST endpoints: `/applications`, `/payments/initialize`, `/payments/verify`, the contact form.
- Confirmation pages on success and validation errors on failure.

## Owns these v1 features
1. Home page · 2. About · 3. Programmes catalogue · 4. Programme
detail · 5. Contact · 6. Application form · 7. Online fee payment
(see [PRODUCT_REQUIREMENTS.md](../docs/PRODUCT_REQUIREMENTS.md)).

## Build slices
S0.2, S1, S2, S3, S4, S6 (apply form), S11–S12 (Paystack initialize +
verify + webhook). See [BUILD_PLAN.md](../docs/BUILD_PLAN.md).

## What does **not** belong here
- Anything that requires sign-in (use [`auth/`](../auth/) and [`dashboard/`](../dashboard/)).
- Course content, lessons, quizzes (those are in [`courses/`](../courses/), [`learning/`](../learning/), [`assessment/`](../assessment/)).
- Database models — those live in [`data_layer/`](../data_layer/).

## Safety rules that apply here
- Application form and contact form are **rate-limited** and include a honeypot.
- Payments are server-verified only (see [`enrolment/`](../enrolment/) for the access-grant side).
- No personal data of minors appears on any public route, ever.
