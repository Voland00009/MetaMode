# Step 1: CC Tools Inventory — MetaMode v1

**Дата:** 2026-04-11
**Статус:** COMPLETED

---

## A. Полная таблица механизмов CC

| Механизм | Что делает | Ключевые возможности для MetaMode |
|---|---|---|
| **Hook: SessionStart** | Срабатывает при старте/resume/clear/compact | Инжектит контекст через `additionalContext`. Matcher: `startup\|resume\|clear\|compact` |
| **Hook: SessionEnd** | Срабатывает при завершении сессии | Получает `session_id`, `transcript_path`, `reason`. Спавнит background process |
| **Hook: PreCompact** | Перед сжатием контекста | Matcher: `manual\|auto`. Страховка — те же данные что SessionEnd |
| **Hook: UserPromptSubmit** | Пользователь отправил промпт | Получает `prompt` в stdin. Exit 2 = блокирует отправку. Для `!save` |
| **Hook: Stop** | Claude завершает ответ | Может заблокировать (exit 2). Потенциально для auto-reflect (v1.1) |
| **Hook: PostToolUse** | После успешного tool call | `tool_name`, `tool_input`, `tool_output`. Async возможен. Feedback only |
| **Hook: PreToolUse** | До вызова tool | Может заблокировать, модифицировать input, inject context |
| **Hook: SubagentStop** | Субагент завершился | Может заблокировать остановку |
| **Hook: FileChanged** | Отслеживаемый файл изменился | Matcher = literal filenames (не glob!). Async возможен |
| **Skill** | Slash-команда пользователя | Frontmatter: name, description, allowed-tools, context:fork, model. Shell `!\`cmd\``. Args: `$0`..`$N` |
| **Subagent** | Изолированный агент | `.claude/agents/name.md`. Свои tools, permissions, model, maxTurns. isolation: worktree |
| **`claude -p`** | Headless CLI | Max covered. --max-turns, --permission-mode, --output-format json, --system-prompt-file, --allowedTools |
| **CLAUDE.md hierarchy** | Инструкции по приоритетам | Managed > Local > Project > User. @imports. .claude/rules/ с paths: |
| **settings.json** | Конфиг hooks/permissions/env | 4 уровня. `env:` для переменных. `hooks:` конфиг |
| **Built-in auto memory** | MEMORY.md + topic files | ~/.claude/projects/<repo>/memory/. 200 строк при старте. Claude пишет сам |
| **MCP servers** | Внешние tool providers | Нам НЕ нужен свой MCP |
| **Background tasks** | async hooks + detached subprocess | `"async": true`. Windows: `subprocess.CREATE_NO_WINDOW` |

## B. Маппинг задач на механизмы

| Задача MetaMode | Механизм CC | Обоснование |
|---|---|---|
| Inject index + log при старте | SessionStart hook (command) | additionalContext инжектит в контекст |
| Flush транскрипта | SessionEnd hook → background `claude -p` | Detached process, dedup 60s |
| Страховка compact | PreCompact hook → background `claude -p` | Тот же flush.py |
| `!save` quick capture | UserPromptSubmit hook (command) | Exit 2 = 0 токенов, парсит prompt |
| `/reflect` рефлексия | Skill (.claude/skills/reflect/SKILL.md) | 4 вопроса, allowed-tools |
| Pending review | SessionStart hook + pending-review.md | Inject pending в additionalContext |
| Compile daily→wiki | `claude -p` из flush.py (вечер) + `/compile` skill (ручной) | Dual-mode: auto вечером + manual днём |
| Lint 7 проверок | Python (structural) + `claude -p` (contradictions) | LLM только для check #7 |
| Query к базе | `claude -p` с --system-prompt-file | AGENTS.md контекст |
| Compile reminder | SessionStart hook | Проверка возраста daily/ |
| Категоризация | AGENTS.md правки | Prompt engineering |

## C. 5 нестандартных комбинаций (рассмотрены)

### 1. "Zero-token save" через exit 2 ✅ ПРИНЯТО
UserPromptSubmit → парсит `!save ...` → пишет в daily/ → exit 2 (блокирует). 0 токенов.

### 2. FileChanged watcher для auto-compile ❌ ОТКЛОНЕНО
Причина: matcher требует literal filenames, не glob. Оставляем проверку в flush.py.

### 3. Subagent compile вместо `claude -p` ❌ ОТКЛОНЕНО для background
Причина: subagent работает внутри сессии (тратит parent context). Compile должен быть в фоне.

### 4. Dual-mode compile: skill + headless ✅ ПРИНЯТО
`/compile` skill для ручного + `claude -p` для auto вечером. Один AGENTS.md промпт.

### 5. Stop hook auto-reflect ⏳ ОТЛОЖЕНО в v1.1
Причина: может раздражать. Compile reminder при SessionStart мягче.

## D. Итоговый набор механизмов для v1

| Hook/Mechanism | Назначение |
|---|---|
| SessionStart (command) | inject index + recent log + pending review + compile reminder |
| SessionEnd (command) | transcript → flush.py (background) |
| PreCompact (command) | страховка → flush.py (background) |
| UserPromptSubmit (command) | `!save` interceptor (exit 2, zero-token) |
| Skill: /reflect | structured рефлексия, 4 вопроса |
| Skill: /compile | ручной compile по запросу |
| `claude -p` | headless из flush.py, compile.py, lint.py, query.py |

Отложено в v1.1: Stop hook auto-reflect, FileChanged watcher.
Не нужно: MCP server, Agent SDK, subagent для compile.

## E. Ключевые технические детали из исследования

### Hook stdin (общие поля для всех events):
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse"
}
```

### Hook stdout (универсальные поля):
```json
{
  "continue": true,
  "stopReason": "...",
  "suppressOutput": false,
  "systemMessage": "..."
}
```

### SessionStart stdout для inject:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "...injected text..."
  }
}
```

### UserPromptSubmit — exit 2 блокирует промпт, stderr = feedback пользователю

### settings.json hook structure:
```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "pattern",
        "hooks": [
          {
            "type": "command",
            "command": "python script.py",
            "timeout": 600,
            "async": false
          }
        ]
      }
    ]
  }
}
```

### Skill frontmatter:
```yaml
---
name: skill-name
description: ...
allowed-tools: Bash(git *) Read Write
disable-model-invocation: true
argument-hint: [args]
---
```

### `claude -p` ключевые флаги:
- `--output-format json|text|stream-json`
- `--max-turns N`
- `--permission-mode acceptEdits|bypassPermissions`
- `--system-prompt-file path`
- `--allowedTools "Read" "Write" "Edit" "Glob" "Grep"`
- `--no-session-persistence` (не сохранять сессию)

### Windows subprocess (из coleam00):
```python
subprocess.Popen(
    ['python', 'script.py'],
    creationflags=subprocess.CREATE_NO_WINDOW,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
    encoding="utf-8"
)
```

### Env vars:
- `CLAUDE_INVOKED_BY` — recursion guard
- `CLAUDE_PROJECT_DIR` — project root в hook scripts
