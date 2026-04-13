---
title: "Context Managers <-> Test Fixtures"
tags: [python, testing]
category: "python"
sources:
  - "daily/example-2026-01-15.md"
created: 2026-01-15
---

# Context Managers <-> Test Fixtures

**Context:** Writing tests that need setup/teardown — database connections, temporary files, mock servers.

**Problem:** Test fixtures (pytest's `yield` fixtures) and context managers solve the same fundamental problem: "do something before, guarantee cleanup after." Developers often write verbose setUp/tearDown methods when a context manager would be cleaner.

**Lesson:** Pytest `yield` fixtures ARE context managers in disguise. If you already have a context manager for production code, you can reuse it directly as a test fixture — no duplication needed.

## The Connection

Both patterns follow the same structure:
1. **Setup** — acquire resource
2. **Yield/use** — hand control to caller
3. **Teardown** — guaranteed cleanup

```python
# Production context manager
@contextmanager
def db_session():
    session = Session()
    yield session
    session.close()

# Test fixture — reuses the same pattern
@pytest.fixture
def session():
    with db_session() as s:
        yield s
    # cleanup happens automatically
```

## Implications

- Don't duplicate setup/teardown logic between production and test code
- If your test fixture is complex, consider extracting a context manager that both production and tests can use
- `contextlib.ExitStack` handles dynamic numbers of context managers — useful for parameterized tests

## Related Concepts

- [[concepts/example-python-context-managers]]
