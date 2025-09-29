"""Test the Flavor of the Day providers."""

from unittest.mock import Mock, patch

import pytest

from custom_components.flavor_of_the_day.exceptions import (
    FlavorNotAvailableError,
    LocationNotFoundError,
)
from custom_components.flavor_of_the_day.providers.culvers import CulversProvider


@pytest.mark.asyncio
async def test_culvers_provider_get_current_flavor() -> None:
    """Test Culvers provider getting current flavor with mock data."""
    session = Mock()
    config = {}
    provider = CulversProvider(session, config)

    # Test with a deterministic location ID to get a consistent flavor
    # The mock implementation uses MD5 hash of location_id to select flavor
    flavor = await provider.get_current_flavor("culvers-madison-west")

    # The flavor should be deterministic based on location ID hash
    assert flavor.name in [
        "Chocolate Chip Cookie Dough",
        "Turtle Dove",
        "Raspberry Cheesecake",
        "Mint Oreo",
        "Peanut Butter Cup",
        "Caramel Pecan",
        "Strawberry",
        "Vanilla",
    ]
    assert "Delicious" in flavor.description
    assert "custard made fresh daily at Culver's" in flavor.description
    assert flavor.available_date is not None


@pytest.mark.asyncio
async def test_culvers_provider_get_current_flavor_error() -> None:
    """Test Culvers provider getting current flavor with error."""
    session = Mock()
    config = {}
    provider = CulversProvider(session, config)

    # Test error handling by patching the _make_request_with_retry method to raise an exception
    with (
        patch.object(
            provider, "_make_request_with_retry", side_effect=Exception("Network error")
        ),
        pytest.raises(FlavorNotAvailableError),
    ):
        await provider.get_current_flavor("test_location")


@pytest.mark.asyncio
async def test_culvers_provider_search_locations() -> None:
    """Test Culvers provider searching for locations with mock data."""
    session = Mock()
    config = {}
    provider = CulversProvider(session, config)

    # Test searching for Madison locations (should return 2 mock locations)
    locations = await provider.search_locations("Madison", "WI")
    assert len(locations) == 2
    assert locations[0].store_id == "culvers-madison-west"
    assert locations[0].name == "Culver's - Madison West"
    assert locations[0].city == "Madison"
    assert locations[0].state == "WI"
    assert locations[1].store_id == "culvers-madison-east"
    assert locations[1].name == "Culver's - Madison East"

    # Test searching for Milwaukee locations (should return 1 mock location)
    locations = await provider.search_locations("Milwaukee", "WI")
    assert len(locations) == 1
    assert locations[0].store_id == "culvers-milwaukee-north"
    assert locations[0].name == "Culver's - Milwaukee North"

    # Test searching for non-existent location (should return empty list)
    locations = await provider.search_locations("NonExistent", "WI")
    assert len(locations) == 0


@pytest.mark.asyncio
async def test_culvers_provider_search_locations_error() -> None:
    """Test Culvers provider searching for locations with error."""
    session = Mock()
    config = {}
    provider = CulversProvider(session, config)

    # Test error handling by patching the _make_request_with_retry method to raise an exception
    with patch.object(
        provider, "_make_request_with_retry", side_effect=Exception("Network error")
    ):
        locations = await provider.search_locations("Madison", "WI")
        assert locations == []  # Should return empty list on error


@pytest.mark.asyncio
async def test_culvers_provider_get_location_by_id() -> None:
    """Test Culvers provider getting location by ID with mock data."""
    session = Mock()
    config = {}
    provider = CulversProvider(session, config)

    # Test getting a known mock location
    location = await provider.get_location_by_id("culvers-madison-west")
    assert location.store_id == "culvers-madison-west"
    assert location.name == "Culver's - Madison West"
    assert location.address == "702 N High Point Rd"
    assert location.city == "Madison"
    assert location.state == "WI"
    assert location.zip_code == "53717"
    assert location.phone == "(608) 833-1000"


@pytest.mark.asyncio
async def test_culvers_provider_get_location_by_id_not_found() -> None:
    """Test Culvers provider getting location by ID that doesn't exist."""
    session = Mock()
    config = {}
    provider = CulversProvider(session, config)

    # Test getting a non-existent location (should raise LocationNotFoundError)
    with pytest.raises(LocationNotFoundError):
        await provider.get_location_by_id("nonexistent-location-id")
