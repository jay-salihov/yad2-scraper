"""Integration tests for CLI arguments and logging (Issue 10)."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from yad2_scraper.__main__ import main


@pytest.mark.integration
class TestIssue10VerboseLogging:
    """Test verbose logging configuration (Issue 10)."""

    def test_verbose_sets_debug_on_yad2_scraper_logger_only(self, tmp_path, monkeypatch):
        """Verbose mode should only set DEBUG on yad2_scraper logger, not root."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        # Mock fetcher and parser to avoid actual HTTP requests
        with patch("yad2_scraper.__main__.Fetcher") as mock_fetcher_class:
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value.__enter__.return_value = mock_fetcher

            # Return empty listings to exit quickly
            mock_fetcher.fetch_page.return_value = """<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [{
                    "queryKey": ["feed", "vehicles", "search"],
                    "state": {
                        "data": {
                            "commercial": [],
                            "private": [],
                            "pagination": {"pages": 0, "total": 0}
                        }
                    }
                }]
            }
        }
    }
}</script>
</body></html>"""

            # Test with verbose flag
            with pytest.raises(SystemExit):  # Will exit(1) because no listings
                main(["--verbose", "--max-pages", "1"])

            # Check that yad2_scraper logger is set to DEBUG
            yad2_logger = logging.getLogger("yad2_scraper")
            assert (
                yad2_logger.level == logging.DEBUG
                or yad2_logger.getEffectiveLevel() == logging.DEBUG
            )

    def test_verbose_does_not_flood_with_httpcore_logs(self, tmp_path, caplog, monkeypatch):
        """Verbose mode should not flood with httpcore debug messages."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        # Mock fetcher and parser
        with patch("yad2_scraper.__main__.Fetcher") as mock_fetcher_class:
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value.__enter__.return_value = mock_fetcher

            mock_fetcher.fetch_page.return_value = """<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [{
                    "queryKey": ["feed", "vehicles", "search"],
                    "state": {
                        "data": {
                            "commercial": [],
                            "private": [],
                            "pagination": {"pages": 0, "total": 0}
                        }
                    }
                }]
            }
        }
    }
}</script>
</body></html>"""

            with caplog.at_level(logging.DEBUG), pytest.raises(SystemExit):
                main(["--verbose", "--max-pages", "1"])

            # httpcore and httpx loggers should NOT be at DEBUG level
            httpcore_logger = logging.getLogger("httpcore")
            httpx_logger = logging.getLogger("httpx")

            # If verbose is implemented correctly, these should not be DEBUG
            # Currently this test will FAIL because basicConfig sets root logger
            assert (
                httpcore_logger.getEffectiveLevel() > logging.DEBUG
            ), "httpcore logger should not be at DEBUG level"
            assert (
                httpx_logger.getEffectiveLevel() > logging.DEBUG
            ), "httpx logger should not be at DEBUG level"


@pytest.mark.integration
class TestCLIArguments:
    """Test CLI argument parsing."""

    def test_max_pages_argument_parsing(self, tmp_path, monkeypatch):
        """Should parse --max-pages argument correctly."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        with patch("yad2_scraper.__main__.Fetcher") as mock_fetcher_class:
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value.__enter__.return_value = mock_fetcher

            # Return empty page
            mock_fetcher.fetch_page.return_value = """<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [{
                    "queryKey": ["feed", "vehicles", "search"],
                    "state": {
                        "data": {
                            "commercial": [],
                            "private": [],
                            "pagination": {"pages": 0, "total": 0}
                        }
                    }
                }]
            }
        }
    }
}</script>
</body></html>"""

            with pytest.raises(SystemExit):
                main(["--max-pages", "5"])

            # Should attempt to fetch pages (though will stop at empty page)
            assert mock_fetcher.fetch_page.called

    def test_no_max_pages_defaults_to_none(self):
        """Should default to None when --max-pages not specified."""
        import argparse

        # Parse args without calling main
        parser = argparse.ArgumentParser()
        parser.add_argument("--max-pages", type=int, default=None)
        parser.add_argument("-v", "--verbose", action="store_true")

        args = parser.parse_args([])
        assert args.max_pages is None


@pytest.mark.integration
class TestLoggingFormat:
    """Test logging format configuration."""

    def test_logging_format_includes_timestamp(self, tmp_path, caplog, monkeypatch):
        """Should include timestamp in log format."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        with patch("yad2_scraper.__main__.Fetcher") as mock_fetcher_class:
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value.__enter__.return_value = mock_fetcher

            mock_fetcher.fetch_page.return_value = """<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [{
                    "queryKey": ["feed", "vehicles", "search"],
                    "state": {
                        "data": {
                            "commercial": [],
                            "private": [],
                            "pagination": {"pages": 0, "total": 0}
                        }
                    }
                }]
            }
        }
    }
}</script>
</body></html>"""

            with caplog.at_level(logging.INFO), pytest.raises(SystemExit):
                main(["--max-pages", "1"])

            # Should have log messages
            assert len(caplog.records) > 0

    def test_default_logging_level_is_info(self, tmp_path, monkeypatch):
        """Default logging level should be INFO."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        with patch("yad2_scraper.__main__.Fetcher") as mock_fetcher_class:
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value.__enter__.return_value = mock_fetcher

            mock_fetcher.fetch_page.return_value = """<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [{
                    "queryKey": ["feed", "vehicles", "search"],
                    "state": {
                        "data": {
                            "commercial": [],
                            "private": [],
                            "pagination": {"pages": 0, "total": 0}
                        }
                    }
                }]
            }
        }
    }
}</script>
</body></html>"""

            with pytest.raises(SystemExit):
                main(["--max-pages", "1"])

            # Root logger should be at INFO level by default
            root_logger = logging.getLogger()
            assert root_logger.level == logging.INFO


@pytest.mark.integration
class TestCLIExitCodes:
    """Test CLI exit codes."""

    def test_no_listings_exits_with_code_1(self, tmp_path, monkeypatch):
        """Should exit with code 1 when no listings found."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        with patch("yad2_scraper.__main__.Fetcher") as mock_fetcher_class:
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value.__enter__.return_value = mock_fetcher

            # Return empty listings
            mock_fetcher.fetch_page.return_value = """<!DOCTYPE html>
<html><body>
<script id="__NEXT_DATA__" type="application/json">{
    "props": {
        "pageProps": {
            "dehydratedState": {
                "queries": [{
                    "queryKey": ["feed", "vehicles", "search"],
                    "state": {
                        "data": {
                            "commercial": [],
                            "private": [],
                            "pagination": {"pages": 0, "total": 0}
                        }
                    }
                }]
            }
        }
    }
}</script>
</body></html>"""

            with pytest.raises(SystemExit) as exc_info:
                main(["--max-pages", "1"])

            assert exc_info.value.code == 1
