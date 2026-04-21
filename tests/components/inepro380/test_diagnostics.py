"""Diagnostics tests for inepro380."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from custom_components.inepro380.decoder import parse_identity_metadata
from custom_components.inepro380.diagnostics import async_get_config_entry_diagnostics
from custom_components.inepro380.models import IneproSnapshot


@pytest.mark.asyncio
async def test_diagnostics_redacts_host_and_includes_snapshot(raw_blocks) -> None:
    """Diagnostics should include decoded data while redacting the host."""

    snapshot = IneproSnapshot(
        values={"serial_number": "22091039", "voltage": 0.0},
        raw_blocks=raw_blocks,
        metadata=parse_identity_metadata(raw_blocks[0x4000]),
    )
    config_entry = SimpleNamespace(
        data={"host": "192.168.88.49", "port": 502, "scan_interval": 30},
        runtime_data=SimpleNamespace(data=snapshot),
    )

    diagnostics = await async_get_config_entry_diagnostics(None, config_entry)

    assert diagnostics["entry"]["host"] == "**REDACTED**"
    assert diagnostics["metadata"]["serial_number"] == "22091039"
    assert diagnostics["values"]["serial_number"] == "22091039"
    assert "0x4000" in diagnostics["raw_blocks"]