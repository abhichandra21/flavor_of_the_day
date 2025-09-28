# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Dependencies
```bash
./scripts/setup                    # Install Python dependencies
```

### Code Quality
```bash
./scripts/lint                     # Format code with ruff and fix issues
ruff format .                      # Format code only
ruff check . --fix                 # Check and fix issues only
```

### Development and Testing
```bash
./scripts/develop                  # Start Home Assistant with this integration loaded
./scripts/test                     # Run full test suite with coverage
./scripts/validate                 # Quick validation and syntax checking
./scripts/test-providers           # Test provider connectivity without HA
```

**Testing Hierarchy (fastest to slowest):**
1. **`./scripts/validate`** - Syntax, imports, manifest validation (~5 seconds)
2. **`./scripts/test-providers`** - Test real API connectivity (~10-30 seconds)
3. **`./scripts/test`** - Full pytest suite with mocks (~30-60 seconds)
4. **`./scripts/develop`** - Full Home Assistant integration test (manual)

Use `./scripts/validate` for quick feedback during development.

## Integration Architecture

### Core Design Pattern: Provider-Coordinator-Sensor
This integration follows a three-layer architecture:

1. **Provider Layer** (`providers/`): Abstract data fetching from external APIs
   - `BaseFlavorProvider`: Abstract base class defining the interface
   - Each store chain has its own provider (Culver's, Kopp's, Oscar's, Leduc's)
   - Providers handle web scraping and API calls to fetch flavor data

2. **Coordinator Layer** (`coordinator.py`): Manages data updates and caching
   - `FlavorUpdateCoordinator`: Extends Home Assistant's `DataUpdateCoordinator`
   - Handles polling intervals, error recovery, and data caching
   - Maps provider exceptions to Home Assistant error types

3. **Sensor Layer** (`sensor.py`): Exposes data to Home Assistant UI
   - Single sensor entity that displays current flavor as state
   - Rich attributes include description, ingredients, allergens, pricing
   - Uses declarative entity pattern with `SensorEntityDescription`

### Provider System Extensibility
To add a new ice cream store provider:

1. Create new provider class inheriting from `BaseFlavorProvider`
2. Implement required abstract methods:
   - `search_locations()`: Find stores by search term/location
   - `get_location_by_id()`: Get specific store details
   - `get_current_flavor()`: Fetch today's flavor
   - `test_connection()`: Validate connectivity
3. Add to `PROVIDER_CLASSES` dictionary in `__init__.py`
4. Add to provider options in `config_flow.py`

### Configuration Flow Pattern
Multi-step setup wizard implemented in `config_flow.py`:

1. **Provider Selection**: Dropdown of available store chains
2. **Location Search**: Text search + optional state filter
3. **Location Selection**: Choose from found locations + customize settings

Key features:
- Dynamic schema generation based on search results
- Single location optimization (skips selection if only one found)
- Connection testing before finalizing setup
- Unique ID management to prevent duplicates

### Data Models and Type Safety
The integration uses structured data models in `models.py`:

- **`FlavorInfo`**: Comprehensive flavor data structure
- **`LocationInfo`**: Store location details
- **`FlavorOfTheDayData`**: Runtime data container

All code uses type hints with `TYPE_CHECKING` guards for import optimization.

### Error Handling Hierarchy
Custom exception system in `exceptions.py`:
- `FlavorProviderError` (base)
  - `FlavorProviderCommunicationError`
    - `FlavorProviderTimeoutError`
    - `RateLimitError`
    - `NetworkError`
  - `FlavorProviderAuthenticationError`
  - `LocationNotFoundError`
  - `FlavorNotAvailableError`

These exceptions map to appropriate Home Assistant error types in the coordinator.

### Modern Home Assistant Patterns
- **Runtime Data**: Uses `entry.runtime_data` instead of deprecated `hass.data`
- **Type-Safe Config Entries**: Custom ConfigEntry type with runtime_data typing
- **Async-First**: All operations use async/await
- **Declarative Entities**: Uses `SensorEntityDescription` pattern
- **Device Grouping**: Proper `DeviceInfo` implementation for UI organization

## File Structure Overview

- **`__init__.py`**: Integration entry point, provider registration, setup/teardown
- **`config_flow.py`**: Multi-step configuration wizard
- **`coordinator.py`**: Data update coordination and error handling
- **`sensor.py`**: Home Assistant sensor entity implementation
- **`const.py`**: Configuration constants and domain definition
- **`data.py`**: Runtime data structures
- **`models.py`**: Data models for flavors and locations
- **`exceptions.py`**: Custom exception hierarchy
- **`providers/`**: Store-specific data providers
  - **`base.py`**: Abstract provider interface
  - **`culvers.py`**: Culver's restaurant chain provider
  - **`kopps.py`**: Kopp's frozen custard provider
  - **`oscars.py`**: Oscar's restaurant provider
  - **`leducs.py`**: Leduc's restaurant provider

## Code Quality Standards

The project uses strict linting with ruff configured to match Home Assistant core standards:
- Target Python 3.13
- "ALL" rule selection with specific ignores for formatter compatibility
- Maximum complexity of 25 for functions
- Fixture parentheses disabled for pytest style
- Runtime typing kept for compatibility

All new code should pass `./scripts/lint` without warnings.