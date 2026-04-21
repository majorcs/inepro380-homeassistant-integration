"""Diagnostics support for inepro380."""

from __future__ import annotations

from dataclasses import asdict

from homeassistant.components.diagnostics import async_redact_data

from .const import REDACTED_CONFIG


async def async_get_config_entry_diagnostics(hass, config_entry):
    """Return diagnostics for a config entry."""

    del hass
    coordinator = config_entry.runtime_data
    payload = {
        "entry": dict(config_entry.data),
        "metadata": asdict(coordinator.data.metadata) if coordinator.data else None,
        "interpreted": dict(coordinator.data.interpreted) if coordinator.data else None,
        "values": dict(coordinator.data.values) if coordinator.data else None,
        "raw_blocks": (
            {
                f"0x{start_address:04X}": registers
                for start_address, registers in coordinator.data.raw_blocks.items()
            }
            if coordinator.data
            else None
        ),
    }
    return async_redact_data(payload, REDACTED_CONFIG)
