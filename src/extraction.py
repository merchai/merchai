"""
src/extraction.py
"""
from __future__ import annotations

import re

# Common English words that appear capitalised but are not brand names
_STOPWORDS = {
    "The", "A", "An", "In", "On", "At", "To", "For", "With", "From", "By",
    "And", "Or", "But", "So", "Yet", "Nor", "Not", "Also", "Very", "Just",
    "That", "This", "These", "Those", "Which", "Who", "What", "When", "Where",
    "Why", "How", "Some", "Any", "All", "Each", "Every", "Most", "Many",
    "More", "Other", "Such", "Same", "Its", "Their", "Our", "Your", "His",
    "Her", "My", "We", "They", "You", "He", "She", "It", "Best", "Top",
    "New", "Here", "There", "If", "Even", "Still", "Only", "First", "Last",
    "One", "Two", "Three", "Four", "Five", "Has", "Have", "Had", "Is", "Are",
    "Was", "Were", "Be", "Been", "Being", "Do", "Does", "Did", "Will",
    "Would", "Could", "Should", "May", "Might", "Must", "Shall", "Can",
    "Including", "Include", "Such", "Like", "Well", "Known", "Popular",
    "Often", "Also", "Both", "Overall", "Another", "However", "While",
}

_BRAND_PATTERN = re.compile(
    r'\b([A-Z][a-zA-Z\-\']+(?:\s+[A-Z][a-zA-Z\-\']+)*)\b'
)

# Multi-word brand names that should be kept intact
_MULTI_WORD_BRANDS = [
    "New Balance", "Under Armour", "On Running", "K-Swiss", "Le Coq Sportif",
    "Louis Vuitton", "Saint Laurent", "Alexander McQueen", "Jimmy Choo",
]
_MULTI_WORD_LOWER = [b.lower() for b in _MULTI_WORD_BRANDS]


def _normalize_to_brand(candidate: str) -> str:
    """Return just the brand name from a Title Case phrase.

    Keeps known multi-word brands intact; otherwise returns the first word only.
    """
    lower = candidate.lower()
    for i, pattern in enumerate(_MULTI_WORD_LOWER):
        if lower.startswith(pattern):
            return _MULTI_WORD_BRANDS[i]
    return candidate.split()[0]


def extract_brands_from_text(text: str) -> list[str]:
    """Extract likely brand mentions from free-form AI response text.

    Returns a flat list of brand name strings (with repetition, for SOV counting).
    """
    mentions: list[str] = []
    for match in _BRAND_PATTERN.finditer(text):
        candidate = match.group(1)
        words = candidate.split()
        # Drop if every word is a common English word
        if all(w in _STOPWORDS for w in words):
            continue
        if len(candidate) < 2:
            continue
        mentions.append(_normalize_to_brand(candidate))
    return mentions


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
