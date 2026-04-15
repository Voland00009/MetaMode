# Установка Obsidian Web Clipper

🌐 [English](web-clipper-setup.md) | **Русский**

Сохраняйте веб-страницы прямо в память Claude. Web Clipper превращает любую статью, страницу документации или исследование в markdown-файл в RAW inbox MetaMode — одним запуском `ingest_raw.py` позже Claude знает, что вы читали.

## Почему это важно

Claude Code забывает всё между сессиями. MetaMode решает это для *разговоров*, но что со знаниями, которые вы находите *вне* Claude — посты в блогах, документация фреймворков, ответы Stack Overflow? Web Clipper закрывает этот разрыв:

```text
Веб-страница → Clip → raw/article.md → ingest_raw.py → knowledge/concepts/*.md → session_start → Claude знает
```

Без Web Clipper пришлось бы копировать-вставлять контент в контекст Claude каждый раз. С ним — клипаете один раз, Claude помнит навсегда.

## Use cases

**Изучение нового фреймворка** — клипайте ключевые страницы документации (getting started, API reference, типовые паттерны). После ингестии Claude может ссылаться на них при написании кода — больше никаких «вставь документацию» в каждой сессии.

**Сохранение решения для дебага** — нашли GitHub issue или блог-пост, который решил ваш баг? Клипните. В следующий раз с той же проблемой Claude уже знает фикс.

**Синтез исследований** — клипните 5-10 статей по теме, запустите ingest, затем попросите Claude синтезировать паттерны. Compiler wiki группирует связанные концепты автоматически.

**Сохранение эфемерного контента** — сообщения в Discord, треды в Slack, посты на форумах, которые могут удалить. Клипни сейчас, обработай позже.

## Предварительные требования

- Установлен Obsidian с `MetaMode/` открытым как vault (см. [Obsidian setup](obsidian-setup.ru.md))
- Браузер Chrome или Firefox

## Шаг 1: Установите Obsidian Web Clipper

1. Перейдите на https://obsidian.md/clipper
2. Нажмите "Get the extension" для вашего браузера (Chrome / Firefox)
3. Установите и закрепите расширение на панели инструментов

## Шаг 2: Настройте расширение

1. Нажмите на иконку Web Clipper в панели браузера
2. Нажмите на иконку шестерёнки (Settings)
3. Под **General**:
   - Vault: выберите vault, указывающий на корневую директорию `MetaMode/` (тот же vault что в [Obsidian setup](obsidian-setup.ru.md))
4. Под **Templates**:
   - Создайте новый template с именем "MetaMode RAW"
   - **Note name**: `{{title|slugify}}`
   - **Save to folder**: `raw` (относительно корня vault = MetaMode/)
   - **Template content**:

```markdown
# {{title}}

## Context
Clipped from: {{url}}
Date: {{date}}

## Key Insight
{{selection|default:content}}

## Source
[{{title}}]({{url}})
```

5. Нажмите Save

## Шаг 3: Установите плагин "Local Images Plus" (опционально)

Этот плагин скачивает изображения с клипнутых страниц в локальное хранилище.

1. Obsidian → Settings → Community Plugins → Browse
2. Найдите "Local Images Plus"
3. Install → Enable
4. В настройках плагина:
   - Media folder: `knowledge/attachments/`

## Шаг 4: Использование

1. Откройте страницу с полезным контентом
2. Выделите текст, который хотите сохранить (опционально — если ничего не выделено, клипается вся страница)
3. Нажмите на иконку Web Clipper
4. Выберите template "MetaMode RAW"
5. Нажмите "Add to Obsidian"
6. Файл появится в папке `raw/`

## Шаг 5: Обработайте клипнутый контент

После клипа запустите в Claude Code или терминале:

```bash
uv run python scripts/ingest_raw.py
```

Это:
- Прочитает файлы из `raw/` (кроме README.md и `raw/processed/`)
- Создаст wiki-статьи в `knowledge/concepts/` и `knowledge/connections/`
- Обновит `knowledge/index.md`
- Переместит обработанные файлы в `raw/processed/`

## Решение проблем

**Клип попадает не в ту папку**: Проверьте, что "Save to folder" в шаблоне равен `raw` (относительно корня MetaMode vault).

**Картинки не скачиваются**: Убедитесь, что "Local Images Plus" включен и настроен на правильную media folder.

**ingest_raw.py падает**: Проверьте, что в `raw/` лежат валидные markdown-файлы. Бинарные файлы или не-markdown контент вызовут ошибки.

## См. также

- [Экосистема](ecosystem.ru.md) — как Web Clipper встраивается в полный pipeline MetaMode
- [Obsidian setup](obsidian-setup.ru.md) — просмотр wiki через graph view и поиск
- [RAW Inbox](raw-inbox.ru.md) — другие способы добавлять внешние документы
