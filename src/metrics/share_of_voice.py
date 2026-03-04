"""
src/metrics/share_of_voice.py
"""
from __future__ import annotations


def compute_share_of_voice(mentions: list) -> dict:
    if not isinstance(mentions, list):
        raise TypeError(f"mentions must be a list, got {type(mentions).__name__}")

    counts: dict[str, int] = {}
    display: dict[str, str] = {}

    for item in mentions:
        if not isinstance(item, str):
            raise TypeError(
                f"each mention must be a str, got {type(item).__name__}: {item!r}"
            )
        key = item.strip().lower()
        if not key:
            continue
        if key not in counts:
            counts[key] = 0
            display[key] = item.strip()
        counts[key] += 1

    total = sum(counts.values())
    if total == 0:
        return {}

    return {display[k]: round(v / total, 2) for k, v in counts.items()}
