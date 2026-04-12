# Next-session prompt — Research round (верификация landscape памяти)

**Дата handoff:** 2026-04-11 (ночь)
**Откуда пришли:** сессия по `next-session-prompt-event-level-memory.md`. Прошли все ключевые развилки: event-level moat понят, гибрид auto+manual принят, рамка ADHD смягчена до v2, Mem0 признан «прошлым сервисом» (fast-start hack), направление склонилось к markdown+compile. Контекстное окно закончилось до запуска research round — переходим сюда.

---

## Роль (не менять)

Ты — инженер-визионер с IQ 180 и 20+ лет опыта в AI-инфраструктуре, базирующийся в Калифорнии. Специализация: системы долговременной памяти для LLM-агентов, token economics, composable архитектуры поверх Claude Code и Claude Agent SDK.

**Критически важно:**
- Не соглашайся с пользователем на автомате. Всегда ищи ЛУЧШИЙ вариант, а не первый.
- Объясняй просто — пользователь начинающий разработчик, многое видит впервые. Если бросаешь термин — сразу расшифровка.
- Если видишь возможность предложить что-то умнее — предлагай, с обоснованием. Самоцензура — нет.
- Когда задаёшь уточняющие вопросы — формат `a/b/c/d` с вариантами и твоей рекомендацией.
- Не добавляй резюмирующий параграф в конце (глобальная преференция пользователя).

---

## Mission (важные коррекции — не теряй!)

**v1 (сейчас):** связка «пользователь + Claude» становится умнее за счёт общей персистентной памяти. **Пользователь** делает свою работу (приложения, сайты, автоматизации) быстрее, дешевле по токенам, качественнее и в итоге **зарабатывает больше**. Claude — инструмент этого усиления, не самоцель. «Прокачать Claude» = прокачать результат пользователя через него. Масштаб: один пользователь + Claude.

**v2 (потом):** на базе той же концепции — продукт для ADHD-аудитории. **Задел в архитектуре v1 делаем** (файловые схемы и хранилище расширяемы), но **не подстраиваем v1 под ADHD**. v1 должна работать для пользователя и Claude уже сегодня, без compromises.

---

## Hard constraints (важные коррекции — не теряй!)

### 1. Не космический корабль
MVP, который работает сегодня, бьёт изящную архитектуру, которую надо полгода строить. **«Лучше решить хоть какой-то вопрос, чем утонуть в идеальном проекте»** — прямая цитата пользователя.

### 2. Cost: ноль подписок в идеале (коррекция от пользователя)
**КРИТИЧЕСКАЯ КОРРЕКЦИЯ:** наличие у пользователя Claude Max / Gemini Pro / Perplexity Pro / ChatGPT Plus **НЕ означает**, что на них можно закладывать архитектуру. Рассуждение пользователя: «у других людей этих подписок не будет». То, что Obsidian и LightRAG выбирают — не случайно: они free и самодостаточны, это сигнал.

Платное решение допустимо **только при выполнении одного из условий**:
- **(a)** оно явно лучше бесплатных аналогов, ИЛИ
- **(b)** оно всё равно понадобится в v2 (ADHD-продукт), и начать на нём сейчас дешевле, чем потом переписывать.

Если хоть одно из этих — **обсуждаем с пользователем перед принятием**, не решаем в одиночку.

### 3. Mem0 = «прошлый сервис» (fast-start hack)
Это был быстрый старт, не выбор по существу. Phase 1 T2–T5 **доводим как эмпирический baseline** — получим реальные цифры «что Mem0 запомнил, что вытащил, где промахнулся». Но **архитектуру дальше на Mem0 не строим**. Параллельно строим markdown+compile и сравниваем обе на 2–3 реальных сессиях.

---

## Что уже решено в предыдущих сессиях

1. **Event-level память** понята: пишем на значимые события (`PostToolUse`, `UserPromptSubmit`, `SubagentStop`, `Notification`), а не один summary в конце сессии. Гранулярность = одно решение / факт / действие.

2. **Hybrid save** принят: автоматический через хуки **плюс** ручной «запомни это сейчас». Пользователь никогда не доходит до auto-compact — пересаживается на новую сессию при ~40% свободного контекста. Значит **`PreCompact` hook как primary save НЕ подходит** — нужен другой жизненный цикл (скорее всего связка Stop hook + manual trigger + session-end ritual).

3. **Скоуп v1:** Claude Code only, но схема файлов и метаданных — расширяемая. Потом можно будет лить данные из других источников (browser Claude, голос, мобильный, заметки) без рефакторинга. [Это выбор (c) из обсуждённого.]

4. **NotebookLM** — пользователь уже параллельно заливает туда данные, Claude имеет доступ, но NotebookLM часто глючит. Учитывать как **возможный layer**, не как опору. Широкое мышление.

5. **Friends:** общая база на несколько человек **не рассматривается**. Для v1 — однопользовательская архитектура. Может потом скриптом поделиться локально (каждый своя база) — это «возможно позже».

6. **6 архитектурных дыр текущего Phase 1 на Mem0** уже сформулированы и лежат в mem0 как отдельная запись: (1) жадный SessionStart, (2) Mem0 extract через `infer=True` — чёрный ящик, (3) нет `PreCompact` хука, (4) self-learning отложен, (5) нет compile-этапа, (6) жёсткий cwd-фильтр убивает cross-project reuse.

7. **Направление, к которому склонились:** Категория 4 (markdown + compile-on-idle в духе Karpathy) с возможным расширением в Категорию 5 (+ локальный векторный индекс: sqlite-vec / LanceDB / Chroma local). **НЕ окончательно** — надо верифицировать свежим ресёрчем и adversarial стресс-тестом.

---

## Сжатый обзор 5 категорий памяти (для быстрого вспоминания)

- **Кат. 1 — Cloud SaaS** (Mem0, Supermemory, Zep Cloud). Плюсы: zero ops, semantic search из коробки. Минусы: vendor lock-in, opacity (infer=True чёрный ящик), cost rising, privacy. → Mem0 закрываем как baseline, дальше не строим.
- **Кат. 2 — Self-hosted graph** (Graphiti, Cognee). Neo4j + Docker + ops. → Overkill для single-user, отброшена.
- **Кат. 3 — Self-hosted agent frameworks** (Letta/MemGPT). → Дублирует Claude Code, отброшена.
- **Кат. 4 — Markdown + compile-on-idle** (Karpathy, claude-mem, coleam00/claude-memory-compiler). $0, transparency, portability, ADHD-ready для v2. Минус: compile-слой надо построить (~200–400 LoC).
- **Кат. 5 — Markdown + локальный векторный индекс** (sqlite-vec, LanceDB, Chroma local). Кат. 4 + быстрый semantic search, всё локально, всё бесплатно.

**Текущий favorite: Кат. 4 с заделом под Кат. 5.** Но research round должен это подтвердить или опровергнуть.

---

## ТВОЯ ПЕРВАЯ ЗАДАЧА В НОВОЙ СЕССИИ: запустить Research Round

**НЕ бросайся в Phase A (инвентарь инструментов) и НЕ бросайся в код.** Пользователь сказал прямо: «нужно очень обстоятельно и творчески подойти к этому процессу». Research round — следующий логический шаг.

### Цели research round

1. **Верифицировать knowledge cutoff.** Мой (Claude) cutoff — май 2025. Текущая дата — апрель 2026. Надо подтвердить, что в ноябре 2025 – апреле 2026 не появилось радикально нового в landscape памяти агентов.
2. **Подтвердить или опровергнуть** склонность к markdown+compile свежими данными и adversarial атакой.
3. **Собрать варианты manual save trigger UX** — пользователь не может голосом, мобильный русский ввод глючит. Это отдельный research-вопрос.
4. **Включить в обзор** то, что я мог пропустить: Obsidian-centric workflows, LightRAG, NotebookLM integration, новые 2026 entrants.

### Три готовых промпта (копи-паста, специализированные)

**Дай пользователю три промпта ниже.** Он вставит их в три LLM (Perplexity Pro, Gemini Deep Research, ChatGPT GPT-5/o3), вернёт результаты. Затем ты синтезируешь. Не меняй промпты по своему усмотрению без согласования с пользователем.

---

### ПРОМПТ P1 — Perplexity Pro (свежие факты + цитаты)

```
I'm designing a persistent memory layer for Claude Code (Anthropic's CLI coding agent) for personal long-term use — one developer, daily sessions, multiple coding projects. Budget ideal: $0/month extra subscriptions. Willing to pay only if clearly superior AND useful for a future broader product.

I need a fresh survey (as of today) of the current state of memory solutions for AI coding agents, with citations and dates. Be factual and current — don't rely on pre-2025 info.

Cover specifically:

1. Mem0 (mem0ai) current status — free tier limits, pricing tiers, 2025–2026 changes, production feedback (Reddit, HN, GitHub issues), known limitations.

2. Open-source / self-hosted memory options for single-user scale:
   - LightRAG (HKUDS/LightRAG) — architecture, minimum hardware, learning curve, who uses it in production at single-user scale, is it overkill for <10k documents.
   - Graphiti (getzep/graphiti) — current state, operational burden.
   - Cognee — same.
   - Letta (formerly MemGPT) — 2026 positioning.

3. Markdown / file-based memory workflows for Claude Code specifically:
   - claude-mem (any version on GitHub/npm)
   - coleam00/claude-memory-compiler (Karpathy-inspired approach)
   - Anyone using Obsidian as storage layer for agent memory — how, what tooling, which plugins
   - Public blog posts or GitHub projects doing "compile-on-idle" via Claude Agent SDK headless

4. NotebookLM integration (Google):
   - Public API status in 2026
   - Can it be used as a memory backend for an agent workflow?
   - Known failure modes when embedded in automated pipelines

5. New entrants 2026 — what's considered "state of the art" for single-user developer memory today that I might not know about?

6. Claude Code hooks / extension specifics — what hooks does Claude Code currently expose (SessionStart, Stop, PreCompact, UserPromptSubmit, PostToolUse, SubagentStop, Notification), any documented patterns for implementing manual "save this moment" triggers in a text-only chat interface (no voice, unreliable mobile input).

Format: bullet points per solution, each with source URL + date of source. Mark which sources are 2026 vs older. Explicitly call out anything where you're uncertain or can't find recent data.
```

---

### ПРОМПТ P2 — Gemini Deep Research (глубокий comparative)

```
Run a deep research task on this question.

CONTEXT: I'm designing a personal persistent memory layer for a developer using Claude Code (Anthropic's CLI coding agent). Goal: accumulate reusable "lessons learned" across sessions so the agent doesn't repeat mistakes and the developer becomes more productive per token spent. Single user, daily use, 1–3 year horizon, multiple coding projects. Budget target: $0/month extra infrastructure.

SPECIFIC QUESTIONS:

1. COMPARATIVE ARCHITECTURE REVIEW (primary)
Compare three memory architectures for single-user long-term developer use:
  A. Pure markdown files + compile-on-idle (periodic LLM run reads raw session logs, writes structured "lessons" in markdown files; retrieval via file loading indexed by topic)
  B. LightRAG (graph+vector hybrid over plain text, self-hosted)
  C. Mem0 cloud SaaS (current use, considering alternatives)

For each, answer:
- Failure modes over 6–12 months of real daily use (what degrades, breaks, rots?)
- Retrieval quality as base grows from 100 → 10,000 entries
- Maintenance burden (what breaks, how often, recovery effort)
- Cost curve (infrastructure, API tokens, storage, maintenance time)
- Privacy/data-locality implications
- Extensibility: what does it take to add a new data source later (e.g., notes from browser, voice transcripts, mobile inbox)

2. MARKDOWN COMPILE-ON-IDLE DETAILS
Find real production examples (public GitHub repos, blog posts, Karpathy's approach specifically):
- How do they structure the raw-log → compiled-lesson pipeline?
- How do they prevent "lesson rot" (outdated or contradictory entries accumulating over time)?
- What does the compile prompt look like?
- How do they index compiled lessons for retrieval (index.md, frontmatter, embeddings, all of the above)?
- Typical code size (lines of code) for a working MVP?

3. LIGHTRAG AT SINGLE-USER SCALE
Honest assessment: is LightRAG overkill for one developer's memory base (expected <10k documents over a year)? Who runs it at this scale? Are there minimal deployment setups (<200 LoC, no docker, no GPU)? What does it give us that pure markdown+compile doesn't?

4. MANUAL SAVE TRIGGER UX PATTERNS (separate important sub-question)
I need a way for the user to say "save this specific moment" during a chat session with Claude Code. Hard constraints:
- Text-only input (no voice capability in the Claude Code TUI)
- Mobile Russian input is unreliable (so can't depend on mobile speech-to-text)
- Must work inside the existing Claude Code chat flow
- Ideally zero friction

Research patterns used in:
- Claude Code hooks (UserPromptSubmit, slash commands, custom skills)
- Obsidian community workflows for "quick capture"
- Text-based chat applications with memory features
- Academic/UX literature on capturing "this is important" signals in conversational interfaces

Propose 4–6 distinct mechanisms, ranked by friction and reliability. For each mechanism, describe: how it works, what breaks it, and what it depends on in Claude Code's current API.

5. HYBRID STRATEGIES
Any evidence that hybrid approaches (markdown primary + optional local vector index for speed; or markdown + graph for cross-linking) actually outperform pure markdown at our scale? At what point does complexity start hurting more than helping?

OUTPUT: thorough comparative report with citations and source dates. Don't refuse to recommend — at the end, give me your top-1 recommendation with reasoning, and the top alternative I should seriously consider.
```

---

### ПРОМПТ P3 — ChatGPT GPT-5 / o3 (adversarial stress test)

```
You are an adversarial technical critic. Be direct, not polite. Find every weakness.

CONTEXT:
I'm designing "MetaMode" — a persistent memory layer that sits on top of Claude Code (Anthropic's CLI coding agent). Goal: one developer + Claude Code accumulate reusable knowledge across sessions so mistakes don't repeat and each session starts with relevant context already in memory.

MY CURRENT DIRECTION:
- Primary storage: markdown files on local disk
- Compile-on-idle: background process using Claude Agent SDK headless periodically reads raw session logs and writes structured "lessons learned" markdown files
- Retrieval: SessionStart hook loads only a small index.md (~200 words); specific lessons pulled in on trigger via skills or UserPromptSubmit hook routing
- Save events: Stop hook writes session transcript + "important moments" (captured via manual trigger in-chat) to a raw log folder
- Cost target: $0/month extra (beyond Claude Max subscription the user already has — but ideally even Max-independent for portability to other users)
- Scale: single user, 1–3 years, daily use, multiple coding projects
- Running parallel track: Mem0 cloud as baseline (will finish empirically for comparison data, but not building architecture further on it)

HARD REQUIREMENTS:
1. Auto-save via hooks (no manual ceremony required)
2. Self-learning (don't repeat past mistakes — this is the whole point)
3. Token economy (lazy retrieval, small SessionStart footprint)
4. $0/mo ideal, cheap if paid (must work without user having any paid subscriptions beyond what's necessary for Claude itself)
5. Transparency (user reads memory files by eye, edits by hand if needed)
6. Moat-awareness (Anthropic will release built-in memory; this solution must remain useful in that world)
7. Portable (files, no vendor lock-in)

YOUR JOB — FIND EVERY WEAKNESS:

1. Where is the cost hidden? Compile-on-idle runs Claude through Agent SDK — how many tokens per day realistically at steady state? What happens if user doesn't have Claude Max? Under what assumptions does "$0/month" collapse?

2. Where does "self-learning" fall apart? Does periodic LLM-compile actually produce lessons that get correctly retrieved next session, or is this theater that feels productive without real benefit? Give concrete failure scenarios with examples.

3. Where does the ~200-line MVP claim break? What engineering effort am I under-estimating? List every hidden corner: error handling, concurrency, log rotation, compile prompt drift, redaction of secrets, schema migration, index staleness, etc.

4. What assumptions collapse on first contact with real data? Think about: file system bloat, prompt rot, context window pressure, compile prompt drift, noise vs signal in event stream, token explosion at scale, inherited bugs in existing tooling.

5. What's the strongest alternative architecture I should be considering and am probably dismissing too quickly? Specifically evaluate: LightRAG, pure Obsidian-based workflow with Templater/Dataview, git-based versioned memory with semantic diff, agent-per-topic architecture.

6. The 7 requirements — any logical contradictions between them? For example: "$0/mo" vs "self-learning via LLM compile" — does the math actually work? "Transparency" vs "semantic retrieval" — do they conflict in practice?

7. Anthropic releases built-in session memory in the next 6 months — what exactly becomes obsolete in my plan? What survives? What gets weaker? Draw the decision tree.

8. What would make a competent senior engineer say "this is overengineered" or "this is undercooked"? Be specific.

9. Manual save trigger UX: user cannot use voice, mobile Russian input is unreliable. My current idea is a text tag like `[MEM]` inside normal chat that a UserPromptSubmit hook detects. Tear this apart and propose something better.

Don't be balanced. Find flaws. I will decide what to keep and what to drop. Length: as long as needed to be thorough. Structured output preferred (numbered findings, severity labels).
```

---

## Что делать, когда результаты вернутся

1. **Свести в одну таблицу:**
   - Что подтвердилось из того, что я уже думал
   - Что опроверглось
   - Что появилось нового
   - Что нужно ещё проверить
2. **Отдельно выписать:** сильнейшие критики из P3 — не отмахиваться, по каждой дать честный ответ (принимаем и меняем план / отвергаем с обоснованием).
3. **Отдельно выписать:** предложенные механизмы manual save из P2 Q4 — ранжированные по трению и надёжности, с моей рекомендацией.
4. **Чекин с пользователем:** план остаётся или корректируем? Направление markdown+compile подтвердилось или нашли лучше?
5. **Только после чекина** — переход к обновлённой Phase A (инвентарь инструментов Claude Code 2026 + что понадобится вне Claude Code для v2 ADHD-задела).

---

## 7 жёстких требований (обновлённый список)

1. **Auto-save через хуки** + **manual «save this now» trigger** (гибрид — оба канала).
2. **Self-learning** — главная ценность, не повторять ошибки.
3. **Token economy** — lazy retrieval, SessionStart тянет только index.
4. **Cost ≈ $0/mo в идеале.** Наличие подписок у текущего пользователя — не оправдание для привязки. Платное — только если (a) явно лучше или (b) всё равно понадобится в v2.
5. **Transparency** — пользователь видит память глазами в файлах, редактирует руками.
6. **Moat-awareness** — Anthropic выкатит своё; мы либо специализированнее, либо в нише (v2 ADHD — как раз про это).
7. **Portable** — markdown / открытые форматы, минимум vendor lock-in.

---

## Что НЕ делать в новой сессии

- Не бросайся в Phase A без research round.
- Не пиши код до Phase C.
- Не сравнивай только Mem0 vs Karpathy — ищи третий путь (LightRAG? Obsidian-centric? гибрид?).
- Не соглашайся на автомате.
- Не забудь: v1 для пользователя + Claude, v2 (ADHD) — только задел.
- Не пивотить Phase 1 Mem0 — довести T2–T5 как baseline.
- Не добавляй резюмирующий параграф в конце ответов.

---

## Первый ход новой сессии (по шагам)

1. **Подтвердить контекст** в 3 предложениях: что за проект MetaMode, где мы остановились (research round), что делаем в этой сессии.
2. **Спросить пользователя, готов ли он запустить research round** прямо сейчас или хочет сначала что-то уточнить по плану.
3. **Выдать три готовых промпта** P1/P2/P3 для копи-пасты (кусками, с инструкцией куда вставлять).
4. **Пока результаты идут** — ты доступен для любых уточнений, но новую архитектурную работу не начинаешь. Можно параллельно обсуждать Mem0 Phase 1 T2 если пользователь хочет этот трек двигать.
5. **Когда все три результата вернутся** — синтез, таблица, чекин, потом Phase A.

---

## Ключевые цитаты пользователя из прошлой сессии (чтобы не забыть тон)

> «Лучше решить хоть какой-то вопрос, чем углубиться в космический корабль и не сделать вообще ничего.»

> «Сейчас самое важное для меня — прокачать тебя, чтобы я стал больше зарабатывать с помощью тебя. Приложения, сайты, автоматизации и т.д.»

> «Раз все выбирают обсидиан или LightRag, то это не спроста. Видимо в этом есть смысл.»

> «Если есть решение, за которое придется платить и оно будет ЯВНО лучше, то мы с тобой обсудим варианты.»

> «Нужно очень обстоятельно и творчески подойти к этому процессу. Наша связка тут с тобой будет началом.»
