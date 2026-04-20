"""Top-level scraper. Tries static HTML, escalates to Playwright, then
falls back to a demo fixture so the diagnostic always has something to
render. Exposes a single dataclass + a single function."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests

from . import (
    clearance_extractor,
    demo_fixtures,
    size_extractor,
    stock_extractor,
    store_locator,
)

log = logging.getLogger(__name__)

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/123.0 Safari/537.36 "
              "GLP1RiskDiagnostic/1.0")

# Paths we try in order on the retailer's domain.
PRODUCT_PATHS = ["/", "/collections/all", "/collections/womens",
                 "/collections/mens", "/products"]


@dataclass
class ScrapeResult:
    url: str
    brand: str
    sizes_offered: Dict[str, int] = field(default_factory=dict)
    stock_by_size: Dict[str, Dict[str, int]] = field(default_factory=dict)
    clearance_items: List[Dict[str, str]] = field(default_factory=list)
    stores: List[Dict[str, str]] = field(default_factory=list)
    is_demo: bool = False
    notes: List[str] = field(default_factory=list)


def _origin(url: str) -> str:
    p = urlparse(url if "://" in url else f"https://{url}")
    return f"{p.scheme}://{p.netloc}"


def _get(url: str, timeout: int = 10) -> Optional[str]:
    try:
        r = requests.get(url, timeout=timeout,
                         headers={"User-Agent": USER_AGENT,
                                  "Accept": "text/html,*/*;q=0.8"})
        if r.status_code == 200 and r.text:
            return r.text
    except requests.RequestException as e:
        log.debug("static fetch failed %s: %s", url, e)
    return None


def _static_pass(origin: str) -> ScrapeResult:
    sizes: Dict[str, int] = {}
    stock: Dict[str, Dict[str, int]] = {}
    clearance: List[Dict[str, str]] = []
    stores: List[Dict[str, str]] = []

    for path in PRODUCT_PATHS:
        html = _get(urljoin(origin, path))
        if not html:
            continue
        page_sizes = size_extractor.extract_sizes(html)
        for k, v in page_sizes.items():
            sizes[k] = sizes.get(k, 0) + v
        page_stock = stock_extractor.extract_stock(html)
        for k, buckets in page_stock.items():
            stock.setdefault(k, {"in_stock": 0, "low_stock": 0,
                                 "out_of_stock": 0})
            for b, n in buckets.items():
                stock[k][b] += n
        time.sleep(1.0)  # polite

    for path in clearance_extractor.CLEARANCE_PATHS:
        html = _get(urljoin(origin, path))
        if html:
            clearance.extend(clearance_extractor.extract_clearance(html))
            time.sleep(1.0)

    for path in store_locator.LOCATOR_PATHS:
        html = _get(urljoin(origin, path))
        if html:
            stores.extend(store_locator.extract_stores(html))
            time.sleep(1.0)

    return ScrapeResult(url=origin, brand="", sizes_offered=sizes,
                        stock_by_size=stock, clearance_items=clearance,
                        stores=stores)


def _is_thin(result: ScrapeResult) -> bool:
    products_seen = sum(result.sizes_offered.values())
    return products_seen < 10 or len(result.stores) < 3


def _playwright_pass(origin: str) -> Optional[ScrapeResult]:
    """Render with headless Chromium for sites that need JS to populate
    variants or store lists. Returns None if Playwright isn't installed
    or the browser launch fails."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.info("playwright not installed; skipping JS pass")
        return None

    sizes: Dict[str, int] = {}
    stock: Dict[str, Dict[str, int]] = {}
    clearance: List[Dict[str, str]] = []
    stores: List[Dict[str, str]] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(user_agent=USER_AGENT)
            page = ctx.new_page()
            for path in PRODUCT_PATHS + clearance_extractor.CLEARANCE_PATHS \
                    + store_locator.LOCATOR_PATHS:
                try:
                    page.goto(urljoin(origin, path),
                              timeout=15000, wait_until="domcontentloaded")
                    page.wait_for_timeout(800)
                    html = page.content()
                except Exception as e:
                    log.debug("playwright nav failed %s: %s", path, e)
                    continue
                ps = size_extractor.extract_sizes(html)
                for k, v in ps.items():
                    sizes[k] = sizes.get(k, 0) + v
                pk = stock_extractor.extract_stock(html)
                for k, buckets in pk.items():
                    stock.setdefault(k, {"in_stock": 0, "low_stock": 0,
                                         "out_of_stock": 0})
                    for b, n in buckets.items():
                        stock[k][b] += n
                if path in clearance_extractor.CLEARANCE_PATHS:
                    clearance.extend(clearance_extractor.extract_clearance(html))
                if path in store_locator.LOCATOR_PATHS:
                    stores.extend(store_locator.extract_stores(html))
            browser.close()
    except Exception as e:
        log.warning("playwright pass failed: %s", e)
        return None

    return ScrapeResult(url=origin, brand="", sizes_offered=sizes,
                        stock_by_size=stock, clearance_items=clearance,
                        stores=stores)


def scrape(url: str, brand: str = "") -> ScrapeResult:
    """Scrape a retailer URL. Always returns a populated ScrapeResult; if
    live extraction is too thin, returns the bundled demo fixture with
    `is_demo=True` so the UI can show a banner.
    """
    if not url.strip():
        result = ScrapeResult(url="", brand=brand or "Demo Retailer")
        _apply_fixture(result, demo_fixtures.DEFAULT_RETAILER,
                       reason="no URL provided")
        return result

    origin = _origin(url)
    result = _static_pass(origin)
    result.brand = brand or urlparse(origin).netloc.replace("www.", "")

    if _is_thin(result):
        result.notes.append("Static scrape was thin; trying headless browser.")
        js = _playwright_pass(origin)
        if js is not None:
            # Merge JS findings into result (they win on overlap).
            for k, v in js.sizes_offered.items():
                result.sizes_offered[k] = result.sizes_offered.get(k, 0) + v
            for k, buckets in js.stock_by_size.items():
                result.stock_by_size.setdefault(
                    k, {"in_stock": 0, "low_stock": 0, "out_of_stock": 0})
                for b, n in buckets.items():
                    result.stock_by_size[k][b] += n
            result.clearance_items.extend(js.clearance_items)
            result.stores.extend(js.stores)

    if _is_thin(result):
        _apply_fixture(result, demo_fixtures.DEFAULT_RETAILER,
                       reason="Live scrape returned insufficient data; "
                              "using demo fixture so the diagnostic can render.")
    return result


def _apply_fixture(result: ScrapeResult, fixture: dict, reason: str) -> None:
    result.sizes_offered = dict(fixture["sizes_offered"])
    result.stock_by_size = {k: dict(v) for k, v in fixture["stock_by_size"].items()}
    result.clearance_items = list(fixture["clearance_items"])
    result.stores = list(fixture["stores"])
    result.is_demo = True
    result.notes.append(reason)


def scrape_fixture(name: str, brand: str = "") -> ScrapeResult:
    """Bypass live scraping and return a named demo fixture directly.
    Useful for the 'Try a sample retailer' button in the UI."""
    fixture = demo_fixtures.FIXTURES.get(name, demo_fixtures.DEFAULT_RETAILER)
    result = ScrapeResult(url="", brand=brand or name.replace("_", " ").title())
    _apply_fixture(result, fixture, reason=f"Loaded demo fixture: {name}")
    return result
