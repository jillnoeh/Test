"""Plotly map of store footprint colored by local GLP-1 adoption."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render(geo_detail) -> None:
    points = geo_detail.store_lat_lon
    if not points:
        st.info("No matched store coordinates to map.")
        return

    df = pd.DataFrame(points, columns=["lat", "lon", "adoption", "label"])
    df["adoption_pct"] = (df["adoption"] * 100).round(1)

    fig = go.Figure(go.Scattergeo(
        lon=df["lon"], lat=df["lat"],
        text=df["label"] + "<br>Local GLP-1 adoption: "
             + df["adoption_pct"].astype(str) + "%",
        hoverinfo="text",
        marker=dict(
            size=11,
            color=df["adoption"],
            colorscale=[
                [0.0, "#bae6fd"],
                [0.5, "#fbbf24"],
                [1.0, "#b91c1c"],
            ],
            cmin=float(df["adoption"].min()),
            cmax=float(df["adoption"].max()),
            line=dict(width=0.5, color="white"),
            colorbar=dict(
                title=dict(text="GLP-1 adoption",
                           font=dict(size=11, color="#475569")),
                tickformat=".1%",
                thickness=12,
                len=0.6,
            ),
        ),
    ))
    fig.update_layout(
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="#f8fafc",
            subunitcolor="#cbd5e1",
            countrycolor="#cbd5e1",
            showlakes=False,
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        height=420,
        paper_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)
