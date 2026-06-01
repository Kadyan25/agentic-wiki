import re

STOPWORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
    "how", "its", "may", "new", "now", "old", "see", "two", "way", "who",
    "with", "from", "this", "that", "they", "have", "been", "will", "would",
    "when", "what", "then", "than", "also", "into", "some", "more", "very",
    "just", "over", "such", "each", "most", "only", "both", "well", "even",
    "does", "were", "said", "here", "used", "many", "make", "like", "time",
    "which", "their", "there", "these", "those", "could", "other", "about",
    "after", "first", "never", "where", "while", "should", "before",
}


def _extract_entities(text: str) -> list[str]:
    """Capitalized multi-word phrases (Title Case sequences of 2+ words)."""
    matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', text)
    seen = set()
    entities = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            entities.append(m)
        if len(entities) >= 10:
            break
    return entities


def _extract_numbers(text: str) -> list[str]:
    """Numbers with optional units (million, percent, %, km, hrs, etc.)."""
    pattern = r'\b(\d[\d,\.]*\s*(?:million|billion|thousand|percent|%|km|kg|hrs?|days?|years?|months?|weeks?|USD|EUR|GBP)?)\b'
    matches = re.findall(pattern, text, re.IGNORECASE)
    seen = set()
    numbers = []
    for m in matches:
        cleaned = m.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            numbers.append(cleaned)
        if len(numbers) >= 10:
            break
    return numbers


def _extract_key_terms(text: str) -> list[str]:
    """Unique words 4+ chars, excluding stopwords."""
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    seen = set()
    terms = []
    for w in words:
        if w not in STOPWORDS and w not in seen:
            seen.add(w)
            terms.append(w)
        if len(terms) >= 10:
            break
    return terms


def run(query: str, context: dict) -> dict:
    intake_data = context.get("intake", {}).get("data", {})
    text = intake_data.get("cleaned_text", query)

    entities = _extract_entities(text)
    numbers = _extract_numbers(text)
    key_terms = _extract_key_terms(text)

    summary = (
        f"Extracted {len(entities)} entities, "
        f"{len(numbers)} numeric values, "
        f"{len(key_terms)} key terms."
    )

    return {
        "output": summary,
        "files_read": [],
        "files_written": [],
        "data": {
            "entities": entities,
            "numbers": numbers,
            "key_terms": key_terms,
        },
    }
