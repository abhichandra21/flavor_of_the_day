"""Constants for tests."""

from datetime import UTC, datetime

from custom_components.flavor_of_the_day.const import (
    CONF_LOCATION_ID,
    CONF_NAME,
    CONF_PROVIDER,
    CONF_UPDATE_INTERVAL,
)
from custom_components.flavor_of_the_day.models import FlavorInfo

CONFIG_DATA = {
    CONF_NAME: "Test Location",
    CONF_PROVIDER: "culvers",
    CONF_LOCATION_ID: "12345",
    CONF_UPDATE_INTERVAL: 3600,
}

CONFIG_DATA_KOPPS = {
    CONF_NAME: "Kopp's Location",
    CONF_PROVIDER: "kopps",
    CONF_LOCATION_ID: "brookfield",
    CONF_UPDATE_INTERVAL: 3600,
}

CULVERS_LOCATION_SEARCH = {
    "12345": "Culver's of Test City @ 123 Main St",
    "67890": "Culver's of Other City @ 456 Oak Ave",
}

COORDINATOR_DATA = FlavorInfo(
    name="Chocolate Peanut Butter",
    description="Rich chocolate custard with swirls of peanut butter",
    ingredients=None,
    allergens=["milk", "peanuts", "soy"],
    price=None,
    available_date=datetime(2025, 1, 9, 16, 12, 51, tzinfo=UTC),
    image_url=None,
)

COORDINATOR_DATA_KOPPS = FlavorInfo(
    name="Turtle Sundae",
    description="Vanilla custard with caramel, pecans, and hot fudge",
    ingredients=None,
    allergens=["milk", "tree nuts"],
    price=None,
    available_date=datetime(2025, 1, 9, 18, 30, 15, tzinfo=UTC),
    image_url=None,
)
