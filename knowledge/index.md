# Knowledge Base Index

| Article | Summary | Compiled From | Updated |
|---------|---------|---------------|---------|
| [[concepts/python-import-time-binding]] | `from X import Y` copies references at import time; patch at consumer, not source | daily/2026-04-11.md | 2026-04-11 |
| [[concepts/mock-patching-at-consumer-level]] | Always patch where a name is read, not where it is defined | daily/2026-04-11.md | 2026-04-11 |
| [[concepts/python-duck-typing-silent-failures]] | Iterating strings as lists produces garbled output without errors | daily/2026-04-11.md | 2026-04-11 |
| [[concepts/claude-cli-json-output-variance]] | `claude -p --output-format json` result field can be string or array | daily/2026-04-11.md | 2026-04-11 |
| [[concepts/tdd-red-phase-value]] | RED phase catches tests failing for wrong reasons before code is written | daily/2026-04-11.md | 2026-04-11 |
| [[connections/duck-typing-and-import-binding]] | Both are Python permissiveness bugs: wrong data flows silently | daily/2026-04-11.md | 2026-04-11 |
| [[concepts/cc-hooks-lifecycle]] | Hooks attach shell commands to Claude Code lifecycle events for automated formatting, testing, linting | raw/Никита Ефимов.md | 2026-04-12 |
| [[concepts/cc-skills-contextual-loading]] | Skills are demand-loaded instruction files that save context window vs monolithic CLAUDE.md | raw/Никита Ефимов.md | 2026-04-12 |
| [[concepts/cc-mcp-server-integration]] | MCP servers bridge Claude Code to external services (GitHub, databases, Slack) | raw/Никита Ефимов.md | 2026-04-12 |
| [[concepts/cc-settings-local-vs-shared]] | `settings.json` for shared config, `settings.local.json` for secrets — never commit tokens | raw/Никита Ефимов.md | 2026-04-12 |
| [[connections/hooks-skills-mcp-layered-automation]] | Three layers: hooks = actions, skills = knowledge, MCP = data — distinct concerns | raw/Никита Ефимов.md | 2026-04-12 |
| [[concepts/human-in-the-loop-quality-gate]] | Pending review prevents AI auto-capture from accumulating junk (95% junk in mem0 experiment) | raw/metamode-vs-coleam00-audit.md | 2026-04-12 |
| [[concepts/fork-dont-rewrite]] | Fork proven code and make surgical additions; MetaMode is ~85% coleam00 with 5 modifications | raw/metamode-vs-coleam00-audit.md | 2026-04-12 |
| [[concepts/per-project-vs-global-tool-config]] | Per-project wins on install UX, global wins on knowledge continuity across projects | raw/metamode-vs-coleam00-audit.md | 2026-04-12 |
| [[concepts/multi-source-knowledge-ingestion]] | RAW inbox pattern: drop markdown + run processor for external knowledge alongside conversation capture | raw/metamode-vs-coleam00-audit.md | 2026-04-12 |
| [[connections/quality-vs-automation-tradeoff]] | Full automation degrades quality; automation + lightweight human gate is the optimal pattern | raw/metamode-vs-coleam00-audit.md | 2026-04-12 |
