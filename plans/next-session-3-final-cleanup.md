# Next Session: Test Web Clipper Pipeline

## Context

MetaMode v1 полностью реализован. Memory cleanup завершён (mem0 удалён, stale файлы удалены, MEMORY.md чистый). Web Clipper установлен и настроен — шаблон "MetaMode RAW", путь `C:\Users\Voland\Dev\MetaMode\raw`.

Осталось протестировать Web Clipper pipeline.

## Task: Test Web Clipper end-to-end

1. Открой любую статью в браузере (что-то полезное — Python tip, архитектурный паттерн)
2. Клипни через Web Clipper с шаблоном "MetaMode RAW"
3. Проверь что файл появился в `raw/`
4. Запусти `uv run python scripts/ingest_raw.py`
5. Проверь что wiki-статья появилась в `knowledge/concepts/` или `knowledge/connections/`
6. Запусти `uv run python scripts/lint.py` — убедись что нет ошибок
7. Коммит результатов

## Constraints

- Русский по умолчанию
- Это финальная проверка — если pipeline работает, MetaMode v1 завершён
