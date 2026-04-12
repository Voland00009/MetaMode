# Session log — Phase 4 T1: Plugin skeleton + smoke test

**Дата:** 2026-04-08
**Phase/Task:** Phase 4 Sessions — T1 (Plugin skeleton + smoke test)
**Статус:** ✅ Закрыта, все AC выполнены

## Что сделано

Поднят скелет plugin-а по pitch-архитектуре и доказана работоспособность цепочки Python → Mem0 cloud → add/search.

Файлы (все в `C:\Users\Voland\.claude\plugins\metamode\`):

- `.venv/` — Python 3.12.10 venv (см. ниже про Python)
- `.env` — `MEM0_API_KEY=...` (юзер создал сам; не в git-скоуп, plugin-папка вне репы)
- `mem0_client.py` — только `get_client()` + `logger` (logging в `error.log`). Полноценные `build_metadata/read_transcript/save_session/retrieve_context` — T2.
- `smoke_test.py` — `add` + polling `search`, exit 0/1
- `hooks/` — пустая, под T3/T4

## Как прошёл smoke test

`add` → id получен, `search` с `version="v2"` + `filters={"user_id": "voland"}` → 1 hit, score 0.9, на первой же попытке (без реального ожидания индексации).

Тестовая запись осталась в Mem0 cloud под `user_id=voland`, `metadata.project=metamode-smoke`. Чистим в T5 по плану pitch.

## AC (pitch T1)

- [x] Smoke-скрипт добавляет запись в Mem0 cloud
- [x] Smoke-скрипт находит её через search
- [x] API key читается из `.env`, не хардкожен
- [x] Ошибки логируются в `error.log` (доказано реальным фейлом на v2 search — упало в лог до фикса)

## Критичные находки (важно для T2/T3)

Три не-очевидных вещи, которые убьют время в T2/T3, если забыть:

1. **`mem0` SDK по умолчанию ходит в v2 API для search.** v2 требует `filters={"user_id": ...}` как kwarg, а НЕ просто `user_id="..."`. Ошибка при неправильном вызове: `400 Bad Request — Filters are required`. Это противоречит примеру из промпта T1 (там был устаревший v1-синтаксис). В `retrieve_context` (T2) сразу использовать v2-форму:
   ```python
   client.search(query, version="v2", filters={"user_id": "voland", "metadata": {"cwd": cwd}})
   ```
   Нюанс: синтаксис `filters` для вложенной metadata надо проверить при реализации T2 — может потребоваться отдельный формат типа `{"AND": [...]}`.

2. **`client.add()` по умолчанию пропускает messages через LLM-экстрактор фактов.** Короткие/мета-сообщения типа "Smoke test: проверка" LLM классифицирует как не-факты и отбрасывает молча — `add` возвращает `PENDING`, но потом `get_all` показывает 0 записей. Для Stop hook (T3) это ок — мы передаём реальные транскрипты сессий, факты будут. Но **для юнит-тестов T2** и для любого debug-smoke нужно `infer=False` — иначе будешь гоняться за призраками.

3. **`add` асинхронный (`status: PENDING`)** когда `infer=True`. С `infer=False` возвращает сразу `ADD` + id. Для тестов всегда используй `infer=False`, иначе придётся ждать индексации.

## Python environment (закрытие блокера прошлой сессии)

Прошлая сессия упёрлась в WindowsApps-заглушку Python. В этой сессии:

- `python --version` запустил установку **Python 3.14.4** через Windows py install manager — оказалось, 3.12 так и не был установлен руками юзера. На PATH висел py launcher, который auto-installed 3.14.
- Принято решение **не использовать 3.14** (свежий релиз, риск отсутствия wheels) и поставить 3.12 явно:
  ```
  py install 3.12    # встал 3.12.10
  py -3.12 -m venv .venv
  ```
- Все зависимости (`mem0ai 1.0.11`, `python-dotenv 1.2.2` + транзитив) встали чисто, wheels для 3.12 нашлись.

**Для T3 (`plugin.json`):** абсолютный путь к интерпретатору — `C:\Users\Voland\.claude\plugins\metamode\.venv\Scripts\python.exe`.

## Инциденты

**Security incident (minor).** Юзер в первый раз положил в `.env` только значение ключа без префикса `MEM0_API_KEY=`. Чтобы диагностировать, почему `dotenv` не видит ключ, я прочитал байты файла — весь ключ попал в историю чата Claude. Ключ ротирован юзером сразу же, новый положен корректно. **Урок:** в инструкциях про `.env` явно писать "формат `KEY=VALUE`, именно с знаком равенства", а не только показывать пример.

## DoD

- [x] Код проходит smoke test руками
- [x] Comprehension gate: объясняю каждую строку `mem0_client.py` (19 строк: dotenv load, logging config, get_client) и `smoke_test.py` (add с infer=False, polling search v2, проверка `response["results"]`)
- [x] `NEXT-SESSION.md` обновлён под T2
- [x] Session log написан (этот файл)
- [x] Handoff-промпт для T2 создан в `~/.claude/plans/metamode-phase4-task2-prompt.md`
- [x] Memory `project_next_action.md` обновлена на T2
- [x] ADR не создаётся (нет архитектурной развилки)

## Не сделано намеренно

- `plugin.json` — T3
- `hooks/session_start.py`, `hooks/stop.py` — T3/T4
- Юнит-тесты — T2
- Регистрация plugin в Claude Code — T3
- Cleanup тестовой записи из Mem0 — T5
