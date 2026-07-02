---
name: writing-quality-tests
description: Use when writing or reviewing automated tests, fixing flaky/nondeterministic tests, refactoring a brittle test suite, or choosing between unit/integration/E2E strategies. Python/pytest and async-specific guidance included. Distinct from TDD (the process of writing tests first); this skill is about test quality and architecture.
metadata:
  author: eder
  version: "1.2"
---

# Writing Quality Tests

## Overview

High-signal tests prove behavior, not implementation. While TDD focuses on the *process* of writing tests first, this skill focuses on the *artifact* — making tests stable, explicit, and valuable long-term.

**Core rule:** If a test is nondeterministic or tied to internals, it is debt. Fix it.

## When to Use

- **New features**: "I need to add tests for this new API endpoint/component."
- **Bug fixes**: "Help me write a regression test for this bug before fixing it."
- **Flaky tests**: "This test fails randomly on CI. How do I make it deterministic?"
- **Refactoring**: "I want to refactor this legacy code but the tests are brittle. How do I improve them first?"
- **Slow tests**: "The test suite takes too long. How can I speed it up or mock dependencies effectively?"
- **Test design**: "Should I use a unit test or integration test for this logic?"
- **Review**: "Check these tests for maintainability, coverage, and clarity."
- Not for manual exploratory testing or load/perf-only work.

## Non-Negotiables

- Deterministic: same input -> same result; no hidden time/network randomness
- Behavioral oracles: assertions map to business behavior or contracts, never incidental internals
- Minimal coupling: tests fail for product changes, not helper refactors
- Focused scope: one behavior per test; isolated fixtures; clear names
- Fast feedback: prefer fast layers; cache expensive setup; parallelize safely

## Workflow

1) Clarify behavior: preconditions, action, postconditions, invariants. If fixing a bug, capture the regression input and watch the test fail against the unfixed code first.
2) Pick level: unit for pure logic; contract for external calls; integration for seams; E2E only to prove flows or contracts end-to-end.
3) Design oracle: assert outputs, state, events, and invariants; avoid implementation details or transient UI.
4) Shape fixtures: use builders/factories; avoid globals; randomize with seeds only when helpful and log the seed.
5) Write the test: AAA (arrange-act-assert) or GWT; table-driven for variants; property-based for algebraic invariants.
6) Validate: run focused test first, then suite. If flaky, hunt nondeterminism (time, randomness, order, network) and remove it.
7) Document intent: name states behavior; failure message points to the expected contract.

## Patterns to Prefer

- Boundary and mutation pairs: min/max/empty/null plus one mutated variation to prove invariants.
- Table-driven cases: enumerate input/output pairs to avoid duplicate tests and improve diffability.
- Property-based checks: algebraic properties (idempotence, reversibility, ordering), round-trips, monotonic counters. Fix the generator or the code when a Hypothesis case fails — don't suppress its health checks — and log the seed for repro.
- Contracts at seams: mock at boundaries you own; for third-party calls, pin to contract tests or recorded fixtures.
- Guarded goldens: only for complex structured output; require explicit review of golden updates, never accept them blindly.

## Coverage Strategy

- **Coverage is opt-in: never run coverage unless the user explicitly requests it in the current session** (e.g., "improve coverage on file X to Y%"). Pressure from a PM, teammate, or CI does not override this.
- Pyramid discipline: many unit tests, fewer integration, very few E2E. Use E2E to prove cross-service flow or UI contract.
- Change-based coverage: every test should fail without the code change and pass with it; capture the regression input/output.
- Critical paths first: auth, billing, migrations, data loss, irreversible actions. Add invariants that must never be violated.
- Data and time: cover time zones, DST, leap years, ordering, pagination, idempotency, and retry semantics.
- Observability: log seeds for randomized tests; emit diagnostics on failure (inputs, seed, environment versions).

When coverage is explicitly requested (e.g., "improve coverage on file X to 80%"), run it scoped to that file only, add behavior-driven tests to hit missing branches, and don't run coverage outside that request:

```bash
pytest --cov=path/to/file.py --cov-report=term-missing
```

## Pytest and Async Reference

For Python projects, load the matching reference file:

- `references/pytest.md` — fixtures and scoping, parametrize, built-in fixtures (`tmp_path`, `monkeypatch`, `caplog`, `time-machine`), exception assertions, `pytest.approx`, marker configuration
- `references/async.md` — `pytest-asyncio` setup, async fixtures and loop scoping, mocking coroutines with `AsyncMock`, testing async context managers/generators, timeouts, `anyio` backend-agnostic tests

## Flake Prevention

- Remove time races: replace sleeps with waits on explicit conditions; freeze or inject clocks.
- Isolate state: fresh fixtures per test; unique temp dirs/ports; clean databases; no shared singletons.
- Control randomness: seed RNG, capture seed in failure output, prefer deterministic builders.
- Network and IO: stub external calls; if unavoidable, record/replay; set tight timeouts and disable retry jitter in tests.
- Parallel safety: ensure fixtures are parallel-safe or mark tests serial; avoid global mutable state.
- Async teardown: always `yield` in async fixtures (not `return`) so teardown is guaranteed; a missing `await` in teardown silently swallows cleanup errors.

## Review Checklist

- Name states behavior and level (e.g., "adds item to cart (integration)").
- Single reason to fail; assertions map to user-visible behavior or contract, not private methods or call order.
- Fixtures minimal and local; builders hide irrelevant details; no shared hidden state.
- Negative and edge cases present; regression case for the original bug captured.
- Tests run quickly; slow/expensive flows justified and focused.
- Async tests use `AsyncMock` (not `MagicMock`) for coroutines and assert with `assert_awaited_*`.
- No `asyncio.run()` inside test bodies; no `time.sleep()` inside async tests; async fixtures use `yield`, not `return`.
- No coverage run unless the user asked for one this session.

## Common Anti-Patterns

- Brittle UI or text snapshots without intent; prefer semantic assertions or scoped snapshots.
- Over-mocking internals; mocking within the module under test; asserting call order that is not part of the contract.
- Sleep-based waits; reliance on wall-clock time; unseeded randomness.
- Combined scenarios covering multiple behaviors in one test; global fixtures that hide setup.
- Golden files updated blindly; tests that assert logging implementation rather than outcomes.
- `MagicMock` for async dependencies — it won't flag a missing `await` in the code under test.
- `asyncio.run()` inside tests — breaks event loop / fixture wiring.
- Session-scoped async fixtures paired with a function-scoped event loop — causes "Future attached to a different loop" errors.
- Running coverage by default, or because of PM/teammate/CI pressure, instead of waiting for an explicit request.

## Red Flags - Stop and Fix

- Tests pass or fail intermittently
- Assertions tied to private methods or call order instead of observable behavior
- Unseeded randomness, sleeps instead of explicit waits, or shared mutable fixtures
- Golden updates accepted without review of intent
- A test never failed before the code change
- About to run coverage without an explicit request this session, for any reason including PM/teammate/CI pressure
- `MagicMock` used where `AsyncMock` is required
- `asyncio.run()` called inside a test function
- Async fixture using `return` instead of `yield` (teardown won't run)
