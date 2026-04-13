# MetaMode Cheatsheet

## Automatic (runs by itself)

| What | When | How |
|------|------|-----|
| **Session flush** | Claude Code session ends | Hook `SessionEnd` → `flush.py` in background |
| **Quality audit** | Right after flush | Pass 2 in `flush.py` — LLM checks quality |
| **Pre-compact backup** | Context window compacts | Hook `PreCompact` → `flush.py` |
| **Wiki injection** | Session starts | Hook `SessionStart` → `session_start.py` |
| **Auto-compile** | After flush, if past 18:00 | `flush.py` → `compile.py` in background |

## Manual Commands

### Instant save
```
!save <text>
```
Saves a note to the daily log directly from chat. Blocks the prompt (0 tokens used).

### Compile to wiki
```bash
uv run python scripts/compile.py
uv run python scripts/compile.py --all          # recompile everything
uv run python scripts/compile.py --file <path>  # one specific file
uv run python scripts/compile.py --dry-run      # show what would be compiled
```
Or in chat: `/compile`

Turns daily logs into wiki articles (`knowledge/concepts/`, `knowledge/connections/`).

### Query the knowledge base
```bash
uv run python scripts/query.py "How does X work?"
uv run python scripts/query.py "Pattern Y" --file-back  # save answer as Q&A article
```
Searches the wiki and synthesizes an answer.

### Lint
```bash
uv run python scripts/lint.py                    # all 7 checks
uv run python scripts/lint.py --structural-only  # skip LLM check (faster)
uv run python scripts/lint.py --include-memory   # also check auto-memory
```

### Process RAW inbox
```bash
uv run python scripts/ingest_raw.py
```
Or in chat: say "process RAW" / "ingest RAW"

Processes files from `raw/` → creates wiki articles, moves to `raw/processed/`.

### End-of-session reflection
In chat: `/reflect`

4 structured questions about the session → saved to daily log.

## When to Use What

| Situation | Action |
|-----------|--------|
| Learned something important right now | `!save <insight>` |
| Found an article/video for the wiki | Save to `raw/`, then run `ingest_raw.py` |
| 3+ daily logs accumulated | `uv run python scripts/compile.py` |
| Want to find something in the wiki | `uv run python scripts/query.py "question"` |
| End of work session | `/reflect` (or just close — auto-flush handles it) |
| Check wiki health | `uv run python scripts/lint.py` |

## Where Things Live

```
daily/              ← daily session logs (automatic)
knowledge/
  concepts/         ← wiki articles (after compile)
  connections/      ← cross-concept relationships
  qa/               ← Q&A articles (query --file-back)
  index.md          ← index of all articles
  log.md            ← operation changelog
raw/                ← incoming documents for processing
  processed/        ← processed files (moved here automatically)
scripts/
  state.json        ← runtime state: hashes, counters, total_cost
```

## Quality Audit

Flush automatically checks quality of extracted data (Pass 2):
- Content is useful → written to daily log as-is
- Content is junk → marked with `<!-- AUDIT_FLAG: reason -->` (data is NOT deleted)
- Flagged entries are skipped during compilation
- If audit fails with an error → content is kept (data is never lost)

## Cost Tracking

All LLM calls (compile, query, flush) accumulate cost in `scripts/state.json` → `total_cost` field.
On Max subscription the cost is $0.00, but the metric is useful if you switch to the API later.
