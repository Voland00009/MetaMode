---
title: "Python Import-Time Binding"
aliases: [import-time reference copy, from-import gotcha]
tags: [python, testing, debugging]
category: "python"
sources:
  - "daily/2026-04-11.md"
created: 2026-04-11
updated: 2026-04-11
---

# Python Import-Time Binding

**Context:** When writing unit tests that use `unittest.mock.patch` to override module-level variables imported with `from X import Y`.

**Problem:** Patching the original module (`config.X`) has no effect on code that already imported the value, because `from config import X` copies the reference at import time.

**Lesson:** Always patch at the consuming module (`module_under_test.X`), not at the source module (`config.X`).

## Key Points

- `from config import DAILY_DIR` creates a new name binding in the importing module that holds a copy of the reference
- After import, the consuming module's `DAILY_DIR` and `config.DAILY_DIR` are independent references
- `unittest.mock.patch('config.DAILY_DIR', new_value)` only rebinds `config.DAILY_DIR` — the consumer still holds the old reference
- `unittest.mock.patch('flush.DAILY_DIR', new_value)` correctly rebinds the name the code actually reads
- This is a general Python behavior, not specific to mock — it applies to any rebinding after import

## Details

When Python executes `from config import DAILY_DIR`, it looks up `DAILY_DIR` in the `config` module's namespace and binds a new local name to the same object. At this point, the importing module has its own independent reference. If you later rebind `config.DAILY_DIR` (which is what `mock.patch('config.DAILY_DIR')` does), the importing module's reference is unaffected — it still points to the original object.

This is particularly insidious in test suites because the tests appear to be patching correctly. The mock is in place, the test runs, but the code under test reads the original value. The failure mode is subtle: tests may pass or fail for the wrong reasons, giving false confidence.

The standard pattern discovered during MetaMode Phase B.2 was to always patch at the consumer level: `flush.DAILY_DIR`, `utils.DAILY_DIR`, `lint.KNOWLEDGE_DIR`, etc. This became the universal convention across all test files in the project.

## Related Concepts

- [[concepts/mock-patching-at-consumer-level]] - The practical pattern that follows from this understanding
- [[concepts/python-duck-typing-silent-failures]] - Another Python permissiveness issue where wrong data passes silently
- [[concepts/tdd-red-phase-value]] - TDD RED phase caught this bug early by revealing wrong-reason test failures
