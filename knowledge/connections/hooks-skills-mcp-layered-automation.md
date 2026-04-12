---
title: "Hooks ↔ Skills ↔ MCP: Three Layers of Claude Code Automation"
tags: [claude-code, workflow, architecture]
category: "claude-code"
sources:
  - "raw/Никита Ефимов.md"
created: 2026-04-12
---

# Hooks ↔ Skills ↔ MCP: Three Layers of Claude Code Automation

**Context:** When setting up Claude Code for a project and deciding which features to configure first, or when understanding why a certain type of automation belongs in one layer rather than another.

**Problem:** Hooks, skills, and MCP servers can seem overlapping — all three "make Claude Code smarter." Without understanding their distinct roles, configuration becomes ad-hoc and the boundaries between layers blur.

**Lesson:** Each layer covers a distinct concern: hooks automate the local toolchain (actions), skills provide contextual expertise (knowledge), and MCP connects external services (data). Together they form a complete automation stack with clear separation of responsibilities.

## The Connection

The three features map to a classic action/knowledge/data separation:

- **Hooks = Actions.** They execute shell commands in response to lifecycle events. Hooks don't teach Claude Code anything — they automate what happens around its work (format after edit, test after stop, lint before commit). Hooks are stateless and reactive.

- **Skills = Knowledge.** They provide specialized instructions and checklists that shape how Claude Code approaches a task. Skills don't execute anything — they define standards, patterns, and expectations. Skills are loaded on demand based on task relevance.

- **MCP = Data.** MCP servers connect Claude Code to external information and actions in remote systems. They don't define rules or automate local tools — they bridge the gap between the local development environment and the broader ecosystem (GitHub, databases, messaging).

A minimal production setup demonstrates this separation: hooks run Prettier and tests (actions), 2-3 skills define code review and testing standards (knowledge), and a GitHub MCP server provides issue and PR context (data). Each layer is independently useful, but together they transform Claude Code from a code editor into a full development workflow participant.

## Implications

Understanding the layer separation helps with configuration decisions:

1. "I want tests to run automatically" → **Hook** (PostToolUse or Stop)
2. "I want Claude to follow our code review checklist" → **Skill** (code-review.md)
3. "I want Claude to read our GitHub issues" → **MCP** (GitHub server)
4. "I want Claude to format code on save" → **Hook** (PostToolUse with matcher)
5. "I want Claude to know our API design patterns" → **Skill** (api-design.md)

Misplacing a concern — like putting formatting rules in a skill instead of a hook — leads to inconsistent enforcement and wasted context window.

## Related Concepts

- [[concepts/cc-hooks-lifecycle]]
- [[concepts/cc-skills-contextual-loading]]
- [[concepts/cc-mcp-server-integration]]
- [[concepts/cc-settings-local-vs-shared]]
