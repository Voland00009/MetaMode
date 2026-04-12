"""SessionStart hook — injects KB context + compile reminder.

Outputs JSON to stdout with additionalContext for Claude to see.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge"
DAILY_DIR = ROOT / "daily"
RAW_DIR = ROOT / "raw"
INDEX_FILE = KNOWLEDGE_DIR / "index.md"
SCRIPTS_DIR = ROOT / "scripts"
STATE_FILE = SCRIPTS_DIR / "state.json"

RAW_EXTENSIONS = {".md", ".txt"}

MAX_CONTEXT_CHARS = 20_000
MAX_LOG_LINES = 30

COMPILE_REMINDER_UNCOMPILED_THRESHOLD = 3
COMPILE_REMINDER_DAYS_THRESHOLD = 3


def get_recent_log() -> str:
    """Get last N lines from today's or yesterday's daily log."""
    today = datetime.now(timezone.utc).astimezone()
    for offset in range(2):
        date = today - timedelta(days=offset)
        log_path = DAILY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if log_path.exists():
            lines = log_path.read_text(encoding="utf-8").splitlines()
            recent = lines[-MAX_LOG_LINES:] if len(lines) > MAX_LOG_LINES else lines
            return "\n".join(recent)
    return "(no recent daily log)"


def get_compile_reminder() -> str:
    """MOD 6: Check if daily logs need compilation."""
    if not DAILY_DIR.exists():
        return ""

    ingested = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            ingested = state.get("ingested", {})
        except (json.JSONDecodeError, OSError):
            pass

    uncompiled = []
    for log_path in sorted(DAILY_DIR.glob("*.md")):
        if log_path.name not in ingested:
            uncompiled.append(log_path.name)

    if len(uncompiled) < COMPILE_REMINDER_UNCOMPILED_THRESHOLD:
        return ""

    oldest = uncompiled[0]
    try:
        oldest_date = datetime.strptime(oldest.replace(".md", ""), "%Y-%m-%d")
        days_old = (datetime.now() - oldest_date).days
    except ValueError:
        days_old = 0

    return (
        f"{len(uncompiled)} uncompiled daily logs "
        f"(oldest: {oldest}, {days_old} days ago). "
        f"Consider running `/compile` or `uv run python scripts/compile.py`."
    )


def get_raw_reminder() -> str:
    """Check if raw/ has unprocessed files."""
    if not RAW_DIR.exists():
        return ""
    files = [
        f for f in RAW_DIR.iterdir()
        if f.is_file() and f.suffix in RAW_EXTENSIONS and f.name != "README.md"
    ]
    if not files:
        return ""
    names = ", ".join(f.name for f in files[:5])
    suffix = f" (and {len(files) - 5} more)" if len(files) > 5 else ""
    return (
        f"{len(files)} unprocessed file(s) in `raw/`: {names}{suffix}. "
        f"Say 'обработай RAW' or run `uv run python scripts/ingest_raw.py`."
    )


def build_context() -> str:
    """Build the full context string to inject at session start."""
    parts = []

    today = datetime.now(timezone.utc).astimezone()
    parts.append(f"## Today\n{today.strftime('%A, %B %d, %Y')}")

    if INDEX_FILE.exists():
        index_content = INDEX_FILE.read_text(encoding="utf-8")
        parts.append(f"## Knowledge Base Index\n\n{index_content}")
    else:
        parts.append("## Knowledge Base Index\n\n(empty - no articles compiled yet)")

    recent_log = get_recent_log()
    parts.append(f"## Recent Daily Log\n\n{recent_log}")

    reminder = get_compile_reminder()
    if reminder:
        parts.append(f"## Compile Reminder\n\n{reminder}")

    raw_reminder = get_raw_reminder()
    if raw_reminder:
        parts.append(f"## RAW Inbox\n\n{raw_reminder}")

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
