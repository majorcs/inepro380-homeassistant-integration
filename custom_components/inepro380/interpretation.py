"""Interpret raw device values into support-friendly diagnostics details."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_MODBUS_BAUD_RATES = (300, 600, 1200, 2400, 4800, 9600)
_PARITY_BY_CODE = {
    1: "even",
    2: "none",
    3: "odd",
}
_COMBINATION_DETAILS = {
    1: {
        "code": "C-01",
        "label": "Forward only",
        "total_active_energy_formula": "forward_only",
    },
    4: {
        "code": "C-04",
        "label": "Reverse only",
        "total_active_energy_formula": "reverse_only",
    },
    5: {
        "code": "C-05",
        "label": "Forward + Reverse",
        "total_active_energy_formula": "forward_plus_reverse",
    },
    6: {
        "code": "C-06",
        "label": "Reverse - Forward",
        "total_active_energy_formula": "reverse_minus_forward",
    },
    9: {
        "code": "C-09",
        "label": "Forward - Reverse",
        "total_active_energy_formula": "forward_minus_reverse",
    },
    10: {
        "code": "C-10",
        "label": "Forward - Reverse",
        "total_active_energy_formula": "forward_minus_reverse",
        "locked_after_set": True,
    },
    11: {
        "code": "C-11",
        "label": "Forward - Reverse",
        "total_active_energy_formula": "forward_minus_reverse",
    },
}
_PHASE_BY_CODE = {
    "1": "L1",
    "2": "L2",
    "3": "L3",
}
_DIRECTION_BY_CODE = {
    "F": "forward",
    "R": "reverse",
}
_QUADRANT_ROMAN = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
}


def interpret_device_details(values: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Return structured interpretations for selected decoded register values."""

    interpreted: dict[str, dict[str, Any]] = {}

    if "baud_rate" in values:
        interpreted["baud_rate"] = _interpret_baud_rate(values["baud_rate"])
    if "parity_setting" in values:
        interpreted["parity_setting"] = _interpret_parity_setting(values["parity_setting"])
    if "combination_code" in values:
        interpreted["combination_code"] = _interpret_combination_code(
            values["combination_code"]
        )
    if "disconnect_counter" in values:
        interpreted["disconnect_counter"] = {
            "meaning": "Number of times the meter has been turned off",
        }
    if "current_transformer_mode" in values:
        interpreted["current_transformer_mode"] = _interpret_ct_mode(
            values["current_transformer_mode"]
        )
    if "current_transformer_ratio" in values:
        interpreted["current_transformer_ratio"] = _interpret_ct_ratio(
            values["current_transformer_ratio"],
            values.get("current_transformer_mode"),
        )

    for key in ("current_direction", "l2_current_direction", "l3_current_direction"):
        if key in values:
            interpreted[key] = _interpret_current_direction(values[key])

    for key in ("quadrant", "l1_quadrant", "l2_quadrant", "l3_quadrant"):
        if key in values:
            interpreted[key] = _interpret_quadrant(values[key])

    return interpreted


def _interpret_baud_rate(value: Any) -> dict[str, Any]:
    if not isinstance(value, int):
        return {"label": f"unknown ({value})", "recognized": False}

    recognized = value in _MODBUS_BAUD_RATES
    return {
        "label": f"{value} baud" if recognized else f"unknown ({value})",
        "recognized": recognized,
        "allowed_values": list(_MODBUS_BAUD_RATES),
        "is_default_modbus": value == 9600,
    }


def _interpret_parity_setting(value: Any) -> dict[str, Any]:
    label = _PARITY_BY_CODE.get(value)
    if label is None:
        return {
            "label": f"unknown ({value})",
            "recognized": False,
            "allowed_values": ["even", "none", "odd"],
        }

    return {
        "label": label,
        "recognized": True,
        "allowed_values": ["even", "none", "odd"],
        "is_default_modbus": label == "even",
    }


def _interpret_combination_code(value: Any) -> dict[str, Any]:
    details = _COMBINATION_DETAILS.get(value)
    if details is None:
        return {
            "label": f"unknown ({value})",
            "recognized": False,
            "allowed_values": sorted(_COMBINATION_DETAILS),
        }

    return {
        **details,
        "recognized": True,
        "allowed_values": sorted(_COMBINATION_DETAILS),
    }


def _interpret_current_direction(value: Any) -> dict[str, Any]:
    if not isinstance(value, str) or len(value) != 2:
        return {"label": f"unknown ({value})", "recognized": False}

    phase = _PHASE_BY_CODE.get(value[0])
    direction = _DIRECTION_BY_CODE.get(value[1])
    if phase is None or direction is None:
        return {"label": f"unknown ({value})", "recognized": False}

    return {
        "label": f"{phase} {direction}",
        "recognized": True,
        "phase": phase,
        "direction": direction,
    }


def _interpret_quadrant(value: Any) -> dict[str, Any]:
    roman = _QUADRANT_ROMAN.get(value)
    if roman is None:
        return {"label": f"unknown ({value})", "recognized": False}

    return {
        "label": f"Quadrant {roman}",
        "recognized": True,
        "roman": roman,
    }


def _interpret_ct_mode(value: Any) -> dict[str, Any]:
    if value in (1, 5):
        return {
            "label": f"{value} A secondary",
            "recognized": True,
            "secondary_current_a": value,
            "allowed_values": [1, 5],
        }

    return {
        "label": f"unknown ({value})",
        "recognized": False,
        "allowed_values": [1, 5],
    }


def _interpret_ct_ratio(value: Any, ct_mode: Any) -> dict[str, Any]:
    if not isinstance(value, int):
        return {"label": f"unknown ({value})", "recognized": False}

    details: dict[str, Any] = {
        "recognized": True,
        "configured": value > 0,
    }
    if value <= 0:
        details["label"] = "not configured"
        return details

    if ct_mode in (1, 5):
        details["label"] = f"{value}/{ct_mode} A"
        details["primary_current_a"] = value
        details["secondary_current_a"] = ct_mode
        return details

    details["label"] = str(value)
    details["primary_current_a"] = value
    return details
