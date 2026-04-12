---
title: "Claude Code Settings: Shared vs Local Configuration"
aliases: [settings.json vs settings.local.json, cc settings security]
tags: [claude-code, devtools, workflow]
category: "claude-code"
sources:
  - "raw/Никита Ефимов.md"
created: 2026-04-12
updated: 2026-04-12
---

# Claude Code Settings: Shared vs Local Configuration

**Context:** When configuring Claude Code for a team project that needs both shared automation rules and per-developer secrets (API tokens, database credentials).

**Problem:** `.claude/settings.json` is committed to the repository, making it ideal for shared team configuration but dangerous for secrets. Putting tokens directly in settings.json exposes them to everyone with repo access.

**Lesson:** Use `settings.json` for shared configuration (hooks, tool settings) and `settings.local.json` (gitignored) for secrets. Reference secrets in shared config via `${ENV_VAR}` syntax.

## Key Points

- `.claude/settings.json` — committed to repo, shared across the team; holds hooks, MCP server definitions, tool preferences
- `.claude/settings.local.json` — gitignored, per-developer; holds API tokens, database URLs, personal overrides
- MCP server configs can reference environment variables with `${GITHUB_TOKEN}` syntax, keeping the structure shared while secrets stay local
- This mirrors the `.env` / `.env.local` pattern common in web development
- Global user settings live in `~/.claude/settings.json` — personal defaults across all projects

## Details

Claude Code's configuration lives in `.claude/settings.json` at the project root. Because this file is committed to version control, it serves as the single source of truth for team-wide automation: hooks that run formatters, MCP server configurations, and other shared preferences. Any developer cloning the repo gets the same Claude Code setup automatically.

However, MCP servers require credentials — GitHub tokens, database connection strings, Slack tokens. These must never be committed. The solution is a two-file pattern: `settings.json` defines the structure and references environment variables (`${GITHUB_TOKEN}`), while `settings.local.json` provides the actual secret values. The `.local` file is added to `.gitignore` so it stays on the developer's machine.

This pattern is conceptually identical to how web frameworks handle `.env` files — a committed `.env.example` with placeholder values, and a gitignored `.env` with real secrets. The key discipline is the same: never put actual credentials in committed files, even if the repository is private.

There's also a global layer: `~/.claude/settings.json` provides user-wide defaults that apply to all projects. This is where personal preferences (like global skills paths or default MCP servers) live. Project-level settings override global ones where they conflict.

## Related Concepts

- [[concepts/cc-mcp-server-integration]] - MCP servers are the primary consumer of the shared/local settings split
- [[concepts/cc-hooks-lifecycle]] - Hooks are configured in the shared settings.json and apply to the whole team
- [[concepts/cc-skills-contextual-loading]] - Skills use a similar project/global split with .claude/skills/ vs ~/.claude/skills/
