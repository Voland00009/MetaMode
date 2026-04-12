# Сессия: MetaMode v2 — продолжение (quality audit + cost tracking + шпаргалка)

## Контекст

Предыдущая сессия начала реализацию v2 improvements. Часть работы сделана, часть нет.

## Что СДЕЛАНО (не трогать, только проверить):

### 1. flush.py — переделан
- **Убран pending review** — теперь пишет прямо в daily log (как coleam00)
- **Добавлен quality audit (Pass 2)** — после извлечения, второй LLM-вызов проверяет качество
- Если аудит находит мусор → помечает `<!-- AUDIT_FLAG: reason -->` (НЕ удаляет!)
- Если аудит падает с ошибкой → считаем "всё ОК" (данные не теряются)
- Удалена функция `write_pending_review()`
- Удалена константа `PENDING_REVIEW_FILE`

### 2. compile.py — частично обновлён
- Добавлен regex-фильтр: записи с `<!-- AUDIT_FLAG: ... -->` заменяются на `[audit-flagged entry skipped]`
- Это значит compile НЕ создаёт wiki-статьи из помеченного мусора

### 3. pending-review.md — очищен
- 4 pending записи мигрированы в daily/2026-04-12.md (секции "migrated from pending review")
- Файл pending-review.md очищен

## Что НЕ СДЕЛАНО (нужно в этой сессии):

### 4. session_start.py — убрать pending review display
- Функция `get_pending_review()` больше не нужна
- Убрать блок "Pending Review" из `build_context()`
- Файл: `hooks/session_start.py`, строки ~42-48 и ~119-126

### 5. Cost tracking (из coleam00)
- Добавить запись `total_cost_usd` из `ResultMessage` в state.json
- Файлы: `scripts/compile.py`, `scripts/query.py`
- Пример формата в state.json: `{"hash": "...", "cost_usd": 0.0, "compiled_at": "..."}`

### 6. Написать шпаргалку
- Файл: `docs/cheatsheet.md`
- Все команды: `!save`, `uv run python scripts/compile.py`, `uv run python scripts/query.py`, `uv run python scripts/lint.py`, `uv run python scripts/ingest_raw.py`
- Что автоматическое (SessionEnd flush, quality audit, compile after 18:00)
- Что ручное (!save, compile, query, lint, ingest_raw, обработай RAW)
- Когда что использовать — простые примеры

### 7. Тест pipeline end-to-end
- Запустить flush.py с тестовым контекстом → проверить что пишет в daily log
- Проверить что quality audit работает (Pass 2)
- Проверить что compile.py пропускает AUDIT_FLAG записи
- Проверить !save с кириллицей (уже проверено — работает)

### 8. Обновить тесты
- Тесты flush.py: убрать тесты pending review, добавить тесты quality audit
- Тесты compile.py: добавить тест на AUDIT_FLAG фильтрацию

## Дополнительный контекст

- Аудит в `raw/metamode-vs-coleam00-audit.md` — ещё не обработан в wiki (запустить ingest_raw.py)
- README черновик в `plans/README-draft.md` — ревью в будущей сессии
- Categorization и enriched session start — оставляем как есть (решено)
- !save баг уже исправлен (UTF-8 fix в коммите 728195d)
