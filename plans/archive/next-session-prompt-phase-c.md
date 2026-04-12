# Phase C: Full Karpathy Setup

## Context

MetaMode v1 работает: hooks (SessionStart/End/PreCompact/UserPromptSubmit), flush, compile, lint, query, skills (/reflect, /compile). Wiki в `knowledge/` подключена к Obsidian.

Но по сравнению с полным методом Карпати (видео + gist) у нас не хватает:
- RAW папки для внешних данных
- Кросс-проектного доступа к wiki
- Obsidian Web Clipper
- Инструкции "обработай RAW и создай wiki"

Исходные материалы: `input/New ASK/Transcrypt.txt` (транскрипт видео), `input/New ASK/Info.txt` (ссылки).

## Tasks

### Task 1: RAW folder + processing workflow

Создать папку `raw/` для внешних данных (статьи, PDF, транскрипты, заметки).

Что нужно:
- Создать `raw/` с README.md (что сюда класть, как обрабатывать)
- Добавить в CLAUDE.md инструкцию: "Когда пользователь говорит 'обработай RAW' или 'я добавил статью в RAW' — прочитай файлы из `raw/`, создай wiki-статьи в `knowledge/concepts/` и `knowledge/connections/`, обнови `index.md`"
- Обновить `compile.py` или создать отдельный скрипт `ingest_raw.py`, который берёт файл из `raw/` и через `claude -p` создаёт wiki-статьи (аналог compile, но для внешних данных а не daily logs)
- Обновить SessionStart hook: если в `raw/` есть необработанные файлы — напомнить

### Task 2: Cross-project wiki access

Настроить доступ к MetaMode wiki из других проектов.

Что нужно:
- Создать шаблон для CLAUDE.md других проектов — блок с путём к wiki и инструкцией как её использовать
- Записать шаблон в `docs/cross-project-template.md`
- Протестировать: добавить шаблон в CLAUDE.md какого-нибудь тестового проекта, открыть Claude Code в нём, спросить что-то что есть в wiki

### Task 3: Obsidian Web Clipper setup

Настроить Obsidian Web Clipper для сохранения веб-страниц в RAW.

Что нужно:
- Установить расширение Obsidian Web Clipper в Chrome
- Настроить шаблон: путь сохранения → `raw/` в MetaMode vault
- Установить плагин "Local Images Plus" в Obsidian (скачивает картинки локально вместо ссылок)
- Написать короткую инструкцию в `docs/web-clipper-setup.md`

### Task 4: Approve pending review + verify full cycle

- Одобрить pending review от прошлых сессий (если есть)
- Убедиться что весь цикл работает: session start → работа → session end → flush → compile → wiki в Obsidian

### Task 5: Cleanup

- Закоммитить всё что нужно
- Обновить .gitignore (raw/ содержимое? или коммитить?)
- Убрать устаревшие plans/ файлы в archive

## Order

Task 3 (Web Clipper) — ручная настройка, не код. Можно сделать параллельно.
Task 1 (RAW) → Task 2 (Cross-project) → Task 4 (Verify) → Task 5 (Cleanup).

## Constraints

- Всё через `claude -p` (Max подписка, $0)
- Не добавлять vector DB / RAG
- Файлы в markdown, git versioning
- Минимум нового кода — переиспользовать существующий compile.py где можно
