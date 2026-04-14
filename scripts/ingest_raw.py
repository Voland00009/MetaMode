"""Ingest external files from raw/ into structured knowledge articles.

Similar to compile.py but for external data (articles, transcripts, notes)
rather than daily conversation logs.

Usage:
    uv run python ingest_raw.py
    uv run python ingest_raw.py --file raw/some-article.md
    uv run python ingest_raw.py --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import shutil
import sys
from pathlib import Path

from config import AGENTS_FILE, CONCEPTS_DIR, CONNECTIONS_DIR, KNOWLEDGE_DIR, RAW_DIR, ROOT_DIR, build_agent_options, now_iso
from utils import (
    file_hash,
    list_wiki_articles,
    load_state,
    read_wiki_index,
    save_state,
)

PROCESSED_DIR = RAW_DIR / "processed"
RAW_EXTENSIONS = {".md", ".txt"}


def list_raw_inbox() -> list[Path]:
    """List unprocessed files in raw/ (excludes README and processed/)."""
    if not RAW_DIR.exists():
        return []
    files = []
    for f in sorted(RAW_DIR.iterdir()):
        if f.is_file() and f.suffix in RAW_EXTENSIONS and f.name != "README.md":
            files.append(f)
    return files


async def ingest_raw_file(raw_path: Path, state: dict) -> None:
    """Process a single raw file into knowledge articles."""
    content = raw_path.read_text(encoding="utf-8")
    schema = AGENTS_FILE.read_text(encoding="utf-8")
    wiki_index = read_wiki_index()

    existing_articles_context = ""
    existing = {}
    for article_path in list_wiki_articles():
        rel = article_path.relative_to(KNOWLEDGE_DIR)
        existing[str(rel)] = article_path.read_text(encoding="utf-8")

    if existing:
        parts = []
        for rel_path, article_content in existing.items():
            parts.append(f"### {rel_path}\n```markdown\n{article_content}\n```")
        existing_articles_context = "\n\n".join(parts)

    timestamp = now_iso()

    prompt = f"""You are a knowledge compiler. Your job is to read an external document
and extract knowledge into structured wiki articles.

## Schema (AGENTS.md)

{schema}

## Current Wiki Index

{wiki_index}

## Existing Wiki Articles

{existing_articles_context if existing_articles_context else "(No existing articles yet)"}

## Document to Process

**File:** {raw_path.name}

{content}

## Your Task

Read the document above and extract knowledge into wiki articles following the schema exactly.

### Rules:

1. **Extract key concepts** - Identify 3-7 distinct concepts worth their own article
2. **Create concept articles** in `knowledge/concepts/` - One .md file per concept
   - Use the exact article format from AGENTS.md (YAML frontmatter + sections)
   - Include `sources:` in frontmatter pointing to `raw/{raw_path.name}`
   - Use `[[concepts/slug]]` wikilinks to link to related concepts
   - Write in encyclopedia style - neutral, comprehensive
3. **Create connection articles** in `knowledge/connections/` if this document reveals non-obvious
   relationships between 2+ concepts
4. **Update existing articles** if this document adds new information to concepts already in the wiki
   - Read the existing article, add the new information, add the source to frontmatter
5. **Update knowledge/index.md** - Add new entries to the table
   - Each entry: `| [[path/slug]] | One-line summary | source-file | {timestamp[:10]} |`
6. **Append to knowledge/log.md** - Add a timestamped entry:
   ```
   ## [{timestamp}] ingest | {raw_path.name}
   - Source: raw/{raw_path.name}
   - Articles created: [[concepts/x]], [[concepts/y]]
   - Articles updated: [[concepts/z]] (if any)
   ```

### File paths:
- Write concept articles to: {CONCEPTS_DIR}
- Write connection articles to: {CONNECTIONS_DIR}
- Update index at: {KNOWLEDGE_DIR / 'index.md'}
- Append log at: {KNOWLEDGE_DIR / 'log.md'}

### Quality standards:
- Every article must have complete YAML frontmatter
- Every article must link to at least 2 other articles via [[wikilinks]]
- Key Points section should have 3-5 bullet points
- Details section should have 2+ paragraphs
- Related Concepts section should have 2+ entries
- Sources section should cite the raw file with specific claims extracted
"""

    from claude_agent_sdk import (
        AssistantMessage,
        ResultMessage,
        TextBlock,
        query,
    )

    try:
        async for message in query(
            prompt=prompt,
            options=build_agent_options(
                cwd=str(ROOT_DIR),
                system_prompt={"type": "preset", "preset": "claude_code"},
                allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
                permission_mode="acceptEdits",
                max_turns=30,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        pass  # LLM writes files directly
            elif isinstance(message, ResultMessage):
                if message.total_cost_usd:
                    state["total_cost"] = state.get("total_cost", 0.0) + message.total_cost_usd
    except Exception as e:
        print(f"  Error: {e}")
        return

    # Move processed file to raw/processed/
    PROCESSED_DIR.mkdir(exist_ok=True)
    dest = PROCESSED_DIR / raw_path.name
    if dest.exists():
        dest = PROCESSED_DIR / f"{raw_path.stem}_{timestamp[:10]}{raw_path.suffix}"
    shutil.move(str(raw_path), str(dest))
    print(f"  Moved to {dest.relative_to(RAW_DIR.parent)}")

    # Update state
    state.setdefault("raw_ingested", {})[raw_path.name] = {
        "hash": file_hash(dest),
        "ingested_at": timestamp,
    }
    save_state(state)


def main():
    parser = argparse.ArgumentParser(description="Ingest raw files into knowledge articles")
    parser.add_argument("--file", type=str, help="Ingest a specific raw file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be ingested")
    args = parser.parse_args()

    state = load_state()

    if args.file:
        target = Path(args.file)
        if not target.is_absolute():
            target = RAW_DIR / target.name
        if not target.exists():
            target = ROOT_DIR / args.file
        if not target.exists():
            print(f"Error: {args.file} not found")
            sys.exit(1)
        to_ingest = [target]
    else:
        to_ingest = list_raw_inbox()

    if not to_ingest:
        print("Nothing to ingest - raw/ inbox is empty.")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Files to ingest ({len(to_ingest)}):")
    for f in to_ingest:
        print(f"  - {f.name}")

    if args.dry_run:
        return

    for i, raw_path in enumerate(to_ingest, 1):
        print(f"\n[{i}/{len(to_ingest)}] Ingesting {raw_path.name}...")
        asyncio.run(ingest_raw_file(raw_path, state))
        print(f"  Done.")

    articles = list_wiki_articles()
    print(f"\nIngestion complete.")
    print(f"Knowledge base: {len(articles)} articles")


if __name__ == "__main__":
    main()
