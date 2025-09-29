"""Test flavor_of_the_day sensors."""

from typing import Any
from unittest.mock import patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.flavor_of_the_day.const import DOMAIN

from .const import CONFIG_DATA


async def test_sensors(
    hass: HomeAssistant,
    mock_flavor_coordinator: Any,  # noqa: ARG001
) -> None:
    """Test sensor setup."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Location",
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 1
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    state = hass.states.get("sensor.test_location_test_location")
    assert state
    assert state.state == "Chocolate Peanut Butter"
    assert (
        state.attributes["description"]
        == "Rich chocolate custard with swirls of peanut butter"
    )
    assert state.attributes["allergens"] == ["milk", "peanuts", "soy"]
    assert state.attributes["name"] == "Chocolate Peanut Butter"
    assert state.attributes["provider"] == "Culver's"
    assert state.attributes["location_id"] == "12345"


async def test_sensor_unavailable(hass: HomeAssistant) -> None:
    """Test sensor when flavor is unavailable."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Location",
        data=CONFIG_DATA,
    )

    with patch(
        "custom_components.flavor_of_the_day.FlavorUpdateCoordinator._async_update_data"
    ) as mock_value:
        mock_value.return_value = None

        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        state = hass.states.get("sensor.test_location_test_location")
        assert state
        assert state.state == "Unknown"
