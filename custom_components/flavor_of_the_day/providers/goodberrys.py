"""Goodberry's provider implementation."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup
from homeassistant.util import dt as dt_util

from custom_components.flavor_of_the_day.exceptions import (
    FlavorNotAvailableError,
    LocationNotFoundError,
)
from custom_components.flavor_of_the_day.models import FlavorInfo, LocationInfo
from custom_components.flavor_of_the_day.providers.base import BaseFlavorProvider

_LOGGER = logging.getLogger(__name__)


class GoodberrysProvider(BaseFlavorProvider):
    """Goodberry's provider implementation."""

    BASE_URL = "https://goodberrys.com"

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "Goodberry's Frozen Custard"

    @property
    def provider_id(self) -> str:
        """Return the provider ID."""
        return "goodberrys"

    async def search_locations(
        self,
        search_term: str,
        state: str | None = None,  # noqa: ARG002
    ) -> list[LocationInfo]:
        """Return a list of all Goodberry's locations, as they are fixed."""
        known_locations = [
            LocationInfo(
                store_id="goodberrys-southern-pines",
                name="Goodberry's - Southern Pines",
                address="231 Carolina Green Pkwy",
                city="Southern Pines",
                state="NC",
            ),
            LocationInfo(
                store_id="goodberrys-raleigh-spring-forest",
                name="Goodberry's - Raleigh (Spring Forest)",
                address="2421 Spring Forest Rd.",
                city="Raleigh",
                state="NC",
            ),
            LocationInfo(
                store_id="goodberrys-raleigh-strickland",
                name="Goodberry's - Raleigh (Strickland Rd)",
                address="9700 Strickland Rd.",
                city="Raleigh",
                state="NC",
            ),
            LocationInfo(
                store_id="goodberrys-raleigh-clark-ave",
                name="Goodberry's - Raleigh (Clark Ave)",
                address="2042 Clark Ave.",
                city="Raleigh",
                state="NC",
            ),
            LocationInfo(
                store_id="goodberrys-cary-kildaire-farm",
                name="Goodberry's - Cary (Kildaire Farm Rd)",
                address="1146 Kildaire Farm Rd.",
                city="Cary",
                state="NC",
            ),
            LocationInfo(
                store_id="goodberrys-cary-davis-dr",
                name="Goodberry's - Cary (Davis Dr)",
                address="2325 Davis Dr.",
                city="Cary",
                state="NC",
            ),
            LocationInfo(
                store_id="goodberrys-garner",
                name="Goodberry's - Garner",
                address="1407 Garner Station Blvd.",
                city="Garner",
                state="NC",
            ),
            LocationInfo(
                store_id="goodberrys-wake-forest",
                name="Goodberry's - Wake Forest",
                address="11736 Retail Dr.",
                city="Wake Forest",
                state="NC",
            ),
            LocationInfo(
                store_id="goodberrys-durham",
                name="Goodberry's - Durham",
                address="3906 N. Roxboro St.",
                city="Durham",
                state="NC",
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
        all_locations = await self.search_locations("")
        for location in all_locations:
            if location.store_id == location_id:
                return location
        msg = f"Location with ID {location_id} not found"
        raise LocationNotFoundError(msg)

    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day from Goodberry's."""
        try:
            async with self.session.get(self.BASE_URL) as response:
                if response.status != 200:  # noqa: PLR2004
                    msg = f"Could not access Goodberry's website for location {location_id}"  # noqa: E501
                    raise FlavorNotAvailableError(msg)  # noqa: TRY301

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Find the flavor of the day
                # The flavor is in a div with a class that contains "flavor-of-the-day"
                fotd_element = soup.select_one("[class*='flavor-of-the-day']")
                if fotd_element:
                    # The flavor name is usually in a strong or h tag
                    flavor_name_tag = fotd_element.find(
                        ["h1", "h2", "h3", "h4", "h5", "h6", "strong"]
                    )
                    if flavor_name_tag:
                        flavor_name = flavor_name_tag.get_text(strip=True)
                        return FlavorInfo(
                            name=flavor_name,
                            available_date=dt_util.now(),
                        )

                msg = f"Could not extract flavor from Goodberry's page for location {location_id}"  # noqa: E501
                raise FlavorNotAvailableError(msg)  # noqa: TRY301

        except Exception as e:
            _LOGGER.exception("Error getting current flavor from Goodberry's")
            msg = f"Could not retrieve flavor for location {location_id}"
            raise FlavorNotAvailableError(msg) from e
