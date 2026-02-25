"""
src/metrics/share_of_voice.py
------------------------------
Core Share of Voice metric for MerchAI Phase 1 MVP.

Takes extracted brand mentions and returns a normalised distribution
showing each brand's relative frequency within an AI-generated response.

This module is:
  - Pure Python, no external dependencies
  - Deterministic: identical input always produces identical output
  - Case-preserving: output keys match the first-seen capitalisation
"""

from __future__ import annotations


def compute_share_of_voice(mentions: list[str]) -> dict[str, float]:
    """
    Compute Share of Voice across brands from a list of mentions.

    Each brand's score is its proportion of total mentions, rounded to 2
    decimal places. Comparison is case-insensitive; output keys preserve
    the capitalisation of the first occurrence of each brand.

    Parameters
    ----------
    mentions:
        Flat list of brand mention strings extracted from an AI response.
        Blank strings and whitespace-only entries are ignored.

    Returns
    -------
    dict mapping brand name → normalised share (0.0 – 1.0).
    Returns an empty dict when no valid mentions are provided.

    Raises
    ------
    TypeError
        If *mentions* is not a list, or any element is not a string.

    Examples
    --------
    >>> compute_share_of_voice(["Nike", "Adidas", "Nike"])
    {'Nike': 0.67, 'Adidas': 0.33}

    >>> compute_share_of_voice([])
    {}
    """
    if not isinstance(mentions, list):
        raise TypeError(f"mentions must be a list, got {type(mentions).__name__}")

    # ── Count occurrences (case-insensitive, preserve first-seen casing) ──
    counts: dict[str, int] = {}        # key = normalised lowercase
    display: dict[str, str] = {}       # key = normalised lowercase, value = display name

    for item in mentions:
        if not isinstance(item, str):
            raise TypeError(f"each mention must be a str, got {type(item).__name__}: {item!r}")
        normalised = item.strip().lower()
        if not normalised:
            continue
        if normalised not in counts:
            counts[normalised] = 0
            display[normalised] = item.strip()   # first-seen capitalisation
        counts[normalised] += 1

    total = sum(counts.values())
    if total == 0:
        return {}

    # ── Normalise ─────────────────────────────────────────────────────────
    return {
        display[key]: round(count / total, 2)
        for key, count in counts.items()
    }
