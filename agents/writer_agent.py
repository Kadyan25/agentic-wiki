import os
import re
import datetime
from .utils import call_ai

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")


def _slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text[:60]


def run(query: str, context: dict) -> dict:
    new_summary = context.get("summarizer", {}).get("output", "")
    today = datetime.date.today().isoformat()

    meta = call_ai(
        "You extract metadata from a query. Reply with exactly two lines:\n"
        "TITLE: <concise topic title, title case, 2-5 words>\n"
        "TAGS: <3-5 comma-separated lowercase tags>",
        f"Query: {query}",
        max_tokens=60,
    )

    title = query.strip().title()
    tags = "ai, knowledge"
    for line in meta.splitlines():
        if line.startswith("TITLE:"):
            title = line[6:].strip()
        elif line.startswith("TAGS:"):
            tags = line[5:].strip()

    filename = _slug(title) + ".md"
    filepath = os.path.join(KNOWLEDGE_DIR, filename)

    created_date = today
    is_update = os.path.exists(filepath)

    if is_update:
        with open(filepath, "r", encoding="utf-8") as f:
            existing = f.read()

        match = re.search(r"\*\*Created\*\*:\s*(\S+)", existing)
        if match:
            created_date = match.group(1)

        # Merge existing note with new summary instead of overwriting
        summary = call_ai(
            "You are a knowledge base editor. You are given an existing note and new information "
            "about the same topic from a new query. Merge them into a single enriched summary. "
            "Keep all unique facts from both. Remove duplicates. Stay under 500 words. "
            "Return only the merged summary text, no headings.",
            f"Existing note:\n{existing}\n\nNew information:\n{new_summary}\n\nNew query: {query}",
            max_tokens=1200,
        )
    else:
        summary = new_summary

    content = f"""# {title}

**Created**: {created_date}
**Updated**: {today}
**Tags**: {tags}

## Summary
{summary}

## Key Points
- See summary above for detailed points.

## Related Topics

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    action = "updated" if is_update else "created"

    return {
        "output": f"Note '{filename}' {action}.",
        "files_read": [],
        "files_written": [filename],
        "filename": filename,
        "title": title,
    }
