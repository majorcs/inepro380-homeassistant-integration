"""Shared fixtures for inepro380 tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(name="device_snapshot")
def fixture_device_snapshot() -> dict[str, dict[str, int | list[int]]]:
    """Load the live-device snapshot captured for offline tests."""

    fixture_path = Path(__file__).resolve().parents[2] / "fixtures" / "device_snapshot.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


@pytest.fixture(name="raw_blocks")
def fixture_raw_blocks(device_snapshot) -> dict[int, list[int]]:
    """Return raw block data keyed by numeric start address."""

    return {
        int(block_name, 16): block_payload["registers"]
        for block_name, block_payload in device_snapshot.items()
    }
