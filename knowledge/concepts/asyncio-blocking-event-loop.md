---
title: "Asyncio Blocking the Event Loop"
aliases: [blocking event loop, sync in async, time.sleep in async]
tags: [python, debugging, architecture]
category: "python"
sources:
  - "raw/example-article.md"
created: 2026-04-13
updated: 2026-04-13
---

# Asyncio Blocking the Event Loop

**Context:** When writing async Python code in web frameworks (FastAPI, aiohttp) or any asyncio-based application that handles concurrent requests or tasks.

**Problem:** Calling synchronous blocking functions (`time.sleep()`, `requests.get()`, CPU-heavy computation) inside an async function freezes the entire event loop. All concurrent tasks — every other request, every other coroutine — stop until the blocking call completes.

**Lesson:** In async code, every blocking call must be replaced with its async equivalent, or offloaded to a thread. `time.sleep()` → `asyncio.sleep()`, `requests.get()` → `httpx.AsyncClient`, CPU work → `asyncio.to_thread()`.

## Key Points

- The asyncio event loop is single-threaded — it can only run one thing at a time, switching between tasks at `await` points
- `time.sleep(5)` inside an async function blocks the thread for 5 seconds — no other task can run during that time
- `requests.get()` blocks on network I/O — use `httpx.AsyncClient` or `aiohttp.ClientSession` instead
- CPU-heavy work blocks the loop just like I/O — use `asyncio.to_thread()` or `concurrent.futures.ProcessPoolExecutor`
- The bug is invisible in single-request testing — it only manifests under concurrent load when other tasks freeze

## Details

Python's asyncio event loop achieves concurrency through cooperative multitasking. Each coroutine runs until it hits an `await` expression, at which point it yields control back to the event loop, which can then run another coroutine. This works beautifully for I/O-bound tasks: while one request waits for a database response, another can process its data.

The system breaks when a coroutine never yields. A `time.sleep(5)` call doesn't contain an `await` — it tells the OS to block the current thread for 5 seconds. Since the event loop runs on that thread, everything stops. A FastAPI server handling 100 concurrent requests will freeze all 100 if any single handler calls `time.sleep()`.

```python
# Bug: blocks the entire event loop for 5 seconds
async def handler():
    time.sleep(5)           # All other requests freeze
    return {"status": "ok"}

# Fix: yields control while waiting
async def handler():
    await asyncio.sleep(5)  # Other requests continue normally
    return {"status": "ok"}
```

The same applies to HTTP calls. `requests.get(url)` blocks on network I/O — potentially for seconds. The async equivalent is `httpx.AsyncClient` or `aiohttp.ClientSession`, which yield control while waiting for the network response.

For CPU-bound work (image processing, JSON serialization of large payloads, cryptographic operations), there is no async equivalent — the CPU genuinely needs to run. The solution is `asyncio.to_thread(cpu_heavy_func, args)`, which runs the function in a separate thread so the event loop stays responsive. For truly CPU-intensive work, `ProcessPoolExecutor` avoids the GIL limitation entirely.

The most dangerous aspect of this bug is that it passes all single-request tests. A handler that blocks for 2 seconds responds correctly — just slowly. The bug only surfaces under concurrent load, when other handlers freeze. Load testing or concurrent integration tests are the only reliable detection method.

## Related Concepts

- [[concepts/asyncio-forgotten-await]] - Another common asyncio mistake: forgetting await produces silent type errors
- [[concepts/asyncio-fire-and-forget-tasks]] - Third major asyncio pitfall: tasks lost to garbage collection
- [[concepts/python-duck-typing-silent-failures]] - Same pattern of Python bugs that manifest silently under specific conditions
