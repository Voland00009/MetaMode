"""Tests for compile.py — daily log to wiki article compilation."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import utils
from utils import file_hash


def test_compile_determines_files_to_compile(tmp_path):
    """compile should identify new/changed daily logs for compilation."""
    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()
    (daily_dir / "2026-04-10.md").write_text("# Session 1\nContent here", encoding="utf-8")
    (daily_dir / "2026-04-11.md").write_text("# Session 2\nMore content", encoding="utf-8")

    state_file = tmp_path / "state.json"

    with patch.object(utils, "DAILY_DIR", daily_dir), \
         patch.object(utils, "STATE_FILE", state_file):
        files = utils.list_raw_files()
        assert len(files) == 2

        # With empty state, all files need compilation
        state = utils.load_state()
        to_compile = []
        for log_path in files:
            rel = log_path.name
            prev = state.get("ingested", {}).get(rel, {})
            if not prev or prev.get("hash") != file_hash(log_path):
                to_compile.append(log_path)
        assert len(to_compile) == 2


def test_compile_skips_unchanged(tmp_path):
    """compile should skip daily logs with unchanged hash."""
    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()
    log_file = daily_dir / "2026-04-10.md"
    log_file.write_text("# Session 1\nContent", encoding="utf-8")

    state = {
        "ingested": {
            "2026-04-10.md": {"hash": file_hash(log_file), "compiled_at": "now"}
        }
    }

    with patch.object(utils, "DAILY_DIR", daily_dir):
        files = utils.list_raw_files()
        to_compile = []
        for log_path in files:
            rel = log_path.name
            prev = state.get("ingested", {}).get(rel, {})
            if not prev or prev.get("hash") != file_hash(log_path):
                to_compile.append(log_path)
        assert len(to_compile) == 0


def test_compile_module_imports():
    """compile.py should be importable and have key functions."""
    import compile
    assert hasattr(compile, "compile_daily_log")
    assert hasattr(compile, "main")
