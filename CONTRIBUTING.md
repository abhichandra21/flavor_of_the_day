# Contribution guidelines

Contributing to the Flavor of the Day integration should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Adding support for new ice cream store providers

## Github is used for everything

Github is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've added new functionality, update the documentation.
3. Make sure your code lints (using `./scripts/lint`).
4. Test your contribution using `./scripts/develop`.
5. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [ruff](https://github.com/charliermarsh/ruff) to make sure the code follows the style. Run `./scripts/lint` to format and check your code.

## Adding New Provider Support

The integration follows a provider pattern that makes it easy to add support for new ice cream store chains. To add a new provider:

1. Create a new provider class in `custom_components/flavor_of_the_day/providers/` that inherits from `BaseFlavorProvider`
2. Implement the required abstract methods: `search_locations()`, `get_location_by_id()`, `get_current_flavor()`, and `test_connection()`
3. Add your provider class to the `PROVIDER_CLASSES` dictionary in `__init__.py`
4. Add your provider to the configuration flow in `config_flow.py`

## Test your code modification

This custom component comes with a development environment that's easy to launch
if you use Visual Studio Code. With this environment you will have a stand alone
Home Assistant instance running and already configured with the included
[`configuration.yaml`](./config/configuration.yaml)
file.

Start the development environment with: `./scripts/develop`

## Development Commands

- `./scripts/setup`: Install Python dependencies
- `./scripts/lint`: Format and lint code with ruff
- `./scripts/develop`: Start Home Assistant with this integration loaded

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
