# Сессия: Аудит MetaMode vs coleam00 + подготовка публичной версии

## Контекст

MetaMode v1 полностью работает, hooks перенесены в глобальные настройки (`~/.claude/settings.json`). Пользователь хочет:
1. Сделать чистую публичную версию для других людей
2. Для этого нужно честно разобраться в отличиях от оригинала (coleam00/claude-memory-compiler)

## Входные материалы

- **Оригинальный coleam00 репо:** https://github.com/coleam00/claude-memory-compiler — склонируй или прочитай через GitHub
- **Видео-транскрипт с описанием метода:** `c:/Users/Voland/Dev/MetaMode/input/New ASK/Transcrypt.txt`
- **Ссылки и контекст:** `c:/Users/Voland/Dev/MetaMode/input/New ASK/Info.txt`
- **Karpathy gist (оригинальная идея):** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- **Наш проект:** `c:/Users/Voland/Dev/MetaMode/` (весь код, hooks, scripts, knowledge)
- **Архитектурное решение:** auto-memory `project_final_decision.md`

## Задача 1: Глубокий аудит — что реально отличается

### Шаги:
1. **Склонируй coleam00/claude-memory-compiler** во временную папку (`c:/Users/Voland/Dev/temp-coleam00/`) и прочитай весь код
2. **Прочитай Karpathy gist** — это первоисточник идеи
3. **Сравни файл-по-файлу** с нашим MetaMode:
   - hooks/ — какие совпадают, какие изменены, какие добавлены
   - scripts/ — что именно поменялось в flush, compile, lint, query
   - AGENTS.md — наша версия vs оригинал
   - Структура данных (daily/, knowledge/, raw/)
4. **Составь честную таблицу:**

| Аспект | coleam00 оригинал | MetaMode | Кто лучше и почему |
|--------|-------------------|----------|-------------------|
| Установка | ? | ? | ? |
| Стоимость | SDK (API billing) | CLI ($0/mo на Max) | ? |
| Автозахват | ? | ? | ? |
| Ручной захват | ? | !save + /reflect | ? |
| Контроль качества | ? | pending review | ? |
| Глобальная работа | ? | глобальные hooks | ? |
| RAW inbox | ? | ingest_raw.py | ? |
| Compile | ? | ? | ? |
| Lint | ? | ? | ? |
| Query | ? | ? | ? |
| Документация | ? | ? | ? |

5. **Будь честным:** если coleam00 в чём-то лучше — скажи прямо. Не приукрашивай MetaMode.

## Задача 2: Проверка работоспособности (заодно)

Пока изучаешь код, проверь что всё работает:
1. `uv run python scripts/compile.py` — компиляция daily logs в wiki
2. `uv run python scripts/lint.py` — проверка здоровья wiki
3. `uv run python scripts/query.py "What do we know about Python import binding?"` — запрос к wiki
4. Проверь что hooks отрабатывают (session_start.py выдаёт JSON)

## Задача 3: Черновик README

На основе аудита напиши черновик README.md в `plans/README-draft.md`:
- Что это (1 абзац)
- Зачем (проблема → решение)
- Чем отличается от coleam00 (честная таблица)
- Быстрый старт (как поставить за 5 минут)
- Структура проекта
- Как пользоваться день-за-днём

**НЕ публикуй** — это черновик для ревью в следующей сессии.

## Важно

- Это исследовательская сессия — не торопись, читай код внимательно
- Если найдёшь баги или проблемы в MetaMode — запиши, но не чини (отдельная задача)
- Сохрани результаты аудита в wiki RAW (`raw/metamode-vs-coleam00-audit.md`)
