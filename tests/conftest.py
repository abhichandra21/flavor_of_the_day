"""Common test fixtures for Flavor of the Day integration."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.core import HomeAssistant

# Import Home Assistant test fixtures
pytest_plugins = "pytest_homeassistant_custom_component.common"

from custom_components.flavor_of_the_day.const import (
    CONF_LOCATION_ID,
    CONF_PROVIDER,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
)
from custom_components.flavor_of_the_day.coordinator import FlavorUpdateCoordinator
from custom_components.flavor_of_the_day.models import FlavorInfo, LocationInfo


@pytest.fixture
def mock_flavor_info():
    """Mock FlavorInfo."""
    return FlavorInfo(
        name="Test Flavor",
        description="Test flavor description",
        ingredients=["ingredient1", "ingredient2"],
        allergens=["allergen1"],
        available_date=None,
        price="$4.99",
    )


@pytest.fixture
def mock_location_info():
    """Mock LocationInfo."""
    return LocationInfo(
        store_id="test123",
        name="Test Store",
        address="123 Main St",
        city="Test City",
        state="TS",
        zip_code="12345",
        phone="(123) 456-7890",
        hours={"monday": "8am-10pm"},
        website_url="https://example.com",
        latitude=43.0732,
        longitude=-89.4012,
    )


@pytest.fixture
def mock_provider(mock_location_info, mock_flavor_info):
    """Mock BaseFlavorProvider."""
    with patch(
        "custom_components.flavor_of_the_day.providers.culvers.CulversProvider"
    ) as mock_class:
        mock_instance = mock_class.return_value
        mock_instance.provider_name = "Test Provider"
        mock_instance.provider_id = "test_provider"
        mock_instance.search_locations.return_value = [mock_location_info]
        mock_instance.get_location_by_id.return_value = mock_location_info
        mock_instance.get_current_flavor.return_value = mock_flavor_info
        mock_instance.test_connection.return_value = True

        yield mock_instance


@pytest.fixture
def mock_coordinator(hass: HomeAssistant, mock_provider, mock_flavor_info):
    """Mock FlavorUpdateCoordinator."""
    coordinator = Mock(spec=FlavorUpdateCoordinator)
    coordinator.data = mock_flavor_info
    coordinator.config_entry = Mock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.data = {"name": "Test Sensor"}
    coordinator.provider = mock_provider
    coordinator.location_id = "test_location_id"
    coordinator.async_request_refresh = AsyncMock()

    return coordinator


@pytest.fixture
def mock_config_entry_data():
    """Mock config entry data."""
    return {
        CONF_PROVIDER: "culvers",
        CONF_LOCATION_ID: "test_location",
        CONF_UPDATE_INTERVAL: 30,
        "name": "Test Entry",
    }


@pytest.fixture
def mock_sensor_entity_description():
    """Mock sensor entity description."""
    return SensorEntityDescription(
        key="flavor_of_the_day",
        name="Flavor of the Day",
        icon="mdi:ice-cream",
    )


@pytest.fixture
async def setup_integration(hass: HomeAssistant, mock_config_entry_data):
    """Set up the flavor_of_the_day integration."""
    config_entry = Mock()
    config_entry.entry_id = "test_entry"
    config_entry.data = mock_config_entry_data
    config_entry.options = {}

    with (
        patch(
            "custom_components.flavor_of_the_day.providers.culvers.CulversProvider"
        ) as mock_provider_class,
        patch("custom_components.flavor_of_the_day.async_get_clientsession"),
    ):
        mock_provider = mock_provider_class.return_value
        mock_provider.get_current_flavor.return_value = FlavorInfo(
            name="Test Flavor", description="Test Description"
        )

        hass.data.setdefault(DOMAIN, {})

        # Import and call async_setup_entry
        from custom_components.flavor_of_the_day import async_setup_entry

        # Call the setup function
        result = await async_setup_entry(hass, config_entry)
        assert result is True

        yield config_entry
