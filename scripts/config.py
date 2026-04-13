"""Path constants and configuration for MetaMode knowledge base."""

import os
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# -- Paths --
ROOT_DIR = Path(__file__).resolve().parent.parent
DAILY_DIR = ROOT_DIR / "daily"
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
CONCEPTS_DIR = KNOWLEDGE_DIR / "concepts"
CONNECTIONS_DIR = KNOWLEDGE_DIR / "connections"
QA_DIR = KNOWLEDGE_DIR / "qa"
REPORTS_DIR = ROOT_DIR / "reports"
SCRIPTS_DIR = ROOT_DIR / "scripts"
HOOKS_DIR = ROOT_DIR / "hooks"
RAW_DIR = ROOT_DIR / "raw"
AGENTS_FILE = ROOT_DIR / "AGENTS.md"

INDEX_FILE = KNOWLEDGE_DIR / "index.md"
LOG_FILE = KNOWLEDGE_DIR / "log.md"
STATE_FILE = SCRIPTS_DIR / "state.json"

# -- Timezone --
# Override with METAMODE_TIMEZONE env var (e.g. "Europe/Moscow", "US/Pacific").
# Falls back to system local timezone if not set.
_tz_name = os.environ.get("METAMODE_TIMEZONE")
LOCAL_TZ: timezone | ZoneInfo = ZoneInfo(_tz_name) if _tz_name else datetime.now(timezone.utc).astimezone().tzinfo  # type: ignore[assignment]


def now_local() -> datetime:
    """Current datetime in the configured timezone."""
    return datetime.now(timezone.utc).astimezone(LOCAL_TZ)


def now_iso() -> str:
    """Current time in ISO 8601 format, configured timezone."""
    return now_local().isoformat(timespec="seconds")


def today_iso() -> str:
    """Current date as YYYY-MM-DD in configured timezone."""
    return now_local().strftime("%Y-%m-%d")
