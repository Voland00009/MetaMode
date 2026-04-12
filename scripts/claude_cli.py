"""Shared helper: run Claude CLI headless (claude -p) as subprocess.

Replaces all claude_agent_sdk.query() calls in the coleam00 codebase.
Uses `claude -p` which is covered by Max subscription ($0/mo).

Usage:
    from claude_cli import run_claude_prompt

    result = run_claude_prompt(
        prompt="Extract knowledge from this text...",
        tools=[],  # no tools = text-only response
    )
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def run_claude_prompt(
    prompt: str,
    *,
    tools: list[str] | None = None,
    permission_mode: str | None = None,
    system_prompt_file: Path | None = None,
    cwd: Path | str | None = None,
    timeout: int = 300,
) -> str:
    """Run a prompt through `claude -p` and return the text result.

    Args:
        prompt: The prompt text to send.
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
        "--no-session-persistence",
    ]

    if tools is not None:
        for tool in tools:
            cmd.extend(["--allowedTools", tool])

    if permission_mode:
        cmd.extend(["--permission-mode", permission_mode])

    if system_prompt_file:
        cmd.extend(["--system-prompt-file", str(system_prompt_file)])

    kwargs: dict = {
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "timeout": timeout,
        "cwd": str(cwd or ROOT_DIR),
        "input": prompt,
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
    result_data = data.get("result", "")

    # result can be a plain string or a list of content blocks
    if isinstance(result_data, str):
        return result_data

    text_parts = []
    for block in result_data:
        if isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(block.get("text", ""))
        elif isinstance(block, str):
            text_parts.append(block)

    return "\n".join(text_parts)
