---
title: "Opt-In Lint Reminders Over Auto-Enforcement"
aliases: [lint reminder, periodic maintenance, opt-in checks]
tags: [workflow, devtools, meta, productivity]
category: "workflow"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
updated: 2026-04-12
---

# Opt-In Lint Reminders Over Auto-Enforcement

**Context:** When building maintenance tasks (wiki lint, memory lint, dependency audits) that should run periodically but don't need to block the developer's current workflow.

**Problem:** Auto-enforced maintenance (runs automatically, blocks on failure) creates friction on every session — especially for infrequent checks that pass 95% of the time. But without any reminder, maintenance is forgotten entirely and problems accumulate silently.

**Lesson:** Use opt-in reminders: check the timestamp of the last run, display a reminder if overdue, but never auto-execute or block. Different maintenance tasks get different intervals based on how fast their target drifts.

## Key Points

- The session start hook checks `state.json` timestamps and shows a `## Lint Reminder` section only when checks are overdue
- **Wiki lint = 7 days** — knowledge articles change frequently through daily compilation
- **Memory lint = 14 days** — memory files change less often, mostly during explicit cleanup sessions
- The reminder tells the user what to run (`uv run python scripts/lint.py`, `uv run python scripts/memory_lint.py`) but never runs it automatically
- `lint.py --include-memory` combines both checks into a single command for convenience when the user decides to act

## Details

The MetaMode project initially considered a "health check system" — an automated suite that would run diagnostics on the wiki, memory, and configuration at session start. After brainstorming and multiple design iterations, this was replaced by a simpler pattern: timestamp-based lint reminders.

The implementation tracks two timestamps in `scripts/state.json`: `last_lint` (wiki lint) and `last_memory_lint` (memory lint). The `session_start.py` hook reads both timestamps, compares them against their respective intervals (7 and 14 days), and includes a reminder in the session start output only when one or both are overdue. If both are current, no reminder appears — zero noise.

The interval difference reflects the drift rate of each system. Wiki articles are compiled from daily logs, so new articles appear frequently and the wiki structure changes often — broken links, orphan files, and index inconsistencies can develop within a week. Memory files, by contrast, change mainly during explicit cleanup sessions (like the Memory System Global Audit) and during the rare add/remove operations. Fourteen days is sufficient to catch drift without over-prompting.

The `--include-memory` flag on `lint.py` was added so that when the user does decide to run lint (prompted by the reminder), they can run both checks in one command. This preserves the opt-in principle — the combined check is available but never forced.

This pattern replaced a more ambitious health check system design that included auto-diagnostics, severity levels, and automatic remediation suggestions. The simpler approach was chosen because the maintenance actions (running lint, reviewing results, fixing issues) inherently require human judgment and can't be meaningfully automated.

## Related Concepts

- [[concepts/stale-memory-worse-than-absence]] - Memory lint catches the staleness that this concept warns about
- [[concepts/two-pass-llm-quality-audit]] - Both are "soft gate" patterns: flag problems without blocking or auto-fixing
- [[concepts/cc-hooks-lifecycle]] - Lint reminders are implemented via the SessionStart hook lifecycle event

