"""Crawl /sale, /clearance, /outlet paths and tag SKUs by size."""
from __future__ import annotations

from typing import Dict, List

from bs4 import BeautifulSoup

from .size_extractor import _normalize

CLEARANCE_PATHS = ["/sale", "/clearance", "/outlet", "/collections/sale",
                   "/collections/clearance", "/collections/outlet",
                   "/collections/final-sale"]


def extract_clearance(html: str) -> List[Dict[str, str]]:
    """Return a list of {sku, size} dicts for SKUs found on a clearance page.

    A "SKU" here is a coarse proxy: every product card with a size variant
    contributes one row per available size.
    """
    soup = BeautifulSoup(html, "lxml")
    items: List[Dict[str, str]] = []

    for card in soup.select(".product-card, .product-item, [data-product-id], "
                            ".grid__item, .product-grid-item, article.product"):
        sku = (card.get("data-product-id") or card.get("data-sku")
               or (card.find("a") or {}).get("href") or "unknown")
        sku = str(sku).split("?")[0][-32:]
        for el in card.select("[data-size], [data-value], .swatch--size, "
                              ".size-option, .product-form__option button, "
                              "option"):
            size = _normalize(el.get("data-size") or el.get("data-value")
                              or el.text)
            if size:
                items.append({"sku": sku, "size": size})

    # Fallback: if no card structure, harvest size labels page-wide.
    if not items:
        for el in soup.select("[data-size], [data-value]"):
            size = _normalize(el.get("data-size") or el.get("data-value"))
            if size:
                items.append({"sku": "page", "size": size})

    return items
