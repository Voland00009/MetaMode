# Сессия: Проверка SDK на Max + миграция CLI → SDK

## Контекст

Аудит MetaMode показал: наш переход с SDK на CLI был ошибкой. coleam00 README утверждает, что Claude Agent SDK покрывается Max подпиской. Если это правда — нужно мигрировать обратно, потому что SDK даёт streaming, max_turns, typed messages и system_prompt preset.

Подробности аудита: `raw/metamode-vs-coleam00-audit.md` и memory `project_audit_done.md`.

## Задача 0: Проверить SDK на Max (БЛОКЕР)

Перед любой миграцией — проверить, что SDK реально работает без API key, на Max подписке.

### Шаги:
1. `uv add claude-agent-sdk` в MetaMode
2. Написать минимальный тест-скрипт (`scripts/test_sdk.py`):
   ```python
   import asyncio
   from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

   async def test():
       async for msg in query(
           prompt="Say 'SDK works' and nothing else",
           options=ClaudeAgentOptions(allowed_tools=[], max_turns=1),
       ):
           if isinstance(msg, AssistantMessage):
               for block in msg.content:
                   if isinstance(block, TextBlock):
                       print(block.text)

   asyncio.run(test())
   ```
3. Запустить: `uv run python scripts/test_sdk.py`
4. **Если работает** → переходим к миграции
5. **Если ошибка авторизации** → SDK не покрыт Max, останавливаемся, документируем результат

## Задача 1: Миграция CLI → SDK (только если Задача 0 = OK)

Заменить `claude_cli.run_claude_prompt()` на `claude_agent_sdk.query()` в 4 файлах.

### Файлы для миграции:

**1. `scripts/flush.py`** — `run_flush()` функция
- Sync → async
- Добавить `max_turns=2`
- **СОХРАНИТЬ** pending review логику (write_pending_review)
- Референс: `c:/Users/Voland/Dev/temp-coleam00/scripts/flush.py` строки 75-139

**2. `scripts/compile.py`** — `compile_daily_log()` функция
- Sync → async
- Добавить `max_turns=30`, `system_prompt={"type": "preset", "preset": "claude_code"}`
- Добавить `permission_mode="acceptEdits"`
- Референс: `c:/Users/Voland/Dev/temp-coleam00/scripts/compile.py` строки 36-163

**3. `scripts/query.py`** — `run_query()` функция
- Sync → async
- Добавить `max_turns=15`, `system_prompt preset`
- **СОХРАНИТЬ** `sys.stdout.reconfigure(encoding="utf-8")` (Windows fix)
- Референс: `c:/Users/Voland/Dev/temp-coleam00/scripts/query.py` строки 25-111

**4. `scripts/lint.py`** — только `check_contradictions()` функция
- Sync → async
- Добавить `max_turns=2`
- Остальные 6 проверок — чистый Python, не менять

### После миграции:
- Удалить `scripts/claude_cli.py`
- Обновить `pyproject.toml` (добавить `claude-agent-sdk`, `python-dotenv`)
- Удалить тестовый `scripts/test_sdk.py`

## Задача 2: Обновить тесты

~10-15 тестов мокают `run_claude_prompt`. Нужно переписать на моки async SDK.

### Подход:
- Вместо `@patch('flush.run_claude_prompt')` → мокать `claude_agent_sdk.query`
- Использовать `AsyncMock` или async generator mocks
- Все 29+ тестов должны проходить после миграции

## Задача 3: Smoke test

После миграции — проверить что всё работает end-to-end:
1. `uv run python scripts/compile.py --dry-run` — должен работать
2. `uv run python scripts/query.py "test question"` — должен ответить
3. `uv run python scripts/lint.py --structural-only` — должен пройти
4. `uv run pytest` — все тесты зелёные

## Что НЕ менять в этой сессии

- hooks/ — не трогать (session-end, pre-compact, session-start, user_prompt_submit)
- !save — не трогать
- ingest_raw.py — можно мигрировать на SDK, но низкий приоритет
- pending review логика — сохранить как есть
- UTF-8 фиксы — сохранить

## Входные материалы

- **coleam00 клон (полный код SDK):** `c:/Users/Voland/Dev/temp-coleam00/`
- **Наш код:** `c:/Users/Voland/Dev/MetaMode/`
- **Аудит:** `raw/metamode-vs-coleam00-audit.md`

## Важно

- Задача 0 — блокер. Если SDK не работает на Max, НЕ мигрируем.
- Делай atomic commits после каждой задачи.
- Сохрани результат проверки SDK в memory (project_audit_done.md) — подтверждено или опровергнуто.
