"""Config flow for inepro380."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant

from .client import IneproConnectionError, IneproModbusTcpClient
from .const import (
    CONF_PROTOCOL,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    MIN_SCAN_INTERVAL_SECONDS,
    PROTOCOL_TCP,
)
from .models import IneproConnectionParameters, IneproDeviceMetadata

_LOGGER = logging.getLogger(__name__)


async def async_validate_tcp_input(
    hass: HomeAssistant, data: dict[str, Any]
) -> IneproDeviceMetadata:
    """Validate TCP connection settings by probing the device."""

    client = IneproModbusTcpClient(
        IneproConnectionParameters(
            host=data[CONF_HOST],
            port=data[CONF_PORT],
            slave_id=data[CONF_SLAVE_ID],
        )
    )
    return await hass.async_add_executor_job(client.probe_device)


class IneproConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for inepro380."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow for this handler."""

        return IneproOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                metadata = await async_validate_tcp_input(self.hass, user_input)
            except IneproConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error while validating PRO380 settings")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(metadata.serial_number)
                self._abort_if_unique_id_configured()

                title = user_input.get(CONF_NAME) or metadata.default_name
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_PROTOCOL: PROTOCOL_TCP,
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                        CONF_SLAVE_ID: user_input[CONF_SLAVE_ID],
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=65535)
                    ),
                    vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=247)
                    ),
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL_SECONDS,
                    ): vol.All(
                        vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL_SECONDS)
                    ),
                    vol.Optional(CONF_NAME): str,
                }
            ),
            errors=errors,
        )


class IneproOptionsFlow(config_entries.OptionsFlow):
    """Handle inepro380 options."""

    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage polling options."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_scan_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self._config_entry.data.get(
                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS
            ),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=current_scan_interval,
                    ): vol.All(
                        vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL_SECONDS)
                    )
                }
            ),
        )