# Lint Reminder + Memory Lint (opt-in)

**Цель:** Еженедельная проверка wiki + опциональная проверка auto-memory Claude.
**Контекст:** Health check система — DEFER. Вместо неё — lint reminder в session_start + memory lint как отдельная команда.

---

## Уже сделано (эта сессия)

- ✅ `get_lint_reminder()` добавлена в `hooks/session_start.py`
- ✅ `lint.py` уже пишет `last_lint` в `scripts/state.json`
- ✅ Протестировано: warning появляется если lint > 7 дней, исчезает после запуска

---

## Что сделать

### Шаг 1. Создать `scripts/memory_lint.py` (opt-in memory проверка)

Отдельный скрипт. Не часть wiki lint — пользователь запускает когда хочет.

**Путь:** `scripts/memory_lint.py`

**Что проверяет (структурно, без LLM):**

1. **MEMORY.md broken refs** — индекс ссылается на `file.md`, но файла нет
2. **Orphan memory files** — `.md` в `memory/` не упомянут в `MEMORY.md`
3. **File count** — если > 30 файлов в одном проекте → warning
4. **Total size** — если > 100K в одном проекте → warning
5. **CLAUDE.md line count** — если global > 40 строк или project > 50 строк → warning

**Где искать memory:**
- Сканировать `~/.claude/projects/*/memory/` — все проекты
- CLAUDE.md: `~/.claude/CLAUDE.md` (global) + `./CLAUDE.md` (текущий проект)

**Формат вывода:** Такой же как `lint.py` — отчёт в `reports/memory-lint-YYYY-MM-DD.md`.

**Сохранять `last_memory_lint`** в `scripts/state.json` — аналогично `last_lint`.

### Шаг 2. Добавить memory lint reminder в `session_start.py`

В `get_lint_reminder()` — добавить вторую проверку:
- Если `last_memory_lint` нет или > 14 дней → warning
- Текст: `"Memory lint не запускался N дней. Скажи 'проверь память' если хочешь."`
- **14 дней**, не 7 — memory меняется реже чем wiki

Оба warning-а (wiki + memory) должны быть в одном блоке `## Lint Reminder`, чтобы не раздувать контекст.

### Шаг 3. Добавить флаг `--include-memory` в `lint.py`

Чтобы можно было запустить всё одной командой:
```bash
uv run python scripts/lint.py                    # только wiki
uv run python scripts/lint.py --include-memory   # wiki + memory
```

При `--include-memory` — импортировать и вызвать проверки из `memory_lint.py`, добавить результаты в общий отчёт.

### Шаг 4. Проверить

1. Запустить `uv run python scripts/memory_lint.py` — должен выдать отчёт по текущему состоянию
2. Проверить что `last_memory_lint` появился в `state.json`
3. Запустить `uv run python scripts/lint.py --include-memory` — должен включить оба отчёта
4. Подделать `last_memory_lint` на 15 дней назад → запустить `session_start.py` → warning должен появиться
5. Убедиться что **без** `--include-memory` lint работает как раньше (не ломает существующее)

### Шаг 5. Удалить устаревшие планы

- `plans/next-session-health-check-design.md`
- `plans/next-session-health-check-research.md`

---

## Что НЕ делать

- Не пихать результаты lint в session context — только reminder (одна строка)
- Не запускать lint автоматически при старте сессии — только напоминание
- Не делать LLM-проверку stale memory в первой версии — добавить позже если нужно
- Не проверять memory других проектов без явного запуска — opt-in only

## Бюджет контекста

- Wiki lint reminder: ~100 chars (одна строка), раз в 7 дней
- Memory lint reminder: ~100 chars (одна строка), раз в 14 дней
- Итого максимум: +200 chars к session context = <1% бюджета
