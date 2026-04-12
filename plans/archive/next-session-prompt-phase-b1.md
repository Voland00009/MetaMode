# Next-session prompt — Phase B.1: Base Setup + CLI Helper

**Дата handoff:** 2026-04-11
**Откуда пришли:** сессия Step 2-3 (plan writing). Полный implementation plan готов: `plans/implementation-plan.md`.

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
- `project_final_decision.md` — архитектурное решен��е
- `project_step2_3_plan.md` �� план (итоги Step 2-3)
- `feedback_session_per_step.md` — одна сессия = один шаг
- `feedback_no_permission_prompts.md` — не спрашивать разрешение на рутину

**0.2.** Прочитать `plans/implementation-plan.md` — ПОЛНЫЙ план, это основа.

**0.3.** Вызвать `mcp__plugin_mem0_mem0__search_memories` с query «MetaMode Phase B implementation plan» и фильтром:
```json
{"filters": {"AND": [{"user_id": "voland"}]}}
```

**0.4.** Подтверждение контекста:
- (а) Steps 2-3 завершены: plan готов, 9 tasks, 4 sessions
- (б) Эта сессия: Phase B.1 — Task 1 (Base setup) + Task 2 (claude_cli.py)
- (в) Вызвать `superpowers:executing-plans` + `superpowers:test-driven-development`

---

## Задача этой сессии

### Task 1: Base Project Setup

Следовать шагам 1-12 из `plans/implementation-plan.md` → Task 1.

**ВАЖНО перед Step 1:**
- Проверить `claude -p --help` чтобы узнать точные флаги (risk item #1, #2, #5, #6)
- Записать результат в план

### Task 2: CLI Helper Module (claude_cli.py)

Следовать шагам 1-5 из `plans/implementation-plan.md` → Task 2.

**ВАЖНО:**
- Сначала TDD: написать тест, убедиться что падает, написать код, убедиться что проходит
- После написания claude_cli.py — smoke test: `uv run python -c "from claude_cli import run_claude_prompt; print('Module loads OK')"`
- Если `claude -p` формат отличается от ожидаемого — обновить claude_cli.py и тесты

### Verification перед закрытием сессии

```bash
uv run python -c "from claude_cli import run_claude_prompt; print('OK')"
uv run python -m pytest tests/ -v
```

Оба должны пройти.

---

## Что НЕ делать
- ❌ Не писать flush.py/compile.py/lint.py — это B.2
- ❌ Не пересматривать архитектуру
- ❌ Не вызывать mem0 без `filters: {"AND": [{"user_id": "voland"}]}`
- ❌ Не спрашивать разрешение на рутину
- ❌ Не забыть проверить `claude -p --help` перед написанием кода
- ❌ Не добавлять резюмирующий параграф
