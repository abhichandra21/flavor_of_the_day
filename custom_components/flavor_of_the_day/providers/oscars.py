"""Oscar's Frozen Custard provider implementation."""

from __future__ import annotations

import logging
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


class OscarsProvider(BaseFlavorProvider):
    """Oscar's provider implementation."""

    BASE_URL = "https://www.oscarscustard.com"

    @property
    def provider_name(self) -> str:
        """Display name for this provider."""
        return "Oscar's Frozen Custard"

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        return "oscars"

    async def search_locations(
        self,
        search_term: str,
        state: str | None = None,  # noqa: ARG002
    ) -> list[LocationInfo]:
        """Return a list of all Oscar's locations, as they are fixed."""
        known_locations = [
            LocationInfo(
                store_id="oscars-west-allis",
                name="Oscar's Frozen Custard - West Allis",
                address="2362 S. 108th St.",
                city="Milwaukee",
                state="WI",
                zip_code="53227",
            ),
            LocationInfo(
                store_id="oscars-franklin",
                name="Oscar's Frozen Custard - Franklin",
                address="7041 South 27th St.",
                city="Franklin",
                state="WI",
                zip_code="53132",
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
        # Get all known locations and find the one with matching ID
        all_locations = await self.search_locations("")

        for location in all_locations:
            if location.store_id == location_id:
                return location

        msg = f"Location with ID {location_id} not found"
        raise LocationNotFoundError(msg)

    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day from Oscar's."""
        try:
            async with self.session.get(self.BASE_URL) as response:
                if response.status != 200:  # noqa: PLR2004
                    msg = f"Could not access Oscar's website for location {location_id}"
                    raise FlavorNotAvailableError(msg)  # noqa: TRY301

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # The flavor is in an h5 tag, like "Monday, September 29: RED RASPBERRY"
                flavor_text = None
                for h5 in soup.find_all("h5"):
                    text = h5.get_text(strip=True)
                    if ":" in text and any(
                        day in text.upper()
                        for day in [
                            "MONDAY",
                            "TUESDAY",
                            "WEDNESDAY",
                            "THURSDAY",
                            "FRIDAY",
                            "SATURDAY",
                            "SUNDAY",
                        ]
                    ):
                        flavor_text = text
                        break

                if not flavor_text:
                    msg = f"Could not find flavor of the day on Oscar's page for location {location_id}"  # noqa: E501
                    raise FlavorNotAvailableError(msg)  # noqa: TRY301

                # The text is like "SUNDAY, SEPTEMBER 28: CHOCOLATE COVERED CHERRY"
                # I need to extract the flavor name after the colon.
                parts = flavor_text.split(":")
                if len(parts) > 1:
                    flavor_name = parts[1].strip()
                    return FlavorInfo(
                        name=flavor_name,
                        available_date=dt_util.now(),
                    )

                msg = f"Could not extract flavor from Oscar's page for location {location_id}"  # noqa: E501
                raise FlavorNotAvailableError(msg)  # noqa: TRY301

        except Exception as e:
            _LOGGER.exception("Error getting current flavor from Oscar's")
            msg = f"Could not retrieve flavor for location {location_id}"
            raise FlavorNotAvailableError(msg) from e

    async def get_upcoming_flavors(
        self,
        location_id: str,  # noqa: ARG002, days:  # noqa: ARG002 int = 7
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors (if supported by Oscar's)."""
        # Oscar's may not provide upcoming flavors, just today's
        # So we'll return an empty list as per the base class default
        # unless they have a specific schedule on their website
        return []
