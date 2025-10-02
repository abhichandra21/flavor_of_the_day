# Gemini Project: Flavor of the Day Home Assistant Integration

## Project Overview

This project is a Home Assistant custom integration called "Flavor of the Day". Its purpose is to fetch and display the daily flavor offerings from various ice cream and frozen custard locations. The integration is designed to be configurable through the Home Assistant UI, allowing users to select their preferred store and receive updates on the latest flavors.

The core of the integration is built in Python and relies on asynchronous web scraping to gather information from provider websites. Key technologies include:

*   **Python:** The primary programming language for the integration.
*   **Home Assistant Core:** The integration is built upon the Home Assistant framework, leveraging its entity model, configuration flow, and other APIs.
*   **aiohttp:** Used for making asynchronous HTTP requests to fetch data from provider websites.
*   **BeautifulSoup4 & lxml:** Used for parsing HTML and extracting flavor information from the scraped web pages.

The project is structured as a standard Home Assistant custom component, with the main logic located in the `custom_components/flavor_of_the_day` directory. This includes the main `__init__.py`, `sensor.py` for the sensor entity, `config_flow.py` for the UI-based configuration, and a `providers` subdirectory that contains the logic for scraping each specific store's website.

## Building and Running

### Setup

To set up the development environment, run the following script. This will create a Python virtual environment and install all necessary dependencies from `requirements.txt` and `requirements-dev.txt`.

```bash
./scripts/setup
```

### Running in Development

To run the integration in a development Home Assistant instance, use the `develop` script. This will start Home Assistant with the custom component loaded.

```bash
./scripts/develop
```

The Home Assistant instance will be available at `http://localhost:8123`.

### Testing

The project includes a test suite using `pytest`. To run the tests, including linting and code coverage, use the `test` script:

```bash
./scripts/test
```

## Development Conventions

*   **Linting:** The project uses `ruff` for linting. The linting rules are defined in the `.ruff.toml` file. The linting script is located at `./scripts/lint`.
*   **Testing:** Unit tests are located in the `tests/` directory. The test suite is run with `pytest`, and code coverage is generated for the `custom_components.flavor_of_the_day` module.
*   **Dependencies:** Runtime dependencies are listed in `requirements.txt` and also in `custom_components/flavor_of_the_day/manifest.json`. Development dependencies are in `requirements-dev.txt`.
*   **Providers:** Each supported store has its own module in the `custom_components/flavor_of_the_day/providers` directory. To add a new provider, a new file would be created in this directory, implementing the base provider class.
*   **Contribution:** The `CONTRIBUTING.md` file outlines the process for contributing to the project, which follows a standard fork-and-pull-request model.
