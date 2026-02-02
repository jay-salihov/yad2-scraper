"""Entry point for `python -m yad2_scraper`."""

from __future__ import annotations

import argparse
import logging
import sys

from yad2_scraper.exporter import export_csv
from yad2_scraper.fetcher import BotDetectedError, Fetcher
from yad2_scraper.models import CarListing
from yad2_scraper.parser import parse_listings

log = logging.getLogger("yad2_scraper")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="yad2-scraper",
        description="Scrape used car listings from yad2.co.il and export to CSV.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of pages to scrape (default: all)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging",
    )
    args = parser.parse_args(argv)

    level = logging.DEBUG if args.verbose else logging.INFO

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )

    # Explicitly set our logger level (basicConfig may be a no-op if handlers exist)
    log.setLevel(level)

    all_listings: list[CarListing] = []
    total_pages: int | None = None

    try:
        with Fetcher() as fetcher:
            page = 0
            while True:
                # Stop if we've hit the user-specified page limit
                if args.max_pages is not None and page >= args.max_pages:
                    log.info("Reached --max-pages limit (%d)", args.max_pages)
                    break

                # Stop if we've gone past the last page (known after first fetch)
                if total_pages is not None and page >= total_pages:
                    log.info("Reached last page (%d)", total_pages)
                    break

                log.info("Fetching page %d ...", page)

                try:
                    html = fetcher.fetch_page(page)
                except BotDetectedError as e:
                    log.error("Stopping: %s", e)
                    break

                try:
                    result = parse_listings(html)
                except ValueError as e:
                    log.error("Parse error on page %d: %s", page, e)
                    break

                all_listings.extend(result.listings)
                log.info(
                    "Page %d: %d listings (running total: %d)",
                    page,
                    len(result.listings),
                    len(all_listings),
                )

                # Learn total pages from the first successful parse
                if total_pages is None and result.total_pages > 0:
                    total_pages = result.total_pages
                    log.info(
                        "Pagination: %d pages, %d total results",
                        result.total_pages,
                        result.total_results,
                    )

                # If a page returned zero listings, we've likely passed the end
                if not result.listings:
                    log.info("Empty page %d — stopping", page)
                    break

                page += 1

    except KeyboardInterrupt:
        log.info("Interrupted — exporting %d listings collected so far", len(all_listings))

    if not all_listings:
        log.warning("No listings scraped — nothing to export")
        sys.exit(1)

    output_path = export_csv(all_listings)
    log.info("Done — %s", output_path)


if __name__ == "__main__":
    main()
