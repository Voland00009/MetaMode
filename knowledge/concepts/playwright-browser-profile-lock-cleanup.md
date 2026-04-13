---
title: "Playwright browser_profile Lock Files After Crash"
aliases: [browser profile lock, SingletonLock, TargetClosedError, persistent context crash]
tags: [playwright, debugging, devtools]
category: "devtools"
sources:
  - "plans/next-session-notebooklm-login-fix.md"
created: 2026-04-13
updated: 2026-04-13
---

# Playwright browser_profile Lock Files After Crash

**Context:** When using `launch_persistent_context()` with a `user_data_dir` (browser profile) and the previous Chromium process crashed, was killed, or didn't close cleanly.

**Problem:** Chromium writes lock files (`SingletonLock`, `*.lock`) into the browser profile directory on launch. If the process exits abnormally, these files remain. The next `launch_persistent_context()` call either hangs waiting for the lock, or fails with `TargetClosedError` / `BrowserClosedError`. No helpful error message explains the root cause.

**Lesson:** Before calling `launch_persistent_context()`, kill stale Chromium processes and remove lock files from the profile directory. This is especially important for automated/headless scripts that may be interrupted.

## Key Points

- Chromium's `SingletonLock` and `*.lock` files in `user_data_dir` prevent concurrent access to the same profile
- If the previous browser process crashed or was force-killed, lock files remain orphaned
- `launch_persistent_context()` with a locked profile either hangs indefinitely or throws a cryptic error
- Fix: kill stale Chromium processes + remove lock files before launch
- On Windows, use `taskkill /F /IM chromium.exe`; on Unix, `pkill -f chromium` or check for the specific Playwright binary

## Details

Playwright's `launch_persistent_context()` launches a full Chromium instance with a persistent user data directory — the same mechanism Chrome uses for user profiles. Chromium enforces single-instance access to a profile via `SingletonLock` (a file or symlink created on startup, removed on clean shutdown).

When the process exits abnormally — OOM kill, `taskkill`, power loss, or a crash in the page being automated — the lock file is not cleaned up. On the next launch attempt, Chromium sees the stale lock and either:
1. Waits indefinitely for the "other instance" to release it
2. Fails immediately with `TargetClosedError` (Playwright wraps the launch failure)

The fix is a pre-launch cleanup routine:

```python
import subprocess
from pathlib import Path

PROFILE_PATH = Path.home() / ".myapp" / "browser_profile"

# Kill stale Playwright Chromium processes
try:
    subprocess.run(["taskkill", "/F", "/IM", "chromium.exe"],
                   capture_output=True, timeout=5)
except Exception:
    pass  # No stale processes — fine

# Remove lock files
for lock in PROFILE_PATH.glob("*.lock"):
    try:
        lock.unlink()
    except OSError:
        pass
singleton = PROFILE_PATH / "SingletonLock"
if singleton.exists():
    try:
        singleton.unlink()
    except OSError:
        pass
```

The `try/except OSError` around each `unlink()` handles the edge case where a file is locked by another process. The `taskkill` call is wrapped because it fails (non-zero exit) when no matching process exists — this is the normal case and should be silently ignored.

For extreme cases where the entire profile is corrupted (not just locked), deleting the whole `browser_profile` directory and re-authenticating is the nuclear option. This loses the saved session but guarantees a clean state.

## Related Concepts

- [[concepts/python-path-tmp-windows-mismatch]] - Discovered together in the same NotebookLM login script
- [[concepts/python-stdout-buffering-file-redirect]] - Compounded the debugging difficulty: lock hang + empty log = no visibility
- [[connections/windows-shell-boundary-failures]] - Another Windows-specific automation failure mode
