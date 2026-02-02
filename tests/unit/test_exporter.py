"""Unit tests for CSV export and deduplication."""

import csv
import pytest
from pathlib import Path
from yad2_scraper.exporter import export_csv
from yad2_scraper.models import CarListing


@pytest.mark.unit
class TestCSVExport:
    """Test CSV file export functionality."""

    def test_export_csv_creates_file(self, tmp_path, sample_listing_complete, monkeypatch):
        """Should create a CSV file in the output directory."""
        # Use temp directory for output
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        filepath = export_csv([listing])

        assert filepath.exists()
        assert filepath.suffix == ".csv"
        assert filepath.parent == tmp_path

    def test_export_csv_includes_header(self, tmp_path, sample_listing_complete, monkeypatch):
        """Should include header row with all field names."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        filepath = export_csv([listing])

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)

        assert "token" in header
        assert "manufacturer" in header
        assert "model" in header
        assert "price" in header

    def test_export_csv_writes_data_rows(self, tmp_path, sample_listing_complete, monkeypatch):
        """Should write data rows for all listings."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        filepath = export_csv([listing])

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0][0] == "test-12345"  # token


@pytest.mark.unit
class TestDeduplication:
    """Test deduplication by token."""

    def test_export_csv_deduplicates_by_token(self, tmp_path, sample_listing_complete, monkeypatch):
        """Should remove duplicate listings with same token."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        listing1 = CarListing.from_raw(sample_listing_complete, "commercial")
        listing2 = CarListing.from_raw(sample_listing_complete, "commercial")
        listing3 = CarListing.from_raw(sample_listing_complete, "commercial")

        filepath = export_csv([listing1, listing2, listing3])

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            rows = list(reader)

        # Should only have 1 row despite 3 identical listings
        assert len(rows) == 1

    def test_export_csv_preserves_order(self, tmp_path, sample_listing_complete,
                                        sample_listing_minimal, monkeypatch):
        """Should preserve order of first occurrence."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        listing1 = CarListing.from_raw(sample_listing_complete, "commercial")
        listing2 = CarListing.from_raw(sample_listing_minimal, "private")
        listing3 = CarListing.from_raw(sample_listing_complete, "commercial")  # Duplicate

        filepath = export_csv([listing1, listing2, listing3])

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            rows = list(reader)

        # Should have 2 rows in order: listing1, listing2
        assert len(rows) == 2
        assert rows[0][0] == "test-12345"  # listing1 token
        assert rows[1][0] == "test-minimal-001"  # listing2 token

    def test_export_csv_handles_empty_token(self, tmp_path, monkeypatch):
        """Should skip listings with empty token."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        # Create listing with empty token
        listing_no_token = CarListing(token="", price="10000")
        listing_with_token = CarListing(token="valid-123", price="20000")

        filepath = export_csv([listing_no_token, listing_with_token])

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            rows = list(reader)

        # Should only include the listing with a token
        assert len(rows) == 1
        assert rows[0][0] == "valid-123"


@pytest.mark.unit
class TestEncoding:
    """Test UTF-8 BOM encoding."""

    def test_export_csv_uses_utf8_bom(self, tmp_path, sample_listing_complete, monkeypatch):
        """Should use UTF-8 with BOM encoding for Hebrew compatibility."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        filepath = export_csv([listing])

        # Read as binary to check BOM
        with open(filepath, "rb") as f:
            first_bytes = f.read(3)

        # UTF-8 BOM is 0xEF 0xBB 0xBF
        assert first_bytes == b'\xef\xbb\xbf'

    def test_export_csv_handles_hebrew_text(self, tmp_path, sample_listing_complete, monkeypatch):
        """Should correctly write Hebrew characters."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        filepath = export_csv([listing])

        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()

        # Hebrew text should be present
        assert "סיטרואן" in content
        assert "בנזין" in content


@pytest.mark.unit
class TestFileNaming:
    """Test output file naming and directory creation."""

    def test_export_csv_creates_output_dir(self, tmp_path, sample_listing_complete, monkeypatch):
        """Should create output directory if it doesn't exist."""
        output_dir = tmp_path / "nonexistent" / "output"
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(output_dir))

        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        filepath = export_csv([listing])

        assert output_dir.exists()
        assert filepath.parent == output_dir

    def test_export_csv_timestamp_format(self, tmp_path, sample_listing_complete, monkeypatch):
        """Should include timestamp in filename."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        filepath = export_csv([listing])

        # Filename should match pattern: yad2_cars_YYYYMMDD_HHMMSS.csv
        assert filepath.name.startswith("yad2_cars_")
        assert filepath.name.endswith(".csv")
        assert len(filepath.name) == len("yad2_cars_20240101_123456.csv")


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases in export."""

    def test_export_csv_handles_empty_list(self, tmp_path, monkeypatch):
        """Should handle empty listing list."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        filepath = export_csv([])

        assert filepath.exists()

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)

        # Should have header but no data rows
        assert len(header) > 0
        assert len(rows) == 0

    def test_export_csv_returns_path_object(self, tmp_path, sample_listing_complete, monkeypatch):
        """Should return a Path object."""
        monkeypatch.setattr("yad2_scraper.exporter.OUTPUT_DIR", str(tmp_path))

        listing = CarListing.from_raw(sample_listing_complete, "commercial")
        filepath = export_csv([listing])

        assert isinstance(filepath, Path)
