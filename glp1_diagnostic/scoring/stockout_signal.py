"""Stockout Signal Score.

If XS/S/M variants are disproportionately out of stock or low stock, the
retailer is leaving smaller-size demand on the table — a leading indicator
that the curve has shifted smaller faster than allocation has caught up."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

SMALL_SIZES = {"XS", "S", "M"}


@dataclass
class StockoutResult:
    score: float
    small_oos_rate: float
    other_oos_rate: float
    headline: str


def _oos_rate(buckets: Dict[str, int]) -> float:
    total = sum(buckets.values())
    if total == 0:
        return 0.0
    oos = buckets.get("out_of_stock", 0) + 0.5 * buckets.get("low_stock", 0)
    return oos / total


def score(stock_by_size: Dict[str, Dict[str, int]]) -> StockoutResult:
    if not stock_by_size:
        return StockoutResult(score=0.0, small_oos_rate=0.0, other_oos_rate=0.0,
                              headline="No stock data available.")

    small_buckets = {"in_stock": 0, "low_stock": 0, "out_of_stock": 0}
    other_buckets = {"in_stock": 0, "low_stock": 0, "out_of_stock": 0}
    for size, b in stock_by_size.items():
        target = small_buckets if size in SMALL_SIZES else other_buckets
        for k in target:
            target[k] += b.get(k, 0)

    small_rate = _oos_rate(small_buckets)
    other_rate = _oos_rate(other_buckets)

    # Score = excess of small-size stockout rate over rest-of-assortment rate.
    # A 30-point excess (50% small OOS vs 20% other) maps to ~75.
    excess = max(0.0, small_rate - other_rate)
    raw = min(100.0, small_rate * 100 * 0.6 + excess * 200)
    raw = min(100.0, raw)

    headline = (
        f"{small_rate*100:.0f}% of XS/S/M variants out of stock "
        f"vs {other_rate*100:.0f}% in larger sizes."
    )
    return StockoutResult(score=round(raw, 1), small_oos_rate=small_rate,
                          other_oos_rate=other_rate, headline=headline)
