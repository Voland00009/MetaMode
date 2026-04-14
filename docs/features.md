🌐 **English** | [Русский](features.ru.md)

# MetaMode Features

End-to-end documentation of how MetaMode works, from session capture to wiki retrieval.

## Pipeline Overview

MetaMode has two pipelines:

1. **Conversation capture** — automatic, runs via hooks on every Claude Code session
2. **External ingestion** — manual, for articles/transcripts/notes from outside Claude Code

Both pipelines produce the same output: structured wiki articles in `knowledge/`.

---

## 1. Conversation Capture Pipeline

### Hook: SessionStart (`hooks/session_start.py`)

**When:** Every Claude Code session start, in any project (hooks are global).

**What it does:**
- Reads `knowledge/index.md` — the full wiki table of contents
- Gets last 30 lines from today's or yesterday's daily log
- Checks for uncompiled daily logs (>3 files = compile reminder)
- Checks for unprocessed files in `raw/` inbox
- Outputs JSON with `additionalContext` — Claude sees this immediately

**Size budget:** `MAX_CONTEXT_CHARS = 20,000` — truncates if wiki index gets large.

**Result:** Claude starts knowing what the wiki contains and what happened recently, without scanning files.

### Hook: SessionEnd (`hooks/session_end.py`)

**When:** Claude Code session ends (user closes, `/exit`, terminal close).

**What it does:**
- Reads JSONL transcript from Claude's transcript file
- Extracts last 30 turns as markdown (user/assistant pairs)
- Writes context to a temp file in `scripts/`
- Spawns `flush.py` as a background process (non-blocking, <1s)

**Gotchas:**
- Recursion guard: if `CLAUDE_INVOKED_BY` env var is set, exits immediately (prevents flush.py → Agent SDK → Claude Code → hook loop)
- Windows: uses `CREATE_NO_WINDOW` flag to avoid console flash
- Max context: 15,000 chars, truncated at turn boundaries

### Hook: PreCompact (`hooks/pre_compact.py`)

**When:** Claude Code is about to auto-compact (context window full).

**What it does:** Same as SessionEnd — extracts transcript and spawns flush.py. This is insurance: without it, decisions from early in a session would be lost when Claude compacts.

**Key difference:** `MIN_TURNS_TO_FLUSH = 5` (vs 1 for SessionEnd) — avoids flushing tiny compactions.

### Hook: UserPromptSubmit (`hooks/user_prompt_submit.py`)

**When:** User types `!save <text>` in Claude Code.

**What it does:**
- Parses text after `!save`
- Writes directly to today's daily log as "Quick Save" entry
- Exits with code 2 — **blocks prompt from reaching Claude** (0 tokens consumed)
- Shows confirmation via stderr

**Use case:** Capture a thought mid-session without spending tokens. Example: `!save Decision: we're using PostgreSQL for the auth service because SQLite can't handle concurrent writes`

### Script: flush.py

**When:** Spawned by SessionEnd or PreCompact hooks.

**What it does (2 passes):**

**Pass 1 — Extract:**
- Reads the temp context file
- Sends to Claude Agent SDK with a structured prompt
- Claude extracts: Context, Key Exchanges, Decisions, Lessons Learned, Action Items
- If nothing worth saving → writes `FLUSH_OK` to daily log

**Pass 2 — Quality Audit:**
- Sends extracted content to another Agent SDK call
- Checks: is this worth keeping? (not just "we did X, then Y")
- Conservative: when in doubt, keeps the content
- If flagged: wraps content in `<!-- AUDIT_FLAG: reason -->` HTML comment
- Flagged entries stay in daily log but are skipped during compilation

**After both passes:**
- Writes to `daily/YYYY-MM-DD.md` with timestamp
- Dedup: skips if same session flushed within 60 seconds
- Checks if auto-compile should trigger (after 18:00, if logs changed)

### Script: compile.py

**When:** Manual (`uv run python scripts/compile.py`) or auto-triggered by flush.py after 18:00.

**What it does:**
- Reads daily logs that haven't been compiled (hash comparison)
- Sends each log + AGENTS.md schema + existing wiki to Agent SDK
- Agent SDK creates/updates wiki articles: concepts, connections, index, log
- Has file-level tools: Read, Write, Edit, Glob, Grep (up to 30 turns)
- Skips audit-flagged entries
- Tracks compilation state in `state.json`

**Options:**
- `--all` — force recompile everything
- `--file daily/2026-04-11.md` — compile specific file
- `--dry-run` — show what would be compiled

---

## 2. External Ingestion Pipeline

### Script: ingest_raw.py

**When:** Manual (`uv run python scripts/ingest_raw.py`) or when user says "обработай RAW".

**Input:** `.md` or `.txt` files dropped into `raw/` directory.

**What it does:**
- Same approach as compile.py but for external documents
- Agent SDK reads the document + schema + existing wiki
- Creates wiki articles, updates index
- Moves processed files to `raw/processed/`

**Use case:** Feed in article summaries, meeting transcripts, research notes — anything from outside Claude Code sessions.

---

## 3. Wiki Structure

### knowledge/index.md
Master navigation. Every article has one row:
```
| [[concepts/slug]] | One-line summary | source-file | date |
```
Claude reads this first to navigate the wiki.

### knowledge/concepts/
Atomic knowledge articles. Each has:
- YAML frontmatter (title, aliases, tags, category, sources, dates)
- Context → Problem → Lesson structure
- Key Points, Details, Related Concepts sections
- Wikilinks to other articles

### knowledge/connections/
Cross-concept relationship articles. For non-obvious connections between 2+ concepts.

### knowledge/qa/
Saved answers from `query.py --file-back`. Question + synthesized answer + sources.

### knowledge/log.md
Timestamped changelog of all compile/ingest/lint operations.

---

## 4. Health Checks

### Script: lint.py

7 checks:
1. **Broken links** — wikilinks pointing to non-existent articles
2. **Orphan pages** — articles no other article links to
3. **Orphan sources** — daily logs not yet compiled
4. **Stale articles** — source log changed after compilation
5. **Missing backlinks** — A links to B but B doesn't link back
6. **Sparse articles** — fewer than 200 words
7. **Contradictions** — LLM reads all articles, finds conflicting claims (expensive)

Use `--structural-only` to skip the LLM contradiction check.

Reports saved to `reports/lint-YYYY-MM-DD.md`.

---

## 5. Query Interface

### Script: query.py

CLI access to the wiki without opening Claude Code.

```bash
uv run python scripts/query.py "How should I handle auth?"
uv run python scripts/query.py "What patterns do I use?" --file-back
```

With `--file-back`: saves the answer as a Q&A article in `knowledge/qa/`.

---

## Tips and Gotchas

### Flush dedup
If you close and reopen Claude Code quickly, the same session might trigger flush twice. `flush.py` deduplicates by session ID + 60-second window.

### Audit flags
Audit-flagged entries (HTML comments in daily logs) are never deleted — they stay for manual review. Compile skips them. If you want to include a flagged entry, remove the HTML comment manually.

### Cost tracking
`scripts/state.json` tracks `total_cost` from Agent SDK calls. On Max subscription this is $0, but the counter is useful for monitoring usage.

### Windows quirks
- `CREATE_NO_WINDOW` flag prevents console flash when spawning background processes
- `sys.stdin.reconfigure(encoding="utf-8")` in hooks — Windows defaults to cp1251
- JSON parsing has a fallback for unescaped backslashes in Windows paths

### Daily log format
Daily logs are immutable — flush appends, never modifies. Each entry has a `### Section (HH:MM)` header. This makes git diffs clean and compilation idempotent.

### Compile timing
Auto-trigger fires only after 18:00 (configurable via `COMPILE_AFTER_HOUR` in flush.py). Before that, compile manually when you want fresh wiki articles.
