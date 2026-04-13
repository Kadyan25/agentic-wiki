import os
import re
from .utils import call_ai

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")


def run(query: str, context: dict) -> dict:
    writer_out = context.get("writer", {})
    filename = writer_out.get("filename", "")
    summary = context.get("summarizer", {}).get("output", "")

    note_content = ""
    if filename:
        path = os.path.join(KNOWLEDGE_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                note_content = f.read()

    # Check for broken [[links]]
    existing_files = {f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(".md")}
    found_links = re.findall(r"\[\[([^\]]+)\]\]", note_content)
    broken_links = []
    for link in found_links:
        slug = link.lower().replace(" ", "-") + ".md"
        if slug not in existing_files:
            broken_links.append(link)

    score_response = call_ai(
        "You are a quality validator for a knowledge base. "
        "Given a query, a summary, and the written note, score the quality from 1-10. "
        "Reply with exactly:\nSCORE: <number>\nISSUES: <comma-separated issues or 'none'>\n"
        "SUGGESTIONS: <one brief suggestion or 'none'>",
        f"Query: {query}\n\nSummary:\n{summary}\n\nNote:\n{note_content}",
        max_tokens=150,
    )

    score = 7
    issues = []
    suggestions = []

    for line in score_response.splitlines():
        if line.startswith("SCORE:"):
            try:
                score = int(line[6:].strip())
            except ValueError:
                pass
        elif line.startswith("ISSUES:"):
            raw = line[7:].strip()
            if raw.lower() != "none":
                issues = [i.strip() for i in raw.split(",")]
        elif line.startswith("SUGGESTIONS:"):
            raw = line[12:].strip()
            if raw.lower() != "none":
                suggestions = [raw]

    if broken_links:
        issues.append(f"Broken links: {', '.join(broken_links)}")

    return {
        "output": f"Validation complete. Score: {score}/10",
        "files_read": [filename] if filename else [],
        "files_written": [],
        "score": score,
        "issues": issues,
        "suggestions": suggestions,
    }
