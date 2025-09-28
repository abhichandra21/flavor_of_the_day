"""Test the Flavor of the Day init."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.flavor_of_the_day.const import DOMAIN


async def test_setup_unload_and_reload_entry(hass: HomeAssistant, bypass_get_data, mock_provider):
    """Test entry setup and unload."""
    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "provider": "culvers",
            "location_id": "123",
            "update_interval": 30,
            "name": "Test Location",
        },
        unique_id="culvers_123",
    )

    entry.add_to_hass(hass)

    # Test setup
    with patch("custom_components.flavor_of_the_day.PROVIDER_CLASSES", {"culvers": mock_provider.__class__}):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data is not None

    # Test unload
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_entry_exception(hass: HomeAssistant):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "provider": "invalid_provider",
            "location_id": "123",
        },
    )

    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_RETRY


class MockConfigEntry:
    """Mock config entry."""

    def __init__(self, *, domain=None, data=None, unique_id=None):
        """Initialize mock config entry."""
        self.domain = domain
        self.data = data or {}
        self.unique_id = unique_id
        self.entry_id = "test_entry_id"
        self.state = ConfigEntryState.NOT_LOADED
        self.runtime_data = None

    def add_to_hass(self, hass):
        """Add to hass."""
        hass.config_entries._entries[self.entry_id] = self