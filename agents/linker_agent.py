import os
import re
import datetime

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")


def _topic_from_filename(fname: str) -> str:
    return fname.replace(".md", "").replace("-", " ").title()


def run(query: str, context: dict) -> dict:
    writer_out = context.get("writer", {})
    target_file = writer_out.get("filename")
    files_written = []

    # Build topic map: {display_name: filename}
    topic_map = {}
    for fname in os.listdir(KNOWLEDGE_DIR):
        if fname.endswith(".md") and fname != "_index.md":
            topic_map[_topic_from_filename(fname)] = fname

    # Add [[links]] to the newly written note
    if target_file:
        path = os.path.join(KNOWLEDGE_DIR, target_file)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            modified = content
            for topic, fname in topic_map.items():
                if fname == target_file:
                    continue
                # Add [[link]] if topic mentioned but not already linked
                pattern = re.compile(
                    r"(?<!\[\[)(?<!\w)" + re.escape(topic) + r"(?!\w)(?!\]\])",
                    re.IGNORECASE,
                )
                if pattern.search(modified):
                    modified = pattern.sub(f"[[{topic}]]", modified, count=1)

            # Inject related topics section if any links were added
            found_links = re.findall(r"\[\[([^\]]+)\]\]", modified)
            if found_links:
                related = ", ".join(f"[[{t}]]" for t in found_links)
                modified = re.sub(
                    r"## Related Topics\n.*",
                    f"## Related Topics\n{related}",
                    modified,
                    flags=re.DOTALL,
                )

            with open(path, "w", encoding="utf-8") as f:
                f.write(modified)
            files_written.append(target_file)

    # Update _index.md
    index_path = os.path.join(KNOWLEDGE_DIR, "_index.md")
    today = datetime.date.today().isoformat()
    lines = [f"# Knowledge Base Index\n\n*Last updated: {today}*\n\n"]
    for topic, fname in sorted(topic_map.items()):
        lines.append(f"- [[{topic}]] → `{fname}`\n")

    with open(index_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    files_written.append("_index.md")

    return {
        "output": f"Links added. Index updated with {len(topic_map)} topics.",
        "files_read": [],
        "files_written": files_written,
    }
