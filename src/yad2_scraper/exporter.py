"""Write CarListing list to CSV with UTF-8 BOM."""

from __future__ import annotations

import csv
import logging
import os
from datetime import datetime
from pathlib import Path

from yad2_scraper.config import CSV_ENCODING, OUTPUT_DIR
from yad2_scraper.models import CarListing

log = logging.getLogger(__name__)


def export_csv(listings: list[CarListing]) -> Path:
    """Deduplicate by token and write listings to a timestamped CSV file.

    Returns the path to the written file.
    """
    # Deduplicate — promoted listings can appear on multiple pages
    seen: set[str] = set()
    unique: list[CarListing] = []
    for listing in listings:
        if listing.token and listing.token not in seen:
            seen.add(listing.token)
            unique.append(listing)

    dupes = len(listings) - len(unique)
    if dupes:
        log.info("Removed %d duplicate listings (by token)", dupes)

    # Ensure output directory exists
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = out_dir / f"yad2_cars_{timestamp}.csv"

    with open(filename, "w", newline="", encoding=CSV_ENCODING) as f:
        writer = csv.writer(f)
        writer.writerow(CarListing.csv_header())
        for listing in unique:
            writer.writerow(listing.csv_row())

    log.info("Wrote %d listings to %s", len(unique), filename)
    return filename
