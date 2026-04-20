"""Big centerpiece score + tier pill + brand label."""
from __future__ import annotations

import streamlit as st

from .theme import TIER_STYLE


def render(brand: str, overall: float, tier: str, summary: str,
           is_demo: bool = False) -> None:
    style = TIER_STYLE[tier]
    pct = max(0.0, min(100.0, overall))

    if is_demo:
        st.markdown(
            '<div class="glp-demo-banner">Demo data — live scrape '
            'unavailable for this URL. The diagnostic below uses a bundled '
            'sample retailer so you can see the full output.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="glp-hero">
          <div style="flex: 0 0 auto;">
            <div class="glp-eyebrow">GLP-1 Size Curve Risk Score</div>
            <div class="glp-brand">{brand}</div>
            <div>
              <span class="glp-bigscore" style="color:{style['fg']};">
                {overall:.0f}<span class="glp-of100">/100</span>
              </span>
            </div>
            <div style="margin-top: 0.6rem;">
              <span class="glp-tierpill"
                    style="background:{style['bg']}; color:{style['fg']};">
                {tier} risk
              </span>
            </div>
          </div>
          <div style="flex: 1 1 auto; padding-left: 1.5rem;
                      border-left: 1px solid #e2e8f0;">
            <div class="glp-eyebrow" style="margin-bottom: 0.5rem;">
              What's driving the score
            </div>
            <div class="glp-summary">{summary}</div>
            <div style="margin-top: 1.1rem; height: 8px; background: #f1f5f9;
                        border-radius: 4px; overflow: hidden;">
              <div style="width: {pct}%; height: 100%;
                          background: {style['bar']};"></div>
            </div>
            <div style="display: flex; justify-content: space-between;
                        font-size: 0.7rem; color: #94a3b8; margin-top: 4px;">
              <span>0 · Low</span><span>25</span><span>50</span>
              <span>75</span><span>100 · Critical</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def summarize(brand: str, score, components: dict) -> str:
    """Plain-English one-paragraph driver summary, deterministic."""
    sorted_c = sorted(components.values(), key=lambda c: -c.score)
    top = sorted_c[0]
    second = sorted_c[1]
    bottom = sorted_c[-1]

    if score.tier in ("Critical", "High"):
        opening = (f"{brand} screens as <b>{score.tier.lower()}</b> exposure "
                   f"to GLP-1-driven size-curve shifts. ")
    elif score.tier == "Moderate":
        opening = (f"{brand} carries <b>moderate</b> exposure today, with "
                   "specific pockets of risk worth monitoring. ")
    else:
        opening = (f"{brand} appears <b>well aligned</b> to projected demand "
                   "shifts, with limited near-term exposure. ")

    body = (f"The largest driver is <b>{top.label}</b> ({top.score:.0f}/100): "
            f"{top.headline} A secondary signal comes from "
            f"<b>{second.label}</b> ({second.score:.0f}/100): {second.headline} ")
    tail = (f"<b>{bottom.label}</b> is the least concerning today "
            f"({bottom.score:.0f}/100).")
    return opening + body + tail
