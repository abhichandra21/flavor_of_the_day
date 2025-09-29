# Flavor of the Day Home Assistant Integration

**Flavor of the Day** is a Home Assistant custom integration that provides information about the daily flavor offerings from popular ice cream and frozen custard locations. The integration allows users to get notified when their favorite store's flavor of the day changes.

## Features
- Supports multiple ice cream store chains (Culver's, Kopp's, Oscar's, Leduc's)
- Real-time flavor information with rich attributes
- Configurable update intervals
- Easy setup through Home Assistant's configuration flow
- Device tracking for multiple locations

## Installation

### Using HACS (Recommended)
1. Install HACS if you haven't already
2. Go to HACS > Integrations
3. Click the `+` icon in the bottom right
4. Search for "Flavor of the Day"
5. Click "Download"
6. Restart Home Assistant

### Manual Installation
1. Download the latest release from the releases page
2. Create a new folder `flavor_of_the_day` in your Home Assistant's `custom_components` directory
3. Copy all the files from the `custom_components/flavor_of_the_day` directory into the new directory in your Home Assistant installation
4. Restart Home Assistant

## Configuration

### Via Home Assistant UI
1. Go to Settings > Devices & Services
2. Click on "+ Add Integration"
3. Search for "Flavor of the Day"
4. Follow the configuration steps:
   - Select the provider (store chain)
   - Search for your location by city, state, or zip code
   - Select the specific location from the results
   - Optionally customize update interval (default: 30 minutes)
5. Click "Submit" to complete the setup

## Sensors

The integration creates a sensor with the following attributes:
- `name`: Current flavor of the day
- `description`: Flavor description
- `ingredients`: List of ingredients
- `allergens`: List of allergens
- `available_date`: Date when flavor is available
- `price`: Price information (if available)
- `nutrition_info`: Nutrition information (if available)
- `provider`: The provider name
- `location_id`: Location identifier
- `last_updated`: Timestamp of last update

## Supported Providers

- **Culver's**: Daily frozen custard flavor information
- **Kopp's**: Frozen custard flavor of the day
- **Oscar's**: Daily ice cream flavor
- **Leduc's**: Daily flavor information

## Troubleshooting

### Common Issues

1. **Location not found**: Make sure you're searching with the correct city name, state, or ZIP code. Some locations might not be available in the provider's system.

2. **No flavor data**: Some locations might not have updated their flavor of the day yet, or the store might be closed.

3. **Connection errors**: The integration relies on the provider's website or API. Network issues or website changes could affect functionality.

4. **Rate limiting**: If you're getting rate limit errors, try increasing the update interval in the configuration.

### Error Messages

- `no_locations_found`: No locations were found matching your search criteria
- `provider_error`: Error occurred communicating with the provider
- `connection_failed`: Could not connect to the location
- `network_error`: Network connectivity issue
- `unknown_error`: An unexpected error occurred

## Configuration Options

- **Provider**: Select the ice cream store chain (Culver's, Kopp's, Oscar's, Leduc's)
- **Location**: Search and select your desired store location
- **Update Interval**: How often to check for new flavors (5-1440 minutes, default: 30)
- **Custom Name**: Optional custom name for the sensor

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Development

To run this integration in development mode:

1. Clone the repository
2. Install dependencies: `./scripts/setup`
3. Start development Home Assistant instance: `./scripts/develop`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter issues with the integration, please create an issue in the GitHub repository with:
- Your Home Assistant version
- The provider and location you're using
- Steps to reproduce the issue
- Any relevant error messages from the logs
