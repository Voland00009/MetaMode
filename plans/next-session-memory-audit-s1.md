# Session 1: Cleanup & .claudeignore

**Date:** 2026-04-12
**Design spec:** `docs/superpowers/specs/2026-04-12-memory-audit-design.md`
**Approach:** B (Structural Optimization), Session 1 of 4
**Context budget:** <=60% — save progress and create next-session prompt when nearing limit

---

## Context

We did a full audit of the memory/config system across all Claude Code projects. Found 5 problems: slow session start, context fills too fast, info lost between sessions, no visibility into what's remembered, too many config files.

Research sources (Anthropic best practices, LLM Wiki v2, claudelint, token optimization guides) confirmed:
- CLAUDE.md should be 80-100 lines max (loaded every turn)
- .claudeignore is one of the highest-leverage optimizations (11K → 1.3K tokens in one case)
- Stale memory files waste context on every session
- "Two strikes" rule: only add to CLAUDE.md after second identical mistake

Full research findings are in the design spec.

## Tasks for this session

### 1. Measure baseline
- Run `/context` at the start and record token breakdown
- Note: system prompt, tools, memory, skills, conversation

### 2. Clean stale memory files (MetaMode project)
Location: `~/.claude/projects/c--Users-Voland-Dev-MetaMode/memory/`

These "Phase X done" files are stale — they track completed build phases that are no longer relevant:
- `project_phase_b1_done.md`
- `project_phase_b2_done.md`
- `project_phase_b3_done.md`
- `project_phase_c_task1_done.md`
- `project_step1_inventory.md`
- `project_step2_3_plan.md`
- `project_skills_plan.md`

Review each before deleting — if any contain non-obvious lessons, extract them first. Then remove from MEMORY.md index.

Also review for staleness:
- `project_ai_memory_system.md` — may overlap with final decision
- `project_research_synthesis.md` — may be superseded by audit
- `project_coleam00_codebase.md` — still relevant?
- `feedback_inventory_first.md` — one-time feedback, still applies?

### 3. Review memory in other project dirs
- `~/.claude/projects/C--Users-Voland/memory/` (7 files) — review, clean stale
- `~/.claude/projects/h-----------6--Training---automation-Projects/memory/` (19 files) — review, clean stale
- Identify any cross-project knowledge that should be global

### 4. Create .claudeignore for MetaMode
Create `MetaMode/.claudeignore`:
```
# Build artifacts
.venv/
__pycache__/
*.pyc
.pytest_cache/
dist/

# Large files
uv.lock
*.base
*.canvas

# Session history (huge JSONL files)
# These are in ~/.claude/projects/, not in repo, but just in case

# Input materials (reference only, not code)
input/

# Processed RAW files
raw/processed/

# Obsidian internals
.obsidian/
```

### 5. Add timestamps to templates
Update these to include `YYYY-MM-DD HH:MM` format:
- `hooks/session_start.py` — if it generates any timestamps
- `scripts/flush.py` — daily log entries
- Memory file creation — add "Updated:" field with datetime
- Design spec template

### 6. Update subscription details
Already done in this session (user_subscriptions.md updated with capabilities).
Verify the file looks correct.

### 7. Measure after
- Run `/context` again and record
- Compare with baseline
- Save results to `reports/memory-audit-s1-results.md`

## After completing all tasks
- Update the design spec with Session 1 results
- Write `plans/next-session-memory-audit-s2.md` for Session 2
- Commit changes

## Session 2 preview (next session)
- Audit and trim both CLAUDE.md files
- Restructure memory into tiers (hot/warm/archive)
- Centralize cross-project user knowledge
- Add session workflow to global CLAUDE.md
