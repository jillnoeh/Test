"""Generate 3-5 key-finding bullets from component results.

Deterministic and template-driven so the output is dependable in a client
meeting. Bullets are phrased to drop straight into a deck."""
from __future__ import annotations

from typing import Dict, List

import streamlit as st


def _fmt_pct(x: float) -> str:
    return f"{x*100:.0f}%"


def generate(brand: str, score, components: Dict) -> List[str]:
    geo = components["geographic"].detail
    gap = components["size_gap"].detail
    md = components["markdown"].detail
    so = components["stockout"].detail

    bullets: List[str] = []

    # 1. Headline tier statement.
    bullets.append(
        f"<b>{brand}</b> screens at <b>{score.overall:.0f}/100</b> on the "
        f"GLP-1 Size Curve Risk Index — <b>{score.tier} risk</b> relative to "
        "the broader specialty apparel set."
    )

    # 2. Geographic finding.
    if geo.matched_stores:
        bullets.append(
            f"<b>Footprint exposure:</b> {geo.matched_stores} matched stores "
            f"sit in markets averaging <b>{_fmt_pct(geo.avg_adoption)}</b> "
            f"local GLP-1 adoption, with <b>{_fmt_pct(geo.top_quartile_share)}</b> "
            "of stores in top-quartile-adoption ZIP codes."
        )

    # 3. Size gap finding (only if there is a gap).
    if gap.gaps:
        biggest = max(gap.gaps.items(), key=lambda kv: kv[1])
        if biggest[1] > 0.02:
            bullets.append(
                f"<b>Assortment gap:</b> projected demand for size "
                f"<b>{biggest[0]}</b> is "
                f"<b>{_fmt_pct(gap.projected_share.get(biggest[0],0))}</b> of "
                f"the curve, but only <b>{_fmt_pct(gap.offered_share.get(biggest[0],0))}</b> "
                f"of the current offer — a {biggest[1]*100:.1f}-point under-index."
            )

    # 4. Markdown finding.
    if md.large_share_clearance > md.large_share_offer + 0.10:
        bullets.append(
            f"<b>Markdown signal:</b> larger sizes (L–3X+) make up "
            f"<b>{_fmt_pct(md.large_share_clearance)}</b> of clearance "
            f"vs. <b>{_fmt_pct(md.large_share_offer)}</b> of the full "
            "assortment — a clear over-clearance pattern in those sizes."
        )

    # 5. Stockout finding.
    if so.small_oos_rate > max(0.10, so.other_oos_rate + 0.05):
        bullets.append(
            f"<b>Demand signal:</b> XS/S/M variants are out of stock "
            f"<b>{_fmt_pct(so.small_oos_rate)}</b> of the time "
            f"(vs. {_fmt_pct(so.other_oos_rate)} elsewhere) — suggesting "
            "smaller-size demand is exceeding allocation."
        )

    return bullets[:5]


def render(brand: str, score, components: Dict) -> None:
    bullets = generate(brand, score, components)
    for b in bullets:
        st.markdown(f'<div class="glp-finding">{b}</div>',
                    unsafe_allow_html=True)
