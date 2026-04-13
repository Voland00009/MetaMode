---
title: ".claudeignore for Context Window Optimization"
aliases: [claudeignore, context window optimization, token budget]
tags: [claude-code, devtools, productivity]
category: "claude-code"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
updated: 2026-04-12
---

# .claudeignore for Context Window Optimization

**Context:** When a Claude Code project contains directories that pollute the context window — virtual environments, lock files, cached data, large input directories.

**Problem:** Without `.claudeignore`, Claude Code scans and indexes all project files. Directories like `.venv/`, `node_modules/`, lock files, and data directories consume thousands of tokens in the context window without providing useful information.

**Lesson:** `.claudeignore` is one of the highest-leverage context optimizations available. A single documented case showed startup dropping from 11,000 to 1,300 tokens. The file uses `.gitignore` syntax and should be configured for every project.

## Key Points

- `.claudeignore` uses `.gitignore` syntax — placed at project root, patterns exclude files from Claude Code's file scanning
- Documented case: 11,000 → 1,300 tokens at startup after adding `.claudeignore` — an 88% reduction
- Common patterns to ignore: `.venv/`, `node_modules/`, `*.lock`, `uv.lock`, `raw/processed/`, `.obsidian/`, `input/`, `docs/archive/`
- Unlike `.gitignore`, `.claudeignore` affects the AI's context window, not version control — files are still accessible but not auto-indexed
- Should be one of the first files created when setting up Claude Code for a project

## Details

Claude Code builds an index of project files to understand the codebase structure. Every file that appears in this index consumes tokens in the context window. For projects with large dependency directories, data files, or generated artifacts, this indexing can waste thousands of tokens on files that provide no useful context for code assistance.

During the MetaMode memory audit, `.claudeignore` files were created for two projects (MetaMode and nails-on-salon). The MetaMode configuration excludes `.venv/`, `input/` (raw data files), `uv.lock` (dependency lock), `raw/processed/` (already-ingested files), `.obsidian/` (Obsidian metadata), `plans/sessions/` (ephemeral session plans), and `docs/archive/` (historical documents). Each of these directories contained files that were never useful for Claude Code's code assistance but consumed context tokens.

The optimization compounds with CLAUDE.md sizing. A project with a lean `.claudeignore` and a sub-100-line CLAUDE.md starts each conversation with a minimal token footprint, leaving maximum room for actual code discussion. Conversely, a project without `.claudeignore` and with a bloated CLAUDE.md may consume 30-50% of the context budget before the first user message.

The baseline measurement before the MetaMode audit was 36% context usage at session start. After applying `.claudeignore` across projects and trimming CLAUDE.md, the goal was to reduce this significantly — though exact post-optimization measurements required manual verification in fresh sessions.

## Related Concepts

- [[concepts/claudemd-per-turn-token-cost]] - Complementary optimization: .claudeignore reduces scanning overhead, CLAUDE.md sizing reduces per-turn instruction cost
- [[concepts/cc-settings-local-vs-shared]] - .claudeignore is committed to the repo (shared), similar to settings.json
- [[concepts/cc-skills-contextual-loading]] - Skills further reduce context usage by loading instructions on demand
