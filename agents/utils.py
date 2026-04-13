import anthropic

client = anthropic.Anthropic()


def call_claude(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text
