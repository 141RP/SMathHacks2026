"""
ReefSync AI Client
Wrapper around the Anthropic SDK. All Claude calls go through here.
"""

import os
import json
from anthropic import Anthropic, APIError

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-opus-4-5"


def call_claude(system: str, user_message: str, max_tokens: int = 512) -> str:
    """Basic Claude call. Returns text response."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def call_claude_stream(system: str, user_message: str, max_tokens: int = 512):
    """Streaming Claude call. Yields text chunks."""
    with client.messages.stream(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def call_claude_json(system: str, user_message: str, max_tokens: int = 512) -> list | dict:
    """Claude call that expects JSON back. Parses and returns it."""
    raw = call_claude(system, user_message, max_tokens)
    # Strip markdown fences if model wraps in them
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(clean)


def call_claude_conversation(
    system: str,
    messages: list[dict],
    max_tokens: int = 512,
) -> str:
    """Multi-turn call. messages = list of {role, content} dicts."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text
