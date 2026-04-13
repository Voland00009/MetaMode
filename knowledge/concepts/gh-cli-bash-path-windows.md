---
title: "gh CLI PATH Resolution in Bash on Windows"
aliases: [gh not found, gh.exe bash path, github cli windows bash]
tags: [devtools, shell, github, debugging]
category: "devtools"
sources:
  - "raw/gh-cli-windows-bash-workaround.md"
  - "raw/gh-path-bashrc-fix.md"
created: 2026-04-13
updated: 2026-04-13
---

# gh CLI PATH Resolution in Bash on Windows

**Context:** When using `gh` (GitHub CLI) from Claude Code or any bash environment on Windows (Git Bash, MSYS2), where `gh.exe` is installed but not found.

**Problem:** `gh.exe` is installed in `C:\Program Files\GitHub CLI\`, which is in the Windows system PATH but not in the bash shell's PATH. Commands like `gh issue comment` fail with "command not found" even though `gh` works fine from PowerShell or cmd.exe.

**Lesson:** On Windows, bash environments (Git Bash, MSYS2) maintain their own PATH separate from the Windows system PATH. Either add the directory to `~/.bashrc` or use the full POSIX-style path (`"/c/Program Files/GitHub CLI/gh.exe"`) to invoke the tool.

## Key Points

- Claude Code on Windows uses bash (MSYS2/Git Bash), which has its own PATH independent of the Windows system PATH
- `gh.exe` installs to `C:\Program Files\GitHub CLI\` — a directory not included in bash's default PATH
- The naive workaround `cmd.exe /c "gh ..."` fails because cmd.exe doesn't propagate stdout/stderr back to bash correctly — only the Windows banner is visible
- Two reliable solutions: (1) full path `"/c/Program Files/GitHub CLI/gh.exe"` or (2) add to `~/.bashrc`: `export PATH="/c/Program Files/GitHub CLI:$PATH"`
- The `~/.bashrc` fix is permanent and applies to all future bash sessions — Claude Code sources `~/.bashrc` at bash startup
- Only the directory needs to be added to PATH, not the full path to the `.exe` — bash resolves executables within PATH directories automatically
- The pattern generalizes: any Windows program installed in `Program Files` (gh, node, etc.) can be fixed the same way by adding its directory to `~/.bashrc`

## Details

Windows maintains a system-wide PATH environment variable that cmd.exe and PowerShell inherit automatically. However, bash environments like Git Bash and MSYS2 construct their own PATH from a combination of built-in defaults and user configuration files (`~/.bashrc`, `~/.bash_profile`). The Windows `Program Files` directories are typically not included in this constructed PATH.

This creates a three-layer problem when trying to use `gh` from Claude Code:

**Layer 1: gh not in PATH.** The simplest failure — bash cannot find the `gh` command. This is solvable by using the full POSIX-style path: `"/c/Program Files/GitHub CLI/gh.exe"`. Note the POSIX path format (`/c/` instead of `C:\`) and the required quotes around the path (because of the space in "Program Files").

**Layer 2: cmd.exe /c swallows output.** The instinct to work around Layer 1 by calling `cmd.exe /c "gh ..."` fails differently. While cmd.exe can find `gh` (it uses the Windows PATH), it doesn't propagate stdout/stderr back to the calling bash process reliably. The user sees only the Windows version banner, not the command output. This makes the workaround worse than the original problem — it appears to work but produces no usable output.

**Layer 3: Cross-shell escaping.** Even if cmd.exe output worked, passing complex arguments (backticks, quotes, parentheses) through two shell layers (bash → cmd.exe) introduces escaping nightmares. Characters that are special in one shell but not the other get mangled in transit.

The permanent fix is adding the directory to `~/.bashrc`, which ensures `gh` is available in all bash sessions without needing full paths. Claude Code sources `~/.bashrc` when it starts a bash session, so the PATH modification takes effect automatically. This is particularly important for Claude Code hooks, which execute in bash and may need to call `gh` for GitHub operations.

The fix requires only the directory path in Unix style (`/c/Program Files/GitHub CLI`), not the full executable path — bash resolves `gh` to `gh.exe` within the directory automatically. If other Windows-installed programs exhibit the same "command not found" behavior (e.g., `node`, `dotnet`), their `Program Files` directories can be added to the same `~/.bashrc` file, building up a cumulative PATH that covers all cross-shell tools.

## Related Concepts

- [[concepts/file-based-input-shell-escaping]] - The companion fix for passing complex text to gh without escaping issues
- [[concepts/windows-cli-arg-length-limit]] - Another Windows shell boundary issue: argument length limits on CLI tools
- [[concepts/uv-run-directory-global-hooks]] - Global hooks also face PATH/cwd challenges that require explicit configuration
