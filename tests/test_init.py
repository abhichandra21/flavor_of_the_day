"""Tests for the Flavor of the Day integration setup."""

from unittest.mock import Mock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.flavor_of_the_day.const import DOMAIN


@pytest.mark.asyncio
async def test_setup_entry(hass: HomeAssistant, mock_config_entry_data) -> None:
    """Test setting up the integration entry."""
    config_entry = Mock()
    config_entry.entry_id = "test_entry"
    config_entry.data = mock_config_entry_data
    config_entry.runtime_data = None

    with (
        patch(
            "custom_components.flavor_of_the_day.providers.culvers.CulversProvider"
        ) as mock_provider_class,
        patch("custom_components.flavor_of_the_day.async_get_clientsession"),
    ):
        # Mock the provider
        mock_provider = mock_provider_class.return_value
        from custom_components.flavor_of_the_day.models import FlavorInfo

        mock_provider.get_current_flavor.return_value = FlavorInfo(
            name="Test Flavor", description="Test Description"
        )

        # Import and call async_setup_entry
        from custom_components.flavor_of_the_day import async_setup_entry

        # Call the setup function
        result = await async_setup_entry(hass, config_entry)
        assert result is True

        # Check that the config entry was added to hass.data
        assert DOMAIN in hass.data
        assert config_entry.entry_id in hass.data[DOMAIN]

        # Check that platforms were forwarded
        # Note: We can't test this directly without more complex mocking


@pytest.mark.asyncio
async def test_unload_entry(hass: HomeAssistant, setup_integration) -> None:
    """Test unloading the integration entry."""
    config_entry = setup_integration

    # Setup the integration first
    with patch(
        "custom_components.flavor_of_the_day.async_unload_platforms", return_value=True
    ) as mock_unload:
        from custom_components.flavor_of_the_day import async_unload_entry

        result = await async_unload_entry(hass, config_entry)
        assert result is True
        mock_unload.assert_called_once_with(config_entry, ["sensor"])
