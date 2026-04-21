"""Client tests for inepro380."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from custom_components.inepro380.client import (
    IneproConnectionError,
    IneproModbusTcpClient,
)
from custom_components.inepro380.const import REGISTER_BLOCKS
from custom_components.inepro380.models import IneproConnectionParameters


class _FakeResponse:
    def __init__(self, registers, error: bool = False) -> None:
        self.registers = registers
        self._error = error

    def isError(self) -> bool:
        return self._error


def test_probe_device_reads_identity_block(raw_blocks) -> None:
    """Probing should decode identity metadata from the first block."""

    with patch("custom_components.inepro380.client.ModbusTcpClient") as client_cls:
        client = client_cls.return_value
        client.connect.return_value = True
        client.read_holding_registers.return_value = _FakeResponse(raw_blocks[0x4000])

        metadata = IneproModbusTcpClient(
            IneproConnectionParameters(host="127.0.0.1", port=502, slave_id=1)
        ).probe_device()

    assert metadata.serial_number == "22091039"
    client.read_holding_registers.assert_called_once_with(
        address=0x4000,
        count=0x20,
        device_id=1,
    )


def test_read_blocks_reads_each_configured_range(raw_blocks) -> None:
    """Block reads should preserve the configured block layout."""

    with patch("custom_components.inepro380.client.ModbusTcpClient") as client_cls:
        client = client_cls.return_value
        client.connect.return_value = True
        client.read_holding_registers.side_effect = [
            _FakeResponse(raw_blocks[0x4000]),
            _FakeResponse(raw_blocks[0x5000]),
            _FakeResponse(raw_blocks[0x6000]),
        ]

        result = IneproModbusTcpClient(
            IneproConnectionParameters(host="127.0.0.1", port=502, slave_id=1)
        ).read_blocks(REGISTER_BLOCKS)

    assert result[0x4000] == raw_blocks[0x4000]
    assert result[0x5000] == raw_blocks[0x5000]
    assert result[0x6000] == raw_blocks[0x6000]


def test_open_client_raises_when_connection_fails() -> None:
    """Connection failures should surface as integration-level errors."""

    with patch("custom_components.inepro380.client.ModbusTcpClient") as client_cls:
        client_cls.return_value.connect.return_value = False

        with pytest.raises(IneproConnectionError):
            IneproModbusTcpClient(
                IneproConnectionParameters(host="127.0.0.1", port=502, slave_id=1)
            ).read_holding_registers(address=0x4000, count=2)
