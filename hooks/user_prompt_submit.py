"""UserPromptSubmit hook — !save quick-capture interceptor.

When user types "!save <text>", this hook:
1. Parses the text after !save
2. Writes it directly to today's daily log
3. Exits with code 2 (blocks prompt from reaching Claude = 0 tokens)
4. Sends feedback via stderr
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import now_local  # noqa: E402

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
    today = now_local()
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
    # Read hook input from stdin (force UTF-8, Windows defaults to cp1251)
    sys.stdin.reconfigure(encoding="utf-8")
    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    prompt = hook_input.get("prompt", "")
    text = parse_save_command(prompt)

    if text is None:
        sys.exit(0)

    log_path = write_quick_save(text)

    # Exit 2 = block prompt from reaching Claude (zero tokens consumed)
    # stderr = feedback shown to user
    print(f"Saved to {log_path.name}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
