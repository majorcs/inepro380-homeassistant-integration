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


def test_manual_english_names_match_selected_registers() -> None:
    """Entity labels should follow the original English manual naming."""

    names_by_address = {
        description.address: description.name
        for description in SENSOR_DESCRIPTIONS
    }

    assert names_by_address[0x400B] == "Meter amps"
    assert names_by_address[0x400C] == "CT ratio"
    assert names_by_address[0x400D] == "S0 output rate"
    assert names_by_address[0x4016] == "Power down counter"
    assert names_by_address[0x4017] == "Present quadrant"
    assert names_by_address[0x401F] == "CT mode"
    assert names_by_address[0x5012] == "Total active power"
    assert names_by_address[0x501A] == "Total reactive power"
    assert names_by_address[0x5022] == "Total apparent power"
    assert names_by_address[0x6000] == "Total active energy"
    assert names_by_address[0x600C] == "Forward active energy"
    assert names_by_address[0x6018] == "Reverse active energy"
    assert names_by_address[0x6030] == "Forward reactive energy"
    assert names_by_address[0x603C] == "Reverse reactive energy"
    assert names_by_address[0x6049] == "Resettable day counter"
