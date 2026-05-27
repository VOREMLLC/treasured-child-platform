# `auth/` — accounts, sessions, role-based access

## What it does
Owns every authentication and authorisation concern: sign-up, log in,
log out, session refresh, password reset, and the **default-deny**
middleware every protected endpoint depends on. The four v1 roles
(Admin, Instructor, Student, Visitor) are defined here; the permissions
matrix lives in [`USER_ROLES.md`](../docs/USER_ROLES.md).

## What goes in (input)
- Sign-up / log-in / log-out / refresh / reset HTTP requests.
- Auth headers and cookies on every other request the platform serves.

## What comes out (output)
- Session cookies (JWT access — short-lived, httpOnly; refresh — longer, rotated).
- A request context attached to every authenticated call: `user.id`, `user.role`, ownership helpers.
- 401 / 403 / 422 / 429 responses on failed checks.

## Owns these v1 features
8. Sign up · 9. Log in / log out · 10. Password reset · 11. Role-gated
access.

## Build slices
S5 (User model + DB), S7, S8, S9, S10 (RBAC middleware).

## What does **not** belong here
- Course / lesson / quiz content (`courses/`, `learning/`, `assessment/`).
- Business rules about progress, payments, certificates.
- Database schema for non-user tables — those live in [`data_layer/`](../data_layer/).

## Safety rules that apply here
- Passwords are stored as **argon2 hashes** — plaintext never persists.
- Wrong-credential responses are deliberately generic (no user-enumeration).
- Student accounts require **parental consent** (`consent_at` set) before they can sign in.
- Every sensitive action (role change, admin creation, manual access grant) writes an `audit_log` row.
