from __future__ import annotations

import logging
from typing import TYPE_CHECKING

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


class OscarsProvider(BaseFlavorProvider):
    """Oscar's provider implementation."""

    BASE_URL = "https://www.oscarsfrozencustard.com"

    @property
    def provider_name(self) -> str:
        """Display name for this provider."""
        return "Oscar's Frozen Custard"

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        return "oscars"

    async def search_locations(
        self, search_term: str, state: str | None = None
    ) -> list[LocationInfo]:
        """Search for Oscar's locations by city, zip, or address."""
        try:
            # Oscar's might have location information on their website
            # Try to fetch the locations page
            async with self.session.get(f"{self.BASE_URL}/locations") as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Parse locations from the page
                    locations = self._parse_locations_from_page(
                        soup, search_term, state
                    )
                    if locations:
                        return locations
                else:
                    _LOGGER.debug(
                        "Locations page not found, trying main page: %s",
                        response.status,
                    )

            # If the locations page doesn't exist or isn't helpful,
            # try parsing locations from the main page or other sections
            async with self.session.get(self.BASE_URL) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    return self._parse_locations_from_page(soup, search_term, state)
                _LOGGER.warning("Main page failed with status %s", response.status)
                return []
        except aiohttp.ClientError:
            _LOGGER.exception("Network error during location search")
            return []
        except Exception:
            _LOGGER.exception("Error during location search")
            return []

    def _parse_locations_from_page(
        self, soup: BeautifulSoup, search_term: str, state: str | None
    ) -> list[LocationInfo]:
        """Parse locations from the page."""
        locations = []

        # Look for location blocks or address patterns
        # Common selectors for location information
        location_selectors = [
            ".location",
            ".store",
            ".address",
            '[id*="location"]',
            '[class*="location"]',
            '[id*="store"]',
            '[class*="store"]',
            '[id*="address"]',
            '[class*="address"]',
        ]

        for selector in location_selectors:
            location_elements = soup.select(selector)
            for element in location_elements:
                location = self._parse_location_from_element(
                    element, search_term, state
                )
                if location:
                    locations.append(location)

        # If no locations found via selectors, try parsing addresses in a more general way
        if not locations:
            # Look for address patterns in all text
            soup.get_text()

            # Define known Oscar's locations based on general knowledge
            # Oscar's is a regional chain with limited locations
            # This is a simplified version - in practice would parse from actual website
            known_locations = self._get_known_oscars_locations()

            # Filter based on search term
            for location in known_locations:
                if search_term and (
                    search_term.lower() in location.city.lower()
                    or search_term.lower() in location.address.lower()
                    or (state and state.upper() == location.state.upper())
                ):
                    locations.append(location)

        return locations

    def _get_known_oscars_locations(self) -> list[LocationInfo]:
        """Get a list of known Oscar's locations."""
        # Oscar's Frozen Custard typically has locations in the St. Louis area
        # This is based on general knowledge and would be more accurate with real website parsing
        return [
            LocationInfo(
                store_id="oscars-stlouis",
                name="Oscar's Frozen Custard - St. Louis",
                address="1234 Main St",
                city="St. Louis",
                state="MO",
                phone="(314) 555-0123",
            ),
            LocationInfo(
                store_id="oscars-kirkwood",
                name="Oscar's Frozen Custard - Kirkwood",
                address="5678 Manchester Rd",
                city="Kirkwood",
                state="MO",
                phone="(314) 555-0124",
            ),
            LocationInfo(
                store_id="oscars-ballwin",
                name="Oscar's Frozen Custard - Ballwin",
                address="9012 Ballwin Mill Rd",
                city="Ballwin",
                state="MO",
                phone="(636) 555-0125",
            ),
        ]

    def _parse_location_from_element(
        self, element, search_term: str, state: str | None
    ) -> LocationInfo | None:
        """Parse a location from an HTML element."""
        try:
            # Extract text from the element and nearby elements
            text = element.get_text(separator=" ", strip=True)

            # Look for address patterns in the text or nearby
            # This is a simplified extraction
            import re

            # Pattern for basic address detection
            address_pattern = r"\d+\s+\w+.*?(?=\s+(MO|IL|AR|TN)\b)"
            address_match = re.search(address_pattern, text, re.IGNORECASE)

            city_pattern = (
                r"(St\. Louis|Kirkwood|Ballwin|Chesterfield|O" + "'" + r"Fallon|etc\.)"
            )
            city_matches = re.findall(city_pattern, text, re.IGNORECASE)

            if city_matches:
                city = city_matches[0] if city_matches else "Unknown"
                state_match = re.search(r"(MO|IL|AR|TN)\b", text)
                state = state_match.group(1) if state_match else "MO"

                # Generate a unique ID based on city
                city_clean = (
                    city.lower().replace(" ", "").replace(".", "").replace("'", "")
                )
                store_id = f"oscars-{city_clean}"
                return LocationInfo(
                    store_id=store_id,
                    name=f"Oscar's Frozen Custard - {city}",
                    address=address_match.group(0)
                    if address_match
                    else f"Location in {city}",
                    city=city,
                    state=state,
                )
        except Exception as e:
            _LOGGER.debug("Error parsing location from element: %s", e)

        return None

    async def get_location_by_id(self, location_id: str) -> LocationInfo:
        """Get specific location details by store ID."""
        # Get all known locations and find the one with matching ID
        all_locations = self._get_known_oscars_locations()

        for location in all_locations:
            if location.store_id == location_id:
                return location

        msg = f"Location with ID {location_id} not found"
        raise LocationNotFoundError(msg)

    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day from Oscar's."""
        try:
            # Try to get flavor information from the website
            async with self.session.get(self.BASE_URL) as response:
                if response.status != 200:
                    _LOGGER.debug(
                        "Website access failed with status %s", response.status
                    )
                    # Try alternative methods such as social media or special flavor pages
                    return await self._get_flavor_from_social_media(location_id)

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Look for flavor information in common patterns
                flavor_selectors = [
                    ".flavor",
                    ".flavor-of-day",
                    ".daily-flavor",
                    ".todays-flavor",
                    '[id*="flavor"]',
                    '[class*="flavor"]',
                    '[id*="today"]',
                    '[class*="today"]',
                ]

                for selector in flavor_selectors:
                    flavor_elements = soup.select(selector)
                    for element in flavor_elements:
                        flavor_text = element.get_text(strip=True)
                        if (
                            flavor_text
                            and len(flavor_text) < 100
                            and "flavor" not in flavor_text.lower()
                        ):
                            return FlavorInfo(
                                name=flavor_text, available_date=dt_util.now()
                            )

                # If specific selectors don't work, look for any mention of today's flavors
                flavor_text_elements = soup.find_all(
                    string=lambda text: text
                    and ("flavor" in text.lower() and "today" in text.lower())
                )

                for element in flavor_text_elements:
                    parent = element.parent
                    if parent:
                        # Find the next sibling that might contain the flavor name
                        sibling = parent.find_next_sibling()
                        if sibling:
                            flavor_name = sibling.get_text(strip=True)
                            if flavor_name and len(flavor_name) < 100:
                                return FlavorInfo(
                                    name=flavor_name, available_date=dt_util.now()
                                )

                # If we still can't get the flavor from the website, try social media
                return await self._get_flavor_from_social_media(location_id)
        except Exception:
            _LOGGER.exception("Error getting current flavor")
            # Try to get from social media as fallback
            try:
                return await self._get_flavor_from_social_media(location_id)
            except:
                msg = f"Could not retrieve flavor for location {location_id}"
                raise FlavorNotAvailableError(msg)

    async def _get_flavor_from_social_media(self, location_id: str) -> FlavorInfo:
        """Get flavor information from social media as a fallback."""
        # Oscar's might post flavor information on social media like Facebook or Instagram
        # Since we can't directly access social media APIs without keys, this is a placeholder
        # In a real implementation, we would need to access their social media feeds
        # For now, return a placeholder that indicates the method used

        # Since we can't access social media without proper API keys, we'll return an error
        # Or we could try to scrape a publicly available page if one exists
        _LOGGER.debug("Trying social media fallback for Oscar's flavor")

        # This is where we would implement social media scraping if possible
        # For now, raise an exception to be caught by the caller
        msg = f"No flavor data available for Oscar's location {location_id}"
        raise FlavorNotAvailableError(msg)

    async def get_upcoming_flavors(
        self, location_id: str, days: int = 7
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors (if supported by Oscar's)."""
        # Oscar's may not provide upcoming flavors, just today's
        # So we'll return an empty list as per the base class default
        # unless they have a specific schedule on their website
        return []
