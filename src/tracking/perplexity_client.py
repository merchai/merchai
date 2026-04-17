import logging
import os
from typing import Dict, Any

import requests
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

API_URL = "https://api.perplexity.ai/chat/completions"
DEFAULT_TIMEOUT = 10
logger = logging.getLogger(__name__)


def _should_retry(exc: BaseException) -> bool:
    if isinstance(exc, requests.exceptions.Timeout):
        return True

    if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
        return 500 <= exc.response.status_code < 600

    return False


@retry(
    retry=retry_if_exception(_should_retry),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _make_request(prompt: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
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

    response = requests.post(
        API_URL,
        json=payload,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def query_perplexity(prompt: str) -> Dict[str, Any]:
    """Send prompt to Perplexity API and return JSON response."""
    try:
        return _make_request(prompt)
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else None
        return {"error": str(e), "status_code": status_code}
    except requests.exceptions.Timeout as e:
        return {"error": f"Timed out after retries: {e}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = query_perplexity("What brands sell hoodies?")
    print(result)