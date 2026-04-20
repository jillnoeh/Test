"""GLP-1 Size Curve Risk Diagnostic — Streamlit entry point.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from scoring import compute_risk_score, load_glp1_data
from scraper import scrape, scrape_fixture
from ui import (
    component_cards,
    findings,
    score_hero,
    size_gap_chart,
    store_map,
    theme,
)

st.set_page_config(
    page_title="GLP-1 Size Curve Risk Diagnostic",
    layout="wide",
    page_icon="◐",
    initial_sidebar_state="collapsed",
)


@st.cache_data(show_spinner=False)
def _load_data():
    return load_glp1_data()


@st.cache_data(show_spinner="Scraping retailer site…")
def _scrape_cached(url: str, brand: str):
    return scrape(url, brand)


def _header() -> None:
    st.markdown(
        """
        <div class="glp-eyebrow-app">CONSULTING DIAGNOSTIC</div>
        <div class="glp-app-title">GLP-1 Size Curve Risk Tool</div>
        <div class="glp-app-sub">
          Scores an apparel retailer's exposure to GLP-1-driven shifts in
          consumer size demand using public-site signals and proprietary
          adoption data.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _input_panel():
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 1.4], gap="medium")
        with c1:
            url = st.text_input("Retailer website URL",
                                placeholder="https://www.examplebrand.com",
                                key="url_input")
        with c2:
            brand = st.text_input("Brand name (for the report)",
                                  placeholder="Example Brand",
                                  key="brand_input")
        with c3:
            st.write("")
            st.write("")
            run = st.button("Run diagnostic", type="primary",
                            use_container_width=True)
        c4, c5, c6 = st.columns([1, 1, 1], gap="medium")
        with c4:
            demo1 = st.button("Sample · Mid-market chain (High)",
                              use_container_width=True)
        with c5:
            demo2 = st.button("Sample · Coastal premium (Critical)",
                              use_container_width=True)
        with c6:
            demo3 = st.button("Sample · Mass basics (Moderate)",
                              use_container_width=True)
    return run, url, brand, demo1, demo2, demo3


def _render_diagnostic(scrape_result, brand: str) -> None:
    data = _load_data()
    score = compute_risk_score(scrape_result, data)
    summary = score_hero.summarize(brand or scrape_result.brand or "Retailer",
                                   score, score.components)
    score_hero.render(
        brand=brand or scrape_result.brand or "Retailer",
        overall=score.overall,
        tier=score.tier,
        summary=summary,
        is_demo=scrape_result.is_demo,
    )

    st.markdown('<div class="glp-section-h">Component scores</div>',
                unsafe_allow_html=True)
    component_cards.render(score.components)

    st.markdown('<div class="glp-section-h">Store footprint vs GLP-1 adoption</div>',
                unsafe_allow_html=True)
    store_map.render(score.components["geographic"].detail)

    st.markdown('<div class="glp-section-h">Size mix: current offer vs projected demand</div>',
                unsafe_allow_html=True)
    size_gap_chart.render(score.components["size_gap"].detail)

    st.markdown('<div class="glp-section-h">Key findings</div>',
                unsafe_allow_html=True)
    findings.render(brand or scrape_result.brand or "The retailer",
                    score, score.components)

    with st.expander("Methodology & data sources"):
        st.markdown("""
        - **Geographic Exposure:** scraped store ZIPs joined to a
          ZIP-level GLP-1 adoption table (fallback: DMA join).
          Score weights average local adoption with a concentration bonus
          when stores cluster in top-quartile-adoption ZIPs.
        - **Size Range Gap:** retailer's offered size mix vs. a projected
          demand curve derived from consumer-panel size migration
          (pre- vs. post-GLP-1 size purchase). Penalizes under-indexing only.
        - **Markdown Signal:** share of clearance SKUs in L/XL/1X/2X/3X+
          vs. share of the full assortment in those sizes.
        - **Stockout Signal:** OOS + half-weighted low-stock rate for
          XS/S/M variants vs. larger sizes.
        - All four components are equal-weighted in the composite.
          Adjust weights in `scoring/risk_model.py:DEFAULT_WEIGHTS`.
        """)


def main() -> None:
    theme.inject_css()
    _header()
    run, url, brand, demo1, demo2, demo3 = _input_panel()

    scrape_result = None
    if demo1:
        scrape_result = scrape_fixture("default",
                                       brand or "Mid-Market Specialty Co.")
    elif demo2:
        scrape_result = scrape_fixture("coastal_premium",
                                       brand or "Coastal Premium Denim")
    elif demo3:
        scrape_result = scrape_fixture("mass_basics",
                                       brand or "Mass Basics Co.")
    elif run:
        if not url.strip():
            st.warning("Enter a retailer URL or pick a sample retailer above.")
            return
        scrape_result = _scrape_cached(url.strip(), brand.strip())

    if scrape_result is None:
        st.markdown(
            "<div style='color:#94a3b8; padding:3rem 0; text-align:center;'>"
            "Enter a retailer URL and click <b>Run diagnostic</b>, or load a "
            "sample retailer to see the full output."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    _render_diagnostic(scrape_result, brand)


if __name__ == "__main__":
    main()
