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


def test_save_appends_to_existing_log(tmp_path):
    """Should append to existing daily log, not overwrite."""
    from user_prompt_submit import write_quick_save

    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = daily_dir / f"{today}.md"
    log_file.write_text("# Existing content\n\n", encoding="utf-8")

    with patch("user_prompt_submit.DAILY_DIR", daily_dir):
        write_quick_save("First save")
        write_quick_save("Second save")

    content = log_file.read_text(encoding="utf-8")
    assert "Existing content" in content
    assert "First save" in content
    assert "Second save" in content
