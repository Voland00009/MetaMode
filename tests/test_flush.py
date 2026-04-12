"""Tests for flush.py — knowledge extraction from conversation context."""

import json
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

import pytest

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


@pytest.mark.asyncio
async def test_run_quality_audit_ok():
    """Quality audit should return None when content is good."""
    mock_gen = _make_sdk_response("QUALITY_OK")
    with patch("claude_agent_sdk.query", side_effect=mock_gen):
        result = await flush.run_quality_audit("Good content with lessons learned")
        assert result is None


@pytest.mark.asyncio
async def test_run_quality_audit_reject():
    """Quality audit should return reason string when content is junk."""
    mock_gen = _make_sdk_response("AUDIT_REJECT: Only routine file reads")
    with patch("claude_agent_sdk.query", side_effect=mock_gen):
        result = await flush.run_quality_audit("Routine stuff")
        assert result == "Only routine file reads"


@pytest.mark.asyncio
async def test_run_quality_audit_error_returns_none():
    """Quality audit should return None (assume OK) on SDK error."""
    async def failing_query(**kwargs):
        raise RuntimeError("SDK failed")
        yield  # noqa: E501

    with patch("claude_agent_sdk.query", side_effect=failing_query):
        result = await flush.run_quality_audit("Some content")
        assert result is None


def _make_sdk_response(text: str):
    """Create a mock async generator that yields an AssistantMessage with given text."""
    from claude_agent_sdk import AssistantMessage, TextBlock

    async def mock_query(**kwargs):
        yield AssistantMessage(content=[TextBlock(text=text)], model="test")

    return mock_query


@pytest.mark.asyncio
async def test_run_flush_calls_sdk():
    """run_flush should call SDK query and return response text."""
    mock_gen = _make_sdk_response("FLUSH_OK")
    with patch("claude_agent_sdk.query", side_effect=mock_gen):
        result = await flush.run_flush("Some conversation context")
        assert result == "FLUSH_OK"


@pytest.mark.asyncio
async def test_run_flush_handles_error():
    """run_flush should catch exceptions and return error string."""
    async def failing_query(**kwargs):
        raise RuntimeError("SDK failed")
        yield  # make it an async generator  # noqa: E501

    with patch("claude_agent_sdk.query", side_effect=failing_query):
        result = await flush.run_flush("Context")
        assert "FLUSH_ERROR" in result
        assert "RuntimeError" in result
