"""Constants for the Flavor of the Day integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

# Version for the integration
VERSION = "0.0.1"

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .data import FlavorOfTheDayData


DOMAIN = "flavor_of_the_day"

# Configuration keys
CONF_PROVIDER = "provider"
CONF_LOCATION_ID = "location_id"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_NAME = "name"

# Default values
DEFAULT_UPDATE_INTERVAL = 30  # minutes

# US States for location filtering
US_STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

# Attribution for data sources
ATTRIBUTION = "Data provided by store locations"

# Custom ConfigEntry type alias for type safety
if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .data import FlavorOfTheDayData

    class FlavorOfTheDayConfigEntry(ConfigEntry):
        """Config entry for the Flavor of the Day integration."""

        runtime_data: FlavorOfTheDayData
