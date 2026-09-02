"""Manifest tests for inepro380."""

from __future__ import annotations

import json
from pathlib import Path

from packaging.requirements import Requirement


def test_pymodbus_requirement_accepts_homeassistant_managed_versions() -> None:
    """The dependency range should not conflict with supported Home Assistant pins."""

    manifest_path = (
        Path(__file__).parents[3]
        / "custom_components"
        / "inepro380"
        / "manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requirements = [Requirement(value) for value in manifest["requirements"]]
    pymodbus = next(item for item in requirements if item.name == "pymodbus")

    assert pymodbus.specifier.contains("3.11.2")
    assert pymodbus.specifier.contains("3.13.1")
    assert pymodbus.specifier.contains("3.15.0")
    assert not pymodbus.specifier.contains("4.0.0")
