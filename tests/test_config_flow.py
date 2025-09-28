"""Test the Flavor of the Day config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.flavor_of_the_day.config_flow import FlavorOfTheDayConfigFlow
from custom_components.flavor_of_the_day.const import DOMAIN


async def test_config_flow_user_step(hass: HomeAssistant):
    """Test the user step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_config_flow_provider_selection(hass: HomeAssistant, mock_provider):
    """Test provider selection step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("custom_components.flavor_of_the_day.config_flow.PROVIDER_CLASSES", {"culvers": mock_provider.__class__}):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"provider": "culvers"},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["step_id"] == "location_search"


async def test_config_flow_location_search(hass: HomeAssistant, mock_provider):
    """Test location search step."""
    # Start the flow and select provider
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("custom_components.flavor_of_the_day.config_flow.PROVIDER_CLASSES", {"culvers": mock_provider.__class__}):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"provider": "culvers"},
        )

        # Search for locations
        result3 = await hass.config_entries.flow.async_configure(
            result2["flow_id"],
            {"search_term": "Test City", "state": "WI"},
        )

    assert result3["type"] == FlowResultType.FORM
    assert result3["step_id"] == "location_select"


async def test_config_flow_complete(hass: HomeAssistant, mock_provider):
    """Test completing the config flow."""
    # Start the flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("custom_components.flavor_of_the_day.config_flow.PROVIDER_CLASSES", {"culvers": mock_provider.__class__}):
        # Select provider
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"provider": "culvers"},
        )

        # Search for locations
        result3 = await hass.config_entries.flow.async_configure(
            result2["flow_id"],
            {"search_term": "Test City"},
        )

        # Select location and complete
        result4 = await hass.config_entries.flow.async_configure(
            result3["flow_id"],
            {
                "location_id": "123",
                "update_interval": 30,
                "name": "Test Location",
            },
        )

    assert result4["type"] == FlowResultType.CREATE_ENTRY
    assert result4["title"] == "Test Location"
    assert result4["data"]["provider"] == "culvers"
    assert result4["data"]["location_id"] == "123"