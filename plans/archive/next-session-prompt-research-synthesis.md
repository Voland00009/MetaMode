# Next-session prompt — Research Synthesis (round 2)

**Дата handoff:** 2026-04-11 (поздний вечер)
**Откуда пришли:** сессия по `next-session-prompt-research-round.md`. Прошли bootstrap, подняли весь контекст из mem0 + inline материалов (Karpathy transcript, AI Memory System reference), сохранили memory в локальный store и в mem0, выдали три промпта P1/P2/P3 для копи-паста в Perplexity/Gemini/ChatGPT. Пользователь закрыл сессию до того, как отправил промпты в LLM.

---

## Роль (не менять)

Ты — инженер-визионер с IQ 180 и 20+ лет опыта в AI-инфраструктуре, базирующийся в Калифорнии. Специализация: системы долговременной памяти для LLM-агентов, token economics, composable архитектуры поверх Claude Code и Claude Agent SDK.

**Критически важно:**
- Не соглашайся с пользователем на автомате. Всегда ищи ЛУЧШИЙ вариант, а не первый.
- Объясняй просто — пользователь начинающий разработчик, многое видит впервые. Если бросаешь термин — сразу расшифровка.
- Если видишь возможность предложить что-то умнее — предлагай, с обоснованием. Самоцензура — нет.
- Когда задаёшь уточняющие вопросы — формат `a/b/c/d` с вариантами и твоей рекомендацией.
- Не добавляй резюмирующий параграф в конце.
- Русский по умолчанию (технические термины и код — английский).

---

## Первый ход новой сессии (строго по шагам)

### Шаг 0 — Bootstrap (КРИТИЧНО)

**0.1.** Прочитать `MEMORY.md` из локального memory store:
```
C:\Users\Voland\.claude\projects\c--Users-Voland-Dev-MetaMode\memory\MEMORY.md
```
Это индекс всех значимых файлов. Обязательно прочитать полностью (по 6 файлам, на которые он ссылается) — там лежит **весь** результат прошлой сессии: правила, конспекты Karpathy method и AI Memory System, cost claim, статус research round.

**0.2.** Вызвать `mcp__plugin_mem0_mem0__search_memories` с query «MetaMode research round Karpathy AI Memory System» и **обязательным** фильтром:
```json
{"filters": {"AND": [{"user_id": "voland"}]}}
```
⚠️ **Критично:** mem0 MCP tools не подставляют `user_id` автоматически, несмотря на обещание docstring. Без явного фильтра всегда возвращается 0 записей. См. `feedback_mem0_filters.md` в локальном store.

**0.3.** После bootstrap — 3 предложения подтверждения контекста пользователю: (а) что за проект, (б) где остановились (research round, 3 промпта выданы), (в) что делаем в этой сессии (принять результаты LLM → синтез → чекин → Phase A).

### Шаг 1 — Спросить пользователя о статусе промптов

Вопрос в формате `a/b/c/d`:

> Какие результаты по research round у тебя на руках?
> **(a)** Все три вернулись — сразу переходим к синтезу.
> **(b)** Часть вернулась (скажи какие) — начнём синтез по ним, остальные добавим позже.
> **(c)** Ни одного ещё нет — подожду, могу параллельно двигать SDK-on-Max тест или Phase 1 Mem0 T2.
> **(d)** Промпты ещё не отправлял — напомнить, где они лежат? Они в прошлом `next-session-prompt-research-round.md`, блоки P1/P2/P3.

**Рекомендация по ожиданию:** если пользователь ответил (c) — предложить **эмпирически верифицировать SDK-on-Max claim прямо сейчас** (см. `project_sdk_max_cost_claim.md`). Это 5 минут и даёт железный ответ на самый важный cost-вопрос MetaMode до возврата результатов.

### Шаг 2 — Если результаты есть: синтез

Пользователь вставит результаты одним или несколькими сообщениями. Когда все три на руках — начинай синтез **строго в этом порядке**:

1. **Единая таблица** 4×N: строки = конкретные факты/выводы; столбцы: «подтвердилось из handoff» / «опроверглось» / «новое» / «требует ещё проверки». Без этой таблицы дальше не идти.

2. **Сильнейшие критики из P3** — отдельный раздел. По каждому пункту: (а) принимаем и меняем план (как именно), ИЛИ (б) отвергаем с обоснованием (почему критик неправ для нашего сценария). Performative-согласие запрещено — см. skill `superpowers:receiving-code-review`.

3. **Manual save UX механизмы из P2 Q4** — ранжированные по трению и надёжности. **Обязательно** сравнить каждый с baseline `/reflect` из AI Memory System (лежит в `project_ai_memory_system.md`). Дать свою рекомендацию.

4. **Наложить inline материал вручную.** LLM не видели `input\New ASK\Transcrypt.txt` и `input\AI Memory System\`. При синтезе учитывать конспекты из локального store:
   - `project_karpathy_method.md` — полный метод + compile + lint + 7 проверок + цитаты
   - `project_ai_memory_system.md` — skill-driven подход + правила категоризации
   - `project_sdk_max_cost_claim.md` — ключевой cost unknown

5. **Чекин с пользователем** перед Phase A:
   - План остаётся (markdown + compile + hooks)?
   - Или нашли лучше (LightRAG / pure Obsidian / gibrid)?
   - Есть ли новые развилки, которые надо обсудить до инвентаря?

6. **Только после чекина** — Phase A. И тогда обязательно помнить `feedback_inventory_first.md`: **не сравнивать два очевидных варианта**, а сделать полный инвентарь ВСЕХ инструментов Claude Code (hooks, skills, subagents, MCP, SDK headless modes, CLAUDE.md hierarchy, background tasks, plugins, settings.json, keybindings) и предложить **3–5 нестандартных комбинаций**.

---

## Что категорически НЕ делать

- ❌ **Не начинать Phase A без синтеза и чекина.** Phase A = инвентарь. Синтез = интерпретация research. Это разные шаги.
- ❌ **Не писать код** до Phase C.
- ❌ **Не сравнивать только Mem0 vs Karpathy.** Третий путь обязателен (LightRAG / Obsidian-centric / git-versioned memory / agent-per-topic / hybrid).
- ❌ **Не соглашаться на автомате.** Пользователь хочет, чтобы я спорил, если не согласен.
- ❌ **Не пивотить Phase 1 Mem0** до завершения synthesis — T2–T5 как baseline.
- ❌ **Не добавлять резюмирующий параграф** в конце ответов (глобальная преференция).
- ❌ **Не вызывать mem0 search/get_memories без `filters: {"AND": [{"user_id": "voland"}]}`** — вернёт пусто и диагноз будет ложный.

---

## Инвентарь памяти (что уже сохранено — не дублировать)

### Локальный store (`C:\Users\Voland\.claude\projects\c--Users-Voland-Dev-MetaMode\memory\`)
- `MEMORY.md` — индекс
- `feedback_mem0_filters.md` — правило user_id в filters
- `feedback_inventory_first.md` — инвентарь + нестандартные комбинации перед архитектурой
- `project_karpathy_method.md` — полный конспект транскрипта Гришина/Карпати: структура raw/wiki, 3 хука (session_start/session_end/pre_compact), compile-on-idle через SDK, lint (7 проверок), query script, cross-project через путь в CLAUDE.md
- `project_ai_memory_system.md` — inline reference `input\AI Memory System\`: skill-driven (`/reflect` + `/lessons` + `/kb-maintain`), правила категоризации (технология, не ошибка, не проект), формат урока (Контекст/Проблема/Урок/Связанные)
- `project_sdk_max_cost_claim.md` — цитата про SDK headless на Max-подписке + план верификации
- `project_research_round.md` — статус round, 3 промпта, что делать при возврате

### Mem0 cloud (user_id=voland)
- `ed606d1b` — 6 архитектурных дыр Phase 1 Mem0 (greedy SessionStart top_k=10, infer=True black box, no PreCompact, no self-learning, no compile stage, strict cwd filter)
- `f081e8a3` — краткий Karpathy method
- `a77eaa23` — scope v1 вариант (c): CC-only, но схема расширяемая
- `62db0d94` — для v1 shared DB не планируется
- `f0566940` — NotebookLM как возможный layer, не foundation
- `394181a2` — event-level granularity как moat против Anthropic built-in
- `6a5e7109` — T1 closed, plugin skeleton в `~/.claude/plugins/metamode/`, Python venv + mem0ai SDK + get_client + smoke test passed
- `8be26b80` — Phase 1 status: T1 closed, T2–T5 pending
- `96e6ddcd` — не удалять skills/plugins, не трогать файлы в `c:\Users\Voland\Dev\MetaMode`
- `0027e931` — feedback: inventory all CC tools + unconventional combinations
- `fc481965` — план фаз A–D
- 4 новых записи от 2026-04-11 (могут ещё быть в статусе PENDING первые минуты):
  - AI Memory System как reference implementation
  - SDK-on-Max cost claim + план верификации
  - Research round launch status
  - Mem0 filters quirk как technical note

---

## Ключевые unknowns на начало следующей сессии

1. **SDK headless на Max-подписке бесплатно?** — самый высокий impact. Верифицировать эмпирически или через research citations. Если false — cost-модель markdown+compile разваливается.
2. **LightRAG overkill или нет для single-user <10k docs?** — решает, нужно ли Cat. 5 (локальный вектор).
3. **Manual save UX механизм** — `[MEM]` тег vs `/reflect` skill vs что-то третье от P2 Q4.
4. **Anthropic built-in memory decision tree** — что выживает из нашего плана, что становится obsolete.
5. **Lesson rot / prompt drift / context bloat** на горизонте 6–12 месяцев реальной работы.

---

## Цитаты пользователя (тон)

> «Лучше решить хоть какой-то вопрос, чем углубиться в космический корабль и не сделать вообще ничего.»

> «Сейчас самое важное для меня — прокачать тебя, чтобы я стал больше зарабатывать с помощью тебя.»

> «Раз все выбирают обсидиан или LightRag, то это не спроста. Видимо в этом есть смысл.»

> «Если есть решение, за которое придется платить и оно будет ЯВНО лучше, то мы с тобой обсудим варианты.»

> «Нужно очень обстоятельно и творчески подойти к этому процессу. Наша связка тут с тобой будет началом.»
