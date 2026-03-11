import os
from typing import Dict, Any

import requests

API_URL = "https://api.perplexity.ai/chat/completions"


def query_perplexity(prompt: str) -> Dict[str, Any]:
    """Send prompt to Perplexity API and return JSON response."""

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