# Python Path("/tmp") vs bash /tmp на Windows

## Context
При написании login-скрипта для NotebookLM cookie refresh: Python-скрипт запускался из bash (Git Bash в Claude Code на Windows), использовал signal-файл для межпроцессной коммуникации. Bash создавал файл через `touch /tmp/nlm_save_signal`, Python проверял через `Path("/tmp/nlm_save_signal").exists()`. Скрипт бесконечно ждал сигнала, который уже был создан.

## Key Insight
На Windows `Path("/tmp")` в Python резолвится в `C:\tmp` (корень текущего диска), а bash `/tmp` — в Git Bash temp-директорию (обычно `/tmp` внутри MSYS2, что маппится на другой реальный путь). Файлы создаются в разных местах, межпроцессная коммуникация молча ломается без ошибок.

**Решение:** использовать `Path.home()` или абсолютные Windows-пути вместо `/tmp` в любом коде, который должен работать между bash и Python на Windows:

```python
# Плохо — bash и Python видят разные директории
SIGNAL_FILE = Path("/tmp/nlm_save_signal")

# Хорошо — одинаковый путь везде
SIGNAL_FILE = Path.home() / ".notebooklm" / "save_signal"
```

Дополнительно: при перенаправлении stdout в файл (`> output.txt`) Python буферизирует вывод. Добавляй `flush=True` к каждому `print()`, иначе лог будет пустым до завершения процесса.

## Example
```bash
# Bash создает файл здесь:
touch /tmp/signal        # → /c/Users/Voland/AppData/Local/Temp/signal (или MSYS2 /tmp)

# Python ищет файл здесь:
Path("/tmp/signal")      # → C:\tmp\signal

# Результат: Python никогда не найдет файл, бесконечный цикл ожидания
```
