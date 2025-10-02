# Home Assistant Flavor of the Day Integration Development Guide

## Overview

The Flavor of the Day integration is a Home Assistant custom component that provides information about the daily flavor offerings from popular ice cream and frozen custard locations. The integration follows Home Assistant's best practices and modern patterns for custom integrations.

## Architecture

The integration follows a three-layer architecture pattern:

1. **Provider Layer** (`providers/`): Abstract data fetching from external APIs
2. **Coordinator Layer** (`coordinator.py`): Manages data updates and caching
3. **Sensor Layer** (`sensor.py`): Exposes data to Home Assistant UI

### Component Structure
```
custom_components/flavor_of_the_day/
├── __init__.py          # Integration entry point and setup
├── config_flow.py       # Configuration flow for UI setup
├── const.py             # Configuration constants and domain definition
├── coordinator.py       # Data update coordinator
├── data.py              # Runtime data structures
├── exceptions.py        # Custom exception hierarchy
├── manifest.json        # Integration manifest
├── models.py            # Data models for flavors and locations
├── sensor.py            # Sensor entity implementation
└── providers/           # Store-specific data providers
    ├── base.py          # Abstract provider interface
    ├── culvers.py       # Culver's restaurant chain provider
    ├── kopps.py         # Kopp's frozen custard provider
    ├── oscars.py        # Oscar's restaurant provider
    └── leducs.py        # Leduc's restaurant provider
```

## Core Implementation Patterns

### 1. Runtime Data Pattern
The integration uses the modern `entry.runtime_data` pattern instead of the deprecated `hass.data`:

```python
# In __init__.py
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # ...
    entry.runtime_data = FlavorOfTheDayData(
        coordinator=coordinator,
        provider=provider,
    )
```

### 2. Config Entry Type Safety
The integration uses type-safe config entries:

```python
# In const.py
if TYPE_CHECKING:
    class FlavorOfTheDayConfigEntry(ConfigEntry):
        runtime_data: FlavorOfTheDayData
```

### 3. Data Update Coordinator
The coordinator manages data fetching with proper error handling:

```python
class FlavorUpdateCoordinator(DataUpdateCoordinator[FlavorInfo]):
    async def _async_update_data(self) -> FlavorInfo:
        try:
            return await self.provider.get_current_flavor(self.location_id)
        except FlavorProviderAuthenticationError as err:
            raise ConfigEntryAuthFailed(
                f"Authentication failed for {self.provider.provider_name}: {err}"
            ) from err
        except FlavorProviderError as err:
            raise UpdateFailed(
                f"Error communicating with {self.provider.provider_name}: {err}"
            ) from err
```

### 4. Declarative Entity Pattern
Sensors use the `SensorEntityDescription` pattern for clean entity definitions:

```python
SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(
        key="flavor_of_the_day",
        name="Flavor of the Day",
        icon="mdi:ice-cream",
        device_class=None,  # Changed from SensorDeviceClass.ENUM
    ),
)
```

## Adding New Providers

To add support for a new ice cream store provider:

### 1. Create Provider Class
Create a new provider file in `providers/` that inherits from `BaseFlavorProvider`:

```python
# providers/new_provider.py
from ..models import FlavorInfo, LocationInfo
from .base import BaseFlavorProvider

class NewProvider(BaseFlavorProvider):
    @property
    def provider_name(self) -> str:
        return "New Ice Cream Store"

    @property
    def provider_id(self) -> str:
        return "newprovider"

    async def search_locations(
        self, search_term: str, state: str | None = None
    ) -> list[LocationInfo]:
        # Implement location search logic
        pass

    async def get_location_by_id(self, location_id: str) -> LocationInfo:
        # Implement location detail retrieval
        pass

    async def get_current_flavor(self, location_id: str) -> FlavorInfo:
        # Implement flavor retrieval logic
        pass
```

### 2. Register Provider
Add the provider to the `PROVIDER_CLASSES` mapping in `__init__.py` and `config_flow.py`.

### 3. Add to Config Flow
Update the `USER_SCHEMA` selector in `config_flow.py` to include your new provider.

## Configuration Flow

The integration implements a multi-step configuration flow:

1. **User Step**: Select provider type
2. **Location Search**: Enter search term and optional state
3. **Location Selection**: Choose from search results and set options

The flow uses Home Assistant's UI selectors for consistent user experience.

## Exception Handling

The integration implements a custom exception hierarchy:

```
FlavorProviderError (base)
├── FlavorProviderCommunicationError
│   ├── FlavorProviderTimeoutError
│   ├── RateLimitError
│   └── NetworkError
├── FlavorProviderAuthenticationError
├── LocationNotFoundError
└── FlavorNotAvailableError
```

## Models and Data Structures

### FlavorInfo Model
```python
@dataclass
class FlavorInfo:
    name: str
    description: str | None
    ingredients: list[str] | None
    allergens: list[str] | None
    image_url: str | None
    available_date: datetime | None
    price: str | None
    nutrition_info: dict[str, str] | None
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
    zip_code: str | None
    phone: str | None
    hours: dict[str, str] | None
    website_url: str | None
    latitude: float | None
    longitude: float | None
```

## Testing Guidelines

### Unit Tests
Create tests using `pytest` and `pytest-homeassistant-custom-component`:

```python
# tests/test_sensor.py
async def test_sensor_state(hass, mock_coordinator):
    """Test sensor state."""
    with patch("custom_components.flavor_of_the_day.coordinator.FlavorUpdateCoordinator"):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_PROVIDER: "culvers", CONF_LOCATION_ID: "test_id"},
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        state = hass.states.get("sensor.flavor_of_the_day")
        assert state.state == "Test Flavor"
```

### Mocking Providers
Use mocking to test without external API calls:

```python
async def test_config_flow(hass, mock_provider):
    """Test config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # Test flow steps...
```

## Code Quality Standards

### Linting
The project uses ruff with Home Assistant's standards:
- Target Python 3.13
- Strict linting with "ALL" rule selection
- Maximum complexity of 25 for functions
- Runtime typing kept for compatibility

### Type Hints
Use proper type hints throughout:

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
```

### Async/Await
All API calls must be async to avoid blocking the event loop.

## Device and Entity Management

### Device Grouping
Sensors are properly grouped under devices using `DeviceInfo`:

```python
@property
def device_info(self) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
        name=self._attr_name,
        manufacturer=self.coordinator.provider.provider_name,
        model="Flavor of the Day Sensor",
    )
```

### Unique Identifiers
Each entity has a unique ID based on the config entry:

```python
self._attr_unique_id = (
    f"{coordinator.config_entry.entry_id}_{entity_description.key}"
)
```

## Error Handling and Recovery

### Coordinator Error Handling
The coordinator handles different error types appropriately:

- `FlavorProviderAuthenticationError` → `ConfigEntryAuthFailed`
- `FlavorProviderError` → `UpdateFailed`

### Connection Testing
Config flow tests connections before finalizing setup:

```python
if not await self.provider.test_connection(location_id):
    errors[CONF_LOCATION_ID] = "connection_failed"
```

## Manifest Configuration

The manifest.json file must include:

- Domain matching directory name
- Correct version format
- All required dependencies
- Proper documentation and issue tracker URLs
- IoT class set to "cloud_polling"

## Development Workflow

### Setting Up Development Environment
1. Install dependencies: `./scripts/setup`
2. Lint code: `./scripts/lint`
3. Start development Home Assistant: `./scripts/develop`

### Testing Changes
1. Run linters: `./scripts/lint`
2. Run tests: `pytest`
3. Test integration in development Home Assistant

## Deviations from Standards and Recommendations

### Current Deviations
1. **Device Class**: Currently using `SensorDeviceClass.ENUM` which may not be appropriate for flavor text
2. **Entity Category**: Consider using `EntityCategory.DIAGNOSTIC` for utility sensors
3. **Testing**: No visible integration tests in the repository

### Recommended Improvements
1. **Add Integration Tests**: Create comprehensive test files
2. **Improve Device Class**: Consider `SensorDeviceClass.TEXT` or custom device class
3. **Add Logging**: Ensure comprehensive logging throughout
4. **Add Documentation**: More detailed setup and troubleshooting docs

## Best Practices

### Do's
- Always use async/await for I/O operations
- Implement proper error handling
- Use Home Assistant's selectors for config flow
- Follow type annotation conventions
- Use `DataUpdateCoordinator` for data management
- Implement proper unique ID management

### Don'ts
- Don't block the event loop with sync operations
- Don't store data in `hass.data` (use `runtime_data` instead)
- Don't hardcode configuration values
- Don't ignore Home Assistant's linting rules
- Don't create duplicate entities

## Troubleshooting

### Common Issues
1. **No Locations Found**: May indicate website structure changes
2. **Connection Errors**: Check internet connectivity and provider availability
3. **Authentication Errors**: Verify account credentials if required

### Debugging
Enable debug logging by adding this to configuration.yaml:

```yaml
logger:
  default: info
  logs:
    custom_components.flavor_of_the_day: debug
```