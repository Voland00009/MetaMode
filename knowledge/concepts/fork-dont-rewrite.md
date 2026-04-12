---
title: "Fork-Don't-Rewrite: Extending Proven Code"
aliases: [fork strategy, surgical modifications, minimal fork]
tags: [architecture, workflow, productivity]
category: "architecture"
sources:
  - "raw/metamode-vs-coleam00-audit.md"
created: 2026-04-12
updated: 2026-04-12
---

# Fork-Don't-Rewrite: Extending Proven Code

**Context:** When you need functionality that an existing open-source project provides at ~80%+, and you want to add specific features or modifications.

**Problem:** The temptation to rewrite from scratch ("I can do it better/cleaner") leads to reimplementing solved problems, introducing new bugs in code that already worked, and spending effort on infrastructure instead of the actual differentiating features.

**Lesson:** Fork the proven codebase and make surgical additions. Keep the original architecture intact, modify only what's necessary, and focus effort exclusively on the features that differentiate your version.

## Key Points

- MetaMode is ~85% coleam00 code by volume — only 5 real modifications on top of the original
- The core scripts (flush, compile, lint, query, utils, config) are functionally identical to the original
- New functionality was added as new files (ingest_raw.py, user_prompt_submit.py) or minimal edits to existing files
- The original architecture decisions (hooks structure, daily→knowledge pipeline, AGENTS.md schema) were preserved as-is
- This approach delivered a working system faster than a rewrite would have, with the confidence of battle-tested code

## Details

The MetaMode project started from coleam00/claude-memory-compiler, which implements Karpathy's LLM wiki-memory pattern. Rather than building a memory system from scratch, the fork strategy preserved the entire original architecture: the hooks pipeline (SessionStart, SessionEnd, PreCompact), the scripts layer (flush.py, compile.py, lint.py, query.py), and the knowledge base structure (daily/, knowledge/, AGENTS.md schema).

The 5 real modifications were all additive: pending review in flush.py (quality gate), !save hook (new file), ingest_raw.py (new file), global hooks configuration (config change), and enriched session start (additions to existing hook). None of these required rewriting the core pipeline — they extended it at well-defined points.

A file-level diff confirms the approach: ~95% of hooks and scripts are identical or nearly identical to the original. The only "rewritten" files are session_start.py (which gained new sections but kept the original structure) and AGENTS.md (simplified for compile quality). Everything else is the original code with UTF-8 fixes for Windows.

The key discipline is resisting the urge to "improve" the original code. The original flush.py works. The original compile.py works. Touching them for style or minor improvements risks introducing bugs in proven code and creates merge conflicts with upstream updates.

## Related Concepts

- [[concepts/human-in-the-loop-quality-gate]] - The most impactful modification added to the fork — a quality gate, not a rewrite
- [[concepts/cc-hooks-lifecycle]] - The hook architecture was inherited from coleam00, not reimplemented
