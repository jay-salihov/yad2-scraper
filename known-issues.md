# Known Issues

Found during testing on 2026-02-01.

---

## 1. Pagination is 1-based — scraper starts at page 0 and crashes

The scraper starts its pagination loop at `page=0`, but Yad2 uses 1-based pagination.
Requesting `?page=0` returns HTTP 404, which hits the `resp.raise_for_status()` call in
`fetcher.py` and crashes with an unhandled `httpx.HTTPStatusError`.

**Reproduce:**
```
python -m yad2_scraper --max-pages 1 -v
```
Crashes immediately with `HTTPStatusError: Client error '404 Not Found'`.

**Fix direction:** Change the starting page from 0 to 1 in `__main__.py`. Adjust the
`--max-pages` logic accordingly (it should count pages fetched, not compare against
the page index).

---

## 2. Unhandled HTTP errors crash the scraper

`fetcher.py` only handles 200 and 3xx redirect status codes. Any other status (404, 403,
500, etc.) falls through to `resp.raise_for_status()`, which raises an unhandled exception
that propagates all the way up and kills the process with a traceback.

**Reproduce:**
```
python -m yad2_scraper --max-pages 1
```
The page=0 404 triggers this, but any transient server error would do the same.

**Fix direction:** Catch `httpx.HTTPStatusError` in `fetch_page` (or in the caller in
`__main__.py`) and handle it gracefully — log a warning and either retry or skip the page,
rather than crashing.

---

## 3. Nested dict fields serialized as Python repr strings in CSV

Several Yad2 fields (`manufacturer`, `model`, `subModel`, `engineType`, `hand`) are
nested objects like `{"id": 38, "text": "סיטרואן"}`. The `from_raw()` method uses
`g("manufacturer")` which retrieves the whole dict, then `str()` converts it to a Python
repr string. The CSV ends up with values like `{'id': 38, 'text': 'סיטרואן'}` instead of
just `סיטרואן`.

**Affected fields (6):** `manufacturer`, `model`, `sub_model`, `engine_type`, `hand`, and
their `_id` counterparts (which are empty because e.g. `manufacturerId` doesn't exist as a
top-level key — the ID is inside `manufacturer.id`).

**Reproduce:**
```python
from yad2_scraper.config import HEADERS, DEFAULT_SEARCH_PARAMS
from yad2_scraper.parser import parse_listings
import httpx

c = httpx.Client(headers=HEADERS, http2=True, follow_redirects=False, timeout=30.0)
r = c.get("https://www.yad2.co.il/vehicles/cars", params={**DEFAULT_SEARCH_PARAMS, "page": "1"})
c.close()
result = parse_listings(r.text)
print(result.listings[0].manufacturer)  # prints {'id': 38, 'text': 'סיטרואן'}
```

**Fix direction:** In `from_raw()`, use `g("manufacturer", "text")` for the display name
and `g("manufacturer", "id")` for the ID. Same pattern for `model`, `subModel`,
`engineType`, and `hand`.

---

## 4. Year field is empty — wrong JSON path

`from_raw()` reads `g("year")` but the actual JSON structure is
`vehicleDates.yearOfProduction`.

**Reproduce:** Same as issue 3 — `result.listings[0].year` is `""`.

**Fix direction:** Change to `g("vehicleDates", "yearOfProduction")`.

---

## 5. Area fields are empty — wrong JSON path

`from_raw()` reads `g("area")` and `g("areaId")` but the actual structure is
`address.area.text` and `address.area.id`.

**Reproduce:** `result.listings[0].area` is `""`.

**Fix direction:** Change to `g("address", "area", "text")` and
`g("address", "area", "id")`.

---

## 6. Image count is 0 and cover image is empty — wrong JSON path

`from_raw()` reads `raw.get("images")` (top-level), but images are at
`metaData.images` (a list of URL strings, not objects). The cover image is at
`metaData.coverImage` (a direct URL string), not `images[0].get("src")`.

**Reproduce:** `result.listings[0].image_count` is `"0"` and `cover_image_url` is `""`,
even though the raw JSON has 5+ images.

**Fix direction:** Read images from `raw.get("metaData", {}).get("images", [])`. Use
`raw.get("metaData", {}).get("coverImage", "")` for the cover URL. Images are plain URL
strings, not objects.

---

## 7. Tags extract wrong key — "name" vs "text"

Tag objects use `{"name": "חסכוני", "id": 11, "priority": 1}` but the code does
`t.get("text", t)`, so it falls back to stringifying the entire dict.

**Reproduce:** `result.listings[0].tags` contains repr-style dicts instead of
comma-separated tag names.

**Fix direction:** Change `t.get("text", t)` to `t.get("name", t)` in the tags
extraction in `from_raw()`.

---

## 8. Agency fields use wrong JSON path

`from_raw()` reads `g("agency", "name")` and `g("agency", "customerId")` but the actual
structure is `customer.agencyName` and `customer.id`.

**Reproduce:** `result.listings[0].agency_name` is `""` even for commercial listings that
have agency info.

**Fix direction:** Change to `g("customer", "agencyName")` and `g("customer", "id")`.

---

## 9. Trade-in field uses wrong JSON path

`from_raw()` reads `g("metaData", "tradeIn")` but the actual field is
`packages.isTradeInButton` (a boolean).

**Reproduce:** `result.listings[0].has_trade_in` is `""` even for listings where
`packages.isTradeInButton` is `true`.

**Fix direction:** Change to `g("packages", "isTradeInButton")`.

---

## 10. Verbose mode floods output with httpcore/hpack debug logs

Setting `-v` enables `DEBUG` on the root logger, which turns on extremely verbose
internal logging from `httpcore` and `hpack` (TLS handshake details, header encoding
byte counts, etc.). A single failed request produces ~150 lines of noise.

**Reproduce:**
```
python -m yad2_scraper -v --max-pages 1 2>&1 | wc -l
```
Outputs ~150 lines, almost all from `httpcore` and `hpack`.

**Fix direction:** Only set DEBUG level on the `yad2_scraper` logger, not the root logger.
Use `logging.getLogger("yad2_scraper").setLevel(logging.DEBUG)` instead of
`logging.basicConfig(level=logging.DEBUG)`, or explicitly silence `httpcore` and `hpack`
loggers.

---

## 11. Missing feed arrays: platinum, boost, solo are not scraped

The feed data contains `platinum`, `boost`, and `solo` arrays in addition to `commercial`
and `private`. The parser only reads `commercial` and `private`. During testing all three
extra arrays were empty, but they likely contain promoted listings on busier result sets.

**Reproduce:**
```python
# After extracting feed state_data:
print(state_data.keys())  # ['platinum', 'boost', 'solo', 'commercial', 'pagination', 'private']
```

**Fix direction:** Add `"platinum"`, `"boost"`, and `"solo"` to the list of arrays
iterated in `parse_listings()`. Decide whether to use the array key or the item's `adType`
field for the `ad_type` CSV column (note: items in the `private` array currently have
`adType: "commercial"` in their JSON, so the array key is more reliable).

---

## 12. Fields that may not exist in the feed: listingSource, financingInfo, commitments

Three groups of CSV columns are always empty because the corresponding data doesn't appear
in the feed JSON (at least for the tested search params):

- `listing_source` — no `listingSource` key in any listing
- `advance_payment`, `monthly_payment`, `number_of_payments`, `balance` — no
  `metaData.financingInfo` in any listing
- `commitments` — no `metaData.commitments` in any listing

These fields may appear on other search result sets or individual listing detail pages, but
they are not present in the feed data for the current search parameters.

**Reproduce:** Scrape any page and check — all five fields are empty across all listings.

**Fix direction:** Investigate whether these fields appear on listing detail pages (the
feed data is a summary). If they are feed-only fields from a previous API version, consider
removing them from the dataclass, or keep them as optional fields that populate when
available.
