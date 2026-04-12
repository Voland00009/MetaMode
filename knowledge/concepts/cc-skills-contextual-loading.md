---
title: "Claude Code Skills: Context-Loaded Instructions"
aliases: [cc skills, claude code skills, demand-loaded instructions]
tags: [claude-code, workflow, productivity]
category: "claude-code"
sources:
  - "raw/Никита Ефимов.md"
created: 2026-04-12
updated: 2026-04-12
---

# Claude Code Skills: Context-Loaded Instructions

**Context:** When a project has many specialized instructions (code review checklists, testing standards, deployment procedures) that don't all need to be active at once.

**Problem:** Putting everything into CLAUDE.md wastes context window on instructions irrelevant to the current task. As the file grows, the signal-to-noise ratio drops and Claude Code becomes less effective.

**Lesson:** Skills are separate markdown files that load on demand based on task relevance. They give Claude Code specialized expertise without permanently consuming context window.

## Key Points

- Skills are stored as `.md` files in `.claude/skills/` (project-specific) or `~/.claude/skills/` (global)
- Unlike CLAUDE.md which loads entirely on every interaction, skills load only when Claude Code determines they're relevant
- Each skill file contains: when to apply, rules/checklists, and expected output format
- A project with 10-15 skills saves significant context compared to a monolithic CLAUDE.md
- Skills are essentially "expert roles" that Claude Code can adopt for specific task types

## Details

CLAUDE.md is the foundational instruction file for Claude Code — it loads in full on every interaction. This works well for universal project rules (language, conventions, architecture decisions) but becomes a problem when you need specialized instructions for different task types. A code review checklist, testing standards, deployment procedures, and API design guidelines might total thousands of tokens that are irrelevant 90% of the time.

Skills solve this by splitting instructions into focused, single-purpose files. Each skill describes its own activation criteria ("when reviewing code", "when writing tests"), its rules, and its expected output format. Claude Code reads the skill metadata and loads the full content only when the current task matches.

The two storage locations serve different purposes. Project skills in `.claude/skills/` are version-controlled and shared with the team — they encode team-specific standards. Global skills in `~/.claude/skills/` are personal — they carry a developer's preferred workflows across all projects.

A well-structured skill has three sections: activation criteria (when to apply), rules or checklists (what to do), and output format (how to present results). This structure ensures Claude Code knows both when and how to use the skill, minimizing irrelevant activation and maximizing the quality of skill-guided output.

## Related Concepts

- [[concepts/cc-hooks-lifecycle]] - Hooks automate actions; skills provide knowledge and instructions — different automation layers
- [[concepts/cc-mcp-server-integration]] - MCP connects to external data; skills define how to process and respond to it
- [[concepts/cc-settings-local-vs-shared]] - Skills files are separate from settings.json but follow the same project/global split
