---
title: "Mock Patching at Consumer Level"
aliases: [patch-where-used, mock target pattern]
tags: [python, testing, tdd]
category: "testing"
sources:
  - "daily/2026-04-11.md"
created: 2026-04-11
updated: 2026-04-11
---

# Mock Patching at Consumer Level

**Context:** Writing Python unit tests with `unittest.mock.patch` for code that uses `from X import Y` style imports.

**Problem:** `mock.patch('source_module.name')` silently does nothing when the code under test already holds its own reference via `from` import.

**Lesson:** Always patch the name where it is *read*, not where it is *defined*. The target string should be `'module_under_test.name'`, not `'config.name'`.

## Key Points

- The mock target is a dotted path to the *name binding* the code reads at runtime
- For `from config import DAILY_DIR` in `flush.py`, the correct patch target is `'flush.DAILY_DIR'`
- This applies to all module-level constants, not just paths — any `from X import Y` follows the same rule
- In MetaMode, this became the standard convention: `flush.DAILY_DIR`, `utils.DAILY_DIR`, `lint.KNOWLEDGE_DIR`, etc.
- Getting this wrong produces tests that pass or fail for the wrong reasons — a dangerous false signal

## Details

The Python documentation for `unittest.mock.patch` explicitly states: "patch where an object is looked up, which is not necessarily the same place as where it is defined." In practice, this is easy to forget because the mental model is "I want to replace `config.DAILY_DIR`" when in reality you need to replace the name the executing code will look up.

During MetaMode Phase B.2, TDD RED phase revealed this immediately. Tests were written first (RED), and when they failed for import-related reasons rather than logic reasons, the root cause was traced to incorrect patch targets. This was fixed before any production code was written, preventing the bug from hiding in a passing test suite.

The pattern was applied consistently across all four migrated scripts (flush.py, compile.py, lint.py, query.py), establishing a project-wide convention that made subsequent test writing faster and more reliable.

## Related Concepts

- [[concepts/python-import-time-binding]] - The underlying Python mechanism that makes this necessary
- [[concepts/tdd-red-phase-value]] - How TDD caught incorrect patch targets before they could mask real bugs
