# Provider API Implementation Details

This document details the implementation of each flavor provider in the Flavor of the Day integration.

## Architecture

The integration uses a provider-based architecture with a common interface defined by `BaseFlavorProvider`. Each provider implements this interface to connect to different ice cream store chains.

## Base Provider Interface

All providers inherit from `BaseFlavorProvider` which defines the following required methods:

```python
class BaseFlavorProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Display name for this provider."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier for this provider (lowercase, no spaces)."""

    @abstractmethod
    async def search_locations(self, search_term: str, state: str | None = None) -> list[LocationInfo]:
        """Search for store locations by city, zip, or address."""

    @abstractmethod
    async def get_location_by_id(self, location_id: str) -> LocationInfo:
        """Get specific location details by store ID."""

    @abstractmethod
    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day."""

    async def test_connection(self, location_id: str) -> bool:
        """Test if provider can connect to store data."""
```

## Provider Implementations

### Culver's Provider (`culvers.py`)

**Base URL**: https://www.culvers.com

**Implementation Details**:
- Uses website scraping to extract flavor information
- Parses Next.js `__NEXT_DATA__` for restaurant details
- Searches for location data in JavaScript structures embedded in HTML
- Uses JSON parsing to extract flavor information from restaurant details
- Implements fallback methods for location extraction

**API Endpoints**:
- Location search: `https://hosted.where2getit.com/culvers/rest/getlist.json`
- Restaurant pages: `https://www.culvers.com/restaurants/{location_id}`

**Data Extraction**:
- Flavors are extracted from the `__NEXT_DATA__` script tag
- Location information is parsed from either JSON structures or HTML elements
- Implements recursive search through JSON structures for location data

### Kopp's Provider (`kopps.py`)

**Base URL**: https://www.kopps.com

**Implementation Details**:
- Uses web scraping to extract flavor information
- Implements robust HTML parsing methods
- Handles dynamic content loading
- Implements multiple fallback strategies for data extraction

**Data Extraction**:
- Flavor names extracted from DOM elements with specific class names
- Implements text-based search for flavor information
- Handles both calendar-based and direct flavor listings

### Oscar's Provider (`oscars.py`)

**Base URL**: https://www.oscarsicecream.com

**Implementation Details**:
- Uses web scraping to access flavor information
- Implements multiple selectors for robust data extraction
- Handles different page layouts that may exist across locations

**Data Extraction**:
- Flavor information extracted from various possible DOM locations
- Implements fallback extraction methods for different page structures

### Leduc's Provider (`leducs.py`)

**Base URL**: https://www.leducscustard.com

**Implementation Details**:
- Uses web scraping to access flavor information
- Implements date-based flavor lookup
- Handles calendar-style flavor displays

**Data Extraction**:
- Flavors extracted based on current date
- Implements parsing for calendar-style layouts
- Multiple fallback strategies for different page formats

## Data Models

### FlavorInfo Model
```python
@dataclass
class FlavorInfo:
    name: str
    description: str | None = None
    ingredients: list[str] | None = None
    allergens: list[str] | None = None
    image_url: str | None = None
    available_date: datetime | None = None
    price: str | None = None
    nutrition_info: dict[str, str] | None = None
```

### LocationInfo Model
```python
@dataclass
class LocationInfo:
    store_id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str | None = None
    phone: str | None = None
    hours: dict[str, str] | None = None
    website_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
```

## Error Handling

Each provider implements error handling using the custom exception hierarchy:

- `FlavorProviderError` (base exception)
  - `FlavorProviderCommunicationError`
    - `FlavorProviderTimeoutError`
    - `RateLimitError`
    - `NetworkError`
  - `FlavorProviderAuthenticationError`
  - `LocationNotFoundError`
  - `FlavorNotAvailableError`

## Provider-Specific Challenges

### Website Structure Changes
- Providers may change their website structure, requiring updates to scraping methods
- JavaScript-heavy sites may require parsing client-side rendered data
- Dynamic content loading can complicate data extraction

### Rate Limiting
- Providers may implement rate limiting
- Aggressive requests might result in IP bans
- Update intervals should be set appropriately

### Data Availability
- Some locations may not publish their flavors online
- Seasonal availability may affect data
- Store-specific practices might vary

## Extending with New Providers

To add support for a new provider:

1. Create a new provider class in `providers/` that extends `BaseFlavorProvider`
2. Implement all required abstract methods
3. Add the provider to the `PROVIDER_CLASSES` dictionary in `__init__.py`
4. Register the provider in the config flow if needed
5. Add appropriate error handling for provider-specific issues
6. Include the provider in test coverage

## Best Practices

1. **Robust Error Handling**: Implement appropriate error handling for network issues, parsing errors, and provider-specific failures
2. **Respectful Scraping**: Use appropriate delays between requests to avoid overloading provider servers
3. **Fallback Mechanisms**: Implement multiple methods to extract data in case primary method fails
4. **Data Validation**: Validate extracted data before returning to ensure quality
5. **Logging**: Use appropriate logging levels to help diagnose issues
6. **Efficient Parsing**: Parse only necessary data to minimize processing time
7. **Session Management**: Reuse HTTP sessions when possible for efficiency