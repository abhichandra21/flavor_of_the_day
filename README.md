# Flavor of the Day

Flavor of the Day is a Home Assistant custom integration that provides information about the daily flavor offerings from popular ice cream and frozen custard locations. Get notified when your favorite store's flavor of the day changes!

## Features

- Supports multiple ice cream store chains (Culver's, Kopp's, Oscar's, Leduc's)
- Real-time flavor information with rich attributes
- Configurable update intervals
- Easy setup through Home Assistant's configuration flow

## Supported Providers

- Culver's: Daily frozen custard flavor information
- Kopp's: Frozen custard flavor of the day
- Oscar's: Daily ice cream flavor
- Leduc's: Daily flavor information

## Installation

### Manual Installation

1. Using the tool of choice open the Home Assistant configuration directory (Where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory there, you need to create it.
3. Download the latest release from the [releases page](../../releases).
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

## What?

This repository contains multiple files, here is a overview:

File | Purpose | Documentation
-- | -- | --
`.devcontainer.json` | Used for development/testing with Visual Studio Code. | [Documentation](https://code.visualstudio.com/docs/remote/containers)
`.github/ISSUE_TEMPLATE/*.yml` | Templates for the issue tracker | [Documentation](https://help.github.com/en/github/building-a-strong-community/configuring-issue-templates-for-your-repository)
`custom_components/flavor_of_the_day/*` | Integration files, this is where everything happens. | [Documentation](https://developers.home-assistant.io/docs/creating_component_index)
`CONTRIBUTING.md` | Guidelines on how to contribute. | [Documentation](https://help.github.com/en/github/building-a-strong-community/setting-guidelines-for-repository-contributors)
`LICENSE` | The license file for the project. | [Documentation](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/licensing-a-repository)
`README.md` | The file you are reading now, should contain info about the integration, installation and configuration instructions. | [Documentation](https://help.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax)
`requirements.txt` | Python packages used for development/lint/testing this integration. | [Documentation](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

## Next steps

These are some next steps you may want to look into:
- Add tests to your integration, [`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) can help you get started.
- Share your integration on the [Home Assistant Community Forum](https://community.home-assistant.io/).
- Submit your integration to [HACS](https://hacs.xyz/docs/publish/start).
