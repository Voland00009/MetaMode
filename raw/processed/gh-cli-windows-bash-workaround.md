# gh CLI не работает через cmd.exe в Claude Code на Windows

## Context
При попытке оставить комментарии к GitHub issues из Claude Code на Windows, `gh issue comment` не выполнялся. Проблема: `gh` не находился в PATH из bash-окружения Claude Code, а вызов через `cmd.exe /c "gh ..."` давал только banner Windows без выполнения команды.

## Key Insight
На Windows в Claude Code три слоя проблем с `gh`:

1. **`gh` не в PATH bash-окружения** — Claude Code использует bash (MSYS2/Git Bash), а `gh.exe` установлен в `C:\Program Files\GitHub CLI\` которого нет в bash PATH
2. **`cmd.exe /c` глотает вывод** — команды через `cmd.exe` не пробрасывают stdout/stderr обратно в bash корректно, видно только banner Windows
3. **Backticks и спецсимволы** — попытка передать `--body` с текстом содержащим backticks, скобки, кавычки ломает парсинг между bash и cmd.exe

**Решение:** использовать полный путь к `gh.exe` напрямую из bash + передавать body через `--body-file`:

```bash
# Найти gh
"/c/Program Files/GitHub CLI/gh.exe" auth status

# Записать комментарий в файл, затем передать через --body-file
"/c/Program Files/GitHub CLI/gh.exe" issue comment 1 \
  --repo Owner/Repo \
  --body-file /path/to/comment.txt
```

## Example
```bash
# НЕ работает:
cmd.exe /c "gh issue comment 1 --repo Owner/Repo --body 'text with `backticks`'"

# Работает:
echo "Comment text" > /tmp/comment.txt
"/c/Program Files/GitHub CLI/gh.exe" issue comment 1 --repo Owner/Repo --body-file /tmp/comment.txt
```

Ключевое: `--body-file` обходит все проблемы с экранированием между shell-ами. Всегда предпочитай `--body-file` над `--body` на Windows.
