"""Composite GLP-1 Size Curve Risk Score.

`compute_risk_score` is the single public entry point. Weights live in the
`DEFAULT_WEIGHTS` dict here — change those values to retune without touching
the component code."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from . import geographic, markdown_signal, size_gap, stockout_signal

# Equal weights by default. Override by passing `weights=` to compute_risk_score.
DEFAULT_WEIGHTS: Dict[str, float] = {
    "geographic": 0.25,
    "size_gap":   0.25,
    "markdown":   0.25,
    "stockout":   0.25,
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class ComponentResult:
    name: str
    label: str
    score: float
    weight: float
    headline: str
    detail: Any = None


@dataclass
class RiskScore:
    overall: float
    tier: str
    components: Dict[str, ComponentResult] = field(default_factory=dict)


def _tier(score: float) -> str:
    if score < 25:
        return "Low"
    if score < 50:
        return "Moderate"
    if score < 75:
        return "High"
    return "Critical"


def load_glp1_data(data_dir: Optional[Path] = None) -> Dict[str, pd.DataFrame]:
    """Load all CSVs from data/ into a dict keyed by short name."""
    d = Path(data_dir) if data_dir else DATA_DIR
    return {
        "dmas": pd.read_csv(d / "glp1_adoption_by_dma.csv",
                            dtype={"dma_code": int}),
        "zips": pd.read_csv(d / "glp1_adoption_by_zip.csv",
                            dtype={"zip": str}),
        "panel": pd.read_csv(d / "glp1_consumer_panel.csv"),
        "demand_curve": pd.read_csv(d / "size_demand_curve.csv"),
    }


def compute_risk_score(
    scrape_result,
    glp1_data: Dict[str, pd.DataFrame],
    weights: Optional[Dict[str, float]] = None,
) -> RiskScore:
    w = dict(weights or DEFAULT_WEIGHTS)
    total_w = sum(w.values()) or 1.0

    geo = geographic.score(scrape_result.stores, glp1_data["zips"],
                           glp1_data["dmas"])
    gap = size_gap.score(scrape_result.sizes_offered,
                         glp1_data["demand_curve"])
    md = markdown_signal.score(scrape_result.clearance_items,
                               scrape_result.sizes_offered)
    so = stockout_signal.score(scrape_result.stock_by_size)

    components = {
        "geographic": ComponentResult(
            name="geographic", label="Geographic Exposure",
            score=geo.score, weight=w["geographic"] / total_w,
            headline=geo.headline, detail=geo,
        ),
        "size_gap": ComponentResult(
            name="size_gap", label="Size Range Gap",
            score=gap.score, weight=w["size_gap"] / total_w,
            headline=gap.headline, detail=gap,
        ),
        "markdown": ComponentResult(
            name="markdown", label="Markdown Signal",
            score=md.score, weight=w["markdown"] / total_w,
            headline=md.headline, detail=md,
        ),
        "stockout": ComponentResult(
            name="stockout", label="Stockout Signal",
            score=so.score, weight=w["stockout"] / total_w,
            headline=so.headline, detail=so,
        ),
    }
    overall = sum(c.score * c.weight for c in components.values())
    overall = round(overall, 1)
    return RiskScore(overall=overall, tier=_tier(overall), components=components)
