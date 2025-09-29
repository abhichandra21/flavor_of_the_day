import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class FlavorOfTheDayServices:
    """Class that holds our services."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize with hass object."""
        self.hass = hass

    def async_register(self) -> None:
        """Register all our services."""
        self.hass.services.async_register(
            DOMAIN,
            "force_refresh",
            self.force_refresh,
        )

    async def force_refresh(self, call: ServiceCall) -> None:
        """Force a refresh of the flavor of the day."""
        entity_ids = call.data.get("entity_id")
        if not entity_ids:
            return

        ent_reg = er.async_get(self.hass)
        for entity_id in entity_ids:
            entry = ent_reg.async_get(entity_id)
            if entry:
                config_entry = self.hass.config_entries.async_get_entry(entry.config_entry_id)
                if config_entry and hasattr(config_entry, "runtime_data"):
                    await config_entry.runtime_data.coordinator.async_request_refresh()