"""Query the knowledge base using index-guided retrieval.

Usage:
    uv run python query.py "How should I handle auth redirects?"
    uv run python query.py "What patterns do I use?" --file-back
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from config import KNOWLEDGE_DIR, QA_DIR, now_iso
from utils import load_state, read_all_wiki_content, save_state

ROOT_DIR = Path(__file__).resolve().parent.parent


async def run_query(question: str, file_back: bool = False) -> str:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    wiki_content = read_all_wiki_content()

    tools = ["Read", "Glob", "Grep"]
    if file_back:
        tools.extend(["Write", "Edit"])

    file_back_instructions = ""
    if file_back:
        timestamp = now_iso()
        file_back_instructions = f"""

## File Back Instructions

After answering, do the following:
1. Create a Q&A article at {QA_DIR}/ with the filename being a slugified version
   of the question
2. Use the Q&A article format from the schema (frontmatter with title, question,
   consulted articles, filed date)
3. Update {KNOWLEDGE_DIR / 'index.md'} with a new row
4. Append to {KNOWLEDGE_DIR / 'log.md'}:
   ## [{timestamp}] query (filed) | question summary
   - Question: {question}
   - Consulted: [[list of articles read]]
   - Filed to: [[qa/article-name]]
"""

    prompt = f"""You are a knowledge base query engine. Answer the user's question by
consulting the knowledge base below.

## How to Answer

1. Read the INDEX section first - it lists every article with a one-line summary
2. Identify 3-10 articles that are relevant to the question
3. Read those articles carefully (they're included below)
4. Synthesize a clear, thorough answer
5. Cite your sources using [[wikilinks]]
6. If the knowledge base doesn't contain relevant information, say so honestly

## Knowledge Base

{wiki_content}

## Question

{question}
{file_back_instructions}"""

    answer = ""

    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                cwd=str(ROOT_DIR),
                system_prompt={"type": "preset", "preset": "claude_code"},
                allowed_tools=tools,
                permission_mode="acceptEdits" if file_back else None,
                max_turns=15,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        answer += block.text
            elif isinstance(message, ResultMessage):
                pass
    except Exception as e:
        answer = f"Error querying knowledge base: {e}"

    state = load_state()
    state["query_count"] = state.get("query_count", 0) + 1
    save_state(state)

    return answer


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Query the personal knowledge base")
    parser.add_argument("question", help="The question to ask")
    parser.add_argument("--file-back", action="store_true", help="File the answer back as Q&A")
    args = parser.parse_args()

    print(f"Question: {args.question}")
    print(f"File back: {'yes' if args.file_back else 'no'}")
    print("-" * 60)

    answer = asyncio.run(run_query(args.question, file_back=args.file_back))
    print(answer)

    if args.file_back:
        print("\n" + "-" * 60)
        qa_count = len(list(QA_DIR.glob("*.md"))) if QA_DIR.exists() else 0
        print(f"Answer filed to knowledge/qa/ ({qa_count} Q&A articles total)")


if __name__ == "__main__":
    main()
