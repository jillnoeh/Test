"""Grouped bar chart: current offer share vs projected demand share by size."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

CANONICAL = ["XS", "S", "M", "L", "XL", "1X", "2X", "3X+"]


def render(gap_detail) -> None:
    sizes = CANONICAL
    offered = [gap_detail.offered_share.get(s, 0) * 100 for s in sizes]
    projected = [gap_detail.projected_share.get(s, 0) * 100 for s in sizes]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Current offer",
        x=sizes, y=offered,
        marker=dict(color="#94a3b8"),
        hovertemplate="%{x}: %{y:.1f}%<extra>Offer</extra>",
    ))
    fig.add_trace(go.Bar(
        name="Projected demand",
        x=sizes, y=projected,
        marker=dict(color="#0f766e"),
        hovertemplate="%{x}: %{y:.1f}%<extra>Demand</extra>",
    ))
    fig.update_layout(
        barmode="group",
        height=360,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(title="", tickfont=dict(size=12, color="#475569")),
        yaxis=dict(title="Share of assortment / demand (%)",
                   gridcolor="#e2e8f0", tickfont=dict(color="#475569"),
                   titlefont=dict(color="#475569", size=11)),
    )
    st.plotly_chart(fig, use_container_width=True)
