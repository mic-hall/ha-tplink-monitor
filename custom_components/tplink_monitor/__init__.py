import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up TP-Link Monitor from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Store configuration in hass.data
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Reload if needed
    hass.async_create_task(hass.config_entries.async_forward_entry_setups(entry, "sensor"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Remove the TP-Link integration."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
