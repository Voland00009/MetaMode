---
title: "Claude Agent SDK Works on Max Subscription ($0/mo)"
aliases: [agent sdk max, sdk without api key, cli to sdk migration]
tags: [claude-code, claude-api, anthropic, workflow]
category: "claude-code"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
updated: 2026-04-12
---

# Claude Agent SDK Works on Max Subscription ($0/mo)

**Context:** When building automation scripts (flush, compile, lint, query) that need to call Claude programmatically, and deciding between CLI subprocess calls (`claude -p`) and the Agent SDK (`claude-agent-sdk` Python package).

**Problem:** The assumption was that Claude Agent SDK requires a paid API key with per-token billing, making CLI subprocess the only $0/mo option for Max subscribers. This assumption delayed migration and forced workarounds for CLI limitations (argument length limits, JSON output variance, shell escaping).

**Lesson:** Claude Agent SDK works on Max subscription without an API key. This was confirmed empirically during MetaMode SDK migration — all 5 scripts migrated from CLI to SDK with zero API cost.

## Key Points

- `claude-agent-sdk` Python package authenticates through the same Max subscription as Claude Code CLI — no separate API key needed
- Migrating from CLI subprocess to SDK eliminates: argument length limits (Windows ~8K), JSON output parsing, shell escaping issues
- The migration pattern: `subprocess.run(["claude", "-p", prompt])` → `async with claude.Agent() as agent: result = await agent.send(prompt)`
- `asyncio.run()` in a sync `main()` bridges the async SDK into existing synchronous scripts
- 5 scripts migrated (flush, compile, query, lint, ingest_raw) with all 22 tests passing after migration

## Details

During MetaMode development, the initial architecture used `claude -p --output-format json` subprocess calls to interact with Claude from Python scripts. This worked but introduced several platform-specific bugs: Windows CLI argument length limit (~8K chars) broke prompts containing full wiki content, the `result` field in JSON output could be either a string or an array (requiring defensive type checking), and shell escaping on Windows was fragile.

The assumption that SDK required a paid API key kept the project on CLI subprocess calls through Phases B.1-C. During the SDK migration session, this assumption was tested empirically by installing `claude-agent-sdk` and running a script — it authenticated successfully using the existing Max subscription with no API key configuration.

The migration was straightforward: each script's `call_claude(prompt)` function was converted from a synchronous subprocess call to an async SDK call. The `asyncio.run()` bridge pattern preserved the synchronous public API of each script while using async internally. For `lint.py`, which needed to maintain its synchronous public API for integration with other tools, a sync wrapper called the async internals.

SDK-specific gotchas discovered during migration: `TextBlock(text=text)` — the constructor does not accept a `type` parameter. `AssistantMessage(content=[...], model="test")` — `model` is a required positional argument. `ResultMessage.total_cost_usd` is `float | None` — check with `if message.total_cost_usd:` before using.

## Related Concepts

- [[concepts/windows-cli-arg-length-limit]] - The CLI limitation that SDK migration eliminates entirely
- [[concepts/claude-cli-json-output-variance]] - Another CLI gotcha eliminated by SDK's typed response objects
- [[concepts/fork-dont-rewrite]] - SDK migration was additive (new module replacing old), not a rewrite of the pipeline

