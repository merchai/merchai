"""
src/metrics/share_of_voice.py
------------------------------
Core Share of Voice metric for MerchAI.

Takes extracted brand mentions from an AI-generated response and returns
a normalised visibility distribution — the foundation of the MerchAI
analytics pipeline.

Rules
-----
- Pure Python, zero external dependencies
- Deterministic: identical input → identical output, always
- Case-insensitive counting, first-seen capitalisation preserved in output
- Blank/whitespace entries silently ignored
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ShareOfVoiceResult:
    """
    Full result from compute_share_of_voice().

    Attributes
    ----------
    shares    : brand → normalised share (0.0–1.0, 2 dp)
    counts    : brand → raw mention count
    total     : total valid mentions processed
    ranked    : [(brand, share), ...] sorted by share desc, alpha tiebreak
    top_brand : highest-share brand, or None if no mentions
    """
    shares: dict[str, float]
    counts: dict[str, int]
    total: int
    ranked: list[tuple[str, float]]
    top_brand: str | None


def compute_share_of_voice(
    mentions: list[str],
    *,
    query_label: str = "",
) -> ShareOfVoiceResult:
    """
    Compute Share of Voice across brands from a flat list of mentions.

    Parameters
    ----------
    mentions :
        List of brand mention strings extracted from an AI response.
    query_label :
        Optional label for the query / campaign (for caller tagging only).

    Returns
    -------
    ShareOfVoiceResult

    Raises
    ------
    TypeError  if mentions is not a list, or any element is not a str.

    Examples
    --------
    >>> r = compute_share_of_voice(["Nike", "Adidas", "Nike"])
    >>> r.shares
    {'Nike': 0.67, 'Adidas': 0.33}
    >>> r.top_brand
    'Nike'
    """
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
        return ShareOfVoiceResult(shares={}, counts={}, total=0, ranked=[], top_brand=None)

    shares = {display[k]: round(v / total, 2) for k, v in counts.items()}
    display_counts = {display[k]: v for k, v in counts.items()}
    ranked = sorted(shares.items(), key=lambda x: (-x[1], x[0]))

    return ShareOfVoiceResult(
        shares=shares,
        counts=display_counts,
        total=total,
        ranked=ranked,
        top_brand=ranked[0][0] if ranked else None,
    )
