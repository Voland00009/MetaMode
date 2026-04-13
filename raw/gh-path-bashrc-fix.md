# Windows bash PATH: программы из Program Files не видны в Claude Code

## Context
Claude Code на Windows использует bash (Git Bash/MSYS2). Программы установленные в `C:\Program Files\` (gh, node и др.) не попадают в bash PATH. Каждая сессия начинается с `gh: command not found`. Полный путь (`"/c/Program Files/GitHub CLI/gh.exe"`) работает, но неудобен и забывается между сессиями.

## Key Insight
Создание `~/.bashrc` с добавлением нужных путей в PATH решает проблему навсегда. Claude Code sourсит `.bashrc` при старте bash-сессии.

```bash
# ~/.bashrc
export PATH="/c/Program Files/GitHub CLI:$PATH"
```

Ключевое: не нужен полный путь к `.exe`, достаточно добавить директорию. Формат пути — Unix-стиль (`/c/Program Files/...`), не Windows (`C:\Program Files\...`).

## Example
До: каждая сессия — `gh: command not found`, workaround через `"/c/Program Files/GitHub CLI/gh.exe"`.
После: `gh --version` работает сразу в любой сессии Claude Code.

Если появятся другие программы с той же проблемой — добавить их путь в тот же `.bashrc`.
