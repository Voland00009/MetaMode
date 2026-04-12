# Next-session prompt — Phase B.4: Integration Testing

Каждый весомый шаг будем делать в новой сессии, чтобы не ловить ошибки.
Все изменения сохраняй.

**Дата handoff:** 2026-04-11
**Откуда пришли:** Phase B.3 (hooks + AGENTS + skills). Все 29 тестов проходят.

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
- `project_phase_b3_done.md` — итоги Phase B.3

**0.2.** Прочитать `plans/implementation-plan.md` — раздел "Verification Checklist (Session B.4)" (в самом конце файла).

**0.3.** Вызвать `mcp__plugin_mem0_mem0__search_memories` с query «MetaMode Phase B implementation» и фильтром:
```json
{"filters": {"AND": [{"user_id": "voland"}]}}
```

**0.4.** Подтверждение контекста:
- (а) Phase B.1 ✅: base setup + claude_cli.py (7 тестов)
- (б) Phase B.2 ✅: flush.py + compile.py + lint.py + query.py (14 новых тестов, 21 всего)
- (в) Phase B.3 ✅: !save hook + AGENTS.md + session-start + skills (8 новых тестов, 29 всего)
- (г) Эта сессия: Phase B.4 — Integration testing + smoke test

---

## Задача этой сессии

### Integration Testing — полный цикл MetaMode

Проверить что все компоненты работают вместе. Чеклист из плана:

1. `uv run python scripts/compile.py --dry-run` — показывает uncompiled logs
2. `uv run python scripts/lint.py --structural-only` — без ошибок
3. Старт новой CC сессии в MetaMode — увидеть KB index injected (session-start.py)
4. Ввести `!save Test quick save` — увидеть feedback, проверить daily log
5. Ввести `/reflect` — получить 4 вопроса, ответы сохраняются в daily log
6. Ввести `/compile` — компилирует daily logs в knowledge articles
7. Завершить сессию — flush.py запускается, пишет в pending-review.md
8. Начать новую сессию — увидеть pending review items в контексте
9. `uv run python scripts/query.py "What do I know?"` — получить ответ из KB

### Что скорее всего вскроется:
- Проблемы с путями на Windows (backslashes)
- Несовпадение форматов между hooks и scripts
- Проблемы с `claude -p` output parsing в реальных условиях
- Matcher regex для UserPromptSubmit — работает ли `^!save` на prompt text?

### Подход:
- Сначала прогнать unit тесты (29 должны пройти)
- Потом ручной smoke test каждого пункта
- Фиксить баги по ходу
- В конце — финальный commit с фиксами

---

## Что уже сделано (полная карта)

| Файл | Статус | MOD |
|------|--------|-----|
| `pyproject.toml` | ✅ | — |
| `scripts/config.py` | ✅ | — |
| `scripts/utils.py` | ✅ | — |
| `scripts/claude_cli.py` | ✅ 7 тестов | — |
| `scripts/flush.py` | ✅ 7 тестов | MOD 1+4 |
| `scripts/compile.py` | ✅ 3 теста | MOD 1 |
| `scripts/lint.py` | ✅ 4 теста | MOD 1 |
| `scripts/query.py` | ✅ | MOD 1 |
| `hooks/session-end.py` | ✅ | — |
| `hooks/pre-compact.py` | ✅ | — |
| `hooks/session_start.py` | ✅ 5 тестов | MOD 4+6 |
| `hooks/user_prompt_submit.py` | ✅ 3 теста | MOD 2 |
| `AGENTS.md` | ✅ | MOD 5 |
| `.claude/skills/reflect/SKILL.md` | ✅ | MOD 3 |
| `.claude/skills/compile/SKILL.md` | ✅ | BONUS |
| `.claude/settings.json` | ✅ | All hooks |
| `knowledge/index.md` | ✅ seed | — |
| `knowledge/log.md` | ✅ seed | — |
| `.gitignore` | ✅ | — |
| `tests/__init__.py` | ✅ | — |

## КРИТИЧЕСКОЕ отклонение от плана:
- Hook файлы используют подчёркивания (`session_start.py`, `user_prompt_submit.py`) вместо дефисов — Python не может импортировать модули с дефисами.
- `max_turns` убран из всех вызовов — флаг не существует.
- settings.json использует соответствующие имена файлов с подчёркиваниями.

## Что НЕ делать
- ❌ Не пересматривать архитектуру
- ❌ Не вызывать mem0 без `filters: {"AND": [{"user_id": "voland"}]}`
- ❌ Не спрашивать разрешение на рутину
- ❌ Не добавлять резюмирующий параграф
