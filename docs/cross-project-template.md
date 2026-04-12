# Cross-Project Wiki Access — Template for CLAUDE.md

Copy the block below into the `CLAUDE.md` of any project where you want Claude Code
to have access to your personal wiki knowledge base.

---

## Block to copy (between the markers)

```markdown
<!-- START: MetaMode Wiki Access -->
## Personal Wiki (MetaMode)

I have a personal knowledge base with concepts, connections, and lessons learned.

**Wiki location:** `C:/Users/Voland/Dev/MetaMode/knowledge/`
**Wiki index:** `C:/Users/Voland/Dev/MetaMode/knowledge/index.md`
**RAW inbox:** `C:/Users/Voland/Dev/MetaMode/raw/` (for saving new knowledge)

### How to use the wiki

- **Before answering conceptual questions** — check the wiki index with `Read` on `C:/Users/Voland/Dev/MetaMode/knowledge/index.md`. If a relevant article exists, read it and use that context in your answer.
- **When you learn something new and reusable** — suggest saving it: "This looks like a useful insight. Want me to save it to your wiki RAW inbox?" If I agree, write a markdown file to `C:/Users/Voland/Dev/MetaMode/raw/` with the content. It will be processed into the wiki later.
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

## Notes

- Paths use forward slashes — Claude Code on Windows handles both `/` and `\`
- The block is self-contained: copy-paste into any CLAUDE.md, no other setup needed
- Wiki is read-only from other projects; new knowledge goes through RAW inbox
- The wiki index is small (<50 lines now), so reading it is cheap
