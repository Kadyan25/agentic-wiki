from openai import OpenAI

client = OpenAI()


def call_ai(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content
