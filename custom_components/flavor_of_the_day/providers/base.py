"""Base class and interface definition for flavor providers."""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import aiohttp
from homeassistant.util import dt as dt_util

if TYPE_CHECKING:
    from datetime import date

    from custom_components.flavor_of_the_day.models import FlavorInfo, LocationInfo


class BaseFlavorProvider(ABC):
    """Base class for flavor providers."""

    def __init__(self, session: aiohttp.ClientSession, config: dict[str, Any]) -> None:
        """Initialize the base flavor provider."""
        self.session = session
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Rate limiting attributes
        self._last_request_time = {}
        self._min_interval = config.get(
            "min_request_interval", 1
        )  # seconds between requests
        self._max_retries = config.get("max_retries", 3)
        self._retry_delay = config.get("retry_delay", 1)  # seconds between retries
        self._timeout = aiohttp.ClientTimeout(
            total=config.get("request_timeout", 30)
        )  # seconds

    async def _rate_limit(self, key: str = "default") -> None:
        """Rate limit requests to avoid overwhelming the provider."""
        now = dt_util.now().timestamp()
        if key in self._last_request_time:
            time_since_last = now - self._last_request_time[key]
            if time_since_last < self._min_interval:
                sleep_time = self._min_interval - time_since_last
                self.logger.debug("Rate limiting for %.2f seconds", sleep_time)
                await asyncio.sleep(sleep_time)
        self._last_request_time[key] = dt_util.now().timestamp()

    async def _make_request_with_retry(
        self, request_func: Any, *args: Any, **kwargs: Any
    ) -> Any:
        """Make a request with retry logic."""
        last_exception = None

        for attempt in range(self._max_retries + 1):
            try:
                # Rate limit before each request
                await self._rate_limit()

                return await request_func(*args, **kwargs)
            except TimeoutError as e:
                last_exception = e
                if attempt < self._max_retries:
                    self.logger.warning(
                        "Request timed out (attempt %s/%s): %s. Retrying in %ss",
                        attempt + 1,
                        self._max_retries + 1,
                        e,
                        self._retry_delay * (attempt + 1),
                    )
                    await asyncio.sleep(
                        self._retry_delay * (attempt + 1)
                    )  # Exponential backoff
                else:
                    self.logger.exception(
                        "Request timed out after %s attempts",
                        self._max_retries + 1,
                    )
                    raise last_exception from e
            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self._max_retries:
                    self.logger.warning(
                        "Request failed (attempt %s/%s): %s. Retrying in %ss",
                        attempt + 1,
                        self._max_retries + 1,
                        e,
                        self._retry_delay * (attempt + 1),
                    )
                    await asyncio.sleep(
                        self._retry_delay * (attempt + 1)
                    )  # Exponential backoff
                else:
                    self.logger.exception(
                        "Request failed after %s attempts",
                        self._max_retries + 1,
                    )
                    raise last_exception from e
            except Exception:
                self.logger.exception("Unexpected error during request")
                raise
        return None  # Explicit return to satisfy linter

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
        self,
        location_id: str,  # noqa: ARG002
        days: int = 7,  # noqa: ARG002
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors (if supported by provider)."""
        return []  # Default: not supported

    async def test_connection(self, location_id: str) -> bool:
        """Test if the provider can successfully get data for a location."""
        try:
            await self.get_current_flavor(location_id)
        except Exception:  # noqa: BLE001
            return False
        else:
            return True
