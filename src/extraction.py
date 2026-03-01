from typing import Any, List, Set

def extract_brands(data: Any) -> List[str]:
    """
    Recursively extracts values associated with the key 'brand' from any nested JSON structure.

    NOTE: This function currently only looks for explicit "brand" keys in structured JSON.
    It does NOT perform free-text parsing or NLP extraction from unstructured text.
    
    Args:
        data: A dict, list, or primitive usually representing parsed JSON.
        
    Returns:
        A sorted list of unique brand names found associated with the key 'brand'.
    """
    brands: Set[str] = set()

    def _recurse(current_data: Any) -> None:
        if isinstance(current_data, dict):
            for key, value in current_data.items():
                if key == "brand" and isinstance(value, str):
                    brands.add(value)
                _recurse(value)
        elif isinstance(current_data, list):
            for item in current_data:
                _recurse(item)

    _recurse(data)
    return sorted(list(brands))
