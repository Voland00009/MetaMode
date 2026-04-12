---
title: "Python Duck Typing Silent Failures"
aliases: [structural type mismatch, string iteration bug]
tags: [python, debugging, architecture]
category: "python"
sources:
  - "daily/2026-04-11.md"
created: 2026-04-11
updated: 2026-04-11
---

# Python Duck Typing Silent Failures

**Context:** When processing data from external sources (APIs, CLI tools) whose return type can vary at runtime — particularly when iterating over results that might be strings instead of lists.

**Problem:** Python's duck typing allows structurally wrong data to pass type checks silently. Iterating a string yields individual characters, each of which passes `isinstance(block, str)`, producing garbled character-per-line output instead of an error.

**Lesson:** When consuming external data in Python, always validate the structural type of the top-level container before iterating. A string is iterable but is almost never the intended iterable.

## Key Points

- Iterating a Python string yields one character per iteration — `for item in "hello"` gives `"h"`, `"e"`, `"l"`, `"l"`, `"o"`
- Each character passes `isinstance(char, str)` — the type check that was meant to handle string blocks also accepts individual characters
- This produces garbled output (one character per line) instead of a clear error, making the bug hard to trace
- The fix is a guard at the top: `if isinstance(result, str): return result` before entering the iteration loop
- This is the same class of bug as import-time binding — Python's permissiveness lets wrong data flow through without raising exceptions

## Details

During MetaMode Phase B.4 integration testing, `claude -p --output-format json` returned `{"result": "text"}` (a string) instead of the expected `{"result": [{...}]}` (an array of blocks). The code in `claude_cli.py` iterated over `result` expecting block objects, but since `result` was a string, Python happily iterated over individual characters.

Each character — being a single-character string — passed the `isinstance(block, str)` check that was meant to handle text blocks within the array. The result was `pending-review.md` filled with character-per-line garbage. The corrupted data was unrecoverable and had to be replaced with a clean template.

The root cause is that Python's duck typing makes strings and lists interchangeable in iteration contexts. Unlike statically typed languages where `string` and `List<Block>` would be caught at compile time, Python only reveals the problem through corrupted output. The defensive pattern is to check the type of the container before iterating: `if isinstance(result, str)` handles the scalar case, and only then fall through to list iteration.

## Related Concepts

- [[concepts/python-import-time-binding]] - Same class of Python permissiveness bug: wrong data passes silently
- [[concepts/claude-cli-json-output-variance]] - The specific external data source that triggered this bug
