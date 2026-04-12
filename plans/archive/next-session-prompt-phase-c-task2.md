# Phase C, Task 2: Cross-project wiki access

## Context

MetaMode — persistent wiki-memory поверх Claude Code. Живёт в `C:\Users\Voland\Dev\MetaMode`. Phase B завершена (все скрипты, hooks, skills работают). Phase C Task 1 завершена (RAW inbox + ingest_raw.py).

Сейчас wiki доступна только из MetaMode проекта. Нужно сделать так, чтобы Claude Code в **любом** проекте мог читать и использовать wiki.

## Задача

Создать шаблон для CLAUDE.md других проектов — блок с путём к wiki и инструкцией как её использовать.

### Что нужно сделать:

1. **Создать `docs/cross-project-template.md`** — готовый блок для вставки в CLAUDE.md любого проекта. Блок должен содержать:
   - Абсолютный путь к MetaMode wiki (`C:\Users\Voland\Dev\MetaMode\knowledge/`)
   - Инструкцию для Claude: "перед ответом на вопрос проверь wiki через Read/Glob"
   - Инструкцию: "если узнал что-то новое — предложи сохранить в wiki"
   - Путь к `raw/` для быстрого сохранения внешних данных

2. **Протестировать**: добавить шаблон в CLAUDE.md какого-нибудь тестового проекта (можно создать temp папку), открыть Claude Code в нём, спросить что-то что есть в wiki (например "что такое duck typing silent failures в Python?")

3. **Подумать об альтернативе**: может ли глобальный `~/.claude/CLAUDE.md` быть лучшим местом для этого блока? Pros/cons обоих подходов.

## Constraints

- Пути должны работать на Windows (backslash или forward slash — проверить что Claude Code читает оба)
- Не менять структуру wiki
- Шаблон должен быть copy-paste ready

## Полный план Phase C (для контекста)

- ~~Task 1: RAW folder + processing workflow~~ ✅
- **Task 2: Cross-project wiki access** ← ЭТО
- Task 3: Obsidian Web Clipper setup (ручная настройка, не код)
- Task 4: Verify full cycle
- Task 5: Cleanup + commit
