"""Test the Flavor of the Day coordinator."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed

from custom_components.flavor_of_the_day.coordinator import FlavorUpdateCoordinator
from custom_components.flavor_of_the_day.exceptions import (
    FlavorProviderAuthenticationError,
    FlavorProviderError,
)
from custom_components.flavor_of_the_day.models import FlavorInfo


@pytest.mark.asyncio
async def test_coordinator_update_data(hass) -> None:
    """Test coordinator successfully updates data."""
    mock_provider = AsyncMock()
    mock_provider.get_current_flavor.return_value = FlavorInfo(
        name="Test Flavor", description="Test Description"
    )

    coordinator = FlavorUpdateCoordinator(
        hass=hass,
        provider=mock_provider,
        location_id="test123",
        update_interval=30,
        config_entry=AsyncMock(),
    )

    result = await coordinator._async_update_data()

    assert result.name == "Test Flavor"
    assert result.description == "Test Description"
    mock_provider.get_current_flavor.assert_called_once_with("test123")


@pytest.mark.asyncio
async def test_coordinator_authentication_error(hass) -> None:
    """Test coordinator handles authentication errors."""
    mock_provider = AsyncMock()
    mock_provider.get_current_flavor.side_effect = FlavorProviderAuthenticationError(
        "Auth failed"
    )

    coordinator = FlavorUpdateCoordinator(
        hass=hass,
        provider=mock_provider,
        location_id="test123",
        update_interval=30,
        config_entry=AsyncMock(),
    )

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_provider_error(hass) -> None:
    """Test coordinator handles provider errors."""
    mock_provider = AsyncMock()
    mock_provider.get_current_flavor.side_effect = FlavorProviderError("Provider error")

    coordinator = FlavorUpdateCoordinator(
        hass=hass,
        provider=mock_provider,
        location_id="test123",
        update_interval=30,
        config_entry=AsyncMock(),
    )

    from homeassistant.helpers.update_coordinator import UpdateFailed

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_unexpected_error(hass) -> None:
    """Test coordinator handles unexpected errors."""
    mock_provider = AsyncMock()
    mock_provider.get_current_flavor.side_effect = Exception("Unexpected error")

    coordinator = FlavorUpdateCoordinator(
        hass=hass,
        provider=mock_provider,
        location_id="test123",
        update_interval=30,
        config_entry=AsyncMock(),
    )

    from homeassistant.helpers.update_coordinator import UpdateFailed

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
