# MetaMode

Persistent wiki-memory layer for Claude Code — fork of coleam00/claude-memory-compiler.
Wiki-memory: hooks capture sessions → compile → structured wiki articles.
Stack: Python, uv, Claude Agent SDK ($0/mo on Max), Obsidian.

## Principles

1. **Hybrid save** — hooks auto-capture + `!save`/`/reflect` manual. Human-in-the-loop for quality.
2. **File-first** — everything in markdown, git versioning.
3. **$0/mo** — Max subscription only, no paid dependencies.
4. **Fork, don't rewrite** — minimal modifications on top of coleam00.

## Conventions

- Tests: logic for save/retrieve/compile; glue-code hooks — best effort
- Commits: explain WHY, not just WHAT
- Session workflow: one task = one session

## Constraints

- No LightRAG/vector DB (overkill for <1K docs)
- No full auto self-learning (replaced with quality audit)

## RAW Inbox

When user says "process RAW" / "ingest RAW":
`uv run python scripts/ingest_raw.py` — creates wiki articles, updates index, moves to `raw/processed/`
