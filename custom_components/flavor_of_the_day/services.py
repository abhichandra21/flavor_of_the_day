"""Services for the Flavor of the Day integration."""

import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_REFRESH = "refresh"


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Flavor of the Day integration."""

    async def handle_refresh(call: ServiceCall) -> None:
        """Handle refresh service call."""
        entity_id = call.data.get("entity_id")

        if not entity_id:
            _LOGGER.error("No entity_id provided for refresh service")
            return

        registry = er.async_get(hass)
        entity_entry = registry.async_get(entity_id)

        if not entity_entry:
            _LOGGER.error("Entity %s not found", entity_id)
            return

        if entity_entry.platform != DOMAIN:
            _LOGGER.error("Entity %s is not a Flavor of the Day entity", entity_id)
            return

        # Get the coordinator from runtime data
        config_entry_id = entity_entry.config_entry_id
        if not config_entry_id:
            _LOGGER.error("No config entry found for entity %s", entity_id)
            return

        entry = hass.config_entries.async_get_entry(config_entry_id)
        if not entry:
            _LOGGER.error("Config entry %s not found", config_entry_id)
            return

        coordinator = entry.runtime_data.coordinator
        await coordinator.async_request_refresh()
        _LOGGER.info("Refreshed flavor data for %s", entity_id)

    hass.services.async_register(DOMAIN, SERVICE_REFRESH, handle_refresh)
