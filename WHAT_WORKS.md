# What works — the proven-feature ledger

This file is the truth ledger for the platform. A feature appears here
**only when** all three are true:

1. It is built.
2. It has at least one automated test that exercises the real behaviour.
3. That test currently passes on the `main` branch.

If any of those stops being true, the feature is **removed** from this
list immediately — not "marked as broken", **removed**. The list reflects
what works *right now*, not what used to work or what we hope works.

This is rule 1 (truth over hype) and rule 3 (measure, don't assume) made
concrete.

---

## Format

Each entry has four fields:

| Feature | Module | Proof | Date verified |
|---|---|---|---|

- **Feature** — one sentence in plain language, written from the user's point of view.
- **Module** — the folder it lives in (e.g. `auth/`).
- **Proof** — the path to the test file and the test name.
- **Date verified** — the day the test was last seen passing.

---

## Confirmed working features

| Feature | Module | Proof | Date verified |
|---|---|---|---|
| The backend boots and `GET /healthz` returns `{"ok": true}` | backend (foundation) | `backend/tests/test_healthz.py::test_healthz_returns_ok_true` | 2026-06-10 |
| `POST /applications` with a valid payload persists an Application row and sends 2 stubbed emails (parent + admin) | public_site / backend | `backend/tests/test_applications.py::test_valid_application_creates_row_and_sends_two_emails` | 2026-06-11 |
| `POST /applications` with a missing required field returns 422 and writes nothing | public_site / backend | `backend/tests/test_applications.py::test_missing_required_field_returns_422_and_writes_nothing` | 2026-06-11 |
| `POST /applications` with an invalid email returns 422 and writes nothing | public_site / backend | `backend/tests/test_applications.py::test_invalid_email_returns_422` | 2026-06-11 |
| `POST /auth/register` with a valid payload creates a User with role=student, status=pending, and an argon2 password hash | auth / backend | `backend/tests/test_auth.py::test_valid_register_creates_pending_student` | 2026-06-11 |
| `POST /auth/register` with a duplicate email returns 409 and leaves exactly one row | auth / backend | `backend/tests/test_auth.py::test_duplicate_email_returns_409` | 2026-06-11 |
| `POST /auth/register` with a password shorter than 8 characters returns 422 and writes nothing | auth / backend | `backend/tests/test_auth.py::test_short_password_returns_422` | 2026-06-11 |
| `POST /auth/register` with an invalid email returns 422 and writes nothing | auth / backend | `backend/tests/test_auth.py::test_invalid_email_returns_422` | 2026-06-11 |
| `POST /auth/login` with the correct password for an active user sets httpOnly access + refresh cookies that decode to that user | auth / backend | `backend/tests/test_auth_login.py::test_login_with_correct_password_sets_cookies_and_returns_user` | 2026-06-11 |
| `POST /auth/login` with the wrong password returns 401 with a generic "Invalid email or password." | auth / backend | `backend/tests/test_auth_login.py::test_login_with_wrong_password_returns_generic_401` | 2026-06-11 |
| `POST /auth/login` for an unknown email returns the **same** generic 401 (no enumeration leak) | auth / backend | `backend/tests/test_auth_login.py::test_login_with_unknown_email_returns_same_generic_401` | 2026-06-11 |
| `POST /auth/login` for a pending account returns the **same** generic 401 (no status leak) | auth / backend | `backend/tests/test_auth_login.py::test_login_for_pending_user_returns_same_generic_401` | 2026-06-11 |
| `POST /auth/refresh` with a valid refresh cookie rotates both access and refresh tokens | auth / backend | `backend/tests/test_auth_login.py::test_refresh_with_valid_refresh_cookie_rotates_both_tokens` | 2026-06-11 |
| `POST /auth/refresh` without a refresh cookie returns 401 | auth / backend | `backend/tests/test_auth_login.py::test_refresh_without_any_cookie_returns_401` | 2026-06-11 |
| `POST /auth/logout` clears both cookies and subsequent `/auth/refresh` returns 401 | auth / backend | `backend/tests/test_auth_login.py::test_logout_returns_200_and_clears_cookies` | 2026-06-11 |
| `POST /auth/forgot-password` for a known email sends one reset email and creates one unconsumed token row | auth / backend | `backend/tests/test_auth_reset.py::test_forgot_password_for_known_email_sends_email_and_creates_token` | 2026-06-11 |
| `POST /auth/forgot-password` for an unknown email returns a **byte-identical** response (no enumeration leak) | auth / backend | `backend/tests/test_auth_reset.py::test_forgot_password_for_unknown_email_returns_identical_response` | 2026-06-11 |
| `POST /auth/reset-password` with a valid token updates the user's password (verifies new, rejects old) and consumes the token | auth / backend | `backend/tests/test_auth_reset.py::test_reset_with_valid_token_changes_password_and_consumes_token` | 2026-06-11 |
| `POST /auth/reset-password` with an already-consumed token returns a generic 400 | auth / backend | `backend/tests/test_auth_reset.py::test_reset_with_consumed_token_returns_generic_400` | 2026-06-11 |
| `POST /auth/reset-password` with an expired token returns the same generic 400 | auth / backend | `backend/tests/test_auth_reset.py::test_reset_with_expired_token_returns_generic_400` | 2026-06-11 |
| `POST /auth/reset-password` with an unknown token returns the same generic 400 | auth / backend | `backend/tests/test_auth_reset.py::test_reset_with_unknown_token_returns_generic_400` | 2026-06-11 |
| `GET /admin/ping` without a session returns 401 generic | auth / backend | `backend/tests/test_rbac.py::test_admin_ping_unauthenticated_returns_401` | 2026-06-11 |
| `GET /admin/ping` as a student returns 403 generic (wrong role) | auth / backend | `backend/tests/test_rbac.py::test_admin_ping_with_student_returns_403` | 2026-06-11 |
| `GET /admin/ping` as an admin returns 200 with the admin's email | auth / backend | `backend/tests/test_rbac.py::test_admin_ping_with_admin_returns_200` | 2026-06-11 |
| `GET /users/{user_id}` without a session returns 401 | auth / backend | `backend/tests/test_rbac.py::test_user_lookup_unauthenticated_returns_401` | 2026-06-11 |
| `GET /users/{own_id}` as the owner returns the own UserResponse | auth / backend | `backend/tests/test_rbac.py::test_user_lookup_with_own_id_returns_own_profile` | 2026-06-11 |
| `GET /users/{other_id}` as a non-owner returns 403 generic | auth / backend | `backend/tests/test_rbac.py::test_user_lookup_with_other_users_id_returns_403` | 2026-06-11 |
| `GET /me` without a session returns 401 | auth / backend | `backend/tests/test_rbac.py::test_me_unauthenticated_returns_401` | 2026-06-11 |
| `GET /me` with a valid session returns the current user | auth / backend | `backend/tests/test_rbac.py::test_me_with_session_returns_current_user` | 2026-06-11 |
| `POST /payments/initialize` without a session returns 401 | enrolment / backend | `backend/tests/test_payments.py::test_initialize_without_session_returns_401` | 2026-06-11 |
| `POST /payments/initialize` for fees creates a pending Payment with the server-side amount (₦125,000) | enrolment / backend | `backend/tests/test_payments.py::test_initialize_fees_creates_pending_payment_with_canonical_amount` | 2026-06-11 |
| `POST /payments/initialize` for a programme uses the programme's price (bece-prep ₦20,000) | enrolment / backend | `backend/tests/test_payments.py::test_initialize_programme_uses_programme_price` | 2026-06-11 |
| `POST /payments/initialize` programme without target → 422 | enrolment / backend | `backend/tests/test_payments.py::test_initialize_programme_without_target_returns_422` | 2026-06-11 |
| `POST /payments/initialize` with an unknown programme slug → 422, no row | enrolment / backend | `backend/tests/test_payments.py::test_initialize_programme_with_unknown_target_returns_422` | 2026-06-11 |
| `POST /payments/initialize` ignores a client-supplied `amount_kobo` (anti-tamper) | enrolment / backend | `backend/tests/test_payments.py::test_initialize_ignores_client_supplied_amount` | 2026-06-11 |
| `POST /payments/verify` with an unknown reference → 404 | enrolment / backend | `backend/tests/test_payments.py::test_verify_unknown_reference_returns_404` | 2026-06-11 |
| `POST /payments/verify` with a Paystack-success + matching amount marks the Payment success and stores raw response | enrolment / backend | `backend/tests/test_payments.py::test_verify_with_paystack_success_marks_payment_success` | 2026-06-11 |
| `POST /payments/verify` with an amount-mismatch marks the Payment failed | enrolment / backend | `backend/tests/test_payments.py::test_verify_with_amount_mismatch_marks_payment_failed` | 2026-06-11 |
| `POST /payments/verify` on an already-success row is idempotent and does NOT re-contact Paystack | enrolment / backend | `backend/tests/test_payments.py::test_verify_is_idempotent_on_already_success` | 2026-06-11 |

---

## How to add a row

1. Build the feature behind a checkpoint (see [HARDENING_RULES.md](HARDENING_RULES.md)).
2. Write a test that fails without the feature and passes with it.
3. Run the full test suite — everything must still pass.
4. Add the row to the table above, including the exact test path.
5. Commit with message `docs(what-works): confirm <feature>`.

## How to remove a row

If a test for a listed feature is failing, deleted, skipped, or no longer
runs in CI, the row is removed in the same commit that introduced the
regression. No "we'll fix it later" entries.
