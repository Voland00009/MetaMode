# MetaMode

Persistent wiki-memory layer for Claude Code. Fork of [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) with extensions.

Claude Code forgets everything between sessions. MetaMode captures conversations automatically, compiles them into structured wiki articles, and injects context at session start. Result: Claude starts every session knowing what happened before.

## How it works

```
Session End / Pre-Compact
    → hooks extract transcript
    → flush.py summarizes via Agent SDK
    → quality audit filters junk
    → daily log entry written

Session Start
    → hook injects wiki index + recent log
    → Claude has full context in <5 seconds

Compile (manual or auto after 18:00)
    → daily logs → structured wiki articles
    → index.md updated

RAW Inbox
    → drop external docs into raw/
    → ingest_raw.py → wiki articles
```

## Setup

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Claude Code with Max subscription

```bash
git clone <this-repo> ~/Dev/MetaMode
cd MetaMode
uv sync
```

Hooks are configured globally in `~/.claude/settings.json` — they fire from any project:

```json
{
  "hooks": {
    "SessionStart": [{"type": "command", "command": "uv run --directory C:/Users/Voland/Dev/MetaMode python hooks/session_start.py"}],
    "SessionEnd": [{"type": "command", "command": "uv run --directory C:/Users/Voland/Dev/MetaMode python hooks/session-end.py"}],
    "PreCompact": [{"type": "command", "command": "uv run --directory C:/Users/Voland/Dev/MetaMode python hooks/pre-compact.py"}],
    "UserPromptSubmit": [{"type": "command", "command": "uv run --directory C:/Users/Voland/Dev/MetaMode python hooks/user_prompt_submit.py"}]
  }
}
```

## Usage

**Automatic** — just use Claude Code. Hooks capture sessions automatically.

**Quick save** — type `!save <text>` in Claude Code to save a note instantly (0 tokens).

**Compile** — `uv run python scripts/compile.py` (or wait for auto-trigger after 18:00)

**Query wiki** — `uv run python scripts/query.py "your question"` (add `--file-back` to save the answer)

**Ingest external docs** — drop `.md`/`.txt` into `raw/`, then `uv run python scripts/ingest_raw.py`

**Lint** — `uv run python scripts/lint.py` (7 structural checks + LLM contradiction detection)

## Project structure

```
MetaMode/
├── hooks/              # Claude Code lifecycle hooks
│   ├── session_start.py    # Injects context at start
│   ├─�� session-end.py      # Captures transcript on exit
│   ├── pre-compact.py      # Captures before auto-compaction
│   └── user_prompt_submit.py  # !save interceptor
├── scripts/            # Core pipeline
│   ├── flush.py            # Transcript → daily log (Agent SDK)
│   ├── compile.py          # Daily logs → wiki articles
│   ├── ingest_raw.py       # External docs → wiki articles
│   ├── lint.py             # 7 health checks
│   ├── query.py            # CLI wiki queries
│   ├── config.py           # Paths and constants
│   └── utils.py            # Shared utilities
├── daily/              # Raw daily logs (immutable)
├── knowledge/          # Compiled wiki
│   ├── index.md            # Master navigation
│   ├── log.md              # Changelog
│   ├── concepts/           # Atomic knowledge articles
│   ├── connections/        # Cross-concept relationships
│   └── qa/                 # Saved Q&A answers
├── raw/                # External document inbox
├── input/              # Reference materials (not processed)
├── AGENTS.md           # Wiki article schema
└── CLAUDE.md           # Project instructions
```

## Key differences from coleam00

1. **Agent SDK** instead of `claude -p` subprocess — cleaner, same $0 cost on Max
2. **Quality audit** — LLM Pass 2 in flush.py filters junk before it reaches daily logs
3. **`!save` hook** — instant capture, blocks prompt from reaching Claude (0 tokens)
4. **RAW inbox** — `ingest_raw.py` processes external documents alongside conversation capture
5. **Cost tracking** — `state.json` accumulates total Agent SDK cost
6. **Auto compile trigger** — flush.py spawns compile.py after 18:00 if logs changed
7. **Article categorization** — tags and category fields in AGENTS.md schema

## Cost

$0/month beyond Claude Max subscription. All Agent SDK calls are covered by Max.

## Stack

Python, uv, Claude Agent SDK, Obsidian (optional — for browsing wiki with graph view)
