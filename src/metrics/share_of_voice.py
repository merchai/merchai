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


def compute_analytics(mentions: list[str], query_label: str = "") -> dict:
    """Full analytics report wrapping compute_share_of_voice."""
    shares = compute_share_of_voice(mentions)

    if not shares:
        return {
            "shares": {}, "counts": {}, "total_mentions": 0, "brand_count": 0,
            "ranked": [], "top_brand": None, "top_share": 0.0,
            "concentration_top3": 0.0, "competitive_gaps": {},
            "confidence_level": "Low", "generated_insight": "",
            "query_label": query_label,
        }

    # Rebuild display-keyed counts
    counts: dict[str, int] = {}
    display: dict[str, str] = {}
    for item in mentions:
        if not isinstance(item, str):
            continue
        key = item.strip().lower()
        if not key:
            continue
        if key not in counts:
            counts[key] = 0
            display[key] = item.strip()
        counts[key] += 1
    display_counts = {display[k]: v for k, v in counts.items()}

    total = sum(display_counts.values())
    ranked = sorted(shares.items(), key=lambda x: (-x[1], x[0]))
    top_brand, top_share = ranked[0]
    brand_count = len(ranked)

    concentration_top3 = round(sum(s for _, s in ranked[:3]), 2)
    competitive_gaps = {b: round(s - top_share, 2) for b, s in ranked[1:]}
    tied_leaders = [b for b, s in ranked if s == top_share]
    is_tied = len(tied_leaders) > 1

    if total < 20:
        confidence_level = "Low"
    elif total < 50:
        confidence_level = "Medium"
    else:
        confidence_level = "High"

    # Template insight
    top_pct = round(top_share * 100)
    if is_tied:
        tied_str = ", ".join(tied_leaders)
        insight = (
            f"{len(tied_leaders)} brands are equally matched at {top_pct}% each: {tied_str}. "
            f"No clear leader — the market is perfectly split at the top."
        )
        suggested_action = (
            f"{tied_str} are all tied at {top_pct}%. Any brand could take the lead with "
            f"a single additional AI mention. Focus on increasing content volume to break the tie."
        )
    else:
        others = [f"{b} at {round(s * 100)}%" for b, s in ranked[1:3]]
        others_txt = (", followed by " + ", ".join(others)) if others else ""
        if brand_count == 1:
            insight = f"{top_brand} has 100% share of voice — no competitors detected in this dataset."
        elif concentration_top3 >= 0.8:
            insight = (
                f"{top_brand} leads with {top_pct}% share of voice{others_txt}. "
                f"The market is highly concentrated — the top {min(3, brand_count)} brands "
                f"account for {round(concentration_top3 * 100)}% of all mentions."
            )
        else:
            insight = (
                f"{top_brand} holds the strongest position at {top_pct}%{others_txt}. "
                f"The competitive landscape is fragmented across {brand_count} brands."
            )

        if brand_count == 1:
            suggested_action = f"{top_brand} owns 100% of the share. Monitor for new entrants entering AI responses."
        elif top_share >= 0.5:
            gap_pct = round((top_share - ranked[1][1]) * 100)
            suggested_action = (
                f"{top_brand} leads by {gap_pct}% over {ranked[1][0]}. "
                f"Defend this advantage with consistent AI-optimized content."
            )
        else:
            suggested_action = (
                f"The market is competitive. Increase product comparison coverage "
                f"to challenge {top_brand}'s {top_pct}% position."
            )

    return {
        "shares": shares,
        "counts": display_counts,
        "total_mentions": total,
        "brand_count": brand_count,
        "ranked": [{"brand": b, "share": s} for b, s in ranked],
        "top_brand": top_brand,
        "top_share": top_share,
        "is_tied": is_tied,
        "tied_leaders": tied_leaders,
        "concentration_top3": concentration_top3,
        "competitive_gaps": competitive_gaps,
        "confidence_level": confidence_level,
        "generated_insight": insight,
        "suggested_action": suggested_action,
        "query_label": query_label,
    }
