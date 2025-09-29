# Flavor of the Day Home Assistant Integration

> [!NOTE]
> This project is actively maintained and provides stable functionality for tracking flavor of the day at supported locations.

**Flavor of the Day** is a Home Assistant custom integration that provides information about the daily flavor offerings from popular ice cream and frozen custard locations. The integration allows users to get notified when their favorite store's flavor of the day changes.

## Features

- **Multiple Supported Providers**: Track flavors from Culver's, Kopp's, Oscar's, and Goodberry's
- **Device Organization**: Each configured location creates a device with sensors organized under it
- **Rich Sensor Data**: Sensors include name, description, ingredients, allergens, pricing, nutrition info, and images
- **Dynamic Entity Pictures**: Displays flavor images when available (e.g., Culver's flavor images)
- **Configurable Update Intervals**: Customize how often flavors are checked (5-1440 minutes)
- **Options Flow**: Modify settings without removing and re-adding the integration
- **Custom Services**: Force refresh flavors using Home Assistant services
- **Robust Error Handling**: Comprehensive error handling and rate limiting to prevent provider issues

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

### After Configuration
After adding the integration, you can modify the update interval through the Options Flow:
1. Go to Settings > Devices & Services
2. Find your Flavor of the Day integration
3. Click the three dots menu and select "Settings"
4. Adjust the update interval as needed

## Services

The integration provides the following custom service:

### `flavor_of_the_day.force_refresh`
Force a refresh of the flavor of the day without waiting for the update interval to expire.

* **Service**: `flavor_of_the_day.force_refresh`
* **Fields**:
  * `entity_id` (string, required): The entity ID of the flavor sensor to refresh

*Example:*
```yaml
service: flavor_of_the_day.force_refresh
data:
  entity_id: sensor.flavor_of_the_day_culvers_location
```

## Sensors

The integration creates a sensor with the following attributes:
- `name`: Current flavor of the day
- `description`: Flavor description
- `ingredients`: List of ingredients
- `allergens`: List of allergens
- `available_date`: Date when flavor is available
- `price`: Price information (if available)
- `nutrition_info`: Nutrition information (if available)
- `image_url`: URL to flavor image (when available)
- `provider`: The provider name
- `location_id`: Location identifier
- `last_updated`: Timestamp of last update

## Supported Providers

- **Culver's**: Daily frozen custard flavor information with images
- **Kopp's**: Frozen custard flavor of the day
- **Oscar's**: Daily ice cream flavor
- **Goodberry's**: Daily frozen custard flavor information

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

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

For developers interested in adding new providers to support additional ice cream store chains, see our [Provider Documentation](PROVIDER_DOCS.md) for detailed instructions and implementation guidelines.

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
