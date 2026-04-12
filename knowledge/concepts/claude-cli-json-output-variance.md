---
title: "Claude CLI JSON Output Variance"
aliases: [claude -p output format, claude cli result types]
tags: [claude-code, python, debugging]
category: "claude-code"
sources:
  - "daily/2026-04-11.md"
created: 2026-04-11
updated: 2026-04-11
---

# Claude CLI JSON Output Variance

**Context:** When using `claude -p --output-format json` in scripts that parse the structured response programmatically.

**Problem:** The `result` field in the JSON response can be either a string (`"text"`) or an array of content blocks (`[{...}]`), depending on the response. Code that assumes one form will break on the other.

**Lesson:** Always check the type of the `result` field before processing. Handle both `str` and `list` cases explicitly.

## Key Points

- `claude -p --output-format json` returns a JSON object with a `result` field
- `result` can be a string: `{"result": "The answer is 42"}`
- `result` can be an array of blocks: `{"result": [{"type": "text", "text": "..."}]}`
- Code must handle both forms — `if isinstance(result, str)` before iteration
- Discovered during MetaMode Phase B.4 when the string form caused a character-per-line garbling bug

## Details

The Claude CLI's `--output-format json` flag produces structured JSON output intended for programmatic consumption. However, the `result` field is polymorphic — it can be either a plain string for simple text responses or an array of content blocks for more complex outputs.

This variance was discovered during MetaMode Phase B.4 integration testing. The `claude_cli.py` module expected `result` to always be an array and iterated over it to extract text blocks. When Claude returned a simple string result, the iteration produced individual characters instead of content blocks, leading to garbled output in `pending-review.md`.

The fix was straightforward: add a type check before the iteration loop. If `result` is a string, return it directly. If it's a list, iterate and extract text content from each block. This defensive approach handles both current forms and is resilient to potential future changes in the CLI output format.

## Related Concepts

- [[concepts/python-duck-typing-silent-failures]] - The Python behavior that made this bug manifest as garbled output rather than an error
- [[concepts/mock-patching-at-consumer-level]] - Both require understanding runtime type behavior in Python
