"""Unit tests for HTTP client and error handling (Issue 2)."""

import httpx
import pytest
import respx

from yad2_scraper.fetcher import BotDetectedError, Fetcher


@pytest.mark.unit
class TestIssue2HTTPErrors:
    """Test handling of HTTP error status codes (Issue 2)."""

    @respx.mock
    def test_fetch_page_404_raises_http_status_error(self):
        """Should raise HTTPStatusError for 404 responses."""
        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(404, text="Not Found")
        )

        fetcher = Fetcher()
        with pytest.raises(httpx.HTTPStatusError):
            fetcher.fetch_page(1)

    @respx.mock
    def test_fetch_page_500_raises_http_status_error(self):
        """Should raise HTTPStatusError for 500 responses."""
        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        fetcher = Fetcher()
        with pytest.raises(httpx.HTTPStatusError):
            fetcher.fetch_page(1)

    @respx.mock
    def test_fetch_page_403_raises_http_status_error(self):
        """Should raise HTTPStatusError for 403 responses."""
        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(403, text="Forbidden")
        )

        fetcher = Fetcher()
        with pytest.raises(httpx.HTTPStatusError):
            fetcher.fetch_page(1)


@pytest.mark.unit
class TestFetcherBasics:
    """Test basic HTTP fetching functionality."""

    @respx.mock
    def test_fetch_page_200_success(self):
        """Should return HTML text for successful 200 response."""
        expected_html = "<html><body>Test</body></html>"
        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(200, text=expected_html)
        )

        fetcher = Fetcher()
        html = fetcher.fetch_page(1)
        assert html == expected_html

    @respx.mock
    def test_fetch_page_includes_search_params(self):
        """Should include search parameters in request."""
        route = respx.get("https://www.yad2.co.il/vehicles/cars")
        route.mock(return_value=httpx.Response(200, text="<html></html>"))

        fetcher = Fetcher()
        fetcher.fetch_page(5)

        # Verify the request was made with correct page parameter
        assert route.called
        request = route.calls.last.request
        assert "page=5" in str(request.url)


@pytest.mark.unit
class TestBotDetection:
    """Test bot detection and retry logic."""

    @respx.mock
    def test_fetch_page_302_retries_with_backoff(self):
        """Should retry with backoff on 302 redirect."""
        # First two requests return 302, third returns 200
        route = respx.get("https://www.yad2.co.il/vehicles/cars")
        route.mock(
            side_effect=[
                httpx.Response(302, headers={"location": "/bot-check"}),
                httpx.Response(302, headers={"location": "/bot-check"}),
                httpx.Response(200, text="<html>Success</html>"),
            ]
        )

        fetcher = Fetcher()
        html = fetcher.fetch_page(1)

        assert html == "<html>Success</html>"
        assert route.call_count == 3

    @respx.mock
    def test_fetch_exhausts_retries_raises_bot_detected(self):
        """Should raise BotDetectedError after max retries."""
        # Always return 302
        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(302, headers={"location": "/bot-check"})
        )

        fetcher = Fetcher()
        with pytest.raises(BotDetectedError, match="Bot detection after"):
            fetcher.fetch_page(1)

    @respx.mock
    def test_fetch_handles_all_redirect_codes(self):
        """Should handle all redirect status codes (301, 302, 303, 307, 308)."""
        for redirect_code in [301, 302, 303, 307, 308]:
            route = respx.get("https://www.yad2.co.il/vehicles/cars")
            route.mock(
                side_effect=[
                    httpx.Response(redirect_code, headers={"location": "/bot-check"}),
                    httpx.Response(200, text="<html>Success</html>"),
                ]
            )

            fetcher = Fetcher()
            html = fetcher.fetch_page(1)
            assert html == "<html>Success</html>"
            route.calls.clear()


@pytest.mark.unit
class TestRateLimiting:
    """Test rate limiting and delays."""

    @respx.mock
    def test_no_delay_on_first_request(self):
        """Should not delay before first request."""
        import time

        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(200, text="<html></html>")
        )

        fetcher = Fetcher()
        start = time.time()
        fetcher.fetch_page(1)
        elapsed = time.time() - start

        # Should complete quickly (< 1 second for first request)
        assert elapsed < 1.0

    @respx.mock
    def test_rate_limiting_delays_requests(self):
        """Should delay between subsequent requests."""
        import time

        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(200, text="<html></html>")
        )

        fetcher = Fetcher()
        fetcher.fetch_page(1)  # First request - no delay

        start = time.time()
        fetcher.fetch_page(2)  # Second request - should have delay
        elapsed = time.time() - start

        # Should have at least DELAY_MIN (3 seconds) delay
        assert elapsed >= 3.0


@pytest.mark.unit
class TestContextManager:
    """Test Fetcher context manager usage."""

    @respx.mock
    def test_context_manager_closes_client(self):
        """Should properly close client when used as context manager."""
        respx.get("https://www.yad2.co.il/vehicles/cars").mock(
            return_value=httpx.Response(200, text="<html></html>")
        )

        with Fetcher() as fetcher:
            html = fetcher.fetch_page(1)
            assert html == "<html></html>"

        # Client should be closed
        assert fetcher._client.is_closed

    def test_manual_close(self):
        """Should close client when close() is called."""
        fetcher = Fetcher()
        fetcher.close()
        assert fetcher._client.is_closed


@pytest.mark.unit
class TestFetcherHeaders:
    """Test that Fetcher sends correct headers."""

    @respx.mock
    def test_fetcher_headers_correct(self):
        """Should send browser-like headers."""
        route = respx.get("https://www.yad2.co.il/vehicles/cars")
        route.mock(return_value=httpx.Response(200, text="<html></html>"))

        fetcher = Fetcher()
        fetcher.fetch_page(1)

        # Verify headers were sent
        assert route.called
        request = route.calls.last.request
        headers = request.headers

        # Check key headers exist
        assert "user-agent" in headers
        assert "accept-language" in headers
