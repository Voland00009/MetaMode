# Сессия: Phase C Completion (Tasks 4 + 5 + Web Clipper)

## Context

MetaMode v1 — persistent wiki-memory поверх Claude Code. Живёт в `C:\Users\Voland\Dev\MetaMode`. Вся функциональная часть реализована: 4 этапа Карпати (RAW → Compiler → Wiki → Lint), 3 хука (SessionStart/End/PreCompact), 6 модификаций (SDK→CLI, !save, /reflect, pending review, категоризация, compile reminder), RAW inbox, cross-project доступ.

Осталось: проверить что всё работает сквозняком, навести порядок в репо, настроить Web Clipper.

Прочитай `CLAUDE.md` в корне проекта для полного контекста архитектуры.

## Task 4: Verify full cycle

Цель: убедиться что весь pipeline работает end-to-end.

### Чеклист проверки:

1. **SessionStart hook** — при старте этой сессии ты уже должен был получить inject из hook. Проверь: ты видишь index.md, recent daily log, RAW reminder? Если да — работает. Если нет — прочитай `hooks/session_start.py` и `scripts/flush.log` для диагностики.

2. **!save interceptor** — попроси пользователя написать `!save тестовая заметка для проверки цикла`. Проверь что запись появилась в `daily/YYYY-MM-DD.md`.

3. **flush.py** — посмотри `scripts/flush.log` на наличие свежих записей. Если есть записи с сегодняшней датой — flush работает.

4. **pending-review.md** — проверь `scripts/pending-review.md`. Если есть записи со статусом `pending` — покажи пользователю, пусть одобрит или отклонит. Одобренные — перенести в daily log через `append_to_daily_log()`.

5. **/compile** — запусти `/compile --dry-run` чтобы увидеть что будет скомпилировано. Потом `/compile` для реальной компиляции. Проверь что новые статьи появились в `knowledge/concepts/` или `knowledge/connections/`.

6. **lint** — запусти `uv run python scripts/lint.py`. Покажи результат пользователю. Исправь критические проблемы (битые ссылки, сироты).

7. **query** — запусти `uv run python scripts/query.py "что мы знаем о Python import time binding?"`. Убедись что ответ приходит из wiki.

8. **Obsidian** — попроси пользователя открыть Obsidian с vault на `knowledge/`. Убедись что граф связей отображается.

### Результат Task 4:
Запиши в daily log секцию "Full Cycle Verification" с результатами каждого пункта (pass/fail).

## Task 5: Cleanup

### 5.1 Git — привести в порядок

Текущие untracked файлы (из git status на 2026-04-12):
```
daily/                    → коммитить (данные, история)
decisions/                → коммитить (ADR)
dist/                     → .gitignore (build artifacts)
docs/archive/             → коммитить (legacy docs)
docs/critical_analysis.md → коммитить
docs/vision_v2_full.md    → коммитить
input/                    → коммитить (исходные материалы Карпати)
plans/NEXT-SESSION.md     → коммитить
plans/current-pitch.md    → коммитить
plans/implementation-plan.md → коммитить
plans/sessions/           → коммитить
plans/next-session-prompt-*.md → коммитить
plans/step1-cc-inventory.md → коммитить
scripts/compile.log       → .gitignore (runtime)
scripts/pending-review.md → .gitignore (runtime)
```

### 5.2 Обновить .gitignore

Добавить:
```
dist/
scripts/compile.log
scripts/pending-review.md
```

### 5.3 Архивировать завершённые планы

Создать `plans/archive/` и переместить туда:
- `plans/next-session-prompt-research-round.md`
- `plans/next-session-prompt-research-synthesis.md`
- `plans/next-session-prompt-checkin.md`
- `plans/next-session-prompt-creative-memory.md`
- `plans/next-session-prompt-event-level-memory.md`
- `plans/next-session-prompt-step2.md`
- `plans/next-session-prompt-phase-a.md`
- `plans/next-session-prompt-phase-b1.md`
- `plans/next-session-prompt-phase-b2.md`
- `plans/next-session-prompt-phase-b3.md`
- `plans/next-session-prompt-phase-c.md`
- `plans/next-session-prompt-phase-c-task2.md`
- `plans/current-pitch.md`
- `plans/step1-cc-inventory.md`

Оставить в `plans/`:
- `NEXT-SESSION.md` (актуальный handoff)
- `implementation-plan.md` (справочный, может пригодиться)
- `next-session-1-finish.md` (этот файл)
- `next-session-2-memory-audit.md` (следующая сессия)
- `sessions/` (история)

### 5.4 Финальный коммит

```
git add -A
git commit -m "chore: Phase C cleanup — archive plans, update .gitignore, commit data files

All Phase B+C implementation is complete. Archiving completed plan files,
adding runtime artifacts to .gitignore, committing daily logs and docs."
```

## Task 3 (partial): Web Clipper Setup

После Tasks 4+5, настроить Obsidian Web Clipper:

1. **Установить расширение** Obsidian Web Clipper для Chrome (obsidian.md/clipper)
2. **Настроить шаблон**: в настройках расширения (шестерёнка) → расположение заметки → `raw/`
3. **Установить плагин "Local Images Plus"** в Obsidian: Settings → Community Plugins → Browse → найти "Local Images Plus" → Install → Enable
4. **Написать `docs/web-clipper-setup.md`** — пошаговая инструкция (чтобы не забыть, если понадобится переустановить)
5. **Протестировать**: сохранить любую веб-страницу → появится в `raw/` → запустить `uv run python scripts/ingest_raw.py` → проверить что wiki-статьи создались

## Constraints

- Всё через `claude -p` (Max подписка, $0)
- Файлы в markdown, git versioning
- Минимум нового кода
- Порядок: Task 4 → Task 5 → Task 3
