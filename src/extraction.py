"""
src/extraction.py
"""
from __future__ import annotations

import re
from typing import Any

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
    # Adjectives and descriptors that are not brand names
    "Excellent", "Strong", "Great", "Good", "Better", "Premium", "Perfect",
    "Ideal", "Notable", "Impressive", "Reliable", "Powerful", "Portable",
    "Lightweight", "Thin", "Sleek", "Durable", "Fast", "Smooth", "Clean",
    "Smart", "High", "Low", "Long", "Short", "Wide", "Deep", "Full", "Rich",
    "True", "Real", "Easy", "Hard", "Old", "Young", "Large", "Small",
    "Simple", "Complex", "Basic", "Advanced", "Standard", "Classic", "Modern",
    "Latest", "Newest", "Older", "Affordable", "Expensive", "Budget", "Value",
    "Best-in-class", "Built", "Designed", "Made", "Based", "Focused",
    "Recommended", "Considered", "Widely", "Highly", "Generally",
    # Product categories
    "Gaming", "Laptop", "Desktop", "Phone", "Tablet", "Device", "Computer",
    "Monitor", "Display", "Keyboard", "Mouse", "Speaker", "Camera", "Battery",
    "Charger", "Headphones", "Earbuds", "Webcam", "Microphone", "Printer",
    # Generic product sub-brands / series words
    "Aurora", "Elite", "Titan", "Fusion", "Nexus", "Apex", "Zenith", "Vortex",
    "Eclipse", "Phantom", "Spectre", "Stealth", "Shadow", "Blaze", "Storm",
    "Vision", "Pro", "Plus", "Max", "Mini", "Lite", "Go", "Ultra",
    "Series", "Edition", "Generation", "Version", "Model", "Line", "Range",
    "Collection", "Family", "Platform", "System", "Suite",
    # Tech / feature words
    "Technology", "Software", "Hardware", "Feature", "Experience",
    "Performance", "Innovation", "Intelligence", "Solution", "Service",
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
        brand = _normalize_to_brand(candidate)
        if brand in _STOPWORDS:
            continue
        mentions.append(brand)
    return mentions


def extract_brands(data: Any) -> list[str]:
    brands: set[str] = set()

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
    return sorted(brands)
