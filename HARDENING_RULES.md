# Hardening rules — the daily working procedure

> The point of these rules is simple: **we should never be more than one
> command away from a working version of the project.**

Every change follows the same four-step loop. No shortcuts.

---

## The loop

### 1. Checkpoint first
Before touching anything, save a snapshot of the current working state.

```bash
git status                              # see what's currently changed
git add -A && git commit -m "checkpoint: <what we're about to attempt>"
```

The commit message describes what you are **about** to try, not what you
did. That way, if it goes wrong, the message tells you exactly what to
undo.

### 2. Change one thing
Make exactly one logical change. Examples of one thing:

- Add a single new file.
- Edit a single function.
- Change a single configuration value.

Examples of **not** one thing:

- "Add the login page and the signup page and fix the header."
- "Refactor the courses module while also adding payments."

If a task feels too big to be one thing, split it before starting.

### 3. Test it
Prove the change does what you claimed. The form of proof depends on what changed:

| Change type | How to prove it |
|---|---|
| Frontend page or component | Open it in the browser and confirm the visible behaviour. Add a render test. |
| Backend endpoint | Hit it with `curl` or the test client. Add a pytest case. |
| Logic / calculation | Add a unit test that fails without the change and passes with it. |
| Configuration | Restart the app and confirm the new value is in effect. |

If you cannot describe how to prove it works, you cannot ship it.

### 4. Commit or rewind
**If the change works**, commit it with a clear message:

```bash
git add -A && git commit -m "feat(<module>): <what it now does>"
```

**If the change is broken or you've lost your way**, rewind to the
checkpoint and try a smaller version:

```bash
git reset --hard HEAD        # discard uncommitted changes
# or, to undo the last commit but keep the files for inspection:
git reset --soft HEAD~1
```

---

## Useful safety commands

| Goal | Command |
|---|---|
| See the full history of commits | `git log --oneline` |
| See what changed since the last commit | `git diff` |
| See what files would be committed right now | `git status` |
| Rewind to a specific past commit (destructive) | `git reset --hard <hash>` |
| Look at a past version without changing anything | `git show <hash>` |
| Create a branch to experiment safely | `git checkout -b experiment/<name>` |

---

## What "broken" means

A change is **broken** if any of the following are true:

- The app no longer starts.
- A test that previously passed now fails.
- An endpoint that previously responded now errors.
- A page that previously rendered is blank or throws.
- A real user could not complete a task they could complete before.

Any of these triggers an immediate rewind. Diagnose **after** restoring
the working state, not while the project is broken.

---

## What never goes into a commit

- A real `.env` file or any secret.
- Generated build outputs (`.next/`, `dist/`, `node_modules/`, `__pycache__/`).
- Real user data (names, emails, payment records).
- A "WIP" or "fix later" comment with no follow-up task written down.

These are enforced by [`.gitignore`](.gitignore) and by review.
