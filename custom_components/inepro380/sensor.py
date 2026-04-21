"""Sensor platform for inepro380."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .descriptions import SENSOR_DESCRIPTIONS, IneproSensorDescription
from .entity import IneproCoordinatorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up inepro380 sensors from a config entry."""

    del hass
    coordinator = config_entry.runtime_data
    async_add_entities(
        IneproSensor(coordinator, config_entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class IneproSensor(IneproCoordinatorEntity, SensorEntity):
    """Representation of a single PRO380 sensor entity."""

    entity_description: IneproSensorDescription

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.values.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict[str, str | int]:
        attributes: dict[str, str | int | dict[str, object]] = {
            "register_address": f"0x{self.entity_description.address:04X}",
            "register_count": self.entity_description.register_count,
        }
        if self.coordinator.data is not None:
            interpreted = self.coordinator.data.interpreted.get(self.entity_description.key)
            if interpreted:
                attributes["interpreted"] = interpreted
        return attributes
