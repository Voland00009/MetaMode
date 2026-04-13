# Obsidian Integration

MetaMode's `knowledge/` directory is a native Obsidian vault. No plugins or extensions needed — Obsidian reads markdown and wikilinks (`[[concept]]`) out of the box.

## Setup

1. [Download Obsidian](https://obsidian.md/) (free for personal use)
2. Open as vault: **File → Open Vault → Open folder as vault** → select your `MetaMode/` root directory
3. Done. All wiki articles, daily logs, and connections are immediately browsable.

## What You Get

### Graph View
Open Graph View (`Ctrl+G` / `Cmd+G`) to see how your knowledge connects. MetaMode articles use `[[wikilinks]]` which Obsidian renders as clickable connections. Clusters show which concepts relate to each other.

### Live Preview
Edit `knowledge/concepts/*.md` directly — changes are saved to disk and will be picked up by MetaMode's compile and lint pipelines.

### Search
`Ctrl+Shift+F` searches across all daily logs, wiki articles, and raw inbox files. Faster than grep for exploring your knowledge base.

### Daily Notes
MetaMode's `daily/` directory contains auto-generated daily logs. Open any `YYYY-MM-DD.md` to review what Claude captured from that day's sessions.

## Use Cases

### 1. Visual Knowledge Exploration
After a few weeks of using MetaMode, your graph view shows a web of interconnected concepts. Click through nodes to rediscover patterns you learned weeks ago. This is especially useful before starting work in an area you haven't touched recently.

### 2. Quick Manual Notes
Open any daily log in Obsidian and type directly. MetaMode's compile pipeline will pick up your additions when it next runs. You can also use `!save <text>` in Claude Code for zero-token quick saves.

### 3. Review Before Sessions
Before a Claude Code session, scan your graph or recent daily logs in Obsidian. This gives you context that helps you ask better questions and avoid repeating past mistakes.

### 4. Knowledge Audit
Sort articles by modification date, check which concepts have no inbound links (orphans), or find articles that are too short. MetaMode's `lint.py` does this automatically, but Obsidian makes it visual.

### 5. Cross-Project Patterns
Since MetaMode captures knowledge from ALL projects (global hooks), Obsidian's graph view reveals patterns across projects — e.g., the same debugging technique appears in both a Python backend and a React frontend.

## Important Notes

- **Obsidian is optional.** MetaMode works entirely without it — the wiki is plain markdown files managed by git.
- **No custom plugins required.** Everything works with vanilla Obsidian.
- **Don't rename files in Obsidian** if you want wikilinks to stay consistent. Use MetaMode's compile pipeline for structural changes.
- **The vault is the MetaMode root**, not just `knowledge/`. This lets you see daily logs, raw inbox, and knowledge articles in one place.

## Web Clipper

Obsidian Web Clipper saves web pages directly into MetaMode's `raw/` inbox. One click to clip, one command to ingest — Claude remembers what you read.

See [Web Clipper setup](web-clipper-setup.md) for installation and configuration.

## See Also

- [Ecosystem overview](ecosystem.md) — how Obsidian fits into the full MetaMode pipeline
- [Web Clipper setup](web-clipper-setup.md) — save web pages into Claude's memory
- [NotebookLM setup](notebooklm-setup.md) — audio overviews and chat with your knowledge
