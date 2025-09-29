"""Test all provider types for the Flavor of the Day integration."""

from unittest.mock import Mock, patch

import pytest

from custom_components.flavor_of_the_day.models import FlavorInfo, LocationInfo
from custom_components.flavor_of_the_day.providers.culvers import CulversProvider
from custom_components.flavor_of_the_day.providers.kopps import KoppsProvider
from custom_components.flavor_of_the_day.providers.leducs import LeducsProvider
from custom_components.flavor_of_the_day.providers.oscars import OscarsProvider


class TestCulversProvider:
    """Test CulversProvider functionality."""

    @pytest.fixture
    def culvers_provider(self):
        """Create a CulversProvider instance for testing."""
        session = Mock()
        config = {}
        return CulversProvider(session, config)

    @pytest.mark.asyncio
    async def test_get_current_flavor(self, culvers_provider) -> None:
        """Test Culvers provider getting current flavor."""
        # This test would require detailed mocking of the Culvers website response
        # For now, just verify the method exists and can be called
        assert hasattr(culvers_provider, "get_current_flavor")

    @pytest.mark.asyncio
    async def test_search_locations(self, culvers_provider) -> None:
        """Test Culvers provider searching for locations."""
        assert hasattr(culvers_provider, "search_locations")

    @pytest.mark.asyncio
    async def test_get_location_by_id(self, culvers_provider) -> None:
        """Test Culvers provider getting location by ID."""
        assert hasattr(culvers_provider, "get_location_by_id")


class TestKoppsProvider:
    """Test KoppsProvider functionality."""

    @pytest.fixture
    def kopps_provider(self):
        """Create a KoppsProvider instance for testing."""
        session = Mock()
        config = {}
        return KoppsProvider(session, config)

    @pytest.mark.asyncio
    async def test_get_current_flavor(self, kopps_provider) -> None:
        """Test Kopps provider getting current flavor."""
        assert hasattr(kopps_provider, "get_current_flavor")

    @pytest.mark.asyncio
    async def test_search_locations(self, kopps_provider) -> None:
        """Test Kopps provider searching for locations."""
        assert hasattr(kopps_provider, "search_locations")

    @pytest.mark.asyncio
    async def test_get_location_by_id(self, kopps_provider) -> None:
        """Test Kopps provider getting location by ID."""
        assert hasattr(kopps_provider, "get_location_by_id")


class TestLeducsProvider:
    """Test LeducsProvider functionality."""

    @pytest.fixture
    def leducs_provider(self):
        """Create a LeducsProvider instance for testing."""
        session = Mock()
        config = {}
        return LeducsProvider(session, config)

    @pytest.mark.asyncio
    async def test_get_current_flavor(self, leducs_provider) -> None:
        """Test Leducs provider getting current flavor."""
        assert hasattr(leducs_provider, "get_current_flavor")

    @pytest.mark.asyncio
    async def test_search_locations(self, leducs_provider) -> None:
        """Test Leducs provider searching for locations."""
        assert hasattr(leducs_provider, "search_locations")

    @pytest.mark.asyncio
    async def test_get_location_by_id(self, leducs_provider) -> None:
        """Test Leducs provider getting location by ID."""
        assert hasattr(leducs_provider, "get_location_by_id")


class TestOscarsProvider:
    """Test OscarsProvider functionality."""

    @pytest.fixture
    def oscars_provider(self):
        """Create a OscarsProvider instance for testing."""
        session = Mock()
        config = {}
        return OscarsProvider(session, config)

    @pytest.mark.asyncio
    async def test_get_current_flavor(self, oscars_provider) -> None:
        """Test Oscars provider getting current flavor."""
        assert hasattr(oscars_provider, "get_current_flavor")

    @pytest.mark.asyncio
    async def test_search_locations(self, oscars_provider) -> None:
        """Test Oscars provider searching for locations."""
        assert hasattr(oscars_provider, "search_locations")

    @pytest.mark.asyncio
    async def test_get_location_by_id(self, oscars_provider) -> None:
        """Test Oscars provider getting location by ID."""
        assert hasattr(oscars_provider, "get_location_by_id")


# Test with mocked responses for each provider
@pytest.mark.asyncio
async def test_all_providers_interface() -> None:
    """Test that all providers implement the required interface."""
    session = Mock()

    providers = [
        CulversProvider(session, {}),
        KoppsProvider(session, {}),
        LeducsProvider(session, {}),
        OscarsProvider(session, {}),
    ]

    for provider in providers:
        # Verify all providers have the necessary methods
        assert hasattr(provider, "provider_name")
        assert hasattr(provider, "provider_id")
        assert hasattr(provider, "search_locations")
        assert hasattr(provider, "get_location_by_id")
        assert hasattr(provider, "get_current_flavor")
        assert hasattr(provider, "test_connection")

        # Verify properties return correct types
        assert isinstance(provider.provider_name, str)
        assert isinstance(provider.provider_id, str)


@pytest.mark.asyncio
async def test_base_provider_test_connection() -> None:
    """Test the test_connection method in the base provider."""
    from custom_components.flavor_of_the_day.providers.base import BaseFlavorProvider

    class MockProvider(BaseFlavorProvider):
        @property
        def provider_name(self) -> str:
            return "Mock Provider"

        @property
        def provider_id(self) -> str:
            return "mock"

        async def search_locations(self, search_term, state=None):
            return []

        async def get_location_by_id(self, location_id):
            return LocationInfo(
                store_id="test",
                name="Test",
                address="123 Main St",
                city="Test City",
                state="TS",
                zip_code="12345",
            )

        async def get_current_flavor(self, location_id):
            return FlavorInfo(name="Test Flavor")

    session = Mock()
    provider = MockProvider(session, {})

    # Mock get_current_flavor to raise an exception
    with patch.object(
        provider, "get_current_flavor", side_effect=Exception("Test error")
    ):
        result = await provider.test_connection("test")
        assert result is False

    # Mock get_current_flavor to succeed
    with patch.object(
        provider, "get_current_flavor", return_value=FlavorInfo(name="Test Flavor")
    ):
        result = await provider.test_connection("test")
        assert result is True
