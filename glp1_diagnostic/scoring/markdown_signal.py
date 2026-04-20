"""Markdown Signal Score.

Large sizes piling up on clearance is the leading indicator that demand has
shifted smaller. We compare the share of clearance SKUs that are L/XL/1X/2X/3X+
against the share of the regular assortment that's in those sizes — a wide
positive gap = high score (misaligned)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

LARGE_SIZES = {"L", "XL", "1X", "2X", "3X+"}


@dataclass
class MarkdownResult:
    score: float
    large_share_clearance: float
    large_share_offer: float
    headline: str


def score(
    clearance_items: List[Dict[str, str]],
    sizes_offered: Dict[str, int],
) -> MarkdownResult:
    if not clearance_items:
        return MarkdownResult(score=0.0, large_share_clearance=0.0,
                              large_share_offer=0.0,
                              headline="No clearance data available.")

    n_clear = len(clearance_items)
    large_clear = sum(1 for c in clearance_items if c.get("size") in LARGE_SIZES)
    large_share_clear = large_clear / n_clear

    n_offer = sum(sizes_offered.values()) or 1
    large_offer = sum(v for k, v in sizes_offered.items() if k in LARGE_SIZES)
    large_share_offer = large_offer / n_offer

    # Excess large-size share in clearance vs. assortment, scaled to 0-100.
    # A 30-point gap (e.g., 75% clearance large vs 45% offer large) → score 75.
    excess = max(0.0, large_share_clear - large_share_offer)
    raw = min(100.0, excess * 250.0)

    headline = (
        f"{large_share_clear*100:.0f}% of clearance is L/XL/1X/2X/3X+ "
        f"vs {large_share_offer*100:.0f}% of full assortment."
    )
    return MarkdownResult(score=round(raw, 1),
                          large_share_clearance=large_share_clear,
                          large_share_offer=large_share_offer,
                          headline=headline)
