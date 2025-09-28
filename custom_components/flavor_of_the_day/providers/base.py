"""Base class for flavor providers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date
from typing import TYPE_CHECKING, Any

import aiohttp

if TYPE_CHECKING:
    from ..models import FlavorInfo, LocationInfo


class BaseFlavorProvider(ABC):
    """Base class for flavor providers."""

    def __init__(self, session: aiohttp.ClientSession, config: dict[str, Any]) -> None:
        self.session = session
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Display name for this provider."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier for this provider (lowercase, no spaces)."""

    @abstractmethod
    async def search_locations(
        self, search_term: str, state: str | None = None
    ) -> list[LocationInfo]:
        """Search for store locations by city, zip, or address."""

    @abstractmethod
    async def get_location_by_id(self, location_id: str) -> LocationInfo:
        """Get specific location details by store ID."""

    @abstractmethod
    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day."""

    async def get_upcoming_flavors(
        self, location_id: str, days: int = 7
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors (if supported by provider)."""
        return []  # Default: not supported

    async def test_connection(self, location_id: str) -> bool:
        """Test if provider can connect to store data."""
        try:
            await self.get_current_flavor(location_id)
            return True
        except Exception:
            return False
