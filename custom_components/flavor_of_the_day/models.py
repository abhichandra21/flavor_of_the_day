"""Data models for the Flavor of the Day integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class FlavorInfo:
    """Information about a flavor of the day."""

    name: str
    description: str | None = None
    ingredients: list[str] | None = None
    allergens: list[str] | None = None
    image_url: str | None = None
    available_date: datetime | None = None
    price: str | None = None
    nutrition_info: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for HA attributes."""
        return {
            "name": self.name,
            "description": self.description,
            "ingredients": self.ingredients,
            "allergens": self.allergens,
            "image_url": self.image_url,
            "available_date": self.available_date.isoformat()
            if self.available_date
            else None,
            "price": self.price,
            "nutrition_info": self.nutrition_info,
        }


@dataclass
class LocationInfo:
    """Information about a store location."""

    store_id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str | None = None
    phone: str | None = None
    hours: dict[str, str] | None = None
    website_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    def display_name(self) -> str:
        """Human readable name for UI."""
        return f"{self.name} - {self.city}, {self.state}"
