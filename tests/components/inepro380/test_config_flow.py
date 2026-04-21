"""Config flow tests for inepro380."""

from __future__ import annotations

from unittest.mock import patch

import pytest
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import selector
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.inepro380.client import IneproConnectionError
from custom_components.inepro380.const import CONF_SCAN_INTERVAL, CONF_SLAVE_ID, DOMAIN
from custom_components.inepro380.models import IneproDeviceMetadata


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_user_flow_creates_entry(hass, raw_blocks) -> None:
    """The user flow should validate the device and create a config entry."""

    with patch(
        "custom_components.inepro380.config_flow.async_validate_tcp_input",
        return_value=IneproDeviceMetadata(
            serial_number="22091039",
            default_name="Inepro PRO380 22091039",
            meter_code="0102",
            protocol_version="3.20",
            software_version="2.18",
            hardware_version="1.32",
        ),
    ), patch(
        "custom_components.inepro380.client.IneproModbusTcpClient.read_blocks",
        return_value=raw_blocks,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={
                CONF_HOST: "192.168.88.49",
                CONF_PORT: 502,
                CONF_SLAVE_ID: 1,
                CONF_SCAN_INTERVAL: 30,
                CONF_NAME: "Meter room",
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Meter room"
    assert result["data"][CONF_HOST] == "192.168.88.49"
    assert result["data"][CONF_PORT] == 502
    assert result["data"][CONF_SLAVE_ID] == 1
    assert result["data"][CONF_SCAN_INTERVAL] == 30


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_user_flow_uses_integer_box_for_slave_id(hass) -> None:
    """The user form should render slave ID as a boxed integer selector."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM

    slave_id_validator = next(
        value
        for key, value in result["data_schema"].schema.items()
        if isinstance(key, vol.Marker) and key.schema == CONF_SLAVE_ID
    )
    assert isinstance(slave_id_validator.validators[0], selector.NumberSelector)
    assert slave_id_validator.validators[0].config["mode"] == "box"


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_user_flow_shows_error_when_connection_fails(hass) -> None:
    """Connection failures should be presented as form errors."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    with patch(
        "custom_components.inepro380.config_flow.async_validate_tcp_input",
        side_effect=IneproConnectionError("cannot connect"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.88.49",
                CONF_PORT: 502,
                CONF_SLAVE_ID: 1,
                CONF_SCAN_INTERVAL: 30,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_user_flow_aborts_for_duplicate_serial(hass) -> None:
    """The flow should reject a device that is already configured."""

    existing_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Inepro PRO380 22091039",
        data={
            CONF_HOST: "192.168.88.49",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
            CONF_SCAN_INTERVAL: 30,
        },
        unique_id="22091039",
    )
    existing_entry.add_to_hass(hass)

    with patch(
        "custom_components.inepro380.config_flow.async_validate_tcp_input",
        return_value=IneproDeviceMetadata(
            serial_number="22091039",
            default_name="Inepro PRO380 22091039",
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={
                CONF_HOST: "192.168.88.49",
                CONF_PORT: 502,
                CONF_SLAVE_ID: 1,
                CONF_SCAN_INTERVAL: 30,
            },
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_reconfigure_flow_updates_tcp_settings(hass) -> None:
    """The reconfigure flow should update TCP connection settings."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Inepro PRO380 22091039",
        data={
            CONF_HOST: "192.168.88.49",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
            CONF_SCAN_INTERVAL: 30,
        },
        unique_id="22091039",
    )
    entry.add_to_hass(hass)

    with patch.object(hass.config_entries, "async_schedule_reload") as mock_reload:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )

        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "reconfigure"

        with patch(
            "custom_components.inepro380.config_flow.async_validate_tcp_input",
            return_value=IneproDeviceMetadata(
                serial_number="22091039",
                default_name="Inepro PRO380 22091039",
            ),
        ):
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {
                    CONF_HOST: "192.168.88.50",
                    CONF_PORT: 1502,
                    CONF_SLAVE_ID: 7,
                },
            )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_HOST] == "192.168.88.50"
    assert entry.data[CONF_PORT] == 1502
    assert entry.data[CONF_SLAVE_ID] == 7
    mock_reload.assert_called_once_with(entry.entry_id)


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_reconfigure_flow_rejects_different_device(hass) -> None:
    """The reconfigure flow should reject switching to a different meter."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Inepro PRO380 22091039",
        data={
            CONF_HOST: "192.168.88.49",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
            CONF_SCAN_INTERVAL: 30,
        },
        unique_id="22091039",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )

    with patch(
        "custom_components.inepro380.config_flow.async_validate_tcp_input",
        return_value=IneproDeviceMetadata(
            serial_number="99999999",
            default_name="Inepro PRO380 99999999",
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.88.51",
                CONF_PORT: 502,
                CONF_SLAVE_ID: 9,
            },
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "different_device"
    assert entry.data[CONF_HOST] == "192.168.88.49"
    assert entry.data[CONF_PORT] == 502
    assert entry.data[CONF_SLAVE_ID] == 1


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_options_flow_updates_scan_interval(hass) -> None:
    """The options flow should allow changing the polling interval."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Inepro PRO380 22091039",
        data={
            CONF_HOST: "192.168.88.49",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
            CONF_SCAN_INTERVAL: 30,
        },
        unique_id="22091039",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_SCAN_INTERVAL: 90},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_SCAN_INTERVAL: 90}
