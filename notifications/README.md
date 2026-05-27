# `notifications/` — email and in-app messages

## What it does
Sends transactional emails for the three v1 events that matter:

1. **Welcome email** on a verified sign-up.
2. **Application received email** on a new admission application.
3. **Payment receipt email** on a server-verified Paystack payment.

In development the sender writes to the console; in production it uses
a real email provider configured via `.env`. Lesson reminders and
nudges are **"later"** ([feature 36](../docs/PRODUCT_REQUIREMENTS.md)).

## What goes in (input)
- Events emitted by other modules:
  - `auth/` after a verified sign-up.
  - `public_site/` after an application form submission.
  - `enrolment/` / payments flow after a Payment row transitions to `status=success`.

## What comes out (output)
- One email per event. Sending is **idempotent** on a `(event_type, target_id)` key — the same event never sends twice.
- An entry in a future `notification_log` table so we can prove what was sent.

## Owns these v1 features
25. Welcome email · 26. Payment receipt email · 27. Application received
email.

## Build slices
S6 (application emails wired here), S13 (payment receipt), S28 (welcome).

## What does **not** belong here
- The decision to enrol someone, grant access, or change a role — those live in their owning modules; `notifications/` only **announces** what already happened.
- SMS, WhatsApp, push notifications — not in v1.

## Safety rules that apply here
- **No payment receipt is ever sent until the server has verified the payment with Paystack.** Never on a client claim.
- **No email content references another learner.** Even sibling-account emails are sent to the right address only.
- **Secrets (SMTP / provider keys) live in `.env`**, never in code.
