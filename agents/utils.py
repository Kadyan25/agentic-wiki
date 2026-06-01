import os
import time

# In-memory response cache keyed by (model, system_prompt, user_message).
# Prevents redundant API calls for identical inputs within a process lifetime.
_cache: dict = {}

DEFAULT_MODEL = "claude-haiku-4-5"


def _get_client():
    from anthropic import Anthropic
    return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _call_anthropic(system_prompt: str, user_message: str, max_tokens: int, model: str) -> str:
    """Single attempt to call the Anthropic API. Raises on failure."""
    client = _get_client()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=[{
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def call_ai(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 1000,
    model: str = DEFAULT_MODEL,
) -> str:
    cache_key = (model, system_prompt, user_message)
    if cache_key in _cache:
        return _cache[cache_key]

    last_err = None
    for attempt in range(2):
        try:
            result = _call_anthropic(system_prompt, user_message, max_tokens, model)
            _cache[cache_key] = result
            return result
        except Exception as e:
            last_err = e
            if attempt == 0:
                time.sleep(1)

    return f"AI call failed: {last_err}"


def call_vision(image_bytes: bytes, media_type: str, prompt: str) -> str:
    """Send an image to Claude's vision API and return the text response."""
    import base64
    client = _get_client()
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_data,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return response.content[0].text


def stream_ai(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 1000,
    model: str = DEFAULT_MODEL,
):
    """Stream tokens from the Anthropic API. Yields text chunks as they arrive."""
    client = _get_client()
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=[{
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def get_active_provider() -> str:
    """Returns a human-readable label for the active provider."""
    return "Claude (Haiku)" if os.getenv("ANTHROPIC_API_KEY") else "No provider configured"
