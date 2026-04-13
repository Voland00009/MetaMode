# Next Session: Ecosystem Docs + Obsidian Web Clipper + Sync

## Context

Аудит 2026-04-13 показал: код MetaMode работает, GitHub issues закрыты, интеграции настроены.
Но документация не покрывает два важных сценария, и ветки не синхронизированы.

## Незакрытые задачи

### 1. Obsidian + Web Clipper как "вторая память для Claude"

**Проблема:** Пользователь не понимает полную цепочку. Нужно описать:

- Установить Obsidian: https://obsidian.md/
- Установить Web Clipper: https://obsidian.md/clipper
- Открыть MetaMode как vault в Obsidian
- Настроить Web Clipper так, чтобы сохранённые страницы попадали в `raw/` директорию MetaMode vault

**Цепочка:**
```
Веб-страница → Web Clipper → raw/article-name.md → ingest_raw.py → knowledge/concepts/*.md → session_start hook → Claude видит
```

**Сценарии для документации:**
- Нашёл полезную статью → Clip → ingest → Claude знает
- Сохранил документацию фреймворка → Clip → ingest → Claude использует при кодинге
- Собрал ресерч по теме → несколько clips → ingest → Claude синтезирует

**Где описать:**
- `docs/web-clipper-setup.md` — УЖЕ СУЩЕСТВУЕТ, содержит техническую инструкцию (установка, шаблон, troubleshooting). Но НЕТ:
  - Объяснения "зачем" — как это делает Obsidian второй памятью для Claude
  - Сценариев использования с примерами
  - Связи с остальным ecosystem (RAW inbox → wiki → Claude)
- `docs/obsidian-setup.md` — уже ссылается на Web Clipper? Проверить, добавить cross-reference
- В ecosystem doc — описать Web Clipper как один из способов загрузки знаний

### 2. Ecosystem doc — как всё связано

**Проблема:** Информация об интеграциях размазана по 3 файлам. Нужен один `docs/ecosystem.md`:

```
MetaMode Ecosystem
├── Автозахват (hooks) → daily logs → wiki articles
├── Obsidian — визуализация + ручные правки + Web Clipper
├── NotebookLM — подкасты, квизы, архив сессий, экономия токенов  
├── RAW Inbox — внешние документы → wiki
└── Всё вместе: знания из ВСЕХ проектов + внешних источников → один мозг
```

Описать:
- Что делает каждый компонент
- Как они связаны
- Почему это лучше, чем каждый по отдельности
- Что человек получает "из коробки" при клонировании репо

### 3. Синхронизация веток

После всех изменений:
```bash
git add -A && git commit
git checkout main (если не удаётся — создать локально из origin/main)
git merge master
git push origin main
git checkout master
```

### 4. NotebookLM login bug (ОТДЕЛЬНО)

Пользователь решает сам по плану: `plans/next-session-notebooklm-login-fix.md`
НЕ трогать в этой сессии.

## Files to check/edit

- `docs/web-clipper-setup.md` — уже существует, проверить содержимое
- `docs/obsidian-setup.md` — добавить Web Clipper секцию
- `docs/ecosystem.md` — СОЗДАТЬ новый
- `README.md` — добавить ссылку на ecosystem doc
- Ветки master/main — синхронизировать

## Prompt

```
Продолжай по плану: C:/Users/Voland/Dev/MetaMode/plans/next-session-docs-ecosystem.md

Контекст: аудит 13 апреля показал, что код работает, но не хватает:
1. Описания Obsidian Web Clipper как способа загрузки веб-страниц в память Claude
2. Единого ecosystem doc, связывающего все интеграции
3. Синхронизации master → main

NotebookLM login bug решается отдельно, не трогай.
```
