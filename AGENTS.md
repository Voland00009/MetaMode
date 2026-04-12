# MetaMode Knowledge Base Schema

This file defines the structure for all knowledge articles in the wiki.
The compiler (compile.py) reads this schema to produce correctly-formatted articles.

---

## Concept Articles (`knowledge/concepts/`)

Atomic units of knowledge — one concept per file.

### Article Categorization (MetaMode Extension)

Every concept article should be categorized by technology/domain using tags in frontmatter:

**Category tags** (use 1-3 per article):
- `python`, `javascript`, `typescript`, `rust`, `go` — language-specific
- `claude-code`, `claude-api`, `anthropic` — Claude ecosystem
- `git`, `github`, `ci-cd` — version control and deployment
- `testing`, `tdd`, `debugging` — quality practices
- `architecture`, `design-patterns`, `refactoring` — software design
- `devtools`, `shell`, `terminal` — development environment
- `web`, `frontend`, `backend`, `api` — web development
- `database`, `sql`, `orm` — data layer
- `ai`, `llm`, `agents`, `prompting` — AI/ML
- `workflow`, `productivity`, `meta` — process and meta-knowledge

### Enhanced Article Format

```markdown
---
title: "Concept Name"
aliases: [alternate-name]
tags: [category-tag-1, category-tag-2]
category: "technology-or-domain"
sources:
  - "daily/2026-04-01.md"
created: 2026-04-01
updated: 2026-04-03
---

# Concept Name

**Context:** [When/where this knowledge applies]

**Problem:** [What challenge or question this addresses]

**Lesson:** [The key takeaway — the most important sentence in the article]

## Key Points

- Point 1
- Point 2
- Point 3

## Details

Detailed explanation with examples, code snippets, or reasoning.

## Related Concepts

- [[concepts/related-concept]] - How it connects
- [[concepts/another-concept]] - Why it matters
```

---

## Connection Articles (`knowledge/connections/`)

Non-obvious relationships between 2+ concepts.

```markdown
---
title: "Concept A ↔ Concept B"
tags: [category-tag]
category: "technology-or-domain"
sources:
  - "daily/2026-04-01.md"
created: 2026-04-01
---

# Concept A ↔ Concept B

**Context:** [When this connection matters]

**Problem:** [What understanding this connection unlocks]

**Lesson:** [The key insight about the relationship]

## The Connection

Explanation of how these concepts relate in a non-obvious way.

## Implications

What changes when you understand this connection.

## Related Concepts

- [[concepts/concept-a]]
- [[concepts/concept-b]]
```

---

## Q&A Articles (`knowledge/qa/`)

Saved answers to specific questions asked via query.py.

```markdown
---
title: "Question text"
tags: [category-tag]
sources:
  - "query response"
created: 2026-04-01
---

# Question

The original question.

# Answer

The synthesized answer from the knowledge base.

# Sources

- [[concepts/relevant]] - What information was used
```

---

## Index (`knowledge/index.md`)

Master navigation table. Each row:

```
| [[path/slug]] | One-line summary | source-file | date |
```

---

## Log (`knowledge/log.md`)

Timestamped changelog of all compile/flush/lint operations.

```
## [ISO-timestamp] operation | source
- Details of what happened
- Articles created/updated/deleted
```
