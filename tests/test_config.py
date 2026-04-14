"""Tests for scripts/config.py helpers."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import config


def test_build_agent_options_injects_strict_mcp_config():
    opts = config.build_agent_options(cwd="/tmp", max_turns=1)
    assert opts.extra_args.get("strict-mcp-config") is None
    assert "strict-mcp-config" in opts.extra_args


def test_build_agent_options_sets_stderr_callback_by_default():
    opts = config.build_agent_options()
    assert opts.stderr is config._sdk_stderr_handler

    def custom(line): pass
    opts2 = config.build_agent_options(stderr=custom)
    assert opts2.stderr is custom


def test_build_agent_options_preserves_caller_extra_args():
    opts = config.build_agent_options(extra_args={"debug-to-stderr": None})
    assert "strict-mcp-config" in opts.extra_args
    assert "debug-to-stderr" in opts.extra_args


def test_no_direct_ClaudeAgentOptions_calls_in_scripts():
    """Guard: only config.py may import ClaudeAgentOptions, ensuring
    build_agent_options is used everywhere else (preserves MCP isolation)."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    violations = []
    for py in scripts_dir.glob("*.py"):
        if py.name == "config.py":
            continue
        text = py.read_text(encoding="utf-8")
        if re.search(r"\bClaudeAgentOptions\s*\(", text):
            violations.append(py.name)
    assert not violations, (
        f"Direct ClaudeAgentOptions(...) calls found in: {violations}. "
        "Use build_agent_options() from config.py instead."
    )
