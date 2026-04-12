# AI Memory System для Claude Code

Система долговременной памяти для Claude Code на базе Obsidian vault. Агент учится на своих ошибках, накапливает знания между сессиями и не повторяет одни и те же ошибки дважды.

## Идея

Вместо векторной базы данных (RAG, embeddings) используется файловая структура Obsidian с wiki-ссылками. Claude Code читает файлы напрямую, навигирует по ссылкам между заметками и находит нужный контекст без API-вызовов к embedding-сервисам.

Три скилла замыкают цикл:
- **/reflect** — после сессии анализирует что было сделано, записывает уроки
- **/lessons** — перед задачей загружает релевантные уроки в контекст
- **/kb-maintain** — раз в 1-2 недели чистит дубли и устаревшее

## Как это работает

```
Работа над задачей
       ↓
  /reflect (после)
       ↓
  Урок записан в Knowledge Base (Obsidian)
  + lab-note в CLAUDE.md проекта
       ↓
  ... проходит время ...
       ↓
  Новая похожая задача
       ↓
  /lessons [категория] (перед)
       ↓
  Агент загружает уроки в контекст
       ↓
  Не повторяет ошибку
```

## Установка

### 1. Скиллы

Скопируй папки из `skills/` в директорию скиллов Claude Code:

```bash
# Скопировать скиллы
cp -r skills/reflect ~/.claude/skills/reflect
cp -r skills/lessons ~/.claude/skills/lessons
cp -r skills/kb-maintain ~/.claude/skills/kb-maintain
```

### 2. Knowledge Base в Obsidian

Скопируй содержимое `knowledge-base-template/` в свой Obsidian vault:

```bash
cp -r knowledge-base-template/ "/path/to/your/vault/Knowledge Base/"
```

Удали папку `_category-template/` после того как поймёшь структуру — это просто пример.

### 3. Настройка путей

В каждом файле SKILL.md замени `YOUR_VAULT_PATH` на реальный путь к твоему vault:

```
# Было:
YOUR_VAULT_PATH/Knowledge Base/

# Стало (пример):
C:/Users/myname/Documents/Obsidian/My Vault/Knowledge Base/
```

Файлы для замены:
- `skills/reflect/SKILL.md`
- `skills/lessons/SKILL.md`
- `skills/kb-maintain/SKILL.md`

### 4. CLAUDE.md

Открой файл `claude-md-snippet.md` и вставь его содержимое в свой глобальный `~/.claude/CLAUDE.md`. Замени `YOUR_VAULT_PATH` на реальный путь.

## Использование

### После работы
```
/reflect
```
Агент проанализирует сессию, запишет уроки в KB и lab-notes в CLAUDE.md проекта.

### Перед новой задачей
```
/lessons nextjs
/lessons supabase rls
/lessons design
```
Агент загрузит уроки из нужной категории в контекст.

### Обслуживание (раз в 1-2 недели)
```
/kb-maintain
```
Проверит дубли, устаревшие записи, битые ссылки.

## Структура Knowledge Base

```
Knowledge Base/
├── _master-index.md          ← навигация, список категорий
├── nextjs/
│   ├── _index.md             ← список статей в категории
│   ├── isr-dynamic-rendering.md
│   └── server-components-gotchas.md
├── supabase/
│   ├── _index.md
│   └── rls-service-role-key.md
├── design/
│   ├── _index.md
│   └── ...
└── ...
```

Каждая категория = технология или домен. Внутри — конкретные уроки с frontmatter, контекстом и wiki-ссылками.

## Что это даёт

- **Нет потери контекста** между сессиями. Урок записан один раз, доступен всегда.
- **Нет повторения ошибок.** Если агент уже наступил на грабли с RLS, он не наступит снова.
- **Нет зависимости от внешних сервисов.** Всё в файлах. Никаких API-ключей, embedding-сервисов, векторных баз.
- **Работает с любым размером проекта.** Obsidian vault масштабируется без деградации.

## Требования

- Claude Code (CLI или расширение VS Code)
- Obsidian (для просмотра и навигации по vault; Claude Code работает с файлами напрямую)
