🌐 [English](cross-project-template.md) | **Русский**

# Доступ к Wiki из других проектов — шаблон для CLAUDE.md

Скопируйте блок ниже в `CLAUDE.md` любого проекта, где вы хотите, чтобы Claude Code
имел доступ к вашей персональной wiki базе знаний.

---

## Блок для копирования (между маркерами)

```markdown
<!-- START: MetaMode Wiki Access -->
## Personal Wiki (MetaMode)

I have a personal knowledge base with concepts, connections, and lessons learned.

**Wiki location:** `<METAMODE_PATH>/knowledge/`
**Wiki index:** `<METAMODE_PATH>/knowledge/index.md`
**RAW inbox:** `<METAMODE_PATH>/raw/` (for saving new knowledge)

### How to use the wiki

- **Before answering conceptual questions** — check the wiki index with `Read` on `<METAMODE_PATH>/knowledge/index.md`. If a relevant article exists, read it and use that context in your answer.
- **When you learn something new and reusable** — suggest saving it: "This looks like a useful insight. Want me to save it to your wiki RAW inbox?" If I agree, write a markdown file to `<METAMODE_PATH>/raw/` with the content. It will be processed into the wiki later.
- **Don't read the wiki on every message** — only when the topic might have a relevant article (debugging patterns, language gotchas, tool quirks, architectural decisions).

### RAW file format

When saving to RAW inbox, use this format:

```
# Title of the insight

## Context
Where/when this came up

## Key Insight
The actual lesson or pattern

## Example (optional)
Code or scenario illustrating the point
```

File name: `raw/<topic-slug>.md` (e.g., `raw/react-useeffect-cleanup.md`)
<!-- END: MetaMode Wiki Access -->
```

---

## Примечания

- Замените `<METAMODE_PATH>` на ваш реальный путь к клону MetaMode (например, `~/Dev/MetaMode` или `C:/Users/you/Dev/MetaMode`)
- Пути используют прямые слеши — Claude Code на Windows работает и с `/`, и с `\`
- Блок самодостаточен: скопируйте в любой CLAUDE.md, другая настройка не нужна
- Wiki доступна только для чтения из других проектов; новые знания проходят через RAW inbox
- Индекс wiki маленький (<50 строк сейчас), поэтому его чтение дёшево
