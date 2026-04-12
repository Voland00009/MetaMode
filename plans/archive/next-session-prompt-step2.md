# Next-session prompt — Phase A, Step 2-3: Algorithm + Order

**Дата handoff:** 2026-04-11
**Откуда пришли:** сессия Step 1 (CC tools inventory). Полный инвентарь механизмов CC, 7 финальных mechanisms, 5 комбинаций оценено. Результат: `plans/step1-cc-inventory.md`.

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
- `project_coleam00_codebase.md` — код coleam00
- `project_step1_inventory.md` — результат Step 1
- `project_skills_plan.md` — какие скиллы использовать
- `feedback_session_per_step.md` — одна сессия = один шаг
- `feedback_no_permission_prompts.md` — не спрашивать разрешение на рутину

**0.2.** Прочитать полный файл `plans/step1-cc-inventory.md` — это основа для Step 2.

**0.3.** Вызвать `mcp__plugin_mem0_mem0__search_memories` с query «MetaMode Phase A step 1 inventory mechanisms» и фильтром:
```json
{"filters": {"AND": [{"user_id": "voland"}]}}
```

**0.4.** Подтверждение контекста:
- (а) Step 1 завершён: 7 mechanisms, /compile добавлен
- (б) Эта сессия: Steps 2-3 — алгоритм реализации + порядок
- (в) Вызвать `superpowers:writing-plans` для структуры плана

---

## Задача этой сессии

### Step 2 — Алгоритм реализации (ОСНОВНОЙ)

Вызвать скилл **superpowers:writing-plans** и в его рамках проработать:

Для каждой из 6 модификаций + base setup:

1. **Base: clone + setup coleam00** — что нужно (Python, uv, git), какие файлы копировать, как адаптировать settings.json
2. **MOD 1: SDK → CLI** — какие файлы менять, как заменить SDK вызовы на `subprocess` + `claude -p`, edge cases (timeout, error handling, output parsing)
3. **MOD 2: !save hook** — UserPromptSubmit hook, парсинг input, куда писать, формат файла, exit 2 для zero-token
4. **MOD 3: /reflect skill** — skill-creator скилл для создания, 4 вопроса из AI Memory System, формат вывода
5. **MOD 4: pending review** — изменения в flush.py, формат pending-review.md, логика в session-start.py
6. **MOD 5: категоризация** — изменения в AGENTS.md, промпт для compile
7. **MOD 6: compile reminder** — логика в session-start.py, threshold
8. **BONUS: /compile skill** — skill для ручного compile (из Комбинации 4)

Для каждого: **входы → алгоритм → выходы → edge cases → зависимости**.

### Step 3 — Порядок реализации

- Что первым, что вторым
- Зависимости между модами
- Что можно параллелить
- Разбивка на сессии Phase B (1 сессия ≈ 1-2 часа)

### Step 4-5 — Если останется время

- Инструменты и зависимости (Python, uv, Obsidian, git)
- Зафиксировать план в `plans/implementation-plan.md`

---

## Контекст (знать наизусть)

### 7 mechanisms (из Step 1):
1. SessionStart hook — inject index + log + pending + reminder
2. SessionEnd hook — background flush.py
3. PreCompact hook — страховка flush.py
4. UserPromptSubmit hook — `!save` interceptor (exit 2, zero-token)
5. Skill /reflect — structured рефлексия
6. Skill /compile — ручной compile
7. `claude -p` — headless из flush/compile/lint/query

### Ключевые технические детали (из inventory):
- Hook stdin: `{session_id, transcript_path, cwd, prompt, ...}`
- SessionStart stdout: `{hookSpecificOutput: {additionalContext: "..."}}`
- UserPromptSubmit exit 2 = блокирует промпт, stderr = feedback
- `claude -p` flags: --max-turns, --permission-mode, --output-format json, --system-prompt-file
- Windows: `subprocess.CREATE_NO_WINDOW`
- Recursion guard: `CLAUDE_INVOKED_BY` env var
- Dedup: 60-sec cooldown по session_id

### Из coleam00 codebase review:
- session-start.py: ~80 строк, читает index.md + recent daily log
- session-end.py: ~130 строк, JSONL transcript, последние 30 turns, 15K chars limit
- flush.py: ~170 строк, LLM extraction, dedup, auto-compile after 18:00
- compile.py: ~150 строк, читает ВСЕ articles, LLM tools, acceptEdits, max_turns 30
- lint.py: ~220 строк, 7 checks (structural + LLM-based)
- query.py: ~80 строк, KB queries + Q&A filing

---

## Что НЕ делать
- ❌ Не писать код — только план
- ❌ Не пересматривать архитектуру без новых данных
- ❌ Не вызывать mem0 без `filters: {"AND": [{"user_id": "voland"}]}`
- ❌ Не спрашивать разрешение на mem0 записи и сохранение файлов
- ❌ Не забыть вызвать superpowers:writing-plans
- ❌ Не добавлять резюмирующий параграф
