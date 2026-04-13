🌐 [English](commands.md) | **Русский**

# Справочник команд

Всё, что умеет MetaMode — автоматические hooks, CLI-скрипты и команды в чате.

---

## Автоматические (Hooks)

Работают без каких-либо действий с вашей стороны. Настройте один раз в [setup](setup.ru.md) — и забудьте.

| Hook | Триггер | Что делает | Что вы видите |
|------|---------|-----------|---------------|
| **SessionStart** | Начало каждой сессии | Загружает wiki-индекс и последние записи daily log в контекст Claude | Claude начинает с вашими знаниями |
| **SessionEnd** | Закрытие сессии (`/exit`, закрытие терминала) | Извлекает транскрипт, запускает `flush.py` в фоне | Ничего — работает тихо |
| **PreCompact** | Claude автоматически сжимает контекст (окно заполнено) | То же, что SessionEnd — страховка от потери ранних решений | Ничего — работает тихо |
| **UserPromptSubmit** | Вы вводите `!save <текст>` | Сохраняет заметку в daily log, блокирует prompt (0 токенов) | Подтверждение в stderr |

### Как работают hooks

- **Глобальные:** hooks срабатывают в каждой сессии Claude Code, из любого проекта
- **Защита от рекурсии:** если вызывающий — Claude Agent SDK (flush/compile), hooks завершаются немедленно — никаких бесконечных циклов
- **Дедупликация flush:** если одна и та же сессия вызывает flush дважды в течение 60 секунд, второй вызов пропускается

---

## CLI-скрипты

Запускайте из директории MetaMode. Все команды используют `uv run python scripts/<script>.py`.

### compile.py — Daily logs в wiki-статьи

Читает нескомпилированные daily logs, отправляет каждый в Agent SDK с wiki-схемой, создаёт/обновляет wiki-статьи.

```bash
uv run python scripts/compile.py                          # компиляция только новых логов
uv run python scripts/compile.py --all                    # принудительная перекомпиляция всего
uv run python scripts/compile.py --file daily/2026-04-01.md  # компиляция одного конкретного лога
uv run python scripts/compile.py --dry-run                # показать, что будет скомпилировано
```

| Флаг | Описание |
|------|----------|
| `--all` | Игнорировать hash cache, перекомпилировать все daily logs |
| `--file <path>` | Скомпилировать конкретный daily log |
| `--dry-run` | Показать, какие файлы будут скомпилированы, без запуска Agent SDK |

**Когда использовать:** после накопления 3+ daily logs, или когда вы хотите свежие wiki-статьи из последних сессий.

**Авто-запуск:** `flush.py` автоматически запускает compile после 18:00, если daily logs изменились за день.

---

### query.py — Спросите вашу wiki

Ищет по wiki и синтезирует ответ с помощью Agent SDK.

```bash
uv run python scripts/query.py "How should I handle auth redirects?"
uv run python scripts/query.py "What patterns do I use?" --file-back
```

| Флаг | Описание |
|------|----------|
| `--file-back` | Сохранить ответ как Q&A-статью в `knowledge/qa/` |

**Когда использовать:** вы хотите проверить, что ваша wiki знает по теме — не открывая Claude Code.

---

### ingest_raw.py — Внешние документы в wiki

Обрабатывает markdown/текстовые файлы из папки `raw/`. Тот же pipeline компиляции, что и `compile.py`, но для внешнего контента.

```bash
uv run python scripts/ingest_raw.py
```

Без флагов. Обрабатывает все `.md` и `.txt` файлы в `raw/`, создаёт wiki-статьи, перемещает оригиналы в `raw/processed/`.

**Когда использовать:** вы нашли статью, сделали заметки с совещания или у вас есть исследовательские записи для wiki. Положите файл в `raw/`, затем запустите скрипт.

**Формат RAW-файла:**
```markdown
# Title of the insight

## Context
Where/when this came up

## Key Insight
The actual lesson or pattern

## Example (optional)
Code or scenario illustrating the point
```

---

### lint.py — Проверка здоровья wiki

Выполняет 7 структурных и семантических проверок вашей wiki.

```bash
uv run python scripts/lint.py                    # все 7 проверок
uv run python scripts/lint.py --structural-only  # пропустить LLM-проверку противоречий (быстрее)
uv run python scripts/lint.py --include-memory   # также проверить auto-memory Claude Code
```

| Флаг | Описание |
|------|----------|
| `--structural-only` | Пропустить LLM-проверку противоречий (только проверки 1-6) |
| `--include-memory` | Также запустить проверки `memory_lint.py` для auto-memory Claude Code |

**7 проверок:**

1. **Broken links** — wikilinks, указывающие на несуществующие статьи
2. **Orphan pages** — статьи, на которые не ссылается ни одна другая статья
3. **Orphan sources** — daily logs, ещё не скомпилированные
4. **Stale articles** — исходный лог изменился после компиляции статьи
5. **Missing backlinks** — A ссылается на B, но B не ссылается обратно на A
6. **Sparse articles** — менее 200 слов
7. **Contradictions** — LLM читает все статьи и находит противоречащие утверждения (затратная операция)

Отчёты сохраняются в `reports/lint-YYYY-MM-DD.md`.

**Когда использовать:** wiki кажется беспорядочной, или вы давно не проверяли. Hook session start напоминает, если lint не запускался более 7 дней.

---

### memory_lint.py — Проверка auto-memory

Отдельный скрипт для проверки встроенной auto-memory Claude Code (файлы `~/.claude/projects/*/memory/`).

```bash
uv run python scripts/memory_lint.py
```

Без флагов. Проверяет:
- Битые ссылки в `MEMORY.md` (индекс указывает на отсутствующий файл)
- Orphan-файлы памяти (файл существует, но не в индексе)
- Количество файлов на проект (предупреждение при > 30)
- Общий размер на проект (предупреждение при > 100K)
- Количество строк в `CLAUDE.md` (глобальный > 40, проектный > 50)

Отчёты сохраняются в `reports/memory-lint-YYYY-MM-DD.md`.

---

### flush.py — Транскрипт в daily log

**Вы не вызываете это напрямую.** Запускается hooks SessionEnd и PreCompact.

Что делает:
1. **Pass 1 (Extract):** отправляет транскрипт в Agent SDK, извлекает структурированные секции (Context, Key Exchanges, Decisions, Lessons, Action Items)
2. **Pass 2 (Quality Audit):** второй вызов Agent SDK фильтрует мусор — помечает малоценные записи комментариями `<!-- AUDIT_FLAG -->`
3. Дописывает результат в `daily/YYYY-MM-DD.md`

Если ничего стоящего не найдено, записывает маркер `FLUSH_OK`.

---

## Команды в чате

Вводите их прямо в Claude Code во время сессии.

### !save — Мгновенная заметка

```
!save Decision: we're using PostgreSQL because SQLite can't handle concurrent writes
!save Bug: auth tokens expire silently — need refresh logic
!save Pattern: always validate webhook signatures before processing
```

- Сохраняет текст напрямую в сегодняшний daily log как запись "Quick Save"
- **Блокирует prompt** — Claude не видит его (0 потреблённых токенов)
- Появляется как запись с таймстампом в daily log
- Работает с любым языком (UTF-8)

### /reflect — Рефлексия в конце сессии

Введите `/reflect` в конце сессии. Claude задаст вам 4 структурированных вопроса:
1. Что вы узнали?
2. Что вас удивило?
3. Что бы вы сделали иначе?
4. Что стоит запомнить на будущее?

Ответы сохраняются в daily log. Это метод захвата наивысшего качества — управляемый человеком, а не автоматически извлечённый.

### /compile — Компиляция wiki

Алиас для запуска `compile.py`. Скажите `/compile` или "compile the wiki" в чате.

---

## Дерево решений

```
Хотите сохранить что-то прямо сейчас?
  --> !save <текст>

Есть нескомпилированные daily logs?
  --> uv run python scripts/compile.py

Нашли статью или заметки для добавления?
  --> Положите в raw/ --> uv run python scripts/ingest_raw.py

Хотите задать вопрос вашей wiki?
  --> uv run python scripts/query.py "вопрос"

Wiki кажется беспорядочной или противоречивой?
  --> uv run python scripts/lint.py

Конец рабочей сессии?
  --> /reflect (или просто закройте — auto-flush справится)
```
