import re

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "that", "this", "these",
    "those", "it", "its", "as", "not", "if", "then", "than", "when", "what",
    "which", "who", "how", "why", "where", "can", "about", "into", "through",
}


def _detect_input_type(text: str) -> str:
    if re.search(r"https?://", text):
        return "url_content"
    if len(text) > 800 and text.count("\n") > 15:
        return "document"
    return "text_query"


def _clean_text(text: str) -> str:
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _extract_topics(text: str) -> list:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    seen = set()
    topics = []
    for w in words:
        if w not in STOPWORDS and w not in seen:
            seen.add(w)
            topics.append(w)
        if len(topics) >= 10:
            break
    return topics


def _detect_intent(text: str) -> str:
    lowered = text.lower().strip()
    if re.search(r"\b(what|why|how|when|where|who|which|explain|describe)\b", lowered):
        return "question"
    if re.search(r"\b(create|make|build|generate|write|add|update|delete|remove)\b", lowered):
        return "command"
    return "informational"


def run(query: str, context: dict) -> dict:
    input_type = _detect_input_type(query)
    cleaned = _clean_text(query)
    key_topics = _extract_topics(cleaned)
    intent = _detect_intent(cleaned)

    return {
        "output": f"Intake complete. Type: {input_type}, Intent: {intent}, Topics: {', '.join(key_topics[:5])}",
        "files_read": [],
        "files_written": [],
        "data": {
            "input_type": input_type,
            "cleaned_text": cleaned,
            "key_topics": key_topics,
            "intent": intent,
        },
    }
