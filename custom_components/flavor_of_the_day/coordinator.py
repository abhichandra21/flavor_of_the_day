"""Flavor update coordinator for the Flavor of the Day integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .exceptions import FlavorProviderAuthenticationError, FlavorProviderError
from .models import FlavorInfo

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .providers.base import BaseFlavorProvider

_LOGGER = logging.getLogger(__name__)


class FlavorUpdateCoordinator(DataUpdateCoordinator[FlavorInfo]):
    """Class to manage fetching flavor data."""

    def __init__(
        self,
        hass: HomeAssistant,
        provider: BaseFlavorProvider,
        location_id: str,
        update_interval: int,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"flavor_coordinator_{provider.provider_id}_{location_id}",
            update_interval=timedelta(minutes=update_interval),
        )
        self.provider = provider
        self.location_id = location_id
        self.config_entry = config_entry

    async def _async_update_data(self) -> FlavorInfo:
        """Fetch data from API endpoint."""
        try:
            # Use the provider to get current flavor
            return await self.provider.get_current_flavor(self.location_id)
        except FlavorProviderAuthenticationError as err:
            msg = f"Authentication failed for {self.provider.provider_name}: {err}"
            raise ConfigEntryAuthFailed(msg) from err
        except FlavorProviderError as err:
            msg = f"Error communicating with {self.provider.provider_name}: {err}"
            raise UpdateFailed(msg) from err
        except Exception as err:
            _LOGGER.exception(
                "Unexpected error communicating with %s",
                self.provider.provider_name,
            )
            provider_name = self.provider.provider_name
            msg = f"Unexpected error communicating with {provider_name}: {err}"
            raise UpdateFailed(msg) from err
