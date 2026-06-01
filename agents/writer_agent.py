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


def _safe_title_from_query(query: str) -> str:
    """Fallback title — first 5 meaningful words of the query, title-cased."""
    words = [w for w in query.strip().split() if len(w) > 2][:5]
    return " ".join(words).title() or "Untitled Note"


def run(query: str, context: dict) -> dict:
    new_summary = context.get("summarizer", {}).get("output", "")

    # Skip writing if summarizer produced nothing useful
    if not new_summary or not new_summary.strip():
        return {
            "output": "Skipped — no summary to write.",
            "files_read": [], "files_written": [], "filename": "", "title": "",
        }

    today = datetime.date.today().isoformat()

    # Ensure knowledge dir exists
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

    # Use intake topics as title/tags if available — saves one LLM call
    intake_data = context.get("intake", {}).get("data", {})
    intake_topics = intake_data.get("key_topics", [])

    title = _safe_title_from_query(query)
    tags = "ai, knowledge"

    if intake_topics and intake_data.get("input_type") == "text_query":
        # Text queries only — intake topics reliably reflect the user's intent
        title = " ".join(intake_topics[:4]).title()
        tags = ", ".join(intake_topics[:5])
    else:
        # Documents, URLs, images, CSVs — LLM picks a better title from raw content
        try:
            meta = call_ai(
                "You extract metadata from a query. Reply with exactly two lines:\n"
                "TITLE: <concise topic title, title case, 2-5 words>\n"
                "TAGS: <3-5 comma-separated lowercase tags>",
                f"Query: {query[:200]}",
                max_tokens=60,
            )
            for line in meta.splitlines():
                if line.startswith("TITLE:"):
                    t = line[6:].strip()
                    if t:
                        title = t
                elif line.startswith("TAGS:"):
                    t = line[5:].strip()
                    if t:
                        tags = t
        except RuntimeError:
            pass  # use fallback title and tags

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

        # Merge existing note with new summary — fall back to new summary if merge fails
        try:
            summary = call_ai(
                "You are a knowledge base editor. You are given an existing note and new information "
                "about the same topic from a new query. Merge them into a single enriched summary. "
                "Keep all unique facts from both. Remove duplicates. Stay under 500 words. "
                "Return only the merged summary text, no headings.",
                f"Existing note:\n{existing}\n\nNew information:\n{new_summary}\n\nNew query: {query}",
                max_tokens=1200,
            )
        except RuntimeError:
            summary = new_summary  # use new summary as-is if merge fails
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

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        return {
            "output": f"Failed to write note: {e}",
            "files_read": [], "files_written": [], "filename": "", "title": "",
        }

    action = "updated" if is_update else "created"
    return {
        "output": f"Note '{filename}' {action}.",
        "files_read": [],
        "files_written": [filename],
        "filename": filename,
        "title": title,
    }
