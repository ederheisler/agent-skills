# Pytest Best Practices

## Fixtures

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

## Parametrize

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

## Built-in Fixtures to Prefer

- `tmp_path` (not `tmpdir`): returns a `pathlib.Path`; isolated per test; cleaned up automatically
- `monkeypatch`: patch env vars, attributes, dict entries, and `os.environ` without teardown boilerplate; prefer over `mock.patch` for simple attribute/env swaps
- `caplog`: assert log records by level and message; set `caplog.set_level(logging.WARNING)` at test scope
- `capsys` / `capfd`: capture stdout/stderr when testing CLI output
- `time-machine`: inject a frozen or traveling clock; never call `datetime.now()` directly in production code that you want to test. Prefer this over `freezegun` — it's faster and actively maintained.

```python
def test_expires_at_midnight(time_machine):
    time_machine.move_to("2024-01-01 23:59:59", tick=False)
    token = Token.create()
    time_machine.shift(timedelta(seconds=2))
    assert token.is_expired()
```

## Exception Assertions

Always use `pytest.raises` as a context manager; always assert on the message with `match=`:

```python
def test_rejects_negative_amount():
    with pytest.raises(ValueError, match="amount must be positive"):
        charge(-1)
```

Never catch exceptions in the test body to assert on them — that lets unexpected exception types pass silently.

## Float Comparisons

Use `pytest.approx` instead of manual tolerances:

```python
assert result == pytest.approx(3.14159, rel=1e-4)
assert results == pytest.approx([1.0, 2.0, 3.0])  # works on sequences
```

## Configuration (`pyproject.toml`)

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

Always declare custom marks (in `markers`, above) to avoid `PytestUnknownMarkWarning`. Suggested marks for selective runs: `unit`, `integration`/`contract`, `property` (Hypothesis-based invariants), `slow`.
