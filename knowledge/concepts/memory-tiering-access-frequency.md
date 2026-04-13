---
title: "Memory Tiering by Access Frequency (Hot/Warm/Archive)"
aliases: [memory tiers, hot warm archive, memory organization]
tags: [ai, agents, workflow, meta]
category: "ai"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
updated: 2026-04-12
---

# Memory Tiering by Access Frequency (Hot/Warm/Archive)

**Context:** When managing persistent memory files for AI assistants across multiple projects, and the flat list of files grows beyond 20-30 entries.

**Problem:** A flat memory directory treats all files equally — active project decisions sit alongside completed-phase markers and historical references. The AI loads all of them into context, wasting tokens on cold information while the index (MEMORY.md) fills up toward its 200-line truncation limit.

**Lesson:** Classify memory files into tiers by access frequency: hot (loaded every session), warm (available but not auto-loaded), archive (removed from index, kept in git). This reduces per-session token cost while preserving historical context.

## Key Points

- **Hot tier** (5-10 files): active project state, current feedback, frequently-referenced facts — loaded into MEMORY.md index and auto-read by the AI
- **Warm tier**: reference material, completed milestones with still-relevant lessons — accessible via direct file read but not in the index
- **Archive tier**: phase trackers, old plans, superseded decisions — removed from memory directory entirely, preserved only in git history
- During the MetaMode audit, memory files went from 21 active → 5 hot (−76%) by archiving phase trackers and centralizing user-level files
- MEMORY.md truncates after 200 lines — tiering is essential for projects with more than ~15-20 memory files

## Details

The MetaMode Memory System Global Audit revealed that a flat memory structure degrades as the project matures. Of 21 memory files in the MetaMode project directory, 10 were phase completion markers (`project_phase_b1_done.md`, etc.) that provided no actionable information — their lessons were already captured in wiki articles or code. Another 3 were outdated research files. Only 5 files contained information that the AI needed on every session.

The tiering solution classifies files by how often they're needed. Hot-tier files stay in the MEMORY.md index and are automatically loaded into every conversation. These include active project decisions, current feedback rules, and frequently-referenced facts (like subscription details or tool setup). Warm-tier files are kept in the memory directory but removed from the index — the AI can read them on demand when the topic comes up, but they don't consume context tokens by default. Archive-tier files are deleted from the memory directory entirely; git history preserves them if needed.

A related optimization is centralizing user-level information. Files like `user_subscriptions.md`, `user_profile.md`, and `user_session_workflow.md` were duplicated across 3 project-specific memory directories. Moving them to the global memory directory (`~/.claude/projects/` root-level equivalent) eliminated duplication and ensured consistency — updating a subscription in one place updates it everywhere.

The audit reduced total memory files from 47 to 23 across all projects (−51%), with MetaMode's active set dropping from 21 to 5 (−76%). This directly reduces the token cost of memory loading on each conversation turn.

## Related Concepts

- [[concepts/stale-memory-worse-than-absence]] - Stale files are the primary candidates for archive tier — they actively mislead if kept hot
- [[concepts/claudemd-per-turn-token-cost]] - Memory files share the same per-turn cost multiplier as CLAUDE.md — fewer hot files = less waste
- [[concepts/claudeignore-context-optimization]] - Complementary optimization: .claudeignore reduces file scanning, tiering reduces memory loading

