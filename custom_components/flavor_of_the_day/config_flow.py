"""Config flow for the Flavor of the Day integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

if TYPE_CHECKING:
    from .models import LocationInfo
    from .providers.base import BaseFlavorProvider

from .const import (
    CONF_LOCATION_ID,
    CONF_NAME,
    CONF_PROVIDER,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .exceptions import FlavorProviderError
from .providers.culvers import CulversProvider
from .providers.kopps import KoppsProvider
from .providers.leducs import LeducsProvider
from .providers.oscars import OscarsProvider

_LOGGER = logging.getLogger(__name__)

# Provider selection schema with HA selector
USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PROVIDER): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(value="culvers", label="Culver's"),
                    selector.SelectOptionDict(
                        value="kopps", label="Kopp's Frozen Custard"
                    ),
                    selector.SelectOptionDict(
                        value="oscars", label="Oscar's Frozen Custard"
                    ),
                    selector.SelectOptionDict(
                        value="leducs", label="Leduc's Frozen Custard"
                    ),
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
    }
)

# Location search schema with HA selectors
LOCATION_SEARCH_SCHEMA = vol.Schema(
    {
        vol.Required("search_term"): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT,
            )
        ),
        vol.Optional("state"): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT,
                max_length=2,
            )
        ),
    }
)


# Base location selection schema (will be created dynamically)
def create_location_select_schema(locations: list[LocationInfo]) -> vol.Schema:
    """Create location selection schema with dynamic options."""
    location_options = [
        selector.SelectOptionDict(
            value=location.store_id, label=location.display_name()
        )
        for location in locations
    ]

    return vol.Schema(
        {
            vol.Required(CONF_LOCATION_ID): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=location_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONF_NAME): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                )
            ),
            vol.Optional(
                CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=1440,
                    step=1,
                    unit_of_measurement="minutes",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }
    )


PROVIDER_CLASSES = {
    "culvers": CulversProvider,
    "kopps": KoppsProvider,
    "oscars": OscarsProvider,
    "leducs": LeducsProvider,
}


class FlavorOfTheDayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Flavor of the Day."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.provider: BaseFlavorProvider | None = None
        self.provider_id: str | None = None
        self.locations: list[LocationInfo] = []
        self.location_details: LocationInfo | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self.provider_id = user_input[CONF_PROVIDER]

            # Set unique ID based on provider to prevent duplicates
            await self.async_set_unique_id(f"{DOMAIN}_{self.provider_id}")

            # Create the provider instance
            session = async_get_clientsession(self.hass)
            provider_class = PROVIDER_CLASSES[self.provider_id]
            self.provider = provider_class(session, {})

            return await self.async_step_location_search()

        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )

    async def async_step_location_search(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the location search step."""
        errors = {}

        if user_input is not None:
            search_term = user_input.get("search_term")
            state = user_input.get("state")

            if not search_term:
                errors["search_term"] = "Search term is required"
            else:
                try:
                    # Search for locations using the provider
                    self.locations = await self.provider.search_locations(
                        search_term, state
                    )

                    if not self.locations:
                        errors["search_term"] = "no_locations_found"
                    else:
                        # If we found exactly one location, skip location selection
                        if len(self.locations) == 1:
                            self.location_details = self.locations[0]
                            return await self.async_step_location_select()

                        # Multiple locations found - show selection form
                        return await self.async_step_location_select()
                except FlavorProviderError as e:
                    _LOGGER.error("Provider error searching for locations: %s", e)
                    errors["search_term"] = "provider_error"
                except Exception as e:
                    _LOGGER.error("Unexpected error searching for locations: %s", e)
                    errors["search_term"] = "unknown_error"

        return self.async_show_form(
            step_id="location_search", data_schema=LOCATION_SEARCH_SCHEMA, errors=errors
        )

    async def async_step_location_select(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the location selection step."""
        errors = {}

        # If location_details is already set (from single location case), skip this step
        if self.location_details:
            return await self.async_step_final()

        if user_input is not None:
            location_id = user_input[CONF_LOCATION_ID]
            custom_name = user_input.get(CONF_NAME)
            update_interval = user_input.get(
                CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
            )

            try:
                # Verify the location and get details
                self.location_details = await self.provider.get_location_by_id(
                    location_id
                )

                # Test connection to the location
                if not await self.provider.test_connection(location_id):
                    errors[CONF_LOCATION_ID] = "connection_failed"
                else:
                    # Set final unique ID with location
                    await self.async_set_unique_id(
                        f"{DOMAIN}_{self.provider_id}_{location_id}"
                    )
                    self._abort_if_unique_id_configured()

                    # Create the config entry
                    title = custom_name or self.location_details.display_name()
                    return self.async_create_entry(
                        title=title,
                        data={
                            CONF_PROVIDER: self.provider_id,
                            CONF_LOCATION_ID: location_id,
                            CONF_UPDATE_INTERVAL: update_interval,
                            CONF_NAME: custom_name or self.location_details.name,
                        },
                    )
            except FlavorProviderError as e:
                _LOGGER.error("Provider error getting location details: %s", e)
                errors[CONF_LOCATION_ID] = "provider_error"
            except Exception as e:
                _LOGGER.error("Unexpected error getting location details: %s", e)
                errors[CONF_LOCATION_ID] = "unknown_error"

        # Create schema with dynamic location options
        schema = create_location_select_schema(self.locations)

        return self.async_show_form(
            step_id="location_select",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "locations_count": len(self.locations),
            },
        )
