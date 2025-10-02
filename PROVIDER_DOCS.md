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

    async def get_upcoming_flavors(
        self, location_id: str, days: int = 7
    ) -> list[tuple[date, FlavorInfo]]:
        """Get upcoming flavors (if supported by provider)."""
        return []

    async def test_connection(self, location_id: str) -> bool:
        """Test if provider can connect to store data."""

    def __init__(self, session: aiohttp.ClientSession, config: dict[str, Any]) -> None:
        """Initialize the base flavor provider."""
        # Includes rate limiting and retry logic implementation
```

## Provider Implementations

### Culver's Provider (`culvers.py`)

**Base URL**: https://www.culvers.com

**Implementation Details**:
- Uses website scraping to extract flavor information
- Utilizes Culver's location API endpoints
- Implements retry and rate limiting logic
- Uses modern API endpoints instead of web scraping

**API Endpoints**:
- Location search: `https://www.culvers.com/api/locator/getLocations`
- Restaurant pages: `https://www.culvers.com/restaurants/{location_id}`

**Data Extraction**:
- Flavors are extracted from the location API response data
- Location information is parsed from API response
- Implements fallback for zip code handling if not in configuration

### Kopp's Provider (`kopps.py`)

**Base URL**: https://www.kopps.com

**Implementation Details**:
- Uses web scraping to extract flavor information
- Implements robust HTML parsing methods
- Handles dynamic content loading
- Implements multiple fallback strategies for data extraction
- Supports fetching upcoming flavors

**Data Extraction**:
- Flavor names extracted from DOM elements with specific class names
- Implements text-based search for flavor information
- Handles both calendar-based and direct flavor listings

### Oscar's Provider (`oscars.py`)

**Base URL**: https://www.oscarscustard.com

**Implementation Details**:
- Uses web scraping to access flavor information
- Implements multiple selectors for robust data extraction
- Handles different page layouts that may exist across locations

**Data Extraction**:
- Flavor information extracted from various possible DOM locations
- Implements fallback extraction methods for different page structures

### Goodberry's Provider (`goodberrys.py`)

**Base URL**: https://goodberrys.com

**Implementation Details**:
- Uses web scraping to extract flavor information
- Implements robust HTML parsing methods
- Handles static location list
- Implements rate limiting and retry logic

**Data Extraction**:
- Flavor name extracted from elements with classes containing "flavor-of-the-day"
- Implements multiple selectors for different possible HTML structures

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

Adding support for a new provider is straightforward. Follow these steps to implement a new provider:

### Step 1: Create the Provider Class

Create a new file in `custom_components/flavor_of_the_day/providers/` with a descriptive name (e.g., `my_new_provider.py`). The class should extend `BaseFlavorProvider` and implement all required abstract methods:

```python
from custom_components.flavor_of_the_day.providers.base import BaseFlavorProvider

class MyNewProvider(BaseFlavorProvider):
    @property
    def provider_name(self) -> str:
        """Display name for this provider."""
        return "My New Provider Name"

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider (lowercase, no spaces)."""
        return "my_new_provider"

    async def search_locations(self, search_term: str, state: str | None = None) -> list[LocationInfo]:
        """Search for store locations by city, zip, or address."""
        # Implement location search logic
        
    async def get_location_by_id(self, location_id: str) -> LocationInfo:
        """Get specific location details by store ID."""
        # Implement location details retrieval logic
        
    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        """Get today's flavor of the day."""
        # Implement flavor retrieval logic
```

### Step 2: Implement Required Methods

Your new provider must implement these methods from the base class:

- **provider_name**: Return a human-readable name for the provider
- **provider_id**: Return a unique identifier (lowercase, no spaces) for the provider
- **search_locations**: Search for locations by city, ZIP code, or address and return a list of `LocationInfo` objects
- **get_location_by_id**: Get specific location details by the location ID and return a `LocationInfo` object
- **get_current_flavor**: Get today's flavor for the given location ID and return a `FlavorInfo` object

### Step 3: Add Provider Class Registration

1. Add your provider class to the import statements in `__init__.py`:
```python
from .providers.my_new_provider import MyNewProvider
```

2. Add your provider to the `PROVIDER_CLASSES` dictionary in `__init__.py`:
```python
PROVIDER_CLASSES = {
    "culvers": CulversProvider,
    "kopps": KoppsProvider,
    "oscars": OscarsProvider,
    "goodberrys": GoodberrysProvider,
    "my_new_provider": MyNewProvider,  # Add this line
}
```

### Step 4: Add to Configuration Flow

1. Add your provider to the import statements in `config_flow.py`:
```python
from .providers.my_new_provider import MyNewProvider
```

2. Add your provider to the `PROVIDER_CLASSES` dictionary in `config_flow.py`:
```python
PROVIDER_CLASSES = {
    "culvers": CulversProvider,
    "kopps": KoppsProvider,
    "oscars": OscarsProvider,
    "goodberrys": GoodberrysProvider,
    "my_new_provider": MyNewProvider,  # Add this line
}
```

3. Add your provider to the UI selection options in `config_flow.py`:
```python
USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PROVIDER): SelectSelector(
            SelectSelectorConfig(
                options=[
                    SelectOptionDict(value="culvers", label="Culver's"),
                    SelectOptionDict(value="kopps", label="Kopp's Frozen Custard"),
                    SelectOptionDict(value="oscars", label="Oscar's Frozen Custard"),
                    SelectOptionDict(
                        value="goodberrys", label="Goodberry's Frozen Custard"
                    ),
                    SelectOptionDict(
                        value="my_new_provider", label="My New Provider Name"
                    ),  # Add this line
                ],
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
    }
)
```

### Step 5: Add Tests

Create tests for your new provider in the `tests/` directory to ensure it works correctly:

1. Add your provider to the test suite in `tests/test_all_providers.py`:
   - Add the import
   - Add the test class following the same pattern as other providers
   - Add your provider to the `test_all_providers_interface` test

### Step 6: Best Practices

Follow these best practices when implementing your provider:

1. **Robust Error Handling**: Implement appropriate error handling for network issues, parsing errors, and provider-specific failures
2. **Respectful Scraping**: Use appropriate delays between requests to avoid overloading provider servers (the base class handles rate limiting)
3. **Fallback Mechanisms**: Implement multiple methods to extract data in case the primary method fails
4. **Data Validation**: Validate extracted data before returning to ensure quality
5. **Logging**: Use appropriate logging levels to help diagnose issues
6. **Efficient Parsing**: Parse only necessary data to minimize processing time
7. **Session Management**: Reuse HTTP sessions when possible (handled by the base class)
8. **Follow HTTP Standards**: Respect HTTP headers, rate limits, and robots.txt files

### Step 7: Testing Your New Provider

After implementing your provider:

1. Test the location search functionality with various inputs
2. Test getting flavor information for known locations
3. Test error conditions (invalid location ID, network errors, etc.)
4. Verify that the sensor displays properly in Home Assistant
5. Ensure the entity picture (if applicable) loads correctly
6. Test the options flow to change update intervals

## Best Practices

1. **Robust Error Handling**: Implement appropriate error handling for network issues, parsing errors, and provider-specific failures
2. **Respectful Scraping**: Use appropriate delays between requests to avoid overloading provider servers
3. **Fallback Mechanisms**: Implement multiple methods to extract data in case primary method fails
4. **Data Validation**: Validate extracted data before returning to ensure quality
5. **Logging**: Use appropriate logging levels to help diagnose issues
6. **Efficient Parsing**: Parse only necessary data to minimize processing time
7. **Session Management**: Reuse HTTP sessions when possible for efficiency