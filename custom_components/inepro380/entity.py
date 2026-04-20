"""Base entity classes for inepro380."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import IneproDataUpdateCoordinator
from .descriptions import IneproSensorDescription


class IneproCoordinatorEntity(CoordinatorEntity[IneproDataUpdateCoordinator]):
    """Common entity behavior for all PRO380 entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IneproDataUpdateCoordinator,
        config_entry,
        description: IneproSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.entity_description = description
        serial_number = coordinator.serial_number or config_entry.unique_id or config_entry.entry_id
        self._attr_unique_id = f"{serial_number}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        metadata = self.coordinator.data.metadata if self.coordinator.data else None
        serial_number = (
            metadata.serial_number
            if metadata is not None
            else (self.config_entry.unique_id or self.config_entry.entry_id)
        )
        return DeviceInfo(
            identifiers={(DOMAIN, serial_number)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=self.config_entry.title,
            serial_number=serial_number,
            sw_version=metadata.software_version if metadata else None,
            hw_version=metadata.hardware_version if metadata else None,
        )