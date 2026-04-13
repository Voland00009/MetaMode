# RAW Inbox — External Knowledge Ingestion

The `raw/` directory is MetaMode's inbox for external documents. Drop markdown or text files there, run the ingestion script, and they become structured wiki articles alongside your auto-captured session knowledge.

## How It Works

```
1. Drop .md or .txt files into raw/
2. Run: uv run python scripts/ingest_raw.py
3. Files → wiki articles in knowledge/concepts/ and knowledge/connections/
4. Originals move to raw/processed/
5. knowledge/index.md updated automatically
```

## File Format

For best results, use this structure:

```markdown
# Title of the Concept

## Context
Where you encountered this, why it matters.

## Key Insight
The core idea — what you want to remember.

## Example
A concrete example or code snippet.
```

But any markdown works — the ingestion script uses Claude Agent SDK to extract structure from whatever you provide.

## Use Cases

### 1. Article/Blog Notes
Read an interesting article? Copy the key points into a `.md` file, drop it in `raw/`, and ingest. The insight lives in your wiki forever, searchable and connected to related concepts.

### 2. Meeting Notes
After a meeting, jot down decisions and action items in markdown. Ingest into MetaMode — now Claude knows what was decided without you repeating it.

### 3. Course/Tutorial Highlights
Taking an online course? Save key takeaways per module. After ingestion, you can query your wiki: "what did I learn about database indexing?"

### 4. Code Review Insights
Found a great pattern in someone else's code review? Save it to raw and ingest. It becomes a wiki article you can reference months later.

### 5. Research Dumps
Working on a problem? Dump links, notes, and findings into raw. After ingestion, Claude has context from your research without you explaining it every session.

### 6. External Documentation
Copy relevant sections from documentation (framework guides, API docs, internal wikis) into raw. This gives Claude Code persistent access to information it might not have in its training data.

## Why This Matters

Claude Code starts each session fresh. Without MetaMode, you'd need to re-explain context every time. The RAW inbox lets you feed Claude external knowledge that:

- **Persists across sessions** — saved in git, available forever
- **Gets compiled** — raw notes become structured wiki articles with wikilinks
- **Connects to session knowledge** — the compile step links raw-sourced articles to conversation-sourced articles
- **Costs nothing extra** — the Agent SDK calls for ingestion are covered by your Max subscription

## Session Start Reminder

MetaMode automatically checks `raw/` at session start. If unprocessed files exist, you'll see:

```
3 unprocessed file(s) in raw/: notes.md, research.md, review.md.
Say 'обработай RAW' or run `uv run python scripts/ingest_raw.py`.
```

## Tips

- **One concept per file** — produces cleaner wiki articles than dumping everything in one file
- **Use descriptive filenames** — `python-import-binding.md` is better than `notes.md`
- **Don't worry about perfection** — the ingestion script extracts structure even from rough notes
- **Check results after ingestion** — open `knowledge/index.md` to verify new articles look right
- **Git tracks everything** — if an ingestion produces bad results, `git checkout` reverts it
