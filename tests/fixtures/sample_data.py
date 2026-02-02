"""Realistic Yad2 JSON data structures for testing."""

# Complete listing with all nested structures matching actual Yad2 API format
LISTING_COMPLETE = {
    "token": "test-12345",
    "orderId": "98765",
    "price": "45000",
    "manufacturer": {"id": 38, "text": "סיטרואן"},
    "model": {"id": 451, "text": "C3"},
    "subModel": {"id": 789, "text": "Shine"},
    "vehicleDates": {"yearOfProduction": 2021},
    "engineType": {"id": 1101, "text": "בנזין"},
    "engineVolume": "1200",
    "hand": {"id": 1, "text": "יד ראשונה"},
    "handNumber": "1",
    "address": {"area": {"id": 5, "text": "תל אביב והמרכז"}},
    "metaData": {
        "images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
        "coverImage": "https://example.com/cover.jpg",
    },
    "tags": [{"name": "חסכוני", "id": 11, "priority": 1}],
    "customer": {"agencyName": "מוסך דוד", "id": "agency-123"},
    "packages": {"isTradeInButton": True},
    "priority": "5",
    "kilometers": "45000",
    "color": {"id": 7, "text": "שחור"},
    "gearBox": {"id": 2, "text": "אוטומטית"},
    "currentOwnership": "1",
    "previousOwnership": "0",
    "pollutionLevel": {"id": 3, "text": "אירו 6"},
    "ownershipType": {"id": 1, "text": "פרטי"},
    "testValidity": "12/2025",
}

# Listing with missing optional fields to test Issue 12
LISTING_MINIMAL = {
    "token": "test-minimal-001",
    "orderId": "11111",
    "price": "25000",
    "manufacturer": {"id": 10, "text": "טויוטה"},
    "model": {"id": 100, "text": "Corolla"},
    # Missing subModel, vehicleDates, engineType, etc.
}

# Listing with nested field variations
LISTING_NO_SUB_MODEL = {
    "token": "test-no-submodel",
    "orderId": "22222",
    "price": "30000",
    "manufacturer": {"id": 15, "text": "הונדה"},
    "model": {"id": 200, "text": "Civic"},
    "subModel": None,  # Explicitly None
    "vehicleDates": {"yearOfProduction": 2020},
    "engineType": {"id": 1102, "text": "דיזל"},
    "hand": {"id": 2, "text": "יד שנייה"},
    "handNumber": "2",
}

# Listing with agency fields
LISTING_AGENCY = {
    "token": "test-agency-001",
    "orderId": "33333",
    "price": "50000",
    "manufacturer": {"id": 20, "text": "מרצדס"},
    "model": {"id": 300, "text": "C-Class"},
    "customer": {"agencyName": "יוקרה מוטורס", "id": "agency-456"},
}

# Listing without agency (private seller)
LISTING_PRIVATE = {
    "token": "test-private-001",
    "orderId": "44444",
    "price": "35000",
    "manufacturer": {"id": 25, "text": "מאזדה"},
    "model": {"id": 400, "text": "3"},
    "customer": {"id": "private-789"},
}

# Listing with multiple tags
LISTING_WITH_TAGS = {
    "token": "test-tags-001",
    "orderId": "55555",
    "price": "40000",
    "manufacturer": {"id": 30, "text": "קיה"},
    "model": {"id": 500, "text": "Sportage"},
    "tags": [
        {"name": "חסכוני", "id": 11, "priority": 1},
        {"name": "מטופל", "id": 12, "priority": 2},
        {"name": "יד ראשונה", "id": 13, "priority": 3},
    ],
}

# Listing without tags
LISTING_NO_TAGS = {
    "token": "test-no-tags",
    "orderId": "66666",
    "price": "28000",
    "manufacturer": {"id": 35, "text": "ניסאן"},
    "model": {"id": 600, "text": "Qashqai"},
    "tags": [],
}

# Full __NEXT_DATA__ JSON structure with all feed arrays
NEXT_DATA_WITH_ALL_ARRAYS = {
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [
                    {
                        "queryKey": ["feed", "vehicles", "search"],
                        "state": {
                            "data": {
                                "commercial": [LISTING_COMPLETE],
                                "private": [LISTING_MINIMAL],
                                "platinum": [LISTING_AGENCY],
                                "boost": [LISTING_PRIVATE],
                                "solo": [LISTING_WITH_TAGS],
                                "pagination": {"pages": 35, "total": 1347},
                            }
                        },
                    }
                ]
            }
        }
    }
}

# __NEXT_DATA__ with only commercial and private arrays (current bug)
NEXT_DATA_MISSING_ARRAYS = {
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [
                    {
                        "queryKey": ["feed", "vehicles", "search"],
                        "state": {
                            "data": {
                                "commercial": [LISTING_COMPLETE, LISTING_AGENCY],
                                "private": [LISTING_MINIMAL, LISTING_PRIVATE],
                                "pagination": {"pages": 35, "total": 1347},
                            }
                        },
                    }
                ]
            }
        }
    }
}

# __NEXT_DATA__ with empty arrays
NEXT_DATA_EMPTY_ARRAYS = {
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [
                    {
                        "queryKey": ["feed", "vehicles", "search"],
                        "state": {
                            "data": {
                                "commercial": [],
                                "private": [],
                                "platinum": [],
                                "boost": [],
                                "solo": [],
                                "pagination": {"pages": 0, "total": 0},
                            }
                        },
                    }
                ]
            }
        }
    }
}


# Valid HTML with embedded __NEXT_DATA__
def create_html_with_next_data(next_data_dict):
    """Create valid HTML with embedded __NEXT_DATA__ JSON."""
    import json

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Yad2 - Cars</title>
</head>
<body>
    <div id="__next"></div>
    <script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data_dict)}</script>
</body>
</html>"""


SAMPLE_HTML_VALID = create_html_with_next_data(NEXT_DATA_WITH_ALL_ARRAYS)

# HTML with malformed JSON
SAMPLE_HTML_MALFORMED_JSON = """<!DOCTYPE html>
<html>
<head>
    <title>Yad2 - Cars</title>
</head>
<body>
    <div id="__next"></div>
    <script id="__NEXT_DATA__" type="application/json">{malformed json here</script>
</body>
</html>"""

# HTML without __NEXT_DATA__ script
SAMPLE_HTML_NO_NEXT_DATA = """<!DOCTYPE html>
<html>
<head>
    <title>Yad2 - Cars</title>
</head>
<body>
    <div id="__next"></div>
</body>
</html>"""
