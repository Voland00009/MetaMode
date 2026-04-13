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
| [[concepts/asyncio-forgotten-await]] | Missing `await` returns coroutine object silently — wrong type flows through code | raw/example-article.md | 2026-04-13 |
| [[concepts/asyncio-blocking-event-loop]] | Sync blocking calls (`time.sleep`, `requests`) inside async freeze all concurrent tasks | raw/example-article.md | 2026-04-13 |
| [[concepts/asyncio-fire-and-forget-tasks]] | `create_task()` without stored reference lets GC destroy the task silently | raw/example-article.md | 2026-04-13 |
| [[connections/asyncio-pitfalls-and-silent-failures]] | Asyncio pitfalls are async manifestations of Python's silent failure pattern | raw/example-article.md | 2026-04-13 |
| [[concepts/gh-cli-bash-path-windows]] | `gh.exe` not in bash PATH on Windows; fix via `~/.bashrc` PATH export, generalizes to any Program Files tool | raw/gh-cli-windows-bash-workaround.md, raw/gh-path-bashrc-fix.md | 2026-04-13 |
| [[concepts/file-based-input-shell-escaping]] | Use `--body-file` / stdin to bypass cross-shell escaping issues on Windows | raw/gh-cli-windows-bash-workaround.md | 2026-04-13 |
| [[connections/windows-shell-boundary-failures]] | PATH, arg length, escaping, stdout swallowing — a family of silent Windows shell bugs | raw/gh-cli-windows-bash-workaround.md | 2026-04-13 |
| [[concepts/git-unrelated-histories]] | `--allow-unrelated-histories` merges branches with no common ancestor; caused by separate repo initialization | raw/git-unrelated-histories-branch-strategy.md | 2026-04-13 |
| [[concepts/github-repo-init-existing-project]] | Always create empty GitHub repo for existing projects; init with README creates unrelated histories | raw/git-unrelated-histories-branch-strategy.md | 2026-04-13 |
| [[connections/git-unrelated-histories-and-tooling-boundaries]] | Unrelated histories is a boundary mismatch bug in the same family as PATH/escaping/arg-length issues | raw/git-unrelated-histories-branch-strategy.md | 2026-04-13 |
| [[concepts/python-path-tmp-windows-mismatch]] | Python `Path("/tmp")` → `C:\tmp` but bash `/tmp` → MSYS2 temp; cross-process signal files silently break | raw/python-path-tmp-windows-mismatch.md | 2026-04-13 |
| [[concepts/python-stdout-buffering-file-redirect]] | `print()` buffers when stdout redirected to file; add `flush=True` or log appears empty until exit | raw/python-path-tmp-windows-mismatch.md | 2026-04-13 |
