"""httpx client wrapper with rate limiting and bot-detection handling."""

from __future__ import annotations

import logging
import random
import time

import httpx

from yad2_scraper.config import (
    BACKOFF_BASE,
    BACKOFF_MAX_RETRIES,
    BASE_URL,
    DEFAULT_SEARCH_PARAMS,
    DELAY_MAX,
    DELAY_MIN,
    HEADERS,
)

log = logging.getLogger(__name__)


class BotDetectedError(Exception):
    """Raised when the site returns a bot-challenge redirect."""


class Fetcher:
    """HTTP client for fetching Yad2 search result pages."""

    def __init__(self) -> None:
        self._client = httpx.Client(
            headers=HEADERS,
            http2=True,
            follow_redirects=False,
            timeout=30.0,
        )
        self._first_request = True

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Fetcher:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def fetch_page(self, page: int) -> str:
        """Fetch a single search results page, returning the HTML.

        Handles rate limiting (random delay between requests) and
        bot detection (exponential backoff on 302 redirects).
        """
        # Rate limiting — skip delay before the very first request
        if not self._first_request:
            delay = random.uniform(DELAY_MIN, DELAY_MAX)
            log.debug("Sleeping %.1fs before request", delay)
            time.sleep(delay)
        self._first_request = False

        params = {**DEFAULT_SEARCH_PARAMS, "page": str(page)}

        for attempt in range(BACKOFF_MAX_RETRIES + 1):
            log.debug("Fetching page %d (attempt %d)", page, attempt + 1)
            resp = self._client.get(BASE_URL, params=params)

            if resp.status_code == 200:
                return resp.text

            if resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("location", "")
                log.warning(
                    "Bot detection: %d redirect to %s (attempt %d/%d)",
                    resp.status_code,
                    location,
                    attempt + 1,
                    BACKOFF_MAX_RETRIES + 1,
                )
                if attempt < BACKOFF_MAX_RETRIES:
                    backoff = BACKOFF_BASE * (2**attempt)
                    log.info("Backing off %.0fs", backoff)
                    time.sleep(backoff)
                    continue
                raise BotDetectedError(
                    f"Bot detection after {BACKOFF_MAX_RETRIES + 1} attempts "
                    f"(last redirect: {location})"
                )

            # Unexpected status
            resp.raise_for_status()

        # Should not reach here, but just in case
        raise BotDetectedError("Exhausted retries")
