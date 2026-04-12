# RAW — External Data Inbox

Drop external materials here for processing into the knowledge wiki.

## What to put here

- Articles (markdown, plain text)
- PDF highlights or exports
- Transcripts (video, podcast)
- Notes and clippings (Obsidian Web Clipper output)
- Any text you want turned into wiki articles

## How to process

1. Drop file(s) into this folder
2. Tell Claude: "обработай RAW" or "process RAW"
3. Claude reads files, creates wiki articles in `knowledge/concepts/` and `knowledge/connections/`, updates `index.md`
4. Processed files get moved to `raw/processed/`

## Naming

No strict rules. Use descriptive names: `karpathy-memory-transcript.md`, `oauth-article.txt`, etc.

## Supported formats

- `.md` (markdown)
- `.txt` (plain text)

PDF and images are not directly supported — convert to text first.
