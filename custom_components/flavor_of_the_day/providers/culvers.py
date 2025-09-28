"""Culver's provider for the Flavor of the Day integration."""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from ..exceptions import FlavorNotAvailableError, LocationNotFoundError
from ..models import FlavorInfo, LocationInfo
from .base import BaseFlavorProvider

_LOGGER = logging.getLogger(__name__)


class CulversProvider(BaseFlavorProvider):
    """Culver's provider implementation."""

    BASE_URL = "https://www.culvers.com"
    API_BASE = "https://hosted.where2getit.com/culvers"

    @property
    def provider_name(self) -> str:
        return "Culver's"

    @property
    def provider_id(self) -> str:
        return "culvers"

    async def search_locations(
        self, search_term: str, state: Optional[str] = None
    ) -> List[LocationInfo]:
        """Search for Culver's locations by city, zip, or address."""
        try:
            _LOGGER.debug(
                f"Searching Culver's locations for: {search_term}, state: {state}"
            )

            # Use the proven approach from ha-culversfotd: parse restaurant directory
            # First, try to get the restaurant directory page
            restaurants_url = "https://www.culvers.com/locator"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with self.session.get(restaurants_url, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.warning(f"Failed to fetch locator page: {response.status}")
                    return []

                html = await response.text()
                _LOGGER.debug(f"Got locator page, length: {len(html)}")

                # Extract restaurant slugs and location data from the page
                locations = await self._extract_locations_from_locator(
                    html, search_term, state
                )
                _LOGGER.debug(f"Found {len(locations)} matching locations")

                return locations

        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error during location search: {e}")
            return []
        except Exception as e:
            _LOGGER.error(f"Error during location search: {e}")
            return []

    async def _extract_locations_from_locator(
        self, html: str, search_term: str, state: Optional[str]
    ) -> List[LocationInfo]:
        """Extract location data from Culver's locator page."""
        try:
            import json

            from bs4 import BeautifulSoup

            locations = []
            soup = BeautifulSoup(html, "html.parser")

            # Look for the __NEXT_DATA__ script tag (following ha-culversfotd approach)
            script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
            if script_tag:
                try:
                    json_data = json.loads(script_tag.string)
                    _LOGGER.debug("Found __NEXT_DATA__ script tag")

                    # Navigate the JSON structure to find restaurant/location data
                    locations = await self._extract_restaurants_from_next_data(
                        json_data, search_term, state
                    )

                except (json.JSONDecodeError, KeyError) as e:
                    _LOGGER.debug(f"Error parsing __NEXT_DATA__: {e}")

            # If no locations found, try alternative approaches
            if not locations:
                _LOGGER.debug(
                    "No locations from __NEXT_DATA__, trying alternative extraction"
                )
                locations = self._extract_locations_fallback(soup, search_term, state)

            return locations

        except Exception as e:
            _LOGGER.error(f"Error extracting locations from locator: {e}")
            return []

    async def _extract_restaurants_from_next_data(
        self, json_data: dict, search_term: str, state: Optional[str]
    ) -> List[LocationInfo]:
        """Extract restaurant locations from __NEXT_DATA__ structure."""
        try:
            locations = []

            # Navigate through the Next.js data structure to find restaurant information
            # Look for common paths where restaurant data might be stored
            paths_to_check = [
                ["props", "pageProps", "restaurants"],
                ["props", "pageProps", "locations"],
                ["props", "pageProps", "data", "restaurants"],
                ["props", "pageProps", "page", "restaurants"],
                ["props", "initialProps", "restaurants"],
                ["query", "restaurants"],
            ]

            for path in paths_to_check:
                try:
                    current = json_data
                    for key in path:
                        current = current[key]

                    if isinstance(current, list):
                        _LOGGER.debug(
                            f"Found restaurant list at path {'.'.join(path)} with {len(current)} items"
                        )
                        for restaurant_data in current:
                            location = self._create_location_from_restaurant_data(
                                restaurant_data
                            )
                            if location:
                                locations.append(location)
                        break

                except (KeyError, TypeError):
                    continue

            # If no direct restaurant list found, search recursively
            if not locations:
                _LOGGER.debug("No direct restaurant list found, searching recursively")
                locations = self._find_restaurants_recursive(json_data)

            # Filter locations based on search criteria
            if locations:
                filtered = self._filter_locations(locations, search_term, state)
                _LOGGER.debug(
                    f"Filtered {len(locations)} total locations to {len(filtered)} matching locations"
                )
                return filtered

            return locations

        except Exception as e:
            _LOGGER.error(f"Error extracting restaurants from __NEXT_DATA__: {e}")
            return []

    def _create_location_from_restaurant_data(
        self, data: dict
    ) -> Optional[LocationInfo]:
        """Create LocationInfo from restaurant data structure."""
        try:
            # Extract fields with common naming patterns
            name = (
                data.get("name") or data.get("title") or data.get("restaurant_name", "")
            )

            # Handle address - could be a string or object
            address_data = data.get("address", {})
            if isinstance(address_data, str):
                address = address_data
                city = data.get("city", "")
                state = data.get("state", "")
                zip_code = data.get("zip", data.get("zipcode", ""))
            else:
                address = address_data.get("street", "") or address_data.get(
                    "address1", ""
                )
                city = address_data.get("city", "") or data.get("city", "")
                state = address_data.get("state", "") or data.get("state", "")
                zip_code = (
                    address_data.get("zip", "")
                    or address_data.get("zipcode", "")
                    or data.get("zip", "")
                )

            # Extract location coordinates
            lat = (
                data.get("latitude")
                or data.get("lat")
                or (data.get("location", {}).get("lat"))
            )
            lng = (
                data.get("longitude")
                or data.get("lng")
                or (data.get("location", {}).get("lng"))
            )

            try:
                latitude = float(lat) if lat else None
                longitude = float(lng) if lng else None
            except (ValueError, TypeError):
                latitude = longitude = None

            # Generate store ID from slug or use provided ID
            store_id = (
                data.get("id") or data.get("slug") or data.get("restaurant_id", "")
            )
            if not store_id and name and city:
                # Generate slug-like ID if none provided
                store_id = (
                    f"{name.lower().replace(' ', '-')}-{city.lower().replace(' ', '-')}"
                )

            # Must have at least name and city to be valid
            if not (name and city):
                return None

            phone = data.get("phone") or data.get("phoneNumber", "")
            hours = data.get("hours", {})

            return LocationInfo(
                store_id=str(store_id),
                name=name,
                address=address,
                city=city,
                state=state,
                zip_code=str(zip_code) if zip_code else "",
                phone=phone,
                hours=hours if isinstance(hours, dict) else {},
                website_url=f"https://www.culvers.com/restaurants/{store_id}"
                if store_id
                else "",
                latitude=latitude,
                longitude=longitude,
            )

        except Exception as e:
            _LOGGER.debug(f"Error creating location from restaurant data: {e}")
            return None

    def _find_restaurants_recursive(self, data, path="root") -> List[LocationInfo]:
        """Recursively search for restaurant data in the JSON structure."""
        locations = []

        if isinstance(data, dict):
            # Check if this object looks like a restaurant
            if self._looks_like_restaurant(data):
                location = self._create_location_from_restaurant_data(data)
                if location:
                    locations.append(location)

            # Search in nested objects
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    nested_locations = self._find_restaurants_recursive(
                        value, f"{path}.{key}"
                    )
                    locations.extend(nested_locations)

        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    nested_locations = self._find_restaurants_recursive(
                        item, f"{path}[{i}]"
                    )
                    locations.extend(nested_locations)

        return locations

    def _looks_like_restaurant(self, data: dict) -> bool:
        """Check if a dictionary looks like restaurant data."""
        restaurant_indicators = [
            "name",
            "address",
            "city",
            "state",
            "restaurant",
            "location",
        ]
        return sum(1 for indicator in restaurant_indicators if indicator in data) >= 3

    def _extract_locations_fallback(
        self, soup, search_term: str, state: Optional[str]
    ) -> List[LocationInfo]:
        """Fallback method to extract locations from HTML."""
        # This can be implemented to parse HTML directly if JSON approach fails
        return []

    def _extract_locations_from_json(self, data) -> List[LocationInfo]:
        """Extract locations from JSON data structure."""
        locations = []

        def find_locations(obj, path=""):
            if isinstance(obj, dict):
                # Check if this looks like a location object
                if self._is_location_object(obj):
                    _LOGGER.debug(f"Found potential location object at {path}")
                    location = self._create_location_from_dict(obj)
                    if location:
                        _LOGGER.debug(
                            f"Created location: {location.name} in {location.city}"
                        )
                        locations.append(location)

                # Recursively search in nested objects
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        find_locations(value, f"{path}.{key}" if path else key)

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)):
                        find_locations(item, f"{path}[{i}]" if path else f"[{i}]")

        find_locations(data)
        return locations

    def _is_location_object(self, obj: dict) -> bool:
        """Check if a dictionary looks like a location object."""
        location_indicators = [
            "address",
            "city",
            "state",
            "zip",
            "latitude",
            "longitude",
            "phone",
        ]
        indicator_count = sum(
            1 for indicator in location_indicators if indicator in obj
        )

        # Also check for common variations
        alt_indicators = [
            "addr",
            "location",
            "street",
            "postal",
            "zipcode",
            "lat",
            "lng",
            "lon",
        ]
        alt_count = sum(1 for indicator in alt_indicators if indicator in obj)

        total_indicators = indicator_count + alt_count

        # Debug output for objects that might be locations
        if total_indicators >= 2:
            _LOGGER.debug(
                f"Location candidate: {total_indicators} indicators, keys: {list(obj.keys())}"
            )

        # Lower threshold and also check for restaurant-specific fields
        restaurant_fields = ["name", "title", "restaurant", "store"]
        has_restaurant_field = any(field in obj for field in restaurant_fields)

        if has_restaurant_field and total_indicators >= 2:
            _LOGGER.debug(
                f"Restaurant location found with {total_indicators} indicators"
            )
            return True

        return total_indicators >= 3

    def _create_location_from_dict(self, data: dict) -> Optional[LocationInfo]:
        """Create LocationInfo from a dictionary."""
        try:
            # Extract common location fields
            store_id = str(
                data.get("id", data.get("storeId", data.get("locationId", "")))
            )
            name = data.get("name", data.get("storeName", ""))
            address = data.get("address", data.get("address1", data.get("street", "")))
            city = data.get("city", "")
            state = data.get("state", data.get("stateCode", ""))
            zip_code = data.get("zip", data.get("zipCode", data.get("postalCode", "")))
            phone = data.get("phone", data.get("phoneNumber", ""))

            # Handle latitude/longitude
            lat = data.get("latitude", data.get("lat", 0))
            lng = data.get("longitude", data.get("lng", data.get("lon", 0)))

            # Convert to float if they're strings
            try:
                latitude = float(lat) if lat else None
                longitude = float(lng) if lng else None
            except (ValueError, TypeError):
                latitude = longitude = None

            # Must have at least city and state to be valid
            if not (city and state):
                return None

            return LocationInfo(
                store_id=store_id,
                name=name or f"Culver's - {city}",
                address=address,
                city=city,
                state=state,
                zip_code=str(zip_code) if zip_code else "",
                phone=phone,
                hours={},
                website_url="",
                latitude=latitude,
                longitude=longitude,
            )
        except Exception as e:
            _LOGGER.debug(f"Error creating location from dict: {e}")
            return None

    def _extract_locations_from_html_fallback(self, html: str) -> List[LocationInfo]:
        """Fallback method to extract locations directly from HTML."""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Look for elements that might contain location data
            locations = []

            # Common patterns for location data in HTML
            location_selectors = [
                "[data-store-id]",
                "[data-location-id]",
                ".restaurant-item",
                ".location-item",
                ".store-item",
            ]

            for selector in location_selectors:
                elements = soup.select(selector)
                for element in elements:
                    location = self._parse_location_element(element)
                    if location:
                        locations.append(location)

            return locations

        except Exception as e:
            _LOGGER.debug(f"Error in HTML fallback extraction: {e}")
            return []

    def _parse_location_element(self, element) -> Optional[LocationInfo]:
        """Parse location from HTML element."""
        # This would be implemented based on actual HTML structure
        # For now, return None as fallback
        return None

    def _filter_locations(
        self, locations: List[LocationInfo], search_term: str, state: Optional[str]
    ) -> List[LocationInfo]:
        """Filter locations based on search criteria."""
        if not locations:
            return []

        filtered = []
        search_lower = search_term.lower() if search_term else ""

        for location in locations:
            # Check state filter first
            if state and location.state.lower() != state.lower():
                continue

            # Check search term match
            if search_term:
                matches = (
                    search_lower in location.city.lower()
                    or search_lower in location.address.lower()
                    or (location.zip_code and search_lower in location.zip_code.lower())
                    or search_lower in location.name.lower()
                )
                if not matches:
                    continue

            filtered.append(location)

        return filtered

    def _parse_xml_locations(self, root) -> Dict[str, Any]:
        """Parse XML response from Culver's API."""
        try:
            # Initialize collection list
            collection = []

            # Look for location elements in XML
            # Common XML patterns for location APIs
            for location_elem in root.findall(".//location"):
                location_data = {}
                for child in location_elem:
                    location_data[child.tag] = child.text
                collection.append(location_data)

            # Alternative pattern - look for any element with location-like attributes
            if not collection:
                for elem in root.iter():
                    if any(
                        attr in elem.attrib for attr in ["clientkey", "store_id", "id"]
                    ):
                        location_data = dict(elem.attrib)
                        # Also get text content of children
                        for child in elem:
                            if child.text and child.text.strip():
                                location_data[child.tag] = child.text.strip()
                        collection.append(location_data)

            _LOGGER.debug(f"Parsed {len(collection)} locations from XML")
            return {"collection": collection}

        except Exception as e:
            _LOGGER.error(f"Error parsing XML locations: {e}")
            return {"collection": []}

    def _parse_location_data(self, data: Dict[str, Any]) -> Optional[LocationInfo]:
        """Parse location data from API response."""
        try:
            store_id = data.get("clientkey", "")
            if not store_id:
                return None

            location = LocationInfo(
                store_id=store_id,
                name=data.get("name", ""),
                address=data.get("address1", ""),
                city=data.get("city", ""),
                state=data.get("state", ""),
                zip_code=data.get("postalcode", ""),
                phone=data.get("phone", ""),
                hours=data.get("hours", {}),
                website_url=data.get("website", ""),
                latitude=float(data.get("latitude", 0.0))
                if data.get("latitude")
                else None,
                longitude=float(data.get("longitude", 0.0))
                if data.get("longitude")
                else None,
            )
            return location
        except (ValueError, TypeError) as e:
            _LOGGER.error(f"Error parsing location data: {e}")
            return None

    async def get_location_by_id(self, location_id: str) -> LocationInfo:
        """Get specific location details by store ID."""
        try:
            # Search for the specific location by ID
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }

            search_data = {"clientkey": location_id, "country": "US"}

            url = f"{self.API_BASE}/rest/getlist.json"
            _LOGGER.debug(f"Getting Culver's location by ID: {location_id}")

            async with self.session.post(
                url, json=search_data, headers=headers
            ) as response:
                if response.status != 200:
                    raise LocationNotFoundError(
                        f"Location with ID {location_id} not found"
                    )

                # Check content type and handle XML/JSON appropriately
                content_type = response.headers.get("content-type", "").lower()
                response_text = await response.text()

                if "application/json" in content_type:
                    data = await response.json()
                elif "text/xml" in content_type or "application/xml" in content_type:
                    _LOGGER.debug("Received XML response for location lookup")
                    from xml.etree import ElementTree as ET

                    root = ET.fromstring(response_text)
                    data = self._parse_xml_locations(root)
                else:
                    # Try JSON anyway
                    try:
                        data = await response.json()
                    except:
                        _LOGGER.error(
                            f"Cannot parse response for location {location_id}"
                        )
                        raise LocationNotFoundError(
                            f"Location with ID {location_id} not found"
                        )

                if data.get("collection"):
                    for location_data in data["collection"]:
                        if location_data.get("clientkey") == location_id:
                            location = self._parse_location_data(location_data)
                            if location:
                                return location

                raise LocationNotFoundError(f"Location with ID {location_id} not found")
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error getting location by ID: {e}")
            raise LocationNotFoundError(f"Location with ID {location_id} not found")
        except Exception as e:
            _LOGGER.error(f"Error getting location by ID: {e}")
            raise LocationNotFoundError(f"Location with ID {location_id} not found")

    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day from Culver's using the proven approach."""
        try:
            _LOGGER.debug(f"Getting flavor for location: {location_id}")

            # Use the restaurant-specific URL approach (following ha-culversfotd)
            restaurant_url = f"{self.BASE_URL}/restaurants/{location_id}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with self.session.get(restaurant_url, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.warning(
                        f"Failed to fetch restaurant page: {response.status}"
                    )
                    raise FlavorNotAvailableError(
                        f"Could not access restaurant page for {location_id}"
                    )

                html = await response.text()
                _LOGGER.debug(f"Got restaurant page, length: {len(html)}")

                # Parse the HTML to extract flavor information
                flavor_info = self._extract_flavor_from_restaurant_page(html)

                if not flavor_info or not flavor_info.name:
                    raise FlavorNotAvailableError(
                        f"No flavor data available for location {location_id}"
                    )

                return flavor_info

        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error getting flavor: {e}")
            raise FlavorNotAvailableError(
                f"Network error accessing location {location_id}"
            )
        except Exception as e:
            _LOGGER.error(f"Error getting current flavor: {e}")
            raise FlavorNotAvailableError(
                f"Could not retrieve flavor for location {location_id}"
            )

    def _extract_flavor_from_restaurant_page(self, html: str) -> Optional[FlavorInfo]:
        """Extract flavor information from restaurant page using __NEXT_DATA__ approach."""
        try:
            import json

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Find the __NEXT_DATA__ script tag (proven approach from ha-culversfotd)
            script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
            if not script_tag or not script_tag.string:
                _LOGGER.debug("No __NEXT_DATA__ script tag found")
                return None

            try:
                json_data = json.loads(script_tag.string)
                _LOGGER.debug("Successfully parsed __NEXT_DATA__")

                # Navigate to restaurant details following the proven path
                restaurant_details = json_data["props"]["pageProps"]["page"][
                    "customData"
                ]["restaurantDetails"]

                # Extract flavor information
                flavors = restaurant_details.get("flavors", [])
                if not flavors:
                    _LOGGER.debug("No flavors found in restaurant details")
                    return None

                # Get the first (current) flavor
                current_flavor = flavors[0]
                flavor_name = current_flavor.get("name", "")

                if not flavor_name:
                    _LOGGER.debug("Flavor name is empty")
                    return None

                _LOGGER.debug(f"Found flavor: {flavor_name}")

                # Extract additional flavor details if available
                description = current_flavor.get("description", "")
                ingredients = current_flavor.get("ingredients", "")

                return FlavorInfo(
                    name=flavor_name,
                    description=description,
                    ingredients=ingredients,
                    available_date=datetime.now(),
                    calories=current_flavor.get("calories"),
                    allergens=current_flavor.get("allergens", []),
                )

            except (json.JSONDecodeError, KeyError) as e:
                _LOGGER.debug(f"Error parsing restaurant data: {e}")
                return None

        except Exception as e:
            _LOGGER.error(f"Error extracting flavor from restaurant page: {e}")
            return None

    async def _get_flavor_from_url(self, url: str) -> Optional[FlavorInfo]:
        """Get flavor information from a URL."""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    _LOGGER.debug(
                        f"Failed to get flavor page: {url}, status {response.status}"
                    )
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Look for flavor information in the page
                # Different possible selectors based on typical Culver's page structure
                flavor_selectors = [
                    ".flavor-name",  # Common flavor name class
                    ".flavor-title",  # Alternative flavor title
                    "[data-flavor-name]",  # Data attribute
                    ".hero-content h2",  # Hero section
                    ".flavor-of-day h2",  # Flavor of day section
                ]

                for selector in flavor_selectors:
                    flavor_element = soup.select_one(selector)
                    if flavor_element:
                        flavor_name = flavor_element.get_text(strip=True)
                        if flavor_name:
                            return FlavorInfo(
                                name=flavor_name,
                                available_date=datetime.now(),
                                description=self._extract_description(soup),
                            )

                # If specific selectors didn't work, look for any element containing "flavor"
                flavor_elements = soup.find_all(
                    string=lambda text: text and "flavor" in text.lower()
                )
                for element in flavor_elements:
                    parent = element.parent
                    if parent:
                        # Look for the next sibling or nearby elements that might contain the flavor name
                        flavor_text = parent.get_text(strip=True)
                        if (
                            len(flavor_text) < 100
                        ):  # Reasonable length for a flavor name
                            return FlavorInfo(
                                name=flavor_text, available_date=datetime.now()
                            )

                return None
        except Exception as e:
            _LOGGER.debug(f"Error parsing flavor from URL {url}: {e}")
            return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract flavor description from soup."""
        description_selectors = [
            ".flavor-description",
            ".flavor-info",
            ".description",
            'p:contains("flavor")',
        ]

        for selector in description_selectors:
            desc_element = soup.select_one(selector)
            if desc_element:
                return desc_element.get_text(strip=True)

        return None

    async def _get_flavor_from_api(self, location_id: str) -> Optional[FlavorInfo]:
        """Get flavor information using API approach."""
        # For Culver's, try to get flavor info via their restaurant API
        # This is a fallback approach when HTML scraping doesn't work
        try:
            # Attempt to get flavor data via a possible API endpoint
            # This is an educated guess based on common patterns
            headers = {
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }

            # Try a possible flavor API endpoint
            flavor_api_url = f"{self.BASE_URL}/api/flavor-of-the-day/{location_id}"
            async with self.session.get(flavor_api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    if "flavor" in data:
                        return FlavorInfo(
                            name=data["flavor"].get("name", ""),
                            description=data["flavor"].get("description", ""),
                            available_date=datetime.now(),
                        )
        except Exception as e:
            _LOGGER.debug(f"Error getting flavor from API: {e}")

        # If API approach fails, return None to use other methods
        return None

    async def get_upcoming_flavors(
        self, location_id: str, days: int = 7
    ) -> List[tuple[date, FlavorInfo]]:
        """Get upcoming flavors (if supported by Culver's)."""
        # Culver's doesn't typically provide upcoming flavors - only the current day's flavor
        # So we'll return an empty list as per the base class default
        return []
