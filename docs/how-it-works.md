🌐 **English** | [Русский](how-it-works.ru.md)

# How It Works

Deep dive into MetaMode's pipeline, architecture, and design decisions.

---

## Overview

MetaMode has two input pipelines (session capture + external ingestion) and one output pipeline (wiki compilation). Everything flows through daily logs as the intermediate format.

```
                   ┌──────────────────────────┐
                   │     Input Pipelines       │
                   ├──────────────────────────┤
                   │                          │
  ┌────────────┐   │   ┌──────────┐           │
  │ Session    │───┼──▶│ flush.py │──┐        │   ┌─────────────┐
  │ End/Compact│   │   └──────────┘  │        │   │  Daily Logs  │
  └────────────┘   │                 ├────────┼──▶│  daily/*.md  │
  ┌────────────┐   │   ┌──────────┐  │        │   └──────┬──────┘
  │ !save      │───┼──▶│ direct   │──┘        │          │
  └────────────┘   │   │ write    │           │          │
  ┌────────────┐   │   └──────────┘           │          ▼
  │ RAW inbox  │───┼─────────────────────────────▶┌─────────────┐
  └────────────┘   │                          │   │ compile.py  │
                   └──────────────────────────┘   └──────┬──────┘
                                                         │
                   ┌──────────────────────────┐          ▼
                   │     Output Pipeline       │   ┌─────────────┐
                   ├──────────────────────────┤   │ Wiki         │
  ┌────────────┐   │   ┌──────────────┐       │   │ knowledge/   │
  │ Next       │◀──┼───│session_start │◀──────┼───│ index.md     │
  │ Session    │   │   │.py           │       │   └─────────────┘
  └────────────┘   │   └──────────────┘       │
                   └──────────────────────────┘
```

---

## 1. Session Capture Pipeline

This is the core loop — fully automatic after [setup](setup.md).

### Step 1: Hook fires

When a Claude Code session ends (or context compacts), the `SessionEnd` / `PreCompact` hook:

1. Reads the JSONL transcript from Claude's transcript file path (provided via stdin)
2. Extracts the last 30 turns as markdown (user/assistant pairs)
3. Truncates to 15,000 characters at turn boundaries — no mid-sentence cuts
4. Writes the context to a temp file: `scripts/session-flush-<session_id>-<timestamp>.md`
5. Spawns `flush.py` as a **background process** and exits immediately

The hook itself does **zero API calls** — only local file I/O. It completes in under 1 second.

**Recursion guard:** if `CLAUDE_INVOKED_BY` environment variable is set (meaning Agent SDK spawned this Claude instance), the hook exits immediately. Without this, flush.py would trigger Claude Code → which would fire SessionEnd → which would spawn flush.py → infinite loop.

**Minimum turns:** `SessionEnd` requires at least 1 turn. `PreCompact` requires 5 turns — avoiding flushes of tiny compactions.

### Step 2: Extract (flush.py Pass 1)

`flush.py` reads the temp context file and sends it to Claude Agent SDK with a structured extraction prompt:

```
Extract from this conversation:
- Context (what the user was working on)
- Key Exchanges (important Q&A)
- Decisions Made (with rationale)
- Lessons Learned (gotchas, patterns)
- Action Items (follow-ups)
```

If nothing worth saving is found, Claude responds with `FLUSH_OK` — a marker that gets written to the daily log so you can see the session was processed.

### Step 3: Quality Audit (flush.py Pass 2)

The extracted content goes through a second Agent SDK call — the quality audit:

```
Is this content WORTH KEEPING in a daily log?
Mark as LOW quality only if ALL are true:
1. No concrete lessons (just "we did X, then Y")
2. No decisions with rationale
3. No reusable patterns or gotchas
4. Only routine operations
```

The audit is **conservative** — when in doubt, it keeps the content. This is by design: losing a good entry is worse than keeping a mediocre one.

**If audit flags the content:** it wraps it in an HTML comment:
```
<!-- AUDIT_FLAG: only routine file operations -->
Content here...
```

Flagged entries stay in the daily log (never deleted) but are **skipped during compilation**. You can review and remove the flag manually if you disagree.

**If audit fails (error):** the content is kept as-is. The system never loses data due to audit failures.

### Step 4: Write to daily log

The result is appended to `daily/YYYY-MM-DD.md` with a timestamped section header:

```markdown
### Session a1b2c3d4 (14:32)

**Context:** User was implementing auth middleware...

**Key Exchanges:**
- ...
```

Daily logs are **append-only** — flush never modifies existing entries. This keeps git diffs clean and makes compilation idempotent.

### Step 5: Dedup and auto-compile

- **Dedup:** if the same session ID was flushed within the last 60 seconds, the second flush is skipped. This handles the case where SessionEnd and PreCompact fire close together.
- **Auto-compile:** if it's after 18:00 (configurable via `COMPILE_AFTER_HOUR`) and today's daily log has changed since last compilation, `flush.py` spawns `compile.py` in the background.

---

## 2. Compilation Pipeline

Turns daily logs into structured wiki articles.

### How compile.py works

1. **Find uncompiled logs:** compares file hashes against `state.json` — only processes logs that changed since last compilation
2. **Read context:** loads the daily log + `AGENTS.md` (wiki article schema) + existing wiki index
3. **Send to Agent SDK:** Claude gets file-level tools (Read, Write, Edit, Glob, Grep) and up to 30 turns to create/update articles
4. **Output:** creates or updates files in `knowledge/concepts/`, `knowledge/connections/`, updates `knowledge/index.md` and `knowledge/log.md`
5. **Track state:** saves file hashes to `state.json` so unchanged logs aren't recompiled

### What the Agent produces

- **Concept articles** — atomic knowledge with YAML frontmatter (title, aliases, tags, category, sources, dates), structured as Context → Problem → Lesson
- **Connection articles** — cross-concept relationships showing how two or more ideas relate
- **Index updates** — one row per article in `knowledge/index.md`
- **Changelog entries** — timestamped operations in `knowledge/log.md`

### Audit-flagged content

Entries wrapped in `<!-- AUDIT_FLAG: ... -->` are invisible to the compiler. It only processes clean, unflagged content.

---

## 3. External Ingestion

For content from outside Claude Code sessions — articles, meeting notes, research.

1. Drop `.md` or `.txt` files into the `raw/` directory
2. Run `uv run python scripts/ingest_raw.py`
3. Same Agent SDK pipeline as compilation — reads the document + schema + existing wiki
4. Creates wiki articles, updates index
5. Moves processed files to `raw/processed/`

The RAW inbox format is intentionally simple:
```markdown
# Title
## Context
## Key Insight
## Example (optional)
```

---

## 4. Context Injection

At the start of every Claude Code session, `session_start.py` runs and outputs JSON that Claude sees immediately:

```json
{
  "additionalContext": "## Knowledge Base Index\n...\n## Recent Daily Log\n..."
}
```

### What gets injected

1. **Full wiki index** — the entire `knowledge/index.md` table (every article, one line each)
2. **Recent daily log** — last 30 lines from today's or yesterday's log
3. **Compile reminder** — if 3+ daily logs are uncompiled or 3+ days since last compile
4. **RAW inbox alert** — if unprocessed files are sitting in `raw/`
5. **Lint reminder** — if wiki lint hasn't run in 7 days or memory lint in 14 days

### Size budget

Total injected context is capped at **20,000 characters** (`MAX_CONTEXT_CHARS`). If the wiki index grows beyond this, it's truncated. For reference, 20K chars is roughly 5K tokens — a small fraction of Claude's context window.

---

## 5. Quality Audit — Why It Exists

### The problem

Early experiments with fully automatic memory capture (similar to [mem0](https://github.com/mem0ai/mem0)) showed that **~95% of auto-captured content was junk** — routine operations, trivial exchanges, content that adds no value to a knowledge base.

Without filtering, the wiki fills up with noise. Compilation produces low-quality articles. Context injection wastes tokens on useless information.

### The solution

A two-pass LLM pipeline:

1. **Pass 1 (Extract):** pulls out structured sections from the raw transcript
2. **Pass 2 (Audit):** a separate LLM call checks whether the extracted content meets minimum quality thresholds

This is the [two-pass LLM quality audit pattern](https://en.wikipedia.org/wiki/Extract,_transform,_load) — extract first, then audit. The second pass catches what the first misses because it operates on clean, structured text rather than raw conversation.

### Design principles

- **Conservative:** when in doubt, keep the content. False negatives (losing good content) are worse than false positives (keeping mediocre content)
- **Non-destructive:** flagged content is never deleted, only wrapped in HTML comments
- **Fail-open:** if the audit LLM call fails, content is kept as-is
- **Human override:** remove the `<!-- AUDIT_FLAG: ... -->` comment to un-flag content

---

## 6. Wiki Structure

### knowledge/index.md — Master navigation

Every article has one row:
```
| [[concepts/slug]] | One-line summary | source-file | date |
```

Claude reads this first at session start to know what's in the wiki. It's the table of contents.

### knowledge/concepts/ — Atomic knowledge

Each article has:
- **YAML frontmatter:** title, aliases, tags, category, sources, created/updated dates
- **Body:** Context → Problem → Lesson structure
- **Sections:** Key Points, Details, Related Concepts
- **Links:** wikilinks to related articles (`[[concepts/other-slug]]`)

### knowledge/connections/ — Cross-concept relationships

For non-obvious relationships between 2+ concepts. Example: "duck typing and import binding are both Python permissiveness bugs where wrong data flows silently."

### knowledge/qa/ — Saved query answers

Created by `query.py --file-back`. Contains the question, synthesized answer, and source articles.

### knowledge/log.md — Operation changelog

Timestamped log of every compile, ingest, and lint operation. Useful for debugging ("when was this article last updated?").

---

## 7. Health Checks

`lint.py` runs 7 checks on the wiki:

| # | Check | What it catches |
|---|-------|----------------|
| 1 | **Broken links** | `[[concepts/foo]]` but `foo.md` doesn't exist |
| 2 | **Orphan pages** | Article exists but nothing links to it |
| 3 | **Orphan sources** | Daily log was never compiled into articles |
| 4 | **Stale articles** | Source daily log changed after article was compiled |
| 5 | **Missing backlinks** | A links to B, but B doesn't link back to A |
| 6 | **Sparse articles** | Fewer than 200 words — probably incomplete |
| 7 | **Contradictions** | LLM reads all articles and finds conflicting claims |

Checks 1-6 are structural (fast, no API calls). Check 7 uses Agent SDK and is expensive — skip it with `--structural-only`.

Reports go to `reports/lint-YYYY-MM-DD.md`. The session start hook reminds you if lint hasn't run in 7 days.

---

## 8. Hooks Lifecycle

### Configuration

Hooks live in `~/.claude/settings.json` — global config that fires for every Claude Code session, in every project. See [setup.md](setup.md) for the full configuration block.

### Execution flow

```
Claude Code session starts
  └─▶ SessionStart hook → session_start.py → JSON to stdout → Claude sees wiki context

User works normally...

Claude Code context compacts (window full)
  └─▶ PreCompact hook → pre_compact.py → extract transcript → spawn flush.py
        └─▶ flush.py (background): extract → audit → daily log

User closes session
  └─▶ SessionEnd hook → session_end.py → extract transcript → spawn flush.py
        └─▶ flush.py (background): extract → audit → daily log
              └─▶ maybe_trigger_compilation() → spawn compile.py (after 18:00)

User types "!save important note"
  └─▶ UserPromptSubmit hook → user_prompt_submit.py → write to daily log → exit(2)
       (exit code 2 = block prompt from reaching Claude)
```

### Key safety mechanisms

- **Recursion guard:** `CLAUDE_INVOKED_BY` environment variable prevents hooks from firing when Agent SDK spawns Claude
- **Flush dedup:** same session ID + 60-second window = skip second flush
- **Non-blocking:** hooks spawn background processes and exit immediately — no delay to the user
- **Fail-safe:** hook errors are logged to `scripts/flush.log` but never surface to the user or block Claude Code

### Windows quirks

- `subprocess.CREATE_NO_WINDOW` flag prevents console windows from flashing when spawning background processes
- `sys.stdin.reconfigure(encoding="utf-8")` in hooks — Windows defaults to cp1251/cp1252 encoding
- JSON parsing includes a fallback for unescaped backslashes in Windows paths

## Cost tracking

MetaMode runs every LLM call through the Claude Agent SDK, which uses your Claude Max subscription. You are not billed per token. Max covers all usage.

So why does `scripts/state.json` accumulate a `total_cost` field?

After every Agent SDK call, the final `ResultMessage` carries a `total_cost_usd` value — the SDK's own **API-equivalent** estimate of what that call would have cost at per-token API rates. MetaMode sums these into `state["total_cost"]` (see `_accumulate_cost` in [`scripts/flush.py`](../scripts/flush.py); `compile.py`, `query.py`, and `ingest_raw.py` do the same inline). The figure is informational — what these calls *would* cost without a Max subscription.

Use cases:

- **Sanity check** — catches runaway loops (e.g. `compile.py` stuck re-processing the same day)
- **Capacity planning** — if you ever migrate off Max, this is your projected monthly bill
- **Curiosity** — see what Max is saving you

**Resetting**: delete `scripts/state.json`. The next hook run recreates it from zero. Daily logs and wiki articles are not affected.

**Disabling**: there is no flag — the field is always written. To stop tracking, remove the `state["total_cost"] += ...` lines (four call sites across `flush.py`, `compile.py`, `query.py`, `ingest_raw.py`).
