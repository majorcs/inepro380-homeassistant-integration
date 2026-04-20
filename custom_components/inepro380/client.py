"""Synchronous Modbus TCP client helpers for inepro380."""

from __future__ import annotations

from collections.abc import Iterable

from pymodbus.client import ModbusTcpClient

from .const import RegisterBlock
from .decoder import parse_identity_metadata
from .models import IneproConnectionParameters, IneproDeviceMetadata


class IneproConnectionError(RuntimeError):
    """Raised when the meter cannot be reached or decoded."""


class IneproModbusTcpClient:
    """Thin synchronous wrapper around `pymodbus` for the PRO380."""

    def __init__(self, parameters: IneproConnectionParameters) -> None:
        self._parameters = parameters

    def probe_device(self) -> IneproDeviceMetadata:
        """Read the identity block and return decoded device metadata."""

        identity_block = self.read_holding_registers(address=0x4000, count=0x20)
        return parse_identity_metadata(identity_block)

    def read_blocks(self, blocks: Iterable[RegisterBlock]) -> dict[int, list[int]]:
        """Read multiple contiguous register blocks in one TCP session."""

        result: dict[int, list[int]] = {}
        client = self._open_client()
        try:
            for block in blocks:
                response = client.read_holding_registers(
                    address=block.start_address,
                    count=block.register_count,
                    device_id=self._parameters.slave_id,
                )
                if response.isError():
                    raise IneproConnectionError(
                        f"Failed to read holding registers at 0x{block.start_address:04X}: {response}"
                    )
                result[block.start_address] = list(response.registers)
        finally:
            client.close()

        return result

    def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Read a single contiguous holding-register range."""

        client = self._open_client()
        try:
            response = client.read_holding_registers(
                address=address,
                count=count,
                device_id=self._parameters.slave_id,
            )
            if response.isError():
                raise IneproConnectionError(
                    f"Failed to read holding registers at 0x{address:04X}: {response}"
                )
            return list(response.registers)
        finally:
            client.close()

    def _open_client(self) -> ModbusTcpClient:
        client = ModbusTcpClient(
            host=self._parameters.host,
            port=self._parameters.port,
            timeout=3,
        )
        if not client.connect():
            raise IneproConnectionError(
                f"Unable to connect to {self._parameters.host}:{self._parameters.port}"
            )
        return client