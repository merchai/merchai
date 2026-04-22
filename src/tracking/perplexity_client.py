import logging
import os
from typing import Dict, Any

import requests

from src.storage import get_recent_run

API_URL = "https://api.perplexity.ai/chat/completions"

logger = logging.getLogger(__name__)

_DEFAULT_DEDUP_HOURS = 24


def query_perplexity(prompt: str) -> Dict[str, Any]:
    """Send prompt to Perplexity API and return JSON response.

    Checks storage for a matching run within DEDUP_WINDOW_HOURS before calling
    the API; returns the cached raw_response payload when a hit is found.
    """
    dedup_hours = float(os.getenv("DEDUP_WINDOW_HOURS", _DEFAULT_DEDUP_HOURS))
    cached = get_recent_run(prompt, within_hours=dedup_hours)
    if cached is not None:
        logger.info("Cache hit for prompt (within %.1fh) — skipping API call", dedup_hours)
        return {"cached": True, "choices": [{"message": {"content": cached["raw_response"]}}]}

    api_key = os.getenv("PERPLEXITY_API_KEY")

    if not api_key:
        raise ValueError("Missing PERPLEXITY_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


if __name__ == "__main__":
    result = query_perplexity("What brands sell hoodies?")
    print(result)