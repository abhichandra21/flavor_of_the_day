"""Flavor of the Day integration for Home Assistant."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client

from .const import (
    CONF_LOCATION_ID,
    CONF_PROVIDER,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
)
from .coordinator import FlavorUpdateCoordinator
from .data import FlavorOfTheDayData
from .providers.culvers import CulversProvider
from .providers.kopps import KoppsProvider
from .providers.leducs import LeducsProvider
from .providers.oscars import OscarsProvider

_LOGGER = logging.getLogger(__name__)

# Mapping of provider IDs to their classes
PROVIDER_CLASSES = {
    "culvers": CulversProvider,
    "kopps": KoppsProvider,
    "oscars": OscarsProvider,
    "leducs": LeducsProvider,
}

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flavor of the Day from a config entry."""
    # Create HTTP session
    session = aiohttp_client.async_get_clientsession(hass)

    # Get provider configuration
    provider_id = entry.data[CONF_PROVIDER]
    location_id = entry.data[CONF_LOCATION_ID]

    # Create provider instance
    if provider_id not in PROVIDER_CLASSES:
        _LOGGER.error("Unsupported provider: %s", provider_id)
        msg = f"Unsupported provider: {provider_id}"
        raise ConfigEntryNotReady(msg)

    provider_class = PROVIDER_CLASSES[provider_id]
    provider = provider_class(session, entry.data)

    # Get update interval from config (default to 30 minutes)
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

    # Create coordinator
    coordinator = FlavorUpdateCoordinator(
        hass,
        provider,
        location_id,
        update_interval,
        entry,
    )

    # Initialize the coordinator
    await coordinator.async_config_entry_first_refresh()

    # Store data in entry runtime_data
    entry.runtime_data = FlavorOfTheDayData(
        coordinator=coordinator,
        provider=provider,
    )

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:  # noqa: ARG001
    """Set up the Flavor of the Day integration."""
    return True
