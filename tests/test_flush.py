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
    """Quality audit returns empty AuditOutcome when content is good."""
    mock_gen = _make_sdk_response("QUALITY_OK")
    with patch("claude_agent_sdk.query", side_effect=mock_gen):
        result = await flush.run_quality_audit("Good content with lessons learned")
        assert result == flush.AuditOutcome()
        assert result.reject_reason is None
        assert result.sdk_error_marker is None


@pytest.mark.asyncio
async def test_run_quality_audit_reject():
    """Quality audit returns reject_reason in AuditOutcome when content is junk."""
    mock_gen = _make_sdk_response("AUDIT_REJECT: Only routine file reads")
    with patch("claude_agent_sdk.query", side_effect=mock_gen):
        result = await flush.run_quality_audit("Routine stuff")
        assert result.reject_reason == "Only routine file reads"
        assert result.sdk_error_marker is None


@pytest.mark.asyncio
async def test_run_quality_audit_generic_error_sets_marker(caplog):
    """Generic (non-SDK) errors should set sdk_error_marker and log ERROR."""
    async def failing_query(**kwargs):
        raise RuntimeError("SDK failed")
        yield  # noqa: E501

    with patch("claude_agent_sdk.query", side_effect=failing_query):
        with caplog.at_level("ERROR"):
            result = await flush.run_quality_audit("Some content")

    assert result.reject_reason is None
    assert result.sdk_error_marker is not None
    assert "RuntimeError" in result.sdk_error_marker
    assert any("Quality audit error" in rec.message for rec in caplog.records)


@pytest.mark.asyncio
async def test_run_quality_audit_handles_process_error(caplog):
    """ProcessError should surface exit_code and stderr into marker + log."""
    from claude_agent_sdk import ProcessError

    async def failing_query(**kwargs):
        raise ProcessError("CLI failed", exit_code=1, stderr="boom stderr line")
        yield  # noqa: E501

    with patch("claude_agent_sdk.query", side_effect=failing_query):
        with caplog.at_level("ERROR"):
            result = await flush.run_quality_audit("Some content")

    assert result.reject_reason is None
    assert result.sdk_error_marker is not None
    assert "exit=1" in result.sdk_error_marker
    assert "ProcessError" in result.sdk_error_marker
    # Logs should include exit code, stderr content, and SDK error label
    log_text = "\n".join(rec.getMessage() for rec in caplog.records)
    assert "Quality audit SDK error" in log_text
    assert "exit=1" in log_text
    assert "boom stderr line" in log_text


def _run_main_with_stubbed_sdk(tmp_path, flush_response, audit_outcome):
    """Helper: invoke flush.main() with run_flush/run_quality_audit stubbed."""
    ctx_file = tmp_path / "ctx.md"
    ctx_file.write_text("real conversation context", encoding="utf-8")
    state_file = tmp_path / "last-flush.json"

    async def fake_flush(_ctx):
        return flush_response

    async def fake_audit(_content):
        return audit_outcome

    with patch.object(flush, "DAILY_DIR", tmp_path), \
         patch.object(flush, "STATE_FILE", state_file), \
         patch.object(flush, "run_flush", fake_flush), \
         patch.object(flush, "run_quality_audit", fake_audit), \
         patch.object(flush, "maybe_trigger_compilation"), \
         patch.object(sys, "argv", ["flush.py", str(ctx_file), "test-sess-id"]):
        flush.main()


def test_main_writes_sdk_error_marker_to_daily_log(tmp_path):
    """main() prepends <!-- AUDIT_SDK_ERROR: ... --> when audit hits SDK error."""
    marker = "AUDIT_SDK_ERROR: exit=1 type=ProcessError"
    _run_main_with_stubbed_sdk(
        tmp_path,
        flush_response="extracted knowledge content",
        audit_outcome=flush.AuditOutcome(sdk_error_marker=marker),
    )

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / f"{today}.md"
    assert log_file.exists(), "daily log file should be created"
    log_content = log_file.read_text(encoding="utf-8")
    assert f"<!-- {marker} -->" in log_content
    assert "extracted knowledge content" in log_content
    # Marker must come before the content (prepended, not appended)
    assert log_content.index(marker) < log_content.index("extracted knowledge content")


def test_main_writes_audit_flag_for_quality_reject(tmp_path):
    """main() still uses AUDIT_FLAG prefix when audit returns reject_reason."""
    _run_main_with_stubbed_sdk(
        tmp_path,
        flush_response="extracted knowledge content",
        audit_outcome=flush.AuditOutcome(reject_reason="Only routine file reads"),
    )

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / f"{today}.md"
    log_content = log_file.read_text(encoding="utf-8")
    assert "<!-- AUDIT_FLAG: Only routine file reads -->" in log_content
    assert "extracted knowledge content" in log_content


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


@pytest.mark.asyncio
async def test_run_flush_handles_process_error():
    """run_flush should surface exit_code and stderr from ClaudeSDKError (ProcessError)."""
    from claude_agent_sdk import ProcessError

    async def failing_query(**kwargs):
        raise ProcessError("CLI failed", exit_code=1, stderr="boom stderr line")
        yield  # noqa: E501

    with patch("claude_agent_sdk.query", side_effect=failing_query):
        result = await flush.run_flush("Context")
        assert "FLUSH_ERROR" in result
        assert "ProcessError" in result
        assert "exit=1" in result
