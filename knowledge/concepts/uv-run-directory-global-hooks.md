---
title: "uv run --directory for Global Hook Execution"
aliases: [uv run directory, global hooks pattern, cross-project script execution]
tags: [devtools, python, shell, workflow]
category: "devtools"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
updated: 2026-04-12
---

# uv run --directory for Global Hook Execution

**Context:** When setting up Claude Code hooks that should work from any project directory but need to execute scripts from a specific project (e.g., MetaMode's memory pipeline scripts).

**Problem:** Global hooks in `~/.claude/settings.json` execute with the current working directory set to whatever project the user is working in. Scripts that depend on a specific project's virtual environment, dependencies, or relative paths break when invoked from a different directory.

**Lesson:** `uv run --directory <path>` sets both the working directory and the virtual environment to the specified project, enabling scripts to run correctly regardless of where the hook is triggered.

## Key Points

- Global hooks in `~/.claude/settings.json` fire in every project, but the cwd is the current project — not the hook script's project
- `uv run --directory C:/Users/Voland/Dev/MetaMode python scripts/flush.py` runs with MetaMode's venv and cwd from any directory
- This is the key mechanism that enables a single, unified knowledge base across all projects
- Without `--directory`, the script would use the current project's venv (which likely lacks required dependencies) or fail to find relative paths
- The pattern applies to any tool ecosystem where scripts need a fixed execution context (npm, pipenv, poetry all have analogous flags)

## Details

MetaMode's architecture uses global hooks — hooks defined in `~/.claude/settings.json` rather than in a project's `.claude/settings.json`. This means the SessionStart, SessionEnd, PreCompact, and user_prompt_submit hooks fire in every Claude Code session, regardless of which project the user is working in. The hooks need to execute MetaMode's Python scripts (flush.py, compile.py, session_start.py), which depend on MetaMode's virtual environment and expect to find configuration files relative to the MetaMode project root.

The `uv run --directory <path>` flag solves both problems simultaneously. It sets the working directory to the specified path (so relative paths like `scripts/state.json`, `daily/`, `knowledge/` resolve correctly) and activates the virtual environment from that directory (so `import` statements find the right packages). The hook command becomes: `uv run --directory C:/Users/Voland/Dev/MetaMode python scripts/session_start.py`.

This pattern was critical for MetaMode's transition from per-project to global configuration. In the per-project model (coleam00's default), hooks live in the project's own `.claude/settings.json` and the cwd is always correct. Moving to global hooks broke all relative paths and venv resolution until `--directory` was applied. The one-time cost of adding `--directory` to each hook command eliminated the need for per-project hook duplication.

## Related Concepts

- [[concepts/per-project-vs-global-tool-config]] - `--directory` is the mechanism that makes global configuration practical
- [[concepts/cc-hooks-lifecycle]] - Hooks are the consumer of this pattern — they trigger the script execution
- [[concepts/cc-settings-local-vs-shared]] - Global hooks live in `~/.claude/settings.json`, the user-wide config layer

