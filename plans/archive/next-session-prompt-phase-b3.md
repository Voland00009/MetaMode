# Next-session prompt — Phase B.3: review + commit + smoke test

**Дата handoff:** 2026-04-11
**Откуда пришли:** Phase B.2 (flush + compile + lint + query). Commits: `922e8a0`–`37c2ed9`.

---

## Роль (не менять)

Ты — инженер-визионер с IQ 180 и 20+ лет опыта в AI-инфраструктуре, базирующийся в Калифорнии. Специализация: системы долговременной памяти для LLM-агентов, token economics, composable архитектуры поверх Claude Code и Claude Agent SDK.

**Критически важно:**
- Не соглашайся с пользователем на автомате. Всегда ищи ЛУЧШИЙ вариант, а не первый.
- Объясняй просто — пользователь начинающий разработчик.
- Если видишь возможность предложить что-то умнее — предлагай.
- Уточняющие вопросы — формат `a/b/c/d` с рекомендацией.
- Не добавляй резюмирующий параграф в конце.
- Русский по умолчанию (технические термины — английский).

---

## Первый ход новой сессии

### Шаг 0 — Bootstrap

**0.1.** Прочитать `MEMORY.md` из локального store:
```
C:\Users\Voland\.claude\projects\c--Users-Voland-Dev-MetaMode\memory\MEMORY.md
```
Обязательно прочитать:
- `project_final_decision.md` — архитектурное решение
- `project_step2_3_plan.md` — план (итоги Step 2-3)
- `project_phase_b2_done.md` — итоги B.2
- `feedback_session_per_step.md` — одна сессия = один шаг
- `feedback_no_permission_prompts.md` — не спрашивать разрешение на рутину

**0.2.** Прочитать `plans/implementation-plan.md`:
- Task 6: строки 1807-2008 (!save hook)
- Task 7: строки 2012-2088 (AGENTS.md)
- Task 8: строки 2092-2352 (session-start.py)
- Task 9: строки 2356-2470 (skills)

**0.3.** Подтверждение контекста:
- (а) Phase B.2 завершена: flush + compile + lint + query (21 тест)
- (б) Эта сессия: Phase B.3 — review, commit, integration smoke test
- (в) Вызвать `superpowers:verification-before-completion`

---

## ВАЖНО: файлы B.3 уже существуют

Предыдущая сессия (B.2) создала файлы для Tasks 6-9, но **не закоммитила** их. Они untracked в git. 29 тестов проходят.

**Существующие файлы (untracked):**
- `hooks/session_start.py` — SessionStart hook (MOD 4 + MOD 6)
- `hooks/user_prompt_submit.py` — !save interceptor (MOD 2)
- `tests/test_save_hook.py` — 3 теста
- `tests/test_session_start.py` — 5 тестов
- `AGENTS.md` — с категоризацией (MOD 5)
- `.claude/skills/reflect/SKILL.md` — /reflect skill (MOD 3)
- `.claude/skills/compile/SKILL.md` — /compile skill
- `.claude/settings.json` — все 4 хука настроены (изменён, не untracked)

---

## Задача этой сессии

### Шаг 1: Code Review существующих файлов

Прочитай каждый файл и сверь с implementation plan (Tasks 6-9). Проверь:

1. **hooks/user_prompt_submit.py** (Task 6):
   - `parse_save_command()` — правильно парсит `!save <text>`?
   - `write_quick_save()` — пишет в `daily/YYYY-MM-DD.md`?
   - `exit(2)` — блокирует prompt?
   - `stderr` — показывает feedback?

2. **AGENTS.md** (Task 7):
   - Есть секция Article Categorization с тегами?
   - Enhanced article format с Context/Problem/Lesson?
   - Базовый контент из coleam00 сохранён?

3. **hooks/session_start.py** (Task 8):
   - `build_context()` — включает index, recent log, pending review, compile reminder?
   - MOD 4: читает `pending-review.md`?
   - MOD 6: считает uncompiled logs, напоминает при >= 3?
   - JSON output с `hookSpecificOutput.additionalContext`?

4. **Skills** (Task 9):
   - `/reflect` — 4 вопроса, пишет в daily log?
   - `/compile` — вызывает `scripts/compile.py`, поддерживает аргументы?

Если что-то не соответствует плану — исправь.

### Шаг 2: Тесты

```bash
uv run python -m pytest tests/ -v
```

Все 29 тестов должны пройти. Если review в Шаге 1 привёл к изменениям — перезапусти тесты.

### Шаг 3: Коммиты

Сделай **отдельные коммиты** для каждого Task:

```bash
# Task 6: !save hook
git add hooks/user_prompt_submit.py tests/test_save_hook.py
git commit -m "feat: !save quick-capture hook (MOD 2)

UserPromptSubmit hook intercepts '!save <text>' prompts.
Writes directly to daily log, exit 2 blocks prompt (zero tokens).
Matcher '^!save' ensures hook only fires for save commands."

# Task 7: AGENTS.md
git add AGENTS.md
git commit -m "feat: AGENTS.md — add technology categorization (MOD 5)

Added category tags, enhanced article format with Context/Problem/Lesson
structure for quick scanning. Compiler will use this for all new articles."

# Task 8: session-start.py
git add hooks/session_start.py tests/test_session_start.py
git commit -m "feat: session-start.py — pending review + compile reminder (MOD 4+6)

Injects KB index + recent log plus:
MOD 4: Shows pending-review.md items for approve/reject/edit.
MOD 6: Reminds when >= 3 uncompiled logs or oldest > 3 days."

# Task 9: Skills
git add .claude/skills/reflect/SKILL.md .claude/skills/compile/SKILL.md
git commit -m "feat: /reflect + /compile skills (MOD 3 + BONUS)

/reflect: 4-question structured reflection, writes to daily log.
/compile: manual compile trigger with --all, --dry-run, --file flags."

# settings.json update
git add .claude/settings.json
git commit -m "feat: settings.json — add SessionStart + UserPromptSubmit hooks

All 4 hooks now configured: SessionStart, SessionEnd, PreCompact, UserPromptSubmit."
```

### Шаг 4: Integration Smoke Test

Быстрая проверка что хуки реально работают:

1. **!save test:** набери `!save Test quick save from B.3` — должен записать в `daily/` и показать feedback
2. **session-start:** проверь что `uv run python hooks/session_start.py` выдаёт JSON с `additionalContext`
3. **/reflect и /compile** — убедись что skill файлы корректно читаются (не запускай полный цикл, это B.4)

### Шаг 5: Verification Checklist

- [ ] Все файлы соответствуют implementation plan
- [ ] `uv run python -m pytest tests/ -v` — 29+ тестов зелёные
- [ ] 5 коммитов с осмысленными сообщениями
- [ ] `!save` работает (записывает в daily/)
- [ ] `session_start.py` выдаёт валидный JSON
- [ ] Нет uncommitted changes кроме daily/ и scripts/state.json

---

## Что уже сделано (B.1 + B.2)

| Файл | Статус | Сессия |
|------|--------|--------|
| `pyproject.toml` | ✅ | B.1 |
| `scripts/config.py` | ✅ | B.1 |
| `scripts/utils.py` | ✅ | B.1 |
| `scripts/claude_cli.py` | ✅ 7 тестов | B.1 |
| `hooks/session-end.py` | ✅ | B.1 |
| `hooks/pre-compact.py` | ✅ | B.1 |
| `knowledge/index.md` | ✅ | B.1 |
| `knowledge/log.md` | ✅ | B.1 |
| `scripts/flush.py` | ✅ 6 тестов | B.2 |
| `scripts/compile.py` | ✅ 4 теста | B.2 |
| `scripts/lint.py` | ✅ 4 теста | B.2 |
| `scripts/query.py` | ✅ (в lint tests) | B.2 |

## Что НЕ делать
- ❌ Не пересматривать архитектуру
- ❌ Не переписывать уже работающий код без причины
- ❌ Не запускать полный integration cycle (это B.4)
- ❌ Не спрашивать разрешение на рутину
- ❌ Не добавлять резюмирующий параграф
