---
title: "Windows Shell Boundaries ↔ Silent CLI Failures"
tags: [devtools, shell, debugging]
category: "devtools"
sources:
  - "raw/gh-cli-windows-bash-workaround.md"
  - "daily/2026-04-12.md"
created: 2026-04-13
---

# Windows Shell Boundaries ↔ Silent CLI Failures

**Context:** When building automation scripts or using CLI tools on Windows from bash environments (Git Bash, MSYS2, Claude Code), and encountering mysterious failures — missing output, garbled text, truncated commands.

**Problem:** Windows introduces multiple shell boundary problems that don't exist on Unix: separate PATH namespaces, argument length limits, cross-shell escaping, and stdout propagation failures. Each manifests silently — no error, just wrong results.

**Lesson:** Windows shell boundaries are a family of bugs, not isolated incidents. Recognizing them as a class lets you apply a consistent defensive strategy: use full paths, pass input via files/stdin, and avoid cross-shell invocation entirely.

## The Connection

The wiki documents three distinct Windows shell boundary failures discovered during MetaMode development:

1. **Argument length limit** ([[concepts/windows-cli-arg-length-limit]]): Windows `CreateProcess` limits CLI args to ~8K chars. `claude -p "long prompt"` silently truncates. Fix: pass via stdin.

2. **PATH namespace mismatch** ([[concepts/gh-cli-bash-path-windows]]): `gh.exe` is in the Windows PATH but not in bash's PATH. `gh` returns "command not found." Fix: full POSIX path or `~/.bashrc` export.

3. **Cross-shell escaping** ([[concepts/file-based-input-shell-escaping]]): Passing text with backticks/quotes through bash → cmd.exe mangles the content. Fix: write to temp file, use `--body-file`.

A fourth pattern — **cmd.exe stdout swallowing** — compounds the problem: `cmd.exe /c "gh ..."` runs but doesn't return output to bash, showing only the Windows banner. This makes the obvious workaround (use cmd.exe to find gh) worse than the original problem.

All four share a root cause: Windows was designed around a single-shell model (cmd.exe), and layering bash on top creates boundary mismatches at every interface point — PATH resolution, argument passing, output streams, and character escaping.

## Implications

1. **Assume bash on Windows is a foreign environment** — any tool installed "normally" on Windows (via MSI, winget, chocolatey) may not be visible from bash. Verify PATH or use full paths.
2. **Never shell out through cmd.exe from bash** — the output propagation is unreliable. Call Windows executables directly from bash using POSIX paths (`"/c/Program Files/Tool/tool.exe"`).
3. **Default to file-based input on Windows** — whether it's `--body-file`, stdin, or `input=` in subprocess. Argument passing is the weakest link in the cross-shell chain.
4. **Test automation on Windows specifically** — these bugs don't exist on macOS/Linux. Scripts that work perfectly on Unix may fail silently on Windows at any of these four boundary points.

## Related Concepts

- [[concepts/windows-cli-arg-length-limit]]
- [[concepts/gh-cli-bash-path-windows]]
- [[concepts/file-based-input-shell-escaping]]
- [[concepts/python-duck-typing-silent-failures]] - Same meta-pattern: silent corruption instead of clear errors
