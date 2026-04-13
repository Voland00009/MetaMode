---
title: "Python Path('/tmp') vs Bash /tmp on Windows"
aliases: [tmp mismatch, path resolution windows, cross-process temp path]
tags: [python, shell, debugging, devtools]
category: "python"
sources:
  - "raw/python-path-tmp-windows-mismatch.md"
created: 2026-04-13
updated: 2026-04-13
---

# Python Path("/tmp") vs Bash /tmp on Windows

**Context:** When writing scripts that use `/tmp` for inter-process communication between bash and Python on Windows — signal files, lock files, temp data exchange.

**Problem:** On Windows, Python's `Path("/tmp")` resolves to `C:\tmp` (the root of the current drive), while bash's `/tmp` resolves to the MSYS2/Git Bash temp directory (a completely different real path). Files created by bash in `/tmp` are invisible to Python checking `Path("/tmp")`, and vice versa. The mismatch is silent — no errors, just infinite waits or missing data.

**Lesson:** Never use `/tmp` for cross-process communication between bash and Python on Windows. Use `Path.home()` or explicit absolute Windows paths that both environments resolve identically.

## Key Points

- Python `Path("/tmp")` on Windows → `C:\tmp` (drive root); bash `/tmp` → MSYS2 virtual filesystem (e.g., `C:\Users\<user>\AppData\Local\Temp` or MSYS2 internal path)
- The mismatch is completely silent — `Path("/tmp/file").exists()` returns `False` without error, even though bash created the file successfully
- This breaks any inter-process pattern: signal files, lock files, shared temp data, pipe-through-file communication
- Fix: use `Path.home() / ".appname" / "signal"` — `Path.home()` resolves to the same real directory from both bash and Python
- Alternative fix: use explicit Windows paths (`C:/Users/Voland/tmp/signal`) in both bash and Python — ugly but unambiguous

## Details

This bug was discovered during development of a NotebookLM cookie refresh login script. The script used a signal file pattern for inter-process communication: a bash process created a signal file via `touch /tmp/nlm_save_signal`, and a Python process polled for it via `Path("/tmp/nlm_save_signal").exists()`. The Python script waited indefinitely — the file existed from bash's perspective but was invisible to Python.

The root cause is that bash on Windows (Git Bash / MSYS2) maintains a virtual filesystem layer. The `/tmp` path in bash maps through MSYS2's path translation, which routes it to a platform-specific temp directory (typically under `AppData/Local/Temp` or the MSYS2 installation's own `/tmp`). Python, running as a native Windows process, has no awareness of MSYS2's virtual filesystem. When Python sees `Path("/tmp")`, it interprets the forward slash as a drive-relative path and resolves it to `C:\tmp` — a directory that may not even exist.

```python
# Bug: bash and Python see different directories
SIGNAL_FILE = Path("/tmp/nlm_save_signal")

# Fix: Path.home() is consistent across bash and Python
SIGNAL_FILE = Path.home() / ".notebooklm" / "save_signal"
```

```bash
# Bash creates file here:
touch /tmp/signal        # → MSYS2 temp (NOT C:\tmp)

# Python looks here:
Path("/tmp/signal")      # → C:\tmp\signal (different location!)

# Result: Python never finds the file, infinite wait loop
```

This is the same class of boundary mismatch as PATH namespace separation and argument escaping differences — bash on Windows operates in a translated environment that diverges from native Windows path resolution. The divergence is invisible because both environments accept `/tmp` as a valid path without error. Only the resolution differs.

The `Path.home()` fix works because the home directory is one of the few paths that both bash and Python resolve to the same physical location. Bash's `~` and Python's `Path.home()` both point to `C:\Users\<username>`. Building temp paths under home (e.g., `~/.appname/`) ensures cross-process compatibility without hardcoding Windows-specific paths.

For scripts that must use system temp directories, `tempfile.gettempdir()` in Python returns the actual Windows temp path, which can be passed explicitly to bash processes via environment variables or arguments — though this adds complexity compared to the `Path.home()` approach.

## Related Concepts

- [[concepts/gh-cli-bash-path-windows]] - Same root cause: bash on Windows maintains a separate namespace (PATH vs filesystem) from native Windows
- [[concepts/file-based-input-shell-escaping]] - Another cross-shell boundary where bash and Windows disagree on interpretation
- [[connections/windows-shell-boundary-failures]] - This is the 5th member of the Windows shell boundary bug family
- [[concepts/python-duck-typing-silent-failures]] - Same failure pattern: silent wrong results instead of clear errors
