---
title: "File-Based Input to Bypass Shell Escaping"
aliases: [body-file, stdin input, shell escaping workaround, file-based arguments]
tags: [devtools, shell, debugging, workflow]
category: "devtools"
sources:
  - "raw/gh-cli-windows-bash-workaround.md"
created: 2026-04-13
updated: 2026-04-13
---

# File-Based Input to Bypass Shell Escaping

**Context:** When passing complex text (containing backticks, quotes, parentheses, markdown) as arguments to CLI tools — especially across shell boundaries on Windows (bash → cmd.exe).

**Problem:** Special characters in CLI arguments get interpreted by the shell before reaching the target program. On Windows with multiple shell layers (bash calling cmd.exe, or bash calling a Windows executable), escaping rules compound — what bash requires contradicts what cmd.exe expects, producing mangled or rejected arguments.

**Lesson:** When text contains special characters, bypass the argument parser entirely by writing to a temp file and using the tool's file-input flag (`--body-file`, `--input-file`, stdin). This eliminates all escaping issues regardless of shell, platform, or nesting depth.

## Key Points

- CLI arguments pass through the shell's parser, which interprets `$`, `` ` ``, `"`, `'`, `()`, `{}` and other special characters
- On Windows with bash, two parsers run in sequence (bash then Windows), each with different escaping rules — no single quoting strategy satisfies both
- `--body-file` (gh CLI), `--input` (many tools), and stdin (`< file` or `| pipe`) all bypass argument parsing entirely
- The file-based approach works identically across platforms — no platform-specific escaping logic needed
- Always prefer `--body-file` over `--body` for `gh` on Windows; always prefer stdin over `-p "prompt"` for `claude` on Windows

## Details

Shell escaping is a solved problem in theory but a recurring source of bugs in practice, especially on Windows where multiple shell layers coexist. A markdown comment containing backticks (`` ` ``), dollar signs (`$`), and quotes is valid text content, but each of these characters triggers special handling in bash and/or cmd.exe.

The specific case that motivated this article was `gh issue comment --body 'text with backticks'` in Claude Code on Windows. The backticks inside the body text were interpreted by bash as command substitution, the quotes conflicted between bash and the Windows process, and no combination of escaping produced the correct result through both shell layers.

The solution is architectural, not syntactic: don't pass the text through any shell parser. Write the content to a temporary file, then pass the file path as the argument:

```bash
# Write content to temp file (no escaping needed inside heredoc)
cat > /tmp/comment.txt << 'EOF'
Comment with `backticks`, $variables, and "quotes"
EOF

# Pass the file path — only the path goes through the shell
gh issue comment 1 --repo Owner/Repo --body-file /tmp/comment.txt
```

This pattern generalizes beyond `gh`. The `claude -p` CLI has the same issue with large or complex prompts — the fix is `subprocess.run([...], input=prompt, text=True)` which pipes through stdin. `curl` has `--data-binary @file`. `jq` reads from stdin by default. Any well-designed CLI tool offers a file-based or stdin-based input path precisely because shell escaping is fundamentally unreliable for complex content.

The key insight is that this is not a quoting problem to solve — it's an architecture problem to avoid. The moment you find yourself writing nested escape sequences, switch to file-based input. The temp file costs nothing, the code becomes readable, and the behavior is deterministic across all platforms.

## Related Concepts

- [[concepts/gh-cli-bash-path-windows]] - The companion PATH issue that must also be solved for gh to work in bash on Windows
- [[concepts/windows-cli-arg-length-limit]] - Another case where file/stdin input is the fix: argument length limits bypass via stdin
- [[concepts/python-duck-typing-silent-failures]] - Same failure pattern: shell escaping bugs often manifest as garbled output rather than clear errors
