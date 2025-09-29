"""Culver's provider for the Flavor of the Day integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import aiohttp
from homeassistant.util import dt as dt_util

from custom_components.flavor_of_the_day.exceptions import (
    FlavorNotAvailableError,
    LocationNotFoundError,
)
from custom_components.flavor_of_the_day.models import FlavorInfo, LocationInfo
from custom_components.flavor_of_the_day.providers.base import BaseFlavorProvider

if TYPE_CHECKING:
    from datetime import date

_LOGGER = logging.getLogger(__name__)

HTTP_OK = 200


class CulversProvider(BaseFlavorProvider):
    """Culver's provider implementation."""

    BASE_URL = "https://www.culvers.com"

    @property
    def provider_name(self) -> str:
        """Display name for this provider."""
        return "Culver's"

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        return "culvers"

    async def search_locations(
        self, search_term: str, state: str | None = None
    ) -> list[LocationInfo]:
        """Search for Culver's locations by city, zip, or address."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

        if state:
            search_location = f"{search_term}, {state}"
        else:
            search_location = search_term

        params = {
            "location": search_location,
            "radius": "40233",  # ~25 miles in meters
            "limit": "25",
            "layer": "",
        }
        url = f"{self.BASE_URL}/api/locator/getLocations"

        try:
            _LOGGER.debug("Searching for Culver's locations with url %s and params %s", url, params)
            async with self.session.get(
                url, headers=headers, params=params, timeout=self._timeout
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return self._parse_search_response(data)
        except aiohttp.ClientError:
            _LOGGER.exception("Network error during Culver's location search")
            return []
        except Exception:
            _LOGGER.exception("Error during Culver's location search")
            return []

    def _parse_search_response(self, response: dict[str, Any]) -> list[LocationInfo]:
        """Parse the response from the location search API."""
        locations = []
        if not isinstance(response, dict) or "data" not in response or "geofences" not in response["data"]:
            _LOGGER.warning("Culver's location search response is not in the expected format: %s", response)
            return []

        for item in response["data"]["geofences"]:
            location = self._create_location_from_api_data(item)
            if location:
                locations.append(location)
        return locations

    def _create_location_from_api_data(self, item: dict[str, Any]) -> LocationInfo | None:
        """Create a LocationInfo object from the API data."""
        try:
            data = item["metadata"]
            store_id = data["slug"]
            name = f"Culver's - {item['description']}"
            address = data["street"]
            city = data["city"]
            state = data["state"]
            zip_code = data["postalCode"]
            website_url = f"{self.BASE_URL}/restaurants/{store_id}"

            latitude = None
            longitude = None
            if 'geometryCenter' in item and 'coordinates' in item['geometryCenter']:
                coords = item['geometryCenter']['coordinates']
                if len(coords) == 2:
                    longitude = coords[0]
                    latitude = coords[1]

            return LocationInfo(
                store_id=store_id,
                name=name,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                phone=None, # Not available in this response
                website_url=website_url,
                latitude=latitude,
                longitude=longitude,
            )
        except (KeyError, ValueError, TypeError) as e:
            _LOGGER.warning("Could not parse location data: %s. Data: %s", e, item)
            return None

    async def get_location_by_id(self, location_id: str) -> LocationInfo:
        """Get specific location details by store ID."""
        # This is a mock implementation to satisfy the abstract base class.
        _LOGGER.warning("get_location_by_id is using a mock implementation.")
        return LocationInfo(
            store_id=location_id,
            name=f"Culver's - {location_id.replace('-', ' ').title()}",
            city=location_id.split('-')[1].title() if '-' in location_id else "",
            state="",
            address="",
            zip_code="",
            phone="",
            website_url=f"{self.BASE_URL}/restaurants/{location_id}"
        )

    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day from Culver's."""
        zip_code = self.config.get("zip_code")
        if not zip_code:
            # Fallback for older configs that don't have the zip code stored.
            # This will do a broad search and might not be accurate.
            _LOGGER.warning("Zip code not found in config, falling back to broad search.")
            parts = location_id.split('-')
            if len(parts) > 1 and len(parts[-1]) == 2 and parts[-1].isalpha(): # Check for 2-letter state code
                state = parts[-1]
                city = "-".join(parts[:-1])
                search_term = f"{city}, {state}"
            else:
                search_term = parts[0] # Fallback to just the first part
        else:
            search_term = zip_code

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        params = {
            "location": search_term,
            "radius": "40233",
            "limit": "25",
            "layer": "",
        }
        url = f"{self.BASE_URL}/api/locator/getLocations"

        try:
            async with self.session.get(url, headers=headers, params=params, timeout=self._timeout) as response:
                response.raise_for_status()
                data = await response.json()

                if not isinstance(data, dict) or "data" not in data or "geofences" not in data["data"]:
                    msg = f"Unexpected response for location {location_id}"
                    raise FlavorNotAvailableError(msg)

                geofences = data["data"]["geofences"]
                if not geofences:
                    msg = f"Location {location_id} not found in API response"
                    raise FlavorNotAvailableError(msg)

                location_data = None
                for item in geofences:
                    if item.get("metadata", {}).get("slug") == location_id:
                        location_data = item["metadata"]
                        break
                
                if not location_data:
                    msg = f"Could not find location {location_id} in API response"
                    raise FlavorNotAvailableError(msg)

                flavor_name = location_data.get("flavorOfDayName")
                if not flavor_name or "closed" in flavor_name.lower():
                    msg = f"Flavor of the day not available for {location_id}"
                    raise FlavorNotAvailableError(msg)

                image_slug = location_data.get("flavorOfDaySlug")
                image_url = f"https://cdn.culvers.com/menu-item-detail/{image_slug}" if image_slug else None

                return FlavorInfo(
                    name=flavor_name,
                    description=location_data.get("flavorOfTheDayDescription"),
                    image_url=image_url,
                    available_date=dt_util.now(),
                )

        except aiohttp.ClientError as e:
            _LOGGER.exception("Network error getting flavor for %s", location_id)
            msg = f"Network error accessing Culver's API for location {location_id}"
            raise FlavorNotAvailableError(msg) from e
        except Exception as e:
            _LOGGER.exception("Error getting flavor for %s", location_id)
            msg = f"Could not retrieve flavor for location {location_id}"
            raise FlavorNotAvailableError(msg) from e

    async def get_upcoming_flavors(
        self, location_id: str, days: int = 7
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors (if supported by Culver's)."""
        return []
