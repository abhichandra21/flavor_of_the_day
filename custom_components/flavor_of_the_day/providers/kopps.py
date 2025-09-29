"""Kopp's Frozen Custard provider implementation."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

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


class KoppsProvider(BaseFlavorProvider):
    """Kopp's provider implementation."""

    BASE_URL = "https://www.kopps.com"

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "Kopp's Frozen Custard"

    @property
    def provider_id(self) -> str:
        """Return the provider ID."""
        return "kopps"

    async def search_locations(
        self,
        search_term: str,
        state: str | None = None,  # noqa: ARG002
    ) -> list[LocationInfo]:
        """Return a list of all Kopp's locations, as they are fixed."""
        known_locations = [
            LocationInfo(
                store_id="kopps-greenfield",
                name="Kopp's Frozen Custard - Greenfield",
                address="7631 W. Layton Ave.",
                city="Greenfield",
                state="WI",
                zip_code="53220",
            ),
            LocationInfo(
                store_id="kopps-brookfield",
                name="Kopp's Frozen Custard - Brookfield",
                address="18880 W. Bluemound Rd.",
                city="Brookfield",
                state="WI",
                zip_code="53045",
            ),
            LocationInfo(
                store_id="kopps-glendale",
                name="Kopp's Frozen Custard - Glendale",
                address="5373 N. Port Washington Rd.",
                city="Glendale",
                state="WI",
                zip_code="53217",
            ),
        ]

        if not search_term:
            return known_locations

        search_lower = search_term.lower()
        return [
            loc
            for loc in known_locations
            if search_lower in loc.name.lower()
            or search_lower in loc.city.lower()
            or search_lower in loc.address.lower()
        ]

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
        msg = f"Location with ID {location_id} not found"
        raise LocationNotFoundError(msg)

    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day from Kopp's."""
        try:
            async with self.session.get(f"{self.BASE_URL}/flavor-preview") as response:
                if response.status != 200:  # noqa: PLR2004
                    msg = f"Could not access Kopp's flavor preview page for location {location_id}"  # noqa: E501
                    raise FlavorNotAvailableError(msg)  # noqa: TRY301

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Get today's day number
                today = dt_util.now().day

                # Find the div for today's flavors
                today_div = soup.find("div", id=str(today))

                if not today_div:
                    msg = f"Could not find today's flavor div on Kopp's flavor preview page for location {location_id}"  # noqa: E501
                    raise FlavorNotAvailableError(msg)  # noqa: TRY301

                # Find all flavor names within the div
                flavors = [
                    h3.get_text(strip=True)
                    for h3 in today_div.find_all(
                        "h3", class_="h5 fw-black text-uppercase mb-0"
                    )
                ]

                if not flavors:
                    msg = f"Could not extract flavors from Kopp's flavor preview page for location {location_id}"  # noqa: E501
                    raise FlavorNotAvailableError(msg)  # noqa: TRY301

                return FlavorInfo(
                    name=" & ".join(flavors),
                    available_date=dt_util.now(),
                )

        except Exception as e:
            _LOGGER.exception("Error getting current flavor from Kopp's")
            msg = f"Could not retrieve flavor for location {location_id}"
            raise FlavorNotAvailableError(msg) from e

    async def get_upcoming_flavors(
        self,
        location_id: str,  # noqa: ARG002, days:  # noqa: ARG002 int = 7
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors from Kopp's flavor preview."""
        try:
            async with self.session.get(f"{self.BASE_URL}/flavor-preview") as response:
                if response.status != 200:  # noqa: PLR2004
                    _LOGGER.debug("Flavor preview page not accessible")
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                upcoming_flavors = []

                # Find the "TOMORROW" section
                tomorrow_flavors_section = None
                for header in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                    if "TOMORROW" in header.get_text(strip=True).upper():
                        tomorrow_flavors_section = header
                        break

                if not tomorrow_flavors_section:
                    return []

                # Find the flavors within the section
                flavors = []
                for sibling in tomorrow_flavors_section.find_next_siblings("p"):
                    flavor_name_tag = sibling.find("strong")
                    if flavor_name_tag:
                        flavors.append(flavor_name_tag.get_text(strip=True))
                    else:
                        break

                if flavors:
                    tomorrow = dt_util.now().date() + timedelta(days=1)
                    upcoming_flavors.append(
                        (
                            tomorrow,
                            FlavorInfo(
                                name=" & ".join(flavors),
                                available_date=dt_util.as_utc(
                                    dt_util.parse_datetime(f"{tomorrow} 00:00:00")
                                ),
                            ),
                        )
                    )

                return upcoming_flavors
        except Exception as e:  # noqa: BLE001
            _LOGGER.debug("Error getting upcoming flavors: %s", e)
            return []
