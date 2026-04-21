"""Constant/helper tests for inepro380."""

from __future__ import annotations

from datetime import timedelta

from custom_components.inepro380.const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    get_scan_interval,
    get_scan_interval_seconds,
)


def test_scan_interval_defaults_to_30_seconds() -> None:
    """The fallback polling interval should be 30 seconds."""

    assert get_scan_interval_seconds() == DEFAULT_SCAN_INTERVAL_SECONDS
    assert get_scan_interval() == timedelta(seconds=30)


def test_scan_interval_prefers_options_over_data() -> None:
    """Options should override the originally stored config data."""

    data = {CONF_SCAN_INTERVAL: 30}
    options = {CONF_SCAN_INTERVAL: 90}

    assert get_scan_interval_seconds(data, options) == 90
    assert get_scan_interval(data, options) == timedelta(seconds=90)


def test_scan_interval_reads_data_when_options_absent() -> None:
    """Stored config data should be used when no override is present."""

    data = {CONF_SCAN_INTERVAL: 45}

    assert get_scan_interval_seconds(data, None) == 45
    assert get_scan_interval(data, None) == timedelta(seconds=45)