"""Leduc's provider for the Flavor of the Day integration."""

import logging
from datetime import date, datetime

from bs4 import BeautifulSoup

from ..exceptions import FlavorNotAvailableError, LocationNotFoundError
from ..models import FlavorInfo, LocationInfo
from .base import BaseFlavorProvider

_LOGGER = logging.getLogger(__name__)


class LeducsProvider(BaseFlavorProvider):
    """Leduc's provider implementation."""

    BASE_URL = "https://www.leducscustard.com"

    @property
    def provider_name(self) -> str:
        return "Leduc's Frozen Custard"

    @property
    def provider_id(self) -> str:
        return "leducs"

    async def search_locations(
        self, search_term: str, state: str | None = None
    ) -> list[LocationInfo]:
        """Search for Leduc's locations by city, zip, or address."""
        try:
            # Leduc's has only one location in Wales, WI
            # Based on the website analysis, they operate only one store
            location = await self.get_location_by_id("leducs-wales")

            # Filter based on search term if provided
            if search_term:
                search_term_lower = search_term.lower()
                if (
                    search_term_lower in location.city.lower()
                    or search_term_lower in location.address.lower()
                    or (state and state.upper() == location.state.upper())
                ):
                    return [location]
                return []  # No match based on search criteria
            return [location]
        except Exception as e:
            _LOGGER.error(f"Error during location search: {e}")
            return []

    async def get_location_by_id(self, location_id: str) -> LocationInfo:
        """Get specific location details by store ID."""
        # Leduc's has only one location
        if location_id == "leducs-wales":
            return LocationInfo(
                store_id="leducs-wales",
                name="Leduc's Frozen Custard",
                address="240 W. Summit Ave.",
                city="Wales",
                state="WI",
                zip_code="53183",
                phone="(262) 968-2894",
                hours={
                    "monday": "11:00AM-9:00PM",
                    "tuesday": "11:00AM-9:00PM",
                    "wednesday": "11:00AM-9:00PM",
                    "thursday": "11:00AM-9:00PM",
                    "friday": "11:00AM-9:00PM",
                    "saturday": "11:00AM-9:00PM",
                    "sunday": "11:00AM-9:00PM",
                },
                website_url=self.BASE_URL,
            )
        raise LocationNotFoundError(f"Location with ID {location_id} not found")

    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day from Leduc's."""
        try:
            # Get the main page to find today's flavor
            async with self.session.get(self.BASE_URL) as response:
                if response.status != 200:
                    raise FlavorNotAvailableError(
                        f"Could not access Leduc's website for location {location_id}"
                    )

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Look for the flavor calendar section which contains today's flavor
                # Based on the analysis, flavors are displayed in a calendar format
                flavor_calendar = soup.find(
                    string=lambda text: text and "Flavor Calendar" in text
                )
                if flavor_calendar:
                    parent = flavor_calendar.parent if flavor_calendar.parent else soup
                else:
                    parent = soup  # If not found, search in the whole document

                # Look for today's date and the corresponding flavor
                today = datetime.now()
                date_str = today.strftime("%b %d").replace(
                    " 0", " "
                )  # Format: "Sep 27"

                # Find elements that contain the date
                date_elements = parent.find_all(
                    string=lambda text: text and date_str in text if text else False
                )

                if date_elements:
                    for date_elem in date_elements:
                        # The flavor name is usually next to or near the date
                        # Look in the parent element that contains the date
                        container = date_elem.parent
                        if container:
                            # Find all text elements in this container
                            text_elements = container.get_text(
                                separator="|", strip=True
                            ).split("|")

                            # Look for flavor-like text (not the date)
                            for text in text_elements:
                                text = text.strip()
                                if (
                                    text
                                    and date_str not in text
                                    and len(text) > 2
                                    and len(text) < 50
                                ):
                                    # This looks like a flavor name
                                    return FlavorInfo(name=text, available_date=today)

                # If the above method doesn't work, try looking for common flavor selectors
                flavor_selectors = [
                    ".flavor-of-day",
                    ".todays-flavor",
                    ".current-flavor",
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
                            return FlavorInfo(name=flavor_text, available_date=today)

                # If we still haven't found a flavor, try a more general approach
                # Look for common flavor-related text on the page
                flavor_keywords = ["flavor", "today", "day"]
                for keyword in flavor_keywords:
                    elements = soup.find_all(
                        string=lambda text: text and keyword in text.lower()
                    )
                    for element in elements:
                        parent = element.parent
                        if parent:
                            # Look for text that might be the flavor name
                            next_sibling = parent.find_next_sibling()
                            if next_sibling:
                                flavor_text = next_sibling.get_text(strip=True)
                                if (
                                    flavor_text
                                    and len(flavor_text) < 100
                                    and "flavor" not in flavor_text.lower()
                                ):
                                    return FlavorInfo(
                                        name=flavor_text, available_date=today
                                    )

                raise FlavorNotAvailableError(
                    f"No flavor data available for location {location_id}"
                )
        except Exception as e:
            _LOGGER.error(f"Error getting current flavor: {e}")
            raise FlavorNotAvailableError(
                f"Could not retrieve flavor for location {location_id}"
            )

    async def get_upcoming_flavors(
        self, location_id: str, days: int = 7
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors from Leduc's flavor calendar."""
        try:
            async with self.session.get(f"{self.BASE_URL}/flavor-calendar") as response:
                if response.status != 200:
                    _LOGGER.debug(
                        f"Flavor calendar page not accessible: {response.status}"
                    )
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                upcoming_flavors = []

                # Based on the website analysis, look for dates and corresponding flavors
                # The HTML structure likely has date-flavor pairs
                date_flavor_pairs = soup.find_all(
                    ["div", "section", "li"],
                    class_=lambda x: x
                    and any(
                        keyword in x.lower()
                        for keyword in ["calendar", "flavor", "day"]
                    ),
                )

                today = datetime.now().date()

                for pair in date_flavor_pairs:
                    # Look for date and flavor in the element
                    date_elem = pair.find(["span", "div", "p"], string=True)
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        # Try to parse the date
                        try:
                            # This is a simplified approach - would need more robust date parsing
                            # Based on the format seen: "Sep 27: Cookies & Cream"
                            import re

                            date_match = re.search(
                                r"([A-Z][a-z]{2})\s+(\d{1,2})", date_text
                            )
                            if date_match:
                                month_name, day_num = date_match.groups()
                                # Convert month name to number - simplified approach
                                month_map = {
                                    "Jan": 1,
                                    "Feb": 2,
                                    "Mar": 3,
                                    "Apr": 4,
                                    "May": 5,
                                    "Jun": 6,
                                    "Jul": 7,
                                    "Aug": 8,
                                    "Sep": 9,
                                    "Oct": 10,
                                    "Nov": 11,
                                    "Dec": 12,
                                }

                                month = month_map.get(month_name, today.month)
                                day = int(day_num)
                                year = today.year

                                # Handle year change
                                if month < today.month or (
                                    month == today.month and day < today.day
                                ):
                                    year += 1

                                flavor_date = date(year, month, day)

                                # Extract flavor name (after the date)
                                flavor_match = re.split(r":\s*", date_text, maxsplit=1)
                                if len(flavor_match) > 1:
                                    flavor_name = flavor_match[1].strip()
                                    if (
                                        flavor_date >= today
                                        and len(upcoming_flavors) < days
                                    ):
                                        flavor_info = FlavorInfo(
                                            name=flavor_name, available_date=flavor_date
                                        )
                                        upcoming_flavors.append(
                                            (flavor_date, flavor_info)
                                        )
                        except Exception as e:
                            _LOGGER.debug(
                                f"Error parsing date from: {date_text}, error: {e}"
                            )
                            continue

                return upcoming_flavors
        except Exception as e:
            _LOGGER.debug(f"Error getting upcoming flavors: {e}")
            return []
