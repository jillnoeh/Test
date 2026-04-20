"""Pull store list from common store-locator patterns.

Tries:
  1. JSON-LD `Organization`/`Store` blocks.
  2. Inline JSON arrays referenced by names like "stores", "locations".
  3. <address> blocks with a US state + ZIP nearby.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List

from bs4 import BeautifulSoup

LOCATOR_PATHS = ["/stores", "/store-locator", "/locations", "/find-a-store",
                 "/pages/stores", "/pages/store-locator", "/our-stores"]

ZIP_RE = re.compile(r"\b(\d{5})(?:-\d{4})?\b")
STATE_RE = re.compile(
    r"\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|"
    r"MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|"
    r"VA|WA|WV|WI|WY|DC)\b"
)


def _store(name: str = "", city: str = "", state: str = "",
           zip_: str = "") -> Dict[str, str]:
    return {"name": name.strip(), "city": city.strip(),
            "state": state.strip(), "zip": zip_.strip()}


def _from_jsonld(soup: BeautifulSoup) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            payload = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            if t in {"Store", "LocalBusiness", "Place"}:
                addr = item.get("address") or {}
                if isinstance(addr, list) and addr:
                    addr = addr[0]
                if isinstance(addr, dict):
                    out.append(_store(
                        name=item.get("name", ""),
                        city=addr.get("addressLocality", ""),
                        state=addr.get("addressRegion", ""),
                        zip_=str(addr.get("postalCode", "")),
                    ))
    return out


def _from_inline_json(html: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    # Hunt for arrays of objects with city/state/zip-like keys.
    for match in re.finditer(
        r'\{[^{}]*?"(?:zip|postal|postcode)"\s*:\s*"?(\d{5})[^{}]*?\}',
        html,
    ):
        blob = match.group(0)
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError:
            continue
        zip_ = str(obj.get("zip") or obj.get("postal") or obj.get("postcode")
                   or "")
        out.append(_store(
            name=str(obj.get("name", "")),
            city=str(obj.get("city", "")),
            state=str(obj.get("state", "") or obj.get("region", "")),
            zip_=zip_,
        ))
    return out


def _from_addresses(soup: BeautifulSoup) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for addr in soup.find_all("address"):
        text = addr.get_text(" ", strip=True)
        zip_match = ZIP_RE.search(text)
        state_match = STATE_RE.search(text)
        if not zip_match or not state_match:
            continue
        # City = the token between the previous comma and the state.
        before = text[: state_match.start()].rstrip(", ").split(",")
        city = before[-1].strip() if before else ""
        out.append(_store(
            name="",
            city=city,
            state=state_match.group(1),
            zip_=zip_match.group(1),
        ))
    return out


def extract_stores(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    seen: set[tuple] = set()
    out: List[Dict[str, str]] = []
    for src in (_from_jsonld(soup), _from_inline_json(html),
                _from_addresses(soup)):
        for store in src:
            if not store["zip"]:
                continue
            key = (store["zip"], store["city"], store["name"])
            if key in seen:
                continue
            seen.add(key)
            out.append(store)
    return out
