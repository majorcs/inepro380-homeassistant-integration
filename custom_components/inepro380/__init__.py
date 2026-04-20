"""The inepro380 integration."""

from __future__ import annotations

try:
    from homeassistant.helpers import config_validation as cv
except ImportError:  # pragma: no cover
    cv = None

from .const import CONF_SLAVE_ID, DOMAIN, PLATFORMS, get_scan_interval

CONFIG_SCHEMA = (
    cv.config_entry_only_config_schema(DOMAIN) if cv is not None else None
)


async def async_setup(hass, config) -> bool:
    """Set up the integration domain."""

    del config
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry) -> bool:
    """Set up inepro380 from a config entry."""

    from homeassistant.const import CONF_HOST, CONF_PORT
    from .client import IneproModbusTcpClient
    from .coordinator import IneproDataUpdateCoordinator
    from .models import IneproConnectionParameters

    client = IneproModbusTcpClient(
        IneproConnectionParameters(
            host=config_entry.data[CONF_HOST],
            port=config_entry.data[CONF_PORT],
            slave_id=config_entry.data[CONF_SLAVE_ID],
        )
    )
    coordinator = IneproDataUpdateCoordinator(
        hass,
        client,
        update_interval=get_scan_interval(config_entry.data, config_entry.options),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    config_entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def async_unload_entry(hass, config_entry) -> bool:
    """Unload a config entry."""

    unloaded = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(config_entry.entry_id, None)
    return unloaded