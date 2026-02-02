# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

yad2-scraper is a Python scraper that extracts used car listings from yad2.co.il (Israeli classifieds) and exports to CSV. The site embeds listing data in a `__NEXT_DATA__` JSON blob in the HTML, so no headless browser is needed — just HTTP requests and JSON parsing.

## Commands

```bash
# Install in editable mode
pip install -e .

# Run scraper (once __main__.py is implemented)
python -m yad2_scraper -v                    # Full scrape
python -m yad2_scraper --max-pages 1 -v      # Single page test
yad2-scraper -v                              # Via entry point
```

No test suite, linter, or formatter is currently configured.

## Architecture

```
CLI (argparse in __main__.py)
  → fetcher.py  — httpx client with rate limiting, bot detection, session cookies
  → parser.py   — extracts __NEXT_DATA__ JSON, navigates to listing arrays
  → models.py   — CarListing dataclass (28 fields) with from_raw() constructor
  → exporter.py — CSV output with UTF-8 BOM (for Hebrew in Excel), deduplication by token
  → output/yad2_cars_{timestamp}.csv
```

**Data path in the JSON**: `props.pageProps.dehydratedState.queries[*].state.data` → `commercial[]` and `private[]` arrays.

## Key Design Decisions

- **src/ layout**: Package lives under `src/yad2_scraper/` to prevent accidental imports from project root
- **UTF-8 BOM (`utf-8-sig`)**: Required for Hebrew text to render correctly in Excel
- **Deduplication by token**: Promoted listings appear across multiple pages
- **Rate limiting**: Random 3-7s delays between requests; exponential backoff (10s/20s/40s) on bot detection (302 redirects from Perfdive/ShieldSquare)
- **Browser mimicry**: Chrome 131 headers, HTTP/2 via httpx, Hebrew locale, Sec-Fetch-* headers
- **Nested field access**: `g(*keys)` helper in models.py for safe deep JSON traversal

## Implementation Status

The full implementation plan and status is in `scraping-implementation-plan.md`.
Testing suite implementation plan and status is in 'testing-suite-implementation.md'

## Search Parameters (config.py)

Year 2020-2023, price 20,000-60,000 NIS, petrol/diesel engines, automatic transmission only. Pagination: pages 0-34, ~40 listings per page, ~1,347 total.

## Version Control

- the project is version controlled on github
- use feature branches when developing new features
- commit often
- main branch should always have a fully tested and working version
