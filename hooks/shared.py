"""Shared utilities for Claude Code hooks.

Hooks run independently (not as part of scripts/), so they maintain their own
shared module rather than importing from scripts/.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


MAX_TURNS = 30
MAX_CONTEXT_CHARS = 15_000


def parse_hook_stdin() -> dict:
    """Read and parse JSON hook input from stdin.

    Handles Windows cp1251 encoding and malformed backslash escapes
    that can appear in Windows file paths.

    Returns parsed dict, or raises ValueError on failure.
    """
    sys.stdin.reconfigure(encoding="utf-8")
    raw = sys.stdin.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fix unescaped backslashes in Windows paths (e.g. C:\Users\...)
        fixed = re.sub(r'(?<!\\)\\(?!["\\])', r'\\\\', raw)
        return json.loads(fixed)


def extract_conversation_context(transcript_path: Path) -> tuple[str, int]:
    """Read JSONL transcript and extract last ~N conversation turns as markdown.

    Returns (context_string, turn_count).
    """
    turns: list[str] = []

    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg = entry.get("message", {})
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
            else:
                role = entry.get("role", "")
                content = entry.get("content", "")

            if role not in ("user", "assistant"):
                continue

            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        text_parts.append(block)
                content = "\n".join(text_parts)

            if isinstance(content, str) and content.strip():
                label = "User" if role == "user" else "Assistant"
                turns.append(f"**{label}:** {content.strip()}\n")

    recent = turns[-MAX_TURNS:]
    context = "\n".join(recent)

    if len(context) > MAX_CONTEXT_CHARS:
        context = context[-MAX_CONTEXT_CHARS:]
        boundary = context.find("\n**")
        if boundary > 0:
            context = context[boundary + 1:]

    return context, len(recent)
