---
title: "Asyncio Fire-and-Forget Task Garbage Collection"
aliases: [fire and forget, create_task gc, untracked tasks, task reference]
tags: [python, debugging, architecture]
category: "python"
sources:
  - "raw/example-article.md"
created: 2026-04-13
updated: 2026-04-13
---

# Asyncio Fire-and-Forget Task Garbage Collection

**Context:** When spawning background tasks in asyncio applications — sending emails, logging analytics, updating caches — where you don't need to wait for the result.

**Problem:** `asyncio.create_task()` returns a `Task` object. If you don't store a reference to it, the task can be garbage collected before it completes. Python's GC sees no live references to the task and destroys it — silently cancelling the work.

**Lesson:** Always store a reference to tasks created with `asyncio.create_task()`. Use a set of active tasks, a `TaskGroup` (Python 3.11+), or an explicit collection to keep tasks alive until completion.

## Key Points

- `asyncio.create_task(coro)` schedules a coroutine but the returned `Task` must be kept alive by a reference
- Without a stored reference, the task is eligible for garbage collection — CPython's reference counting may destroy it immediately
- The bug is intermittent: it depends on GC timing, making it hard to reproduce in testing
- Python 3.11+ `TaskGroup` handles lifetime management automatically — prefer it for structured concurrency
- Common pattern: maintain a `background_tasks: set[asyncio.Task]` and use `task.add_done_callback(background_tasks.discard)` for cleanup

## Details

The asyncio event loop holds only a weak reference to tasks. This is a deliberate design choice — it prevents the event loop from accumulating tasks indefinitely. But it means the caller must maintain a strong reference to any task that should complete.

```python
# Bug: task may be garbage collected before completing
async def handle_request(data):
    asyncio.create_task(send_analytics(data))  # No reference stored!
    return {"status": "ok"}

# Fix: store references in a module-level set
background_tasks = set()

async def handle_request(data):
    task = asyncio.create_task(send_analytics(data))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)  # Auto-cleanup when done
    return {"status": "ok"}
```

The garbage collection behavior is particularly treacherous because it's non-deterministic. In CPython, reference counting usually destroys objects immediately when the last reference drops — but the exact timing depends on code structure, local variable lifetimes, and interpreter optimizations. A task might complete successfully in development (where the scope lives long enough) but silently disappear in production under load.

Python 3.11 introduced `TaskGroup`, which provides structured concurrency and automatic lifetime management. Tasks created within a `TaskGroup` context are guaranteed to complete (or be cancelled) before the group exits. For new code, `TaskGroup` is the preferred pattern over manual task set management.

```python
# Python 3.11+ structured concurrency
async def process_batch(items):
    async with asyncio.TaskGroup() as tg:
        for item in items:
            tg.create_task(process_item(item))
    # All tasks guaranteed complete here
```

For web frameworks, FastAPI's `BackgroundTasks` and Starlette's background task system handle the reference management internally — they're the recommended approach for fire-and-forget work in request handlers rather than raw `create_task()`.

## Related Concepts

- [[concepts/asyncio-forgotten-await]] - Another asyncio lifetime bug: coroutines that never execute vs tasks that get destroyed
- [[concepts/asyncio-blocking-event-loop]] - Third major asyncio pitfall: blocking calls freezing all concurrent work
- [[concepts/python-duck-typing-silent-failures]] - Same pattern: Python fails silently rather than raising an obvious error
