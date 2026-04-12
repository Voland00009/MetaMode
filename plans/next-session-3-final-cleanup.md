# Next Session: Final Cleanup + Memory Audit

## Context

MetaMode v1 полностью реализован и работает. Все фазы (B.1–B.3, C) завершены.
Последняя сессия memory cleanup удалила mem0 MCP plugin (292 записи, 95% мусор, 3 полезных сохранены в auto-memory).

Остались хвосты из memory cleanup + финальная уборка.

## Task 1: Finish memory cleanup (from pending action items)

### 1.1 Delete 6 stale auto-memory files

Удалить из `C:\Users\Voland\.claude\projects\c--Users-Voland-Dev-MetaMode\memory\`:

- `feedback_mem0_filters.md` — mem0 удалён, неактуально
- `project_path_options.md` — решение принято давно
- `project_manual_save_ux.md` — решение принято давно
- `project_p3_critique_verdicts.md` — исторический, неактуально
- `project_sdk_max_cost_claim.md` — resolved, неактуально
- `project_research_round.md` — completed, неактуально

После удаления — обновить `MEMORY.md`, убрав ссылки на удалённые файлы.

### 1.2 Verify SessionStart hook

Проверь что при старте сессии:
- НЕТ блока про mem0 bootstrap (был в session_start hook inject)
- Есть: wiki index, daily log, pending review, RAW reminder
- Нет ошибок в `scripts/flush.log`

### 1.3 Clean up CLAUDE.md references

Проверь `~/.claude/CLAUDE.md` и project `CLAUDE.md` — убери любые упоминания mem0 если есть.

## Task 2: Test Web Clipper pipeline

1. Открой любую статью в браузере
2. Клипни через Web Clipper с шаблоном "MetaMode RAW" в папку `C:\Users\Voland\Dev\MetaMode\raw`
3. Запусти `uv run python scripts/ingest_raw.py`
4. Проверь что wiki-статья появилась в `knowledge/concepts/`
5. Запусти lint: `uv run python scripts/lint.py`

## Task 3: Final commit

```
git add -A
git commit -m "chore: final cleanup — remove stale memories, approve pending review"
```

## Constraints

- Русский по умолчанию
- Минимум действий — только чистка, никаких новых фич
- Коммит в конце
