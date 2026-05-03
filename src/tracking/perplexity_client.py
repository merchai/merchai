"""
src/tracking/perplexity_client.py

Production-grade Perplexity API client with retries, exponential backoff,
structured system prompting, and response validation.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

API_URL = "https://api.perplexity.ai/chat/completions"
DEFAULT_MODEL = "sonar-pro"
DEFAULT_TIMEOUT = 15
MAX_RETRIES = 3
BACKOFF_BASE = 2.0

SYSTEM_PROMPT = """You are a market research assistant specializing in brand analysis.
When asked about brands in a category, list them clearly by name.
Always mention the brand name explicitly (e.g. "Nike", "Adidas") rather than
referring to them indirectly. Include both dominant and niche players.
Be comprehensive and factual."""


class PerplexityError(Exception):
    """Raised when the Perplexity API returns an unrecoverable error."""


def _build_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _build_payload(prompt: str, model: str) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }


def _extract_text(response_json: dict[str, Any]) -> str:
    try:
        return response_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise PerplexityError(f"Unexpected response shape: {e}") from e


def query_perplexity(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = MAX_RETRIES,
) -> str:
    """
    Send a prompt to Perplexity and return the assistant's text response.

    Retries on transient network/server errors with exponential backoff.
    Raises PerplexityError on auth failures or malformed responses.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise PerplexityError("Missing PERPLEXITY_API_KEY environment variable.")

    headers = _build_headers(api_key)
    payload = _build_payload(prompt, model)
    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL, json=payload, headers=headers, timeout=timeout,
            )
            if response.status_code == 401:
                raise PerplexityError("Invalid API key (401 Unauthorized).")
            response.raise_for_status()
            return _extract_text(response.json())

        except PerplexityError:
            raise

        except requests.exceptions.RequestException as e:
            last_error = e
            wait = BACKOFF_BASE ** attempt
            logger.warning(
                "Perplexity request failed (attempt %d/%d): %s — retrying in %.1fs",
                attempt + 1, max_retries, e, wait,
            )
            time.sleep(wait)

    raise PerplexityError(
        f"Perplexity API unavailable after {max_retries} attempts: {last_error}"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(query_perplexity("What brands sell hoodies?"))