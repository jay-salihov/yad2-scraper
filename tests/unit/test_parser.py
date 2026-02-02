"""Unit tests for parser JSON extraction and listing parsing (Issue 11)."""

import json

import pytest

from yad2_scraper.parser import _find_feed_query, extract_next_data, parse_listings


@pytest.mark.unit
class TestIssue11MissingFeedArrays:
    """Test that parser includes platinum, boost, and solo arrays (Issue 11)."""

    def test_parse_listings_includes_platinum_array(self, sample_next_data):
        """Parser should extract listings from platinum array."""
        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data)}</script>
</body></html>"""

        result = parse_listings(html)

        # Should include listing from platinum array
        tokens = [listing.token for listing in result.listings]
        assert "test-agency-001" in tokens, "Platinum listing should be included"

    def test_parse_listings_includes_boost_array(self, sample_next_data):
        """Parser should extract listings from boost array."""
        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data)}</script>
</body></html>"""

        result = parse_listings(html)

        # Should include listing from boost array
        tokens = [listing.token for listing in result.listings]
        assert "test-private-001" in tokens, "Boost listing should be included"

    def test_parse_listings_includes_solo_array(self, sample_next_data):
        """Parser should extract listings from solo array."""
        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data)}</script>
</body></html>"""

        result = parse_listings(html)

        # Should include listing from solo array
        tokens = [listing.token for listing in result.listings]
        assert "test-tags-001" in tokens, "Solo listing should be included"

    def test_parse_listings_includes_all_five_arrays(self, sample_next_data):
        """Parser should extract listings from all 5 feed arrays."""
        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data)}</script>
</body></html>"""

        result = parse_listings(html)

        # Should have 5 listings total (one from each array)
        assert len(result.listings) == 5, "Should include all 5 listings from all arrays"


@pytest.mark.unit
class TestExtractNextData:
    """Test __NEXT_DATA__ JSON extraction from HTML."""

    def test_extract_next_data_valid_html(self, sample_html_valid):
        """Should extract __NEXT_DATA__ from valid HTML."""
        data = extract_next_data(sample_html_valid)
        assert "props" in data
        assert "pageProps" in data["props"]

    def test_extract_next_data_missing_raises_error(self, sample_html_no_next_data):
        """Should raise ValueError when __NEXT_DATA__ script tag missing."""
        with pytest.raises(ValueError, match="__NEXT_DATA__ script tag not found"):
            extract_next_data(sample_html_no_next_data)

    def test_extract_next_data_malformed_json_raises(self, sample_html_malformed):
        """Should raise JSONDecodeError for malformed JSON."""
        with pytest.raises(json.JSONDecodeError):
            extract_next_data(sample_html_malformed)

    def test_extract_next_data_returns_dict(self, sample_html_valid):
        """Should return a dictionary."""
        data = extract_next_data(sample_html_valid)
        assert isinstance(data, dict)


@pytest.mark.unit
class TestFindFeedQuery:
    """Test _find_feed_query helper function."""

    def test_find_feed_query_finds_correct_query(self, sample_next_data):
        """Should find the query with queryKey starting with 'feed'."""
        queries = sample_next_data["props"]["pageProps"]["dehydratedState"]["queries"]
        feed_query = _find_feed_query(queries)

        assert feed_query is not None
        assert feed_query["queryKey"] == ["feed", "vehicles", "search"]

    def test_find_feed_query_returns_none_when_missing(self):
        """Should return None when no feed query exists."""
        queries = [
            {"queryKey": ["other", "query"]},
            {"queryKey": ["another", "query"]},
        ]
        feed_query = _find_feed_query(queries)
        assert feed_query is None

    def test_find_feed_query_handles_empty_list(self):
        """Should return None for empty queries list."""
        feed_query = _find_feed_query([])
        assert feed_query is None


@pytest.mark.unit
class TestParseListingsPagination:
    """Test pagination info extraction."""

    def test_parse_listings_extracts_pagination(self, sample_next_data):
        """Should extract pagination info correctly."""
        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data)}</script>
</body></html>"""

        result = parse_listings(html)
        assert result.total_pages == 35
        assert result.total_results == 1347

    def test_parse_listings_handles_empty_pagination(self, sample_next_data_empty):
        """Should handle empty pagination correctly."""
        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data_empty)}</script>
</body></html>"""

        result = parse_listings(html)
        assert result.total_pages == 0
        assert result.total_results == 0


@pytest.mark.unit
class TestParseListingsEdgeCases:
    """Test edge cases in listing parsing."""

    def test_parse_listings_handles_empty_arrays(self, sample_next_data_empty):
        """Should handle empty feed arrays without errors."""
        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data_empty)}</script>
</body></html>"""

        result = parse_listings(html)
        assert result.listings == []

    def test_parse_listings_skips_items_without_token(self):
        """Should skip items that don't have a token field."""
        next_data = {
            "props": {
                "pageProps": {
                    "dehydratedState": {
                        "queries": [
                            {
                                "queryKey": ["feed", "vehicles", "search"],
                                "state": {
                                    "data": {
                                        "commercial": [
                                            {"price": "50000"},  # No token
                                            {"token": "valid-123", "price": "40000"},
                                        ],
                                        "private": [],
                                        "pagination": {"pages": 1, "total": 1},
                                    }
                                },
                            }
                        ]
                    }
                }
            }
        }

        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
</body></html>"""

        result = parse_listings(html)
        assert len(result.listings) == 1
        assert result.listings[0].token == "valid-123"

    def test_parse_listings_handles_parse_errors_gracefully(self):
        """Should log and continue when individual listing parsing fails."""
        next_data = {
            "props": {
                "pageProps": {
                    "dehydratedState": {
                        "queries": [
                            {
                                "queryKey": ["feed", "vehicles", "search"],
                                "state": {
                                    "data": {
                                        "commercial": [
                                            {"token": "good-123", "price": "40000"},
                                            "invalid",  # Not a dict
                                        ],
                                        "private": [],
                                        "pagination": {"pages": 1, "total": 2},
                                    }
                                },
                            }
                        ]
                    }
                }
            }
        }

        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
</body></html>"""

        result = parse_listings(html)
        # Should successfully parse the valid listing
        assert len(result.listings) == 1
        assert result.listings[0].token == "good-123"

    def test_parse_listings_no_feed_query(self):
        """Should return empty result when no feed query found."""
        next_data = {"props": {"pageProps": {"dehydratedState": {"queries": []}}}}

        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
</body></html>"""

        result = parse_listings(html)
        assert result.listings == []
        assert result.total_pages == 0
        assert result.total_results == 0


@pytest.mark.unit
class TestParseListingsIntegration:
    """Integration tests for full parsing flow."""

    def test_parse_listings_complete_flow(self, sample_next_data):
        """Should parse complete HTML and return all listings."""
        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data)}</script>
</body></html>"""

        result = parse_listings(html)

        # Verify listings
        assert len(result.listings) > 0
        assert all(listing.token for listing in result.listings)

        # Verify pagination
        assert result.total_pages > 0
        assert result.total_results > 0
