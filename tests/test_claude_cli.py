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
        assert "--output-format" in cmd
        assert "--no-session-persistence" in cmd


def test_run_claude_prompt_with_tools():
    """run_claude_prompt should pass --allowedTools when tools are specified."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({
        "result": [{"type": "text", "text": "Done"}],
        "is_error": False
    })

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


def test_run_claude_prompt_is_error_flag():
    """run_claude_prompt should raise when Claude returns is_error=True."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({
        "result": [{"type": "text", "text": "error details"}],
        "is_error": True
    })

    with patch("claude_cli.subprocess.run", return_value=mock_result):
        try:
            run_claude_prompt("Will error")
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "error" in str(e).lower()


def test_run_claude_prompt_raw_text_fallback():
    """run_claude_prompt should handle non-JSON output gracefully."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Just plain text response"

    with patch("claude_cli.subprocess.run", return_value=mock_result):
        result = run_claude_prompt("Simple question")
        assert result == "Just plain text response"


def test_run_claude_prompt_string_result():
    """run_claude_prompt should handle result as plain string (not array).

    Bug found in B.4: claude -p can return {"result": "text"} instead of
    {"result": [{"type": "text", "text": "text"}]}. Iterating over a string
    yields individual characters, producing character-per-line output.
    """
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({
        "result": "FLUSH_OK",
        "session_id": "test-456",
        "is_error": False
    })

    with patch("claude_cli.subprocess.run", return_value=mock_result):
        result = run_claude_prompt("Flush this")
        assert result == "FLUSH_OK"
        assert "\n" not in result  # must NOT be "F\nL\nU\nS\nH\n_\nO\nK"
