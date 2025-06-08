"""The Helty CMV integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .cmv import HeltyCMV
from .coordinator import HeltyDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.FAN, Platform.SWITCH, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Helty CMV from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    cmv_device = HeltyCMV(entry.data[CONF_HOST], entry.data[CONF_PORT])

    coordinator = HeltyDataUpdateCoordinator(hass, device=cmv_device)

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        raise

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok