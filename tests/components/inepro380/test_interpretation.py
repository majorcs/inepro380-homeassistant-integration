"""Tests for interpreted device details."""

from __future__ import annotations

from custom_components.inepro380.interpretation import interpret_device_details


def test_interpret_device_details_maps_documented_values() -> None:
    """Documented enum-like values should gain stable meanings."""

    interpreted = interpret_device_details(
        {
            "baud_rate": 9600,
            "parity_setting": 1,
            "combination_code": 10,
            "current_direction": "1F",
            "l2_current_direction": "2R",
            "quadrant": 4,
            "current_transformer_mode": 5,
            "current_transformer_ratio": 200,
            "disconnect_counter": 12,
        }
    )

    assert interpreted["baud_rate"]["label"] == "9600 baud"
    assert interpreted["baud_rate"]["is_default_modbus"] is True
    assert interpreted["parity_setting"]["label"] == "even"
    assert interpreted["combination_code"]["code"] == "C-10"
    assert interpreted["combination_code"]["locked_after_set"] is True
    assert interpreted["current_direction"]["label"] == "L1 forward"
    assert interpreted["l2_current_direction"]["direction"] == "reverse"
    assert interpreted["quadrant"]["roman"] == "IV"
    assert interpreted["current_transformer_mode"]["secondary_current_a"] == 5
    assert interpreted["current_transformer_ratio"]["label"] == "200/5 A"
    assert interpreted["disconnect_counter"]["meaning"].startswith("Number of times")


def test_interpret_device_details_surfaces_unknown_values_explicitly() -> None:
    """Undocumented values should stay visible instead of being silently mapped."""

    interpreted = interpret_device_details(
        {
            "parity_setting": 9,
            "combination_code": 99,
            "current_direction": "ZX",
            "quadrant": 9,
            "current_transformer_mode": 2,
            "current_transformer_ratio": 0,
        }
    )

    assert interpreted["parity_setting"]["recognized"] is False
    assert interpreted["parity_setting"]["label"] == "unknown (9)"
    assert interpreted["combination_code"]["label"] == "unknown (99)"
    assert interpreted["current_direction"]["label"] == "unknown (ZX)"
    assert interpreted["quadrant"]["label"] == "unknown (9)"
    assert interpreted["current_transformer_mode"]["label"] == "unknown (2)"
    assert interpreted["current_transformer_ratio"]["label"] == "not configured"
