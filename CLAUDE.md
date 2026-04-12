# MetaMode

## Что это
Persistent memory layer поверх Claude Code — fork coleam00/claude-memory-compiler + 6 модификаций. Karpathy-inspired wiki-память: hooks автоматически захватывают сессии, compile превращает daily logs в structured wiki-статьи, lint следит за здоровьем базы.

## Stack
- Language: Python (из coleam00)
- Package manager: uv
- Base: coleam00/claude-memory-compiler (fork)
- Integration: Claude Code hooks (SessionStart, SessionEnd, PreCompact, UserPromptSubmit) + skills (/reflect)
- LLM calls: `claude-agent-sdk` (Claude Agent SDK, покрыт Max подпиской, $0/mo)
- UI: Obsidian (knowledge/ как vault)
- Versioning: git

## Архитектура (решение 2026-04-11, не менять без новых данных)

### Из coleam00 (as-is):
- hooks/ — SessionStart (inject index), SessionEnd (flush), PreCompact (страховка)
- scripts/ — flush.py, compile.py, lint.py, query.py, config.py, utils.py
- AGENTS.md — схема статей
- daily/ → knowledge/ (concepts/, connections/, qa/)

### 6 модификаций:
1. ~~SDK → subprocess `claude -p`~~ Migrated back to SDK (2026-04-12, SDK confirmed on Max)
2. `!save` interceptor hook (UserPromptSubmit, quick capture)
3. `/reflect` skill (structured рефлексия, 4 вопроса)
4. Pending review в flush.py (полу-авто: предлагает → user approves)
5. Категоризация по технологии/домену в AGENTS.md
6. Compile reminder при SessionStart

Детали: см. `memory/project_final_decision.md` в локальном store.

## Принципы
1. **Hybrid save: auto + manual** — hooks захватывают автоматически, !save и /reflect — по запросу. Human-in-the-loop для качества.
2. **File-first** — всё в markdown, git versioning. File corpus выживает в любом Anthropic-сценарии.
3. **$0/mo** — никаких API ключей, облачных сервисов, платных зависимостей. Только Max подписка.
4. **Fork, don't rewrite** — берём проверенный код coleam00, модифицируем минимально.

## Conventions
- Tests: покрывается логика save/retrieve/compile; glue-код hooks — best effort
- Commits: объясняют ПОЧЕМУ, не только ЧТО
- Session workflow: одна задача = одна сессия

## Что НЕ делать
- ~~Не использовать Claude Agent SDK напрямую~~ SDK подтверждён на Max (2026-04-12)
- Не добавлять LightRAG/vector DB (overkill для <1K docs, единогласно P1+P2+P3)
- Не добавлять полный auto self-learning (drop'нут в v1, заменён на pending review)
- Не тащить legacy mentor protocol из docs/archive/

## Где что лежит
- `plans/next-session-prompt-phase-a.md` — промпт следующей сессии (Phase A: planning)
- `plans/sessions/` — история сессий
- `plans/archive/` — завершённые/отменённые pitches
- `decisions/` — ADR (архитектурные решения)
- `docs/vision_v2_full.md` — широкое видение MetaMode (контекст)
- `docs/archive/` — legacy материалы

## Hooks

- SessionStart: inject index.md + recent log + pending review + compile reminder + RAW reminder
- SessionEnd: extract transcript → flush.py (background)
- PreCompact: страховка → flush.py (background)
- UserPromptSubmit: `!save` interceptor

## RAW Inbox

Когда пользователь говорит "обработай RAW", "process RAW" или "я добавил статью в RAW":

1. Прочитай файлы из `raw/` (кроме README.md и `raw/processed/`)
2. Запусти `uv run python scripts/ingest_raw.py` — создаст wiki-статьи в `knowledge/concepts/` и `knowledge/connections/`, обновит `index.md`
3. Обработанные файлы автоматически перемещаются в `raw/processed/`
