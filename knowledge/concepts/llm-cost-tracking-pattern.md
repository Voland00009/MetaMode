---
title: "LLM Cost Tracking via SDK Accumulation"
aliases: [cost tracking, total_cost_usd, token cost accumulation]
tags: [ai, claude-api, workflow, devtools]
category: "ai"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
updated: 2026-04-12
---

# LLM Cost Tracking via SDK Accumulation

**Context:** When building tools that make multiple LLM calls across different scripts (flush, compile, query) and you want to track cumulative spending without a billing dashboard.

**Problem:** Individual LLM calls have small costs that feel negligible, but they accumulate across dozens of daily operations. Without tracking, spending is invisible until a billing surprise — especially important when verifying a "$0/mo" assumption on a Max subscription.

**Lesson:** Accumulate `ResultMessage.total_cost_usd` from each SDK call into a shared `state.json` file. Each script adds its cost to a running `total_cost` field, providing a single source of truth for cumulative LLM spending.

## Key Points

- `ResultMessage.total_cost_usd` is `float | None` — always check `if message.total_cost_usd:` before accumulating
- Three SDK-calling scripts (flush, compile, query) all write to the same `state.json["total_cost"]` field
- flush.py uses a separate bridge function (`_accumulate_cost()`) because it has its own `last-flush.json` state file, distinct from the shared `state.json`
- On Max subscription, `total_cost_usd` reports 0.0 — the tracking confirms the $0/mo claim empirically
- The pattern works identically for paid API keys, where the accumulated cost becomes a real budget monitoring tool

## Details

During MetaMode v2 implementation, cost tracking was added to all three scripts that call the Claude Agent SDK. The implementation reads the current `total_cost` from `scripts/state.json`, adds the cost from the latest SDK response, and writes the updated total back. This happens after every successful LLM call, so the state file always reflects cumulative spending.

The `flush.py` script required special handling because it maintains its own state file (`scripts/last-flush.json`) for flush-specific data like the last flush timestamp and session ID. Rather than duplicating the cost tracking logic, a bridge function `_accumulate_cost()` reads from the shared `state.json`, updates the total, and writes back — keeping the cost data centralized even though flush.py's other state is separate.

The type handling for `total_cost_usd` is important: the field is `float | None` on the `ResultMessage` object. A `None` value indicates the cost couldn't be determined (e.g., during testing with mock responses). The guard `if message.total_cost_usd:` handles both `None` and `0.0` correctly — a zero cost doesn't need to be accumulated.

## Related Concepts

- [[concepts/claude-agent-sdk-max-subscription]] - SDK on Max reports $0 cost, which this tracking pattern validates
- [[concepts/two-pass-llm-quality-audit]] - The quality audit pass is an additional SDK call whose cost is tracked by the same mechanism
- [[concepts/fork-dont-rewrite]] - Cost tracking was borrowed from coleam00's original design and adapted to the SDK migration

