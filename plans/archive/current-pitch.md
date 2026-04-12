# MetaMode Phase 1 — Persistent Memory Layer

## Problem

Claude Code теряет контекст между сессиями: каждая новая сессия начинается "с нуля", и юзер вынужден вручную пересказывать, что было сделано раньше, какие решения приняты, какие preferences у проекта. Существующий workaround — `NEXT-SESSION.md` и session logs — работает, но требует ceremony: юзер пишет handoff руками, Claude читает руками. Если забыть обновить — контекст теряется. Нужен слой, который делает это автоматически через lifecycle hooks Claude Code, без ручных команд и без `/remember`-style tools.

## Appetite

**5 сессий Claude Code** — жёсткий потолок Shape Up style. Если на 5-й сессии гипотеза не подтверждена или MVP не работает — режем scope или честно фиксируем провал гипотезы (см. ADR-0001: решение о провайдере обратимо). НЕ добавляем сессии — добавление сессий сверх appetite означает, что scope был неправильно оценён, и это сигнал эскалировать pitch в 3-файловый spec, а не продолжать текущий.

## Success criteria

Гипотеза "zero-ceremony memory через hooks" считается подтверждённой, если:

1. **Primary (юзабилити):** в **3 реальных сессиях подряд** на разных задачах Claude самостоятельно вспомнил релевантный факт из предыдущих сессий **без ручного ввода** со стороны юзера. "Релевантный факт" = что-то, что юзер сам распознал как "о, правильно вспомнил". Проверка: вести короткий лог в `plans/sessions/` — отмечать, сработало или нет.
2. **Secondary (техника):** SessionStart hook успешно подтягивает память, Stop hook успешно сохраняет — 0 потерянных сессий за неделю реального использования. Измеряется по логам hooks.

Если (1) провалено — гипотеза провалена независимо от (2). Если (1) ок, но (2) нестабильно — это технический долг, не провал гипотезы.

## Solution sketch

Claude Code plugin на **Python** (Mem0 Python SDK — основной, больше примеров, проще входной барьер). Plugin регистрирует два lifecycle hook:

- **SessionStart hook** — при старте сессии вызывает `mem0.search()` по текущему cwd/project-контексту, подтягивает top-N релевантных memories, инжектит в system context сессии.
- **Stop hook** — при завершении сессии вызывает `mem0.add()` с summary того, что произошло в сессии (агенту даётся инструкция сформулировать summary перед выходом).

Провайдер — Mem0 cloud free tier (ADR-0001). Plugin ставится через `~/.claude/plugins/`. Никаких MCP-tool, никаких `/remember` команд — всё автоматически.

## Non-goals

Явно НЕ делаем в Phase 1:

- **MCP-tool для ручного вызова памяти** (`mcp__mem0__add_memory` и т.п.) — нарушает принцип hooks-driven.
- **Manual-команды** (`/remember`, `/forget`) — тот же запрет.
- **Failure-tagging** (пометка "это была ошибка, не повторять") — откладывается до Phase 2, если базовый recall сработает.
- **Self-host Mem0** (Docker + локальная векторная БД) — отложено до Phase 2 по ADR-0001.
- **Web UI / dashboard для просмотра памяти** — используем Mem0 cloud dashboard как есть.
- **Multi-user / team memory** — один юзер, один Mem0 аккаунт.
- **Тонкая настройка metadata schema** — стартовый минимум, детали в Phase 3 Plan.

## Open questions

- RESOLVED in Plan Q1: metadata = `{project, cwd, session_id, timestamp}` + `user_id="voland"` как отдельный параметр Mem0.
- RESOLVED in Plan Q2: Claude Code сам передаёт `session_id` и `transcript_path` в stdin-payload обоих хуков — state-файл не нужен.
- RESOLVED in Plan Q3: Stop hook читает `transcript_path` (JSONL) и передаёт messages напрямую в `mem0.add(messages=...)` — Mem0 сам извлекает facts.
- RESOLVED in Plan Q4: стартовые `top_k=10`, фильтр `user_id="voland"` + `metadata.cwd == current_cwd`; тонкая настройка эмпирически в Phase 4.

## Plan

### Резолв Q1–Q4

**Q1 — metadata schema.** Для каждой записи Mem0:
```python
metadata = {
    "project": basename(cwd),  # или из CLAUDE.md если есть
    "cwd": <absolute path>,
    "session_id": <из payload>,
    "timestamp": <UTC ISO8601>,
}
```
Плюс `user_id="voland"` (фиксированная константа соло-юзера) — это отдельный параметр SDK, не metadata; он первичный фильтр в `search()`. `cwd` — надёжный дискриминатор проекта, `session_id` — для группировки при отладке, `timestamp` — для будущих TTL. Mem0 metadata schemaless, поля расширяем без миграции.

**Q2 — hook contract.** Никакого state-файла. Claude Code передаёт в stdin JSON обоих хуков:
- `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `source`, `model`

Оба хука получают одинаковый `session_id` для одной сессии. Это самый чистый вариант из тех, что рассматривались в pitch. Источник: Claude Code hooks docs.

**Q3 — summary capture.** Stop hook читает `transcript_path` (JSONL-транскрипт сессии), парсит в `list[{role, content}]`, передаёт сырой список в `mem0.add(messages=..., user_id="voland", metadata={...})`. Mem0 сам извлекает facts своим LLM-pipeline. Альтернативы (просить агента саммаризировать / свой summarizer) отвергнуты — хрупко и дороже. Риск больших транскриптов митигируется `max_messages=50` (последние N сообщений).

**Q4 — retrieve параметры.** `top_k=10`, `user_id="voland"`, `filters={"metadata": {"cwd": <current_cwd>}}`, сортировка — дефолтная Mem0 по релевантности. Запрос — контекстная строка вида `"project context and recent decisions for {project_name}"`. Финальные значения подстраиваем в Phase 4 по реальным данным.

### Архитектура plugin-а

Структура файлов (ровно 5, в границах pitch):

```
~/.claude/plugins/metamode/
├── plugin.json                  # манифест Claude Code, регистрация SessionStart и Stop
├── hooks/
│   ├── session_start.py         # тонкий glue: stdin → retrieve_context → stdout additionalContext
│   └── stop.py                  # тонкий glue: stdin → save_session → exit 0
├── mem0_client.py               # вся логика: get_client, build_metadata, read_transcript, save_session, retrieve_context
└── tests/
    └── test_mem0_client.py      # юнит-тесты build_metadata и read_transcript
```

Зависимости: `mem0ai`, `python-dotenv`. API key — в `~/.claude/plugins/metamode/.env`, переменная `MEM0_API_KEY`.

**Разделение ответственности:** вся чистая логика живёт в `mem0_client.py` и тестируется изолированно (mocked client). Hook-скрипты — тонкие адаптеры stdin/stdout, не тестируются юнитами (проверяются ручным прогоном Claude Code).

**SessionStart output:** JSON `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "<retrieved text>"}}` в stdout + exit 0.

**Обработка ошибок:** hook никогда не блокирует Claude Code. Любая ошибка (нет API key, network, Mem0 500) логируется в `~/.claude/plugins/metamode/error.log`, hook выходит с exit 0. Если retrieve провалился — сессия стартует без контекста, это деградация, не поломка (соответствует success criteria: нестабильность hooks = tech debt, не провал гипотезы).

**ADR не создаётся:** решения Q1–Q4 обратимы за ≤1 сессии, триггер §3 foundation-template не срабатывает.

**Эскалация:** если в T1–T2 выяснится, что файлов нужно >5 ИЛИ задач >6 ИЛИ возникла архитектурная развилка ≥2 альтернатив — останавливаемся и эскалируем pitch в 3-файловый spec (template §4.6).

## Tasks

- [x] **T1. Plugin skeleton + smoke test.** ✅ 2026-04-08 (see `sessions/2026-04-08-phase4-t1-skeleton.md`) Создать `~/.claude/plugins/metamode/`, установить `mem0ai` + `python-dotenv`, положить `.env` с API key, написать `mem0_client.get_client()` и smoke-скрипт: `add([{"role":"user","content":"test"}], user_id="voland")` + `search("test", user_id="voland")`. Проверить, что работает из того Python, которым Claude Code запускает hooks.
  - AC: smoke-скрипт успешно добавляет и находит запись; API key не хардкожен; ошибки логируются в `error.log`.

- [ ] **T2. `mem0_client.py` — ядро логики + тесты.** Реализовать `build_metadata`, `read_transcript`, `save_session`, `retrieve_context`. Юнит-тесты: `build_metadata` (структура полей) и `read_transcript` (парсинг фикстурного JSONL, обрезка до `max_messages`).
  - AC: `pytest tests/` проходит; `read_transcript` корректно парсит реальный JSONL-транскрипт (взять из `~/.claude/projects/.../*.jsonl`); сетевые вызовы в тестах замоканы.

- [ ] **T3. Stop hook + `plugin.json`.** Написать `hooks/stop.py` (stdin JSON → `save_session`), зарегистрировать в `plugin.json` под событием Stop. Ручной прогон: запустить тестовую сессию Claude Code, завершить, проверить запись в Mem0 dashboard.
  - AC: после 1 реальной сессии в Mem0 dashboard видна запись с `metadata.cwd` = тестовая папка; при симулированной ошибке (отключить сеть) Claude Code всё равно завершается нормально.

- [ ] **T4. SessionStart hook.** Написать `hooks/session_start.py` (stdin JSON → `retrieve_context` → stdout `additionalContext` JSON). Зарегистрировать в `plugin.json`.
  - AC: старт новой сессии в той же тестовой папке — Claude в первом ответе ссылается на факт из предыдущей сессии без ручного ввода юзера.

- [ ] **T5. Реальное тестирование + замер success criteria.** 3 реальных рабочих сессии подряд. После каждой — запись в `plans/sessions/YYYY-MM-DD-phase1-test-N.md`: сработал ли recall, что вспомнил, что пропустил. Замер вторичного критерия по `error.log`: сколько запусков/успешных/ошибок.
  - AC: 3/3 с успешным recall → primary критерий выполнен → гипотеза подтверждена. <3/3 → ретроспектива и решение: режем scope / эскалируем в spec / фиксируем провал гипотезы.

Итого 5 задач в appetite 5 сессий. Cleanup/retrospective делаем по ходу T5.
