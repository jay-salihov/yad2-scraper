"""Shared pytest fixtures for all test files."""

import pytest

from tests.fixtures import sample_data


@pytest.fixture
def sample_listing_complete():
    """Return a complete listing dict with all nested fields."""
    return sample_data.LISTING_COMPLETE.copy()


@pytest.fixture
def sample_listing_minimal():
    """Return a minimal listing dict with missing optional fields."""
    return sample_data.LISTING_MINIMAL.copy()


@pytest.fixture
def sample_listing_no_sub_model():
    """Return a listing without sub_model field."""
    return sample_data.LISTING_NO_SUB_MODEL.copy()


@pytest.fixture
def sample_listing_agency():
    """Return a listing from an agency."""
    return sample_data.LISTING_AGENCY.copy()


@pytest.fixture
def sample_listing_private():
    """Return a listing from a private seller."""
    return sample_data.LISTING_PRIVATE.copy()


@pytest.fixture
def sample_listing_with_tags():
    """Return a listing with multiple tags."""
    return sample_data.LISTING_WITH_TAGS.copy()


@pytest.fixture
def sample_listing_no_tags():
    """Return a listing without tags."""
    return sample_data.LISTING_NO_TAGS.copy()


@pytest.fixture
def sample_next_data():
    """Return __NEXT_DATA__ JSON with all 5 feed arrays."""
    return sample_data.NEXT_DATA_WITH_ALL_ARRAYS.copy()


@pytest.fixture
def sample_next_data_missing_arrays():
    """Return __NEXT_DATA__ JSON with only commercial and private arrays."""
    return sample_data.NEXT_DATA_MISSING_ARRAYS.copy()


@pytest.fixture
def sample_next_data_empty():
    """Return __NEXT_DATA__ JSON with empty feed arrays."""
    return sample_data.NEXT_DATA_EMPTY_ARRAYS.copy()


@pytest.fixture
def sample_html_valid():
    """Return valid HTML with embedded __NEXT_DATA__ JSON."""
    return sample_data.SAMPLE_HTML_VALID


@pytest.fixture
def sample_html_malformed():
    """Return HTML with malformed JSON."""
    return sample_data.SAMPLE_HTML_MALFORMED_JSON


@pytest.fixture
def sample_html_no_next_data():
    """Return HTML without __NEXT_DATA__ script tag."""
    return sample_data.SAMPLE_HTML_NO_NEXT_DATA


@pytest.fixture
def temp_output_dir(tmp_path):
    """Return a temporary directory for CSV exports."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
