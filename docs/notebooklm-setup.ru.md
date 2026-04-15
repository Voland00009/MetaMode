# Интеграция с NotebookLM

🌐 [English](notebooklm-setup.md) | **Русский**

MetaMode интегрируется с [Google NotebookLM](https://notebooklm.google.com/) для генерации контента и долгосрочной архивации сессий. Это опционально — MetaMode работает полностью без него.

## Что даёт NotebookLM

NotebookLM — AI-инструмент Google для исследований. В связке с MetaMode он даёт:

1. **Генерацию контента** — подкасты, видео, слайд-деки, квизы, отчёты из вашей базы знаний
2. **Внешний мозг для экономии токенов** — выгружать контекст в NotebookLM вместо того, чтобы забивать им контекстное окно Claude

## Установка

### 1. Установите CLI

```bash
python3 -m venv ~/.notebooklm-venv
source ~/.notebooklm-venv/bin/activate  # Windows: .notebooklm-venv\Scripts\activate
pip install "notebooklm-py[browser]"
playwright install chromium
```

### 2. Установите Skills

Скопируйте skills из MetaMode в директорию skills Claude Code:

```bash
# macOS/Linux
cp -r skills/notebooklm ~/.claude/SKILLS/notebooklm

# Windows (PowerShell)
Copy-Item -Recurse skills\notebooklm $env:USERPROFILE\.claude\SKILLS\notebooklm
```

### 3. Аутентификация

В Claude Code скажите `/notebooklm` — skill проведёт через браузерную аутентификацию Google. Войдёте в свой Google-аккаунт, skill сохранит cookies сессии.

## Известное ограничение: cookies истекают

**Это самая частая проблема.** Cookies Google истекают каждые 1-7 дней. Когда увидите "auth error" или "SID cookie missing" — нужно перелогиниться:

1. В Claude Code скажите `/notebooklm`
2. Skill обнаружит просроченные cookies и перезапустит флоу логина

**Почему это нельзя «починить»:** notebooklm-py — неофициальный API, использующий браузерную автоматизацию (Playwright). Google не предоставляет публичный API для NotebookLM, так что browser cookies — единственный метод аутентификации. Политика безопасности Google инвалидирует эти cookies периодически. Это намеренная мера безопасности Google, а не баг.

## Use cases

### 1. Генерация подкастов
Превратите daily logs или wiki-статьи в аудио-обзоры:
```
/notebooklm
"Создай подкаст из сегодняшнего daily log, суммаризируй что я узнал"
```
Полезно для повторения в дороге или на тренировке.

### 2. Учебные материалы
Генерация квизов и карточек из базы знаний:
```
"Сгенерируй квиз по моим wiki-статьям про паттерны тестирования в Python"
```

### 3. Слайд-деки из знаний
Превратите накопленные знания в презентации:
```
"Создай слайд-дек по паттернам дебаггинга из моих последних 5 сессий"
```

### 4. Кросс-сессионные исследования
Задавайте вопросы по всем архивированным сессиям:
```
"Какие подходы я пробовал для снижения latency API?"
```
NotebookLM ищет по всем саммари сессий и синтезирует ответ.

### 5. Экономия токенов
Вместо загрузки полного wiki в контекст Claude (дорого за каждый turn), загрузите его в NotebookLM как source. Затем запрашивайте NotebookLM из Claude по конкретным вопросам — Claude получает только ответ, а не весь корпус.

## Как всё соединяется

```
Сессия Claude Code
    ↓ (авто, через хуки)
Daily logs + wiki-статьи MetaMode
    ↓ (вручную, через /notebooklm)
NotebookLM
    ↓ (по запросу)
Подкасты, квизы, отчёты, поиск
```

- **Hooks** захватывают автоматически — вы ничего не делаете
- **Wiki** компилируется автоматически после 18:00 или вручную через `/compile`
- **NotebookLM** вызывается вручную через `/notebooklm`

## Решение проблем

| Проблема | Решение |
|----------|---------|
| "Auth error" / "SID missing" | Перелогиниться: `/notebooklm` → флоу логина |
| "notebooklm: command not found" | Установить: `pip install "notebooklm-py[browser]"` в `~/.notebooklm-venv` |
| Генерация зависла на "in_progress" | Подождать (audio: 10-20 мин, video: 15-45 мин) или перезапустить |
| "No notebook context" | Запустить `notebooklm use <id>` для выбора notebook |
| Rate limit errors | Подождать 5-10 минут, потом повторить |

## См. также

- [Экосистема](ecosystem.ru.md) — как NotebookLM встраивается в полный pipeline MetaMode
- [Obsidian setup](obsidian-setup.ru.md) — просмотр и визуализация wiki
- [RAW Inbox](raw-inbox.ru.md) — ингестия внешних документов в wiki
