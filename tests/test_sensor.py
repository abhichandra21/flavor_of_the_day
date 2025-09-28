"""Test the Flavor of the Day sensor."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.flavor_of_the_day.const import DOMAIN


async def test_sensor_setup(hass: HomeAssistant, bypass_get_data, mock_provider):
    """Test sensor setup."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "provider": "culvers",
            "location_id": "123",
            "name": "Test Location",
        },
        unique_id="culvers_123",
    )

    entry.add_to_hass(hass)

    with patch("custom_components.flavor_of_the_day.PROVIDER_CLASSES", {"culvers": mock_provider.__class__}):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Check that sensor entity was created
    entity_registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)

    assert len(entities) == 1
    entity = entities[0]
    assert entity.domain == SENSOR_DOMAIN
    assert entity.unique_id == "culvers_123_flavor"


async def test_sensor_state(hass: HomeAssistant, bypass_get_data, mock_provider):
    """Test sensor state."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "provider": "culvers",
            "location_id": "123",
            "name": "Test Location",
        },
        unique_id="culvers_123",
    )

    entry.add_to_hass(hass)

    with patch("custom_components.flavor_of_the_day.PROVIDER_CLASSES", {"culvers": mock_provider.__class__}):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("sensor.test_location_flavor_of_the_day")
    assert state
    assert state.state != STATE_UNAVAILABLE


class MockConfigEntry:
    """Mock config entry."""

    def __init__(self, *, domain=None, data=None, unique_id=None):
        """Initialize mock config entry."""
        self.domain = domain
        self.data = data or {}
        self.unique_id = unique_id
        self.entry_id = "test_entry_id"
        self.runtime_data = None

    def add_to_hass(self, hass):
        """Add to hass."""
        hass.config_entries._entries[self.entry_id] = self