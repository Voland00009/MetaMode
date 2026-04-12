# MetaMode vs coleam00/claude-memory-compiler: Deep Audit

> **Updated 2026-04-12**: SDK migration complete. MetaMode now uses `claude-agent-sdk` (same as coleam00). CLI→SDK difference eliminated.

## Context
Full code-level comparison of MetaMode (fork) with coleam00/claude-memory-compiler (original). Both implement Karpathy's LLM wiki-memory pattern for Claude Code.

## Key Insight
MetaMode is ~85% coleam00 code by volume. After SDK migration, the core LLM backend is identical. The remaining 5 real modifications are surgical additions on top of the original architecture.

## Honest Comparison Table (post-SDK migration)

| Aspect | coleam00 (original) | MetaMode (fork) | Who wins |
|--------|---------------------|-----------------|----------|
| **LLM calls** | Claude Agent SDK (async, streaming) | Claude Agent SDK (async, streaming) | **Tie** — identical backend after migration |
| **Cost** | $0/mo on Max (SDK covered) | $0/mo on Max (SDK covered) | **Tie** — both free on Max |
| **Dependencies** | claude-agent-sdk, python-dotenv, tzdata | claude-agent-sdk, tzdata | **Tie** — nearly identical |
| **Installation** | Clone into project, uv sync, hooks activate | Clone, uv sync, configure global hooks | **coleam00** — zero-config per project. MetaMode requires manual global setup |
| **Scope** | Per-project (hooks in .claude/settings.json) | Global (hooks in ~/.claude/settings.json) | **MetaMode** — one wiki for all projects. coleam00 needs copy per project |
| **Auto-capture** | SessionEnd + PreCompact → flush → daily log | Same, but flush → pending review (not auto-saved) | **Tie** — MetaMode adds review step (quality+), but adds friction (speed-) |
| **Manual capture** | None | `!save <text>` quick-capture hook | **MetaMode** — useful for saving during session without waiting for end |
| **Quality control** | Auto-saves everything LLM extracts | Pending review: human approves before daily log | **MetaMode** — prevents junk accumulation (proven by mem0 cleanup of 95% junk) |
| **External data** | Not supported (conversations only) | `ingest_raw.py` + Web Clipper pipeline | **MetaMode** — supports both internal (sessions) and external (articles, transcripts) |
| **Session start** | Date + KB index + recent log | Same + pending review + compile reminder + RAW reminder | **MetaMode** — more context, but also more tokens at start |
| **Compile** | SDK with streaming, cost tracking, system_prompt preset | SDK with streaming, system_prompt preset, no cost tracking | **Tie** — functionally identical after migration |
| **Query** | SDK with streaming, max_turns=15 | SDK with streaming, max_turns=15 | **Tie** — functionally identical after migration |
| **Lint** | 7 checks, contradiction via SDK | Same 7 checks, contradiction via SDK | **Tie** — functionally identical |
| **AGENTS.md** | 519 lines: full reference with hooks, costs, customization | 153 lines: article formats + categorization tags only | **coleam00** for completeness, **MetaMode** for compile quality (less noise in prompt) |
| **Categorization** | No categorization system | Tag taxonomy (python, claude-code, testing, etc.) in AGENTS.md | **MetaMode** — but premature at <50 articles |
| **Windows support** | CREATE_NO_WINDOW for hooks, backslash JSON fix | Same + sys.stdin/stdout.reconfigure(encoding="utf-8") | **MetaMode** — actually tested on Windows, found and fixed UTF-8 bug |
| **Tests** | No tests | 22 tests (pytest) covering core logic | **MetaMode** — has test coverage |
| **Documentation** | Good README + extremely detailed AGENTS.md | CLAUDE.md project doc, README draft | **coleam00** — well-documented for newcomers |
| **Skill integration** | None | /reflect skill (structured reflection, 4 questions) | **MetaMode** — additional capture mechanism |
| **Cost tracking** | Tracks cost per compile/query in state.json | Not implemented | **coleam00** — useful for visibility even at $0 |

## What coleam00 Does Better

1. **Installation UX**: "Clone and it works" vs MetaMode's manual global hooks setup
2. **Documentation**: AGENTS.md is a complete technical reference (519 lines)
3. **Cost tracking**: Visibility into LLM usage even at $0 (useful for understanding token spend)
4. **Self-contained**: Hooks are per-project in .claude/settings.json, no global config needed

## What MetaMode Does Better

1. **Quality control**: Pending review prevents auto-saving junk (proven — mem0 had 95% junk)
2. **External knowledge**: ingest_raw.py handles articles, transcripts, notes — not just conversations
3. **Global operation**: One wiki serves all projects (no copy per project)
4. **!save quick-capture**: Instant save during session
5. **Windows battle-tested**: UTF-8 encoding fixes for cp1251 console
6. **Test coverage**: 22 tests vs 0
7. **Richer session start**: Pending review + compile reminder + RAW inbox reminder

## What's No Longer Different (after SDK migration)

1. ~~CLI vs SDK~~ — both use Claude Agent SDK now
2. ~~$0 vs API billing~~ — both free on Max
3. ~~Fewer dependencies~~ — both depend on claude-agent-sdk
4. ~~No streaming~~ — both have streaming through SDK

## Honest Assessment (updated)

After SDK migration, MetaMode is **coleam00 + 5 additions**: pending review, !save hook, ingest_raw.py, global hooks, enriched session start. The core is identical.

**Remaining unique value**: quality control (pending review), external data pipeline (ingest_raw.py), quick capture (!save), global operation, Windows fixes, test coverage.

**Honest pitch**: "coleam00 fork with quality control, external data support, and global operation."

## File-Level Diff Summary

### Identical (~95%+ same code):
- hooks/session-end.py (only UTF-8 fix added)
- hooks/pre-compact.py (only UTF-8 fix added)
- scripts/utils.py (identical)
- scripts/config.py (added RAW_DIR, removed TIMEZONE)

### Modified (same structure, minor additions):
- scripts/flush.py (added pending review logic)
- scripts/compile.py (identical to coleam00 after SDK migration)
- scripts/query.py (added stdout UTF-8 fix)
- scripts/lint.py (identical to coleam00 after SDK migration)

### Rewritten:
- hooks/session_start.py (added pending review, compile reminder, RAW reminder)
- AGENTS.md (simplified + added categorization)

### New in MetaMode:
- scripts/ingest_raw.py (external data pipeline)
- hooks/user_prompt_submit.py (!save interceptor)
- tests/ (22 tests)
