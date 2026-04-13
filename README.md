🌐 **English** | [Русский](README.ru.md)

# MetaMode

**Persistent wiki-memory for Claude Code.** Sessions captured automatically, compiled into structured wiki articles, injected at session start. Claude remembers.

![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Cost $0/mo](https://img.shields.io/badge/cost-%240%2Fmo-brightgreen)

Fork of [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) with quality audit, instant save, RAW inbox, and Agent SDK integration.

---

## The Problem

Claude Code forgets everything between sessions. Every new conversation starts from zero — you re-explain your stack, repeat past decisions, and lose the lessons you already learned. The built-in auto-memory helps, but it's shallow: it stores facts, not structured knowledge.

## The Solution

MetaMode captures your sessions automatically via hooks, extracts the important parts, filters out noise with a quality audit, and compiles everything into a structured wiki. At the start of each session, it injects the wiki index and recent context — so Claude starts knowing what happened before.

## How It Works

```
┌─────────────────┐     ┌───────────┐     ┌───────────┐     ┌───────────────┐
│  You use         │────▶│  Hooks    │────▶│ flush.py  │────▶│  Daily Log    │
│  Claude Code     │     │  capture  │     │ extract + │     │  (append)     │
└─────────────────┘     │  session  │     │ audit     │     └───────┬───────┘
                        └───────────┘     └───────────┘             │
                                                                    ▼
┌─────────────────┐     ┌───────────┐     ┌─────────────────────────┐
│  Next session    │◀────│  Inject   │◀────│  Wiki Articles          │
│  has context     │     │  at start │     │  (compile.py)           │
└─────────────────┘     └───────────┘     └─────────────────────────┘
```

**Session end** → hooks extract the transcript → `flush.py` summarizes via Agent SDK → quality audit filters junk → daily log entry written.

**Session start** → hook reads wiki index + recent daily log → Claude sees it immediately.

**Compile** → daily logs → structured wiki articles with cross-references.

## Before & After

| Without MetaMode | With MetaMode |
|---|---|
| "What framework are we using again?" | Claude already knows your stack |
| "Remember that auth decision from last week?" | Decision is in the wiki, injected at start |
| "We tried X before and it didn't work because..." | Lesson captured, Claude won't repeat the mistake |
| Session starts blank every time | Session starts with full context in <5 seconds |

## Quick Start

```bash
git clone https://github.com/Voland00009/MetaMode.git ~/Dev/MetaMode
cd MetaMode && uv sync
```

Then configure hooks in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{"type": "command", "command": "uv run --directory ~/Dev/MetaMode python hooks/session_start.py"}],
    "SessionEnd": [{"type": "command", "command": "uv run --directory ~/Dev/MetaMode python hooks/session_end.py"}],
    "PreCompact": [{"type": "command", "command": "uv run --directory ~/Dev/MetaMode python hooks/pre_compact.py"}],
    "UserPromptSubmit": [{"type": "command", "command": "uv run --directory ~/Dev/MetaMode python hooks/user_prompt_submit.py"}]
  }
}
```

> Replace `~/Dev/MetaMode` with your actual clone path. On Windows: `C:/Users/YOU/Dev/MetaMode`

See [docs/setup.md](docs/setup.md) for full installation instructions with verification steps and troubleshooting.

## What You Get

| Tool | What it does | How |
|------|-------------|-----|
| **Auto-capture** | Sessions saved automatically | Hooks fire on session end/compact |
| **`!save <text>`** | Instant note, 0 tokens | Type in chat — blocks prompt, saves directly |
| **compile.py** | Daily logs → wiki articles | `uv run python scripts/compile.py` |
| **query.py** | Ask your wiki from CLI | `uv run python scripts/query.py "question"` |
| **ingest_raw.py** | External docs → wiki | Drop in `raw/`, then run script |
| **lint.py** | 7 health checks | `uv run python scripts/lint.py` |
| **`/reflect`** | End-of-session reflection | 4 structured questions → daily log |

## Key Features (vs coleam00 original)

1. **Agent SDK** instead of `claude -p` subprocess — cleaner API, no CLI argument length limits, same $0 cost on Max subscription
2. **Quality audit** — two-pass LLM pipeline in `flush.py`: Pass 1 extracts, Pass 2 filters junk before it reaches daily logs
3. **`!save` hook** — type `!save <text>` in Claude Code to capture a thought instantly; blocks the prompt (0 tokens consumed)
4. **RAW inbox** — `ingest_raw.py` processes external documents (articles, meeting notes, research) alongside conversation capture
5. **Cost tracking** — `scripts/state.json` accumulates total Agent SDK cost across all operations
6. **Auto compile trigger** — `flush.py` spawns `compile.py` automatically after 18:00 if daily logs changed
7. **Article categorization** — tags and category fields in the wiki article schema for structured knowledge organization

## Project Structure

```
MetaMode/
├── hooks/                  # Claude Code lifecycle hooks
│   ├── session_start.py        # Injects wiki context at session start
│   ├── session_end.py          # Captures transcript on session close
│   ├── pre_compact.py          # Captures before context compaction
│   ├── user_prompt_submit.py   # !save interceptor
│   └── shared.py               # Common utilities for hooks
├── scripts/                # Core pipeline
│   ├── flush.py                # Transcript → daily log (2-pass with audit)
│   ├── compile.py              # Daily logs → wiki articles
│   ├── ingest_raw.py           # External docs → wiki articles
│   ├── lint.py                 # 7 structural + LLM health checks
│   ├── memory_lint.py          # Claude Code auto-memory health checks
│   ├── query.py                # CLI wiki query interface
│   ├── config.py               # Paths and constants
│   └── utils.py                # Shared utilities
├── daily/                  # Daily session logs (immutable, append-only)
├── knowledge/              # Compiled wiki
│   ├── index.md                # Master navigation table
│   ├── log.md                  # Operation changelog
│   ├── concepts/               # Atomic knowledge articles
│   ├── connections/            # Cross-concept relationships
│   └── qa/                     # Saved Q&A answers
├── raw/                    # External document inbox
├── reports/                # Lint reports
├── AGENTS.md               # Wiki article schema for Agent SDK
├── CLAUDE.md               # Project instructions for Claude Code
└── pyproject.toml          # Python dependencies
```

## Cost

**$0/month** — all LLM calls go through Claude Agent SDK, which is included in the Claude Max subscription. No API keys, no usage-based billing.

## Documentation

- **[Setup Guide](docs/setup.md)** — step-by-step installation (cross-platform)
- **[Command Reference](docs/commands.md)** — every command with flags, examples, and decision tree
- **[How It Works](docs/how-it-works.md)** — deep dive into the pipeline and architecture
- **[Cheatsheet](docs/cheatsheet.md)** — quick reference card
- **[Cross-Project Template](docs/cross-project-template.md)** — give other projects read access to your wiki

> 📖 **Документация на русском:** [README](README.ru.md) ・ [Установка](docs/setup.ru.md) ・ [Команды](docs/commands.ru.md) ・ [Как это работает](docs/how-it-works.ru.md) ・ [Шпаргалка](docs/cheatsheet.ru.md)

## Contributing

Contributions welcome! This is a personal tool that grew useful enough to share. If you find bugs, have ideas, or want to improve the docs — open an issue or PR.

## Acknowledgments

MetaMode is a fork of [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) by Cole Medin, adapted from [Andrej Karpathy's LLM Knowledge Base](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) architecture. Thank you both for the foundational work.

## License

[MIT](LICENSE)
