"""Unit tests for CarListing model and field extraction (Issues 3-9, 12)."""

import pytest
from yad2_scraper.models import CarListing


@pytest.mark.unit
class TestIssue3NestedDictFields:
    """Test extraction of text values from nested dict fields (Issue 3)."""

    def test_manufacturer_extracts_text_not_dict(self, sample_listing_complete):
        """Manufacturer should extract 'text' field from nested dict."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.manufacturer == "סיטרואן"
        assert listing.manufacturer != "{'id': 38, 'text': 'סיטרואן'}"

    def test_manufacturer_id_extracts_id(self, sample_listing_complete):
        """Manufacturer ID should extract 'id' field from nested dict."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.manufacturer_id == "38"

    def test_model_extracts_text_not_dict(self, sample_listing_complete):
        """Model should extract 'text' field from nested dict."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.model == "C3"
        assert listing.model != "{'id': 451, 'text': 'C3'}"

    def test_model_id_extracts_id(self, sample_listing_complete):
        """Model ID should extract 'id' field from nested dict."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.model_id == "451"

    def test_sub_model_extracts_text_not_dict(self, sample_listing_complete):
        """Sub-model should extract 'text' field from nested dict."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.sub_model == "Shine"
        assert listing.sub_model != "{'id': 789, 'text': 'Shine'}"

    def test_sub_model_id_extracts_id(self, sample_listing_complete):
        """Sub-model ID should extract 'id' field from nested dict."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.sub_model_id == "789"

    def test_engine_type_extracts_text_not_dict(self, sample_listing_complete):
        """Engine type should extract 'text' field from nested dict."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.engine_type == "בנזין"
        assert listing.engine_type != "{'id': 1101, 'text': 'בנזין'}"

    def test_engine_type_id_extracts_id(self, sample_listing_complete):
        """Engine type ID should extract 'id' field from nested dict."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.engine_type_id == "1101"

    def test_hand_extracts_text_not_dict(self, sample_listing_complete):
        """Hand should extract 'text' field from nested dict."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.hand == "יד ראשונה"
        assert listing.hand != "{'id': 1, 'text': 'יד ראשונה'}"


@pytest.mark.unit
class TestIssue4YearField:
    """Test year extraction from vehicleDates.yearOfProduction (Issue 4)."""

    def test_year_from_vehicle_dates_year_of_production(self, sample_listing_complete):
        """Year should be extracted from vehicleDates.yearOfProduction."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.year == "2021"

    def test_year_missing_vehicle_dates(self, sample_listing_minimal):
        """Year should be empty string when vehicleDates missing."""
        listing = CarListing.from_raw(sample_listing_minimal, "private")
        assert listing.year == ""


@pytest.mark.unit
class TestIssue5AreaFields:
    """Test area extraction from address.area nested dict (Issue 5)."""

    def test_area_from_address_area_text(self, sample_listing_complete):
        """Area should be extracted from address.area.text."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.area == "תל אביב והמרכז"

    def test_area_id_from_address_area_id(self, sample_listing_complete):
        """Area ID should be extracted from address.area.id."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.area_id == "5"


@pytest.mark.unit
class TestIssue6Images:
    """Test image extraction from metaData.images (Issue 6)."""

    def test_image_count_from_metadata_images(self, sample_listing_complete):
        """Image count should be from metaData.images array length."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.image_count == "2"

    def test_cover_image_url_from_metadata_cover_image(self, sample_listing_complete):
        """Cover image URL should be from metaData.coverImage."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.cover_image_url == "https://example.com/cover.jpg"

    def test_image_count_zero_when_no_images(self, sample_listing_minimal):
        """Image count should be 0 when metaData.images missing."""
        listing = CarListing.from_raw(sample_listing_minimal, "private")
        assert listing.image_count == "0"


@pytest.mark.unit
class TestIssue7Tags:
    """Test tag extraction using 'name' field (Issue 7)."""

    def test_tags_extract_name_not_text(self, sample_listing_with_tags):
        """Tags should extract 'name' field, not 'text'."""
        listing = CarListing.from_raw(sample_listing_with_tags, "commercial")
        assert "חסכוני" in listing.tags
        assert "מטופל" in listing.tags
        assert "יד ראשונה" in listing.tags

    def test_tags_single_tag(self, sample_listing_complete):
        """Tags should work with single tag."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.tags == "חסכוני"

    def test_tags_empty_list(self, sample_listing_no_tags):
        """Tags should be empty string when tag list is empty."""
        listing = CarListing.from_raw(sample_listing_no_tags, "private")
        assert listing.tags == ""


@pytest.mark.unit
class TestIssue8Agency:
    """Test agency extraction from customer.agencyName (Issue 8)."""

    def test_agency_name_from_customer_agency_name(self, sample_listing_agency):
        """Agency name should be from customer.agencyName."""
        listing = CarListing.from_raw(sample_listing_agency, "commercial")
        assert listing.agency_name == "יוקרה מוטורס"

    def test_agency_customer_id_from_customer_id(self, sample_listing_agency):
        """Agency customer ID should be from customer.id."""
        listing = CarListing.from_raw(sample_listing_agency, "commercial")
        assert listing.agency_customer_id == "agency-456"

    def test_private_seller_no_agency_name(self, sample_listing_private):
        """Private seller should have empty agency name."""
        listing = CarListing.from_raw(sample_listing_private, "private")
        assert listing.agency_name == ""

    def test_agency_name_from_complete_listing(self, sample_listing_complete):
        """Complete listing should have agency name."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.agency_name == "מוסך דוד"


@pytest.mark.unit
class TestIssue9TradeIn:
    """Test trade-in extraction from packages.isTradeInButton (Issue 9)."""

    def test_has_trade_in_from_packages_is_trade_in_button(self, sample_listing_complete):
        """has_trade_in should be from packages.isTradeInButton."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.has_trade_in == "True"

    def test_has_trade_in_missing_packages(self, sample_listing_minimal):
        """has_trade_in should be empty when packages missing."""
        listing = CarListing.from_raw(sample_listing_minimal, "private")
        assert listing.has_trade_in == ""


@pytest.mark.unit
class TestIssue12MissingFields:
    """Test handling of missing optional fields (Issue 12)."""

    def test_optional_fields_missing_data_no_crash(self, sample_listing_minimal):
        """Should handle missing optional fields without crashing."""
        listing = CarListing.from_raw(sample_listing_minimal, "private")

        # Should not crash and should have some basic data
        assert listing.token == "test-minimal-001"
        assert listing.price == "25000"
        assert listing.manufacturer == "טויוטה"
        assert listing.model == "Corolla"

        # Missing fields should be empty strings
        assert listing.sub_model == ""
        assert listing.year == ""
        assert listing.engine_type == ""

    def test_none_sub_model_handled(self, sample_listing_no_sub_model):
        """Should handle explicitly None sub_model."""
        listing = CarListing.from_raw(sample_listing_no_sub_model, "private")
        assert listing.sub_model == ""


@pytest.mark.unit
class TestHelperFunction:
    """Test the g() helper function for nested field access."""

    def test_g_helper_handles_none(self, sample_listing_complete):
        """g() should return empty string for None values."""
        # Create a listing with None value
        raw = sample_listing_complete.copy()
        raw["subModel"] = None
        listing = CarListing.from_raw(raw, "commercial")
        assert listing.sub_model == ""

    def test_g_helper_handles_missing_keys(self, sample_listing_minimal):
        """g() should return empty string for missing keys."""
        listing = CarListing.from_raw(sample_listing_minimal, "private")
        assert listing.engine_type == ""

    def test_g_helper_nested_path(self, sample_listing_complete):
        """g() should handle nested paths correctly."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        # This tests the nested path for area
        assert listing.area != ""


@pytest.mark.unit
class TestCSVSerialization:
    """Test CSV header and row generation."""

    def test_csv_header_all_fields(self):
        """CSV header should include all field names."""
        header = CarListing.csv_header()
        assert "token" in header
        assert "manufacturer" in header
        assert "model" in header
        assert "year" in header
        assert "price" in header
        assert len(header) == 29  # Total number of fields

    def test_csv_row_all_strings(self, sample_listing_complete):
        """CSV row should convert all values to strings."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        row = listing.csv_row()
        assert all(isinstance(val, str) for val in row)
        assert len(row) == len(CarListing.csv_header())

    def test_csv_row_order_matches_header(self, sample_listing_complete):
        """CSV row values should match header order."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        header = CarListing.csv_header()
        row = listing.csv_row()

        # Token should be first
        assert header[0] == "token"
        assert row[0] == listing.token


@pytest.mark.unit
class TestAdType:
    """Test ad_type field assignment."""

    def test_ad_type_commercial(self, sample_listing_complete):
        """Ad type should be set to 'commercial'."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.ad_type == "commercial"

    def test_ad_type_private(self, sample_listing_minimal):
        """Ad type should be set to 'private'."""
        listing = CarListing.from_raw(sample_listing_minimal, "private")
        assert listing.ad_type == "private"


@pytest.mark.unit
class TestBasicFields:
    """Test basic field extraction."""

    def test_token_extraction(self, sample_listing_complete):
        """Token should be extracted correctly."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.token == "test-12345"

    def test_order_id_extraction(self, sample_listing_complete):
        """Order ID should be extracted correctly."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.order_id == "98765"

    def test_price_extraction(self, sample_listing_complete):
        """Price should be extracted correctly."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.price == "45000"

    def test_priority_extraction(self, sample_listing_complete):
        """Priority should be extracted correctly."""
        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        assert listing.priority == "5"
