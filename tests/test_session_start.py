"""Tests for session-start.py — context injection with pending review + compile reminder."""

import json
import sys
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))


def _fresh_import():
    """Force re-import of session_start to pick up patched module-level vars."""
    if "session_start" in sys.modules:
        del sys.modules["session_start"]
    import session_start
    return session_start


def test_build_context_includes_index(tmp_path):
    """Should include knowledge base index in context."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    index_file = knowledge_dir / "index.md"
    index_file.write_text(
        "| [[concepts/test]] | Test article | daily/2026-04-11.md | 2026-04-11 |",
        encoding="utf-8",
    )

    mod = _fresh_import()
    with patch.object(mod, "KNOWLEDGE_DIR", knowledge_dir), \
         patch.object(mod, "INDEX_FILE", index_file), \
         patch.object(mod, "DAILY_DIR", tmp_path / "daily"), \
         patch.object(mod, "PENDING_REVIEW_FILE", tmp_path / "nonexistent.md"), \
         patch.object(mod, "STATE_FILE", tmp_path / "state.json"):
        context = mod.build_context()
        assert "concepts/test" in context


def test_build_context_includes_pending_review(tmp_path):
    """MOD 4: Should include pending review items."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "index.md").write_text("Empty index", encoding="utf-8")

    pending = tmp_path / "pending-review.md"
    pending.write_text(
        "---\nsession_id: abc\nstatus: pending\n---\n\nImportant lesson here\n\n---\n",
        encoding="utf-8",
    )

    mod = _fresh_import()
    with patch.object(mod, "KNOWLEDGE_DIR", knowledge_dir), \
         patch.object(mod, "INDEX_FILE", knowledge_dir / "index.md"), \
         patch.object(mod, "DAILY_DIR", tmp_path / "daily"), \
         patch.object(mod, "PENDING_REVIEW_FILE", pending), \
         patch.object(mod, "STATE_FILE", tmp_path / "state.json"):
        context = mod.build_context()
        assert "Pending Review" in context
        assert "Important lesson here" in context


def test_build_context_compile_reminder(tmp_path):
    """MOD 6: Should remind about uncompiled logs."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "index.md").write_text("Empty", encoding="utf-8")

    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()
    for i in range(4):
        d = datetime.now() - timedelta(days=i)
        (daily_dir / f"{d.strftime('%Y-%m-%d')}.md").write_text(
            f"# Log {i}", encoding="utf-8"
        )

    state_file = tmp_path / "state.json"
    state_file.write_text('{"ingested": {}}', encoding="utf-8")

    mod = _fresh_import()
    with patch.object(mod, "KNOWLEDGE_DIR", knowledge_dir), \
         patch.object(mod, "INDEX_FILE", knowledge_dir / "index.md"), \
         patch.object(mod, "DAILY_DIR", daily_dir), \
         patch.object(mod, "PENDING_REVIEW_FILE", tmp_path / "nonexistent.md"), \
         patch.object(mod, "STATE_FILE", state_file):
        context = mod.build_context()
        assert "Compile Reminder" in context


def test_build_context_no_reminder_when_few_logs(tmp_path):
    """Should NOT show compile reminder when fewer than threshold logs."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "index.md").write_text("Empty", encoding="utf-8")

    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()
    # Only 1 log — below threshold
    today = datetime.now().strftime("%Y-%m-%d")
    (daily_dir / f"{today}.md").write_text("# Today", encoding="utf-8")

    state_file = tmp_path / "state.json"
    state_file.write_text('{"ingested": {}}', encoding="utf-8")

    mod = _fresh_import()
    with patch.object(mod, "KNOWLEDGE_DIR", knowledge_dir), \
         patch.object(mod, "INDEX_FILE", knowledge_dir / "index.md"), \
         patch.object(mod, "DAILY_DIR", daily_dir), \
         patch.object(mod, "PENDING_REVIEW_FILE", tmp_path / "nonexistent.md"), \
         patch.object(mod, "STATE_FILE", state_file):
        context = mod.build_context()
        assert "Compile Reminder" not in context


def test_main_outputs_json(tmp_path, capsys):
    """main() should output valid JSON with additionalContext."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "index.md").write_text("Test index", encoding="utf-8")

    mod = _fresh_import()
    with patch.object(mod, "KNOWLEDGE_DIR", knowledge_dir), \
         patch.object(mod, "INDEX_FILE", knowledge_dir / "index.md"), \
         patch.object(mod, "DAILY_DIR", tmp_path / "daily"), \
         patch.object(mod, "PENDING_REVIEW_FILE", tmp_path / "nonexistent.md"), \
         patch.object(mod, "STATE_FILE", tmp_path / "state.json"):
        mod.main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert "hookSpecificOutput" in output
    assert "additionalContext" in output["hookSpecificOutput"]
