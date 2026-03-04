"""
src/extraction.py
"""


def extract_brands(data: dict) -> list:
    results: list[str] = []
    _recurse(data, results)
    return sorted(results)


def _recurse(obj: object, results: list[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "brand" and isinstance(value, str):
                results.append(value)
            else:
                _recurse(value, results)
    elif isinstance(obj, list):
        for item in obj:
            _recurse(item, results)
