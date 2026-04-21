"""Description coverage tests for inepro380."""

from __future__ import annotations

from custom_components.inepro380.descriptions import (
    ENERGY_SENSORS,
    IDENTITY_SENSORS,
    MEASUREMENT_SENSORS,
    SENSOR_DESCRIPTIONS,
)


def test_all_read_ranges_are_described() -> None:
    """The integration should expose every readable register described in the map."""

    assert len(IDENTITY_SENSORS) == 25
    assert len(MEASUREMENT_SENSORS) == 25
    assert len(ENERGY_SENSORS) == 38
    assert len(SENSOR_DESCRIPTIONS) == 88


def test_all_keys_and_addresses_are_unique() -> None:
    """No two entities should share the same key or starting register."""

    keys = [description.key for description in SENSOR_DESCRIPTIONS]
    addresses = [description.address for description in SENSOR_DESCRIPTIONS]

    assert len(keys) == len(set(keys))
    assert len(addresses) == len(set(addresses))
