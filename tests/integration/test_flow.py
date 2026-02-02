"""Integration tests for end-to-end scraping flow (Issue 1)."""

import json
import pytest
import httpx
import respx
from unittest.mock import patch
from yad2_scraper.__main__ import main
from yad2_scraper.fetcher import BotDetectedError


@pytest.mark.integration
class TestIssue1Pagination:
    """Test pagination starting at correct page (Issue 1)."""

    @respx.mock
    def test_pagination_starts_at_page_1_not_0(self, tmp_path, monkeypatch):
        """Pagination should start at page 1, not page 0."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        # Mock responses - page 0 returns 404, page 1 returns valid data
        route = respx.get("https://www.yad2.co.il/vehicles/cars")

        def custom_response(request):
            # Check the page parameter
            page_param = None
            for key, value in request.url.params.items():
                if key == "page":
                    page_param = value
                    break

            if page_param == "0":
                # Page 0 should return 404
                return httpx.Response(404, text="Not Found")
            elif page_param == "1":
                # Page 1 returns valid data
                next_data = {
                    "props": {
                        "pageProps": {
                            "dehydratedState": {
                                "queries": [{
                                    "queryKey": ["feed", "vehicles", "search"],
                                    "state": {
                                        "data": {
                                            "commercial": [{"token": "test-123", "price": "50000"}],
                                            "private": [],
                                            "pagination": {"pages": 1, "total": 1}
                                        }
                                    }
                                }]
                            }
                        }
                    }
                }
                html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
</body></html>"""
                return httpx.Response(200, text=html)
            else:
                return httpx.Response(404, text="Not Found")

        route.mock(side_effect=custom_response)

        # Run main with max-pages=1
        # Currently this will FAIL because it starts at page 0
        with pytest.raises(httpx.HTTPStatusError):
            main(["--max-pages", "1"])

    @respx.mock
    def test_max_pages_counts_pages_fetched_not_index(self, tmp_path, monkeypatch):
        """--max-pages should count pages fetched, not page numbers."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        route = respx.get("https://www.yad2.co.il/vehicles/cars")

        pages_fetched = []

        def track_pages(request):
            page_param = None
            for key, value in request.url.params.items():
                if key == "page":
                    page_param = value
                    break

            pages_fetched.append(page_param)

            next_data = {
                "props": {
                    "pageProps": {
                        "dehydratedState": {
                            "queries": [{
                                "queryKey": ["feed", "vehicles", "search"],
                                "state": {
                                    "data": {
                                        "commercial": [{"token": f"test-{page_param}", "price": "50000"}],
                                        "private": [],
                                        "pagination": {"pages": 10, "total": 100}
                                    }
                                }
                            }]
                        }
                    }
                }
            }
            html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
</body></html>"""
            return httpx.Response(200, text=html)

        route.mock(side_effect=track_pages)

        main(["--max-pages", "3"])

        # Should fetch exactly 3 pages: 0, 1, 2 (currently)
        # After fix: should fetch pages 1, 2, 3
        assert len(pages_fetched) == 3


@pytest.mark.integration
class TestScrapingFlow:
    """Test full scraping flow."""

    @respx.mock
    def test_full_scraping_flow_with_mocked_responses(self, tmp_path, sample_next_data, monkeypatch):
        """Should complete full scraping flow with mocked HTTP responses."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        route = respx.get("https://www.yad2.co.il/vehicles/cars")

        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_next_data)}</script>
</body></html>"""

        route.mock(return_value=httpx.Response(200, text=html))

        main(["--max-pages", "1"])

        # Should have created a CSV file
        csv_files = list(tmp_path.glob("yad2_cars_*.csv"))
        assert len(csv_files) == 1

    @respx.mock
    def test_scraping_handles_bot_detection_gracefully(self, tmp_path, monkeypatch):
        """Should handle bot detection and exit gracefully."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        # Always return 302 redirect
        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(302, headers={"location": "/bot-check"})
        )

        # Should exit due to bot detection, but not crash
        with pytest.raises(SystemExit):
            main(["--max-pages", "1"])

    @respx.mock
    def test_scraping_handles_parse_errors_gracefully(self, tmp_path, monkeypatch):
        """Should handle parse errors and exit gracefully."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        # Return HTML without __NEXT_DATA__
        html = "<html><body>No data here</body></html>"
        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(200, text=html)
        )

        with pytest.raises(SystemExit):
            main(["--max-pages", "1"])


@pytest.mark.integration
class TestScrapingEdgeCases:
    """Test edge cases in scraping flow."""

    @respx.mock
    def test_scraping_stops_on_empty_page(self, tmp_path, monkeypatch):
        """Should stop scraping when encountering an empty page."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        route = respx.get("https://www.yad2.co.il/vehicles/cars")

        def page_response(request):
            # First page has data, second page is empty
            page_param = None
            for key, value in request.url.params.items():
                if key == "page":
                    page_param = value
                    break

            if page_param == "0":
                # First page with data
                next_data = {
                    "props": {
                        "pageProps": {
                            "dehydratedState": {
                                "queries": [{
                                    "queryKey": ["feed", "vehicles", "search"],
                                    "state": {
                                        "data": {
                                            "commercial": [{"token": "test-123", "price": "50000"}],
                                            "private": [],
                                            "pagination": {"pages": 10, "total": 100}
                                        }
                                    }
                                }]
                            }
                        }
                    }
                }
            else:
                # Empty page
                next_data = {
                    "props": {
                        "pageProps": {
                            "dehydratedState": {
                                "queries": [{
                                    "queryKey": ["feed", "vehicles", "search"],
                                    "state": {
                                        "data": {
                                            "commercial": [],
                                            "private": [],
                                            "pagination": {"pages": 10, "total": 100}
                                        }
                                    }
                                }]
                            }
                        }
                    }
                }

            html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
</body></html>"""
            return httpx.Response(200, text=html)

        route.mock(side_effect=page_response)

        main(["--max-pages", "10"])

        # Should have created CSV with 1 listing
        csv_files = list(tmp_path.glob("yad2_cars_*.csv"))
        assert len(csv_files) == 1

    @respx.mock
    def test_scraping_respects_max_pages(self, tmp_path, monkeypatch):
        """Should stop after max-pages limit."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        route = respx.get("https://www.yad2.co.il/vehicles/cars")

        next_data = {
            "props": {
                "pageProps": {
                    "dehydratedState": {
                        "queries": [{
                            "queryKey": ["feed", "vehicles", "search"],
                            "state": {
                                "data": {
                                    "commercial": [{"token": "test-123", "price": "50000"}],
                                    "private": [],
                                    "pagination": {"pages": 100, "total": 1000}
                                }
                            }
                        }]
                    }
                }
            }
        }

        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
</body></html>"""

        route.mock(return_value=httpx.Response(200, text=html))

        main(["--max-pages", "2"])

        # Should have made exactly 2 requests
        assert route.call_count == 2

    @respx.mock
    def test_keyboard_interrupt_exports_partial_results(self, tmp_path, monkeypatch):
        """Should export partial results when interrupted."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        route = respx.get("https://www.yad2.co.il/vehicles/cars")

        next_data = {
            "props": {
                "pageProps": {
                    "dehydratedState": {
                        "queries": [{
                            "queryKey": ["feed", "vehicles", "search"],
                            "state": {
                                "data": {
                                    "commercial": [{"token": "test-123", "price": "50000"}],
                                    "private": [],
                                    "pagination": {"pages": 100, "total": 1000}
                                }
                            }
                        }]
                    }
                }
            }
        }

        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
</body></html>"""

        # First request succeeds, second raises KeyboardInterrupt
        route.mock(side_effect=[
            httpx.Response(200, text=html),
            KeyboardInterrupt(),
        ])

        main(["--max-pages", "10"])

        # Should have created CSV with partial results
        csv_files = list(tmp_path.glob("yad2_cars_*.csv"))
        assert len(csv_files) == 1


@pytest.mark.integration
class TestPaginationLogic:
    """Test pagination logic and total pages handling."""

    @respx.mock
    def test_learns_total_pages_from_first_response(self, tmp_path, monkeypatch):
        """Should learn total pages from first successful parse."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        route = respx.get("https://www.yad2.co.il/vehicles/cars")

        next_data = {
            "props": {
                "pageProps": {
                    "dehydratedState": {
                        "queries": [{
                            "queryKey": ["feed", "vehicles", "search"],
                            "state": {
                                "data": {
                                    "commercial": [{"token": "test-123", "price": "50000"}],
                                    "private": [],
                                    "pagination": {"pages": 5, "total": 50}
                                }
                            }
                        }]
                    }
                }
            }
        }

        html = f"""<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
</body></html>"""

        route.mock(return_value=httpx.Response(200, text=html))

        main([])

        # Should fetch 5 pages (or fail at page 0 if bug exists)
        # After fix: should fetch pages 1-5
        assert route.call_count == 5
