"""Extract __NEXT_DATA__ JSON from HTML, parse listings from dehydratedState."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup

from yad2_scraper.models import CarListing

log = logging.getLogger(__name__)


@dataclass
class PageResult:
    """Parsed result from a single search results page."""

    listings: list[CarListing]
    total_pages: int
    total_results: int


def extract_next_data(html: str) -> dict[str, Any]:
    """Pull the __NEXT_DATA__ JSON blob from the page HTML.

    Returns the parsed dict, or raises ValueError if not found.
    """
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if script is None or not hasattr(script, "string") or not script.string:
        raise ValueError("__NEXT_DATA__ script tag not found — possible bot challenge page")
    return json.loads(script.string)


def _find_feed_query(queries: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Locate the query whose queryKey starts with 'feed'."""
    for q in queries:
        key = q.get("queryKey", [])
        if isinstance(key, list) and key and key[0] == "feed":
            return q
    return None


def parse_listings(html: str) -> PageResult:
    """Parse all car listings and pagination info from a search results page."""
    data = extract_next_data(html)

    queries = (
        data.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [])
    )

    feed_query = _find_feed_query(queries)
    if feed_query is None:
        log.warning("No 'feed' query found in dehydratedState — page may be empty")
        return PageResult(listings=[], total_pages=0, total_results=0)

    state_data = feed_query.get("state", {}).get("data", {})

    # Pagination
    pagination = state_data.get("pagination", {})
    total_pages = int(pagination.get("pages", 0))
    total_results = int(pagination.get("total", 0))

    # Listings from both commercial and private arrays
    listings: list[CarListing] = []

    for ad_type in ("commercial", "private"):
        raw_items = state_data.get(ad_type, [])
        for item in raw_items:
            if not isinstance(item, dict) or not item.get("token"):
                continue
            try:
                listings.append(CarListing.from_raw(item, ad_type))
            except Exception:
                token = item.get("token", "?")
                log.warning("Failed to parse %s listing %s", ad_type, token, exc_info=True)

    log.debug(
        "Parsed %d listings (total_pages=%d, total_results=%d)",
        len(listings),
        total_pages,
        total_results,
    )
    return PageResult(listings=listings, total_pages=total_pages, total_results=total_results)
