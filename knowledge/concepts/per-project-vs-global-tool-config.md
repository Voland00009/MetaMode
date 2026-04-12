---
title: "Per-Project vs Global Tool Configuration"
aliases: [global hooks, per-project hooks, tool scope tradeoff]
tags: [devtools, workflow, claude-code]
category: "devtools"
sources:
  - "raw/metamode-vs-coleam00-audit.md"
created: 2026-04-12
updated: 2026-04-12
---

# Per-Project vs Global Tool Configuration

**Context:** When configuring developer tools (hooks, linters, formatters, memory systems) that could apply to a single project or across all projects on a machine.

**Problem:** Per-project configuration is zero-config for new users (clone and it works) but requires duplication across projects. Global configuration eliminates duplication but requires manual setup and can't be shared via version control.

**Lesson:** Choose per-project when the tool is project-specific and team-shared. Choose global when the tool is personal and cross-project. For knowledge systems like wiki-memory, global is better — one unified knowledge base beats fragmented per-project copies.

## Key Points

- Per-project (coleam00 pattern): hooks in `.claude/settings.json`, committed to repo, works for any cloner — but needs a copy per project
- Global (MetaMode pattern): hooks in `~/.claude/settings.json`, one installation, one wiki for all projects — but requires manual setup
- Per-project wins on **installation UX**: "clone and it works" vs reading setup docs
- Global wins on **knowledge continuity**: lessons from project A are available in project B
- The `uv run --directory <path>` pattern enables global hooks that point back to a specific project directory

## Details

coleam00/claude-memory-compiler uses per-project configuration: hooks are defined in `.claude/settings.json` at the project root, and the memory system lives inside the project directory. This is excellent for onboarding — any developer who clones the repo gets the full memory system working immediately. But it means each project has its own isolated knowledge base, and lessons learned in one project don't transfer to another.

MetaMode moved hooks to `~/.claude/settings.json` (the global user config) so that the memory system activates in every project. The hooks use `uv run --directory C:/Users/Voland/Dev/MetaMode` to invoke scripts from a fixed location regardless of the current working directory. This creates a single unified wiki where knowledge from all projects accumulates.

The tradeoff is installation UX. coleam00 is truly zero-config per project. MetaMode requires the user to: (1) clone the MetaMode repo, (2) run `uv sync`, (3) copy hook definitions into their global `~/.claude/settings.json`. This is a one-time cost, but it's a real barrier compared to "clone and it works."

For a personal knowledge system, global is the clear winner — the whole point is accumulating knowledge across all work. For team tooling (formatters, linters, test runners), per-project is better — it ensures consistency across the team without requiring each developer to configure global settings.

## Related Concepts

- [[concepts/cc-settings-local-vs-shared]] - The shared vs local settings split is the mechanism that enables both patterns
- [[concepts/cc-hooks-lifecycle]] - Hooks are the specific tool being configured per-project vs globally
