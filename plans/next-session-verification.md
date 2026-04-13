# Next Session: Final Verification Pass

## Context

Пользователь дал 9 требований для MetaMode. За 2 сессии (Phase 1 + Phase 2) было сделано много работы. Нужна финальная верификация: все ли 9 пунктов закрыты.

## Original 9 Requirements (status)

### 1. GitHub Issues — баги от @ub3dqy
**DONE** (commit 90d78aa, issues #1-#3 closed)
- Timezone: `METAMODE_TIMEZONE` env var, `now_local()` everywhere
- pre_compact: MIN_TURNS = 1
- flush.py: subprocess error handling

### 2. Интеграции Obsidian + NotebookLM — описание в репо
**DONE** — docs/obsidian-setup.md, docs/notebooklm-setup.md, docs/raw-inbox.md
**VERIFY:** Открыть каждый doc, проверить что ссылки работают, инструкции полные.

### 3. Obsidian — сценарии использования (wiki как vault, backlinks, graph)
**DONE** — docs/obsidian-setup.md содержит 5 use cases
**VERIFY:** Проверить что описание "страница в Obsidian → сразу в мозг Claude" корректно. Механизм: wiki/ = vault, hook session_start инжектирует index.md → Claude видит.

### 4. NotebookLM — skills, баги, сценарии использования
**PARTIALLY DONE:**
- Skills добавлены в skills/ (notebooklm, wrapup)
- docs/notebooklm-setup.md написан с 6 use cases
- **НЕ ПРОВЕРЕНО:** баг с перелогиниванием. В memory есть инфо что auto-refresh cookies настроен через Task Scheduler каждые 6h. Но auth expired в текущей сессии → нужно проверить Task Scheduler.
- **VERIFY:** Работает ли auto-refresh? Если нет — починить или документировать как known limitation.

### 5. Нативная связка инструментов — описание совместной работы
**PARTIALLY DONE:** Каждый doc описывает свой инструмент отдельно.
**VERIFY:** Есть ли описание того, КАК инструменты работают ВМЕСТЕ? Нужен раздел/doc о workflow: Claude Code → MetaMode → Obsidian → NotebookLM. Если нет — создать.

### 6. RAW Inbox — загрузка файлов, анализ, запоминание
**DONE** — docs/raw-inbox.md с 6 use cases
**VERIFY:** Проверить что описание полное и понятное для нового пользователя.

### 7. Глобальная установка (не в проект)
**DONE** — hooks в ~/.claude/settings.json, README документирует это
**VERIFY:** README hooks section показывает правильный формат с matcher/timeout.

### 8. Обновление системных файлов памяти (memory lint 14d)
**DONE** — session_start.py проверяет last_memory_lint, 14-day threshold
**VERIFY:** Документировано ли в README? Да, в секции Maintenance.

### 9. Repo = Local parity
**DONE** — аудит проведён, README обновлён, ветки синхронизированы
**VERIFY:** Прогнать финальную проверку: `git status` чист? `git diff origin/main` = 0?

## Action Items для верификации

1. Открыть docs/obsidian-setup.md, docs/notebooklm-setup.md, docs/raw-inbox.md — проверить полноту
2. Проверить Task Scheduler для NotebookLM cookie refresh
3. Решить: нужен ли отдельный doc "how tools work together" (п.5)?
4. Проверить что RAW inbox содержит 3 новых файла, запустить ingest
5. Финальный git status — все чисто?

## Prompt для следующей сессии

```
Финальная верификация MetaMode.

План: plans/next-session-verification.md
Контекст: за 2 сессии закрыты 9 требований пользователя (GitHub issues, интеграции, docs, parity). Нужна финальная проверка что ВСЁ на месте.

Главные вопросы:
1. Открой все 3 integration docs — полные ли инструкции?
2. NotebookLM auth expired — проверь Task Scheduler "NotebookLM Cookie Refresh", работает ли?
3. Нужен ли отдельный doc о совместной работе инструментов (Obsidian + NotebookLM + MetaMode)?
4. Обработай RAW inbox (3 новых файла)
5. Git status — всё чисто и запушено?

Критерий: человек клонирует репо и получает ВСЁ из коробки.
```
