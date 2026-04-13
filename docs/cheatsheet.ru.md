🌐 [English](cheatsheet.md) | **Русский**

# Шпаргалка MetaMode

## Автоматическое (работает само)

| Что | Когда | Как |
|-----|-------|-----|
| **Session flush** | Сессия Claude Code завершается | Hook `SessionEnd` → `flush.py` в фоне |
| **Quality audit** | Сразу после flush | Pass 2 в `flush.py` — LLM проверяет качество |
| **Pre-compact backup** | Сжатие контекстного окна | Hook `PreCompact` → `flush.py` |
| **Wiki injection** | Начало сессии | Hook `SessionStart` → `session_start.py` |
| **Auto-compile** | После flush, если позже 18:00 | `flush.py` → `compile.py` в фоне |

## Ручные команды

### Мгновенное сохранение
```
!save <текст>
```
Сохраняет заметку в дневной лог прямо из чата. Блокирует промпт (0 токенов потрачено).

### Compile в wiki
```bash
uv run python scripts/compile.py
uv run python scripts/compile.py --all          # перекомпилировать всё
uv run python scripts/compile.py --file <path>  # один конкретный файл
uv run python scripts/compile.py --dry-run      # показать, что будет скомпилировано
```
Или в чате: `/compile`

Превращает дневные логи в wiki-статьи (`knowledge/concepts/`, `knowledge/connections/`).

### Запрос к базе знаний
```bash
uv run python scripts/query.py "How does X work?"
uv run python scripts/query.py "Pattern Y" --file-back  # сохранить ответ как Q&A-статью
```
Ищет по wiki и синтезирует ответ.

### Lint
```bash
uv run python scripts/lint.py                    # все 7 проверок
uv run python scripts/lint.py --structural-only  # без LLM-проверки (быстрее)
uv run python scripts/lint.py --include-memory   # также проверить auto-memory
```

### Обработка RAW inbox
```bash
uv run python scripts/ingest_raw.py
```
Или в чате: скажите "process RAW" / "ingest RAW"

Обрабатывает файлы из `raw/` → создаёт wiki-статьи, перемещает в `raw/processed/`.

### Рефлексия в конце сессии
В чате: `/reflect`

4 структурированных вопроса о сессии → сохраняются в дневной лог.

## Когда что использовать

| Ситуация | Действие |
|----------|----------|
| Узнали что-то важное прямо сейчас | `!save <инсайт>` |
| Нашли статью/видео для wiki | Сохраните в `raw/`, затем запустите `ingest_raw.py` |
| Накопилось 3+ дневных лога | `uv run python scripts/compile.py` |
| Хотите найти что-то в wiki | `uv run python scripts/query.py "вопрос"` |
| Конец рабочей сессии | `/reflect` (или просто закройте — auto-flush справится) |
| Проверить здоровье wiki | `uv run python scripts/lint.py` |

## Где что хранится

```
daily/              ← дневные логи сессий (автоматически)
knowledge/
  concepts/         ← wiki-статьи (после compile)
  connections/      ← связи между концепциями
  qa/               ← Q&A-статьи (query --file-back)
  index.md          ← индекс всех статей
  log.md            ← лог операций
raw/                ← входящие документы для обработки
  processed/        ← обработанные файлы (перемещаются автоматически)
scripts/
  state.json        ← состояние: хеши, счётчики, total_cost
```

## Quality Audit

Flush автоматически проверяет качество извлечённых данных (Pass 2):
- Контент полезен → записывается в дневной лог как есть
- Контент бесполезен → помечается `<!-- AUDIT_FLAG: reason -->` (данные НЕ удаляются)
- Помеченные записи пропускаются при компиляции
- Если audit завершается с ошибкой → контент сохраняется (данные никогда не теряются)

## Учёт стоимости

Все вызовы LLM (compile, query, flush) накапливают стоимость в `scripts/state.json` → поле `total_cost`.
На Max-подписке стоимость $0.00, но метрика полезна, если вы перейдёте на API позднее.
