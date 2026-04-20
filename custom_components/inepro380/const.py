"""Constants for the inepro380 integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

DOMAIN = "inepro380"
MANUFACTURER = "inepro"
MODEL = "PRO380-Mod"
DEFAULT_NAME = "Inepro PRO380"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL_SECONDS = 30
DEFAULT_SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS)
MIN_SCAN_INTERVAL_SECONDS = 5

CONF_PROTOCOL = "protocol"
CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"
PROTOCOL_TCP = "tcp"

REDACTED_CONFIG = {"host"}
PLATFORMS: tuple[str, ...] = ("sensor",)


def get_scan_interval_seconds(
    data: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
) -> int:
    """Return the effective scan interval in seconds."""

    if options and CONF_SCAN_INTERVAL in options:
        return int(options[CONF_SCAN_INTERVAL])
    if data and CONF_SCAN_INTERVAL in data:
        return int(data[CONF_SCAN_INTERVAL])
    return DEFAULT_SCAN_INTERVAL_SECONDS


def get_scan_interval(
    data: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
) -> timedelta:
    """Return the effective scan interval as a `timedelta`."""

    return timedelta(seconds=get_scan_interval_seconds(data, options))


@dataclass(frozen=True, slots=True)
class RegisterBlock:
    """A contiguous Modbus register block."""

    start_address: int
    register_count: int


REGISTER_BLOCKS: tuple[RegisterBlock, ...] = (
    RegisterBlock(start_address=0x4000, register_count=0x20),
    RegisterBlock(start_address=0x5000, register_count=0x32),
    RegisterBlock(start_address=0x6000, register_count=0x4B),
)