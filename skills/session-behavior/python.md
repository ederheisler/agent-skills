---
name: python-session-behavior
description: >-
  Python-specific behavioral contract. Loaded on top of the base session-behavior contract when working in a Python codebase. Adds toolchain defaults, Python push-back triggers, async rules, and testing defaults.
metadata:
  type: extension
  extends: session-behavior
  version: "2.0"
---

# Python Session Behavior

All base rules from `session-behavior` still apply. What follows is Python-specific on top of that.

---

## Toolchain Defaults

**Package management:** use `uv` if available, otherwise `pip`. Never suggest `conda` or `pipenv` unless the project already uses them. Check with `which uv` before recommending.

**Virtual environments:** never install into the system Python. If there's no active venv, say so before running `pip install`. Don't silently add `--break-system-packages`.

**Test runner:** `pytest` only. Don't write `unittest.TestCase` subclasses in new code. If touching a file that uses `unittest`, leave it — don't rewrite tests that aren't broken.

**Formatter/linter:** `ruff` for both. If the project uses `black` + `flake8`, leave it. Only suggest a toolchain migration if the user asks.

---

## Push-Back Triggers

Push back (one objection, then do what the user decides) when you see:

**Bare `except:`**
```python
try:
    result = fetch()
except:
    pass
```
Swallows `KeyboardInterrupt`, `SystemExit`, and every unexpected error. Minimum: `except Exception:`. Better: name the specific exception.

**Mutable default arguments**
```python
def add_item(item, items=[]):
    items.append(item)
```
The list is shared across all calls. Use `None` and assign inside the function.

**Sync DB/HTTP calls in an async function**
```python
async def get_user(user_id: int):
    return db.query(User).filter(User.id == user_id).first()  # blocks the event loop
```
Blocks the event loop. Use `await` with an async ORM/driver, or run in a thread with `asyncio.to_thread`.

**Old-style type hints in new code** — `from typing import List, Dict, Optional, Tuple` in new files or new functions. Use built-in generics instead (PEP 585): `list[str]`, `dict[str, int]`, `str | None`. Don't rewrite existing annotations you're not touching.

**`TYPE_CHECKING` guards** — a code smell, not a tool. They paper over circular imports; fix the architecture instead. Flag them on new code and on files being significantly refactored.

**Late imports** (inside functions or classes) — same root cause as `TYPE_CHECKING`: circular dependencies that signal poor architecture. The only exception is an intentional lazy-load for startup performance, which should be commented.

**`# type: ignore` without explanation** — acceptable as a last resort, but must include a comment saying why:
```python
result = lib.func()  # type: ignore  # library stub is wrong, fixed upstream in v2
```
If you're adding more than one or two in a session, something structural is wrong — flag it.

**Business logic in routers**
```python
@router.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    item = db.query(Item).filter(Item.id == item_id).first()
    ...
```
Routers delegate; services decide. Validation, DB queries, and domain rules belong in the service layer. Services raise `HTTPException` directly — let them bubble up through the router.

**Naive or deprecated datetime usage** — two rules, no exceptions:
- Never `datetime.utcnow()` — it returns a naive datetime with no tzinfo, silently wrong when compared to aware datetimes. Use `datetime.now(datetime.UTC)` instead.
- Never `timezone.utc` — use the `datetime.UTC` alias (Python 3.11+). If the project targets < 3.11, use `timezone.utc` and add a comment, but flag the version constraint.

```python
# BAD
datetime.utcnow()
datetime.now(timezone.utc)

# GOOD
datetime.now(datetime.UTC)
```

**`os.path` for new path code** — `pathlib.Path` is the modern replacement. Push back if the file is new or being significantly refactored. Don't rewrite existing `os.path` calls you aren't touching.

**`print()` for logging in server/service code** — use the `logging` module. `print()` is fine in scripts, CLIs, and notebooks.

**Global mutable state** — module-level dicts/lists mutated at runtime are concurrency bugs waiting to happen. Push back and suggest a dependency-injected or context-local alternative.

---

## Async Rules

Apply these without being asked when the project uses `async`/`await`:

- All DB calls, HTTP calls, and file I/O must be awaited
- Don't mix `asyncio.run()` calls inside coroutines
- Don't use `time.sleep()` inside async functions — use `await asyncio.sleep()`
- `async def` functions that don't `await` anything should be `def` — flag it

Before writing a new async function: does the caller chain actually support async? Introducing `async def` at one layer requires auditing the whole call stack.

---

## Testing Defaults

- New tests: plain `pytest` functions, `assert` statements, no `self`
- Fixtures over setup/teardown methods
- Don't mock the database for integration tests — a test that mocks DB internals proves nothing about real queries
- One assertion per test is a guideline, not a law — use judgment
- If you write a function, write a test for it in the same PR unless the user explicitly opts out

---

## What NOT to Push Back On

- Code inside `tests/` — style rules are relaxed there
- Old-style type hints (`List`, `Dict`) in files you're not touching
- `os.path` calls in files you're not touching
- `# type: ignore` with a comment explaining why — that's the right pattern
- The user's choice of sync vs async if the codebase is already committed to one
