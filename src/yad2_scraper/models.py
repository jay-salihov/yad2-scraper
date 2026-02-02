"""CarListing dataclass with CSV serialization."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


@dataclass
class CarListing:
    token: str = ""
    order_id: str = ""
    ad_type: str = ""  # "commercial" or "private"
    listing_source: str = ""
    manufacturer: str = ""
    manufacturer_id: str = ""
    model: str = ""
    model_id: str = ""
    sub_model: str = ""
    sub_model_id: str = ""
    year: str = ""
    engine_type: str = ""
    engine_type_id: str = ""
    engine_volume_cc: str = ""
    hand: str = ""
    hand_number: str = ""
    price: str = ""
    advance_payment: str = ""
    monthly_payment: str = ""
    number_of_payments: str = ""
    balance: str = ""
    area: str = ""
    area_id: str = ""
    image_count: str = ""
    cover_image_url: str = ""
    tags: str = ""
    agency_name: str = ""
    agency_customer_id: str = ""
    commitments: str = ""
    has_trade_in: str = ""
    priority: str = ""

    @classmethod
    def csv_header(cls) -> list[str]:
        return [f.name for f in fields(cls)]

    def csv_row(self) -> list[str]:
        return [str(getattr(self, f.name)) for f in fields(self)]

    @classmethod
    def from_raw(cls, raw: dict[str, Any], ad_type: str) -> CarListing:
        """Build a CarListing from a raw Yad2 feed item."""

        def g(*keys: str) -> str:
            """Walk nested keys, return stringified value or empty string."""
            obj: Any = raw
            for k in keys:
                if isinstance(obj, dict):
                    obj = obj.get(k)
                else:
                    return ""
            return str(obj) if obj is not None else ""

        def nested_text(key: str) -> str:
            """Extract 'text' from a nested dict field, or stringify scalars."""
            val = raw.get(key)
            if isinstance(val, dict):
                return str(val.get("text", "")) if val.get("text") is not None else ""
            return str(val) if val is not None else ""

        def nested_id(key: str) -> str:
            """Extract 'id' from a nested dict field."""
            val = raw.get(key)
            if isinstance(val, dict):
                return str(val.get("id", "")) if val.get("id") is not None else ""
            return ""

        # Payment info lives under metaData.financingInfo
        fin = raw.get("metaData", {}).get("financingInfo") or {}

        # Tags list -> comma-separated string (use 'name' field, fall back to 'text')
        tags_list = raw.get("tags") or []
        tags_str = ", ".join(
            str(t.get("name", t.get("text", t))) if isinstance(t, dict) else str(t)
            for t in tags_list
        )

        # Images from metaData
        metadata = raw.get("metaData") or {}
        images = metadata.get("images") or []
        cover_url = str(metadata.get("coverImage", "")) if metadata.get("coverImage") else ""

        # Commitments
        commitments_list = metadata.get("commitments") or []
        commitments_str = ", ".join(
            str(c.get("text", c)) if isinstance(c, dict) else str(c) for c in commitments_list
        )

        return cls(
            token=g("token"),
            order_id=g("orderId"),
            ad_type=ad_type,
            listing_source=g("listingSource"),
            manufacturer=nested_text("manufacturer"),
            manufacturer_id=nested_id("manufacturer"),
            model=nested_text("model"),
            model_id=nested_id("model"),
            sub_model=nested_text("subModel"),
            sub_model_id=nested_id("subModel"),
            year=g("vehicleDates", "yearOfProduction"),
            engine_type=nested_text("engineType"),
            engine_type_id=nested_id("engineType"),
            engine_volume_cc=g("engineVolume"),
            hand=nested_text("hand"),
            hand_number=g("handNumber"),
            price=g("price"),
            advance_payment=str(fin.get("advancePayment", "")) if fin else "",
            monthly_payment=str(fin.get("monthlyPayment", "")) if fin else "",
            number_of_payments=str(fin.get("numberOfPayments", "")) if fin else "",
            balance=str(fin.get("balance", "")) if fin else "",
            area=g("address", "area", "text"),
            area_id=g("address", "area", "id"),
            image_count=str(len(images)),
            cover_image_url=cover_url,
            tags=tags_str,
            agency_name=g("customer", "agencyName"),
            agency_customer_id=g("customer", "id"),
            commitments=commitments_str,
            has_trade_in=g("packages", "isTradeInButton"),
            priority=g("priority"),
        )
