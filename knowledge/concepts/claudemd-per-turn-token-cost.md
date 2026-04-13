---
title: "CLAUDE.md Per-Turn Token Cost Multiplier"
aliases: [CLAUDE.md token cost, context window budget, instruction file sizing]
tags: [claude-code, workflow, productivity]
category: "claude-code"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
updated: 2026-04-12
---

# CLAUDE.md Per-Turn Token Cost Multiplier

**Context:** When writing CLAUDE.md project instructions for Claude Code and deciding how much to include.

**Problem:** CLAUDE.md loads in full on every single conversation turn — not just once at session start. A 300-line file across 40 messages means 12,000 lines of repeated instruction tokens, consuming context window budget that could hold actual conversation and code.

**Lesson:** Keep CLAUDE.md under 80-100 lines. Move domain-specific knowledge into skills (demand-loaded). Use the "two strikes" rule: only add an instruction to CLAUDE.md after Claude makes the same mistake twice.

## Key Points

- CLAUDE.md loads into **every turn** of the conversation — the cost is `lines × number_of_turns`, not just `lines`
- Anthropic recommends 80-100 lines maximum for CLAUDE.md
- A documented optimization reduced a project's startup from 11,000 to 1,300 tokens using `.claudeignore` + CLAUDE.md trimming
- "Two strikes" rule: don't add an instruction after the first mistake — it might be a one-off. Add it only after the second identical mistake
- Skills are the escape hatch: domain knowledge loads on demand, not every turn

## Details

During the MetaMode memory audit, research into Claude Code best practices revealed that CLAUDE.md has a hidden cost multiplier. Unlike a configuration file that loads once, CLAUDE.md content is injected into every conversation turn. This means a project with a 300-line CLAUDE.md and a 40-message conversation effectively sends 12,000 lines of instructions — most of which are irrelevant to any individual message.

The MetaMode project's CLAUDE.md was at 137 lines before the audit — above the recommended 80-100 line threshold. Analysis revealed that significant portions duplicated the Claude Code system prompt (a "work with code" section that restated default behavior), included stack/architecture information derivable from `pyproject.toml`, and listed hook configurations already present in `settings.json`. After removing derivable and duplicated content, CLAUDE.md dropped from 137 to 51 lines — a 63% reduction.

The "two strikes" rule provides a practical heuristic for CLAUDE.md maintenance. When Claude makes a mistake, the instinct is to add an instruction preventing it. But most mistakes are contextual one-offs. Adding an instruction for every mistake bloats the file with rules that fire on every turn but are relevant once. Waiting for the second occurrence confirms the pattern is recurring and worth the per-turn cost.

MEMORY.md has a related constraint: it truncates after 200 lines. This makes it critical to keep the memory index concise — one-line entries, no full content in the index file.

## Related Concepts

- [[concepts/cc-skills-contextual-loading]] - Skills are the solution to CLAUDE.md bloat: load knowledge on demand, not every turn
- [[concepts/claudeignore-context-optimization]] - Complementary optimization: .claudeignore reduces file scanning, CLAUDE.md sizing reduces instruction overhead
