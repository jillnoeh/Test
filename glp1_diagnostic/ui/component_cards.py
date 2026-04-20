"""2x2 grid of component score cards."""
from __future__ import annotations

from typing import Dict

import streamlit as st

from .theme import TIER_STYLE, tier_for


def _card(label: str, score: float, headline: str) -> str:
    style = TIER_STYLE[tier_for(score)]
    pct = max(0.0, min(100.0, score))
    return f"""
    <div class="glp-card">
      <div class="glp-card-label">{label}</div>
      <div class="glp-card-score" style="color:{style['fg']};">
        {score:.0f}<span style="font-size:1rem;color:#94a3b8;font-weight:500;">
        /100</span>
      </div>
      <div class="glp-card-meter">
        <div style="width:{pct}%;background:{style['bar']};"></div>
      </div>
      <div class="glp-card-headline">{headline}</div>
    </div>
    """


def render(components: Dict) -> None:
    order = ["geographic", "size_gap", "markdown", "stockout"]
    cards = [components[k] for k in order]
    row1 = st.columns(2, gap="medium")
    row2 = st.columns(2, gap="medium")
    for col, c in zip(row1 + row2, cards):
        with col:
            st.markdown(_card(c.label, c.score, c.headline),
                        unsafe_allow_html=True)
