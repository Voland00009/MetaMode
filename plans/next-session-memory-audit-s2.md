# Session 2: CLAUDE.md Optimization & Memory Restructure

**Date:** 2026-04-12
**Design spec:** `docs/superpowers/specs/2026-04-12-memory-audit-design.md`
**Approach:** B (Structural Optimization), Session 2 of 4
**Context budget:** <=60% — save progress and create next-session prompt when nearing limit
**Previous session results:** `reports/memory-audit-s1-results.md`

---

## Context

Session 1 completed: deleted 18 stale memory files across 3 projects (47 → 29), created `.claudeignore` for MetaMode, verified timestamps and subscriptions.

**IMPORTANT: All optimizations must apply GLOBALLY across all projects, not just MetaMode.**

### Session 1 baseline (`/context` at 36% usage, mid-session):
| Category | Tokens | % |
|----------|--------|---|
| System prompt | 6.6k | 3.3% |
| System tools | 10.5k | 5.2% |
| System tools (deferred) | 8.8k | 4.4% |
| Memory files | 3k | 1.5% |
| Skills (37 skills) | 2.3k | 1.2% |
| Messages | 49.5k | 24.8% |

Key insight: Memory files = only 3k tokens (CLAUDE.md global 870 + CLAUDE.md project 1.2k + MEMORY.md 911). Skills listings = 2.3k for 37 skills. The biggest win from S1 is .claudeignore (reduces file scanning), not memory token count.

Now we optimize the two files that are loaded EVERY TURN — the global and project CLAUDE.md files. These are the highest-leverage targets because they multiply by turn count (e.g., 80 lines × 40 turns = 3,200 lines of input).

Research says: 80-100 lines max per CLAUDE.md, apply "two strikes" rule, move domain knowledge to skills.

## Tasks for this session

### 1. Measure baseline
- Run `/context` at the start and record token breakdown
- Compare with Session 1 (if S1 baseline was recorded)

### 2. Audit global CLAUDE.md (~66 lines)
Location: `~/.claude/CLAUDE.md`

Review each section against these criteria:
- **"Two strikes" rule:** Is this instruction here because Claude made the same mistake twice? If not, does Claude already do this correctly without the instruction?
- **Domain knowledge:** Should this move to a skill (loaded on demand) instead of CLAUDE.md (loaded every turn)?
- **Duplication:** Is this already covered by memory files or project CLAUDE.md?

Specific areas to check:
- "Язык" section — needed or default behavior?
- "Уровень объяснений" — already in memory (`user_level.md`, `user_learning_metamode.md`)?
- "Стиль ответов" — some of these may be default Claude behavior
- "Работа с кодом" — some overlap with system prompt defaults
- "Personal Wiki" section — could move to a skill or remain since it's cross-project

### 3. Audit project CLAUDE.md (~71 lines)
Location: `MetaMode/CLAUDE.md`

Same criteria plus:
- Architecture details that belong in AGENTS.md
- Hook details that are derivable from code
- "Что НЕ делать" — still relevant?
- "Где что лежит" — derivable from file system?

### 4. Restructure memory into tiers
Current MetaMode memory (14 files) — classify each:
- **Hot (active):** Currently relevant, loaded into context
- **Warm (reference):** Useful background, accessed on demand
- **Archive:** Historical, rarely needed

Implementation: create subdirectories `memory/archive/` for archived files, update MEMORY.md with tier labels.

### 5. Centralize cross-project user knowledge
Currently duplicated:
- User level: `user_level.md` (Training) + `user_learning_metamode.md` (MetaMode)
- Session workflow: `feedback_session_workflow.md` (C--Users-Voland) + `feedback_session_per_step.md` (MetaMode)
- User profile: `user_profile.md` (Training only)

Move user-level info to global memory (`C--Users-Voland`), remove duplicates from project memory.

### 6. Add .claudeignore to other projects
- Create `.claudeignore` for wife's website project (nails-on-salon)
- Standard template: `.venv/`, `node_modules/`, `dist/`, `*.lock`

### 7. Measure after
- Run `/context` again and record
- Compare with baseline
- Append results to `reports/memory-audit-s2-results.md`

## After completing all tasks
- Update the design spec with Session 2 results
- Write `plans/next-session-memory-audit-s3.md` for Session 3
- Commit changes

## Session 3 preview (next session)
- Re-audit MetaMode vs Karpathy original + Wiki v2 comparison
- Process `input/New ASK/Transcrypt.txt`
- Update MetaMode README
- Create feature documentation
