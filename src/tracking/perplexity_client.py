import os
import requests

API_URL = "https://api.perplexity.ai/chat/completions"


def query_perplexity(prompt: str) -> dict:

    api_key = os.getenv("PERPLEXITY_API_KEY")  # get key from env

    if not api_key:
        raise ValueError("Missing PERPLEXITY_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "sonar-pro",  # model name
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()  # raise error if bad status
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}  # graceful error


if __name__ == "__main__":
    result = query_perplexity("What brands sell hoodies?")
    print(result)
