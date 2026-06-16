---
name: writing-quality-tests
description: Guide for writing robust, high-signal automated tests. Use when asking "How do I test this effectively?", fixing flaky tests, refactoring test suites, or deciding between unit/integration/E2E strategies. Covers pytest best practices and async testing patterns. distinct from TDD (process); this skill focuses on test quality and architecture.
license: Complete terms in LICENSE.txt
metadata:
  author: eder
  version: "1.1"
---

# Writing Quality Tests

## Overview

High-signal tests prove behavior, not implementation. While TDD focuses on the *process* of writing tests first, this skill focuses on the *artifact*—making tests stable, explicit, and valuable long-term.

**Core rule:** If a test is nondeterministic or tied to internals, it is debt. Fix it.

## When to Use

- **New features**: "I need to add tests for this new API endpoint/component."
- **Bug fixes**: "Help me write a regression test for this bug before fixing it."
- **Flaky tests**: "This test fails randomly on CI. How do I make it deterministic?"
- **Refactoring**: "I want to refactor this legacy code but the tests are brittle. How do I improve them first?"
- **Slow tests**: "The test suite takes too long. How can I speed it up or mock dependencies effectively?"
- **Test Design**: "Should I use a unit test or integration test for this logic?"
- **Review**: "Check these tests for maintainability, coverage, and clarity."
- Not for manual exploratory testing or load/perf-only work.

## Non-Negotiables

- Deterministic: same input -> same result; no hidden time/network randomness
- Behavioral oracles: assertions map to business behavior or contracts, never incidental internals
- Minimal coupling: tests fail for product changes, not helper refactors
- Focused scope: one behavior per test; isolated fixtures; clear names
- Fast feedback: prefer fast layers; cache expensive setup; parallelize safely

## Workflow

0) Prove it fails: capture the regression input or wished-for case and watch the test fail first (or reproduce the bug) before code changes.
1) Clarify behavior: preconditions, action, postconditions, invariants. Capture regression input if fixing a bug.
2) Pick level: unit for pure logic; contract for external calls; integration for seams; E2E only to prove flows or contracts end-to-end.
3) Design oracle: assert outputs, state, events, and invariants; avoid implementation details or transient UI.
4) Shape fixtures: use builders/factories; avoid globals; randomize with seeds only when helpful and log the seed.
5) Write the test: AAA (arrange-act-assert) or GWT; table-driven for variants; property-based for algebraic invariants.
6) Validate: run focused test first, then suite. If flaky, hunt nondeterminism (time, randomness, order, network) and remove it.
7) Document intent: name states behavior; failure message points to the expected contract.

## Patterns to Prefer

- Boundary and mutation pairs: min/max/empty/null plus one mutated variation to prove invariants.
- Table-driven cases: enumerate input/output pairs to avoid duplicate tests and improve diffability.
- Property-based checks: algebraic properties (idempotence, reversibility, ordering), round-trips, monotonic counters.
- Contracts at seams: mock at boundaries you own; for third-party calls, pin to contract tests or recorded fixtures.
- Guarded goldens: only for complex structured output; require explicit review of golden updates.

## Coverage Strategy

- Coverage is opt-in: never run coverage unless explicitly requested by the user in the current session (e.g., "improve coverage on file X to Y%"). PM/teammate/CI pressure does not override this rule.
- Pyramid discipline: many unit tests, fewer integration, very few E2E. Use E2E to prove cross-service flow or UI contract.
- Change-based coverage: every test should fail without the code change and pass with it; capture the regression input/output.
- Critical paths first: auth, billing, migrations, data loss, irreversible actions. Add invariants that must never be violated.
- Data and time: cover time zones, DST, leap years, ordering, pagination, idempotency, and retry semantics.
- Observability: log seeds for randomized tests; emit diagnostics on failure (inputs, seed, environment versions).

**Example (explicit coverage request):** User: "improve coverage on file X to 80%". Run targeted coverage for that file only, add behavior-driven tests to hit missing branches, and avoid coverage runs outside that request.

```bash
pytest --cov=path/to/file.py --cov-report=term-missing
```

## Pytest Best Practices

### Fixtures

Use `conftest.py` for shared fixtures; keep test-local fixtures inside the test file. Match scope to lifetime:

- `scope="function"` (default): fresh per test — use for anything mutable
- `scope="module"`: shared across a file — use for read-only resources
- `scope="session"`: shared across the entire run — use for expensive one-time setup (DB migrations, compiled assets)

```python
# conftest.py
@pytest.fixture
def user(db):  # function-scoped: fresh per test
    return UserFactory.create()

@pytest.fixture(scope="session")
def engine():  # session-scoped: one DB engine for all tests
    return create_engine(TEST_DATABASE_URL)
```

Factory fixtures return a callable so callers control parameters without coupling to defaults:

```python
@pytest.fixture
def make_order():
    def _make(status="pending", total=100):
        return Order(status=status, total=total)
    return _make

def test_cancels_pending(make_order):
    order = make_order(status="pending")
    order.cancel()
    assert order.status == "cancelled"
```

### Parametrize

Use `@pytest.mark.parametrize` for table-driven cases. Name the parameters; the test ID is auto-generated.

```python
@pytest.mark.parametrize("amount,expected", [
    (0, Decimal("0.00")),
    (1, Decimal("0.01")),
    (999_99, Decimal("999.99")),
])
def test_format_currency(amount, expected):
    assert format_currency(amount) == expected
```

Stack `parametrize` decorators for a cartesian product. Use `pytest.param(..., id="label")` to give human-readable IDs to non-obvious cases.

### Built-in Fixtures to Prefer

- `tmp_path` (not `tmpdir`): returns a `pathlib.Path`; isolated per test; cleaned up automatically
- `monkeypatch`: patch env vars, attributes, dict entries, and `os.environ` without teardown boilerplate; prefer over `mock.patch` for simple attribute/env swaps
- `caplog`: assert log records by level and message; set `caplog.set_level(logging.WARNING)` at test scope
- `capsys` / `capfd`: capture stdout/stderr when testing CLI output
- `freezegun` or `time-machine`: inject a frozen clock; never call `datetime.now()` directly in production code that you want to test

```python
def test_expires_at_midnight(freezer):  # pytest-freezegun
    freezer.move_to("2024-01-01 23:59:59")
    token = Token.create()
    freezer.tick(delta=timedelta(seconds=2))
    assert token.is_expired()
```

### Exception Assertions

Always use `pytest.raises` as a context manager; always assert on the message with `match=`:

```python
def test_rejects_negative_amount():
    with pytest.raises(ValueError, match="amount must be positive"):
        charge(-1)
```

Never catch exceptions in the test body to assert on them — that lets unexpected exception types pass silently.

### Float Comparisons

Use `pytest.approx` instead of manual tolerances:

```python
assert result == pytest.approx(3.14159, rel=1e-4)
assert results == pytest.approx([1.0, 2.0, 3.0])  # works on sequences
```

### Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q --tb=short"
markers = [
    "slow: marks tests as slow (>1s)",
    "integration: cross-component with real wiring",
    "unit: isolated logic with mocked deps",
]
```

Always declare custom marks to avoid `PytestUnknownMarkWarning`.

## Async Testing

### Setup: `pytest-asyncio`

Install `pytest-asyncio` and enable auto mode so every `async def test_*` is collected without explicit decoration:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

With auto mode, async test functions and async fixtures are handled transparently. Without it, every async test needs `@pytest.mark.asyncio`.

### Async Fixtures

Async fixtures work the same way as sync ones — just use `async def`. Scope rules are identical:

```python
@pytest.fixture
async def client(app):  # function-scoped async fixture
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(scope="session")
async def db_pool():  # session-scoped — one pool for all tests
    pool = await asyncpg.create_pool(TEST_DSN)
    yield pool
    await pool.close()
```

Never mix a session-scoped async fixture with a function-scoped event loop (the default). Either use `asyncio_mode = "auto"` with a session-scoped `event_loop_policy` fixture, or keep session fixtures sync.

### Mocking Async Code

Use `unittest.mock.AsyncMock` for coroutines; `MagicMock` silently passes `await` calls without raising, masking missing awaits.

```python
from unittest.mock import AsyncMock, patch

async def test_notifies_on_payment():
    notifier = AsyncMock()
    payment = Payment(notifier=notifier)
    await payment.complete()
    notifier.send.assert_awaited_once_with(subject="Payment confirmed")
```

`assert_awaited_once_with` is distinct from `assert_called_once_with` — use the `awaited` variants for coroutines so missing `await` in production code is caught.

### Testing Async Context Managers and Generators

```python
async def test_async_context_manager():
    async with connect(TEST_DSN) as conn:
        result = await conn.fetch("SELECT 1")
    assert result[0][0] == 1

async def test_async_generator():
    chunks = []
    async for chunk in stream_response(url):
        chunks.append(chunk)
    assert b"".join(chunks) == expected_body
```

### Timeouts

Wrap operations that should complete quickly with `asyncio.wait_for` so a hung test fails fast instead of blocking CI:

```python
async def test_responds_within_deadline():
    result = await asyncio.wait_for(slow_query(), timeout=2.0)
    assert result is not None
```

For pytest-anyio / anyio-based tests, use `anyio.fail_after`:

```python
async def test_responds_within_deadline():
    with anyio.fail_after(2):
        result = await slow_query()
```

### Backend-Agnostic Tests with `anyio`

If the codebase must support both asyncio and Trio, use `anyio` and `pytest-anyio` instead of `pytest-asyncio`:

```python
import pytest
import anyio

@pytest.mark.anyio
async def test_runs_on_both_backends():
    await anyio.sleep(0)
    assert True
```

Configure backends in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
anyio_backends = ["asyncio", "trio"]
```

### Do Not

- Do not call `asyncio.run()` inside tests — it creates a new event loop and breaks fixture wiring
- Do not wrap async tests in `asyncio.get_event_loop().run_until_complete(...)` — same problem
- Do not use `MagicMock` where `AsyncMock` is required
- Do not share mutable state between coroutines without explicit locks; flakiness from concurrent fixture teardown is common

## Flake Prevention

- Remove time races: replace sleeps with waits on explicit conditions; freeze or inject clocks.
- Isolate state: fresh fixtures per test; unique temp dirs/ports; clean databases; no shared singletons.
- Control randomness: seed RNG, capture seed in failure output, prefer deterministic builders.
- Network and IO: stub external calls; if unavoidable, record/replay; set tight timeouts and retries with jitter disabled in tests.
- Parallel safety: ensure fixtures are parallel-safe or mark tests serial; avoid global mutable state.
- Async teardown: always `yield` in async fixtures (not `return`) so teardown is guaranteed; missing `await` in teardown silently swallows cleanup errors.

## Review Checklist

- Name states behavior and level (e.g., "adds item to cart (integration)").
- Single reason to fail; assertions map to user-visible behavior or contract.
- Fixtures minimal and local; builders hide irrelevant details; no shared hidden state.
- Negative and edge cases present; regression case for the original bug captured.
- Tests run quickly; slow/expensive flows justified and focused.
- Async tests use `AsyncMock` (not `MagicMock`) for coroutines and assert with `assert_awaited_*`.
- No `asyncio.run()` inside test bodies; no `time.sleep()` inside async tests.

## Hygiene (adaptable patterns)

- Structure: Given–When–Then or AAA so intent is obvious.
- Hypothesis: fix generators or code instead of suppressing health checks; log seeds for repro.
- Async correctness: use real async paths/fakes; don’t hide missing awaits with sync doubles; use `AsyncMock`.
- Assertion scope: assert behavior/contract fields; avoid brittle full-payload snapshots unless testing a contract.
- Coverage as health, not blocker: focus on low-coverage behavior-heavy files; be pragmatic with legacy or infra-heavy areas.

### Marks (for selective runs)

Register all marks in `pyproject.toml` to avoid warnings.

- `unit`: isolated logic with external deps mocked
- `integration` / `contract`: cross-component seams with real wiring or adapters
- `async`: true async paths; avoid sync fakes masking awaits
- `property`: Hypothesis-based invariants in dedicated property files
- `slow`: >1s or real infra; justify and keep focused

## Common Anti-Patterns

- Brittle UI or text snapshots without intent; prefer semantic assertions or scoped snapshots.
- Over-mocking internals; mocking within the module under test; asserting call order that is not part of the contract.
- Sleep-based waits; reliance on wall-clock time; unseeded randomness.
- Combined scenarios covering multiple behaviors in one test; global fixtures that hide setup.
- Golden files updated blindly; tests that assert logging implementation rather than outcomes.
- Running coverage by default instead of waiting for explicit coverage requests.
- Using `MagicMock` for async dependencies — it silently passes `await` without executing the coroutine.
- Calling `asyncio.run()` inside tests — breaks event loop / fixture wiring.
- Session-scoped async fixtures with a function-scoped event loop — causes "Future attached to a different loop" errors.

## Red Flags - Stop and Fix

- Tests pass or fail intermittently
- Assertions tied to private methods or call order instead of observable behavior
- Unseeded randomness, sleeps instead of explicit waits, or shared mutable fixtures
- Golden updates accepted without review of intent
- A test never failed before the code change
- Running coverage without the user explicitly asking
- Running coverage due to PM/teammate/CI pressure
- `MagicMock` used where `AsyncMock` is required
- `asyncio.run()` called inside a test function
- Async fixture using `return` instead of `yield` (teardown won’t run)
