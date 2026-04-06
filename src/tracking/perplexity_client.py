import logging
import os
from typing import Any, Dict

import requests
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

API_URL = "https://api.perplexity.ai/chat/completions"
MODEL_NAME = "sonar-pro"
DEFAULT_TIMEOUT = 20
DEFAULT_MAX_RETRIES = 3

logger = logging.getLogger(__name__)


def should_retry(exception: BaseException) -> bool:
    if isinstance(exception, requests.exceptions.Timeout):
        return True

    if isinstance(exception, requests.exceptions.HTTPError):
        response = exception.response
        if response is not None and 500 <= response.status_code < 600:
            return True

    return False


@retry(
    retry=retry_if_exception(should_retry),
    stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def make_request(prompt: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    api_key = os.getenv("PERPLEXITY_API_KEY")

    if not api_key:
        return {"success": False, "error": "PERPLEXITY_API_KEY is not set."}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=timeout,
    )

    response.raise_for_status()
    return response.json()


def query_perplexity(prompt: str) -> Dict[str, Any]:
    try:
        return make_request(prompt)
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else None
        return {
            "success": False,
            "error": f"HTTP error: {e}",
            "status_code": status_code,
        }
    except requests.exceptions.Timeout as e:
        return {
            "success": False,
            "error": f"Timed out after retries: {e}",
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
        }