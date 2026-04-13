---
title: "Windows CLI Argument Length Limit for LLM Tools"
aliases: [cli arg limit, stdin vs args, windows 8k limit]
tags: [python, devtools, shell, debugging]
category: "devtools"
sources:
  - "daily/2026-04-12.md"
  - "raw/gh-cli-windows-bash-workaround.md"
created: 2026-04-12
updated: 2026-04-13
---

# Windows CLI Argument Length Limit for LLM Tools

**Context:** When using `claude -p` or similar CLI tools in Python scripts on Windows, passing large prompts (e.g., full wiki content) as command-line arguments.

**Problem:** Windows has a ~8,192 character limit on command-line arguments. When a prompt includes full wiki content or other large payloads, the CLI call silently truncates or fails. This is invisible until the LLM produces garbled or incomplete responses.

**Lesson:** Pass large prompts via stdin (`input=prompt` in `subprocess.run()`) instead of as CLI arguments. Stdin has no practical length limit and works identically across platforms.

## Key Points

- Windows `cmd.exe` limits command-line arguments to ~8,192 characters; PowerShell has a higher but still finite limit
- `claude -p "very long prompt..."` breaks when the prompt includes embedded wiki content, daily logs, or other large text
- The fix: use `subprocess.run([...], input=prompt, text=True)` to pipe the prompt through stdin
- This is a general pattern — any CLI tool that accepts large text input should use stdin, not args
- The bug manifests silently: no error, just truncated input leading to wrong LLM output

## Details

During MetaMode Phase C verification, cross-project wiki access was tested by embedding full wiki content into a `claude -p` prompt. On Windows, this exceeded the ~8K character CLI argument limit, causing the subprocess call to fail. The fix was straightforward: instead of passing the prompt as a CLI argument, pipe it through stdin using the `input` parameter of `subprocess.run()`.

This is a well-known Windows limitation that affects many tools beyond Claude CLI. The `CreateProcess` Windows API has a hard limit on the combined length of all command-line arguments. Unix-like systems have much higher limits (typically 128K-2M), so the bug may not appear during development on macOS/Linux but surfaces in production on Windows.

The stdin approach is universally safer: it has no practical length limit, works identically across operating systems, and avoids shell escaping issues with special characters in the prompt text. For any script that passes user-generated or variable-length content to a CLI tool, stdin should be the default transport.

## Related Concepts

- [[concepts/claude-cli-json-output-variance]] - Another CLI integration gotcha: polymorphic output types
- [[concepts/python-duck-typing-silent-failures]] - Same failure pattern: silent corruption instead of a clear error
- [[concepts/file-based-input-shell-escaping]] - Generalized pattern: file/stdin input bypasses both length limits and escaping issues
- [[concepts/gh-cli-bash-path-windows]] - Another Windows shell boundary failure: PATH mismatch between bash and Windows
- [[connections/windows-shell-boundary-failures]] - This concept is part of a family of Windows shell boundary bugs
