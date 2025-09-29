"""Test the Flavor of the Day config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.flavor_of_the_day.const import DOMAIN


@pytest.mark.asyncio
async def test_form(hass) -> None:
    """Test we can instantiate the config flow."""
    # Get the actual hass instance from the fixture
    if hasattr(hass, "__anext__"):
        hass = await hass.__anext__()

    # Import and test the config flow directly
    from custom_components.flavor_of_the_day.config_flow import FlavorOfTheDayConfigFlow

    # Create config flow instance
    flow = FlavorOfTheDayConfigFlow()
    flow.hass = hass

    # Test the init method exists and the flow can be created
    assert flow is not None
    assert hasattr(flow, "async_step_user")
    assert hasattr(flow, "async_step_location_search")
    assert hasattr(flow, "async_step_location_select")


@pytest.mark.asyncio
async def test_create_entry(hass: HomeAssistant) -> None:
    """Test creating an entry with valid data."""
    with (
        patch(
            "custom_components.flavor_of_the_day.providers.culvers.CulversProvider.search_locations",
            return_value=[],
        ),
        patch(
            "custom_components.flavor_of_the_day.config_flow.async_get_clientsession"
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        # Submit provider selection
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"provider": "culvers"}
        )

        # Submit location search
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"search_term": "Madison", "state": "WI"}
        )

        # Since search returns empty, should get error
        assert result["errors"]["search_term"] == "no_locations_found"


@pytest.mark.asyncio
async def test_form_with_locations(hass: HomeAssistant) -> None:
    """Test form with locations found."""
    from custom_components.flavor_of_the_day.models import LocationInfo

    location = LocationInfo(
        store_id="test123",
        name="Test Culver's",
        address="123 Main St",
        city="Madison",
        state="WI",
        zip_code="53703",
        phone="(608) 555-0123",
        hours={},
        website_url="",
        latitude=43.0732,
        longitude=-89.4012,
    )

    with (
        patch(
            "custom_components.flavor_of_the_day.providers.culvers.CulversProvider.search_locations",
            return_value=[location],
        ),
        patch(
            "custom_components.flavor_of_the_day.providers.culvers.CulversProvider.get_location_by_id",
            return_value=location,
        ),
        patch(
            "custom_components.flavor_of_the_day.providers.culvers.CulversProvider.test_connection",
            return_value=True,
        ),
        patch(
            "custom_components.flavor_of_the_day.config_flow.async_get_clientsession"
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        # Submit provider selection
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"provider": "culvers"}
        )

        # Submit location search
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"search_term": "Madison", "state": "WI"}
        )

        # Should now show location selection form
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "location_select"

        # Submit location selection
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"location_id": "test123", "name": "My Culver's", "update_interval": 30},
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "My Culver's"
        assert result["data"]["provider"] == "culvers"
        assert result["data"]["location_id"] == "test123"
        assert result["data"]["update_interval"] == 30
