"""Shared models for the inepro380 integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class IneproConnectionParameters:
    """Connection parameters for a single PRO380 device."""

    host: str
    port: int
    slave_id: int


@dataclass(slots=True)
class IneproDeviceMetadata:
    """Device-level metadata decoded from the identity register block."""

    serial_number: str
    default_name: str
    meter_code: str | None = None
    protocol_version: str | None = None
    software_version: str | None = None
    hardware_version: str | None = None


@dataclass(slots=True)
class IneproSnapshot:
    """A single decoded snapshot for one meter."""

    values: dict[str, Any]
    raw_blocks: dict[int, list[int]]
    metadata: IneproDeviceMetadata