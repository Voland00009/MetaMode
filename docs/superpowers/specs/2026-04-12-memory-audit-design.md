# Memory System Global Audit & Optimization — Design Spec

**Date:** 2026-04-12 16:20 UTC+3
**Status:** Approved (Approach B)
**Scope:** Global (all projects) with future MetaMode integration

---

## Problem Statement

5 pain points identified:
1. **(A) Slow session start** — Claude scans files, wastes tokens "remembering" context
2. **(B) Context window fills too fast** — bloated memory + skills + plugins eat space before work begins
3. **(C) Information lost between sessions** — fragmented across 4 project memory dirs
4. **(D) No visibility** into what Claude remembers vs forgets
5. **(E) Too many configs** — CLAUDE.md (global) + CLAUDE.md (project) + MEMORY.md + AGENTS.md + knowledge/index.md + daily logs + plans/ + decisions/ + docs/

## Current State Snapshot (2026-04-12)

### Memory structure

| Layer | Location | Size | Loaded when |
|-------|----------|------|-------------|
| Global CLAUDE.md | `~/.claude/CLAUDE.md` | 66 lines | Every turn |
| Project CLAUDE.md | `MetaMode/CLAUDE.md` | 71 lines | Every turn |
| Auto-memory index | `~/.claude/projects/.../memory/MEMORY.md` | 21 entries | Session start |
| Auto-memory files | `~/.claude/projects/.../memory/*.md` | ~700 lines total | On demand |
| SessionStart hook | Injects index.md + daily log | ~30 lines | Session start |
| AGENTS.md | `MetaMode/AGENTS.md` | ~80 lines | On demand |
| Wiki knowledge | `MetaMode/knowledge/` | 16 articles | On demand |

### Per-project memory directories

| Directory | Files | Size | Status |
|-----------|-------|------|--------|
| `c--Users-Voland-Dev-MetaMode` | 21 memory files | 22MB (incl. sessions) | Active, bloated |
| `C--Users-Voland` | 7 memory files | 18MB | Stale? |
| `h---Training---automation-Projects` | 19 memory files | 87MB | Active (wife's site) |
| `c--Users-Voland-Dev` | 0 memory files | 20KB | Empty |

### Key metrics

- **Total memory files across all projects:** 47
- **Stale "Phase X done" markers in MetaMode:** ~12 files
- **.claudeignore:** Does NOT exist in any project
- **Timestamps in files:** Date only, no time

## Research Findings

### From Anthropic Official Best Practices
Source: https://code.claude.com/docs/en/best-practices

- CLAUDE.md loaded every turn — keep concise, ~80-100 lines per file
- "Ruthlessly prune. If Claude already does something correctly without the instruction, delete it"
- "Two strikes" rule: only add after second identical mistake
- .claudeignore is critical for startup token reduction
- Skills > CLAUDE.md for domain-specific knowledge (loaded on demand)
- Subagents for exploration keep main context clean
- `/clear` between unrelated tasks
- `/compact` with focus instructions: `/compact Focus on the API changes`

### From claudelint
Source: https://claudelint.com/rules/claude-md/claude-md-size

- Warn at 40KB
- Practical limit: one screen (~80-100 lines)
- Cost multiplier: lines × turns (300 lines × 40 turns = 12,000 lines of input)

### From token optimization experts
Sources:
- https://www.mindstudio.ai/blog/claude-code-token-management-hacks-3
- https://genaiskills.io/articles/claude-code-token-optimisation
- https://dev.to/boucle2026/7-ways-to-cut-your-claude-code-token-usage-elb

- .claudeignore reduced one project from 11,000 to 1,300 startup tokens
- Model switching (Opus for complex, Sonnet for daily, Haiku for repetitive)
- Session naming with `/rename` for findability
- `/btw` for side questions that don't enter history

### From LLM Wiki v2
Source: https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2

- Lifecycle management: confidence scoring, retention curves
- Consolidation tiers: working → episodic → semantic → procedural
- Schema document is most important file
- v2 adds supersession mechanism (new info replaces old, versions preserved)
- Overkill for <500 documents, relevant later

### From everything-claude-code
Source: https://github.com/affaan-m/everything-claude-code

- Hook profiles: minimal/standard/strict for runtime token trade-offs
- Skill-based compartmentalization (load only relevant skills)
- Progressive context refinement for subagents

## Chosen Approach: B (Structural Optimization)

4 sessions, each using <=60% context window, then new session.

### Session 1: Cleanup & .claudeignore ✅ (2026-04-12)

- [x] Delete stale memory files — 10 from MetaMode, 4 from C--Users-Voland, 7 from Training (18 total)
- [x] Review and clean memory in other project dirs (47 → 29 files, -38%)
- [x] Create `.claudeignore` for MetaMode
- [ ] ~~Create `.claudeignore` template for other projects~~ (deferred to S2)
- [x] Add datetime (not just date) to all file templates — already in place
- [x] Update `user_subscriptions.md` with full subscription details
- [ ] ~~Measure: run `/context` before and after~~ (interactive command, not automatable)
- Results: `reports/memory-audit-s1-results.md`

### Session 2: CLAUDE.md optimization & memory restructure ✅ (2026-04-12)
- [x] Audit global CLAUDE.md — 66→23 lines (−65%), removed system prompt duplicates
- [x] Audit project CLAUDE.md — 71→28 lines (−61%), removed derivable info
- [x] Restructure memory into tiers: 5 active + 10 archived in MetaMode
- [x] Centralize cross-project knowledge — 6 files moved to global memory
- [x] Remove duplicated info between CLAUDE.md and memory files
- [x] Add .claudeignore to nails-on-salon project
- Results: `reports/memory-audit-s2-results.md`

### Session 3: MetaMode audit + documentation
- [ ] Re-audit MetaMode vs Karpathy original + Wiki v2 comparison
- [ ] Process `input/New ASK/Transcrypt.txt` — extract any new patterns we're missing
- [ ] Update MetaMode README with usage instructions
- [ ] Create MetaMode feature documentation (what it does, how to use, tips)
- [ ] Generate presentation via NotebookLM (if accessible)
- [ ] Record all changes made since last audit

### Session 4: Testing & verification
- [ ] e2e test: new session start in MetaMode — measure tokens
- [ ] e2e test: new session start in wife's website project — measure tokens
- [ ] Verify memory persists correctly across sessions
- [ ] Verify .claudeignore works
- [ ] Final token comparison: before vs after
- [ ] Save results to `reports/`

## Design Principles

1. **60% context budget per session** — never exceed, save and switch to new session
2. **Timestamp everything** — `2026-04-12 16:20` format, not just date
3. **Skills over CLAUDE.md** — domain knowledge loaded on demand
4. **Single source of truth** — no duplication between memory layers
5. **Global-first** — user-level info in global memory, project-specific in project memory
6. **Future-ready** — structure allows MetaMode integration later

## User Context

- **Subscriptions:** Claude Max, Gemini PRO, Perplexity Pro, ChatGPT Plus
- **Tools available:** NotebookLM (API access via skill, sometimes flaky)
- **Deep Research:** Available via Gemini, Perplexity, ChatGPT
- **Skill ecosystem:** superpowers plugin + 11 standalone skills in ~/.claude/SKILLS/
