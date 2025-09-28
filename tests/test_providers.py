"""Test the provider system."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import aiohttp
import pytest
from custom_components.flavor_of_the_day.providers.base import BaseFlavorProvider
from custom_components.flavor_of_the_day.providers.culvers import CulversProvider


class TestBaseFlavorProvider:
    """Test the base provider."""

    def test_abstract_methods(self):
        """Test that base provider cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseFlavorProvider()


class TestCulversProvider:
    """Test the Culvers provider."""

    async def test_search_locations_mock(self):
        """Test searching for locations with mocked HTTP response."""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_response = AsyncMock()
        mock_response.text.return_value = """
        <div data-testid="location-card">
            <span>123 Main St</span>
            <span>Test City, WI 12345</span>
        </div>
        """
        mock_session.get.return_value.__aenter__.return_value = mock_response

        config = {"provider": "culvers"}
        provider = CulversProvider(mock_session, config)

        with patch.object(provider, '_parse_location_data') as mock_parse:
            mock_parse.return_value = [{
                "store_id": "123",
                "name": "Culver's Test Location",
                "address": "123 Main St",
                "city": "Test City",
                "state": "WI",
                "zip_code": "12345",
            }]

            locations = await provider.search_locations("Test City", "WI")

            assert len(locations) == 1
            assert locations[0]["city"] == "Test City"
            assert locations[0]["state"] == "WI"

    async def test_test_connection(self):
        """Test connection testing."""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.get.return_value.__aenter__.return_value = mock_response

        config = {"provider": "culvers"}
        provider = CulversProvider(mock_session, config)

        result = await provider.test_connection()
        assert result is True

    async def test_test_connection_failure(self):
        """Test connection testing failure."""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.get.side_effect = aiohttp.ClientError("Connection failed")

        config = {"provider": "culvers"}
        provider = CulversProvider(mock_session, config)

        result = await provider.test_connection()
        assert result is False