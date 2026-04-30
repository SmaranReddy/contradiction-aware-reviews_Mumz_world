"""
LLM wrapper — backed by Groq.
Keeps chat_completion / parse_json_response signatures unchanged.
"""

import json
import re

from models.llm_client import generate_response

DEFAULT_MODEL = "llama-3.1-8b-instant"

_JSON_INSTRUCTION = (
    "\n\nReturn ONLY valid JSON. No markdown. No explanation."
)


def chat_completion(
    prompt: str,
    system: str = "You are a helpful AI assistant.",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    json_mode: bool = False,
) -> str:
    """Send a single user prompt and return the assistant reply as a string."""
    user_prompt = prompt
    if json_mode:
        user_prompt += _JSON_INSTRUCTION
    result = generate_response(user_prompt, system=system)
    if not result and json_mode:
        return "{}"
    return result


def parse_json_response(raw: str) -> dict:
    """Extract and parse the first JSON object from raw LLM output."""
    if not raw:
        return {}
    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return {}
        return json.loads(match.group())
    except Exception:
        return {}
