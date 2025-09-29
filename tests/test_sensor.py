"""Test the Flavor of the Day sensor."""

from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.components.sensor import SensorEntityDescription

from custom_components.flavor_of_the_day.const import ATTRIBUTION
from custom_components.flavor_of_the_day.models import FlavorInfo
from custom_components.flavor_of_the_day.sensor import (
    FlavorOfTheDaySensor,
)


@pytest.mark.asyncio
async def test_sensor_attributes() -> None:
    """Test sensor attributes."""
    mock_coordinator = AsyncMock()
    mock_coordinator.data = FlavorInfo(
        name="Test Flavor",
        description="Test Description",
        ingredients=["Ingredient 1", "Ingredient 2"],
        allergens=["Allergen 1"],
        available_date=None,
        price="$4.99",
    )
    mock_coordinator.config_entry = Mock()
    mock_coordinator.config_entry.entry_id = "test_entry_id"
    mock_coordinator.config_entry.data = {"name": "Test Sensor"}
    mock_coordinator.provider = Mock()
    mock_coordinator.provider.provider_name = "Test Provider"
    mock_coordinator.location_id = "test_location_id"
    mock_coordinator.last_update_success_time = "2023-01-01T00:00:00"

    entity_description = SensorEntityDescription(
        key="flavor_of_the_day",
        name="Flavor of the Day",
        icon="mdi:ice-cream",
    )

    sensor = FlavorOfTheDaySensor(
        coordinator=mock_coordinator,
        entity_description=entity_description,
    )

    # Test native value
    assert sensor.native_value == "Test Flavor"

    # Test extra state attributes
    attrs = sensor.extra_state_attributes
    assert attrs["name"] == "Test Flavor"
    assert attrs["description"] == "Test Description"
    assert attrs["ingredients"] == ["Ingredient 1", "Ingredient 2"]
    assert attrs["allergens"] == ["Allergen 1"]
    assert attrs["provider"] == "Test Provider"
    assert attrs["location_id"] == "test_location_id"
    assert attrs["last_updated"] == "2023-01-01T00:00:00"

    # Test attribution
    assert sensor._attr_attribution == ATTRIBUTION

    # Test unique ID
    assert sensor.unique_id == "test_entry_id_flavor_of_the_day"

    # Test name
    assert sensor.name == "Test Sensor"


@pytest.mark.asyncio
async def test_sensor_with_none_data() -> None:
    """Test sensor when coordinator data is None."""
    mock_coordinator = AsyncMock()
    mock_coordinator.data = None

    entity_description = SensorEntityDescription(
        key="flavor_of_the_day",
        name="Flavor of the Day",
        icon="mdi:ice-cream",
    )

    sensor = FlavorOfTheDaySensor(
        coordinator=mock_coordinator,
        entity_description=entity_description,
    )

    # Test native value when data is None
    assert sensor.native_value == "Unknown"

    # Test extra state attributes when data is None
    attrs = sensor.extra_state_attributes
    assert attrs == {}
