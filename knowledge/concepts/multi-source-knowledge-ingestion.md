---
title: "Multi-Source Knowledge Ingestion"
aliases: [external knowledge pipeline, RAW inbox, ingest_raw]
tags: [ai, workflow, meta, productivity]
category: "ai"
sources:
  - "raw/metamode-vs-coleam00-audit.md"
created: 2026-04-12
updated: 2026-04-12
---

# Multi-Source Knowledge Ingestion

**Context:** When building a personal knowledge base that should capture insights from multiple sources — not just AI conversations, but also articles, videos, transcripts, and notes.

**Problem:** Conversation-only capture misses a large portion of learning. Developers learn from blog posts, conference talks, documentation, code reviews, and other external sources that never pass through an AI session.

**Lesson:** A knowledge system needs an external ingestion pipeline alongside conversation capture. A simple "RAW inbox" pattern — drop a file, run a processor — handles this without complex infrastructure.

## Key Points

- coleam00 captures knowledge only from Claude Code conversations (SessionEnd → flush → daily log)
- MetaMode adds `ingest_raw.py` — a script that processes markdown files from a `raw/` inbox into structured wiki articles
- The RAW inbox pattern: user drops a markdown file into `raw/`, runs `uv run python scripts/ingest_raw.py`, processed files move to `raw/processed/`
- Obsidian Web Clipper can save articles directly to the `raw/` folder, creating a browser → wiki pipeline
- The same LLM (Claude Agent SDK) processes both conversation transcripts and external documents, ensuring consistent article quality

## Details

The original coleam00 system captures knowledge exclusively from Claude Code sessions. The SessionEnd hook extracts the conversation transcript, flush.py sends it to the LLM for summarization, and the result goes into the daily log. This works well for conversation-derived insights but ignores everything the developer learns outside of Claude Code.

MetaMode's `ingest_raw.py` adds a parallel pipeline for external sources. The user places a markdown file in the `raw/` directory — either manually, via Obsidian Web Clipper, or through any tool that can write markdown files. Running the ingest script processes each file: the LLM reads the content, extracts concepts and connections following the same AGENTS.md schema, creates structured wiki articles in `knowledge/concepts/` and `knowledge/connections/`, updates the index, and moves the processed file to `raw/processed/`.

The session start hook reminds the user when unprocessed files exist in the RAW inbox, preventing files from being forgotten. This creates a complete capture loop: conversations are captured automatically (flush.py), external knowledge is captured semi-automatically (drop file + run script), and both produce identically-structured wiki articles.

The key architectural decision was reusing the same processing pipeline (LLM + AGENTS.md schema) for both sources. This means external articles produce the same article format as conversation-derived insights, making the knowledge base uniform regardless of source. The alternative — separate formats for different sources — would fragment the wiki and complicate search/compilation.

## Related Concepts

- [[concepts/human-in-the-loop-quality-gate]] - External ingestion has an implicit quality gate: the user chose to save the article
- [[concepts/fork-dont-rewrite]] - ingest_raw.py was added as a new file, not by modifying the existing flush pipeline
