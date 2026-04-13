# MetaMode-public Repository — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a clean public repository `MetaMode-public/` with exhaustive English documentation, example content, and a NotebookLM presentation — ready for sharing with Claude Code users.

**Architecture:** Fresh directory (no git history from private repo). Copy source code, strip personal data, add `.gitkeep` placeholders with example content, rewrite all docs for public audience. Presentation via NotebookLM skill.

**Tech Stack:** Python, uv, Claude Agent SDK, Markdown, NotebookLM

---

## File Structure

### Files to CREATE (new for public repo)
- `docs/setup.md` — step-by-step installation guide (cross-platform)
- `docs/commands.md` — exhaustive command reference
- `docs/how-it-works.md` — deep dive into pipeline
- `daily/.gitkeep`
- `daily/example-2026-01-15.md` — example daily log
- `knowledge/concepts/.gitkeep`
- `knowledge/concepts/example-python-context-managers.md` — example wiki article
- `knowledge/connections/.gitkeep`
- `knowledge/connections/example-context-managers-and-testing.md` — example connection
- `knowledge/qa/.gitkeep`
- `raw/.gitkeep`
- `raw/example-article.md` — example RAW input
- `reports/.gitkeep`
- `plans/.gitkeep`
- `knowledge/index.md` — starter index with example entries
- `knowledge/log.md` — empty starter log

### Files to COPY from private repo (source code — unchanged)
- `hooks/session_start.py`
- `hooks/session_end.py`
- `hooks/pre_compact.py`
- `hooks/user_prompt_submit.py`
- `hooks/shared.py`
- `scripts/config.py`
- `scripts/flush.py`
- `scripts/compile.py`
- `scripts/ingest_raw.py`
- `scripts/query.py`
- `scripts/lint.py`
- `scripts/memory_lint.py`
- `scripts/utils.py`
- `AGENTS.md`
- `CLAUDE.md` (will be rewritten for public)
- `pyproject.toml`
- `LICENSE`

### Files to REWRITE for public audience
- `README.md` — complete rewrite (English, user-facing)
- `CLAUDE.md` — generic version without personal preferences
- `.gitignore` — expanded for public use
- `docs/cheatsheet.md` — English translation

### Files to NOT copy (personal/private)
- `input/` — entire directory (100+ personal files)
- `daily/2026-*.md` — real session logs
- `knowledge/concepts/*.md` — real wiki articles (personal knowledge)
- `knowledge/connections/*.md` — real connections
- `knowledge/qa/*.md` — real Q&A
- `raw/*.md` — real RAW files
- `reports/audit/` — audit reports
- `scripts/state.json` — runtime state
- `.claude/` — Claude Code settings
- `docs/cross-project-template.md` — keep (useful for users)

---

## Task 1: Create directory and copy source code

**Files:**
- Create: `C:/Users/Voland/Dev/MetaMode-public/` (entire directory structure)

- [ ] **Step 1: Create MetaMode-public directory**

```bash
mkdir -p /c/Users/Voland/Dev/MetaMode-public
```

- [ ] **Step 2: Copy source code files**

```bash
# Create directory structure
cd /c/Users/Voland/Dev/MetaMode-public
mkdir -p hooks scripts docs daily knowledge/concepts knowledge/connections knowledge/qa raw reports plans

# Copy Python source
cp /c/Users/Voland/Dev/MetaMode/hooks/session_start.py hooks/
cp /c/Users/Voland/Dev/MetaMode/hooks/session_end.py hooks/
cp /c/Users/Voland/Dev/MetaMode/hooks/pre_compact.py hooks/
cp /c/Users/Voland/Dev/MetaMode/hooks/user_prompt_submit.py hooks/
cp /c/Users/Voland/Dev/MetaMode/hooks/shared.py hooks/

cp /c/Users/Voland/Dev/MetaMode/scripts/config.py scripts/
cp /c/Users/Voland/Dev/MetaMode/scripts/flush.py scripts/
cp /c/Users/Voland/Dev/MetaMode/scripts/compile.py scripts/
cp /c/Users/Voland/Dev/MetaMode/scripts/ingest_raw.py scripts/
cp /c/Users/Voland/Dev/MetaMode/scripts/query.py scripts/
cp /c/Users/Voland/Dev/MetaMode/scripts/lint.py scripts/
cp /c/Users/Voland/Dev/MetaMode/scripts/memory_lint.py scripts/
cp /c/Users/Voland/Dev/MetaMode/scripts/utils.py scripts/

# Copy config files
cp /c/Users/Voland/Dev/MetaMode/AGENTS.md .
cp /c/Users/Voland/Dev/MetaMode/pyproject.toml .
cp /c/Users/Voland/Dev/MetaMode/LICENSE .
cp /c/Users/Voland/Dev/MetaMode/docs/cross-project-template.md docs/
cp /c/Users/Voland/Dev/MetaMode/docs/features.md docs/
```

- [ ] **Step 3: Initialize git repo**

```bash
cd /c/Users/Voland/Dev/MetaMode-public
git init
```

- [ ] **Step 4: Verify — all Python files present, no personal data**

```bash
find . -name "*.py" | sort
# Expected: 13 Python files in hooks/ and scripts/
ls input/ 2>/dev/null
# Expected: directory not found (good — no personal data)
```

---

## Task 2: .gitignore and .gitkeep files

**Files:**
- Create: `.gitignore`
- Create: `.gitkeep` files in empty directories

- [ ] **Step 1: Write public .gitignore**

```gitignore
# Python
.venv/
__pycache__/
*.pyc
dist/

# Runtime state (regenerated automatically)
scripts/state.json
scripts/last-flush.json
scripts/flush.log
scripts/session-flush-*.md
scripts/flush-context-*.md
scripts/pending-review.md
scripts/compile.log

# Personal content — keep your data local
# Uncomment these if you want to exclude personal content from git:
# daily/*.md
# !daily/example-*.md
# knowledge/concepts/*.md
# !knowledge/concepts/example-*.md
# knowledge/connections/*.md
# !knowledge/connections/example-*.md
# knowledge/qa/*.md
# raw/*.md
# !raw/example-*.md

# Reports (generated by lint)
reports/*.md

# Editor
.vscode/
.idea/

# Obsidian
.obsidian/
knowledge/.obsidian/
*.base
*.canvas

# OS
.DS_Store
Thumbs.db

# Claude Code local settings
.claude/settings.local.json
```

- [ ] **Step 2: Create .gitkeep files**

```bash
touch daily/.gitkeep
touch knowledge/concepts/.gitkeep
touch knowledge/connections/.gitkeep
touch knowledge/qa/.gitkeep
touch raw/.gitkeep
touch reports/.gitkeep
touch plans/.gitkeep
```

- [ ] **Step 3: Commit — repo skeleton**

```bash
git add -A
git commit -m "chore: repo skeleton — source code, .gitignore, directory structure"
```

---

## Task 3: Example content

**Files:**
- Create: `daily/example-2026-01-15.md`
- Create: `knowledge/concepts/example-python-context-managers.md`
- Create: `knowledge/connections/example-context-managers-and-testing.md`
- Create: `raw/example-article.md`
- Create: `knowledge/index.md`
- Create: `knowledge/log.md`

- [ ] **Step 1: Write example daily log**

File: `daily/example-2026-01-15.md`

This should look like a real daily log entry — 2 sessions, demonstrating the format that flush.py produces. Include:
- Session header with timestamp
- Context, Key Exchanges, Decisions Made, Lessons Learned, Action Items sections
- One session about a real coding topic (e.g., setting up a REST API)
- One quick save entry

Reference the actual format from `flush.py` prompt.

- [ ] **Step 2: Write example concept article**

File: `knowledge/concepts/example-python-context-managers.md`

Follow the AGENTS.md schema exactly:
- YAML frontmatter (title, aliases, tags, category, sources, created, updated)
- Context → Problem → Lesson
- Key Points, Details, Related Concepts sections
- Source pointing to the example daily log

- [ ] **Step 3: Write example connection article**

File: `knowledge/connections/example-context-managers-and-testing.md`

Follow the AGENTS.md connection schema:
- Shows how two concepts relate
- References both concept articles via wikilinks

- [ ] **Step 4: Write example RAW input file**

File: `raw/example-article.md`

Follow the RAW inbox format from CLAUDE.md:
- `# Title` → `## Context` → `## Key Insight` → `## Example`
- Topic: something practical (e.g., "Python asyncio common pitfalls")
- This is what a user would drop into `raw/` before running `ingest_raw.py`

- [ ] **Step 5: Write starter index.md**

File: `knowledge/index.md`

```markdown
# Knowledge Base Index

| Article | Summary | Compiled From | Updated |
|---------|---------|---------------|---------|
| [[concepts/example-python-context-managers]] | `with` statement manages resources automatically; always prefer over manual open/close | daily/example-2026-01-15.md | 2026-01-15 |
| [[connections/example-context-managers-and-testing]] | Context managers simplify test fixtures — same pattern, different purpose | daily/example-2026-01-15.md | 2026-01-15 |
```

- [ ] **Step 6: Write starter log.md**

File: `knowledge/log.md`

```markdown
# Knowledge Base Changelog

## 2026-01-15T18:30:00+00:00 compile | daily/example-2026-01-15.md
- Created: concepts/example-python-context-managers.md
- Created: connections/example-context-managers-and-testing.md
- Updated: index.md
```

- [ ] **Step 7: Commit — example content**

```bash
git add daily/example-*.md knowledge/ raw/example-*.md
git commit -m "docs: add example content — daily log, wiki articles, RAW input"
```

---

## Task 4: CLAUDE.md for public repo

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write generic CLAUDE.md**

This replaces the private CLAUDE.md. Must be generic (no personal preferences, no Russian):

```markdown
# MetaMode

Persistent wiki-memory layer for Claude Code — fork of coleam00/claude-memory-compiler.
Wiki-memory: hooks capture sessions → compile → structured wiki articles.
Stack: Python, uv, Claude Agent SDK ($0/mo on Max), Obsidian.

## Principles

1. **Hybrid save** — hooks auto-capture + `!save`/`/reflect` manual. Human-in-the-loop for quality.
2. **File-first** — everything in markdown, git versioning.
3. **$0/mo** — Max subscription only, no paid dependencies.
4. **Fork, don't rewrite** — minimal modifications on top of coleam00.

## Conventions

- Tests: logic for save/retrieve/compile; glue-code hooks — best effort
- Commits: explain WHY, not just WHAT
- Session workflow: one task = one session

## Constraints

- No LightRAG/vector DB (overkill for <1K docs)
- No full auto self-learning (replaced with quality audit)

## RAW Inbox

When user says "process RAW" / "ingest RAW":
`uv run python scripts/ingest_raw.py` — creates wiki articles, updates index, moves to `raw/processed/`
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add generic CLAUDE.md for public repo"
```

---

## Task 5: README.md — complete rewrite for public audience

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

Structure (all in English):

### Header
- Project name + one-line description
- Badges: Python 3.12+, License MIT, Cost $0/mo

### The Problem
2-3 sentences: Claude Code forgets everything. Every session starts from zero. You explain the same context over and over.

### The Solution
2-3 sentences: MetaMode captures sessions automatically, builds a wiki, injects context at session start. Claude remembers.

### How It Works (visual pipeline)
```
┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
│ You use      │───▶│ Hooks    │───▶│ flush.py │───▶│ Daily Log    │
│ Claude Code  │    │ capture  │    │ extract  │    │ (append)     │
└─────────────┘    │ session  │    │ + audit  │    └──────┬───────┘
                   └──────────┘    └──────────┘           │
                                                          ▼
┌─────────────┐    ┌──────────┐    ┌──────────────────────┐
│ Next session │◀───│ Inject   │◀───│ Wiki Articles        │
│ has context  │    │ at start │    │ (compile.py)         │
└─────────────┘    └──────────┘    └──────────────────────┘
```

### Before & After
Side-by-side comparison:
- **Without MetaMode:** "What framework are we using?" / "Can you remind me about the auth decision?"
- **With MetaMode:** Claude starts knowing your stack, decisions, patterns, lessons

### Quick Start
```bash
git clone https://github.com/Voland00009/MetaMode.git ~/Dev/MetaMode
cd MetaMode && uv sync
```
+ pointer to `docs/setup.md` for full instructions

### What You Get
Table of all tools with one-line descriptions:
| Tool | What it does |
|------|-------------|
| Auto-capture | Sessions saved automatically via hooks |
| `!save <text>` | Instant note, 0 tokens |
| `compile.py` | Daily logs → wiki articles |
| `query.py` | Ask your wiki from CLI |
| `ingest_raw.py` | External docs → wiki |
| `lint.py` | 7 health checks |
| `/reflect` | End-of-session reflection |

### Key Features (vs coleam00 original)
Numbered list of 7 differences (from current README, but explained for newcomers)

### Project Structure
Directory tree (from current README)

### Cost
$0/month — all LLM calls via Claude Max subscription

### Documentation
Links to setup.md, commands.md, how-it-works.md, cheatsheet.md

### Contributing + License

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for public audience — problem/solution/quickstart"
```

---

## Task 6: docs/setup.md — Installation guide

**Files:**
- Create: `docs/setup.md`

- [ ] **Step 1: Write setup.md**

Structure:

### Prerequisites
- Python 3.12+ (check: `python --version`)
- uv (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Claude Code CLI (install: `npm install -g @anthropic-ai/claude-code`)
- Claude Max subscription (for $0 Agent SDK calls)

### Installation

#### Step 1: Clone
```bash
git clone https://github.com/Voland00009/MetaMode.git ~/Dev/MetaMode
cd MetaMode
```

#### Step 2: Install dependencies
```bash
uv sync
```
Expected: "Resolved X packages..." message

#### Step 3: Configure hooks

**macOS/Linux:**
Edit `~/.claude/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [{"type": "command", "command": "uv run --directory ~/Dev/MetaMode python hooks/session_start.py"}],
    "SessionEnd": [{"type": "command", "command": "uv run --directory ~/Dev/MetaMode python hooks/session_end.py"}],
    "PreCompact": [{"type": "command", "command": "uv run --directory ~/Dev/MetaMode python hooks/pre_compact.py"}],
    "UserPromptSubmit": [{"type": "command", "command": "uv run --directory ~/Dev/MetaMode python hooks/user_prompt_submit.py"}]
  }
}
```

**Windows (PowerShell / Git Bash):**
Same but with Windows paths: `C:/Users/YOU/Dev/MetaMode`

**Note:** explain that hooks are global — fire from any project

#### Step 4: Verify installation
```bash
# Test session_start hook
uv run python hooks/session_start.py
# Expected: JSON with "additionalContext" key

# Test !save
echo '{"type":"user","content":"!save Test note"}' | uv run python hooks/user_prompt_submit.py
# Expected: stderr message "Saved to daily/..."
```

#### Step 5: Add wiki access to other projects
Point to `docs/cross-project-template.md`

### Copy-paste block for Claude Code
A single markdown block that a user can paste into Claude Code and have it do all setup automatically:
```
Install MetaMode for me. Clone from https://github.com/Voland00009/MetaMode.git to ~/Dev/MetaMode,
run uv sync, then configure hooks in ~/.claude/settings.json following docs/setup.md.
```

### Troubleshooting
- "uv not found" → install uv
- "claude-agent-sdk not found" → `uv sync` again
- Hooks not firing → check settings.json path, verify with `claude /hooks`
- Windows encoding issues → UTF-8 note
- "Permission denied" on macOS → chmod +x not needed (Python scripts)

### Uninstall
- Remove hooks from settings.json
- Delete the MetaMode directory
- That's it — no system-wide changes

- [ ] **Step 2: Commit**

```bash
git add docs/setup.md
git commit -m "docs: add setup.md — cross-platform installation guide"
```

---

## Task 7: docs/commands.md — Command reference

**Files:**
- Create: `docs/commands.md`

- [ ] **Step 1: Write commands.md**

Structure:

### Automatic (Hooks)
For each hook: what, when, how, what you see

| Hook | Trigger | What it does | User sees |
|------|---------|-------------|-----------|
| SessionStart | Every session start | Injects wiki index + recent log | Context appears in Claude's knowledge |
| SessionEnd | Session close | Extracts transcript → flush.py | Nothing (background) |
| PreCompact | Context compaction | Same as SessionEnd | Nothing (background) |
| UserPromptSubmit | `!save <text>` | Saves note, blocks prompt | Confirmation message |

### Manual CLI Commands

For EACH command, include:
- Full command with all flags
- What it does (2-3 sentences)
- All available flags with descriptions
- Example usage with expected output
- When to use it

Commands:
1. `compile.py` — `--all`, `--file`, `--dry-run`
2. `query.py` — `--file-back`
3. `ingest_raw.py` — no flags
4. `lint.py` — `--structural-only`, `--include-memory`
5. `memory_lint.py` — standalone
6. `flush.py` — not called directly (document why)

### In-Chat Commands
- `!save <text>` — detailed usage, examples
- `/reflect` — what it asks, what it produces
- `/compile` — alias for compile.py

### Decision Tree
```
Want to save something right now?
  → !save <text>

Have uncompiled daily logs?
  → uv run python scripts/compile.py

Found an article or notes to add?
  → Drop in raw/ → uv run python scripts/ingest_raw.py

Want to ask your wiki a question?
  → uv run python scripts/query.py "question"

Wiki feels messy or inconsistent?
  → uv run python scripts/lint.py

End of work session?
  → /reflect (or just close — auto-flush handles it)
```

- [ ] **Step 2: Commit**

```bash
git add docs/commands.md
git commit -m "docs: add commands.md — exhaustive command reference with decision tree"
```

---

## Task 8: docs/how-it-works.md — Deep dive

**Files:**
- Create: `docs/how-it-works.md`

- [ ] **Step 1: Write how-it-works.md**

Structure:

### Overview
One paragraph + pipeline diagram (ASCII art)

### 1. Session Capture Pipeline
Detailed walkthrough:
- SessionEnd/PreCompact hook fires → extracts transcript → writes temp file → spawns flush.py
- flush.py Pass 1 (Extract): sends to Agent SDK, extracts structured sections
- flush.py Pass 2 (Quality Audit): second Agent SDK call, filters junk
- Result written to `daily/YYYY-MM-DD.md`
- Diagram: Hook → Extract → Audit → Daily Log

### 2. Compilation Pipeline
- compile.py reads uncompiled daily logs
- Sends to Agent SDK with AGENTS.md schema + existing wiki
- Agent creates/updates wiki articles
- Updates index.md and log.md
- Diagram: Daily Logs → Compile → Wiki Articles

### 3. External Ingestion
- Drop files in `raw/`
- ingest_raw.py processes them same way as compile
- Moves to `raw/processed/`

### 4. Context Injection
- session_start.py reads index.md + recent daily log
- Outputs JSON → Claude sees it immediately
- Size budget: 20,000 chars max

### 5. Quality Audit (detail)
- Why: 95% of auto-captured content is noise (mem0 experiment)
- How: two-pass LLM — extract then audit
- AUDIT_FLAG mechanism — flagged content stays but gets skipped
- Conservative: when in doubt, keeps content

### 6. Wiki Structure
- Concept articles: atomic knowledge with YAML frontmatter
- Connection articles: cross-concept relationships
- Q&A articles: saved query answers
- Index: master navigation table
- Log: operation changelog

### 7. Health Checks
All 7 lint checks explained with examples of what they catch

### 8. Hooks Lifecycle
- How hooks are configured (global settings.json)
- Recursion guard (CLAUDE_INVOKED_BY)
- Flush dedup (60s window)
- Windows quirks

- [ ] **Step 2: Commit**

```bash
git add docs/how-it-works.md
git commit -m "docs: add how-it-works.md — deep dive into pipeline and architecture"
```

---

## Task 9: docs/cheatsheet.md — English version

**Files:**
- Create: `docs/cheatsheet.md`

- [ ] **Step 1: Translate and update cheatsheet**

Take the existing Russian cheatsheet, translate to English, ensure completeness. Keep it as a quick-reference card format — tables, minimal prose.

- [ ] **Step 2: Commit**

```bash
git add docs/cheatsheet.md
git commit -m "docs: add English cheatsheet"
```

---

## Task 10: Hardcoded paths audit

**Files:**
- Modify: any files with hardcoded paths

- [ ] **Step 1: Search for hardcoded paths**

```bash
cd /c/Users/Voland/Dev/MetaMode-public
grep -rn "Voland\|C:\\\\Users\|/home/" --include="*.py" --include="*.md" --include="*.json"
```

Expected: zero results (config.py uses `Path(__file__).resolve()`, README uses placeholders)

- [ ] **Step 2: Verify README hook paths use placeholder**

Check that all hook configuration examples use `/FULL/PATH/TO/MetaMode` or `~/Dev/MetaMode` placeholder.

- [ ] **Step 3: Commit if any fixes needed**

---

## Task 11: Final review and docs polish

- [ ] **Step 1: Read through all docs end-to-end**

Check for:
- Consistent terminology
- No broken links between docs
- All cross-references work
- No personal data leaked
- Every question from the spec's "must answer" list is covered

- [ ] **Step 2: Verify the "10-minute test"**

Walk through as a new user:
1. README answers "what is this?" ✓
2. README answers "why do I need it?" ✓
3. setup.md gets me running ✓
4. commands.md tells me everything I can do ✓
5. how-it-works.md explains the internals ✓
6. Example content lets me try compile/query immediately ✓

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "docs: final polish — consistency, cross-references, completeness check"
```

---

## Task 12: NotebookLM presentation

- [ ] **Step 1: Invoke NotebookLM skill**

Use `/notebooklm` skill to create a presentation covering:
- What MetaMode is and why it exists
- The problem it solves (Claude forgetting)
- What you get after installation
- How the pipeline works
- All available tools
- Before/after comparison
- $0 cost model

Source material: README.md + docs/*.md from the public repo

- [ ] **Step 2: Save presentation link/output**

---

## Task 13: Publish to GitHub

- [ ] **Step 1: Create GitHub repo**

```bash
cd /c/Users/Voland/Dev/MetaMode-public
gh repo create Voland00009/MetaMode --public --source=. --push
```

- [ ] **Step 2: Verify on GitHub**

```bash
gh repo view Voland00009/MetaMode --web
```

Check: README renders correctly, all files present, no personal data.
