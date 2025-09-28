"""Global fixtures for flavor_of_the_day integration tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield


@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture():
    """Skip calls to get data from API."""
    with patch(
        "custom_components.flavor_of_the_day.FlavorUpdateCoordinator._async_update_data"
    ):
        yield


@pytest.fixture(name="mock_provider")
def mock_provider_fixture():
    """Mock a flavor provider."""
    with patch(
        "custom_components.flavor_of_the_day.providers.culvers.CulversProvider"
    ) as mock_provider:
        provider = mock_provider.return_value
        provider.search_locations.return_value = [
            {
                "store_id": "123",
                "name": "Test Location",
                "address": "123 Test St",
                "city": "Test City",
                "state": "WI",
                "zip_code": "12345",
            }
        ]
        provider.get_location_by_id.return_value = {
            "store_id": "123",
            "name": "Test Location",
            "address": "123 Test St",
            "city": "Test City",
            "state": "WI",
            "zip_code": "12345",
        }
        provider.get_current_flavor.return_value = {
            "name": "Vanilla",
            "description": "Classic vanilla custard",
            "ingredients": ["Milk", "Cream", "Sugar", "Vanilla"],
            "allergens": ["Dairy"],
            "image_url": None,
            "available_date": None,
            "price": "$2.99",
            "nutrition_info": {},
        }
        provider.test_connection.return_value = True
        yield provider