"""Global fixtures for flavor_of_the_day integration."""

from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import pytest
from aioresponses import aioresponses
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.flavor_of_the_day.const import DOMAIN
from tests.const import CONFIG_DATA, COORDINATOR_DATA


# This fixture enables loading custom integrations in all tests.
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):  # noqa: ARG001, ANN001, ANN201
    """Enable custom integration tests."""
    return


# This fixture prevents HomeAssistant from creating/dismissing persistent notifications.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture() -> Generator[None]:
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


@pytest.fixture
def mock_flavor_coordinator() -> Generator[Any]:
    """Mock coordinator data."""
    with patch(
        "custom_components.flavor_of_the_day.FlavorUpdateCoordinator._async_update_data"
    ) as mock_value:
        mock_value.return_value = COORDINATOR_DATA
        yield


@pytest.fixture
def mock_aioclient() -> Generator[aioresponses]:
    """Fixture to mock aioclient calls."""
    with aioresponses() as m:
        yield m


@pytest.fixture(name="integration")
async def integration_fixture(hass: HomeAssistant) -> MockConfigEntry:
    """Set up the flavor_of_the_day integration."""
    entry = MockConfigEntry(
        domain=DOMAIN, title="Test Location", data=CONFIG_DATA, version=1
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry
