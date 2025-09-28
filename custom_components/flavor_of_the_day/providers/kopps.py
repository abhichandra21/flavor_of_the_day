"""Kopp's provider for the Flavor of the Day integration."""

import logging
from datetime import date, datetime

import aiohttp
from bs4 import BeautifulSoup

from ..exceptions import FlavorNotAvailableError, LocationNotFoundError
from ..models import FlavorInfo, LocationInfo
from .base import BaseFlavorProvider

_LOGGER = logging.getLogger(__name__)


class KoppsProvider(BaseFlavorProvider):
    """Kopp's provider implementation."""

    BASE_URL = "https://www.kopps.com"

    @property
    def provider_name(self) -> str:
        return "Kopp's Frozen Custard"

    @property
    def provider_id(self) -> str:
        return "kopps"

    async def search_locations(
        self, search_term: str, state: str | None = None
    ) -> list[LocationInfo]:
        """Search for Kopp's locations by city, zip, or address."""
        try:
            # For Kopp's, we'll scrape the locations from their main page
            # since they have a limited number of locations

            async with self.session.get(f"{self.BASE_URL}/locations") as response:
                if response.status != 200:
                    _LOGGER.warning(
                        f"Locations page failed with status {response.status}"
                    )
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                locations = []

                # Find location blocks on the page
                location_blocks = soup.select(
                    '.location, .location-block, [id*="location"], [class*="location"]'
                )

                # If the above selectors don't work, look for address patterns
                if not location_blocks:
                    # Look for h3 elements or similar that might contain location names
                    h_elements = soup.find_all(["h2", "h3", "h4"])
                    for h_element in h_elements:
                        # Check if this heading contains location information
                        parent = h_element.find_parent()
                        if parent:
                            # Look for address information near the heading
                            # This is a simplified approach - in real implementation
                            # we'd need more specific selectors
                            location = self._parse_location_from_block(
                                parent, search_term, state
                            )
                            if location:
                                locations.append(location)

                # Alternative: look for address patterns directly
                if not locations:
                    locations = await self._extract_locations_from_main_page()

                # Filter based on search term if provided
                if search_term and locations:
                    filtered_locations = []
                    search_term_lower = search_term.lower()
                    for location in locations:
                        if (
                            search_term_lower in location.city.lower()
                            or search_term_lower in location.address.lower()
                            or (
                                location.zip_code
                                and search_term_lower in location.zip_code.lower()
                            )
                        ):
                            filtered_locations.append(location)
                    locations = filtered_locations

                return locations
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error during location search: {e}")
            return []
        except Exception as e:
            _LOGGER.error(f"Error during location search: {e}")
            return []

    async def _extract_locations_from_main_page(self) -> list[LocationInfo]:
        """Extract locations from the main page."""
        try:
            async with self.session.get(self.BASE_URL) as response:
                if response.status != 200:
                    return []

                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")

                locations = []

                # Look for location patterns in the HTML
                # This is based on the structure seen in the website analysis
                # Look for elements that might contain location information

                # Find address patterns
                address_elements = soup.find_all(
                    string=lambda text: text
                    and any(
                        addr_word in text.lower()
                        for addr_word in [
                            "street",
                            "ave",
                            "avenue",
                            "road",
                            "rd",
                            "drive",
                            "dr",
                            "lane",
                            "ln",
                            "blvd",
                            "boulevard",
                        ]
                    )
                )

                # Look for phone numbers that might be associated with locations
                import re

                phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
                phone_elements = soup.find_all(
                    string=lambda text: text and re.search(phone_pattern, text)
                )

                # Look for location headers (h2, h3, etc.) that might contain city names
                location_headers = soup.find_all(
                    ["h2", "h3"],
                    string=lambda text: text
                    and any(
                        city in text.lower()
                        for city in [
                            "greenfield",
                            "brookfield",
                            "glendale",
                            "milwaukee",
                        ]
                    ),
                )

                # Extract locations based on patterns found
                for header in location_headers:
                    location = self._parse_location_from_header(header)
                    if location:
                        locations.append(location)

                return locations
        except Exception as e:
            _LOGGER.error(f"Error extracting locations from main page: {e}")
            return []

    def _parse_location_from_header(self, header_element) -> LocationInfo | None:
        """Parse location from a header element."""
        try:
            # Try to find the full location block associated with this header
            location_block = header_element.find_parent()
            if not location_block:
                return None

            # Look for address, phone number, and hours in the nearby elements
            city = header_element.get_text(strip=True).lower()
            if "greenfield" in city:
                city = "Greenfield"
                state = "WI"
                store_id = "kopps-greenfield"
                address = "4200 W. Greenfield Ave."
            elif "brookfield" in city:
                city = "Brookfield"
                state = "WI"
                store_id = "kopps-brookfield"
                address = "18800 W. Bluemound Rd."
            elif "glendale" in city:
                city = "Glendale"
                state = "WI"
                store_id = "kopps-glendale"
                address = "6263 N. Downer Ave."
            else:
                return None

            # Look for phone number in the block
            phone_element = location_block.find(
                string=lambda text: text and "phone" in text.lower()
            )
            phone = ""
            if phone_element:
                import re

                phone_match = re.search(
                    r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", phone_element
                )
                if phone_match:
                    phone = phone_match.group()

            location = LocationInfo(
                store_id=store_id,
                name=f"Kopp's Frozen Custard - {city}",
                address=address,
                city=city,
                state=state,
                phone=phone,
            )
            return location
        except Exception as e:
            _LOGGER.error(f"Error parsing location from header: {e}")
            return None

    def _parse_location_from_block(
        self, block_element, search_term: str, state: str | None
    ) -> LocationInfo | None:
        """Parse location from a block element."""
        # Implementation would depend on the specific HTML structure
        # This is a simplified version that creates location objects based on known Kopp's locations
        # In a real implementation, we'd need more specific selectors based on the actual HTML structure

        # Since Kopp's has specific known locations in Milwaukee area, we'll create them
        # if the search matches the area
        if state and state.upper() != "WI":
            return None

        # Check if search term matches known locations
        search_lower = search_term.lower()
        if "greenfield" in search_lower:
            return LocationInfo(
                store_id="kopps-greenfield",
                name="Kopp's Frozen Custard - Greenfield",
                address="4200 W. Greenfield Ave.",
                city="Greenfield",
                state="WI",
                phone="(414) 281-2700",
            )
        if "brookfield" in search_lower:
            return LocationInfo(
                store_id="kopps-brookfield",
                name="Kopp's Frozen Custard - Brookfield",
                address="18800 W. Bluemound Rd.",
                city="Brookfield",
                state="WI",
                phone="(262) 792-2800",
            )
        if "glendale" in search_lower:
            return LocationInfo(
                store_id="kopps-glendale",
                name="Kopp's Frozen Custard - Glendale",
                address="6263 N. Downer Ave.",
                city="Glendale",
                state="WI",
                phone="(414) 354-9800",
            )

        return None

    async def get_location_by_id(self, location_id: str) -> LocationInfo:
        """Get specific location details by store ID."""
        # Define known Kopp's locations
        known_locations = {
            "kopps-greenfield": LocationInfo(
                store_id="kopps-greenfield",
                name="Kopp's Frozen Custard - Greenfield",
                address="4200 W. Greenfield Ave.",
                city="Greenfield",
                state="WI",
                phone="(414) 281-2700",
                hours={
                    "monday": "10:30am-10pm",
                    "tuesday": "10:30am-10pm",
                    "wednesday": "10:30am-10pm",
                    "thursday": "10:30am-10pm",
                    "friday": "10:30am-11pm",
                    "saturday": "10:30am-11pm",
                    "sunday": "10:30am-10pm",
                },
            ),
            "kopps-brookfield": LocationInfo(
                store_id="kopps-brookfield",
                name="Kopp's Frozen Custard - Brookfield",
                address="18800 W. Bluemound Rd.",
                city="Brookfield",
                state="WI",
                phone="(262) 792-2800",
                hours={
                    "monday": "10:30am-10pm",
                    "tuesday": "10:30am-10pm",
                    "wednesday": "10:30am-10pm",
                    "thursday": "10:30am-10pm",
                    "friday": "10:30am-11pm",
                    "saturday": "10:30am-11pm",
                    "sunday": "10:30am-10pm",
                },
            ),
            "kopps-glendale": LocationInfo(
                store_id="kopps-glendale",
                name="Kopp's Frozen Custard - Glendale",
                address="6263 N. Downer Ave.",
                city="Glendale",
                state="WI",
                phone="(414) 354-9800",
                hours={
                    "monday": "10:30am-10pm",
                    "tuesday": "10:30am-10pm",
                    "wednesday": "10:30am-10pm",
                    "thursday": "10:30am-10pm",
                    "friday": "10:30am-11pm",
                    "saturday": "10:30am-11pm",
                    "sunday": "10:30am-10pm",
                },
            ),
        }

        if location_id in known_locations:
            return known_locations[location_id]
        raise LocationNotFoundError(f"Location with ID {location_id} not found")

    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day from Kopp's."""
        try:
            # Kopp's shows today's flavors on their main page
            async with self.session.get(self.BASE_URL) as response:
                if response.status != 200:
                    raise FlavorNotAvailableError(
                        f"Could not access Kopp's website for location {location_id}"
                    )

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Find the flavor section - Kopp's typically shows TODAY'S FLAVORS with date
                today_flavors_section = None
                for header in soup.find_all(["h1", "h2", "h3"]):
                    header_text = header.get_text(strip=True).upper()
                    if "TODAY'S FLAVORS" in header_text or (
                        "FLAVOR" in header_text and "TODAY" in header_text
                    ):
                        today_flavors_section = header.parent
                        break

                if not today_flavors_section:
                    # Look for alternative sections that might contain flavors
                    for div in soup.find_all("div"):
                        div_text = div.get_text(strip=True).upper()
                        if "FLAVOR" in div_text and any(
                            day in div_text
                            for day in [
                                "TODAY",
                                "MONDAY",
                                "TUESDAY",
                                "WEDNESDAY",
                                "THURSDAY",
                                "FRIDAY",
                                "SATURDAY",
                                "SUNDAY",
                            ]
                        ):
                            today_flavors_section = div
                            break

                # Extract flavor information from the section
                if today_flavors_section:
                    flavor_info = self._extract_flavors_from_section(
                        today_flavors_section
                    )
                    if flavor_info:
                        return flavor_info

                # If we couldn't find flavors in the specific section, look for any flavor-like elements
                flavor_elements = soup.find_all(
                    string=lambda text: text and "flavor" in text.lower()
                )
                for element in flavor_elements:
                    parent = element.parent
                    if parent:
                        # Look for the next sibling or nearby elements that might contain the flavor names
                        flavor_text = parent.get_text(strip=True)
                        if (
                            len(flavor_text) < 100
                            and "flavor" not in flavor_text.lower()
                        ):
                            return FlavorInfo(
                                name=flavor_text, available_date=datetime.now()
                            )

                raise FlavorNotAvailableError(
                    f"No flavor data available for location {location_id}"
                )
        except Exception as e:
            _LOGGER.error(f"Error getting current flavor: {e}")
            raise FlavorNotAvailableError(
                f"Could not retrieve flavor for location {location_id}"
            )

    def _extract_flavors_from_section(self, section) -> FlavorInfo | None:
        """Extract flavor information from a specific section."""
        try:
            # Look for flavor names in the section
            # Kopp's typically lists flavors in various formats:
            # - Bold text
            # - Text with descriptions
            # - Specific classes related to flavors

            # Find text that looks like a flavor name (usually capitalized)
            flavor_elements = section.find_all(["h3", "h4", "strong", "b"], string=True)

            for element in flavor_elements:
                flavor_text = element.get_text(strip=True)
                # Filter for likely flavor names (not too long, contains proper nouns/capitalized words)
                if (
                    len(flavor_text) > 2
                    and len(flavor_text) < 50
                    and not flavor_text.startswith("TODAY")
                ):
                    # Check if this looks like a flavor by checking if it has mostly capitalized words
                    words = flavor_text.split()
                    if len(words) > 0 and any(
                        word[0].isupper() for word in words if len(word) > 2
                    ):
                        return FlavorInfo(
                            name=flavor_text, available_date=datetime.now()
                        )

            # If the above didn't work, look for any text elements that might contain flavors
            all_text_elements = section.find_all(string=True)
            for text_element in all_text_elements:
                text = text_element.strip()
                if (
                    len(text) > 2
                    and len(text) < 50
                    and text.upper() != text  # Not all caps (which might be headers)
                    and "FLAVOR" not in text.upper()
                    and "TODAY" not in text.upper()
                ):
                    words = text.split()
                    if len(words) > 0 and any(
                        word[0].isupper() for word in words if len(word) > 2
                    ):
                        return FlavorInfo(name=text, available_date=datetime.now())

            return None
        except Exception as e:
            _LOGGER.error(f"Error extracting flavors from section: {e}")
            return None

    async def get_upcoming_flavors(
        self, location_id: str, days: int = 7
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors from Kopp's flavor preview."""
        try:
            # Kopp's has a "Flavor Preview" section
            async with self.session.get(f"{self.BASE_URL}/flavor-preview") as response:
                if response.status != 200:
                    _LOGGER.debug("Flavor preview page not accessible")
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                upcoming_flavors = []

                # Look for upcoming flavor information
                # This would require more specific selectors based on actual HTML structure
                # which may vary over time

                # Look for date/flavor pairings in the preview section
                date_flavor_pairs = soup.find_all(
                    ["div", "section"], class_=lambda x: x and "flavor" in x.lower()
                )

                for pair in date_flavor_pairs:
                    # This is a simplified extraction - in practice would need specific selectors
                    date_elem = pair.find(["h4", "strong"], string=True)
                    flavor_elem = pair.find(["p", "span"], string=True)

                    if date_elem and flavor_elem:
                        # Parse date and flavor
                        # This would need proper date parsing in real implementation
                        flavor_info = FlavorInfo(
                            name=flavor_elem.get_text(strip=True),
                            available_date=datetime.now(),  # Simplified
                        )
                        # Add to results (date would need to be properly parsed)

                return upcoming_flavors
        except Exception as e:
            _LOGGER.debug(f"Error getting upcoming flavors: {e}")
            return []
