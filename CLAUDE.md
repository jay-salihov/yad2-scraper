# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

yad2-scraper is a Python scraper that extracts used car listings from yad2.co.il (Israeli classifieds) and exports to CSV. The site embeds listing data in a `__NEXT_DATA__` JSON blob in the HTML, so no headless browser is needed — just HTTP requests and JSON parsing.

## Commands

```bash
# Install in editable mode
pip install -e .

# Install with dev dependencies (includes ruff, mypy, pre-commit, pytest)
pip install -e ".[dev]"

# Run scraper
python -m yad2_scraper -v                    # Full scrape
python -m yad2_scraper --max-pages 1 -v      # Single page test
yad2-scraper -v                              # Via entry point

# Code quality checks
ruff check .                                 # Lint code
ruff check --fix .                           # Lint and auto-fix
ruff format .                                # Format code
mypy src/yad2_scraper                        # Type check

# Testing
pytest                                       # Run full test suite with coverage
pytest tests/unit                            # Run only unit tests
pytest tests/integration                     # Run only integration tests

# Pre-commit hooks
pre-commit install                           # Install git hooks
pre-commit run --all-files                   # Run all hooks manually
```

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

## Search Parameters (config.py)

Year 2020-2023, price 20,000-60,000 NIS, petrol/diesel engines, automatic transmission only. Pagination: pages 0-34, ~40 listings per page, ~1,347 total.

## Version Control

- the project is version controlled on github
- use feature branches when developing new features
- commit often
- main branch should always have a fully tested and working version

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration. On every push to `main` and all PRs, 6 jobs run in parallel:

1. **Test Suite** - Runs pytest with 98 tests, enforces ≥85% coverage (currently at 97.93%)
2. **Lint (Ruff)** - Validates code quality with ruff linter
3. **Format Check (Ruff)** - Ensures consistent code formatting
4. **Type Check (mypy)** - Validates type annotations
5. **Docker Build** - Ensures Dockerfile builds successfully and image runs
6. **CI Status Check** - Branch protection gate (all jobs must pass)

**Expected runtime:** ~60-75 seconds (parallel execution)

### Interpreting CI Results

- **Green checkmark** - All checks passed, safe to merge
- **Red X** - One or more checks failed, review the logs
- **Yellow dot** - CI is still running, wait for completion

Click on the failing job in the GitHub Actions tab to see detailed error messages and logs.

### Branch Protection

The `main` branch is protected with the following rules:
- All CI status checks must pass before merging
- Branches must be up to date with main before merging
- Conversation resolution required before merging

## Development Workflow

### Initial Setup

1. **Clone the repository and set up virtual environment:**
   ```bash
   git clone <repo-url>
   cd yad2-scraper
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies with dev tools:**
   ```bash
   pip install -e ".[dev,test]"
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit to catch issues early:
- **Ruff** - Auto-fixes linting issues and formats code
- **mypy** - Type checks source code
- **File hygiene** - Removes trailing whitespace, fixes line endings, validates YAML/TOML

If a hook fails, the commit is blocked. Fix the issues and try committing again.

**Bypass hooks (not recommended):**
```bash
git commit --no-verify -m "message"
```

### Quality Checks

Run these checks locally before pushing to ensure CI will pass:

```bash
# Format code
ruff format .

# Lint and auto-fix
ruff check --fix .

# Type check
mypy src/yad2_scraper

# Run tests with coverage
pytest

# Run all pre-commit hooks
pre-commit run --all-files
```

### Commit Best Practices

- **Commit often** - Small, focused commits are easier to review
- **Write descriptive messages** - Explain "why" not "what"
- **Run quality checks** - Let pre-commit hooks catch issues before pushing
- **Test before committing** - Ensure tests pass locally

### Feature Branch Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "Add new feature"  # Pre-commit hooks run automatically
   ```

3. **Push to GitHub:**
   ```bash
   git push -u origin feature/my-new-feature
   ```

4. **Create a Pull Request:**
   - Navigate to GitHub and create a PR from your branch to `main`
   - CI will run automatically on the PR
   - Address any CI failures before requesting review

5. **Merge after approval:**
   - All CI checks must pass (green)
   - All conversations must be resolved
   - Branch must be up to date with main

### Handling CI Failures

If CI fails on your PR:

1. **Check the GitHub Actions tab** to see which job failed
2. **Read the error logs** to understand what went wrong
3. **Fix the issue locally:**
   - Lint errors: `ruff check --fix .`
   - Format errors: `ruff format .`
   - Type errors: Fix issues flagged by `mypy src/yad2_scraper`
   - Test failures: Fix failing tests, ensure `pytest` passes locally
   - Coverage too low: Add tests to increase coverage to ≥85%
4. **Commit and push the fix:**
   ```bash
   git add .
   git commit -m "Fix CI failure"
   git push
   ```
5. **CI will automatically re-run** on the new commit
