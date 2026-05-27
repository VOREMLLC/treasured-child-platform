# Engineering principles

These eight rules govern every change in this repository. They are not
suggestions. If a change cannot be made within them, the change does not
happen until the rules are revisited explicitly.

---

## 1. Truth over hype
Never claim a feature works, or quote a number (enrolments, completions,
grades, revenue), unless it has been built, tested, and the number comes
from real data. If something is incomplete or unverified, say so plainly.

## 2. One source of truth
Every number has exactly **one** place it is calculated. The dashboard,
the report card, the certificate and the admin view all read from the
same query. If two views disagree, one of them is wrong — never
"reconcile" by averaging or guessing.

## 3. Measure, don't assume
A feature is not "done" because the code compiles. It is done when a
test proves it does the thing it claims to do, end to end, with realistic
inputs. No exceptions for "small" changes.

## 4. One module, one job
Each major capability (public site, auth, courses, learning, assessment,
certificates, dashboard, notifications, data layer) lives in its own
folder with its own README and its own tests. If one module breaks, the
others keep running. No tangled cross-imports.

## 5. Secrets only in `.env`
API keys, database passwords, JWT secrets, Paystack keys, Anthropic
keys — none of these ever appear in source code. They live in `.env`,
which is in `.gitignore`. The only file in git is `.env.example`, which
lists variable **names** and dummy values.

## 6. Build the environment around the model
Before writing any feature code, the supporting environment must exist:
governance files, folder structure, design system, tests. The model
(human or AI) does its best work when the rails are already laid.

## 7. Change one thing at a time; checkpoint first
Every change is preceded by a git checkpoint (a commit). Every change
addresses exactly one concern. If something breaks, we rewind to the
previous checkpoint rather than patch on top. See
[HARDENING_RULES.md](HARDENING_RULES.md) for the exact procedure.

## 8. Small explained steps; real user data is read-only
Each step is small enough to explain in plain language and undo in one
command. Any database, file, or API that contains real user information
(especially about minors) is treated as **read-only** until the user
explicitly grants write permission for a specific operation.

---

## How these rules show up in practice

- A pull request touching two unrelated concerns is split.
- A test that doesn't actually exercise the feature is rejected.
- A dashboard widget showing a number with no test backing it up is removed.
- A `.env` discovered in `git status` is the highest-priority bug.
- A feature claim in [WHAT_WORKS.md](WHAT_WORKS.md) without a passing test is removed.
