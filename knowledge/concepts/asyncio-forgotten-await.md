---
title: "Asyncio Forgotten Await: Silent Coroutine Propagation"
aliases: [forgotten await, missing await, coroutine object bug]
tags: [python, debugging, architecture]
category: "python"
sources:
  - "raw/example-article.md"
created: 2026-04-13
updated: 2026-04-13
---

# Asyncio Forgotten Await: Silent Coroutine Propagation

**Context:** When calling async functions in Python web frameworks (FastAPI, aiohttp) or any asyncio-based code.

**Problem:** Calling an async function without `await` returns a coroutine object instead of the actual result. Python does not raise an error — the coroutine object silently flows through downstream code until something tries to use it as the expected type.

**Lesson:** A missing `await` is a silent type error. The coroutine object passes through assignments and function arguments without complaint, only failing when an attribute or method is accessed that coroutines don't have. Always `await` async function calls.

## Key Points

- `user = get_user(1)` on an async function returns a coroutine object, not the user data
- No error at assignment — the bug only surfaces later when `user.name` raises `AttributeError`
- Python 3.12+ emits a `RuntimeWarning: coroutine was never awaited` — but only if the coroutine is garbage collected without being awaited, and only to stderr
- This is the same class of bug as duck typing silent failures: wrong data type flows silently through code
- Linters like `ruff` and `mypy` can catch missing awaits statically — enable `async` rules as a safety net

## Details

When Python encounters a call to an async function without `await`, it creates a coroutine object and returns it immediately. The coroutine object is a valid Python object — it can be assigned to variables, passed to functions, and stored in data structures. Nothing about this operation raises an exception.

```python
async def get_user(id):
    return await db.fetch_one(query, id)

# Bug: user is a coroutine object, not user data
user = get_user(1)
print(type(user))  # <class 'coroutine'>
print(user.name)   # AttributeError: 'coroutine' object has no attribute 'name'
```

The failure mode is particularly insidious in web frameworks. In FastAPI, a forgotten `await` in a route handler might return a coroutine object as the HTTP response body. FastAPI may serialize it as a string representation (`<coroutine object get_user at 0x...>`) rather than raising an error, producing a 200 response with garbage content.

The bug shares its root cause with Python's duck typing silent failures: Python's permissiveness lets structurally wrong data propagate through code without type enforcement at boundaries. A coroutine object is not a User, but Python doesn't check — just as a string is not a list, but Python iterates it anyway.

Modern Python (3.12+) mitigates this slightly with `RuntimeWarning: coroutine 'get_user' was never awaited`, but this warning only fires when the coroutine is garbage collected, not when it's created. If the coroutine is stored in a variable that outlives the current scope, the warning may never appear.

## Related Concepts

- [[concepts/python-duck-typing-silent-failures]] - Same class of bug: wrong type flows silently through Python code without raising exceptions
- [[concepts/asyncio-blocking-event-loop]] - Another common asyncio mistake: using sync calls inside async functions
- [[concepts/asyncio-fire-and-forget-tasks]] - Third major asyncio pitfall: untracked tasks disappearing via garbage collection
