"""Tests for flush.py — knowledge extraction from conversation context."""

import json
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import flush


def test_append_to_daily_log_creates_file(tmp_path):
    """append_to_daily_log should create daily log file if missing."""
    with patch.object(flush, "DAILY_DIR", tmp_path):
        flush.append_to_daily_log("Test content", "Test Section")

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

    with patch.object(flush, "DAILY_DIR", tmp_path):
        flush.append_to_daily_log("New entry", "Session")

    content = log_file.read_text(encoding="utf-8")
    assert "# Existing" in content
    assert "New entry" in content


def test_dedup_skips_recent_flush(tmp_path):
    """Flush should skip if same session was flushed within 60 seconds."""
    state_file = tmp_path / "last-flush.json"
    state_file.write_text(json.dumps({
        "session_id": "test-session",
        "timestamp": time.time()  # just now
    }), encoding="utf-8")

    with patch.object(flush, "STATE_FILE", state_file):
        state = flush.load_flush_state()
        assert state["session_id"] == "test-session"
        assert time.time() - state["timestamp"] < 60


def test_write_pending_review(tmp_path):
    """write_pending_review should create/append to pending-review.md."""
    pending_file = tmp_path / "pending-review.md"

    with patch.object(flush, "PENDING_REVIEW_FILE", pending_file):
        flush.write_pending_review("Learned about X", "session-abc")

    content = pending_file.read_text(encoding="utf-8")
    assert "session-abc" in content
    assert "Learned about X" in content
    assert "status: pending" in content


def test_write_pending_review_appends(tmp_path):
    """write_pending_review should append multiple entries."""
    pending_file = tmp_path / "pending-review.md"
    pending_file.write_text("# Existing entry\n", encoding="utf-8")

    with patch.object(flush, "PENDING_REVIEW_FILE", pending_file):
        flush.write_pending_review("Entry 2", "session-def")

    content = pending_file.read_text(encoding="utf-8")
    assert "# Existing entry" in content
    assert "Entry 2" in content


def test_run_flush_calls_claude_cli():
    """run_flush should call run_claude_prompt with tools=[]."""
    with patch("claude_cli.run_claude_prompt", return_value="FLUSH_OK") as mock:
        result = flush.run_flush("Some conversation context")
        assert result == "FLUSH_OK"
        mock.assert_called_once()
        _, kwargs = mock.call_args
        assert kwargs.get("tools") == []


def test_run_flush_handles_error():
    """run_flush should catch exceptions and return error string."""
    with patch("claude_cli.run_claude_prompt", side_effect=RuntimeError("CLI failed")):
        result = flush.run_flush("Context")
        assert "FLUSH_ERROR" in result
        assert "RuntimeError" in result
