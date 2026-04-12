---
name: compile
description: Manually compile daily logs into wiki knowledge articles
allowed-tools: Bash Read Write Edit Glob Grep
---

# /compile — Manual Knowledge Compilation

Compile unprocessed daily logs into structured knowledge articles.

## Usage

- `/compile` — compile all new/changed daily logs
- `/compile --all` — force recompile everything
- `/compile --dry-run` — show what would be compiled
- `/compile --file daily/2026-04-11.md` — compile specific file

## Process

Run the compile script:

```bash
uv run python scripts/compile.py $ARGS
```

Where `$ARGS` are the arguments passed after `/compile` (if any).

After compilation completes, report:
1. How many logs were compiled
2. How many articles were created/updated
3. Any errors encountered

If there are no logs to compile, inform the user: "All daily logs are up to date."
