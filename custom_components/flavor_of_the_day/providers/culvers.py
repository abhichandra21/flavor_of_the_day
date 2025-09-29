"""Culver's provider for the Flavor of the Day integration."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import aiohttp
from bs4 import BeautifulSoup
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
        params = {
            "location": search_term,
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
        url = f"{self.BASE_URL}/restaurants/{location_id}"
        _LOGGER.debug("Getting flavor for location %s from %s", location_id, url)

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        }

        try:
            async with self.session.get(url, headers=headers, timeout=self._timeout) as response:
                response.raise_for_status()
                html = await response.text()
                flavor_info = self._extract_flavor_from_restaurant_page(html)
                if flavor_info:
                    return flavor_info

                msg = f"Flavor of the day not found on page for location {location_id}"
                raise FlavorNotAvailableError(msg)

        except aiohttp.ClientError as e:
            _LOGGER.exception("Network error getting flavor for %s", location_id)
            msg = f"Network error accessing Culver's page for location {location_id}"
            raise FlavorNotAvailableError(msg) from e
        except Exception as e:
            _LOGGER.exception("Error getting flavor for %s", location_id)
            msg = f"Could not retrieve flavor for location {location_id}"
            raise FlavorNotAvailableError(msg) from e

    def _extract_flavor_from_restaurant_page(self, html: str) -> FlavorInfo | None:
        """Extract flavor information from restaurant page."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Find the "Today's Flavor of the Day" subheading
            subheading = soup.find("h3", string="Today’s Flavor of the Day")
            if subheading:
                flavor_heading = subheading.find_previous_sibling("h2")
                if flavor_heading:
                    flavor_name = flavor_heading.get_text(strip=True)
                    if flavor_name:
                        _LOGGER.debug("Found flavor via h3 sibling search: %s", flavor_name)
                        return FlavorInfo(name=flavor_name, available_date=dt_util.now())

            # Fallback to __NEXT_DATA__ parsing
            script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
            if script_tag and script_tag.string:
                json_data = json.loads(script_tag.string)
                _LOGGER.debug("Falling back to __NEXT_DATA__ parsing")

                if "props" in json_data and "pageProps" in json_data["props"] and "restaurant" in json_data["props"]["pageProps"]:
                    restaurant_data = json_data["props"]["pageProps"]["restaurant"]
                    
                    fotd = restaurant_data.get("FlavorOfTheDay")
                    if fotd and fotd.get("Name"):
                        flavor_name = fotd["Name"]
                        _LOGGER.debug("Found flavor in restaurant data: %s", flavor_name)
                        return FlavorInfo(
                            name=flavor_name,
                            description=fotd.get("Description"),
                            available_date=dt_util.now(),
                        )

            return None

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            _LOGGER.debug("Error parsing restaurant data: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error extracting flavor from restaurant page: %s", e)
            return None

    async def get_upcoming_flavors(
        self, location_id: str, days: int = 7
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors (if supported by Culver's)."""
        return []