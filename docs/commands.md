🌐 **English** | [Русский](commands.ru.md)

# Command Reference

Everything MetaMode can do — automatic hooks, CLI scripts, and in-chat commands.

---

## Automatic (Hooks)

These run without any action from you. Configure once in [setup](setup.md), then forget.

| Hook | Trigger | What it does | You see |
|------|---------|-------------|---------|
| **SessionStart** | Every session start | Injects wiki index + recent daily log into Claude's context | Claude starts with your knowledge |
| **SessionEnd** | Session close (`/exit`, close terminal) | Extracts transcript, spawns `flush.py` in background | Nothing — runs silently |
| **PreCompact** | Claude auto-compacts context (window full) | Same as SessionEnd — insurance against losing early decisions | Nothing — runs silently |
| **UserPromptSubmit** | You type `!save <text>` | Saves note directly to daily log, blocks prompt (0 tokens) | Confirmation message on stderr |

### How hooks work

- **Global:** hooks fire in every Claude Code session, from any project
- **Recursion guard:** if Claude Agent SDK is the caller (flush/compile), hooks exit immediately — no infinite loops
- **Flush dedup:** if the same session flushes twice within 60 seconds, the second flush is skipped

---

## CLI Scripts

Run these from your MetaMode directory. All commands use `uv run python scripts/<script>.py`.

### compile.py — Daily logs to wiki articles

Reads uncompiled daily logs, sends each to Agent SDK with the wiki schema, creates/updates wiki articles.

```bash
uv run python scripts/compile.py                          # compile new logs only
uv run python scripts/compile.py --all                    # force recompile everything
uv run python scripts/compile.py --file daily/2026-04-01.md  # compile one specific log
uv run python scripts/compile.py --dry-run                # show what would be compiled
```

| Flag | Description |
|------|-------------|
| `--all` | Ignore hash cache, recompile all daily logs |
| `--file <path>` | Compile a specific daily log file |
| `--dry-run` | Print which files would be compiled, don't run Agent SDK |

**When to use:** after accumulating 3+ daily logs, or when you want fresh wiki articles from recent sessions.

**Auto-trigger:** `flush.py` automatically spawns compile after 18:00 if daily logs changed during the day.

---

### query.py — Ask your wiki

Searches the wiki and synthesizes an answer using Agent SDK.

```bash
uv run python scripts/query.py "How should I handle auth redirects?"
uv run python scripts/query.py "What patterns do I use?" --file-back
```

| Flag | Description |
|------|-------------|
| `--file-back` | Save the answer as a Q&A article in `knowledge/qa/` |

**When to use:** you want to check what your wiki knows about a topic — without opening Claude Code.

---

### ingest_raw.py — External docs to wiki

Processes markdown/text files from the `raw/` inbox. Same compilation pipeline as `compile.py`, but for external content.

```bash
uv run python scripts/ingest_raw.py
```

No flags. Processes all `.md` and `.txt` files in `raw/`, creates wiki articles, moves originals to `raw/processed/`.

**When to use:** you found an article, took meeting notes, or have research notes you want in your wiki. Drop the file in `raw/`, then run this.

**RAW file format:**
```markdown
# Title of the insight

## Context
Where/when this came up

## Key Insight
The actual lesson or pattern

## Example (optional)
Code or scenario illustrating the point
```

---

### lint.py — Wiki health checks

Runs 7 structural and semantic checks on your wiki.

```bash
uv run python scripts/lint.py                    # all 7 checks
uv run python scripts/lint.py --structural-only  # skip LLM contradiction check (faster)
uv run python scripts/lint.py --include-memory   # also check Claude Code auto-memory
```

| Flag | Description |
|------|-------------|
| `--structural-only` | Skip the LLM-powered contradiction check (checks 1-6 only) |
| `--include-memory` | Also run `memory_lint.py` checks on Claude Code's auto-memory |

**The 7 checks:**

1. **Broken links** — wikilinks pointing to non-existent articles
2. **Orphan pages** — articles no other article links to
3. **Orphan sources** — daily logs not yet compiled
4. **Stale articles** — source log changed after article was compiled
5. **Missing backlinks** — A links to B but B doesn't link back to A
6. **Sparse articles** — fewer than 200 words
7. **Contradictions** — LLM reads all articles, flags conflicting claims (expensive)

Reports saved to `reports/lint-YYYY-MM-DD.md`.

**When to use:** wiki feels messy, or you haven't checked in a while. The session start hook reminds you if lint hasn't run in 7 days.

---

### memory_lint.py — Auto-memory health checks

Standalone script for checking Claude Code's built-in auto-memory (the `~/.claude/projects/*/memory/` files).

```bash
uv run python scripts/memory_lint.py
```

No flags. Checks:
- `MEMORY.md` broken references (index points to missing file)
- Orphan memory files (file exists but not in index)
- File count per project (warns if > 30)
- Total size per project (warns if > 100K)
- `CLAUDE.md` line count (global > 40, project > 50)

Reports saved to `reports/memory-lint-YYYY-MM-DD.md`.

---

### flush.py — Transcript to daily log

**You don't call this directly.** It's spawned by SessionEnd and PreCompact hooks.

What it does:
1. **Pass 1 (Extract):** sends transcript to Agent SDK, extracts structured sections (Context, Key Exchanges, Decisions, Lessons, Action Items)
2. **Pass 2 (Quality Audit):** second Agent SDK call filters junk — marks low-value entries with `<!-- AUDIT_FLAG -->` comments
3. Appends result to `daily/YYYY-MM-DD.md`

If nothing worth saving was found, writes `FLUSH_OK` marker instead.

---

## In-Chat Commands

Type these directly in Claude Code during a session.

### !save — Instant note

```
!save Decision: we're using PostgreSQL because SQLite can't handle concurrent writes
!save Bug: auth tokens expire silently — need refresh logic
!save Pattern: always validate webhook signatures before processing
```

- Saves text directly to today's daily log as a "Quick Save" entry
- **Blocks the prompt** — Claude never sees it (0 tokens consumed)
- Appears as a timestamped entry in the daily log
- Works with any language (UTF-8)

### /reflect — End-of-session reflection

Type `/reflect` at the end of a session. Claude asks you 4 structured questions:
1. What did you learn?
2. What surprised you?
3. What would you do differently?
4. What should you remember for next time?

Answers are saved to the daily log. This is the highest-quality capture method — human-guided, not auto-extracted.

### /compile — Compile wiki

Alias for running `compile.py`. Say `/compile` or "compile the wiki" in chat.

---

## Decision Tree

```
Want to save something right now?
  --> !save <text>

Have uncompiled daily logs?
  --> uv run python scripts/compile.py

Found an article or notes to add?
  --> Drop in raw/ --> uv run python scripts/ingest_raw.py

Want to ask your wiki a question?
  --> uv run python scripts/query.py "question"

Wiki feels messy or inconsistent?
  --> uv run python scripts/lint.py

End of work session?
  --> /reflect (or just close — auto-flush handles it)
```
