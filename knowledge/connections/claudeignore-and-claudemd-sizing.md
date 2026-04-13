---
title: ".claudeignore ↔ CLAUDE.md Sizing: Complementary Context Optimizations"
tags: [claude-code, productivity, workflow]
category: "claude-code"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
---

# .claudeignore ↔ CLAUDE.md Sizing: Complementary Context Optimizations

**Context:** When optimizing Claude Code's context window usage to maximize the space available for actual code discussion and minimize wasted tokens.

**Problem:** Context window waste comes from two independent sources: file scanning overhead (Claude Code indexing irrelevant files) and instruction overhead (CLAUDE.md content loaded every turn). Optimizing only one leaves the other as a bottleneck.

**Lesson:** `.claudeignore` and CLAUDE.md sizing are complementary optimizations that address different layers of context waste. Together they reduced MetaMode's context baseline from 36% to a significantly lower level. Neither alone is sufficient.

## The Connection

Context window budget is consumed at two distinct stages of each conversation turn:

- **File scanning** (addressed by `.claudeignore`): Claude Code builds an index of project files. Without exclusions, virtual environments, lock files, data directories, and cached artifacts all contribute tokens. `.claudeignore` removes these from scanning entirely — a documented case showed 11,000 → 1,300 tokens, an 88% reduction at this layer.

- **Instruction injection** (addressed by CLAUDE.md sizing): CLAUDE.md loads in full on every turn. At 137 lines × 40 turns, this is 5,480 lines of repeated instructions. Trimming to 51 lines saves 63% per turn. The "two strikes" rule and moving domain knowledge to skills further reduces this cost.

The MetaMode audit applied both optimizations simultaneously: `.claudeignore` was created for two projects (removing `.venv/`, `input/`, lock files, etc.), and CLAUDE.md was trimmed from 137 to 51 lines. Skills were identified as the escape hatch for domain knowledge that was removed from CLAUDE.md but still needed occasionally.

## Implications

1. **Always configure both** — a lean CLAUDE.md with no `.claudeignore` still wastes thousands of tokens on file scanning. A good `.claudeignore` with a bloated CLAUDE.md still wastes per-turn instruction budget.
2. **Measure the baseline** — use `/context` at session start to see the combined effect. The MetaMode baseline was 36% before optimization.
3. **Skills are the third leg** — content removed from CLAUDE.md doesn't disappear, it moves to on-demand skills. The three together (ignore + size + skills) form a complete context optimization strategy.
4. **The multiplier matters** — file scanning waste is roughly constant per session; CLAUDE.md waste multiplies per turn. For long conversations, CLAUDE.md sizing has a larger cumulative impact.

## Related Concepts

- [[concepts/claudeignore-context-optimization]]
- [[concepts/claudemd-per-turn-token-cost]]
- [[concepts/cc-skills-contextual-loading]]
