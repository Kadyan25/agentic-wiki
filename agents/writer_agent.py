import os
import re
import datetime
from .utils import call_claude

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")


def _slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text[:60]


def run(query: str, context: dict) -> dict:
    summary = context.get("summarizer", {}).get("output", "")
    today = datetime.date.today().isoformat()

    # Ask Claude to extract a clean topic title and tags from the query
    meta = call_claude(
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

    # Check if file already exists (update vs create)
    created_date = today
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            existing = f.read()
        match = re.search(r"\*\*Created\*\*:\s*(\S+)", existing)
        if match:
            created_date = match.group(1)

    content = f"""# {title}

**Created**: {created_date}
**Updated**: {today}
**Tags**: {tags}

## Summary
{summary}

## Key Points
- See summary above for detailed points.

## Related Topics
<!-- [[links]] will be added by the Linker Agent -->
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    action = "updated" if os.path.exists(filepath) else "created"

    return {
        "output": f"Note '{filename}' {action}.",
        "files_read": [],
        "files_written": [filename],
        "filename": filename,
        "title": title,
    }
