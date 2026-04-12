---
title: "TDD RED Phase Value"
aliases: [red-green-refactor, test-first bug detection]
tags: [tdd, testing, workflow]
category: "testing"
sources:
  - "daily/2026-04-11.md"
created: 2026-04-11
updated: 2026-04-11
---

# TDD RED Phase Value

**Context:** When implementing features using Test-Driven Development (TDD), the RED phase is where you write a failing test before writing any production code.

**Problem:** Without the RED phase, bugs in test setup (wrong mock targets, incorrect imports, bad assumptions) hide inside passing tests, creating false confidence.

**Lesson:** The RED phase catches "failing for the wrong reason" — when a test fails due to setup errors rather than missing logic, you fix the test infrastructure before writing code, preventing hidden bugs.

## Key Points

- RED phase = write a test that fails for the *right* reason (missing functionality)
- If the test fails for the *wrong* reason (import error, bad mock target), the RED phase reveals this immediately
- Without RED, a bad mock target can make a test pass vacuously — the mock does nothing, the code runs with real values, and the test happens to pass
- In MetaMode Phase B.2, RED phase caught incorrect `mock.patch` targets (patching `config.X` instead of `module.X`) before any production code was written
- This prevented a subtle class of bugs where tests pass but don't actually test what they claim to test

## Details

During MetaMode Phase B.2 (SDK-to-CLI migration), the TDD RED phase provided immediate value by catching a Python import-time binding bug. Tests were written first with `mock.patch('config.DAILY_DIR')` as the target. In the RED phase, these tests failed — but not because the production code was missing. They failed because the mock wasn't reaching the code under test.

This "wrong reason" failure is exactly what the RED phase is designed to catch. The developer investigated why the test failed, discovered the import-time binding issue, and corrected the mock targets to `'flush.DAILY_DIR'`, `'utils.DAILY_DIR'`, etc. Only after the tests failed for the *right* reason (missing implementation) did development proceed to the GREEN phase.

Had the tests been written after the production code (non-TDD), the incorrect mock targets might have gone unnoticed. The tests could have passed because the real `config.DAILY_DIR` pointed to a valid directory in the test environment, giving false confidence that the mocks were working correctly.

## Related Concepts

- [[concepts/python-import-time-binding]] - The specific bug that TDD RED phase caught in this case
- [[concepts/mock-patching-at-consumer-level]] - The correct pattern that was discovered through RED phase investigation
