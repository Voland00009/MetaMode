# Session 2026-04-08 — phase4-t1-blocker

**Фича:** `plans/current-pitch.md` — MetaMode Phase 1 Persistent Memory Layer
**Задача:** T1. Plugin skeleton + smoke test

## Что сделано

- Прочитан контекст: `CLAUDE.md`, `current-pitch.md` (Plan + Tasks), ADR-0001, `NEXT-SESSION.md`, foundation template §3.
- Сверился с актуальным Mem0 Python SDK quickstart: пакет `mem0ai`, класс `from mem0 import MemoryClient`, `client.add(messages, user_id=...)`, `client.search(query, filters={"user_id": ...})` (в облачном SDK фильтры чаще через `filters`, но `user_id=` kwarg тоже поддерживается в ряде версий — уточним при первом прогоне).
- Проверено Python-окружение на машине — **блокер**: установлен только WindowsApps-заглушка `C:\Users\Voland\AppData\Local\Microsoft\WindowsApps\python.exe`, реального Python нет. Любой `python -c ...` падает с exit 49.
- Юзеру рекомендована установка Python 3.12 с python.org (галка "Add to PATH") или через `winget install Python.Python.3.12`. Юзер подтвердил установку.

## Ключевые решения

- Папка plugin-а, venv и файлы **не создавались** в этой сессии — сознательно, чтобы начать T1 с чистого листа в новой сессии, когда PATH с новым Python уже подхвачен в bash.
- API key от Mem0 cloud у юзера есть — закинет в следующей сессии при создании `.env`.

## Что пошло не так

- Блокер Python обнаружился только на этапе `python --version` — риск из pitch-секции "риски и что делать если" сработал. В новую сессию входим с уже снятым блокером.

## Для следующей сессии

Запускать тем же промптом `~/.claude/plans/metamode-phase4-task1-prompt.md`. Python уже установлен — начинаем прямо с шага "создать venv". AC T1 и список файлов без изменений.
