# Руководство по установке

🌐 [English](setup.md) | **Русский**

Пошаговая установка для macOS, Linux и Windows.

---

## Необходимые инструменты

| Инструмент | Проверка | Установка |
|------------|----------|-----------|
| **Python 3.12+** | `python --version` | [python.org](https://www.python.org/downloads/) |
| **uv** | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Claude Code** | `claude --version` | `npm install -g @anthropic-ai/claude-code` |
| **Подписка Claude Max** | — | Необходима для бесплатных вызовов Agent SDK |

---

## Установка

### Шаг 1: Клонируйте репозиторий

```bash
git clone https://github.com/Voland00009/MetaMode.git ~/Dev/MetaMode
cd ~/Dev/MetaMode
```

> **Windows:** используйте `C:/Users/YOU/Dev/MetaMode` вместо `~/Dev/MetaMode`.

### Шаг 2: Установите зависимости

```bash
uv sync
```

Вы должны увидеть `Resolved X packages in ...` — это значит, что всё прошло успешно.

### Шаг 3: Настройте hooks

Hooks являются **глобальными** — они срабатывают в каждой сессии Claude Code, из любого проекта. Именно так MetaMode автоматически захватывает все ваши сессии.

Отредактируйте `~/.claude/settings.json` (создайте файл, если его нет):

**macOS / Linux:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "uv run --directory ~/Dev/MetaMode python hooks/session_start.py"
      }
    ],
    "SessionEnd": [
      {
        "type": "command",
        "command": "uv run --directory ~/Dev/MetaMode python hooks/session_end.py"
      }
    ],
    "PreCompact": [
      {
        "type": "command",
        "command": "uv run --directory ~/Dev/MetaMode python hooks/pre_compact.py"
      }
    ],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "uv run --directory ~/Dev/MetaMode python hooks/user_prompt_submit.py"
      }
    ]
  }
}
```

**Windows (PowerShell или Git Bash):**

Та же структура, но с Windows-путями:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "uv run --directory C:/Users/YOU/Dev/MetaMode python hooks/session_start.py"
      }
    ],
    "SessionEnd": [
      {
        "type": "command",
        "command": "uv run --directory C:/Users/YOU/Dev/MetaMode python hooks/session_end.py"
      }
    ],
    "PreCompact": [
      {
        "type": "command",
        "command": "uv run --directory C:/Users/YOU/Dev/MetaMode python hooks/pre_compact.py"
      }
    ],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "uv run --directory C:/Users/YOU/Dev/MetaMode python hooks/user_prompt_submit.py"
      }
    ]
  }
}
```

> Замените `YOU` на ваше реальное имя пользователя Windows.

**Зачем `uv run --directory`?** Эта опция указывает uv искать виртуальное окружение в директории MetaMode, независимо от того, откуда вы запускаете Claude Code. Без неё hooks будут падать в других проектах.

**Уже есть hooks?** Добавьте записи MetaMode в существующие массивы — несколько hooks на одно событие поддерживаются.

### Шаг 4: Проверьте установку

Выполните эти команды из директории MetaMode:

```bash
# Тест session_start hook — должен вывести JSON с "additionalContext"
uv run python hooks/session_start.py

# Тест !save — должен вывести "Saved to daily/..." в stderr
echo '{"type":"user","content":"!save Test note from setup verification"}' | uv run python hooks/user_prompt_submit.py
```

Затем запустите новую сессию Claude Code в любом месте. Вы должны увидеть внедрённый контекст MetaMode (индекс wiki, последние записи лога). Если wiki пуста, вы увидите пример контента из `knowledge/index.md`.

### Шаг 5: Дайте другим проектам доступ к wiki (опционально)

По умолчанию hooks внедряют контекст wiki в каждую сессию. Но если вы хотите, чтобы Claude мог *читать* ваши wiki-статьи или *сохранять* в RAW inbox из другого проекта, добавьте блок в `CLAUDE.md` этого проекта.

Смотрите [Шаблон для кросс-проектной интеграции](cross-project-template.ru.md) для готового блока.

---

## Установка одной командой (для Claude Code)

Вставьте это в Claude Code, и он выполнит установку за вас:

```
Install MetaMode for me. Clone from https://github.com/Voland00009/MetaMode.git
to ~/Dev/MetaMode, run uv sync, then configure hooks in ~/.claude/settings.json
following docs/setup.md. Verify with a test run of session_start.py.
```

---

## Решение проблем

### "uv: command not found"

Установите uv:
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### "No module named claude_agent_sdk"

Выполните `uv sync` ещё раз из директории MetaMode. Agent SDK указан в `pyproject.toml` и устанавливается автоматически.

### Hooks не срабатывают

1. Убедитесь, что `~/.claude/settings.json` существует и содержит валидный JSON
2. Проверьте, что путь в командах hooks указывает на вашу реальную директорию MetaMode
3. Выполните `claude /hooks` внутри Claude Code, чтобы увидеть зарегистрированные hooks
4. Убедитесь, что команды hooks используют `uv run --directory` (а не просто `uv run`)

### Проблемы с кодировкой на Windows

Если вы видите искажённый вывод или ошибки кодировки, добавьте это в профиль вашего терминала:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

Hooks обрабатывают кодировку внутренне (`sys.stdin.reconfigure(encoding="utf-8")`), но для отображения в терминале это может быть необходимо.

### "Permission denied" на macOS/Linux

Python-скрипты не требуют `chmod +x` — они вызываются через `python`, а не исполняются напрямую. Если вы получаете ошибки доступа, проверьте права на директорию:

```bash
ls -la ~/Dev/MetaMode/hooks/
```

---

## Удаление

1. Удалите записи MetaMode hooks из `~/.claude/settings.json`
2. Удалите директорию MetaMode: `rm -rf ~/Dev/MetaMode`
3. Это всё — MetaMode не вносит системных изменений

Ваши ежедневные логи и wiki-статьи находятся внутри директории MetaMode. Сделайте резервную копию перед удалением, если хотите их сохранить.
