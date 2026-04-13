---
title: "Stale Memory Detection ↔ Periodic Lint Lifecycle"
tags: [ai, workflow, meta]
category: "ai"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
---

# Stale Memory Detection ↔ Periodic Lint Lifecycle

**Context:** When maintaining persistent AI memory systems that accumulate files over weeks and months, and wanting to prevent quality degradation without constant manual attention.

**Problem:** Stale memory files actively mislead the AI (38% staleness found in audit), but one-off audits don't prevent re-accumulation. The problem is inherently recurring — new files become stale as the project evolves.

**Lesson:** Stale memory detection (the problem) and periodic lint reminders (the solution) form a lifecycle: the audit reveals what staleness looks like, the lint codifies those checks into automated detection, and the reminder ensures the detection runs regularly without adding friction.

## The Connection

The MetaMode Memory System Global Audit was a one-time event that deleted 18 stale files (38% of total). But the conditions that created staleness — phase completions, decision changes, project evolution — are ongoing. Without a recurring mechanism, the same audit would need to be repeated manually every few weeks.

The memory lint system (`memory_lint.py`) codifies the audit's findings into automated checks: broken references in MEMORY.md, orphan files with no index entry, file count thresholds (>30), total size limits (>100K), and CLAUDE.md line counts. These are the specific patterns that the manual audit identified as indicators of staleness or bloat.

The opt-in reminder bridges the gap between "checks exist" and "checks run." The session start hook monitors the `last_memory_lint` timestamp and displays a reminder when 14 days have elapsed. The user decides when to act, preserving the opt-in principle while ensuring the lint doesn't go indefinitely unrun.

Together they form a complete lifecycle:
1. **Detection** (audit) identifies what staleness looks like → patterns codified into lint rules
2. **Automation** (lint script) checks for those patterns on demand → reports findings
3. **Cadence** (reminder) ensures the lint runs at appropriate intervals → prevents re-accumulation

## Implications

1. **One-off audits should produce reusable checks** — the value of an audit isn't just the cleanup, it's the rules extracted for ongoing detection
2. **Different decay rates need different intervals** — wiki content drifts weekly (7-day lint), memory files drift monthly (14-day lint), so intervals should match
3. **The pattern generalizes** — any system that accumulates persistent state (databases, config files, dependency lists) benefits from the same audit → lint → remind lifecycle
4. **Lint thresholds should be calibrated from real audits** — the >30 file count and >100K size limits came from observing actual project sizes, not arbitrary numbers

## Related Concepts

- [[concepts/stale-memory-worse-than-absence]]
- [[concepts/opt-in-lint-reminders]]
- [[concepts/memory-tiering-access-frequency]]
- [[concepts/human-in-the-loop-quality-gate]]

