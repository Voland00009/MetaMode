# MetaMode v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fork coleam00/claude-memory-compiler and apply 6 modifications to create a persistent wiki-memory layer for Claude Code, running at $0/mo on Max subscription.

**Architecture:** Clone coleam00 as base, replace Claude Agent SDK calls with `claude -p` subprocess (MOD 1), add `!save` quick-capture hook (MOD 2), `/reflect` skill (MOD 3), pending review workflow (MOD 4), technology categorization (MOD 5), compile reminder (MOD 6), and bonus `/compile` skill. All LLM calls go through CLI headless mode covered by Max subscription.

**Tech Stack:** Python 3.12+, uv package manager, Claude Code CLI (`claude -p`), Obsidian (read-only UI over `knowledge/`), git for versioning.

---

## File Structure

### Files to copy from coleam00 (then modify):

| File | Responsibility | Modifications |
|------|---------------|---------------|
| `hooks/session-start.py` | Inject KB context at session start | MOD 4 (pending review), MOD 6 (compile reminder) |
| `hooks/session-end.py` | Capture transcript, spawn flush | None (as-is) |
| `hooks/pre-compact.py` | Safety net before compaction | None (as-is) |
| `scripts/flush.py` | LLM extraction from transcript | MOD 1 (SDK->CLI), MOD 4 (pending review) |
| `scripts/compile.py` | Daily logs -> wiki articles | MOD 1 (SDK->CLI) |
| `scripts/lint.py` | 7 health checks | MOD 1 (SDK->CLI) |
| `scripts/query.py` | KB queries + Q&A filing | MOD 1 (SDK->CLI) |
| `scripts/config.py` | Path constants | Timezone fix |
| `scripts/utils.py` | Shared helpers | None (as-is) |
| `AGENTS.md` | KB schema | MOD 5 (categorization) |
| `pyproject.toml` | Dependencies | Remove claude-agent-sdk |
| `.gitignore` | Ignores | As-is |

### Files to create (new):

| File | Responsibility |
|------|---------------|
| `scripts/claude_cli.py` | Shared helper: subprocess wrapper for `claude -p` |
| `hooks/user-prompt-submit.py` | MOD 2: `!save` interceptor |
| `.claude/skills/reflect/SKILL.md` | MOD 3: `/reflect` skill |
| `.claude/skills/compile/SKILL.md` | BONUS: `/compile` skill |

### Directories to create:

```
MetaMode/
  daily/                  # auto-created by flush.py
  knowledge/
    index.md              # auto-created by compile.py
    log.md                # auto-created by compile.py  
    concepts/
    connections/
    qa/
  reports/                # auto-created by lint.py
  hooks/
  scripts/
  .claude/
    settings.json         # hooks config (project-level)
    skills/
      reflect/SKILL.md
      compile/SKILL.md
```

### Dependency graph:

```
Task 1 (Base setup)
  └─> Task 2 (claude_cli.py helper)
        ├─> Task 3 (flush.py MOD 1)
        ├─> Task 4 (compile.py MOD 1)
        └─> Task 5 (lint.py + query.py MOD 1)
  └─> Task 6 (!save hook, MOD 2) — independent of MOD 1
  └─> Task 7 (AGENTS.md categorization, MOD 5) — independent
  └─> Task 8 (session-start.py: MOD 4 + MOD 6) — after Task 3
  └─> Task 9 (skills: /reflect + /compile) — after Task 4
```

---

## Task 1: Base Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `scripts/config.py`
- Create: `scripts/utils.py`
- Create: `hooks/session-end.py`
- Create: `hooks/pre-compact.py`
- Create: `knowledge/index.md`, `knowledge/log.md`
- Create: `.claude/settings.json`
- Create: `.gitignore` (update existing)

This task copies the coleam00 base and adapts it to MetaMode's directory structure. No SDK code yet — that comes in Tasks 2-5.

- [ ] **Step 1: Initialize project with uv**

```bash
cd c:/Users/Voland/Dev/MetaMode
uv init --no-readme
```

Expected: creates `pyproject.toml` if not present.

- [ ] **Step 2: Write pyproject.toml**

```toml
[project]
name = "metamode"
version = "0.1.0"
description = "Persistent wiki-memory layer for Claude Code — fork of coleam00/claude-memory-compiler"
requires-python = ">=3.12"
dependencies = [
    "tzdata>=2024.1",
]

[tool.ruff]
line-length = 100
```

Key difference from coleam00: **no `claude-agent-sdk`** dependency. We use `claude -p` CLI instead.
No `python-dotenv` either — we don't need .env files since there are no API keys.

- [ ] **Step 3: Run uv sync to create venv and lockfile**

```bash
uv sync
```

Expected: creates `.venv/`, `uv.lock`.

- [ ] **Step 4: Write scripts/config.py**

```python
"""Path constants and configuration for MetaMode knowledge base."""

from pathlib import Path
from datetime import datetime, timezone

# -- Paths --
ROOT_DIR = Path(__file__).resolve().parent.parent
DAILY_DIR = ROOT_DIR / "daily"
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
CONCEPTS_DIR = KNOWLEDGE_DIR / "concepts"
CONNECTIONS_DIR = KNOWLEDGE_DIR / "connections"
QA_DIR = KNOWLEDGE_DIR / "qa"
REPORTS_DIR = ROOT_DIR / "reports"
SCRIPTS_DIR = ROOT_DIR / "scripts"
HOOKS_DIR = ROOT_DIR / "hooks"
AGENTS_FILE = ROOT_DIR / "AGENTS.md"

INDEX_FILE = KNOWLEDGE_DIR / "index.md"
LOG_FILE = KNOWLEDGE_DIR / "log.md"
STATE_FILE = SCRIPTS_DIR / "state.json"


def now_iso() -> str:
    """Current time in ISO 8601 format, local timezone."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def today_iso() -> str:
    """Current date as YYYY-MM-DD."""
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
```

Note: removed hardcoded `TIMEZONE = "America/Chicago"` — we use system local timezone via `.astimezone()` (no argument = system tz). This works on Windows without `tzdata` for the basic case, but `tzdata` is kept as a dependency for edge cases.

- [ ] **Step 5: Write scripts/utils.py**

Copy verbatim from coleam00 (see fetched code above). No modifications needed — it's pure file operations with no SDK dependency.

```python
"""Shared utilities for MetaMode knowledge base."""

import hashlib
import json
import re
from pathlib import Path

from config import (
    CONCEPTS_DIR,
    CONNECTIONS_DIR,
    DAILY_DIR,
    INDEX_FILE,
    KNOWLEDGE_DIR,
    QA_DIR,
    STATE_FILE,
)


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"ingested": {}, "query_count": 0, "last_lint": None, "total_cost": 0.0}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def extract_wikilinks(content: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def wiki_article_exists(link: str) -> bool:
    path = KNOWLEDGE_DIR / f"{link}.md"
    return path.exists()


def read_wiki_index() -> str:
    if INDEX_FILE.exists():
        return INDEX_FILE.read_text(encoding="utf-8")
    return "# Knowledge Base Index\n\n| Article | Summary | Compiled From | Updated |\n|---------|---------|---------------|---------|"


def read_all_wiki_content() -> str:
    parts = [f"## INDEX\n\n{read_wiki_index()}"]
    for subdir in [CONCEPTS_DIR, CONNECTIONS_DIR, QA_DIR]:
        if not subdir.exists():
            continue
        for md_file in sorted(subdir.glob("*.md")):
            rel = md_file.relative_to(KNOWLEDGE_DIR)
            content = md_file.read_text(encoding="utf-8")
            parts.append(f"## {rel}\n\n{content}")
    return "\n\n---\n\n".join(parts)


def list_wiki_articles() -> list[Path]:
    articles = []
    for subdir in [CONCEPTS_DIR, CONNECTIONS_DIR, QA_DIR]:
        if subdir.exists():
            articles.extend(sorted(subdir.glob("*.md")))
    return articles


def list_raw_files() -> list[Path]:
    if not DAILY_DIR.exists():
        return []
    return sorted(DAILY_DIR.glob("*.md"))


def count_inbound_links(target: str, exclude_file: Path | None = None) -> int:
    count = 0
    for article in list_wiki_articles():
        if article == exclude_file:
            continue
        content = article.read_text(encoding="utf-8")
        if f"[[{target}]]" in content:
            count += 1
    return count


def get_article_word_count(path: Path) -> int:
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:]
    return len(content.split())


def build_index_entry(rel_path: str, summary: str, sources: str, updated: str) -> str:
    link = rel_path.replace(".md", "")
    return f"| [[{link}]] | {summary} | {sources} | {updated} |"
```

- [ ] **Step 6: Write hooks/session-end.py**

Copy verbatim from coleam00. No modifications — it does no SDK calls, only local I/O and spawns flush.py.

(Full code as fetched above — copy exactly.)

- [ ] **Step 7: Write hooks/pre-compact.py**

Copy verbatim from coleam00. Same reasoning — pure local I/O.

(Full code as fetched above — copy exactly.)

- [ ] **Step 8: Create directory structure**

```bash
mkdir -p knowledge/concepts knowledge/connections knowledge/qa daily reports
```

- [ ] **Step 9: Create seed files**

`knowledge/index.md`:
```markdown
# Knowledge Base Index

| Article | Summary | Compiled From | Updated |
|---------|---------|---------------|---------|
```

`knowledge/log.md`:
```markdown
# Build Log
```

- [ ] **Step 10: Write .claude/settings.json (project-level hooks config)**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory \"%CWD%\" python hooks/session-start.py",
            "timeout": 15
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory \"%CWD%\" python hooks/session-end.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory \"%CWD%\" python hooks/pre-compact.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Important:** This is `.claude/settings.json` (project-level, checked into repo). It merges with the existing `.claude/settings.local.json` (user-level, gitignored permissions). The `%CWD%` placeholder — need to verify if CC expands this. Alternative: use relative paths like coleam00 does (`uv run python hooks/session-start.py`), which works because CC runs hooks from project root.

Simpler approach (coleam00 pattern):
```json
{
  "hooks": {
    "SessionStart": [{"matcher": "", "hooks": [{"type": "command", "command": "uv run python hooks/session-start.py", "timeout": 15}]}],
    "SessionEnd": [{"matcher": "", "hooks": [{"type": "command", "command": "uv run python hooks/session-end.py", "timeout": 10}]}],
    "PreCompact": [{"matcher": "", "hooks": [{"type": "command", "command": "uv run python hooks/pre-compact.py", "timeout": 10}]}]
  }
}
```

- [ ] **Step 11: Update .gitignore**

```gitignore
# Python
.venv/
__pycache__/
*.pyc

# Runtime state (regenerated automatically)
scripts/state.json
scripts/last-flush.json
scripts/flush.log
scripts/compile.log
scripts/session-flush-*.md
scripts/flush-context-*.md

# Reports (generated by lint)
reports/

# OS
.DS_Store
Thumbs.db

# Claude Code local settings
.claude/settings.local.json
```

- [ ] **Step 12: Initialize git repo and commit base**

```bash
git init
git add pyproject.toml uv.lock scripts/config.py scripts/utils.py hooks/session-end.py hooks/pre-compact.py knowledge/index.md knowledge/log.md .claude/settings.json .gitignore AGENTS.md CLAUDE.md
git commit -m "feat: base project setup — fork of coleam00/claude-memory-compiler

Copied core structure: config, utils, session-end/pre-compact hooks.
Removed claude-agent-sdk dependency (will use claude -p CLI instead).
Adapted timezone to system local (was hardcoded America/Chicago)."
```

---

## Task 2: MOD 1 — CLI Helper Module (`claude_cli.py`)

**Files:**
- Create: `scripts/claude_cli.py`
- Test: `tests/test_claude_cli.py`

This is the shared module that replaces all `claude_agent_sdk.query()` calls. Every script that previously used the SDK will import from here instead.

**Design rationale:** coleam00 uses the SDK's async streaming `query()` in 4 files. Instead of duplicating subprocess logic in each, we create one helper that all 4 scripts share. The helper wraps `claude -p` with proper flags, error handling, and Windows compatibility.

- [ ] **Step 1: Write the failing test for `run_claude_prompt`**

Create `tests/__init__.py` (empty) and `tests/test_claude_cli.py`:

```python
"""Tests for claude_cli.py — the SDK-to-CLI replacement."""

import json
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from claude_cli import run_claude_prompt


def test_run_claude_prompt_returns_text():
    """run_claude_prompt should return the text result from claude -p."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({
        "result": [{"type": "text", "text": "Hello from Claude"}],
        "session_id": "test-123",
        "is_error": False
    })

    with patch("claude_cli.subprocess.run", return_value=mock_result) as mock_run:
        result = run_claude_prompt("Say hello")
        assert result == "Hello from Claude"
        mock_run.assert_called_once()
        args = mock_run.call_args
        cmd = args[0][0]
        assert "claude" in cmd[0]
        assert "-p" in cmd


def test_run_claude_prompt_with_tools():
    """run_claude_prompt should pass --allowedTools when tools are specified."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({
        "result": [{"type": "text", "text": "Done"}],
        "is_error": False
    })

    with patch("claude_cli.subprocess.run", return_value=mock_result):
        run_claude_prompt("Compile", tools=["Read", "Write", "Edit"])

    call_args = subprocess.run.call_args  # won't work — use the mock
    # Re-check with the mock:
    with patch("claude_cli.subprocess.run", return_value=mock_result) as mock_run:
        run_claude_prompt("Compile", tools=["Read", "Write", "Edit"])
        cmd = mock_run.call_args[0][0]
        assert "--allowedTools" in cmd


def test_run_claude_prompt_error_handling():
    """run_claude_prompt should raise on non-zero exit code."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Error: something went wrong"

    with patch("claude_cli.subprocess.run", return_value=mock_result):
        try:
            run_claude_prompt("Bad prompt")
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "something went wrong" in str(e)


def test_run_claude_prompt_timeout():
    """run_claude_prompt should handle subprocess timeout."""
    with patch("claude_cli.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=300)):
        try:
            run_claude_prompt("Slow prompt", timeout=300)
            assert False, "Should have raised"
        except subprocess.TimeoutExpired:
            pass


def test_run_claude_prompt_with_system_prompt_file(tmp_path):
    """run_claude_prompt should pass --system-prompt-file when specified."""
    prompt_file = tmp_path / "system.md"
    prompt_file.write_text("You are a compiler.")

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({
        "result": [{"type": "text", "text": "Compiled"}],
        "is_error": False
    })

    with patch("claude_cli.subprocess.run", return_value=mock_result) as mock_run:
        run_claude_prompt("Compile this", system_prompt_file=prompt_file)
        cmd = mock_run.call_args[0][0]
        assert "--system-prompt-file" in cmd
        idx = cmd.index("--system-prompt-file")
        assert cmd[idx + 1] == str(prompt_file)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd c:/Users/Voland/Dev/MetaMode
uv run python -m pytest tests/test_claude_cli.py -v
```

Expected: `ModuleNotFoundError: No module named 'claude_cli'`

- [ ] **Step 3: Write scripts/claude_cli.py**

```python
"""Shared helper: run Claude CLI headless (claude -p) as subprocess.

Replaces all claude_agent_sdk.query() calls in the coleam00 codebase.
Uses `claude -p` which is covered by Max subscription ($0/mo).

Usage:
    from claude_cli import run_claude_prompt

    result = run_claude_prompt(
        prompt="Extract knowledge from this text...",
        max_turns=2,
        tools=[],  # no tools = text-only response
    )
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# Recursion guard: inherit from parent process
RECURSION_ENV_VAR = "CLAUDE_INVOKED_BY"


def run_claude_prompt(
    prompt: str,
    *,
    max_turns: int = 2,
    tools: list[str] | None = None,
    permission_mode: str | None = None,
    system_prompt_file: Path | None = None,
    cwd: Path | str | None = None,
    timeout: int = 300,
) -> str:
    """Run a prompt through `claude -p` and return the text result.

    Args:
        prompt: The prompt text to send.
        max_turns: Maximum agentic turns (default 2 for simple extraction).
        tools: List of allowed tools (e.g., ["Read", "Write"]). None = no tools.
        permission_mode: "acceptEdits" or "bypassPermissions". None = default.
        system_prompt_file: Path to a file with system prompt.
        cwd: Working directory for claude process. Defaults to project root.
        timeout: Timeout in seconds (default 300 = 5 min).

    Returns:
        The text content from Claude's response.

    Raises:
        RuntimeError: If claude exits with non-zero code or returns an error.
        subprocess.TimeoutExpired: If the process exceeds timeout.
    """
    cmd = [
        "claude",
        "-p",
        "--output-format", "json",
        "--max-turns", str(max_turns),
        "--no-session-persistence",
    ]

    if tools is not None:
        for tool in tools:
            cmd.extend(["--allowedTools", tool])

    if permission_mode:
        cmd.extend(["--permission-mode", permission_mode])

    if system_prompt_file:
        cmd.extend(["--system-prompt-file", str(system_prompt_file)])

    cmd.append(prompt)

    kwargs: dict = {
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "timeout": timeout,
        "cwd": str(cwd or ROOT_DIR),
    }

    # Windows: prevent console flash
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    result = subprocess.run(cmd, **kwargs)

    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (exit {result.returncode}): {result.stderr.strip()}"
        )

    # Parse JSON output
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        # Fallback: maybe it returned raw text
        return result.stdout.strip()

    # Check for error flag
    if data.get("is_error"):
        raise RuntimeError(f"claude -p returned error: {data}")

    # Extract text from result blocks
    result_blocks = data.get("result", [])
    text_parts = []
    for block in result_blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(block.get("text", ""))
        elif isinstance(block, str):
            text_parts.append(block)

    return "\n".join(text_parts)
```

**Key design decisions:**
- `--output-format json` — structured output, parseable.
- `--no-session-persistence` — don't create a saved session for background tasks.
- `--max-turns` defaults to 2 for simple text extraction (flush), can be set to 30 for compile.
- Windows `CREATE_NO_WINDOW` — same pattern as coleam00.
- Returns only text content, not the full JSON — callers get a simple string.

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run python -m pytest tests/test_claude_cli.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/claude_cli.py tests/test_claude_cli.py tests/__init__.py
git commit -m "feat: add claude_cli.py — subprocess wrapper replacing Agent SDK

All LLM calls go through claude -p (Max subscription, $0/mo).
Supports: tools, permission_mode, system_prompt_file, timeout.
Windows CREATE_NO_WINDOW for background use."
```

---

## Task 3: MOD 1 — Migrate flush.py (SDK -> CLI)

**Files:**
- Create: `scripts/flush.py`
- Test: `tests/test_flush.py`

This is the most critical migration — flush.py runs after every session. The original uses `claude_agent_sdk.query()` with `allowed_tools=[]` and `max_turns=2`. Our replacement uses `run_claude_prompt()` with the same constraints.

- [ ] **Step 1: Write the failing test for flush extraction**

```python
"""Tests for flush.py — knowledge extraction from conversation context."""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import config


def test_append_to_daily_log_creates_file(tmp_path):
    """append_to_daily_log should create daily log file if missing."""
    with patch.object(config, "DAILY_DIR", tmp_path):
        from flush import append_to_daily_log
        append_to_daily_log("Test content", "Test Section")

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / f"{today}.md"
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Test content" in content
    assert "Test Section" in content


def test_append_to_daily_log_appends(tmp_path):
    """append_to_daily_log should append to existing file."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / f"{today}.md"
    log_file.write_text("# Existing\n\n", encoding="utf-8")

    with patch.object(config, "DAILY_DIR", tmp_path):
        from flush import append_to_daily_log
        append_to_daily_log("New entry", "Session")

    content = log_file.read_text(encoding="utf-8")
    assert "# Existing" in content
    assert "New entry" in content


def test_dedup_skips_recent_flush(tmp_path):
    """Flush should skip if same session was flushed within 60 seconds."""
    import time
    state_file = tmp_path / "last-flush.json"
    state_file.write_text(json.dumps({
        "session_id": "test-session",
        "timestamp": time.time()  # just now
    }), encoding="utf-8")

    with patch("flush.STATE_FILE", state_file):
        from flush import load_flush_state
        state = load_flush_state()
        assert state["session_id"] == "test-session"
        assert time.time() - state["timestamp"] < 60
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m pytest tests/test_flush.py -v
```

Expected: FAIL (module not found).

- [ ] **Step 3: Write scripts/flush.py (migrated)**

```python
"""Memory flush — extracts knowledge from conversation context via claude -p.

Spawned by session-end.py or pre-compact.py as a background process.

Usage:
    uv run python flush.py <context_file.md> <session_id>
"""

from __future__ import annotations

import os
os.environ["CLAUDE_INVOKED_BY"] = "memory_flush"

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = ROOT / "daily"
SCRIPTS_DIR = ROOT / "scripts"
STATE_FILE = SCRIPTS_DIR / "last-flush.json"
LOG_FILE = SCRIPTS_DIR / "flush.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def load_flush_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_flush_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state), encoding="utf-8")


def append_to_daily_log(content: str, section: str = "Session") -> None:
    today = datetime.now(timezone.utc).astimezone()
    log_path = DAILY_DIR / f"{today.strftime('%Y-%m-%d')}.md"

    if not log_path.exists():
        DAILY_DIR.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"# Daily Log: {today.strftime('%Y-%m-%d')}\n\n## Sessions\n\n## Memory Maintenance\n\n",
            encoding="utf-8",
        )

    time_str = today.strftime("%H:%M")
    entry = f"### {section} ({time_str})\n\n{content}\n\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


def run_flush(context: str) -> str:
    """Use claude -p to extract knowledge from conversation context."""
    from claude_cli import run_claude_prompt

    prompt = f"""Review the conversation context below and respond with a concise summary
of important items that should be preserved in the daily log.
Do NOT use any tools - just return plain text.

Format your response as a structured daily log entry with these sections:

**Context:** [One line about what the user was working on]

**Key Exchanges:**
- [Important Q&A or discussions]

**Decisions Made:**
- [Any decisions with rationale]

**Lessons Learned:**
- [Gotchas, patterns, or insights discovered]

**Action Items:**
- [Follow-ups or TODOs mentioned]

Skip anything that is:
- Routine tool calls or file reads
- Content that's trivial or obvious
- Trivial back-and-forth or clarification exchanges

Only include sections that have actual content. If nothing is worth saving,
respond with exactly: FLUSH_OK

## Conversation Context

{context}"""

    try:
        response = run_claude_prompt(prompt, max_turns=2, tools=[])
    except Exception as e:
        import traceback
        logging.error("claude -p error: %s\n%s", e, traceback.format_exc())
        response = f"FLUSH_ERROR: {type(e).__name__}: {e}"

    return response


COMPILE_AFTER_HOUR = 18
PENDING_REVIEW_FILE = SCRIPTS_DIR / "pending-review.md"


def maybe_trigger_compilation() -> None:
    """If past compile hour and today's log changed, spawn compile.py."""
    import subprocess as _sp

    now = datetime.now(timezone.utc).astimezone()
    if now.hour < COMPILE_AFTER_HOUR:
        return

    today_log = f"{now.strftime('%Y-%m-%d')}.md"
    compile_state_file = SCRIPTS_DIR / "state.json"
    if compile_state_file.exists():
        try:
            compile_state = json.loads(compile_state_file.read_text(encoding="utf-8"))
            ingested = compile_state.get("ingested", {})
            if today_log in ingested:
                from hashlib import sha256
                log_path = DAILY_DIR / today_log
                if log_path.exists():
                    current_hash = sha256(log_path.read_bytes()).hexdigest()[:16]
                    if ingested[today_log].get("hash") == current_hash:
                        return
        except (json.JSONDecodeError, OSError):
            pass

    compile_script = SCRIPTS_DIR / "compile.py"
    if not compile_script.exists():
        return

    logging.info("End-of-day compilation triggered (after %d:00)", COMPILE_AFTER_HOUR)

    cmd = ["uv", "run", "--directory", str(ROOT), "python", str(compile_script)]

    kwargs: dict = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = _sp.CREATE_NO_WINDOW
    else:
        kwargs["start_new_session"] = True

    try:
        log_handle = open(str(SCRIPTS_DIR / "compile.log"), "a")
        _sp.Popen(cmd, stdout=log_handle, stderr=_sp.STDOUT, cwd=str(ROOT), **kwargs)
    except Exception as e:
        logging.error("Failed to spawn compile.py: %s", e)


def write_pending_review(content: str, session_id: str) -> None:
    """MOD 4: Write extracted content to pending-review.md for human approval.

    Instead of auto-appending to daily log, write to a staging file.
    Session-start hook will show this for approve/reject.
    """
    timestamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    entry = f"""---
session_id: {session_id}
timestamp: {timestamp}
status: pending
---

{content}

---
"""
    # Append (multiple sessions may produce pending items)
    with open(PENDING_REVIEW_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


def main():
    if len(sys.argv) < 3:
        logging.error("Usage: %s <context_file.md> <session_id>", sys.argv[0])
        sys.exit(1)

    context_file = Path(sys.argv[1])
    session_id = sys.argv[2]

    logging.info("flush.py started for session %s, context: %s", session_id, context_file)

    if not context_file.exists():
        logging.error("Context file not found: %s", context_file)
        return

    # Dedup: skip if same session flushed within 60 seconds
    state = load_flush_state()
    if (
        state.get("session_id") == session_id
        and time.time() - state.get("timestamp", 0) < 60
    ):
        logging.info("Skipping duplicate flush for session %s", session_id)
        context_file.unlink(missing_ok=True)
        return

    context = context_file.read_text(encoding="utf-8").strip()
    if not context:
        logging.info("Context file is empty, skipping")
        context_file.unlink(missing_ok=True)
        return

    logging.info("Flushing session %s: %d chars", session_id, len(context))

    response = run_flush(context)

    # MOD 4: Write to pending review instead of directly to daily log
    if "FLUSH_OK" in response:
        logging.info("Result: FLUSH_OK")
        append_to_daily_log("FLUSH_OK - Nothing worth saving from this session", "Memory Flush")
    elif "FLUSH_ERROR" in response:
        logging.error("Result: %s", response)
        append_to_daily_log(response, "Memory Flush")
    else:
        logging.info("Result: pending review (%d chars)", len(response))
        write_pending_review(response, session_id)

    save_flush_state({"session_id": session_id, "timestamp": time.time()})
    context_file.unlink(missing_ok=True)
    maybe_trigger_compilation()
    logging.info("Flush complete for session %s", session_id)


if __name__ == "__main__":
    main()
```

**Changes from coleam00:**
1. `run_flush()`: replaced `async` SDK `query()` with synchronous `run_claude_prompt()` from `claude_cli.py`
2. `write_pending_review()`: new function (MOD 4) — writes to staging file instead of auto-appending
3. In `main()`: non-FLUSH_OK results go to `write_pending_review()` instead of `append_to_daily_log()`
4. Removed `asyncio.run()` — no longer async
5. `maybe_trigger_compilation()`: changed Windows flags from `CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS` to `CREATE_NO_WINDOW` (consistent with session-end.py pattern, avoids SDK I/O issues)

- [ ] **Step 4: Run tests**

```bash
uv run python -m pytest tests/test_flush.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/flush.py tests/test_flush.py
git commit -m "feat: flush.py — SDK->CLI migration + pending review (MOD 1+4)

Replaced claude_agent_sdk.query() with claude_cli.run_claude_prompt().
Added write_pending_review() for human-in-the-loop approval.
Non-trivial extractions go to pending-review.md instead of auto-appending."
```

---

## Task 4: MOD 1 — Migrate compile.py (SDK -> CLI)

**Files:**
- Create: `scripts/compile.py`
- Test: `tests/test_compile.py`

compile.py is the most complex script — it gives Claude full tool access (Read, Write, Edit, Glob, Grep) with `permission_mode="acceptEdits"` and `max_turns=30`. The CLI equivalent uses `--permission-mode acceptEdits --allowedTools Read Write Edit Glob Grep --max-turns 30`.

- [ ] **Step 1: Write the failing test**

```python
"""Tests for compile.py — daily log to wiki article compilation."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_compile_determines_files_to_compile(tmp_path):
    """compile should identify new/changed daily logs for compilation."""
    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()
    (daily_dir / "2026-04-10.md").write_text("# Session 1\nContent here", encoding="utf-8")
    (daily_dir / "2026-04-11.md").write_text("# Session 2\nMore content", encoding="utf-8")

    import config
    with patch.object(config, "DAILY_DIR", daily_dir), \
         patch.object(config, "STATE_FILE", tmp_path / "state.json"):
        from utils import list_raw_files, load_state, file_hash
        files = list_raw_files()
        assert len(files) == 2

        # With empty state, all files need compilation
        state = load_state()
        to_compile = []
        for log_path in files:
            rel = log_path.name
            prev = state.get("ingested", {}).get(rel, {})
            if not prev or prev.get("hash") != file_hash(log_path):
                to_compile.append(log_path)
        assert len(to_compile) == 2


def test_compile_skips_unchanged(tmp_path):
    """compile should skip daily logs with unchanged hash."""
    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()
    log_file = daily_dir / "2026-04-10.md"
    log_file.write_text("# Session 1\nContent", encoding="utf-8")

    import config
    from utils import file_hash

    state = {
        "ingested": {
            "2026-04-10.md": {"hash": file_hash(log_file), "compiled_at": "now"}
        }
    }

    with patch.object(config, "DAILY_DIR", daily_dir):
        from utils import list_raw_files
        files = list_raw_files()
        to_compile = []
        for log_path in files:
            rel = log_path.name
            prev = state.get("ingested", {}).get(rel, {})
            if not prev or prev.get("hash") != file_hash(log_path):
                to_compile.append(log_path)
        assert len(to_compile) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m pytest tests/test_compile.py -v
```

Expected: FAIL (compile module issues or import errors — config patching may need adjustment).

- [ ] **Step 3: Write scripts/compile.py**

```python
"""Compile daily conversation logs into structured knowledge articles.

Usage:
    uv run python compile.py
    uv run python compile.py --all
    uv run python compile.py --file daily/2026-04-01.md
    uv run python compile.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import AGENTS_FILE, CONCEPTS_DIR, CONNECTIONS_DIR, DAILY_DIR, KNOWLEDGE_DIR, now_iso
from utils import (
    file_hash,
    list_raw_files,
    list_wiki_articles,
    load_state,
    read_wiki_index,
    save_state,
)
from claude_cli import run_claude_prompt

ROOT_DIR = Path(__file__).resolve().parent.parent


def compile_daily_log(log_path: Path, state: dict) -> None:
    """Compile a single daily log into knowledge articles."""
    log_content = log_path.read_text(encoding="utf-8")
    schema = AGENTS_FILE.read_text(encoding="utf-8")
    wiki_index = read_wiki_index()

    existing_articles_context = ""
    existing = {}
    for article_path in list_wiki_articles():
        rel = article_path.relative_to(KNOWLEDGE_DIR)
        existing[str(rel)] = article_path.read_text(encoding="utf-8")

    if existing:
        parts = []
        for rel_path, content in existing.items():
            parts.append(f"### {rel_path}\n```markdown\n{content}\n```")
        existing_articles_context = "\n\n".join(parts)

    timestamp = now_iso()

    prompt = f"""You are a knowledge compiler. Your job is to read a daily conversation log
and extract knowledge into structured wiki articles.

## Schema (AGENTS.md)

{schema}

## Current Wiki Index

{wiki_index}

## Existing Wiki Articles

{existing_articles_context if existing_articles_context else "(No existing articles yet)"}

## Daily Log to Compile

**File:** {log_path.name}

{log_content}

## Your Task

Read the daily log above and compile it into wiki articles following the schema exactly.

### Rules:

1. **Extract key concepts** - Identify 3-7 distinct concepts worth their own article
2. **Create concept articles** in `knowledge/concepts/` - One .md file per concept
   - Use the exact article format from AGENTS.md (YAML frontmatter + sections)
   - Include `sources:` in frontmatter pointing to the daily log file
   - Use `[[concepts/slug]]` wikilinks to link to related concepts
   - Write in encyclopedia style - neutral, comprehensive
3. **Create connection articles** in `knowledge/connections/` if this log reveals non-obvious
   relationships between 2+ existing concepts
4. **Update existing articles** if this log adds new information to concepts already in the wiki
   - Read the existing article, add the new information, add the source to frontmatter
5. **Update knowledge/index.md** - Add new entries to the table
   - Each entry: `| [[path/slug]] | One-line summary | source-file | {timestamp[:10]} |`
6. **Append to knowledge/log.md** - Add a timestamped entry:
   ```
   ## [{timestamp}] compile | {log_path.name}
   - Source: daily/{log_path.name}
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
- Sources section should cite the daily log with specific claims extracted
"""

    try:
        run_claude_prompt(
            prompt,
            max_turns=30,
            tools=["Read", "Write", "Edit", "Glob", "Grep"],
            permission_mode="acceptEdits",
            timeout=600,  # 10 min — compile can be slow with many articles
        )
    except Exception as e:
        print(f"  Error: {e}")
        return

    # Update state
    rel_path = log_path.name
    state.setdefault("ingested", {})[rel_path] = {
        "hash": file_hash(log_path),
        "compiled_at": now_iso(),
    }
    save_state(state)


def main():
    parser = argparse.ArgumentParser(description="Compile daily logs into knowledge articles")
    parser.add_argument("--all", action="store_true", help="Force recompile all logs")
    parser.add_argument("--file", type=str, help="Compile a specific daily log file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be compiled")
    args = parser.parse_args()

    state = load_state()

    if args.file:
        target = Path(args.file)
        if not target.is_absolute():
            target = DAILY_DIR / target.name
        if not target.exists():
            target = ROOT_DIR / args.file
        if not target.exists():
            print(f"Error: {args.file} not found")
            sys.exit(1)
        to_compile = [target]
    else:
        all_logs = list_raw_files()
        if args.all:
            to_compile = all_logs
        else:
            to_compile = []
            for log_path in all_logs:
                rel = log_path.name
                prev = state.get("ingested", {}).get(rel, {})
                if not prev or prev.get("hash") != file_hash(log_path):
                    to_compile.append(log_path)

    if not to_compile:
        print("Nothing to compile - all daily logs are up to date.")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Files to compile ({len(to_compile)}):")
    for f in to_compile:
        print(f"  - {f.name}")

    if args.dry_run:
        return

    for i, log_path in enumerate(to_compile, 1):
        print(f"\n[{i}/{len(to_compile)}] Compiling {log_path.name}...")
        compile_daily_log(log_path, state)
        print(f"  Done.")

    articles = list_wiki_articles()
    print(f"\nCompilation complete.")
    print(f"Knowledge base: {len(articles)} articles")


if __name__ == "__main__":
    main()
```

**Changes from coleam00:**
1. Replaced `async` SDK `query()` with synchronous `run_claude_prompt()` 
2. Removed `asyncio.run()` — no longer async
3. Removed cost tracking (`message.total_cost_usd`) — CLI doesn't report cost (Max subscription, $0 anyway)
4. `timeout=600` (10 min) — compile with many articles can be slow
5. `compile_daily_log` returns `None` instead of `float` (no cost to track)

- [ ] **Step 4: Run tests**

```bash
uv run python -m pytest tests/test_compile.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/compile.py tests/test_compile.py
git commit -m "feat: compile.py — SDK->CLI migration (MOD 1)

Replaced claude_agent_sdk with claude_cli.run_claude_prompt().
Uses --permission-mode acceptEdits --max-turns 30 for full tool access.
Removed cost tracking (irrelevant on Max subscription)."
```

---

## Task 5: MOD 1 — Migrate lint.py + query.py (SDK -> CLI)

**Files:**
- Create: `scripts/lint.py`
- Create: `scripts/query.py`
- Test: `tests/test_lint.py`

lint.py has 6 structural checks (pure Python, no changes needed) and 1 LLM check (contradictions). Only the LLM check needs migration. query.py is similar — one LLM call.

- [ ] **Step 1: Write the failing test for structural lint checks**

```python
"""Tests for lint.py — knowledge base health checks."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_check_broken_links(tmp_path):
    """Should detect wikilinks pointing to non-existent articles."""
    knowledge_dir = tmp_path / "knowledge"
    concepts_dir = knowledge_dir / "concepts"
    concepts_dir.mkdir(parents=True)

    # Article with a broken link
    (concepts_dir / "real-article.md").write_text(
        "---\ntitle: Real\n---\nSee [[concepts/nonexistent]]",
        encoding="utf-8",
    )

    import config
    from unittest.mock import patch

    with patch.object(config, "KNOWLEDGE_DIR", knowledge_dir), \
         patch.object(config, "CONCEPTS_DIR", concepts_dir), \
         patch.object(config, "CONNECTIONS_DIR", knowledge_dir / "connections"), \
         patch.object(config, "QA_DIR", knowledge_dir / "qa"):
        from lint import check_broken_links
        issues = check_broken_links()
        assert len(issues) == 1
        assert issues[0]["check"] == "broken_link"
        assert "nonexistent" in issues[0]["detail"]


def test_check_sparse_articles(tmp_path):
    """Should detect articles with fewer than 200 words."""
    knowledge_dir = tmp_path / "knowledge"
    concepts_dir = knowledge_dir / "concepts"
    concepts_dir.mkdir(parents=True)

    (concepts_dir / "short.md").write_text(
        "---\ntitle: Short\n---\nJust a few words here.",
        encoding="utf-8",
    )

    import config
    from unittest.mock import patch

    with patch.object(config, "KNOWLEDGE_DIR", knowledge_dir), \
         patch.object(config, "CONCEPTS_DIR", concepts_dir), \
         patch.object(config, "CONNECTIONS_DIR", knowledge_dir / "connections"), \
         patch.object(config, "QA_DIR", knowledge_dir / "qa"):
        from lint import check_sparse_articles
        issues = check_sparse_articles()
        assert len(issues) == 1
        assert issues[0]["check"] == "sparse_article"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m pytest tests/test_lint.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write scripts/lint.py**

Same as coleam00 except `check_contradictions()` uses `run_claude_prompt()` instead of SDK:

```python
"""Lint the knowledge base for structural and semantic health.

Usage:
    uv run python lint.py
    uv run python lint.py --structural-only
"""

from __future__ import annotations

import argparse
from pathlib import Path

from config import KNOWLEDGE_DIR, REPORTS_DIR, now_iso, today_iso
from utils import (
    count_inbound_links,
    extract_wikilinks,
    file_hash,
    get_article_word_count,
    list_raw_files,
    list_wiki_articles,
    load_state,
    read_all_wiki_content,
    save_state,
    wiki_article_exists,
)

ROOT_DIR = Path(__file__).resolve().parent.parent


def check_broken_links() -> list[dict]:
    issues = []
    for article in list_wiki_articles():
        content = article.read_text(encoding="utf-8")
        rel = article.relative_to(KNOWLEDGE_DIR)
        for link in extract_wikilinks(content):
            if link.startswith("daily/"):
                continue
            if not wiki_article_exists(link):
                issues.append({
                    "severity": "error",
                    "check": "broken_link",
                    "file": str(rel),
                    "detail": f"Broken link: [[{link}]] - target does not exist",
                })
    return issues


def check_orphan_pages() -> list[dict]:
    issues = []
    for article in list_wiki_articles():
        rel = article.relative_to(KNOWLEDGE_DIR)
        link_target = str(rel).replace(".md", "").replace("\\", "/")
        inbound = count_inbound_links(link_target)
        if inbound == 0:
            issues.append({
                "severity": "warning",
                "check": "orphan_page",
                "file": str(rel),
                "detail": f"Orphan page: no other articles link to [[{link_target}]]",
            })
    return issues


def check_orphan_sources() -> list[dict]:
    state = load_state()
    ingested = state.get("ingested", {})
    issues = []
    for log_path in list_raw_files():
        if log_path.name not in ingested:
            issues.append({
                "severity": "warning",
                "check": "orphan_source",
                "file": f"daily/{log_path.name}",
                "detail": f"Uncompiled daily log: {log_path.name} has not been ingested",
            })
    return issues


def check_stale_articles() -> list[dict]:
    state = load_state()
    ingested = state.get("ingested", {})
    issues = []
    for log_path in list_raw_files():
        rel = log_path.name
        if rel in ingested:
            stored_hash = ingested[rel].get("hash", "")
            current_hash = file_hash(log_path)
            if stored_hash != current_hash:
                issues.append({
                    "severity": "warning",
                    "check": "stale_article",
                    "file": f"daily/{rel}",
                    "detail": f"Stale: {rel} has changed since last compilation",
                })
    return issues


def check_missing_backlinks() -> list[dict]:
    issues = []
    for article in list_wiki_articles():
        content = article.read_text(encoding="utf-8")
        rel = article.relative_to(KNOWLEDGE_DIR)
        source_link = str(rel).replace(".md", "").replace("\\", "/")
        for link in extract_wikilinks(content):
            if link.startswith("daily/"):
                continue
            target_path = KNOWLEDGE_DIR / f"{link}.md"
            if target_path.exists():
                target_content = target_path.read_text(encoding="utf-8")
                if f"[[{source_link}]]" not in target_content:
                    issues.append({
                        "severity": "suggestion",
                        "check": "missing_backlink",
                        "file": str(rel),
                        "detail": f"[[{source_link}]] links to [[{link}]] but not vice versa",
                    })
    return issues


def check_sparse_articles() -> list[dict]:
    issues = []
    for article in list_wiki_articles():
        word_count = get_article_word_count(article)
        if word_count < 200:
            rel = article.relative_to(KNOWLEDGE_DIR)
            issues.append({
                "severity": "suggestion",
                "check": "sparse_article",
                "file": str(rel),
                "detail": f"Sparse article: {word_count} words (minimum recommended: 200)",
            })
    return issues


def check_contradictions() -> list[dict]:
    """Use claude -p to detect contradictions across articles."""
    from claude_cli import run_claude_prompt

    wiki_content = read_all_wiki_content()

    prompt = f"""Review this knowledge base for contradictions, inconsistencies, or
conflicting claims across articles.

## Knowledge Base

{wiki_content}

## Instructions

Look for:
- Direct contradictions (article A says X, article B says not-X)
- Inconsistent recommendations (different articles recommend conflicting approaches)
- Outdated information that conflicts with newer entries

For each issue found, output EXACTLY one line in this format:
CONTRADICTION: [file1] vs [file2] - description of the conflict
INCONSISTENCY: [file] - description of the inconsistency

If no issues found, output exactly: NO_ISSUES

Do NOT output anything else - no preamble, no explanation, just the formatted lines."""

    try:
        response = run_claude_prompt(prompt, max_turns=2, tools=[])
    except Exception as e:
        return [{"severity": "error", "check": "contradiction", "file": "(system)", "detail": f"LLM check failed: {e}"}]

    issues = []
    if "NO_ISSUES" not in response:
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("CONTRADICTION:") or line.startswith("INCONSISTENCY:"):
                issues.append({
                    "severity": "warning",
                    "check": "contradiction",
                    "file": "(cross-article)",
                    "detail": line,
                })

    return issues


def generate_report(all_issues: list[dict]) -> str:
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    suggestions = [i for i in all_issues if i["severity"] == "suggestion"]

    lines = [
        f"# Lint Report - {today_iso()}",
        "",
        f"**Total issues:** {len(all_issues)}",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        f"- Suggestions: {len(suggestions)}",
        "",
    ]

    for severity, issues, marker in [
        ("Errors", errors, "x"),
        ("Warnings", warnings, "!"),
        ("Suggestions", suggestions, "?"),
    ]:
        if issues:
            lines.append(f"## {severity}")
            lines.append("")
            for issue in issues:
                lines.append(f"- **[{marker}]** `{issue['file']}` - {issue['detail']}")
            lines.append("")

    if not all_issues:
        lines.append("All checks passed. Knowledge base is healthy.")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Lint the knowledge base")
    parser.add_argument("--structural-only", action="store_true", help="Skip LLM checks (faster)")
    args = parser.parse_args()

    print("Running knowledge base lint checks...")
    all_issues: list[dict] = []

    checks = [
        ("Broken links", check_broken_links),
        ("Orphan pages", check_orphan_pages),
        ("Orphan sources", check_orphan_sources),
        ("Stale articles", check_stale_articles),
        ("Missing backlinks", check_missing_backlinks),
        ("Sparse articles", check_sparse_articles),
    ]

    for name, check_fn in checks:
        print(f"  Checking: {name}...")
        issues = check_fn()
        all_issues.extend(issues)
        print(f"    Found {len(issues)} issue(s)")

    if not args.structural_only:
        print("  Checking: Contradictions (LLM)...")
        issues = check_contradictions()
        all_issues.extend(issues)
        print(f"    Found {len(issues)} issue(s)")
    else:
        print("  Skipping: Contradictions (--structural-only)")

    report = generate_report(all_issues)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"lint-{today_iso()}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {report_path}")

    state = load_state()
    state["last_lint"] = now_iso()
    save_state(state)

    errors = sum(1 for i in all_issues if i["severity"] == "error")
    warnings = sum(1 for i in all_issues if i["severity"] == "warning")
    suggestions = sum(1 for i in all_issues if i["severity"] == "suggestion")
    print(f"\nResults: {errors} errors, {warnings} warnings, {suggestions} suggestions")

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    exit(main())
```

- [ ] **Step 4: Write scripts/query.py**

```python
"""Query the knowledge base using index-guided retrieval.

Usage:
    uv run python query.py "How should I handle auth redirects?"
    uv run python query.py "What patterns do I use?" --file-back
"""

from __future__ import annotations

import argparse
from pathlib import Path

from config import KNOWLEDGE_DIR, QA_DIR, now_iso
from utils import load_state, read_all_wiki_content, save_state
from claude_cli import run_claude_prompt

ROOT_DIR = Path(__file__).resolve().parent.parent


def run_query(question: str, file_back: bool = False) -> str:
    wiki_content = read_all_wiki_content()

    tools = ["Read", "Glob", "Grep"]
    permission_mode = None
    if file_back:
        tools.extend(["Write", "Edit"])
        permission_mode = "acceptEdits"

    file_back_instructions = ""
    if file_back:
        timestamp = now_iso()
        file_back_instructions = f"""

## File Back Instructions

After answering, do the following:
1. Create a Q&A article at {QA_DIR}/ with the filename being a slugified version
   of the question
2. Use the Q&A article format from the schema (frontmatter with title, question,
   consulted articles, filed date)
3. Update {KNOWLEDGE_DIR / 'index.md'} with a new row
4. Append to {KNOWLEDGE_DIR / 'log.md'}:
   ## [{timestamp}] query (filed) | question summary
   - Question: {question}
   - Consulted: [[list of articles read]]
   - Filed to: [[qa/article-name]]
"""

    prompt = f"""You are a knowledge base query engine. Answer the user's question by
consulting the knowledge base below.

## How to Answer

1. Read the INDEX section first - it lists every article with a one-line summary
2. Identify 3-10 articles that are relevant to the question
3. Read those articles carefully (they're included below)
4. Synthesize a clear, thorough answer
5. Cite your sources using [[wikilinks]]
6. If the knowledge base doesn't contain relevant information, say so honestly

## Knowledge Base

{wiki_content}

## Question

{question}
{file_back_instructions}"""

    max_turns = 15 if file_back else 2
    answer = run_claude_prompt(
        prompt,
        max_turns=max_turns,
        tools=tools,
        permission_mode=permission_mode,
    )

    state = load_state()
    state["query_count"] = state.get("query_count", 0) + 1
    save_state(state)

    return answer


def main():
    parser = argparse.ArgumentParser(description="Query the personal knowledge base")
    parser.add_argument("question", help="The question to ask")
    parser.add_argument("--file-back", action="store_true", help="File the answer back as Q&A")
    args = parser.parse_args()

    print(f"Question: {args.question}")
    print(f"File back: {'yes' if args.file_back else 'no'}")
    print("-" * 60)

    answer = run_query(args.question, file_back=args.file_back)
    print(answer)

    if args.file_back:
        print("\n" + "-" * 60)
        qa_count = len(list(QA_DIR.glob("*.md"))) if QA_DIR.exists() else 0
        print(f"Answer filed to knowledge/qa/ ({qa_count} Q&A articles total)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests**

```bash
uv run python -m pytest tests/test_lint.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/lint.py scripts/query.py tests/test_lint.py
git commit -m "feat: lint.py + query.py — SDK->CLI migration (MOD 1)

Both now use claude_cli.run_claude_prompt() instead of Agent SDK.
lint.py: 6 structural checks unchanged, LLM contradiction check migrated.
query.py: index-guided retrieval with optional file-back."
```

---

## Task 6: MOD 2 — `!save` Quick-Capture Hook

**Files:**
- Create: `hooks/user-prompt-submit.py`
- Test: `tests/test_save_hook.py`
- Modify: `.claude/settings.json` (add UserPromptSubmit hook)

This is the "zero-token save" mechanism. When user types `!save <text>`, the hook intercepts it (via exit code 2), writes directly to `daily/`, and blocks the prompt from reaching Claude — consuming zero tokens.

- [ ] **Step 1: Write the failing test**

```python
"""Tests for !save hook — UserPromptSubmit interceptor."""

import json
import sys
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))


def test_parse_save_command():
    """Should extract text after !save."""
    from user_prompt_submit import parse_save_command
    assert parse_save_command("!save This is important") == "This is important"
    assert parse_save_command("!save   Trimmed  ") == "Trimmed"
    assert parse_save_command("regular prompt") is None
    assert parse_save_command("!savenotsave") is None
    assert parse_save_command("!save") is None  # nothing to save


def test_save_writes_to_daily_log(tmp_path):
    """Should append !save content to today's daily log."""
    from user_prompt_submit import write_quick_save

    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()

    with patch("user_prompt_submit.DAILY_DIR", daily_dir):
        write_quick_save("TIL: Python pathlib is great")

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = daily_dir / f"{today}.md"
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "TIL: Python pathlib is great" in content
    assert "Quick Save" in content
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m pytest tests/test_save_hook.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write hooks/user-prompt-submit.py**

```python
"""UserPromptSubmit hook — !save quick-capture interceptor.

When user types "!save <text>", this hook:
1. Parses the text after !save
2. Writes it directly to today's daily log
3. Exits with code 2 (blocks prompt from reaching Claude = 0 tokens)
4. Sends feedback via stderr

Configure in .claude/settings.json:
{
    "hooks": {
        "UserPromptSubmit": [{
            "matcher": "^!save",
            "hooks": [{
                "type": "command",
                "command": "uv run python hooks/user-prompt-submit.py"
            }]
        }]
    }
}
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = ROOT / "daily"


def parse_save_command(prompt: str) -> str | None:
    """Extract text after !save. Returns None if not a save command or empty."""
    prompt = prompt.strip()
    if not prompt.startswith("!save"):
        return None
    # Must be "!save " (with space) not "!savenotsave"
    if len(prompt) <= 5:
        return None
    if prompt[5] != " ":
        return None
    text = prompt[6:].strip()
    return text if text else None


def write_quick_save(text: str) -> Path:
    """Append quick-save text to today's daily log. Returns the log path."""
    today = datetime.now(timezone.utc).astimezone()
    log_path = DAILY_DIR / f"{today.strftime('%Y-%m-%d')}.md"

    if not log_path.exists():
        DAILY_DIR.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"# Daily Log: {today.strftime('%Y-%m-%d')}\n\n## Sessions\n\n## Memory Maintenance\n\n",
            encoding="utf-8",
        )

    time_str = today.strftime("%H:%M")
    entry = f"### Quick Save ({time_str})\n\n{text}\n\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)

    return log_path


def main():
    # Read hook input from stdin
    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Not valid JSON — not our problem, let it through
        sys.exit(0)

    prompt = hook_input.get("prompt", "")
    text = parse_save_command(prompt)

    if text is None:
        # Not a !save command — let it through to Claude
        sys.exit(0)

    # It's a !save command — write to daily log and block
    log_path = write_quick_save(text)

    # Exit 2 = block prompt from reaching Claude (zero tokens consumed)
    # stderr = feedback shown to user
    print(f"Saved to {log_path.name}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
```

**Key design:**
- `exit(2)` = CC blocks the prompt entirely. Claude never sees it. Zero tokens.
- `stderr` output = shown to user as feedback ("Saved to 2026-04-11.md").
- `matcher: "^!save"` in settings.json = hook only fires for `!save` prompts, not every prompt.
- `parse_save_command` distinguishes `!save text` from `!savenotsave` and empty `!save`.

- [ ] **Step 4: Run tests**

```bash
uv run python -m pytest tests/test_save_hook.py -v
```

Expected: PASS.

- [ ] **Step 5: Update .claude/settings.json — add UserPromptSubmit hook**

Add to the existing hooks config:

```json
"UserPromptSubmit": [
  {
    "matcher": "^!save",
    "hooks": [
      {
        "type": "command",
        "command": "uv run python hooks/user-prompt-submit.py",
        "timeout": 5
      }
    ]
  }
]
```

- [ ] **Step 6: Commit**

```bash
git add hooks/user-prompt-submit.py tests/test_save_hook.py .claude/settings.json
git commit -m "feat: !save quick-capture hook (MOD 2)

UserPromptSubmit hook intercepts '!save <text>' prompts.
Writes directly to daily log, exit 2 blocks prompt (zero tokens).
Matcher '^!save' ensures hook only fires for save commands."
```

---

## Task 7: MOD 5 — Technology Categorization in AGENTS.md

**Files:**
- Create: `AGENTS.md` (adapted from coleam00 with categorization)

This is a prompt engineering task — we modify AGENTS.md to include categorization rules so the compiler produces better-organized articles.

- [ ] **Step 1: Copy AGENTS.md from coleam00**

Copy the full AGENTS.md fetched above.

- [ ] **Step 2: Add categorization section to AGENTS.md**

Insert after the Concept Articles format section, before Connection Articles:

```markdown
### Article Categorization (MetaMode Extension)

Every concept article should be categorized by technology/domain using tags in frontmatter:

**Category tags** (use 1-3 per article):
- `python`, `javascript`, `typescript`, `rust`, `go` — language-specific
- `claude-code`, `claude-api`, `anthropic` — Claude ecosystem
- `git`, `github`, `ci-cd` — version control and deployment  
- `testing`, `tdd`, `debugging` — quality practices
- `architecture`, `design-patterns`, `refactoring` — software design
- `devtools`, `shell`, `terminal` — development environment
- `web`, `frontend`, `backend`, `api` — web development
- `database`, `sql`, `orm` — data layer
- `ai`, `llm`, `agents`, `prompting` — AI/ML
- `workflow`, `productivity`, `meta` — process and meta-knowledge

**Enhanced article format:**

```markdown
---
title: "Concept Name"
aliases: [alternate-name]
tags: [category-tag-1, category-tag-2]
category: "technology-or-domain"
sources:
  - "daily/2026-04-01.md"
created: 2026-04-01
updated: 2026-04-03
---

# Concept Name

**Context:** [When/where this knowledge applies]

**Problem:** [What challenge or question this addresses]

**Lesson:** [The key takeaway — the most important sentence in the article]

## Key Points
...

## Details
...

## Related Concepts
- [[concepts/related]] - How it connects
```

The enhanced format adds: `category` field, `Context/Problem/Lesson` structure at the top for quick scanning. The compiler should use this format for all new articles.
```

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "feat: AGENTS.md — add technology categorization (MOD 5)

Added category tags, enhanced article format with Context/Problem/Lesson
structure for quick scanning. Compiler will use this for all new articles."
```

---

## Task 8: MOD 4 + MOD 6 — Pending Review + Compile Reminder in session-start.py

**Files:**
- Create: `hooks/session-start.py` (modified from coleam00)
- Test: `tests/test_session_start.py`

session-start.py gets two additions:
1. **MOD 4**: Read `pending-review.md` and inject its content for user approval
2. **MOD 6**: Check if daily logs need compilation and remind user

- [ ] **Step 1: Write the failing test**

```python
"""Tests for session-start.py — context injection with pending review + compile reminder."""

import json
import sys
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))


def test_build_context_includes_index(tmp_path):
    """Should include knowledge base index in context."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    index_file = knowledge_dir / "index.md"
    index_file.write_text("| [[concepts/test]] | Test article | daily/2026-04-11.md | 2026-04-11 |", encoding="utf-8")

    with patch("session_start.KNOWLEDGE_DIR", knowledge_dir), \
         patch("session_start.INDEX_FILE", index_file), \
         patch("session_start.DAILY_DIR", tmp_path / "daily"), \
         patch("session_start.PENDING_REVIEW_FILE", tmp_path / "nonexistent.md"), \
         patch("session_start.STATE_FILE", tmp_path / "state.json"):
        from session_start import build_context
        context = build_context()
        assert "concepts/test" in context


def test_build_context_includes_pending_review(tmp_path):
    """MOD 4: Should include pending review items."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "index.md").write_text("Empty index", encoding="utf-8")

    pending = tmp_path / "pending-review.md"
    pending.write_text("---\nsession_id: abc\nstatus: pending\n---\n\nImportant lesson here\n\n---\n", encoding="utf-8")

    with patch("session_start.KNOWLEDGE_DIR", knowledge_dir), \
         patch("session_start.INDEX_FILE", knowledge_dir / "index.md"), \
         patch("session_start.DAILY_DIR", tmp_path / "daily"), \
         patch("session_start.PENDING_REVIEW_FILE", pending), \
         patch("session_start.STATE_FILE", tmp_path / "state.json"):
        from session_start import build_context
        context = build_context()
        assert "Pending Review" in context
        assert "Important lesson here" in context


def test_build_context_compile_reminder(tmp_path):
    """MOD 6: Should remind about uncompiled logs."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "index.md").write_text("Empty", encoding="utf-8")

    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()
    # Create 4 uncompiled daily logs
    for i in range(4):
        d = datetime.now() - timedelta(days=i)
        (daily_dir / f"{d.strftime('%Y-%m-%d')}.md").write_text(f"# Log {i}", encoding="utf-8")

    state_file = tmp_path / "state.json"
    state_file.write_text('{"ingested": {}}', encoding="utf-8")

    with patch("session_start.KNOWLEDGE_DIR", knowledge_dir), \
         patch("session_start.INDEX_FILE", knowledge_dir / "index.md"), \
         patch("session_start.DAILY_DIR", daily_dir), \
         patch("session_start.PENDING_REVIEW_FILE", tmp_path / "nonexistent.md"), \
         patch("session_start.STATE_FILE", state_file):
        from session_start import build_context
        context = build_context()
        assert "Compile Reminder" in context
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m pytest tests/test_session_start.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write hooks/session-start.py**

```python
"""SessionStart hook — injects KB context + pending review + compile reminder.

Outputs JSON to stdout with additionalContext for Claude to see.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge"
DAILY_DIR = ROOT / "daily"
INDEX_FILE = KNOWLEDGE_DIR / "index.md"
SCRIPTS_DIR = ROOT / "scripts"
PENDING_REVIEW_FILE = SCRIPTS_DIR / "pending-review.md"
STATE_FILE = SCRIPTS_DIR / "state.json"

MAX_CONTEXT_CHARS = 20_000
MAX_LOG_LINES = 30

# MOD 6: Compile reminder thresholds
COMPILE_REMINDER_UNCOMPILED_THRESHOLD = 3  # remind if >= N uncompiled logs
COMPILE_REMINDER_DAYS_THRESHOLD = 3  # remind if oldest uncompiled > N days


def get_recent_log() -> str:
    today = datetime.now(timezone.utc).astimezone()
    for offset in range(2):
        date = today - timedelta(days=offset)
        log_path = DAILY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if log_path.exists():
            lines = log_path.read_text(encoding="utf-8").splitlines()
            recent = lines[-MAX_LOG_LINES:] if len(lines) > MAX_LOG_LINES else lines
            return "\n".join(recent)
    return "(no recent daily log)"


def get_pending_review() -> str:
    """MOD 4: Read pending review items for user approval."""
    if not PENDING_REVIEW_FILE.exists():
        return ""
    content = PENDING_REVIEW_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return ""
    return content


def get_compile_reminder() -> str:
    """MOD 6: Check if daily logs need compilation."""
    if not DAILY_DIR.exists():
        return ""

    # Load compilation state
    ingested = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            ingested = state.get("ingested", {})
        except (json.JSONDecodeError, OSError):
            pass

    # Find uncompiled logs
    uncompiled = []
    for log_path in sorted(DAILY_DIR.glob("*.md")):
        if log_path.name not in ingested:
            uncompiled.append(log_path.name)

    if len(uncompiled) < COMPILE_REMINDER_UNCOMPILED_THRESHOLD:
        return ""

    # Check age of oldest uncompiled
    oldest = uncompiled[0]  # sorted, so first is oldest
    try:
        oldest_date = datetime.strptime(oldest.replace(".md", ""), "%Y-%m-%d")
        days_old = (datetime.now() - oldest_date).days
    except ValueError:
        days_old = 0

    if days_old < COMPILE_REMINDER_DAYS_THRESHOLD and len(uncompiled) < COMPILE_REMINDER_UNCOMPILED_THRESHOLD:
        return ""

    return (
        f"{len(uncompiled)} uncompiled daily logs "
        f"(oldest: {oldest}, {days_old} days ago). "
        f"Consider running `/compile` or `uv run python scripts/compile.py`."
    )


def build_context() -> str:
    parts = []

    today = datetime.now(timezone.utc).astimezone()
    parts.append(f"## Today\n{today.strftime('%A, %B %d, %Y')}")

    # Knowledge base index
    if INDEX_FILE.exists():
        index_content = INDEX_FILE.read_text(encoding="utf-8")
        parts.append(f"## Knowledge Base Index\n\n{index_content}")
    else:
        parts.append("## Knowledge Base Index\n\n(empty - no articles compiled yet)")

    # Recent daily log
    recent_log = get_recent_log()
    parts.append(f"## Recent Daily Log\n\n{recent_log}")

    # MOD 4: Pending review
    pending = get_pending_review()
    if pending:
        parts.append(
            f"## Pending Review\n\n"
            f"The following knowledge was extracted from recent sessions and needs your review.\n"
            f"Reply 'approve' to save to daily log, 'reject' to discard, or 'edit' to modify.\n\n"
            f"{pending}"
        )

    # MOD 6: Compile reminder
    reminder = get_compile_reminder()
    if reminder:
        parts.append(f"## Compile Reminder\n\n{reminder}")

    context = "\n\n---\n\n".join(parts)

    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS] + "\n\n...(truncated)"

    return context


def main():
    context = build_context()
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
uv run python -m pytest tests/test_session_start.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add hooks/session-start.py tests/test_session_start.py
git commit -m "feat: session-start.py — pending review + compile reminder (MOD 4+6)

Injects KB index + recent log (from coleam00) plus:
MOD 4: Shows pending-review.md items for approve/reject/edit.
MOD 6: Reminds when >= 3 uncompiled logs or oldest > 3 days."
```

---

## Task 9: Skills — /reflect + /compile

**Files:**
- Create: `.claude/skills/reflect/SKILL.md`
- Create: `.claude/skills/compile/SKILL.md`

Skills are markdown files with YAML frontmatter. Claude Code reads them when the user types `/reflect` or `/compile`.

- [ ] **Step 1: Create .claude/skills/ directory**

```bash
mkdir -p .claude/skills/reflect .claude/skills/compile
```

- [ ] **Step 2: Write /reflect skill**

`.claude/skills/reflect/SKILL.md`:

```markdown
---
name: reflect
description: Structured end-of-session reflection — captures what you learned, what surprised you, what to do differently
allowed-tools: Read Write Edit
---

# /reflect — Session Reflection

Guide the user through a structured reflection at the end of a session. This captures high-quality knowledge that auto-flush might miss.

## Process

Ask these 4 questions one at a time, waiting for the user's answer before proceeding:

1. **What did you learn today?** — New facts, patterns, or concepts discovered in this session.
2. **What surprised you?** — Anything unexpected, counter-intuitive, or that changed your mental model.
3. **What would you do differently?** — Mistakes, wrong turns, or approaches you'd change next time.
4. **What should you remember for next time?** — Action items, gotchas, or context for future sessions.

## After all 4 answers

Compile the user's answers into a structured daily log entry and append it to today's daily log at `daily/YYYY-MM-DD.md`.

Use this format:

```
### Reflection (HH:MM)

**Learned:**
- [compiled from answer 1]

**Surprised:**
- [compiled from answer 2]

**Do Differently:**
- [compiled from answer 3]

**Remember:**
- [compiled from answer 4]
```

Create the daily log file if it doesn't exist. Use the same header format as other daily log entries:
```
# Daily Log: YYYY-MM-DD

## Sessions

## Memory Maintenance
```

After writing, confirm: "Reflection saved to daily/YYYY-MM-DD.md"
```

- [ ] **Step 3: Write /compile skill**

`.claude/skills/compile/SKILL.md`:

```markdown
---
name: compile
description: Manually compile daily logs into wiki knowledge articles
allowed-tools: Bash Read Write Edit Glob Grep
---

# /compile — Manual Knowledge Compilation

Compile unprocessed daily logs into structured knowledge articles.

## Usage

- `/compile` — compile all new/changed daily logs
- `/compile --all` — force recompile everything
- `/compile --dry-run` — show what would be compiled
- `/compile --file daily/2026-04-11.md` — compile specific file

## Process

Run the compile script:

```bash
uv run python scripts/compile.py $ARGS
```

Where `$ARGS` are the arguments passed after `/compile` (if any — `$0` contains them).

After compilation completes, report:
1. How many logs were compiled
2. How many articles were created/updated
3. Any errors encountered

If there are no logs to compile, inform the user: "All daily logs are up to date."
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/reflect/SKILL.md .claude/skills/compile/SKILL.md
git commit -m "feat: /reflect + /compile skills (MOD 3 + BONUS)

/reflect: 4-question structured reflection, writes to daily log.
/compile: manual compile trigger with --all, --dry-run, --file flags."
```

---

## Implementation Order and Session Plan

### Dependency graph (critical path):

```
Session B.1: Task 1 (Base) → Task 2 (claude_cli.py)
Session B.2: Task 3 (flush.py) → Task 4 (compile.py) → Task 5 (lint+query)
Session B.3: Task 6 (!save) + Task 7 (AGENTS.md) + Task 8 (session-start) + Task 9 (skills)
Session B.4: Integration testing + smoke test
```

### Session breakdown:

| Session | Tasks | Duration est. | What's testable after |
|---------|-------|---------------|----------------------|
| **B.1** | Task 1 (Base setup) + Task 2 (claude_cli.py) | 1-2h | `uv run python -c "from claude_cli import run_claude_prompt; print('OK')"` |
| **B.2** | Task 3 (flush) + Task 4 (compile) + Task 5 (lint+query) | 1-2h | `uv run python scripts/compile.py --dry-run`, `uv run python scripts/lint.py --structural-only` |
| **B.3** | Task 6 (!save) + Task 7 (AGENTS.md) + Task 8 (session-start) + Task 9 (skills) | 1-2h | Full hook cycle: start session → see context → `!save test` → `/reflect` → `/compile` |
| **B.4** | Integration test: full session lifecycle | 1h | End-to-end: session start → work → session end → flush → compile → query |

### What can be parallelized in B.3:

Tasks 6, 7, 8, 9 are mostly independent (different files). If using subagent-driven development, they can run in parallel:
- Agent A: Task 6 (!save hook)
- Agent B: Task 7 (AGENTS.md) + Task 9 (skills)
- Agent C: Task 8 (session-start.py)

### Known gaps (to resolve during implementation):

1. **Pending review approve/reject mechanism** — session-start.py shows pending items and asks user to "approve/reject/edit", but there's no automated handler. In v1 this is manual: user reads the pending items, then either (a) types `!save <approved text>` to save, or (b) manually deletes pending-review.md. A dedicated `!approve` / `!reject` handler could be added in v1.1 as another UserPromptSubmit matcher.

2. **pytest dependency** — not in pyproject.toml. Add as dev dependency: `uv add --dev pytest`.

3. **`sys.path.insert` in tests** — fragile. Consider adding a `conftest.py` that handles path setup, or use `uv run python -m pytest` with proper package structure.

### Risk items:

1. **`claude -p` output format** — we assume `--output-format json` returns `{"result": [{"type": "text", "text": "..."}]}`. Need to verify in B.1. If format differs, only `claude_cli.py` needs updating (single point of change).
2. **`--no-session-persistence`** flag — may not exist in current CLI version. Need to verify. Fallback: omit it (sessions are cleaned up automatically).
3. **Windows `CREATE_NO_WINDOW`** — tested by coleam00, should work. Verify in B.1.
4. **Hook `matcher` for UserPromptSubmit** — `"^!save"` regex on the `prompt` field. Need to verify CC applies matcher to the prompt text, not event name. If not, remove matcher and handle in Python.
5. **Skill `$ARGS` / `$0` substitution** — verify how CC passes arguments to skills. If not supported, `/compile` skill will need to parse arguments differently.
6. **`claude -p` with `--allowedTools`** — verify the exact flag name. Could be `--allowed-tools` (kebab-case). Check `claude --help`.

---

## Verification Checklist (Session B.4)

- [ ] `uv run python scripts/compile.py --dry-run` — shows uncompiled logs
- [ ] `uv run python scripts/lint.py --structural-only` — runs without errors
- [ ] Start a new CC session in MetaMode project — see KB index injected
- [ ] Type `!save Test quick save` — see feedback, check daily log
- [ ] Type `/reflect` — get 4 questions, answers saved to daily log
- [ ] Type `/compile` — compiles daily logs into knowledge articles
- [ ] End session — flush.py runs, writes to pending-review.md
- [ ] Start new session — see pending review items in context
- [ ] `uv run python scripts/query.py "What do I know?"` — returns answer from KB
