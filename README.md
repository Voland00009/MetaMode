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

**Timezone** — by default MetaMode uses the system timezone. To override, set `METAMODE_TIMEZONE`:

```bash
export METAMODE_TIMEZONE=Europe/Moscow  # or America/New_York, Asia/Tokyo, etc.
```

Hooks are configured globally in `~/.claude/settings.json` — they fire from any project:

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "uv run --directory /FULL/PATH/TO/MetaMode python hooks/session_start.py", "timeout": 10 }
      ]}
    ],
    "SessionEnd": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "uv run --directory /FULL/PATH/TO/MetaMode python hooks/session_end.py", "timeout": 10 }
      ]}
    ],
    "PreCompact": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "uv run --directory /FULL/PATH/TO/MetaMode python hooks/pre_compact.py", "timeout": 10 }
      ]}
    ],
    "UserPromptSubmit": [
      { "matcher": "^!save", "hooks": [
        { "type": "command", "command": "uv run --directory /FULL/PATH/TO/MetaMode python hooks/user_prompt_submit.py", "timeout": 5 }
      ]}
    ]
  }
}
```

> Replace `/FULL/PATH/TO/MetaMode` with your actual clone path (e.g., `~/Dev/MetaMode` on macOS/Linux, `C:/Users/you/Dev/MetaMode` on Windows).
>
> `matcher: ""` means the hook fires for all projects. `UserPromptSubmit` uses `"^!save"` to only trigger on `!save` commands.

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
│   ├── session_end.py      # Captures transcript on exit
│   ├── pre_compact.py      # Captures before auto-compaction
│   ├── user_prompt_submit.py  # !save interceptor
│   └── shared.py           # Common utilities for hooks
├── scripts/            # Core pipeline
│   ├── flush.py            # Transcript → daily log (Agent SDK)
│   ├── compile.py          # Daily logs → wiki articles
│   ├── ingest_raw.py       # External docs → wiki articles
│   ├── lint.py             # 7 health checks
│   ├── memory_lint.py      # Auto-memory health checks
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

## Integrations

MetaMode connects with external tools to capture, browse, and review your knowledge. See [Ecosystem overview](docs/ecosystem.md) for how everything fits together.

- **[Obsidian](docs/obsidian-setup.md)** — browse wiki with graph view, search, and backlinks
- **[Web Clipper](docs/web-clipper-setup.md)** — save web pages into Claude's memory with one click
- **[NotebookLM](docs/notebooklm-setup.md)** — generate audio overviews and chat with your knowledge base
- **[RAW Inbox](docs/raw-inbox.md)** — ingest external documents (articles, notes, transcripts) into the wiki

## Skills

MetaMode includes optional Claude Code skills in `skills/`. To install:

```bash
# Copy to your global skills directory
cp -r skills/* ~/.claude/SKILLS/
```

Available skills:

- **wrapup** — end-of-session summary, saves key memories
- **notebooklm** — interact with NotebookLM from Claude Code (create notebooks, add sources, generate audio)

> Skills in the repo are clean templates. After copying, customize them locally (e.g., add environment-specific auth or paths). Local changes won't affect the repo.

## Maintenance

MetaMode reminds you about pending maintenance at session start:

- **Compile** — when 3+ daily logs are uncompiled, you'll see a reminder
- **Wiki lint** — if `scripts/lint.py` hasn't run in 7+ days
- **Memory lint** — if `scripts/memory_lint.py` hasn't run in 14+ days
- **RAW inbox** — when unprocessed files are waiting in `raw/`

Run lint manually: `uv run python scripts/lint.py`

## Cost

$0/month beyond Claude Max subscription. All Agent SDK calls are covered by Max.

## Stack

Python, uv, Claude Agent SDK, Obsidian (optional — for browsing wiki with graph view)
