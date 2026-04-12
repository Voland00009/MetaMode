# MetaMode

Persistent memory layer поверх Claude Code — fork coleam00/claude-memory-compiler.
Wiki-память: hooks захватывают сессии → compile → structured wiki-статьи.
Stack: Python, uv, Claude Agent SDK ($0/mo на Max), Obsidian.

## Принципы

1. **Hybrid save** — hooks авто-захват + `!save`/`/reflect` вручную. Human-in-the-loop для качества.
2. **File-first** — всё в markdown, git versioning.
3. **$0/mo** — только Max подписка, никаких платных зависимостей.
4. **Fork, don't rewrite** — минимальные модификации поверх coleam00.

## Conventions

- Tests: логика save/retrieve/compile; glue-код hooks — best effort
- Commits: объясняют ПОЧЕМУ, не только ЧТО
- Session workflow: одна задача = одна сессия

## Ограничения

- Не добавлять LightRAG/vector DB (overkill для <1K docs)
- Не добавлять полный auto self-learning (заменён на pending review)

## RAW Inbox

Когда пользователь говорит "обработай RAW" / "process RAW":
`uv run python scripts/ingest_raw.py` — создаст wiki-статьи, обновит index, переместит в `raw/processed/`
