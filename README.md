# yad2-scraper

[![CI](https://github.com/jay-salihov/yad2-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/jay-salihov/yad2-scraper/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-97.93%25-brightgreen)](htmlcov/index.html)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A Python scraper that extracts used car listings from [yad2.co.il](https://www.yad2.co.il) (Israeli classifieds) and exports them to CSV.

## Features

- 🚗 Scrapes car listings from yad2.co.il search results
- 📊 Exports to CSV with UTF-8 BOM encoding (Hebrew-compatible for Excel)
- 🔄 Automatic deduplication of promoted listings across pages
- 🤖 Bot detection handling with exponential backoff
- 🎯 Rate limiting to avoid overwhelming the server
- ✅ 98 automated tests with 97.93% code coverage
- 🔍 Type-checked with mypy
- 🎨 Formatted with ruff

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/jay-salihov/yad2-scraper.git
cd yad2-scraper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

### Usage

```bash
# Full scrape (all pages)
yad2-scraper -v

# Test with single page
yad2-scraper --max-pages 1 -v

# Alternative using Python module
python -m yad2_scraper -v
```

The scraper will create CSV files in the `output/` directory with timestamped filenames like `yad2_cars_2024-01-15_143022.csv`.

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality Checks

```bash
# Format code
ruff format .

# Lint and auto-fix
ruff check --fix .

# Type check
mypy src/yad2_scraper

# Run tests with coverage
pytest
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:
- **ruff** - Auto-fixes linting issues and formats code
- **mypy** - Type checks source code
- **File hygiene** - Removes trailing whitespace, fixes line endings

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration. On every push to `main` and all PRs, the following checks run in parallel:

1. **Test Suite** - 98 tests with ≥85% coverage requirement
2. **Lint** - Code quality validation with ruff
3. **Format Check** - Ensures consistent code formatting
4. **Type Check** - Validates type annotations with mypy
5. **Docker Build** - Ensures Dockerfile builds successfully
6. **CI Status** - Branch protection gate

All checks must pass before merging to `main`.

## Project Structure

```
src/yad2_scraper/
├── __main__.py    # CLI entry point with argparse
├── fetcher.py     # HTTP client with rate limiting & bot detection
├── parser.py      # JSON extraction from __NEXT_DATA__
├── models.py      # CarListing dataclass (28 fields)
├── exporter.py    # CSV export with UTF-8 BOM
└── config.py      # Search parameters

tests/
├── unit/          # Unit tests for individual functions
└── integration/   # Integration tests for workflows
```

## Configuration

Search parameters are configured in `src/yad2_scraper/config.py`:
- **Year:** 2020-2023
- **Price:** 20,000-60,000 NIS
- **Engine:** Petrol/Diesel only
- **Transmission:** Automatic only
- **Pagination:** ~40 listings per page, ~1,347 total across 35 pages

## How It Works

1. **No headless browser needed** - yad2.co.il embeds listing data in a `__NEXT_DATA__` JSON blob in the HTML
2. **HTTP/2 with httpx** - Faster requests with browser-like headers
3. **Rate limiting** - Random 3-7s delays between requests
4. **Bot detection** - Exponential backoff on 302 redirects (10s/20s/40s)
5. **Deduplication** - Promoted listings appear on multiple pages, deduplicated by token
6. **UTF-8 BOM** - Ensures Hebrew text renders correctly in Excel

## Testing

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov=yad2_scraper --cov-report=html
```

**Current test coverage:** 97.93% (241/241 statements)

## License

This project is for educational purposes only. Please respect yad2.co.il's terms of service and use responsibly.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run quality checks (`ruff format . && ruff check --fix . && mypy src/yad2_scraper && pytest`)
5. Commit your changes (pre-commit hooks will run automatically)
6. Push to your fork and create a Pull Request

All PRs must pass CI checks before merging.
