# Next Session: Docs Polish — "зачем" + cross-refs

## Context

Ecosystem doc создан, Web Clipper обновлён. Но аудит показал две оставшиеся дыры:

1. **obsidian-setup.md** — нет секции "зачем" (сразу Setup). Нужен короткий абзац вверху, как в web-clipper-setup.md.
2. **notebooklm-setup.md и raw-inbox.md** — нет блока See Also с cross-references на ecosystem и соседние доки.

## Задачи

### 1. obsidian-setup.md — добавить "Why This Matters"

Перед секцией `## Setup` добавить краткое объяснение:
- Obsidian = визуальный интерфейс к wiki, которую строит MetaMode
- Graph view показывает связи между концепциями из разных проектов
- Без Obsidian wiki работает, но ты теряешь визуализацию и быстрый поиск

### 2. notebooklm-setup.md — добавить See Also

В конец файла (после Troubleshooting):
```markdown
## See Also

- [Ecosystem overview](ecosystem.md) — how NotebookLM fits into the full MetaMode pipeline
- [Obsidian setup](obsidian-setup.md) — browse and visualize your wiki
- [RAW Inbox](raw-inbox.md) — ingest external documents into the wiki
```

### 3. raw-inbox.md — добавить See Also

В конец файла (после Tips):
```markdown
## See Also

- [Ecosystem overview](ecosystem.md) — how RAW inbox fits into the full MetaMode pipeline
- [Web Clipper setup](web-clipper-setup.md) — clip web pages directly into RAW inbox
- [Obsidian setup](obsidian-setup.md) — browse and visualize your wiki
```

### 4. Коммит + sync master → main

```bash
git add docs/obsidian-setup.md docs/notebooklm-setup.md docs/raw-inbox.md
git commit -m "docs: add 'why' to obsidian-setup + cross-refs to all integration docs"
git checkout main && git merge master && git push origin main
git checkout master && git push origin master
```

## Аудит после завершения

Все 4 integration docs должны иметь:
- [ ] Мотивация ("зачем") в начале
- [ ] Use cases / сценарии
- [ ] See Also блок с cross-refs на ecosystem + соседние доки

## Prompt

```
Продолжай по плану: C:/Users/Voland/Dev/MetaMode/plans/next-session-docs-polish.md
```
