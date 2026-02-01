"""Constants: base URL, search params, headers, delay settings."""

BASE_URL = "https://www.yad2.co.il/vehicles/cars"

DEFAULT_SEARCH_PARAMS = {
    "year": "2020-2023",
    "price": "20000-60000",
    "engineType": "1101,1102,2101,2102",
    "gearBox": "102",
    "priceOnly": "1",
    "imgOnly": "1",
}

# Chrome-like headers to mimic a real browser session
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

# Rate limiting
DELAY_MIN = 3.0  # seconds
DELAY_MAX = 7.0  # seconds

# Bot detection backoff
BACKOFF_BASE = 10.0  # seconds
BACKOFF_MAX_RETRIES = 3

# Output
OUTPUT_DIR = "output"
CSV_ENCODING = "utf-8-sig"  # UTF-8 with BOM for Excel Hebrew compat
