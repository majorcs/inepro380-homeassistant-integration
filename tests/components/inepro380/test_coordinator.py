"""Coordinator tests for inepro380."""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.inepro380.client import IneproConnectionError
from custom_components.inepro380.coordinator import (
    IneproDataUpdateCoordinator,
    _extract_registers,
)


def test_extract_registers_returns_slice(raw_blocks) -> None:
    """Register extraction should return the requested contiguous slice."""

    assert _extract_registers(raw_blocks, 0x5002, 2) == raw_blocks[0x5000][2:4]


def test_extract_registers_raises_for_missing_range(raw_blocks) -> None:
    """Missing ranges should raise a `KeyError`."""

    with pytest.raises(KeyError):
        _extract_registers(raw_blocks, 0x7000, 1)


@pytest.mark.asyncio
async def test_coordinator_wraps_connection_errors(hass) -> None:
    """Transport failures should become `UpdateFailed`."""

    coordinator = IneproDataUpdateCoordinator(
        hass,
        SimpleNamespace(read_blocks=lambda _: (_ for _ in ()).throw(IneproConnectionError("boom"))),
        update_interval=timedelta(seconds=30),
    )

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()