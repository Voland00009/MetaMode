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
| [[concepts/windows-cli-arg-length-limit]] | Windows ~8K char CLI arg limit breaks `claude -p`; fix: pass prompt via stdin | daily/2026-04-12.md | 2026-04-12 |
| [[concepts/two-pass-llm-quality-audit]] | Extract → audit pattern: Pass 2 marks junk with AUDIT_FLAG but never deletes | daily/2026-04-12.md | 2026-04-12 |
| [[concepts/claudemd-per-turn-token-cost]] | CLAUDE.md loads every turn: lines x turns = real cost; keep under 80-100 lines | daily/2026-04-12.md | 2026-04-12 |
| [[concepts/claudeignore-context-optimization]] | `.claudeignore` is highest-leverage context optimization; documented 88% token reduction | daily/2026-04-12.md | 2026-04-12 |
| [[concepts/stale-memory-worse-than-absence]] | Outdated memory files actively mislead AI; 38% of files were stale in audit | daily/2026-04-12.md | 2026-04-12 |
| [[connections/claudeignore-and-claudemd-sizing]] | Two complementary context optimizations: file scanning + per-turn instruction cost | daily/2026-04-12.md | 2026-04-12 |
| [[concepts/claude-agent-sdk-max-subscription]] | Claude Agent SDK works on Max subscription ($0/mo) without API key; eliminates CLI limitations | daily/2026-04-12.md | 2026-04-12 |
| [[concepts/memory-tiering-access-frequency]] | Hot/warm/archive tiers for AI memory files; MetaMode 21→5 active (−76%) | daily/2026-04-12.md | 2026-04-12 |
| [[concepts/opt-in-lint-reminders]] | Periodic maintenance via reminders, not auto-enforcement; wiki 7d, memory 14d intervals | daily/2026-04-12.md | 2026-04-12 |
| [[concepts/uv-run-directory-global-hooks]] | `uv run --directory` enables global hooks to execute project-specific scripts from any cwd | daily/2026-04-12.md | 2026-04-12 |
| [[concepts/llm-cost-tracking-pattern]] | Accumulate `ResultMessage.total_cost_usd` across SDK calls into shared state.json | daily/2026-04-12.md | 2026-04-12 |
| [[connections/stale-memory-and-periodic-lint]] | Audit detects staleness patterns → lint codifies checks → reminders ensure cadence | daily/2026-04-12.md | 2026-04-12 |
