"""The Kachelmann Wetter component."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv

from .const import CONF_LATITUDE, CONF_LONGITUDE, DOMAIN, SUBENTRY_TYPE_LOCATION
from .coordinator import KmwDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)
PLATFORMS = [Platform.WEATHER, Platform.SENSOR]


@dataclass
class KmwRuntimeData:
    """Runtime data for the KMW integration."""

    coordinators: dict[str, KmwDataUpdateCoordinator] = field(default_factory=dict)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry to new version."""
    if config_entry.version > 2:  # noqa: PLR2004
        return False

    if config_entry.version == 1:
        _LOGGER.info("Migrating KMW config entry from V1 to V2")

        # Create a legacy subentry named "Kachelmann Wetter" so the device
        # name matches the old entity_id prefix (sensor.kachelmann_wetter_*)
        lat = hass.config.latitude
        lon = hass.config.longitude

        subentry = ConfigSubentry(
            data=MappingProxyType(
                {
                    CONF_LATITUDE: lat,
                    CONF_LONGITUDE: lon,
                }
            ),
            subentry_type=SUBENTRY_TYPE_LOCATION,
            title="Kachelmann Wetter",
            unique_id="zone.home",
        )
        hass.config_entries.async_add_subentry(config_entry, subentry)
        hass.config_entries.async_update_entry(config_entry, version=2)

        _LOGGER.info(
            "KMW migration: created location '%s', subentry_id=%s",
            subentry.title,
            subentry.subentry_id,
        )

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Kachelmann Wetter as config entry."""
    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    runtime_data = KmwRuntimeData()

    for subentry in config_entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_TYPE_LOCATION:
            continue
        coordinator = KmwDataUpdateCoordinator(hass, config_entry, subentry)
        await coordinator.async_config_entry_first_refresh()
        runtime_data.coordinators[subentry.subentry_id] = coordinator

    config_entry.runtime_data = runtime_data

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
