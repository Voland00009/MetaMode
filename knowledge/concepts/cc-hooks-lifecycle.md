---
title: "Claude Code Hooks: Lifecycle Automation"
aliases: [cc hooks, claude code hooks, lifecycle hooks]
tags: [claude-code, devtools, workflow]
category: "claude-code"
sources:
  - "raw/Никита Ефимов.md"
created: 2026-04-12
updated: 2026-04-12
---

# Claude Code Hooks: Lifecycle Automation

**Context:** When setting up Claude Code for a project and wanting to automate repetitive tasks like formatting, linting, and testing on every file change.

**Problem:** Without hooks, the developer must manually ask Claude Code to run formatters, linters, and tests after each change — or remember to do it themselves. This is error-prone and breaks flow.

**Lesson:** Hooks let you attach shell commands to specific lifecycle events in Claude Code. Define the rule once, and it executes automatically on every relevant action — removing human memory from the loop.

## Key Points

- Hooks are shell commands that fire at specific points in the Claude Code lifecycle
- Four hook types: **PreToolUse** (before a tool runs), **PostToolUse** (after a tool runs), **Notification** (on notifications), **Stop** (when the agent finishes)
- The `matcher` field filters which tool triggers the hook (e.g., `"Write|Edit"` for file changes only)
- Environment variable `$CLAUDE_FILE_PATH` provides the path to the affected file
- Hooks are configured in `.claude/settings.json` and committed to the repo, so they apply to the whole team

## Details

Hooks are the automation layer of Claude Code. They execute shell commands in response to lifecycle events, without requiring the developer to issue explicit instructions. The most common pattern is PostToolUse hooks that run formatters or tests after file modifications.

A PostToolUse hook with `matcher: "Write|Edit"` fires only when Claude Code writes or edits a file. The matcher supports regex-style alternation (`|`), so you can combine multiple tool names. The hook command has access to environment variables like `$CLAUDE_FILE_PATH`, which contains the path of the file that was just modified — enabling targeted operations like running only the related tests instead of the full suite.

PreToolUse hooks are useful for validation before an action happens — for example, checking that a file isn't in a protected directory before allowing a write. Stop hooks run when the agent finishes its task, making them ideal for a final test run to verify the overall result.

Because hooks live in `.claude/settings.json`, they're version-controlled and shared across the team. This means formatting standards, test requirements, and other quality gates are enforced consistently for everyone using Claude Code on the project.

## Related Concepts

- [[concepts/cc-skills-contextual-loading]] - Skills provide knowledge/instructions; hooks provide automated actions — complementary layers
- [[concepts/cc-settings-local-vs-shared]] - Hooks go in shared settings.json; secrets go in local settings
- [[concepts/cc-mcp-server-integration]] - MCP connects external services; hooks automate local toolchain
