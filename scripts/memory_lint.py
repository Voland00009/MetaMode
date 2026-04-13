"""Lint Claude Code auto-memory for structural health.

Standalone opt-in script. Checks:
- MEMORY.md broken refs (index points to missing file)
- Orphan memory files (file exists but not in MEMORY.md)
- File count per project (warning if > 30)
- Total size per project (warning if > 100K)
- CLAUDE.md line count (global > 40, project > 50)

Usage:
    uv run python scripts/memory_lint.py
"""

from __future__ import annotations

import re
from pathlib import Path

from config import REPORTS_DIR, ROOT_DIR, STATE_FILE, now_iso, today_iso
from utils import load_state, save_state

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
GLOBAL_CLAUDEMD = Path.home() / ".claude" / "CLAUDE.md"
PROJECT_CLAUDEMD = ROOT_DIR / "CLAUDE.md"

FILE_COUNT_THRESHOLD = 30
TOTAL_SIZE_THRESHOLD = 100 * 1024  # 100 KB
GLOBAL_CLAUDEMD_LINE_THRESHOLD = 40
PROJECT_CLAUDEMD_LINE_THRESHOLD = 50


def _extract_md_links(index_text: str) -> list[str]:
    """Extract markdown link targets from MEMORY.md: [title](file.md)."""
    return re.findall(r"\]\(([^)]+\.md)\)", index_text)


def check_broken_refs(memory_dir: Path) -> list[dict]:
    """MEMORY.md references a file that doesn't exist."""
    index_path = memory_dir / "MEMORY.md"
    if not index_path.exists():
        return []
    index_text = index_path.read_text(encoding="utf-8")
    issues = []
    for ref in _extract_md_links(index_text):
        target = memory_dir / ref
        if not target.exists():
            issues.append({
                "severity": "error",
                "check": "memory_broken_ref",
                "file": f"{memory_dir.name}/{ref}",
                "detail": f"MEMORY.md links to `{ref}` but file does not exist",
            })
    return issues


def check_orphan_files(memory_dir: Path) -> list[dict]:
    """Memory file exists but is not referenced in MEMORY.md."""
    index_path = memory_dir / "MEMORY.md"
    if not index_path.exists():
        return []
    index_text = index_path.read_text(encoding="utf-8")
    referenced = set(_extract_md_links(index_text))
    issues = []
    for md_file in sorted(memory_dir.glob("*.md")):
        if md_file.name == "MEMORY.md":
            continue
        if md_file.name not in referenced:
            issues.append({
                "severity": "warning",
                "check": "memory_orphan_file",
                "file": f"{memory_dir.name}/{md_file.name}",
                "detail": f"`{md_file.name}` exists but is not referenced in MEMORY.md",
            })
    return issues


def check_file_count(memory_dir: Path) -> list[dict]:
    """Warn if too many memory files in one project."""
    md_files = [f for f in memory_dir.glob("*.md") if f.name != "MEMORY.md"]
    if len(md_files) > FILE_COUNT_THRESHOLD:
        return [{
            "severity": "warning",
            "check": "memory_file_count",
            "file": memory_dir.name,
            "detail": f"{len(md_files)} memory files (threshold: {FILE_COUNT_THRESHOLD})",
        }]
    return []


def check_total_size(memory_dir: Path) -> list[dict]:
    """Warn if total memory size exceeds threshold."""
    total = sum(f.stat().st_size for f in memory_dir.glob("*.md"))
    if total > TOTAL_SIZE_THRESHOLD:
        kb = total / 1024
        return [{
            "severity": "warning",
            "check": "memory_total_size",
            "file": memory_dir.name,
            "detail": f"Total memory size: {kb:.1f}K (threshold: {TOTAL_SIZE_THRESHOLD // 1024}K)",
        }]
    return []


def check_claudemd_lines() -> list[dict]:
    """Check CLAUDE.md line counts."""
    issues = []
    for path, label, threshold in [
        (GLOBAL_CLAUDEMD, "global ~/.claude/CLAUDE.md", GLOBAL_CLAUDEMD_LINE_THRESHOLD),
        (PROJECT_CLAUDEMD, "project CLAUDE.md", PROJECT_CLAUDEMD_LINE_THRESHOLD),
    ]:
        if path.exists():
            lines = len(path.read_text(encoding="utf-8").splitlines())
            if lines > threshold:
                issues.append({
                    "severity": "warning",
                    "check": "claudemd_line_count",
                    "file": label,
                    "detail": f"{lines} lines (threshold: {threshold})",
                })
    return issues


def discover_memory_dirs() -> list[Path]:
    """Find all memory/ dirs under ~/.claude/projects/."""
    dirs = []
    if CLAUDE_PROJECTS_DIR.exists():
        for project_dir in sorted(CLAUDE_PROJECTS_DIR.iterdir()):
            mem_dir = project_dir / "memory"
            if mem_dir.is_dir():
                dirs.append(mem_dir)
    return dirs


def run_memory_lint() -> list[dict]:
    """Run all memory checks across all projects. Returns list of issues."""
    all_issues: list[dict] = []

    memory_dirs = discover_memory_dirs()
    for mem_dir in memory_dirs:
        project_name = mem_dir.parent.name
        print(f"  Scanning: {project_name}")
        for check_fn in [check_broken_refs, check_orphan_files, check_file_count, check_total_size]:
            all_issues.extend(check_fn(mem_dir))

    print("  Checking: CLAUDE.md line counts...")
    all_issues.extend(check_claudemd_lines())

    return all_issues


def generate_report(all_issues: list[dict]) -> str:
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]

    lines = [
        f"# Memory Lint Report - {today_iso()}",
        "",
        f"**Total issues:** {len(all_issues)}",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        "",
    ]

    for severity, issues, marker in [
        ("Errors", errors, "x"),
        ("Warnings", warnings, "!"),
    ]:
        if issues:
            lines.append(f"## {severity}")
            lines.append("")
            for issue in issues:
                lines.append(f"- **[{marker}]** `{issue['file']}` - {issue['detail']}")
            lines.append("")

    if not all_issues:
        lines.append("All checks passed. Memory is healthy.")
        lines.append("")

    return "\n".join(lines)


def main():
    print("Running memory lint checks...")
    all_issues = run_memory_lint()

    report = generate_report(all_issues)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"memory-lint-{today_iso()}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {report_path}")

    state = load_state()
    state["last_memory_lint"] = now_iso()
    save_state(state)

    errors = sum(1 for i in all_issues if i["severity"] == "error")
    warnings = sum(1 for i in all_issues if i["severity"] == "warning")
    print(f"\nResults: {errors} errors, {warnings} warnings")

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    exit(main())
