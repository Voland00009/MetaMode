# Python asyncio Common Pitfalls

## Context
Working with async Python code in web frameworks (FastAPI, aiohttp) and running into subtle bugs that don't raise obvious errors.

## Key Insight
Three most common asyncio mistakes:
1. **Forgetting `await`** — returns a coroutine object instead of the result. No error, just wrong type flowing through your code silently.
2. **Blocking the event loop** — calling `time.sleep()`, `requests.get()`, or CPU-heavy code inside an async function freezes ALL concurrent tasks. Use `asyncio.sleep()`, `httpx.AsyncClient`, or `asyncio.to_thread()`.
3. **Fire-and-forget tasks** — `asyncio.create_task()` without storing the reference lets the task get garbage collected. Always keep a reference or use a task group.

## Example
```python
# Bug: forgot await — result is a coroutine object, not data
async def get_user(id):
    return await db.fetch_one(query, id)

user = get_user(1)        # Missing await! user is a coroutine
print(user.name)           # AttributeError: coroutine has no attribute 'name'

# Fix:
user = await get_user(1)   # Now user is the actual data

# Bug: blocking the event loop
async def handler():
    time.sleep(5)           # Blocks EVERYTHING for 5 seconds
    await asyncio.sleep(5)  # Correct — yields control to other tasks
```
