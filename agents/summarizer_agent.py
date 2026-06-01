from .utils import call_ai, stream_ai

SYSTEM_PROMPT = (
    "You are a knowledge summarizer. Given a user query and existing research notes, "
    "produce a structured, concise markdown summary. Include: a direct answer to the query, "
    "key facts as bullet points, and relevant subtopics. Keep it under 400 words. "
    "Only use facts present in the provided research notes. "
    "If the answer is not in the notes, say so explicitly — do not infer or invent facts."
)


def _build_user_message(query: str, context: dict) -> str:
    research_output = context.get("research", {}).get("output", "")
    return (
        f"Query: {query}\n\n"
        f"Existing research notes:\n{research_output}\n\n"
        "Produce a structured markdown summary answering the query."
    )


def run(query: str, context: dict) -> dict:
    user_message = _build_user_message(query, context)
    summary = call_ai(SYSTEM_PROMPT, user_message, max_tokens=1000, model="claude-sonnet-4-6")
    return {
        "output": summary,
        "files_read": [],
        "files_written": [],
    }


def stream(query: str, context: dict):
    """Generator — yields text chunks from the Anthropic streaming API."""
    user_message = _build_user_message(query, context)
    yield from stream_ai(SYSTEM_PROMPT, user_message, max_tokens=1000, model="claude-sonnet-4-6")
