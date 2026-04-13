from .utils import call_claude


def run(query: str, context: dict) -> dict:
    research_output = context.get("research", {}).get("output", "")

    system_prompt = (
        "You are a knowledge summarizer. Given a user query and existing research notes, "
        "produce a structured, concise markdown summary. Include: a direct answer to the query, "
        "key facts as bullet points, and relevant subtopics. Keep it under 400 words."
    )

    user_message = (
        f"Query: {query}\n\n"
        f"Existing research notes:\n{research_output}\n\n"
        "Produce a structured markdown summary answering the query."
    )

    summary = call_claude(system_prompt, user_message, max_tokens=1000)

    return {
        "output": summary,
        "files_read": [],
        "files_written": [],
    }
