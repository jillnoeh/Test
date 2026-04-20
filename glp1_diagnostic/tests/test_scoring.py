"""Boundary tests for the four scoring components."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from scoring import compute_risk_score, load_glp1_data
from scoring import geographic, markdown_signal, size_gap, stockout_signal
from scraper import ScrapeResult, scrape_fixture


def test_geographic_no_stores():
    zips = pd.DataFrame(columns=["zip", "lat", "lon", "adoption_rate"])
    dmas = pd.DataFrame(columns=["dma_name", "lat", "lon", "adoption_rate"])
    r = geographic.score([], zips, dmas)
    assert r.score == 0.0


def test_size_gap_perfect_match():
    # If offer mirrors projected, score should be 0.
    demand = pd.DataFrame([
        {"size": "S", "projected_share": 0.5, "baseline_share": 0.5, "delta": 0},
        {"size": "M", "projected_share": 0.5, "baseline_share": 0.5, "delta": 0},
    ])
    r = size_gap.score({"S": 50, "M": 50}, demand)
    assert r.score == 0.0


def test_size_gap_full_under_index():
    demand = pd.DataFrame([
        {"size": "S", "projected_share": 1.0, "baseline_share": 0.5, "delta": 0.5},
        {"size": "M", "projected_share": 0.0, "baseline_share": 0.5, "delta": -0.5},
    ])
    r = size_gap.score({"S": 0, "M": 100}, demand)
    assert r.score >= 99.0


def test_markdown_all_large():
    items = [{"sku": f"x{i}", "size": "2X"} for i in range(10)]
    r = markdown_signal.score(items, {"S": 50, "2X": 50})
    # 100% large in clearance vs 50% in offer → 50pt excess → score 100 (capped)
    assert r.score >= 90.0


def test_stockout_all_small_oos():
    stock = {
        "XS": {"in_stock": 0, "low_stock": 0, "out_of_stock": 10},
        "S":  {"in_stock": 0, "low_stock": 0, "out_of_stock": 10},
        "M":  {"in_stock": 0, "low_stock": 0, "out_of_stock": 10},
        "L":  {"in_stock": 10, "low_stock": 0, "out_of_stock": 0},
        "XL": {"in_stock": 10, "low_stock": 0, "out_of_stock": 0},
    }
    r = stockout_signal.score(stock)
    assert r.score >= 80.0


def test_composite_three_fixtures():
    data = load_glp1_data()
    coastal = compute_risk_score(scrape_fixture("coastal_premium"), data)
    default = compute_risk_score(scrape_fixture("default"), data)
    mass = compute_risk_score(scrape_fixture("mass_basics"), data)
    assert coastal.tier == "Critical"
    assert default.tier in ("High", "Critical")
    assert mass.tier in ("Low", "Moderate")
    assert coastal.overall > default.overall > mass.overall
