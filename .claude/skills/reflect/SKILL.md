---
name: reflect
description: Structured end-of-session reflection — captures what you learned, what surprised you, what to do differently
allowed-tools: Read Write Edit
---

# /reflect — Session Reflection

Guide the user through a structured reflection at the end of a session. This captures high-quality knowledge that auto-flush might miss.

## Process

Ask these 4 questions one at a time, waiting for the user's answer before proceeding:

1. **What did you learn today?** — New facts, patterns, or concepts discovered in this session.
2. **What surprised you?** — Anything unexpected, counter-intuitive, or that changed your mental model.
3. **What would you do differently?** — Mistakes, wrong turns, or approaches you'd change next time.
4. **What should you remember for next time?** — Action items, gotchas, or context for future sessions.

## After all 4 answers

Compile the user's answers into a structured daily log entry and append it to today's daily log at `daily/YYYY-MM-DD.md`.

Use this format:

```
### Reflection (HH:MM)

**Learned:**
- [compiled from answer 1]

**Surprised:**
- [compiled from answer 2]

**Do Differently:**
- [compiled from answer 3]

**Remember:**
- [compiled from answer 4]
```

Create the daily log file if it doesn't exist. Use the same header format as other daily log entries:
```
# Daily Log: YYYY-MM-DD

## Sessions

## Memory Maintenance
```

After writing, confirm: "Reflection saved to daily/YYYY-MM-DD.md"
