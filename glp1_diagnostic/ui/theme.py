"""Color palette, tier styling, CSS injection."""
from __future__ import annotations

import streamlit as st

PALETTE = {
    "ink":     "#1f2937",
    "slate":   "#475569",
    "fog":     "#94a3b8",
    "mist":    "#e2e8f0",
    "paper":   "#f8fafc",
    "accent":  "#0f766e",
    "accent_dark": "#115e59",
    "warn":    "#b45309",
    "alert":   "#b91c1c",
    "good":    "#166534",
}

TIER_STYLE = {
    "Low":      {"bg": "#ecfdf5", "fg": "#166534", "bar": "#16a34a"},
    "Moderate": {"bg": "#fef9c3", "fg": "#854d0e", "bar": "#ca8a04"},
    "High":     {"bg": "#ffedd5", "fg": "#9a3412", "bar": "#ea580c"},
    "Critical": {"bg": "#fee2e2", "fg": "#991b1b", "bar": "#dc2626"},
}


def tier_for(score: float) -> str:
    if score < 25:
        return "Low"
    if score < 50:
        return "Moderate"
    if score < 75:
        return "High"
    return "Critical"


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 2.5rem; max-width: 1200px; }
        h1, h2, h3, h4 { font-family: -apple-system, "Segoe UI", Roboto,
                          "Helvetica Neue", Arial, sans-serif;
                          letter-spacing: -0.01em; color: #1f2937; }
        .glp-eyebrow { text-transform: uppercase; letter-spacing: 0.12em;
                       color: #64748b; font-size: 0.75rem; font-weight: 600; }
        .glp-brand   { font-size: 1.6rem; font-weight: 700; color: #1f2937;
                       margin: 0.25rem 0 0.4rem 0; }
        .glp-hero    { display: flex; align-items: center; gap: 2.25rem;
                       background: #ffffff; border: 1px solid #e2e8f0;
                       border-radius: 18px; padding: 2rem 2.25rem;
                       box-shadow: 0 1px 2px rgba(15,23,42,0.04); }
        .glp-bigscore { font-size: 5.4rem; font-weight: 700; line-height: 1;
                        color: #0f172a; font-variant-numeric: tabular-nums; }
        .glp-of100   { font-size: 1.4rem; color: #94a3b8; font-weight: 500;
                       margin-left: 0.25rem; }
        .glp-tierpill { display: inline-block; padding: 0.4rem 0.95rem;
                        border-radius: 999px; font-weight: 600;
                        font-size: 0.95rem; letter-spacing: 0.02em; }
        .glp-summary { color: #334155; font-size: 1.02rem; line-height: 1.55;
                       max-width: 720px; }
        .glp-card    { background: #ffffff; border: 1px solid #e2e8f0;
                       border-radius: 14px; padding: 1.15rem 1.25rem;
                       height: 100%; }
        .glp-card-label { color: #64748b; font-size: 0.8rem; font-weight: 600;
                          text-transform: uppercase; letter-spacing: 0.08em; }
        .glp-card-score { font-size: 2.4rem; font-weight: 700; color: #0f172a;
                          line-height: 1; margin: 0.45rem 0 0.5rem 0;
                          font-variant-numeric: tabular-nums; }
        .glp-card-meter { height: 6px; background: #f1f5f9; border-radius: 3px;
                          overflow: hidden; margin: 0.3rem 0 0.7rem 0; }
        .glp-card-meter > div { height: 100%; border-radius: 3px; }
        .glp-card-headline { color: #475569; font-size: 0.92rem;
                             line-height: 1.4; }
        .glp-section-h { font-size: 1.05rem; font-weight: 700; color: #1f2937;
                         text-transform: uppercase; letter-spacing: 0.1em;
                         margin: 2.5rem 0 0.75rem 0;
                         border-top: 1px solid #e2e8f0; padding-top: 1.5rem; }
        .glp-finding { background: #f8fafc; border-left: 3px solid #0f766e;
                       padding: 0.75rem 1rem; border-radius: 4px;
                       margin-bottom: 0.55rem; color: #1f2937;
                       font-size: 0.97rem; line-height: 1.5; }
        .glp-demo-banner { background: #fef3c7; color: #854d0e;
                           padding: 0.55rem 0.85rem; border-radius: 6px;
                           font-size: 0.85rem; margin-bottom: 1rem;
                           border: 1px solid #fde68a; }
        .glp-eyebrow-app { font-weight: 600; color: #0f766e;
                           letter-spacing: 0.18em; font-size: 0.7rem;
                           text-transform: uppercase; }
        .glp-app-title { font-size: 1.7rem; font-weight: 700; color: #1f2937;
                         margin: 0.1rem 0 0.25rem 0; }
        .glp-app-sub { color: #64748b; margin-bottom: 1.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
