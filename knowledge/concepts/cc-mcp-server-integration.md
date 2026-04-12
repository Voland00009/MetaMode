---
title: "MCP Servers: External Service Integration for Claude Code"
aliases: [mcp servers, model context protocol, claude code mcp]
tags: [claude-code, api, devtools]
category: "claude-code"
sources:
  - "raw/Никита Ефимов.md"
created: 2026-04-12
updated: 2026-04-12
---

# MCP Servers: External Service Integration for Claude Code

**Context:** When you want Claude Code to interact with external systems — GitHub issues, databases, Slack channels — rather than just local files and terminal commands.

**Problem:** Without MCP, Claude Code is limited to the local filesystem and shell. It can't read your GitHub issues, query your database, or check Slack messages — forcing the developer to copy-paste context manually.

**Lesson:** MCP (Model Context Protocol) servers act as bridges between Claude Code and external services. Each server exposes a specific service's API as tools that Claude Code can call directly.

## Key Points

- MCP servers are configured in `.claude/settings.json` under the `mcpServers` key
- Each server is an npm package that runs as a subprocess, exposing service-specific tools
- Popular servers: GitHub (`@modelcontextprotocol/server-github`), PostgreSQL (`server-postgres`), Slack (`server-slack`), filesystem (`server-filesystem`)
- Servers require credentials via `env` — API tokens, database URLs, etc.
- Secrets should go in `settings.local.json` (gitignored), not in the shared `settings.json`

## Details

Model Context Protocol (MCP) is a standardized way for AI assistants to communicate with external services. In Claude Code, MCP servers are configured as subprocesses that Claude Code launches and communicates with. Each server translates Claude Code's requests into service-specific API calls and returns structured results.

The GitHub MCP server is the most common example. Once configured with a personal access token, it gives Claude Code the ability to read issues and their comments, create pull requests with descriptions linked to issues, read and respond to code review comments, and search repositories through the GitHub API. This transforms Claude Code from a code editor into a full development workflow participant.

MCP servers are configured as entries in the `mcpServers` object of `settings.json`. Each entry specifies the `command` to run (typically `npx`), `args` (the npm package and flags), and `env` (environment variables including credentials). Multiple servers can be configured simultaneously — for example, GitHub + PostgreSQL + Slack — giving Claude Code a broad view of the project's ecosystem.

The security consideration is important: `settings.json` is typically committed to the repository, but tokens and credentials must not be. The pattern is to use `settings.local.json` (added to `.gitignore`) for secrets, or reference environment variables with `${VAR_NAME}` syntax in the configuration.

## Related Concepts

- [[concepts/cc-hooks-lifecycle]] - Hooks automate local toolchain; MCP connects external services — different scope of automation
- [[concepts/cc-skills-contextual-loading]] - Skills define how Claude Code should work; MCP defines what external data it can access
- [[concepts/cc-settings-local-vs-shared]] - The shared vs local settings split is critical for MCP credential security
