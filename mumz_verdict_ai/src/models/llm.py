"""
Thin LLM wrapper supporting OpenRouter and OpenAI-compatible APIs.
Set OPENROUTER_API_KEY or OPENAI_API_KEY in your environment.
"""

import json
import os

import httpx

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_OPENAI_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"  # change to any OpenRouter model slug


def _get_api_key() -> tuple[str, str]:
    """Return (api_key, base_url)."""
    if key := os.environ.get("OPENROUTER_API_KEY"):
        return key, _OPENROUTER_URL
    if key := os.environ.get("OPENAI_API_KEY"):
        return key, _OPENAI_URL
    raise ValueError("Set OPENROUTER_API_KEY or OPENAI_API_KEY")


def chat_completion(
    prompt: str,
    system: str = "You are a helpful AI assistant.",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    json_mode: bool = False,
) -> str:
    """Send a single user prompt and return the assistant reply as a string."""
    api_key, base_url = _get_api_key()

    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = httpx.post(base_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def parse_json_response(raw: str) -> dict:
    """Strip markdown fences if present, then parse JSON."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]  # drop opening fence line
        cleaned = cleaned.rsplit("```", 1)[0]  # drop closing fence
    return json.loads(cleaned.strip())
