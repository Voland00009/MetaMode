---
title: "Python stdout Buffering When Redirecting to File"
aliases: [flush=True, stdout buffering, print buffering, empty log file]
tags: [python, shell, debugging]
category: "python"
sources:
  - "raw/python-path-tmp-windows-mismatch.md"
created: 2026-04-13
updated: 2026-04-13
---

# Python stdout Buffering When Redirecting to File

**Context:** When running a Python script with stdout redirected to a file (`python script.py > output.txt`) and expecting to monitor the log in real time — tailing the file, checking for progress, or reading partial output from another process.

**Problem:** Python buffers stdout when it detects the output is not a terminal (i.e., redirected to a file or pipe). `print()` calls accumulate in an internal buffer and are only flushed when the buffer fills (~8KB) or the process exits. The log file appears empty or incomplete during execution, even though the script is actively printing.

**Lesson:** Add `flush=True` to every `print()` call in scripts whose output may be redirected, or run Python with `-u` (unbuffered) flag. Without explicit flushing, file-based logs are invisible until the process terminates.

## Key Points

- Python uses line-buffered stdout for terminals (flush after each `\n`) but block-buffered for files/pipes (flush after ~8KB or on exit)
- `print("status", flush=True)` forces immediate write to the output stream — essential for real-time logging
- `python -u script.py > log.txt` disables all stdout/stderr buffering globally — simpler but less granular
- `PYTHONUNBUFFERED=1` environment variable achieves the same as `-u` without modifying the command line
- This is especially dangerous in long-running scripts (daemons, watchers, login scripts) where the process may run for minutes or hours before exiting

## Details

Python's stdout buffering strategy depends on whether the output stream is connected to a terminal (TTY). When writing to a terminal, Python uses line buffering — each `print()` call that ends with a newline flushes immediately, so output appears in real time. When stdout is redirected to a file or pipe, Python switches to block buffering — output accumulates in an internal buffer (typically 8KB) and is written to the file only when the buffer fills or the process exits cleanly.

This behavior is inherited from C's `stdio` library and is designed for performance — writing large blocks to files is faster than writing line by line. But it creates a frustrating experience when debugging: a script that prints progress updates every second appears to produce no output at all when redirected to a file. Tailing the file shows nothing. Only when the process finishes (or crashes) does the accumulated output appear.

```python
# Bug: log file appears empty during execution
print(f"[{time.strftime('%H:%M:%S')}] Waiting for signal...")
# Output sits in buffer, never reaches the file until process exits

# Fix: each print immediately writes to file
print(f"[{time.strftime('%H:%M:%S')}] Waiting for signal...", flush=True)
```

The bug was encountered during NotebookLM login script development, where a Python process ran in the background with stdout redirected to a log file. The script printed status updates while waiting for a signal file, but the log remained empty — making it impossible to diagnose the concurrent `/tmp` path mismatch bug. Two silent failures compounding each other.

Three solutions exist, in order of preference: (1) `flush=True` on individual `print()` calls — most explicit, no side effects; (2) `python -u` flag — disables buffering globally, affects all output including stderr; (3) `PYTHONUNBUFFERED=1` env var — same as `-u` but configured externally. For scripts that will always be redirected, wrapping stdout at startup with `sys.stdout.reconfigure(line_buffering=True)` provides a one-time fix without modifying every print call.

## Related Concepts

- [[concepts/python-path-tmp-windows-mismatch]] - Discovered together: both bugs compounded in the same script, making diagnosis harder
- [[concepts/python-duck-typing-silent-failures]] - Same failure pattern: Python silently does the wrong thing without raising errors
- [[connections/windows-shell-boundary-failures]] - File redirection buffering is another case where shell behavior differs from terminal behavior
