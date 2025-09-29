from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import FlavorUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


# Entity descriptions for declarative entity definitions
SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(
        key="flavor_of_the_day",
        name="Flavor of the Day",
        icon="mdi:ice-cream",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        FlavorOfTheDaySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in SENSOR_DESCRIPTIONS
    )


class FlavorOfTheDaySensor(CoordinatorEntity[FlavorUpdateCoordinator], SensorEntity):
    """Flavor of the Day sensor."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: FlavorUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description

        # Use config entry ID for unique ID (blueprint pattern)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

        # Get custom name from config or use default
        custom_name = coordinator.config_entry.data.get("name")
        if custom_name:
            self._attr_name = custom_name
        else:
            self._attr_name = entity_description.name

    @property
    def native_value(self) -> str:
        """Return the current flavor name."""
        if self.coordinator.data:
            return self.coordinator.data.name
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional flavor information."""
        if not self.coordinator.data:
            return {}

        attrs = self.coordinator.data.to_dict()
        attrs.update(
            {
                "provider": self.coordinator.provider.provider_name,
                "location_id": self.coordinator.location_id,
                "last_updated": self.coordinator.last_update_success,
            }
        )
        return attrs

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for grouping."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self._attr_name,
            manufacturer=self.coordinator.provider.provider_name,
            model="Flavor of the Day Sensor",
            configuration_url=None,
        )
