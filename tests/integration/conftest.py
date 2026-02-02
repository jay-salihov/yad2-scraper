"""Shared fixtures for integration tests."""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_fetcher_sleep():
    """Mock time.sleep in fetcher to eliminate real delays in integration tests."""
    with patch("yad2_scraper.fetcher.time.sleep") as mock_sleep:
        yield mock_sleep
