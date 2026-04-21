"""Sensor platform tests for inepro380."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.inepro380.const import (
    CONF_PROTOCOL,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DOMAIN,
    PROTOCOL_TCP,
)


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_setup_entry_creates_device_and_measurement_entities(hass, raw_blocks) -> None:
    """Setting up the integration should create one device and core sensors."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Inepro PRO380 22091039",
        data={
            CONF_PROTOCOL: PROTOCOL_TCP,
            CONF_HOST: "192.168.88.49",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
            CONF_SCAN_INTERVAL: 30,
        },
        unique_id="22091039",
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.inepro380.client.IneproModbusTcpClient.read_blocks",
        return_value=raw_blocks,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    device = dr.async_get(hass).async_get_device(identifiers={(DOMAIN, "22091039")})
    assert device is not None

    l1_voltage = hass.states.get("sensor.inepro_pro380_22091039_l1_voltage")
    assert l1_voltage is not None
    assert float(l1_voltage.state) == pytest.approx(234.300003)
    assert l1_voltage.attributes["unit_of_measurement"] == "V"

    serial_sensor = hass.states.get("sensor.inepro_pro380_22091039_serial_number")
    assert serial_sensor is None
