# Obsidian Web Clipper Setup

Setup guide for saving web pages into MetaMode RAW inbox via Obsidian Web Clipper.

## Prerequisites

- Obsidian installed with `knowledge/` opened as vault
- Chrome or Firefox browser

## Step 1: Install Obsidian Web Clipper

1. Go to https://obsidian.md/clipper
2. Click "Get the extension" for your browser (Chrome / Firefox)
3. Install and pin the extension to toolbar

## Step 2: Configure the extension

1. Click the Web Clipper icon in browser toolbar
2. Click the gear icon (Settings)
3. Under **General**:
   - Vault: select the vault that points to `knowledge/`
4. Under **Templates**:
   - Create a new template called "MetaMode RAW"
   - **Note name**: `{{title|slugify}}`
   - **Save to folder**: `../raw` (relative to knowledge/ vault root)
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

**Clip goes to wrong folder**: Check that the template's "Save to folder" path is `../raw` (one level up from the vault root `knowledge/`).

**Images not downloading**: Make sure "Local Images Plus" is enabled and configured with the correct media folder path.

**ingest_raw.py fails**: Check that `raw/` contains valid markdown files. Binary files or non-markdown content will cause errors.
