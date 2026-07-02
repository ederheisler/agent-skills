# Async Testing

## Setup: `pytest-asyncio`

Install `pytest-asyncio` and enable auto mode so every `async def test_*` is collected without explicit decoration:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

With auto mode, async test functions and async fixtures are handled transparently. Without it, every async test needs `@pytest.mark.asyncio`.

## Async Fixtures

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

A session-scoped async fixture needs a loop that lives that long, but the default event loop is function-scoped, producing "Future attached to a different loop" errors. Fix it by setting the loop scope explicitly (pytest-asyncio >= 0.23):

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
```

or per-fixture with `@pytest_asyncio.fixture(loop_scope="session")`. If you can't widen the loop scope, keep the fixture sync instead.

## Mocking Async Code

Use `unittest.mock.AsyncMock` for coroutines. `MagicMock` doesn't hide the `await` itself — awaiting a `MagicMock()` result raises `TypeError` immediately. The real danger is the opposite: if the *production* code forgets to `await` a call, a `MagicMock` collaborator won't complain (calling it just returns a `Mock`, no coroutine, no warning), so the missing `await` slips through. `AsyncMock` makes the call return an awaitable, matching the real dependency, and its `assert_awaited_*` methods catch the missing `await` where a plain `assert_called_*` would not.

```python
from unittest.mock import AsyncMock, patch

async def test_notifies_on_payment():
    notifier = AsyncMock()
    payment = Payment(notifier=notifier)
    await payment.complete()
    notifier.send.assert_awaited_once_with(subject="Payment confirmed")
```

## Testing Async Context Managers and Generators

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

## Timeouts

Wrap operations that should complete quickly with `asyncio.wait_for` so a hung test fails fast instead of blocking CI:

```python
async def test_responds_within_deadline():
    result = await asyncio.wait_for(slow_query(), timeout=2.0)
    assert result is not None
```

For `anyio`-based tests, use `anyio.fail_after`:

```python
async def test_responds_within_deadline():
    with anyio.fail_after(2):
        result = await slow_query()
```

## Backend-Agnostic Tests with `anyio`

If the codebase must support both asyncio and Trio, use `anyio` (its pytest plugin ships built in — no separate `pytest-anyio` package) instead of `pytest-asyncio`:

```python
import pytest
import anyio

@pytest.mark.anyio
async def test_runs_on_both_backends():
    await anyio.sleep(0)
    assert True
```

Select backends with the `anyio_backend` fixture (there is no ini-file setting for this):

```python
# conftest.py
import pytest

@pytest.fixture(params=["asyncio", "trio"])
def anyio_backend(request):
    return request.param
```

## Do Not

- Do not call `asyncio.run()` inside tests — it creates a new event loop and breaks fixture wiring
- Do not wrap async tests in `asyncio.get_event_loop().run_until_complete(...)` — same problem
- Do not use `MagicMock` where `AsyncMock` is required
- Do not share mutable state between coroutines without explicit locks; flakiness from concurrent fixture teardown is common
- Do not use `return` in an async fixture that needs teardown — use `yield`, or the cleanup code after it never runs
