---
name: wrapup
description: End-of-session wrap-up — summarizes the session and saves key memories. Trigger on "/wrapup" or when user says "wrap up", "save this session", "end of session", "session summary".
---

# Session Wrap-Up

Run this at the end of every session to capture what happened and commit it to long-term memory.

## Step 1: Review the Session

Look back through the entire conversation and identify:

- **Decisions made** — what was decided and why
- **Work completed** — what was built, fixed, configured, or shipped
- **Key learnings** — anything surprising or non-obvious that came up
- **Open threads** — anything left unfinished or to revisit next time
- **User preferences revealed** — any new feedback about how the user likes to work

## Step 2: Save Memories

Check the existing memory index and save or update memories as needed:

- **feedback** — any corrections or confirmed approaches from this session
- **project** — ongoing work, goals, deadlines, or context that future sessions need
- **user** — anything new learned about the user's role, preferences, or knowledge
- **reference** — any external resources, tools, or systems referenced

Rules:
- Don't duplicate existing memories — update them instead
- Don't save things derivable from code or git history
- Convert relative dates to absolute dates
- Include **Why:** and **How to apply:** for feedback and project memories

## Step 3: Write Session Summary

Create a markdown session summary with today's date. Keep it concise but complete.

Format:
```markdown
# Session Summary — YYYY-MM-DD

## What We Did
- Bullet points of key work completed

## Decisions Made
- Key decisions and their reasoning

## Key Learnings
- Non-obvious insights or discoveries

## Open Threads
- Anything to pick up next time

## Tools & Systems Touched
- List of tools, repos, services involved
```

## Step 4: Confirm

Tell the user:
- How many memories were saved/updated
- Any open threads to pick up next time

Keep it brief. No need to read back the full summary — just confirm it's done.

## Error Handling

- If there's nothing meaningful to save: just say so, don't force empty memories
