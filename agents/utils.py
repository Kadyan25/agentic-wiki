import os
import time

# In-memory response cache keyed by (model, system_prompt, user_message).
# Prevents redundant API calls for identical inputs within a process lifetime.
_cache: dict = {}

DEFAULT_MODEL = "claude-haiku-4-5"


def _get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set or is empty. "
            "Add it to your .env file or Render environment variables."
        )
    from anthropic import Anthropic
    return Anthropic(api_key=api_key)


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
    """
    Call the Anthropic API with 2-attempt retry and in-memory caching.
    Raises RuntimeError on failure — never returns an error string as content.
    """
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

    raise RuntimeError(f"AI call failed after 2 attempts: {last_err}")


def call_vision(image_bytes: bytes, media_type: str, prompt: str) -> str:
    """
    Send an image to Claude's vision API with 2-attempt retry.
    Raises RuntimeError on failure.
    """
    import base64
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")

    last_err = None
    for attempt in range(2):
        try:
            client = _get_client()
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
        except Exception as e:
            last_err = e
            if attempt == 0:
                time.sleep(1)

    raise RuntimeError(f"Vision call failed after 2 attempts: {last_err}")


def stream_ai(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 1000,
    model: str = DEFAULT_MODEL,
):
    """
    Stream tokens from the Anthropic API.
    Yields text chunks as they arrive.
    Raises RuntimeError if the stream cannot be established after 2 attempts.
    """
    last_err = None
    for attempt in range(2):
        try:
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
            return  # success
        except Exception as e:
            last_err = e
            if attempt == 0:
                time.sleep(1)

    raise RuntimeError(f"Stream failed after 2 attempts: {last_err}")


def get_active_provider() -> str:
    """Returns a human-readable label for the active provider."""
    return "Claude (Haiku)" if os.environ.get("ANTHROPIC_API_KEY", "").strip() else "No provider configured"
