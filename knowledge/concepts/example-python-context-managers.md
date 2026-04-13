---
title: "Python Context Managers for Resource Cleanup"
aliases: [context-managers, with-statement]
tags: [python, design-patterns]
category: "python"
sources:
  - "daily/example-2026-01-15.md"
created: 2026-01-15
updated: 2026-01-15
---

# Python Context Managers for Resource Cleanup

**Context:** Working with resources that need guaranteed cleanup — database connections, file handles, network sockets, locks.

**Problem:** Manual resource management (`open()` + `close()`) breaks when exceptions occur mid-operation. Forgetting `close()` causes resource leaks. Try/finally blocks work but are verbose and error-prone.

**Lesson:** The `with` statement guarantees cleanup via `__enter__`/`__exit__` protocol. Always prefer it over manual open/close — it handles exceptions, early returns, and nested resources correctly.

## Key Points

- `with` calls `__exit__()` even if an exception occurs inside the block
- Multiple resources: `with open(a) as f1, open(b) as f2:` — both get cleaned up
- `contextlib.contextmanager` decorator turns generators into context managers (less boilerplate than writing a class)
- Database sessions, file handles, locks, and network connections should always use context managers

## Details

```python
# Bad — resource leak on exception
conn = db.connect()
result = conn.execute(query)  # if this throws, conn is never closed
conn.close()

# Good — guaranteed cleanup
with db.connect() as conn:
    result = conn.execute(query)
# conn.close() called automatically, even on exception

# Custom context manager with contextlib
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.time()
    yield
    print(f"{label}: {time.time() - start:.2f}s")

with timer("query"):
    db.execute(slow_query)
```

## Related Concepts

- [[connections/example-context-managers-and-testing]] - Context managers simplify test fixtures
