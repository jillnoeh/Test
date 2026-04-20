"""Size Range Gap Score.

Compare the retailer's offered size mix to the projected demand curve from
the consumer panel. Penalize sizes where projected demand share exceeds
offered share — i.e., the retailer is under-indexed on growing sizes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

CANONICAL = ["XS", "S", "M", "L", "XL", "1X", "2X", "3X+"]


@dataclass
class SizeGapResult:
    score: float
    offered_share: Dict[str, float]
    projected_share: Dict[str, float]
    gaps: Dict[str, float]   # projected - offered (positive = under-indexed)
    headline: str


def score(
    sizes_offered: Dict[str, int],
    demand_curve: pd.DataFrame,
) -> SizeGapResult:
    total = sum(sizes_offered.values())
    if total == 0:
        return SizeGapResult(score=0.0, offered_share={}, projected_share={},
                             gaps={}, headline="No size data available.")

    offered_share = {s: sizes_offered.get(s, 0) / total for s in CANONICAL}
    projected = {row["size"]: float(row["projected_share"])
                 for _, row in demand_curve.iterrows()}
    gaps = {s: projected.get(s, 0.0) - offered_share[s] for s in CANONICAL}

    # Score = sum of positive gaps, normalized. Maximum possible positive-gap
    # sum is 1.0 (retailer offers nothing, demand is everywhere); that maps
    # to 100. Realistic maxima are ~0.40, so we scale by 2.5 for sensitivity.
    positive_gap_sum = sum(g for g in gaps.values() if g > 0)
    raw = min(100.0, positive_gap_sum * 250.0)

    biggest_gap = max(gaps.items(), key=lambda kv: kv[1])
    if biggest_gap[1] > 0:
        headline = (
            f"Largest under-index: size {biggest_gap[0]} "
            f"(offer {offered_share[biggest_gap[0]]*100:.0f}% vs projected demand "
            f"{projected.get(biggest_gap[0], 0)*100:.0f}%)."
        )
    else:
        headline = "Size mix is well aligned to projected demand."

    return SizeGapResult(score=round(raw, 1), offered_share=offered_share,
                         projected_share=projected, gaps=gaps,
                         headline=headline)
