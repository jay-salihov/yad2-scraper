# Automated Testing Suite Implementation Plan

## Overview

Create a comprehensive pytest-based testing suite for the yad2-scraper project that validates all 12 documented issues in `known-issues.md` and establishes a maintainable test infrastructure following Python best practices.

---

## Project Structure (After Implementation)

```
yad2-scraper/
├── src/yad2_scraper/          # Existing production code
├── tests/                      # NEW: Test suite
│   ├── __init__.py
│   ├── conftest.py            # Shared pytest fixtures
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── sample_data.py     # Realistic Yad2 JSON structures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_models.py     # Tests Issues 3-9, 12
│   │   ├── test_parser.py     # Tests Issue 11
│   │   ├── test_fetcher.py    # Tests Issue 2
│   │   └── test_exporter.py   # CSV export & deduplication
│   └── integration/
│       ├── __init__.py
│       ├── test_cli.py        # Tests Issue 10
│       └── test_flow.py       # Tests Issue 1 + end-to-end
├── pyproject.toml             # UPDATED: Add test dependencies & pytest config
└── htmlcov/                   # Generated coverage report
```

---

## Critical Files to Create/Modify

### 1. pyproject.toml (MODIFY)
**Path**: `/home/jay/Projects/Active/yad2-scraper/pyproject.toml`

Add test dependencies and pytest configuration:

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "pytest-mock>=3.12",
    "respx>=0.21",           # httpx mocking
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=yad2_scraper",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "unit: Unit tests for individual functions",
    "integration: Integration tests for workflows",
]
```

### 2. tests/conftest.py (CREATE)
**Path**: `/home/jay/Projects/Active/yad2-scraper/tests/conftest.py`

**Purpose**: Central pytest fixtures for all test files

**Key Fixtures**:
- `sample_listing_complete()` - Listing dict with correct nested paths for all fields
- `sample_next_data()` - Full `__NEXT_DATA__` JSON with all 5 feed arrays
- `sample_html()` - Valid HTML with embedded JSON
- `temp_output_dir(tmp_path)` - Temporary CSV export directory

### 3. tests/fixtures/sample_data.py (CREATE)
**Path**: `/home/jay/Projects/Active/yad2-scraper/tests/fixtures/sample_data.py`

**Purpose**: Realistic Yad2 JSON data structures

**Key Data**:
```python
LISTING_COMPLETE = {
    "token": "test-12345",
    "orderId": "98765",
    "price": "45000",
    "manufacturer": {"id": 38, "text": "סיטרואן"},        # Nested
    "model": {"id": 451, "text": "C3"},                   # Nested
    "subModel": {"id": 789, "text": "Shine"},             # Nested
    "vehicleDates": {"yearOfProduction": 2021},           # Issue 4
    "engineType": {"id": 1101, "text": "בנזין"},          # Nested
    "engineVolume": "1200",
    "hand": {"id": 1, "text": "יד ראשונה"},              # Nested
    "handNumber": "1",
    "address": {                                          # Issue 5
        "area": {"id": 5, "text": "תל אביב והמרכז"}
    },
    "metaData": {                                         # Issue 6
        "images": [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg"
        ],
        "coverImage": "https://example.com/cover.jpg"
    },
    "tags": [                                             # Issue 7
        {"name": "חסכוני", "id": 11, "priority": 1}      # Uses "name"
    ],
    "customer": {                                         # Issue 8
        "agencyName": "מוסך דוד",
        "id": "agency-123"
    },
    "packages": {                                         # Issue 9
        "isTradeInButton": True
    },
    "priority": "5"
}

NEXT_DATA_WITH_ALL_ARRAYS = {
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [{
                    "queryKey": ["feed", "vehicles", "search"],
                    "state": {
                        "data": {
                            "commercial": [LISTING_COMPLETE],
                            "private": [LISTING_COMPLETE],
                            "platinum": [LISTING_COMPLETE],  # Issue 11
                            "boost": [],
                            "solo": [],
                            "pagination": {"pages": 35, "total": 1347}
                        }
                    }
                }]
            }
        }
    }
}
```

### 4. tests/unit/test_models.py (CREATE)
**Path**: `/home/jay/Projects/Active/yad2-scraper/tests/unit/test_models.py`

**Purpose**: Test `CarListing.from_raw()` field extraction (Issues 3-9, 12)

**Test Coverage** (~30 tests):

```python
# Issue 3: Nested dict fields (6 tests)
def test_manufacturer_extracts_text_not_dict()
def test_manufacturer_id_extracts_id()
def test_model_extracts_text_not_dict()
def test_sub_model_extracts_text_not_dict()
def test_engine_type_extracts_text_not_dict()
def test_hand_extracts_text_not_dict()

# Issue 4: Year field (1 test)
def test_year_from_vehicle_dates_year_of_production()

# Issue 5: Area fields (2 tests)
def test_area_from_address_area_text()
def test_area_id_from_address_area_id()

# Issue 6: Images (2 tests)
def test_image_count_from_metadata_images()
def test_cover_image_url_from_metadata_cover_image()

# Issue 7: Tags (1 test)
def test_tags_extract_name_not_text()

# Issue 8: Agency (2 tests)
def test_agency_name_from_customer_agency_name()
def test_agency_customer_id_from_customer_id()

# Issue 9: Trade-in (1 test)
def test_has_trade_in_from_packages_is_trade_in_button()

# Issue 12: Missing fields (1 test)
def test_optional_fields_missing_data_no_crash()

# Additional tests (10 tests)
def test_g_helper_handles_none()
def test_g_helper_handles_missing_keys()
def test_csv_header_all_fields()
def test_csv_row_all_strings()
...
```

**Current Bug Reference** (from models.py:53-115):
- Line 88: `g("manufacturer")` → should be `g("manufacturer", "text")`
- Line 89: `g("manufacturerId")` → should be `g("manufacturer", "id")`
- Line 90-93: Similar issues for model, sub_model
- Line 94: `g("year")` → should be `g("vehicleDates", "yearOfProduction")`
- Line 95-96: Similar for engine_type
- Line 98: `g("hand")` → should be `g("hand", "text")`
- Line 105: `g("area")` → should be `g("address", "area", "text")`
- Line 106: `g("areaId")` → should be `g("address", "area", "id")`
- Line 74-75: Images from `raw.get("images")` → should be `raw.get("metaData", {}).get("images", [])`
- Line 71: Tags use `t.get("text", t)` → should be `t.get("name", t)`
- Line 110-111: Agency from `g("agency", "name")` → should be `g("customer", "agencyName")`
- Line 113: `g("metaData", "tradeIn")` → should be `g("packages", "isTradeInButton")`

### 5. tests/unit/test_parser.py (CREATE)
**Path**: `/home/jay/Projects/Active/yad2-scraper/tests/unit/test_parser.py`

**Purpose**: Test JSON extraction and listing parsing (Issue 11)

**Test Coverage** (~12 tests):

```python
# Issue 11: Missing feed arrays (3 tests)
def test_parse_listings_includes_platinum_array()
def test_parse_listings_includes_boost_array()
def test_parse_listings_includes_solo_array()

# Core parsing (9 tests)
def test_extract_next_data_valid_html()
def test_extract_next_data_missing_raises_error()
def test_extract_next_data_malformed_json_raises()
def test_find_feed_query_finds_correct_query()
def test_parse_listings_extracts_pagination()
def test_parse_listings_handles_empty_arrays()
def test_parse_listings_skips_items_without_token()
def test_parse_listings_handles_parse_errors_gracefully()
def test_parse_listings_logs_failed_items()
```

**Current Bug Reference** (from parser.py:73):
- Line 73: `for ad_type in ("commercial", "private"):` → should include "platinum", "boost", "solo"

### 6. tests/unit/test_fetcher.py (CREATE)
**Path**: `/home/jay/Projects/Active/yad2-scraper/tests/unit/test_fetcher.py`

**Purpose**: Test HTTP client and error handling (Issue 2)

**Test Coverage** (~10 tests):

```python
# Issue 2: Unhandled HTTP errors (3 tests)
def test_fetch_page_404_raises_http_status_error()
def test_fetch_page_500_raises_http_status_error()
def test_fetch_page_403_raises_http_status_error()

# Additional fetcher tests (7 tests)
def test_fetch_page_200_success()
def test_fetch_page_302_retries_with_backoff()
def test_fetch_exhausts_retries_raises_bot_detected()
def test_rate_limiting_delays_requests()
def test_no_delay_on_first_request()
def test_context_manager_closes_client()
def test_fetcher_headers_correct()
```

**Mocking Strategy**: Use `respx` library to mock httpx requests
```python
import respx
import httpx

def test_fetch_page_404_raises_http_status_error(respx_mock):
    respx_mock.get("https://www.yad2.co.il/vehicles/cars").mock(
        return_value=httpx.Response(404)
    )

    fetcher = Fetcher()
    with pytest.raises(httpx.HTTPStatusError):
        fetcher.fetch_page(1)
```

### 7. tests/unit/test_exporter.py (CREATE)
**Path**: `/home/jay/Projects/Active/yad2-scraper/tests/unit/test_exporter.py`

**Purpose**: Test CSV export and deduplication

**Test Coverage** (~8 tests):
- `test_export_csv_creates_file()`
- `test_export_csv_includes_header()`
- `test_export_csv_deduplicates_by_token()`
- `test_export_csv_preserves_order()`
- `test_export_csv_uses_utf8_bom()`
- `test_export_csv_creates_output_dir()`
- `test_export_csv_timestamp_format()`
- `test_export_csv_handles_empty_list()`

### 8. tests/integration/test_cli.py (CREATE)
**Path**: `/home/jay/Projects/Active/yad2-scraper/tests/integration/test_cli.py`

**Purpose**: Test CLI arguments and logging (Issue 10)

**Test Coverage** (~6 tests):

```python
# Issue 10: Verbose logging (2 tests)
def test_verbose_sets_debug_on_yad2_scraper_logger_only()
def test_verbose_does_not_flood_with_httpcore_logs()

# CLI tests (4 tests)
def test_max_pages_argument_parsing()
def test_no_max_pages_defaults_to_none()
def test_logging_format_includes_timestamp()
def test_default_logging_level_is_info()
```

**Current Bug Reference** (from __main__.py):
- Verbose mode uses `logging.basicConfig(level=logging.DEBUG)` which sets root logger
- Should use `logging.getLogger("yad2_scraper").setLevel(logging.DEBUG)` instead

### 9. tests/integration/test_flow.py (CREATE)
**Path**: `/home/jay/Projects/Active/yad2-scraper/tests/integration/test_flow.py`

**Purpose**: End-to-end scraping flow (Issue 1)

**Test Coverage** (~8 tests):

```python
# Issue 1: Pagination (2 tests)
def test_pagination_starts_at_page_1_not_0()
def test_max_pages_counts_pages_fetched_not_index()

# Integration tests (6 tests)
def test_full_scraping_flow_with_mocked_responses()
def test_scraping_handles_bot_detection_gracefully()
def test_scraping_handles_parse_errors_gracefully()
def test_scraping_stops_on_empty_page()
def test_scraping_respects_max_pages()
def test_no_listings_exits_with_code_1()
```

**Current Bug Reference** (from __main__.py):
- Pagination likely starts at `page=0` which returns 404
- Should start at `page=1`
- `--max-pages` logic needs to count pages fetched, not page numbers

---

## Implementation Steps

### Step 1: Setup Test Infrastructure
1. Create `tests/` directory structure:
   - `tests/__init__.py`
   - `tests/fixtures/__init__.py`
   - `tests/unit/__init__.py`
   - `tests/integration/__init__.py`

2. Update `pyproject.toml`:
   - Add `[project.optional-dependencies]` with test group
   - Add `[tool.pytest.ini_options]` configuration

3. Install test dependencies:
   ```bash
   pip install -e ".[test]"
   ```

### Step 2: Create Fixtures
1. Create `tests/fixtures/sample_data.py`:
   - `LISTING_COMPLETE` dict with all nested structures
   - `NEXT_DATA_WITH_ALL_ARRAYS` dict
   - Helper functions to generate variations

2. Create `tests/conftest.py`:
   - `@pytest.fixture` for `sample_listing_complete`
   - `@pytest.fixture` for `sample_next_data`
   - `@pytest.fixture` for `sample_html`
   - `@pytest.fixture` for `temp_output_dir`

### Step 3: Unit Tests (Models)
1. Create `tests/unit/test_models.py`:
   - Write ~30 tests covering all field extractions
   - Focus on Issues 3-9, 12
   - Test the `g()` helper function
   - Test CSV serialization methods

**Expected Result**: All tests should FAIL initially because bugs exist

### Step 4: Unit Tests (Parser)
1. Create `tests/unit/test_parser.py`:
   - Write ~12 tests for JSON extraction and parsing
   - Focus on Issue 11 (missing feed arrays)
   - Test error handling for malformed HTML/JSON

**Expected Result**: Tests for platinum/boost/solo should FAIL

### Step 5: Unit Tests (Fetcher)
1. Create `tests/unit/test_fetcher.py`:
   - Write ~10 tests with respx mocking
   - Focus on Issue 2 (unhandled HTTP errors)
   - Test rate limiting and bot detection

**Expected Result**: Tests should PASS (fetcher error handling might already work)

### Step 6: Unit Tests (Exporter)
1. Create `tests/unit/test_exporter.py`:
   - Write ~8 tests for CSV export
   - Test deduplication logic
   - Test UTF-8 BOM encoding

**Expected Result**: Tests should mostly PASS

### Step 7: Integration Tests (CLI)
1. Create `tests/integration/test_cli.py`:
   - Write ~6 tests for CLI and logging
   - Focus on Issue 10 (verbose logging flood)
   - Use `unittest.mock.patch` for mocking

**Expected Result**: Verbose logging test should FAIL

### Step 8: Integration Tests (Flow)
1. Create `tests/integration/test_flow.py`:
   - Write ~8 end-to-end tests
   - Focus on Issue 1 (pagination starting at 0)
   - Mock full scraping flow with respx

**Expected Result**: Pagination test should FAIL

### Step 9: Run Tests and Verify Coverage
```bash
pytest                          # Run all tests
pytest --cov --cov-report=html  # With coverage report
open htmlcov/index.html         # View coverage
```

**Expected Coverage**:
- models.py: 100%
- parser.py: 100%
- fetcher.py: 95%+
- exporter.py: 100%
- Overall: 85%+

### Step 10: Document Test Suite
Add to README.md or create TESTING.md:
```markdown
## Running Tests

# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Run with coverage
pytest --cov --cov-report=html

# Run only unit tests
pytest -m unit

# Run specific issue tests
pytest -k "issue_3"
```

---

## Test Execution Commands

```bash
# Install dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov --cov-report=term-missing --cov-report=html

# Run tests for specific issue
pytest -k "manufacturer"  # Issue 3 tests
pytest -k "pagination"    # Issue 1 tests
pytest -k "verbose"       # Issue 10 tests

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test function
pytest tests/unit/test_models.py::test_manufacturer_extracts_text_not_dict
```

---

## Success Criteria

1. **All 12 known issues have dedicated test coverage**
2. **Tests fail initially** (proving they catch the bugs)
3. **Test suite runs in < 5 seconds** (with mocked HTTP)
4. **Coverage >= 85%** overall
5. **Zero external dependencies** during test runs (everything mocked)
6. **Clear test names** that describe what they validate
7. **Fixtures are reusable** across test files
8. **Documentation** explains how to run tests

---

## Testing Best Practices Applied

✅ **Isolation**: No real HTTP requests, all mocked with respx
✅ **Fast**: Complete test suite runs in seconds
✅ **Deterministic**: No flaky tests, reproducible results
✅ **Readable**: Descriptive test names with issue numbers
✅ **Maintainable**: Centralized fixtures in conftest.py
✅ **Comprehensive**: Unit + integration + coverage reporting
✅ **Industry Standard**: pytest with standard plugins
✅ **CI-Ready**: Can integrate with GitHub Actions easily

---

## Files Summary

**Create (10 new files)**:
- `tests/__init__.py`
- `tests/conftest.py` (~100 lines)
- `tests/fixtures/__init__.py`
- `tests/fixtures/sample_data.py` (~150 lines)
- `tests/unit/__init__.py`
- `tests/unit/test_models.py` (~400 lines)
- `tests/unit/test_parser.py` (~200 lines)
- `tests/unit/test_fetcher.py` (~150 lines)
- `tests/unit/test_exporter.py` (~120 lines)
- `tests/integration/__init__.py`
- `tests/integration/test_cli.py` (~100 lines)
- `tests/integration/test_flow.py` (~150 lines)

**Modify (1 file)**:
- `pyproject.toml` (add ~30 lines)

**Total**: ~1,400 lines of test code

---

## Notes

- Tests document expected behavior and serve as regression prevention
- Tests will initially FAIL, proving they catch the documented bugs
- After fixing the bugs in production code, tests should PASS
- The test suite becomes the specification for correct behavior
- Coverage reports identify untested code paths
