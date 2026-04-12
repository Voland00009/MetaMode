"""Tests for lint.py — knowledge base health checks."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import utils
import lint


def _patch_dirs(tmp_path):
    """Helper: create knowledge dir structure and return patch context managers."""
    knowledge_dir = tmp_path / "knowledge"
    concepts_dir = knowledge_dir / "concepts"
    connections_dir = knowledge_dir / "connections"
    qa_dir = knowledge_dir / "qa"
    concepts_dir.mkdir(parents=True)
    return knowledge_dir, concepts_dir, connections_dir, qa_dir


def test_check_broken_links(tmp_path):
    """Should detect wikilinks pointing to non-existent articles."""
    knowledge_dir, concepts_dir, connections_dir, qa_dir = _patch_dirs(tmp_path)

    (concepts_dir / "real-article.md").write_text(
        "---\ntitle: Real\n---\nSee [[concepts/nonexistent]]",
        encoding="utf-8",
    )

    with patch.object(utils, "KNOWLEDGE_DIR", knowledge_dir), \
         patch.object(utils, "CONCEPTS_DIR", concepts_dir), \
         patch.object(utils, "CONNECTIONS_DIR", connections_dir), \
         patch.object(utils, "QA_DIR", qa_dir), \
         patch.object(lint, "KNOWLEDGE_DIR", knowledge_dir):
        issues = lint.check_broken_links()
        assert len(issues) == 1
        assert issues[0]["check"] == "broken_link"
        assert "nonexistent" in issues[0]["detail"]


def test_check_sparse_articles(tmp_path):
    """Should detect articles with fewer than 200 words."""
    knowledge_dir, concepts_dir, connections_dir, qa_dir = _patch_dirs(tmp_path)

    (concepts_dir / "short.md").write_text(
        "---\ntitle: Short\n---\nJust a few words here.",
        encoding="utf-8",
    )

    with patch.object(utils, "KNOWLEDGE_DIR", knowledge_dir), \
         patch.object(utils, "CONCEPTS_DIR", concepts_dir), \
         patch.object(utils, "CONNECTIONS_DIR", connections_dir), \
         patch.object(utils, "QA_DIR", qa_dir), \
         patch.object(lint, "KNOWLEDGE_DIR", knowledge_dir):
        issues = lint.check_sparse_articles()
        assert len(issues) == 1
        assert issues[0]["check"] == "sparse_article"


def test_check_orphan_sources(tmp_path):
    """Should detect daily logs that haven't been compiled."""
    daily_dir = tmp_path / "daily"
    daily_dir.mkdir()
    (daily_dir / "2026-04-10.md").write_text("# Session", encoding="utf-8")

    state_file = tmp_path / "state.json"

    with patch.object(utils, "DAILY_DIR", daily_dir), \
         patch.object(utils, "STATE_FILE", state_file):
        issues = lint.check_orphan_sources()
        assert len(issues) == 1
        assert issues[0]["check"] == "orphan_source"


def test_generate_report():
    """generate_report should format issues into a readable report."""
    issues = [
        {"severity": "error", "check": "broken_link", "file": "concepts/x.md", "detail": "broken"},
        {"severity": "warning", "check": "orphan_page", "file": "concepts/y.md", "detail": "orphan"},
    ]
    report = lint.generate_report(issues)
    assert "Total issues:** 2" in report
    assert "Errors" in report
    assert "Warnings" in report
