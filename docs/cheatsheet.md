# MetaMode Cheatsheet

## Автоматическое (работает само)

| Что | Когда | Как |
|-----|-------|-----|
| **Session flush** | При завершении сессии Claude Code | Hook `SessionEnd` → `flush.py` в фоне |
| **Quality audit** | Сразу после flush | Pass 2 в `flush.py` — LLM проверяет качество |
| **Pre-compact страховка** | При сжатии контекста | Hook `PreCompact` → `flush.py` |
| **KB index injection** | При старте сессии | Hook `SessionStart` → `session_start.py` |
| **Auto-compile** | После flush, если > 18:00 | `flush.py` → `compile.py` в фоне |

## Ручные команды

### Быстрое сохранение
```
!save <текст>
```
Сохраняет заметку в daily log прямо из чата. Поддерживает кириллицу.

### Компиляция в wiki
```
uv run python scripts/compile.py
uv run python scripts/compile.py --all          # перекомпилировать всё
uv run python scripts/compile.py --file <path>  # один файл
uv run python scripts/compile.py --dry-run      # показать что будет
```
Или в чате: `/compile`

Превращает daily logs в wiki-статьи (`knowledge/concepts/`, `knowledge/connections/`).

### Запрос к базе знаний
```
uv run python scripts/query.py "Как работает X?"
uv run python scripts/query.py "Паттерн Y" --file-back  # сохранить ответ как Q&A статью
```
Ищет по wiki и синтезирует ответ.

### Линтер
```
uv run python scripts/lint.py
```
7 проверок: broken links, orphan pages, orphan sources, stale articles, missing backlinks, sparse articles, contradictions (LLM).

### Обработка RAW inbox
```
uv run python scripts/ingest_raw.py
```
Или в чате: скажи `обработай RAW`

Обрабатывает файлы из `raw/` → создаёт wiki-статьи, перемещает в `raw/processed/`.

### Рефлексия
В чате: `/reflect`

4 вопроса о сессии → структурированная запись в daily log.

## Когда что использовать

| Ситуация | Действие |
|----------|----------|
| Узнал что-то важное прямо сейчас | `!save <инсайт>` |
| Нашёл статью/видео для базы | Сохрани в `raw/`, потом `обработай RAW` |
| Накопилось 3+ daily logs | `uv run python scripts/compile.py` |
| Хочешь найти что-то в базе | `uv run python scripts/query.py "вопрос"` |
| Конец рабочей сессии | `/reflect` (или просто закрой — flush автоматический) |
| Проверить здоровье wiki | `uv run python scripts/lint.py` |

## Где что лежит

```
daily/              ← дневные логи (автоматически)
knowledge/
  concepts/         ← wiki-статьи (после compile)
  connections/      ← связи между концептами
  qa/               ← Q&A статьи (query --file-back)
  index.md          ← индекс всех статей
  log.md            ← лог операций
raw/                ← входящие статьи для обработки
  processed/        ← обработанные файлы
scripts/
  state.json        ← состояние: хэши, счётчики, total_cost
```

## Quality Audit

Flush автоматически проверяет качество извлечённых данных (Pass 2):
- Если контент полезный → пишет в daily log как есть
- Если мусор → помечает `<!-- AUDIT_FLAG: причина -->` (данные НЕ удаляются)
- Помеченные записи пропускаются при compile
- Если аудит упал с ошибкой → считаем "всё ОК" (данные не теряются)

## Cost Tracking

Все LLM-вызовы (compile, query, flush) накапливают стоимость в `scripts/state.json` → поле `total_cost`.
На Max подписке стоимость = $0.00, но метрика полезна при переходе на API.
