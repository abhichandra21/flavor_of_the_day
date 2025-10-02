"""Sensor platform for Flavor of the Day integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FlavorUpdateCoordinator


SENSOR_DESCRIPTION = SensorEntityDescription(
    key="flavor_of_the_day",
    translation_key="flavor_of_the_day",
    icon="mdi:ice-cream",
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Flavor of the Day sensor."""
    runtime_data = entry.runtime_data
    coordinator = runtime_data.coordinator

    async_add_entities([FlavorOfTheDaySensor(coordinator, SENSOR_DESCRIPTION)])


class FlavorOfTheDaySensor(CoordinatorEntity, SensorEntity):
    """Sensor for today's flavor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FlavorUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.coordinator.config_entry.data.get("name", "Flavor of the Day")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self.coordinator.config_entry.data.get("name", "Flavor of the Day"),
            manufacturer=self.coordinator.provider.provider_name,
            model="Flavor of the Day Sensor",
        )

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "Unknown"
        return self.coordinator.data.name

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        flavor = self.coordinator.data
        attributes: dict[str, Any] = {
            "name": flavor.name,
            "provider": self.coordinator.provider.provider_name,
            "location_id": self.coordinator.location_id,
        }

        if flavor.description:
            attributes["description"] = flavor.description

        if flavor.ingredients:
            attributes["ingredients"] = flavor.ingredients

        if flavor.allergens:
            attributes["allergens"] = flavor.allergens

        if flavor.price:
            attributes["pricing"] = flavor.price

        if flavor.available_date:
            attributes["available_date"] = flavor.available_date.isoformat()

        if flavor.image_url:
            attributes["image_url"] = flavor.image_url

        return attributes
