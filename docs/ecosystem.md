# MetaMode Ecosystem

How all parts of MetaMode work together to give Claude persistent memory across sessions, projects, and external sources.

## The Problem

Claude Code is stateless — every session starts from zero. You explain the same context, re-share the same decisions, re-discover the same bugs. MetaMode fixes this with a pipeline that captures, compiles, and injects knowledge automatically.

But conversations are only one source of knowledge. You also learn from articles, docs, research, and other people's code. The ecosystem connects all of these into one memory.

## Components

```text
MetaMode Ecosystem
├── Hooks          — auto-capture conversations → daily logs
├── Compile        — daily logs → structured wiki articles
├── RAW Inbox      — external docs → wiki articles
├── Web Clipper    — web pages → RAW inbox (one click)
├── Obsidian       — browse, search, visualize the wiki
└── NotebookLM     — audio overviews, quizzes, chat with knowledge
```

### Hooks (auto-capture)

Three Claude Code lifecycle hooks fire automatically from any project:

- **SessionStart** — injects wiki index + recent daily log into Claude's context
- **SessionEnd / PreCompact** — extracts the conversation transcript, summarizes it via Agent SDK, and writes a daily log entry

You don't need to do anything. Open Claude Code, work, close it — the hooks handle the rest.

### Compile (daily logs → wiki)

`scripts/compile.py` reads daily log entries and produces structured wiki articles in `knowledge/concepts/` and `knowledge/connections/`. Each article is atomic — one concept per file, with wikilinks connecting related ideas.

Compile runs automatically after 18:00 when flush detects new logs, or manually via `uv run python scripts/compile.py`.

### RAW Inbox (external docs)

Drop any `.md` or `.txt` file into `raw/`. Run `uv run python scripts/ingest_raw.py`. The script creates wiki articles and moves processed files to `raw/processed/`.

This is the entry point for knowledge from outside Claude — notes, transcripts, copied documentation, anything in markdown.

### Web Clipper (web → RAW)

Obsidian Web Clipper is a browser extension that saves any web page as a markdown file directly into `raw/`. One click to clip, one command to ingest.

```text
Blog post → Web Clipper → raw/blog-post.md → ingest_raw.py → knowledge/concepts/blog-insight.md
```

This turns your browser into a knowledge capture tool — articles, docs, Stack Overflow answers, anything you read can become part of Claude's memory.

See [Web Clipper setup](web-clipper-setup.md) for installation.

### Obsidian (visualization)

MetaMode's `knowledge/` directory is a native Obsidian vault. Open it and you get:

- **Graph view** — see how concepts connect across projects and topics
- **Full-text search** — find anything across daily logs, wiki, and RAW inbox
- **Backlinks** — discover which articles reference a given concept
- **Direct editing** — fix or extend wiki articles in a rich editor

Obsidian is optional — the wiki is plain markdown managed by git. But the graph view makes patterns visible that you'd never find by reading files.

See [Obsidian setup](obsidian-setup.md) for configuration.

### NotebookLM (learning & review)

Google NotebookLM can ingest your wiki articles and generate:

- **Audio overviews** — podcast-style summaries you can listen to while walking
- **Quizzes** — test your retention of concepts you learned weeks ago
- **Chat** — ask questions about your own knowledge base without spending Claude tokens

NotebookLM is best for review and consolidation — it helps you internalize knowledge that MetaMode captured.

See [NotebookLM setup](notebooklm-setup.md) for configuration.

## How They Connect

```text
                    ┌─────────────┐
                    │  You code   │
                    │  in Claude  │
                    └──────┬──────┘
                           │ hooks auto-capture
                           ▼
┌──────────┐    ┌──────────────────┐    ┌───────────┐
│ Web page │───▶│    RAW Inbox     │    │ Daily Log │
│ (Clipper)│    │  raw/*.md        │    │ daily/*.md│
└──────────┘    └────────┬─────────┘    └─────┬─────┘
                         │ ingest_raw.py      │ compile.py
                         ▼                    ▼
                   ┌──────────────────────────────┐
                   │       Wiki (knowledge/)       │
                   │  concepts/ + connections/     │
                   └──────┬───────────┬────────────┘
                          │           │
                 ┌────────▼──┐   ┌────▼────────┐
                 │ Obsidian  │   │ NotebookLM  │
                 │ browse +  │   │ audio +     │
                 │ visualize │   │ quizzes     │
                 └───────────┘   └─────────────┘
                          │
                  session_start hook
                          │
                          ▼
                 ┌─────────────────┐
                 │ Next session:   │
                 │ Claude knows    │
                 │ everything      │
                 └─────────────────┘
```

## What You Get Out of the Box

After cloning MetaMode and configuring hooks:

| Feature | Setup needed | Ongoing effort |
|---------|-------------|---------------|
| Auto-capture sessions | Configure hooks once | None — automatic |
| Compile wiki | None | Runs after 18:00 or manually |
| RAW inbox | None | Drop files, run ingest |
| Web Clipper | Install browser extension | One click per page |
| Obsidian | Open folder as vault | None — reads markdown |
| NotebookLM | Configure CLI + cookie auth | Upload sources periodically |

## Why Together > Apart

Each tool is useful alone. Together they create a feedback loop:

1. You **learn** something in a Claude session → hooks capture it
2. You **read** an article that expands on it → Web Clipper captures it
3. Both get **compiled** into the same wiki → connections form automatically
4. You **see** the connections in Obsidian's graph → new insights
5. You **review** via NotebookLM audio → better retention
6. Next session, Claude **starts with all of this** → better answers → you learn more

The wiki is the hub. Everything flows into it, and everything reads from it.
