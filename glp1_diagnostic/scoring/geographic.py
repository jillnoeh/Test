"""Geographic Exposure Score.

Joins scraped store ZIPs to the GLP-1 ZIP-level adoption table. Falls back
to a DMA-name match when ZIP isn't available. Higher score = more exposure
(stores concentrated in high-adoption markets)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd


@dataclass
class GeoResult:
    score: float
    matched_stores: int
    avg_adoption: float
    top_quartile_share: float
    store_lat_lon: List[Tuple[float, float, float, str]]
    # (lat, lon, adoption_rate, label)
    headline: str


def _match_store(
    store: Dict[str, str],
    zips: pd.DataFrame,
    dmas: pd.DataFrame,
) -> Tuple[float | None, float | None, float | None]:
    """Return (adoption_rate, lat, lon) for a store, or (None, None, None)."""
    z = (store.get("zip") or "").strip()
    if z:
        hit = zips.loc[zips["zip"] == z]
        if not hit.empty:
            row = hit.iloc[0]
            return float(row["adoption_rate"]), float(row["lat"]), float(row["lon"])
    city = (store.get("city") or "").strip().lower()
    if city:
        hit = dmas.loc[dmas["dma_name"].str.lower() == city]
        if not hit.empty:
            row = hit.iloc[0]
            return float(row["adoption_rate"]), float(row["lat"]), float(row["lon"])
    return None, None, None


def score(
    stores: List[Dict[str, str]],
    zips: pd.DataFrame,
    dmas: pd.DataFrame,
) -> GeoResult:
    if not stores:
        return GeoResult(score=0.0, matched_stores=0, avg_adoption=0.0,
                         top_quartile_share=0.0, store_lat_lon=[],
                         headline="No store footprint data available.")

    rates: List[float] = []
    points: List[Tuple[float, float, float, str]] = []
    for s in stores:
        rate, lat, lon = _match_store(s, zips, dmas)
        if rate is None:
            continue
        rates.append(rate)
        label = (s.get("name") or s.get("city") or s.get("zip") or "").strip()
        points.append((lat, lon, rate, label))

    if not rates:
        return GeoResult(score=0.0, matched_stores=0, avg_adoption=0.0,
                         top_quartile_share=0.0, store_lat_lon=[],
                         headline="No store ZIPs matched the GLP-1 dataset.")

    avg_rate = sum(rates) / len(rates)
    # Population reference: top quartile of ZIP adoption nationally.
    top_q_threshold = float(zips["adoption_rate"].quantile(0.75))
    in_top_q = sum(1 for r in rates if r >= top_q_threshold)
    top_q_share = in_top_q / len(rates)

    # Anchor: avg adoption ~ 7% maps to score ~70. Multiply by 1000 to get a
    # 0-100 range, then add a concentration bonus when >40% of stores fall
    # in top-quartile-adoption ZIPs.
    base = min(100.0, avg_rate * 1000.0)
    bonus = 0.0
    if top_q_share > 0.40:
        bonus = min(15.0, (top_q_share - 0.40) * 60.0)
    final = min(100.0, base + bonus)

    headline = (
        f"{len(rates)} stores avg {avg_rate*100:.1f}% local GLP-1 adoption; "
        f"{top_q_share*100:.0f}% sit in top-quartile adoption ZIPs."
    )
    return GeoResult(score=round(final, 1), matched_stores=len(rates),
                     avg_adoption=avg_rate, top_quartile_share=top_q_share,
                     store_lat_lon=points, headline=headline)
