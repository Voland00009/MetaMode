# Next Session: Fix NotebookLM Login Script in Skill

## Problem

Skill `~/.claude/SKILLS/notebooklm/` содержит login-скрипт, который ломается на Windows из-за двух багов:

### Баг 1: Path("/tmp") mismatch
Python `Path("/tmp")` → `C:\tmp`, bash `/tmp` → Git Bash temp. Signal-файл создаётся в одном месте, ищется в другом. Скрипт бесконечно ждёт сигнал, который уже существует.

### Баг 2: stdout buffering
Скрипт запускается в фоне с `> output.txt`. Python буферизирует stdout → лог пустой → непонятно что происходит, невозможно дебажить.

### Баг 3 (bonus): browser_profile corruption
Если Playwright Chromium крашится или не закрывается корректно, browser_profile остаётся залоченным. Следующий `launch_persistent_context` падает с `TargetClosedError`. Нужна очистка lock-файлов перед запуском.

## What Worked (final solution)

1. Signal-файл через `Path.home() / ".notebooklm" / "save_signal"` — одинаковый путь для bash и Python
2. `flush=True` на каждом `print()`
3. Удаление browser_profile + kill Playwright chrome перед чистым стартом
4. Login-скрипт написан в `~/.notebooklm/nlm_login.py`, запуск через полный путь к python.exe из venv

## Task

1. Прочитать текущий skill: `~/.claude/SKILLS/notebooklm/` — найти секцию login/authenticate
2. Исправить login-скрипт в skill:
   - Заменить все `Path("/tmp/...")` на `Path.home() / ".notebooklm" / ...`
   - Добавить `flush=True` ко всем print()
   - Добавить cleanup lock-файлов перед launch_persistent_context
   - Добавить kill stale Playwright chrome перед запуском
3. Проверить refresh_auth.py (`~/.notebooklm/refresh_auth.py`) — те же проблемы?
4. Подумать: нужен ли fallback если browser_profile не удаляется (locked files)?

## Files

- Skill: `~/.claude/SKILLS/notebooklm/` (точный путь к файлу skill нужно найти)
- Refresh script: `~/.notebooklm/refresh_auth.py`
- RAW с описанием бага: `raw/python-path-tmp-windows-mismatch.md`

## Prompt

```
Исправь login-скрипт в NotebookLM skill.

План: C:/Users/Voland/Dev/MetaMode/plans/next-session-notebooklm-login-fix.md
Контекст: при ре-логине на Windows скрипт молча зависал из-за Path("/tmp") mismatch между bash и Python + stdout buffering. Детали бага и решение в плане.
```
