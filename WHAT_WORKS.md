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
