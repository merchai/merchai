from typing import Any, List, Set

def extract_brands(data: Any) -> List[str]:
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
