# Obsidian Web Clipper Setup

Save web pages directly into Claude's memory. Web Clipper turns any article, documentation page, or research into a markdown file in MetaMode's RAW inbox — one `ingest_raw.py` run later, Claude knows what you read.

## Why This Matters

Claude Code forgets everything between sessions. MetaMode fixes that for *conversations*, but what about knowledge you find *outside* Claude — blog posts, framework docs, Stack Overflow answers? Web Clipper closes that gap:

```text
Web page → Clip → raw/article.md → ingest_raw.py → knowledge/concepts/*.md → session_start → Claude knows
```

Without Web Clipper, you'd have to copy-paste content into Claude's context window every time. With it, you clip once and Claude remembers forever.

## Use Cases

**Learning a new framework** — clip the key docs pages (getting started, API reference, common patterns). After ingestion, Claude can reference them when writing code — no more "paste the docs" in every session.

**Saving a debugging solution** — found a GitHub issue or blog post that solved your bug? Clip it. Next time the same problem appears, Claude already knows the fix.

**Research synthesis** — clip 5-10 articles on a topic, run ingest, then ask Claude to synthesize patterns across all of them. The wiki compiler groups related concepts automatically.

**Preserving ephemeral content** — Discord messages, Slack threads, forum posts that might get deleted. Clip now, process later.

## Prerequisites

- Obsidian installed with `MetaMode/` opened as vault (see [Obsidian setup](obsidian-setup.md))
- Chrome or Firefox browser

## Step 1: Install Obsidian Web Clipper

1. Go to https://obsidian.md/clipper
2. Click "Get the extension" for your browser (Chrome / Firefox)
3. Install and pin the extension to toolbar

## Step 2: Configure the extension

1. Click the Web Clipper icon in browser toolbar
2. Click the gear icon (Settings)
3. Under **General**:
   - Vault: select the vault that points to your `MetaMode/` root directory (same vault as in [Obsidian setup](obsidian-setup.md))
4. Under **Templates**:
   - Create a new template called "MetaMode RAW"
   - **Note name**: `{{title|slugify}}`
   - **Save to folder**: `raw` (relative to vault root = MetaMode/)
   - **Template content**:

```markdown
# {{title}}

## Context
Clipped from: {{url}}
Date: {{date}}

## Key Insight
{{selection|default:content}}

## Source
[{{title}}]({{url}})
```

5. Click Save

## Step 3: Install "Local Images Plus" plugin (optional)

This plugin downloads images from clipped pages to local storage.

1. Obsidian → Settings → Community Plugins → Browse
2. Search for "Local Images Plus"
3. Install → Enable
4. In plugin settings:
   - Media folder: `knowledge/attachments/`

## Step 4: Usage

1. Browse to a page with useful content
2. Select the text you want to save (optional — if nothing selected, clips full page)
3. Click the Web Clipper icon
4. Choose template "MetaMode RAW"
5. Click "Add to Obsidian"
6. File appears in `raw/` folder

## Step 5: Process clipped content

After clipping, run in Claude Code or terminal:

```bash
uv run python scripts/ingest_raw.py
```

This will:
- Read files from `raw/` (except README.md and `raw/processed/`)
- Create wiki articles in `knowledge/concepts/` and `knowledge/connections/`
- Update `knowledge/index.md`
- Move processed files to `raw/processed/`

## Troubleshooting

**Clip goes to wrong folder**: Check that the template's "Save to folder" path is `raw` (relative to your MetaMode vault root).

**Images not downloading**: Make sure "Local Images Plus" is enabled and configured with the correct media folder path.

**ingest_raw.py fails**: Check that `raw/` contains valid markdown files. Binary files or non-markdown content will cause errors.

## See Also

- [Ecosystem overview](ecosystem.md) — how Web Clipper fits into the full MetaMode pipeline
- [Obsidian setup](obsidian-setup.md) — browsing your wiki with graph view and search
- [RAW Inbox](raw-inbox.md) — other ways to add external documents
