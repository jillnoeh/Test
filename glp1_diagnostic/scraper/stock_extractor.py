"""Detect in-stock / low-stock / out-of-stock signals per size on a page."""
from __future__ import annotations

import json
import re
from typing import Dict

from bs4 import BeautifulSoup

from .size_extractor import CANONICAL_SIZES, _normalize

OOS_TOKENS = re.compile(
    r"(out\s*of\s*stock|sold\s*out|unavailable|notify\s*me|"
    r"oos|outofstock)",
    re.IGNORECASE,
)
LOW_TOKENS = re.compile(
    r"(only\s+\d+\s+left|low\s*stock|hurry|few\s+left|limited)",
    re.IGNORECASE,
)


def _empty_counts() -> Dict[str, Dict[str, int]]:
    return {s: {"in_stock": 0, "low_stock": 0, "out_of_stock": 0}
            for s in CANONICAL_SIZES}


def _bump(counts: Dict[str, Dict[str, int]], size: str, bucket: str) -> None:
    if size in counts:
        counts[size][bucket] = counts[size].get(bucket, 0) + 1


def extract_stock(html: str) -> Dict[str, Dict[str, int]]:
    """Walk size-bearing elements and classify each into a stock bucket."""
    soup = BeautifulSoup(html, "lxml")
    counts = _empty_counts()

    # JSON-LD offers expose availability machine-readably.
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            payload = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue
            offers = item.get("offers") or []
            if isinstance(offers, dict):
                offers = [offers]
            for offer in offers:
                if not isinstance(offer, dict):
                    continue
                size = _normalize(offer.get("size") or offer.get("name"))
                if not size:
                    continue
                avail = (offer.get("availability") or "").lower()
                if "outofstock" in avail or "soldout" in avail:
                    _bump(counts, size, "out_of_stock")
                elif "limitedavailability" in avail or "lowstock" in avail:
                    _bump(counts, size, "low_stock")
                else:
                    _bump(counts, size, "in_stock")

    # Size buttons commonly carry a disabled/sold-out class for OOS variants.
    for el in soup.select("[data-size], [data-value], .swatch--size button, "
                          ".size-option, .product-form__option button"):
        size = _normalize(el.get("data-size") or el.get("data-value")
                          or el.text)
        if not size:
            continue
        cls = " ".join(el.get("class") or [])
        aria_disabled = (el.get("aria-disabled") or "").lower() == "true"
        title = (el.get("title") or "") + " " + (el.get("aria-label") or "")
        if (el.has_attr("disabled") or aria_disabled
                or re.search(r"sold[-_ ]?out|disabled|unavailable", cls, re.I)
                or OOS_TOKENS.search(title)):
            _bump(counts, size, "out_of_stock")
        elif re.search(r"low[-_ ]?stock|limited", cls, re.I) or LOW_TOKENS.search(title):
            _bump(counts, size, "low_stock")
        else:
            _bump(counts, size, "in_stock")

    return counts
