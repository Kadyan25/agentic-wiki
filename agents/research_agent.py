import os

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")


def run(query: str, context: dict) -> dict:
    query_lower = query.lower()
    keywords = [w for w in query_lower.split() if len(w) > 3]

    files_read = []
    relevant_contents = []
    all_topics = []

    for fname in os.listdir(KNOWLEDGE_DIR):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(KNOWLEDGE_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        topic = fname.replace(".md", "").replace("-", " ")
        all_topics.append(topic)

        # Simple relevance: keyword match in filename or content
        score = sum(1 for kw in keywords if kw in content.lower() or kw in fname.lower())
        if score > 0:
            files_read.append(fname)
            relevant_contents.append(f"### {fname}\n{content}")

    # Identify gaps: topics mentioned in query not covered by existing files
    gaps = []
    for kw in keywords:
        covered = any(kw in t for t in all_topics)
        if not covered:
            gaps.append(kw)

    combined = "\n\n".join(relevant_contents) if relevant_contents else "No relevant notes found."

    return {
        "output": combined,
        "files_read": files_read,
        "files_written": [],
        "gaps": gaps,
    }
