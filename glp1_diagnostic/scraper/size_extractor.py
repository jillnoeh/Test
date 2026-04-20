"""Pull a normalized size mix from a product page.

Looks for three common patterns:
  1. Shopify variant JSON in window.ShopifyAnalytics or ld+json Product blocks.
  2. <select name="size"> dropdowns and size-button groups.
  3. Schema.org `offers` / `availability` markup.
"""
from __future__ import annotations

import json
import re
from typing import Dict, Iterable

from bs4 import BeautifulSoup

CANONICAL_SIZES = ["XS", "S", "M", "L", "XL", "1X", "2X", "3X+"]

# Map common variant labels to our canonical buckets.
SIZE_ALIASES = {
    "xxs": "XS", "xs": "XS",
    "small": "S", "s": "S", "sm": "S",
    "medium": "M", "m": "M", "md": "M",
    "large": "L", "l": "L", "lg": "L",
    "xl": "XL", "x-large": "XL", "x large": "XL", "extra large": "XL",
    "1x": "1X", "1xl": "1X", "xxl": "1X",
    "2x": "2X", "2xl": "2X", "xxxl": "2X",
    "3x": "3X+", "3xl": "3X+", "xxxxl": "3X+", "4x": "3X+", "4xl": "3X+",
    "5x": "3X+",
}

# Numeric size buckets (women's): rough mapping to letter sizes.
NUMERIC_TO_LETTER = {
    0: "XS", 2: "XS", 4: "S", 6: "S", 8: "M", 10: "M", 12: "L", 14: "L",
    16: "XL", 18: "1X", 20: "1X", 22: "2X", 24: "2X", 26: "3X+", 28: "3X+",
    30: "3X+",
}


def _normalize(token: str) -> str | None:
    if not token:
        return None
    t = str(token).strip().lower()
    if t in SIZE_ALIASES:
        return SIZE_ALIASES[t]
    # Plain integer (women's numeric size).
    if re.fullmatch(r"\d{1,2}", t):
        n = int(t)
        if n in NUMERIC_TO_LETTER:
            return NUMERIC_TO_LETTER[n]
    # Strip common decorations like "Size: M" or "M (in stock)".
    m = re.search(r"\b(xxs|xs|s|sm|small|m|md|medium|l|lg|large|xl|x-large|"
                  r"1x|1xl|xxl|2x|2xl|xxxl|3x|3xl|xxxxl|4x|4xl|5x)\b", t)
    if m:
        return SIZE_ALIASES.get(m.group(1))
    return None


def _from_jsonld(soup: BeautifulSoup) -> Iterable[str]:
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            payload = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("@type") not in {"Product", "ProductGroup"}:
                continue
            offers = item.get("offers") or []
            if isinstance(offers, dict):
                offers = [offers]
            for offer in offers:
                if not isinstance(offer, dict):
                    continue
                for key in ("size", "name", "sku"):
                    val = offer.get(key)
                    if val:
                        norm = _normalize(val)
                        if norm:
                            yield norm
            # Some sites put sizes on `hasVariant`.
            for variant in item.get("hasVariant", []) or []:
                if isinstance(variant, dict):
                    for key in ("size", "name"):
                        val = variant.get(key)
                        if val:
                            norm = _normalize(val)
                            if norm:
                                yield norm


def _from_shopify(html: str) -> Iterable[str]:
    # Shopify exposes /products/<handle>.json with variants[].option1 = size.
    for match in re.finditer(r'"option1":"([^"]+)"', html):
        norm = _normalize(match.group(1))
        if norm:
            yield norm


def _from_buttons(soup: BeautifulSoup) -> Iterable[str]:
    # Common patterns: <button data-size="M">, <li class="size">M</li>,
    # <select name="size"><option>M</option></select>.
    for el in soup.select("[data-size], [data-value], .swatch--size, "
                          ".size-option, .product-form__option button"):
        for attr in ("data-size", "data-value"):
            val = el.get(attr)
            if val:
                norm = _normalize(val)
                if norm:
                    yield norm
        if el.text:
            norm = _normalize(el.text)
            if norm:
                yield norm
    for select in soup.select("select"):
        name = (select.get("name") or "") + " " + (select.get("id") or "")
        if "size" in name.lower():
            for opt in select.find_all("option"):
                norm = _normalize(opt.text)
                if norm:
                    yield norm


def extract_sizes(html: str) -> Dict[str, int]:
    """Return a count of canonical-size mentions found on the page.

    The count is a proxy for "how many SKUs offered at this size" — a page
    listing one product with sizes XS/S/M will contribute 1 to each. A
    collection page listing 40 products * 5 sizes will contribute 40 to each.
    """
    soup = BeautifulSoup(html, "lxml")
    counts = {s: 0 for s in CANONICAL_SIZES}
    for src in (_from_jsonld(soup), _from_shopify(html), _from_buttons(soup)):
        for size in src:
            counts[size] = counts.get(size, 0) + 1
    return counts
