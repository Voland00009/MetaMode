# NotebookLM Integration

MetaMode integrates with [Google NotebookLM](https://notebooklm.google.com/) for content generation and long-term session archival. This is optional — MetaMode works fully without it.

## What NotebookLM Adds

NotebookLM is Google's AI-powered research tool. When connected to MetaMode, it provides:

1. **AI Brain** — a searchable archive of all your session summaries. Ask questions like "what did I learn about testing last month?" and get answers across all sessions.
2. **Content generation** — podcasts, videos, slide decks, quizzes, reports from your knowledge base
3. **External brain for token savings** — offload context to NotebookLM instead of stuffing it into Claude's context window

## Setup

### 1. Install the CLI

```bash
python3 -m venv ~/.notebooklm-venv
source ~/.notebooklm-venv/bin/activate  # Windows: .notebooklm-venv\Scripts\activate
pip install "notebooklm-py[browser]"
playwright install chromium
```

### 2. Install the Skills

Copy the skills from MetaMode to your Claude Code skills directory:

```bash
# macOS/Linux
cp -r skills/notebooklm ~/.claude/SKILLS/notebooklm
cp -r skills/wrapup ~/.claude/SKILLS/wrapup

# Windows (PowerShell)
Copy-Item -Recurse skills\notebooklm $env:USERPROFILE\.claude\SKILLS\notebooklm
Copy-Item -Recurse skills\wrapup $env:USERPROFILE\.claude\SKILLS\wrapup
```

### 3. Authenticate

In Claude Code, say `/notebooklm` — the skill will guide you through browser-based Google authentication. You'll sign into your Google account and the skill will save the session cookies.

### 4. Create Your AI Brain

In Claude Code, say `/wrapup`. On first run, it will offer to create an "AI Brain" notebook — this is where all your session summaries go.

## Known Limitation: Cookie Expiration

**This is the most common issue.** Google cookies expire every 1-7 days. When you see "auth error" or "SID cookie missing", you need to re-authenticate:

1. In Claude Code, say `/notebooklm`
2. The skill will detect the expired cookies and re-run the login flow

**Why this can't be "fixed":** notebooklm-py is an unofficial API that uses browser automation (Playwright). Google does not offer a public API for NotebookLM, so browser cookies are the only authentication method. Google's security policy invalidates these cookies periodically. This is a deliberate Google security measure, not a bug.

## Use Cases

### 1. Session Archival (via /wrapup)
At the end of each session, `/wrapup` saves a structured summary to your AI Brain notebook. Over time, this builds a searchable archive of everything you've discussed with Claude.

**Why it matters:** Claude's auto-memory has a ~200-line limit and no search. NotebookLM has no practical limit and supports natural language queries.

### 2. Podcast Generation
Turn your daily logs or wiki articles into audio overviews:
```
/notebooklm
"Create a podcast from today's daily log summarizing what I learned"
```
Useful for review during commutes or exercise.

### 3. Study Materials
Generate quizzes and flashcards from your knowledge base:
```
"Generate a quiz from my MetaMode wiki articles about Python testing patterns"
```

### 4. Slide Decks from Knowledge
Turn accumulated knowledge into presentations:
```
"Create a slide deck about the debugging patterns from my last 5 sessions"
```

### 5. Cross-Session Research
Ask questions across all your archived sessions:
```
"What approaches have I tried for reducing API latency?"
```
NotebookLM searches all session summaries and synthesizes an answer.

### 6. Token Savings
Instead of loading full wiki content into Claude's context window (expensive per-turn), upload it to NotebookLM as a source. Then query NotebookLM from Claude for specific answers — Claude only receives the answer, not the full corpus.

## How the Pieces Fit Together

```
Claude Code session
    ↓ (auto, via hooks)
MetaMode daily logs + wiki articles
    ↓ (manual, via /wrapup)
NotebookLM AI Brain
    ↓ (on demand)
Podcasts, quizzes, reports, search
```

- **Hooks** capture automatically — you don't do anything
- **Wiki** compiles automatically after 18:00 or manually via `/compile`
- **NotebookLM** is triggered manually via `/wrapup` or `/notebooklm`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Auth error" / "SID missing" | Re-authenticate: `/notebooklm` → login flow |
| "notebooklm: command not found" | Install: `pip install "notebooklm-py[browser]"` in `~/.notebooklm-venv` |
| Generation stuck at "in_progress" | Wait (audio: 10-20min, video: 15-45min) or retry |
| "No notebook context" | Run `notebooklm use <id>` to select a notebook |
| Rate limit errors | Wait 5-10 minutes, then retry |
