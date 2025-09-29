"""Config flow for Flavor of the Day integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_STATE
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_LOCATION_ID,
    CONF_PROVIDER,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    US_STATES,
)
from .exceptions import FlavorProviderError
from .providers.culvers import CulversProvider
from .providers.kopps import KoppsProvider
from .providers.oscars import OscarsProvider
from .providers.goodberrys import GoodberrysProvider

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult

    from .models import LocationInfo
    from .providers.base import BaseFlavorProvider

# Constants for validation
MIN_SEARCH_TERM_LENGTH = 2
MIN_UPDATE_INTERVAL = 5
MAX_UPDATE_INTERVAL = 1440

_LOGGER = logging.getLogger(__name__)

# Provider selection schema with HA selector
USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PROVIDER): SelectSelector(
            SelectSelectorConfig(
                options=[
                    SelectOptionDict(value="culvers", label="Culver's"),
                    SelectOptionDict(value="kopps", label="Kopp's Frozen Custard"),
                    SelectOptionDict(value="oscars", label="Oscar's Frozen Custard"),
                    SelectOptionDict(value="goodberrys", label="Goodberry's Frozen Custard"),
                ],
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
    }
)

# Location search schema with HA selectors
LOCATION_SEARCH_SCHEMA = vol.Schema(
    {
        vol.Required("search_term"): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.TEXT,
            )
        ),
        vol.Optional("state"): SelectSelector(
            SelectSelectorConfig(
                options=[
                    SelectOptionDict(value=abbr, label=name)
                    for abbr, name in US_STATES.items()
                ],
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
    }
)


# Base location selection schema (will be created dynamically)
def create_location_select_schema(locations: list[LocationInfo]) -> vol.Schema:
    """Create location selection schema with dynamic options."""
    location_options = [
        SelectOptionDict(value=location.store_id, label=location.display_name())
        for location in locations
    ]

    return vol.Schema(
        {
            vol.Required(CONF_LOCATION_ID): SelectSelector(
                SelectSelectorConfig(
                    options=location_options,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONF_NAME): TextSelector(
                TextSelectorConfig(
                    type=TextSelectorType.TEXT,
                )
            ),
            vol.Optional(
                CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
            ): NumberSelector(
                NumberSelectorConfig(
                    min=5,
                    max=1440,
                    step=1,
                    unit_of_measurement="minutes",
                    mode=NumberSelectorMode.BOX,
                )
            ),
        }
    )


PROVIDER_CLASSES = {
    "culvers": CulversProvider,
    "kopps": KoppsProvider,
    "oscars": OscarsProvider,
    "goodberrys": GoodberrysProvider,
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

    def _get_provider_instance(self, provider_id: str) -> BaseFlavorProvider:
        """Get a provider instance based on provider ID."""
        session = async_get_clientsession(self.hass)
        if provider_id in PROVIDER_CLASSES:
            provider_class = PROVIDER_CLASSES[provider_id]
            return provider_class(session, {})
        msg = f"Unknown provider ID: {provider_id}"
        raise ValueError(msg)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self.provider_id = user_input[CONF_PROVIDER]

            # Create the provider instance
            session = async_get_clientsession(self.hass)
            provider_class = PROVIDER_CLASSES[self.provider_id]
            self.provider = provider_class(session, {})

            if self.provider_id in ["kopps", "oscars"]:
                # For providers with fixed locations, get all locations
                self.locations = await self.provider.search_locations("")
                return await self.async_step_location_select()
            else:
                # For other providers, go to location search
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
            errors = {}

            search_term = user_input.get("search_term", "").strip()
            state = user_input.get(CONF_STATE)

            min_search_term_len = 2

            if not search_term:
                errors["search_term"] = "required"
            elif len(search_term) < min_search_term_len:
                errors["search_term"] = "too_short"
            else:
                try:
                    # Use the provider that was already selected in the first step
                    if not self.provider:
                        self.provider = self._get_provider_instance(self.provider_id)
                    locations = await self.provider.search_locations(search_term, state)
                    if not locations:
                        errors["search_term"] = "no_locations_found"
                    else:
                        self.locations = locations
                        return await self.async_step_location_select()
                except FlavorProviderError:
                    _LOGGER.exception("Provider error searching for locations")
                    errors["search_term"] = "provider_error"
                except (TimeoutError, aiohttp.ClientError):
                    _LOGGER.exception("Network error searching for locations")
                    errors["search_term"] = "network_error"
                except Exception:
                    _LOGGER.exception("Unexpected error searching for locations")
                    errors["search_term"] = "unknown_error"

        return self.async_show_form(
            step_id="location_search", data_schema=LOCATION_SEARCH_SCHEMA, errors=errors
        )

    async def async_step_location_select(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the location selection step."""
        errors = {}
        if user_input is not None:
            location_id = user_input[CONF_LOCATION_ID]

            selected_location = next((loc for loc in self.locations if loc.store_id == location_id), None)

            if not selected_location:
                errors[CONF_LOCATION_ID] = "invalid_location"
            else:
                await self.async_set_unique_id(f"{self.provider_id}_{location_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=selected_location.name,
                    data={
                        CONF_PROVIDER: self.provider_id,
                        CONF_LOCATION_ID: location_id,
                        "zip_code": selected_location.zip_code,
                        CONF_UPDATE_INTERVAL: user_input.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    },
                )


        return self.async_show_form(
            step_id="location_select",
            data_schema=create_location_select_schema(self.locations),
            description_placeholders={"locations_count": len(self.locations)},
            errors=errors,
        )

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> FlavorOfTheDayOptionsFlow:
        """Get the options flow for this handler."""
        return FlavorOfTheDayOptionsFlow(config_entry)


class FlavorOfTheDayOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for Flavor of the Day."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=5,
                            max=1440,
                            step=1,
                            unit_of_measurement="minutes",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )