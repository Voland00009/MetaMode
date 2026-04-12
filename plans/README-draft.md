# MetaMode

**Wiki-memory for Claude Code — your sessions compile into a searchable knowledge base.**

Based on [Karpathy's LLM wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), forked from [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) with 5 additions on top.

## The Problem

Every new Claude Code session starts from scratch. Claude re-scans your project, asks the same questions, and burns tokens rediscovering what it knew yesterday. CLAUDE.md helps, but it's static and limited.

## The Solution

MetaMode automatically captures knowledge from your sessions, compiles it into a structured wiki, and injects it into every future session. Claude opens your project and already knows your architecture, decisions, gotchas, and lessons learned.

```
Session ends → hook captures transcript → LLM extracts knowledge → pending review
You approve → daily log → compiler → wiki articles (concepts, connections, Q&A)
Next session starts → hook injects wiki index → Claude remembers everything
```

## What's Different from coleam00

MetaMode shares the same core (Claude Agent SDK, $0/mo on Max) and adds 5 things:

| Feature | coleam00 (original) | MetaMode |
|---------|---------------------|----------|
| Quality control | Auto-saves everything | Pending review: you approve before saving |
| External data | Conversations only | + RAW inbox for articles, transcripts, notes |
| Quick capture | None | `!save <text>` during any session |
| Scope | Per-project hooks | Global hooks (one wiki for all projects) |
| Session context | Index + recent log | + pending review + compile reminder + RAW reminder |

**Choose coleam00 if** you want per-project isolation or zero-config setup.
**Choose MetaMode if** you want quality control, external data support, and one wiki across all projects.

## Quick Start

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with Max subscription
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Obsidian](https://obsidian.md/) (optional, for browsing the wiki as a graph)

### Install (5 minutes)

**1. Clone and install dependencies:**

```bash
git clone https://github.com/YOUR_USERNAME/MetaMode.git
cd MetaMode
uv sync
```

**2. Add hooks to your global Claude settings:**

Edit `~/.claude/settings.json` (create if it doesn't exist):

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "uv run --directory /FULL/PATH/TO/MetaMode python hooks/session_start.py",
        "timeout": 10
      }]
    }],
    "SessionEnd": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "uv run --directory /FULL/PATH/TO/MetaMode python hooks/session-end.py",
        "timeout": 10
      }]
    }],
    "PreCompact": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "uv run --directory /FULL/PATH/TO/MetaMode python hooks/pre-compact.py",
        "timeout": 10
      }]
    }],
    "UserPromptSubmit": [{
      "matcher": "^!save",
      "hooks": [{
        "type": "command",
        "command": "uv run --directory /FULL/PATH/TO/MetaMode python hooks/user_prompt_submit.py",
        "timeout": 5
      }]
    }]
  }
}
```

Replace `/FULL/PATH/TO/MetaMode` with the actual path (e.g., `C:/Users/you/Dev/MetaMode` on Windows, `/home/you/Dev/MetaMode` on Linux/Mac).

**3. Open any project in Claude Code.** The hooks activate automatically.

**4. (Optional) Open MetaMode folder in Obsidian** for graph view of your knowledge base.

### Verify it works

```bash
# Check session start hook outputs JSON
cd /path/to/MetaMode
uv run python hooks/session_start.py

# Run structural health checks (free, no LLM calls)
uv run python scripts/lint.py --structural-only

# Ask your wiki a question (uses LLM)
uv run python scripts/query.py "What do I know about testing patterns?"
```

## Project Structure

```
MetaMode/
├── hooks/                      # Claude Code hooks (auto-fire on events)
│   ├── session_start.py        # Injects wiki index at session start
│   ├── session-end.py          # Captures transcript → flush → daily log
│   ├── pre-compact.py          # Safety net before context compaction
│   └── user_prompt_submit.py   # !save quick-capture interceptor
├── scripts/                    # Core scripts
│   ├── flush.py                # Extracts knowledge from conversations
│   ├── compile.py              # Compiles daily logs → wiki articles
│   ├── query.py                # Ask questions to your wiki
│   ├── lint.py                 # 7 health checks for wiki quality
│   ├── ingest_raw.py           # Process external docs from raw/
│   ├── config.py               # Path constants
│   └── utils.py                # Shared helpers
├── daily/                      # Conversation logs (auto-generated)
├── knowledge/                  # Compiled wiki (LLM-generated)
│   ├── index.md                # Master index (the retrieval mechanism)
│   ├── log.md                  # Build log
│   ├── concepts/               # Atomic knowledge articles
│   ├── connections/            # Cross-cutting insights
│   └── qa/                     # Saved query answers
├── raw/                        # External data inbox (articles, transcripts)
│   └── processed/              # Processed raw files (auto-moved)
├── reports/                    # Lint reports
├── AGENTS.md                   # Wiki schema (article format spec)
└── CLAUDE.md                   # Project instructions
```

## Daily Workflow

### Automatic (zero effort)

1. **Work normally** in any project with Claude Code
2. **Close session** → hook captures transcript → flush extracts knowledge → saves to pending review
3. **Next session** → hook shows pending items → approve/reject/edit
4. **After 6 PM** → compiler auto-runs → daily logs become wiki articles

### Manual commands

```bash
# Quick-save during a session (0 tokens)
!save Important: always run migrations before deploying

# Compile daily logs into wiki articles
uv run python scripts/compile.py

# Ask your wiki a question
uv run python scripts/query.py "What auth patterns do I use?"

# Ask + save the answer back into the wiki
uv run python scripts/query.py "How do I handle errors?" --file-back

# Run health checks
uv run python scripts/lint.py                    # all checks (LLM cost)
uv run python scripts/lint.py --structural-only  # free checks only

# Process external articles from raw/
uv run python scripts/ingest_raw.py
```

### Adding external knowledge

1. Drop a markdown or text file into `raw/`
2. Run `uv run python scripts/ingest_raw.py` (or say "обработай RAW" in a session)
3. Articles are created in `knowledge/`, source file moves to `raw/processed/`

With Obsidian Web Clipper, you can clip articles directly from your browser into `raw/`.

## How It Works (Under the Hood)

### The Karpathy Analogy

```
daily/          = source code    (your conversations)
LLM             = compiler       (extracts and organizes)
knowledge/      = executable     (structured, queryable wiki)
lint            = test suite     (health checks)
queries         = runtime        (using the knowledge)
```

### Why No RAG?

At personal scale (50-500 articles), the LLM reading a structured index outperforms vector similarity. The LLM understands what you're really asking; cosine similarity just finds similar words. RAG becomes necessary at ~2,000+ articles.

### Cost: $0/month

All LLM calls use the Claude Agent SDK, which is covered by your Claude Max subscription (also Team and Enterprise). No API key, no billing, no separate credits.

## Credits

- **Andrej Karpathy** — [original LLM wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- **coleam00** — [claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) (the codebase this is forked from)
- **Edward Grishin** — [video walkthrough](https://www.youtube.com/watch?v=P7JDXCAVPxY) that introduced the method to Russian-speaking community

## License

MIT
