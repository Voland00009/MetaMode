---
title: "Two-Pass LLM Quality Audit (Extract + Audit)"
aliases: [quality audit, AUDIT_FLAG, two-pass extraction, extract-then-audit]
tags: [ai, agents, workflow, meta]
category: "ai"
sources:
  - "daily/2026-04-12.md"
created: 2026-04-12
updated: 2026-04-12
---

# Two-Pass LLM Quality Audit (Extract + Audit)

**Context:** When building AI knowledge capture systems that auto-save session content but need quality control without manual review friction.

**Problem:** Manual pending review creates too much friction — users skip it. Fully automatic capture accumulates junk (95% in mem0 experiment). Neither extreme works.

**Lesson:** Use a two-pass LLM system: Pass 1 extracts and saves all knowledge (auto-save, zero friction). Pass 2 audits quality and marks junk with `<!-- AUDIT_FLAG: reason -->` — but never deletes. Downstream tools (compile.py) skip flagged entries.

## Key Points

- Pass 1 (extraction): LLM extracts knowledge from session transcript → writes directly to daily log (same as coleam00, zero friction)
- Pass 2 (audit): separate LLM call reviews each extracted entry against 4 junk criteria → marks low-quality entries with HTML comment flags
- The 4 junk criteria (all must be true simultaneously): no lessons learned + no decisions made + no reusable patterns + only routine operations
- Critical safety rule: audit **never deletes** data, only marks it — human can always review and unflag
- Compile.py skips entries with `<!-- AUDIT_FLAG -->` when building wiki articles, keeping the knowledge base clean

## Details

MetaMode v1 used a manual pending review pattern: flush.py extracted knowledge into a staging area, and the user approved entries at the next session start. This was theoretically sound but failed in practice — the approval step was buried in a long session start context, easy to miss, and created friction that a beginning developer would skip.

The v2 replacement uses two LLM passes within flush.py itself. The first pass extracts knowledge from the conversation transcript exactly as coleam00 does — writing everything to the daily log with no human intervention. The second pass immediately re-reads the extracted content and evaluates each entry against strict quality criteria. Entries that fail all four criteria simultaneously are marked with an HTML comment: `<!-- AUDIT_FLAG: routine debugging, no reusable pattern -->`.

The AUDIT_FLAG approach is deliberately conservative. When in doubt, the audit preserves the entry (no flag). If the SDK call fails or returns an ambiguous response, the entry is preserved. The flag is a soft signal, not a hard gate — a human reviewing the daily log can see flagged entries and unflag them if the audit was wrong. This "mark but don't delete" principle ensures that the worst case is a false positive (extra entry in the wiki) rather than a false negative (lost knowledge).

The compile.py step reads the daily log and skips any section containing an AUDIT_FLAG comment. This means flagged entries persist in the daily log for reference but don't propagate into wiki articles, keeping the structured knowledge base clean while maintaining a complete raw record.

## Related Concepts

- [[concepts/human-in-the-loop-quality-gate]] - The predecessor pattern (manual review) that this replaced due to UX friction
- [[connections/quality-vs-automation-tradeoff]] - This is the practical implementation of "automation + lightweight gate"
- [[concepts/fork-dont-rewrite]] - The audit was added as a new pass in flush.py, not a rewrite of the extraction logic
