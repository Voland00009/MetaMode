"""Memory flush — extracts knowledge from conversation context via Claude Agent SDK.

Spawned by session_end.py or pre_compact.py as a background process.

Usage:
    uv run python flush.py <context_file.md> <session_id>
"""

from __future__ import annotations

import os
os.environ["CLAUDE_INVOKED_BY"] = "memory_flush"

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from config import build_agent_options, now_local  # noqa: E402

DAILY_DIR = ROOT / "daily"
SCRIPTS_DIR = ROOT / "scripts"
STATE_FILE = SCRIPTS_DIR / "last-flush.json"
LOG_FILE = SCRIPTS_DIR / "flush.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def load_flush_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_flush_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state), encoding="utf-8")


def append_to_daily_log(content: str, section: str = "Session") -> None:
    today = now_local()
    log_path = DAILY_DIR / f"{today.strftime('%Y-%m-%d')}.md"

    if not log_path.exists():
        DAILY_DIR.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"# Daily Log: {today.strftime('%Y-%m-%d')}\n\n## Sessions\n\n## Memory Maintenance\n\n",
            encoding="utf-8",
        )

    time_str = today.strftime("%H:%M")
    entry = f"### {section} ({time_str})\n\n{content}\n\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


async def run_flush(context: str) -> str:
    """Use Claude Agent SDK to extract knowledge from conversation context."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeSDKError,
        ResultMessage,
        TextBlock,
        query,
    )

    prompt = f"""Review the conversation context below and respond with a concise summary
of important items that should be preserved in the daily log.
Do NOT use any tools - just return plain text.

Format your response as a structured daily log entry with these sections:

**Context:** [One line about what the user was working on]

**Key Exchanges:**
- [Important Q&A or discussions]

**Decisions Made:**
- [Any decisions with rationale]

**Lessons Learned:**
- [Gotchas, patterns, or insights discovered]

**Action Items:**
- [Follow-ups or TODOs mentioned]

Skip anything that is:
- Routine tool calls or file reads
- Content that's trivial or obvious
- Trivial back-and-forth or clarification exchanges

Only include sections that have actual content. If nothing is worth saving,
respond with exactly: FLUSH_OK

## Conversation Context

{context}"""

    response = ""

    try:
        async for message in query(
            prompt=prompt,
            options=build_agent_options(
                cwd=str(ROOT),
                allowed_tools=[],
                max_turns=2,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response += block.text
            elif isinstance(message, ResultMessage):
                if message.total_cost_usd:
                    _accumulate_cost(message.total_cost_usd)
    except ClaudeSDKError as e:
        import traceback
        stderr_text = getattr(e, "stderr", None) or ""
        exit_code = getattr(e, "exit_code", None)
        logging.error(
            "Agent SDK error (exit=%s): %s\nstderr: %s\n%s",
            exit_code, e, stderr_text, traceback.format_exc(),
        )
        response = f"FLUSH_ERROR: {type(e).__name__} (exit={exit_code}): {e}"
        if stderr_text:
            for line in str(stderr_text).splitlines():
                logging.error("  SDK stderr: %s", line)
    except Exception as e:
        import traceback
        logging.error("Agent SDK error: %s\n%s", e, traceback.format_exc())
        response = f"FLUSH_ERROR: {type(e).__name__}: {e}"

    return response


def _accumulate_cost(cost_usd: float) -> None:
    """Add cost to the main state.json (shared with compile/query)."""
    from utils import load_state, save_state
    state = load_state()
    state["total_cost"] = state.get("total_cost", 0.0) + cost_usd
    save_state(state)


COMPILE_AFTER_HOUR = 18
AUDIT_FLAG = "<!-- AUDIT_FLAG:"


class AuditOutcome(NamedTuple):
    """Result of `run_quality_audit`.

    Fields are mutually exclusive:
    - both None → audit passed, quality OK
    - `reject_reason` set → audit flagged content as low-quality
    - `sdk_error_marker` set → audit itself failed (SDK/runtime error);
      content is still saved to preserve the never-lose-data policy.
    """

    reject_reason: str | None = None
    sdk_error_marker: str | None = None


async def run_quality_audit(content: str) -> AuditOutcome:
    """Pass 2: Quick LLM check — does the extracted content contain junk?

    Returns an `AuditOutcome` describing the audit result.
    The caller marks the entry with an HTML comment but NEVER deletes it.
    """
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeSDKError,
        ResultMessage,
        TextBlock,
        query,
    )

    audit_prompt = f"""You are a quality auditor for a personal knowledge base.
Below is content that was auto-extracted from a Claude Code session.

Your job: decide if this content is WORTH KEEPING in a daily log that will later
be compiled into wiki articles.

## Content to audit

{content}

## Quality criteria — mark as LOW quality if ALL of these are true:
1. No concrete lessons learned (just "we did X, then Y")
2. No decisions with rationale
3. No reusable patterns or gotchas
4. Only routine operations (file reads, installs, config changes)

## IMPORTANT
- Be CONSERVATIVE. When in doubt, say QUALITY_OK.
- Most content IS worth keeping. Only flag obvious junk.
- A session that records a single real decision or lesson = KEEP.

## Response format
If quality is OK: respond with exactly QUALITY_OK
If low quality: respond with AUDIT_REJECT: <one-line reason>

Respond with ONLY one of these two formats, nothing else."""

    response = ""
    try:
        async for message in query(
            prompt=audit_prompt,
            options=build_agent_options(
                cwd=str(ROOT),
                allowed_tools=[],
                max_turns=1,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response += block.text
            elif isinstance(message, ResultMessage):
                if message.total_cost_usd:
                    _accumulate_cost(message.total_cost_usd)
    except ClaudeSDKError as e:
        import traceback
        stderr_text = getattr(e, "stderr", None) or ""
        exit_code = getattr(e, "exit_code", None)
        logging.error(
            "Quality audit SDK error (exit=%s): %s\nstderr: %s\n%s",
            exit_code, e, stderr_text, traceback.format_exc(),
        )
        if stderr_text:
            for line in str(stderr_text).splitlines():
                logging.error("  SDK stderr: %s", line)
        marker = f"AUDIT_SDK_ERROR: exit={exit_code} type={type(e).__name__}"
        return AuditOutcome(sdk_error_marker=marker)
    except Exception as e:
        import traceback
        logging.error("Quality audit error: %s\n%s", e, traceback.format_exc())
        marker = f"AUDIT_SDK_ERROR: exit=None type={type(e).__name__}"
        return AuditOutcome(sdk_error_marker=marker)

    response = response.strip()
    if response.startswith("AUDIT_REJECT:"):
        reason = response[len("AUDIT_REJECT:"):].strip()
        return AuditOutcome(reject_reason=reason)
    return AuditOutcome()


def maybe_trigger_compilation() -> None:
    """If past compile hour and today's log changed, spawn compile.py."""
    import subprocess as _sp

    now = now_local()
    if now.hour < COMPILE_AFTER_HOUR:
        return

    today_log = f"{now.strftime('%Y-%m-%d')}.md"
    compile_state_file = SCRIPTS_DIR / "state.json"
    if compile_state_file.exists():
        try:
            compile_state = json.loads(compile_state_file.read_text(encoding="utf-8"))
            ingested = compile_state.get("ingested", {})
            if today_log in ingested:
                from hashlib import sha256
                log_path = DAILY_DIR / today_log
                if log_path.exists():
                    current_hash = sha256(log_path.read_bytes()).hexdigest()[:16]
                    if ingested[today_log].get("hash") == current_hash:
                        return
        except (json.JSONDecodeError, OSError):
            pass

    compile_script = SCRIPTS_DIR / "compile.py"
    if not compile_script.exists():
        return

    logging.info("End-of-day compilation triggered (after %d:00)", COMPILE_AFTER_HOUR)

    cmd = ["uv", "run", "--directory", str(ROOT), "python", str(compile_script)]

    kwargs: dict = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = _sp.CREATE_NO_WINDOW
    else:
        kwargs["start_new_session"] = True

    try:
        log_handle = open(str(SCRIPTS_DIR / "compile.log"), "a")
        try:
            _sp.Popen(cmd, stdout=log_handle, stderr=_sp.STDOUT, cwd=str(ROOT), **kwargs)
        except Exception as e:
            log_handle.close()
            logging.error("Failed to spawn compile.py: %s", e)
    except OSError as e:
        logging.error("Failed to open compile.log: %s", e)


def main():
    if len(sys.argv) < 3:
        logging.error("Usage: %s <context_file.md> <session_id>", sys.argv[0])
        sys.exit(1)

    context_file = Path(sys.argv[1])
    session_id = sys.argv[2]

    logging.info("flush.py started for session %s, context: %s", session_id, context_file)

    if not context_file.exists():
        logging.error("Context file not found: %s", context_file)
        return

    # Dedup: skip if same session flushed within 60 seconds
    state = load_flush_state()
    if (
        state.get("session_id") == session_id
        and time.time() - state.get("timestamp", 0) < 60
    ):
        logging.info("Skipping duplicate flush for session %s", session_id)
        context_file.unlink(missing_ok=True)
        return

    context = context_file.read_text(encoding="utf-8").strip()
    if not context:
        logging.info("Context file is empty, skipping")
        context_file.unlink(missing_ok=True)
        return

    logging.info("Flushing session %s: %d chars", session_id, len(context))

    response = asyncio.run(run_flush(context))

    if "FLUSH_OK" in response:
        logging.info("Result: FLUSH_OK")
        append_to_daily_log("FLUSH_OK - Nothing worth saving from this session", "Memory Flush")
    elif "FLUSH_ERROR" in response:
        logging.error("Result: %s", response)
        append_to_daily_log(response, "Memory Flush")
    else:
        # Pass 2: Quality audit — check if extracted content is worth keeping
        outcome = asyncio.run(run_quality_audit(response))
        if outcome.sdk_error_marker:
            logging.info(
                "Audit SDK-failed, content saved with marker (%d chars)", len(response)
            )
            flagged_content = f"<!-- {outcome.sdk_error_marker} -->\n{response}"
            append_to_daily_log(flagged_content, f"Session {session_id[:8]}")
        elif outcome.reject_reason:
            logging.info(
                "Audit flagged (%d chars): %s", len(response), outcome.reject_reason
            )
            flagged_content = f"{AUDIT_FLAG} {outcome.reject_reason} -->\n{response}"
            append_to_daily_log(flagged_content, f"Session {session_id[:8]}")
        else:
            logging.info("Result: saved to daily log (%d chars)", len(response))
            append_to_daily_log(response, f"Session {session_id[:8]}")

    save_flush_state({"session_id": session_id, "timestamp": time.time()})
    context_file.unlink(missing_ok=True)
    maybe_trigger_compilation()
    logging.info("Flush complete for session %s", session_id)


if __name__ == "__main__":
    main()
