# Setup Guide

Step-by-step installation for macOS, Linux, and Windows.

---

## Prerequisites

| Tool | Check | Install |
|------|-------|---------|
| **Python 3.12+** | `python --version` | [python.org](https://www.python.org/downloads/) |
| **uv** | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Claude Code** | `claude --version` | `npm install -g @anthropic-ai/claude-code` |
| **Claude Max subscription** | — | Required for $0 Agent SDK calls |

---

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/Voland00009/MetaMode.git ~/Dev/MetaMode
cd ~/Dev/MetaMode
```

> **Windows:** use `C:/Users/YOU/Dev/MetaMode` instead of `~/Dev/MetaMode`.

### Step 2: Install dependencies

```bash
uv sync
```

You should see `Resolved X packages in ...` — that means it worked.

### Step 3: Configure hooks

Hooks are **global** — they fire in every Claude Code session, from any project. This is how MetaMode captures all your sessions automatically.

Edit `~/.claude/settings.json` (create it if it doesn't exist):

**macOS / Linux:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "uv run --directory ~/Dev/MetaMode python hooks/session_start.py"
      }
    ],
    "SessionEnd": [
      {
        "type": "command",
        "command": "uv run --directory ~/Dev/MetaMode python hooks/session_end.py"
      }
    ],
    "PreCompact": [
      {
        "type": "command",
        "command": "uv run --directory ~/Dev/MetaMode python hooks/pre_compact.py"
      }
    ],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "uv run --directory ~/Dev/MetaMode python hooks/user_prompt_submit.py"
      }
    ]
  }
}
```

**Windows (PowerShell or Git Bash):**

Same structure, but use Windows paths:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "uv run --directory C:/Users/YOU/Dev/MetaMode python hooks/session_start.py"
      }
    ],
    "SessionEnd": [
      {
        "type": "command",
        "command": "uv run --directory C:/Users/YOU/Dev/MetaMode python hooks/session_end.py"
      }
    ],
    "PreCompact": [
      {
        "type": "command",
        "command": "uv run --directory C:/Users/YOU/Dev/MetaMode python hooks/pre_compact.py"
      }
    ],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "uv run --directory C:/Users/YOU/Dev/MetaMode python hooks/user_prompt_submit.py"
      }
    ]
  }
}
```

> Replace `YOU` with your actual Windows username.

**Why `uv run --directory`?** This tells uv to resolve the virtual environment from the MetaMode directory, regardless of where you're running Claude Code. Without it, hooks would fail in other projects.

**Already have hooks?** Add the MetaMode entries to your existing arrays — multiple hooks per event are supported.

### Step 4: Verify installation

Run these commands from your MetaMode directory:

```bash
# Test session_start hook — should print JSON with "additionalContext"
uv run python hooks/session_start.py

# Test !save — should print "Saved to daily/..." on stderr
echo '{"type":"user","content":"!save Test note from setup verification"}' | uv run python hooks/user_prompt_submit.py
```

Then start a new Claude Code session anywhere. You should see MetaMode's context injected (wiki index, recent log). If the wiki is empty, you'll see the example content from `knowledge/index.md`.

### Step 5: Give other projects wiki access (optional)

By default, hooks inject wiki context into every session. But if you want Claude to *read* your wiki articles or *save* to the RAW inbox from another project, add a block to that project's `CLAUDE.md`.

See [Cross-Project Template](cross-project-template.md) for a copy-paste block.

---

## One-Command Setup (for Claude Code)

Paste this into Claude Code and let it do the setup for you:

```
Install MetaMode for me. Clone from https://github.com/Voland00009/MetaMode.git
to ~/Dev/MetaMode, run uv sync, then configure hooks in ~/.claude/settings.json
following docs/setup.md. Verify with a test run of session_start.py.
```

---

## Troubleshooting

### "uv: command not found"

Install uv:
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### "No module named claude_agent_sdk"

Run `uv sync` again from the MetaMode directory. The Agent SDK is declared in `pyproject.toml` and installed automatically.

### Hooks not firing

1. Check that `~/.claude/settings.json` exists and is valid JSON
2. Verify the path in hook commands points to your actual MetaMode directory
3. Run `claude /hooks` inside Claude Code to see registered hooks
4. Make sure hook commands use `uv run --directory` (not just `uv run`)

### Windows encoding issues

If you see garbled output or encoding errors, add this to your terminal profile:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

Hooks handle encoding internally (`sys.stdin.reconfigure(encoding="utf-8")`), but terminal display may still need this.

### "Permission denied" on macOS/Linux

Python scripts don't need `chmod +x` — they're invoked via `python`, not executed directly. If you get permission errors, check the directory permissions:

```bash
ls -la ~/Dev/MetaMode/hooks/
```

---

## Uninstall

1. Remove the MetaMode hook entries from `~/.claude/settings.json`
2. Delete the MetaMode directory: `rm -rf ~/Dev/MetaMode`
3. That's it — MetaMode makes no system-wide changes

Your daily logs and wiki articles are inside the MetaMode directory. Back them up before deleting if you want to keep them.
