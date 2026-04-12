# Сессия: Memory Cleanup — Шаги 4-5

## Context

Продолжение cleanup сессии. Шаги 1-3 выполнены (см. `memory/project_mem0_cleanup.md`):
- Полезные записи из mem0 спасены в CC auto-memory
- Плагин mem0 отключен и удалён из конфигов и файловой системы

## Шаг 4. Почистить CC auto-memory

Удалить устаревшие файлы из `~/.claude/projects/c--Users-Voland-Dev-MetaMode/memory/`:

| Файл | Причина удаления |
|------|-----------------|
| `feedback_mem0_filters.md` | mem0 больше не используется |
| `project_path_options.md` | варианты a/b/c, решение принято |
| `project_manual_save_ux.md` | решение принято, реализовано |
| `project_p3_critique_verdicts.md` | исторический интерес, не влияет |
| `project_sdk_max_cost_claim.md` | RESOLVED, факт в final_decision |
| `project_research_round.md` | завершён, синтез в отдельном файле |

После удаления — обновить `MEMORY.md` (убрать строки удалённых файлов).
Также удалить `project_mem0_cleanup.md` и его строку в MEMORY.md (cleanup завершён).

Показать список перед удалением и спросить подтверждение.

## Шаг 5. Проверка

1. Убедиться что в новой сессии нет "Mem0 Session Bootstrap" блока
2. Проверить SessionStart hook: `uv run python hooks/session_start.py`
3. Проверить что `MEMORY.md` чистый и актуальный

## Constraints

- Показывать список перед удалением, спрашивать подтверждение
- Не удалять ничего без явного "да"
