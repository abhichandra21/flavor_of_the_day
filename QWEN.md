# QWEN.md - Flavor of the Day Home Assistant Integration

## Project Overview

**Flavor of the Day** is a Home Assistant custom integration that provides information about the daily flavor offerings from popular ice cream and frozen custard locations. The integration allows users to get notified when their favorite store's flavor of the day changes.

### Key Features
- Supports multiple ice cream store chains (Culver's, Kopp's, Oscar's, Leduc's)
- Real-time flavor information with rich attributes
- Configurable update intervals
- Easy setup through Home Assistant's configuration flow
- Home Assistant 2025.2.4 compatible

### Architecture
The integration follows a three-layer architecture:
1. **Provider Layer** (`providers/`): Abstract data fetching from external APIs
2. **Coordinator Layer** (`coordinator.py`): Manages data updates and caching
3. **Sensor Layer** (`sensor.py`): Exposes data to Home Assistant UI

## Project Structure

```
flavor_of_the_day/
├── .devcontainer.json         # VS Code development container configuration
├── .github/                   # GitHub issue templates
├── .ruff.toml                # Python linting configuration (matching Home Assistant standards)
├── CLAUDE.md                 # Claude AI guidance file
├── CONTRIBUTING.md           # Contribution guidelines
├── QWEN.md                   # This file
├── README.md                 # Project documentation
├── config/                   # Home Assistant configuration directory (for development)
├── custom_components/        # Home Assistant custom components
│   └── flavor_of_the_day/    # Main integration directory
│       ├── __init__.py       # Integration entry point and setup
│       ├── config_flow.py    # Configuration flow for UI setup
│       ├── const.py          # Configuration constants
│       ├── coordinator.py    # Data update coordinator
│       ├── data.py           # Runtime data structures
│       ├── exceptions.py     # Custom exception hierarchy
│       ├── manifest.json     # Integration manifest
│       ├── models.py         # Data models for flavors and locations
│       ├── sensor.py         # Sensor entity implementation
│       └── providers/        # Store-specific data providers
│           ├── base.py       # Abstract provider interface
│           ├── culvers.py    # Culver's restaurant chain provider
│           ├── kopps.py      # Kopp's frozen custard provider
│           ├── oscars.py     # Oscar's restaurant provider
│           └── leducs.py     # Leduc's restaurant provider
├── hacs.json                 # HACS integration configuration
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies for development
└── scripts/                  # Development scripts
    ├── setup                 # Install Python dependencies
    ├── lint                  # Format and lint code with ruff
    └── develop               # Start Home Assistant with this integration loaded
```

## Building and Running

### Prerequisites
- Python 3.13+
- Home Assistant (2025.2.4 or compatible)
- Required Python packages: `aiohttp`, `beautifulsoup4`, `lxml`, `python-dateutil`

### Development Setup
1. Clone the repository
2. Install dependencies: `./scripts/setup`
3. Start development Home Assistant instance: `./scripts/develop`

### Development Commands
- `./scripts/setup`: Install Python dependencies
- `./scripts/lint`: Format and lint code with ruff
- `./scripts/develop`: Start Home Assistant with this integration loaded

### Testing
The integration uses Home Assistant's testing framework, though specific test files are not visible in the current structure. Additional tests can be added following Home Assistant patterns.

## Development Conventions

### Code Quality
- The project uses strict linting with ruff configured to match Home Assistant core standards
- Target Python 3.13
- "ALL" rule selection with specific ignores for formatter compatibility
- Maximum complexity of 25 for functions
- Runtime typing kept for compatibility

### Adding New Provider Support
The integration follows a provider pattern that makes it easy to add support for new ice cream store chains:
1. Create a new provider class in `custom_components/flavor_of_the_day/providers/` that inherits from `BaseFlavorProvider`
2. Implement the required abstract methods: `search_locations()`, `get_location_by_id()`, `get_current_flavor()`, and `test_connection()`
3. Add your provider class to the `PROVIDER_CLASSES` dictionary in `__init__.py`
4. Add your provider to the configuration flow in `config_flow.py`

### Error Handling
Custom exception system in `exceptions.py`:
- `FlavorProviderError` (base)
  - `FlavorProviderCommunicationError`
    - `FlavorProviderTimeoutError`
    - `RateLimitError`
    - `NetworkError`
  - `FlavorProviderAuthenticationError`
  - `LocationNotFoundError`
  - `FlavorNotAvailableError`

### Modern Home Assistant Patterns
- **Runtime Data**: Uses `entry.runtime_data` instead of deprecated `hass.data`
- **Type-Safe Config Entries**: Custom ConfigEntry type with runtime_data typing
- **Async-First**: All operations use async/await
- **Declarative Entities**: Uses `SensorEntityDescription` pattern
- **Device Grouping**: Proper `DeviceInfo` implementation for UI organization

## Installation Options

### Manual Installation
1. Using the tool of choice open the Home Assistant configuration directory (Where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory there, you need to create it.
3. Download the latest release from the releases page.
4. Create a new folder `flavor_of_the_day` in the `custom_components` directory.
5. Copy all the files from the `custom_components/flavor_of_the_day` directory in this repository into the new directory in your Home Assistant installation.

### Using HACS (Home Assistant Community Store)
1. Install HACS if you haven't already.
2. Go to HACS > Integrations.
3. Click the blue "+" button in the bottom right.
4. Search for "Flavor of the Day".
5. Click the "Download" button on the integration.
6. Restart Home Assistant.

## Configuration

### Via Home Assistant UI
1. Go to Settings > Devices & Services
2. Click on "+ Add Integration"
3. Search for "Flavor of the Day"
4. Follow the configuration steps:
   - Select the provider (store chain)
   - Search for your location by city, state, or zip code
   - Select the specific location from the results
   - Optionally customize update interval
5. Click "Submit" to complete the setup

### Configuration Options
- **Provider**: Select the ice cream store chain (Culver's, Kopp's, Oscar's, Leduc's)
- **Location**: Search and select your desired store location
- **Update Interval**: How often to check for new flavors (default: 30 minutes)

## Usage

Once configured, the integration will create a sensor that displays the current flavor of the day. The sensor includes rich attributes with additional information:
- Flavor name
- Description
- Ingredients
- Allergens
- Pricing information
- Last updated timestamp

## Supported Providers
- Culver's: Daily frozen custard flavor information
- Kopp's: Frozen custard flavor of the day
- Oscar's: Daily ice cream flavor
- Leduc's: Daily flavor information