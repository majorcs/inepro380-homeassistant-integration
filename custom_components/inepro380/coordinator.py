"""Data coordinator for inepro380."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import IneproConnectionError, IneproModbusTcpClient
from .const import DOMAIN, REGISTER_BLOCKS
from .decoder import parse_identity_metadata
from .descriptions import SENSOR_DESCRIPTIONS
from .models import IneproSnapshot

_LOGGER = logging.getLogger(__name__)


def _extract_registers(
    raw_blocks: dict[int, list[int]], address: int, register_count: int
) -> list[int]:
    """Extract a register slice from the fetched block dictionary."""

    for block_start, registers in raw_blocks.items():
        offset = address - block_start
        if offset < 0:
            continue
        block_end = block_start + len(registers)
        if address + register_count <= block_end:
            return registers[offset : offset + register_count]

    raise KeyError(f"Register range 0x{address:04X}/len={register_count} not present")


class IneproDataUpdateCoordinator(DataUpdateCoordinator[IneproSnapshot]):
    """Coordinator responsible for fetching and decoding device data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: IneproModbusTcpClient,
        update_interval,
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self._client = client

    async def _async_update_data(self) -> IneproSnapshot:
        try:
            raw_blocks = await self.hass.async_add_executor_job(
                self._client.read_blocks, REGISTER_BLOCKS
            )
        except IneproConnectionError as err:
            raise UpdateFailed(str(err)) from err

        values: dict[str, object] = {}
        for description in SENSOR_DESCRIPTIONS:
            registers = _extract_registers(
                raw_blocks, description.address, description.register_count
            )
            values[description.key] = description.decoder(registers)

        metadata = parse_identity_metadata(raw_blocks[0x4000])
        return IneproSnapshot(values=values, raw_blocks=raw_blocks, metadata=metadata)

    @property
    def serial_number(self) -> str | None:
        """Return the currently known serial number."""

        if self.data is None:
            return None
        return self.data.metadata.serial_number