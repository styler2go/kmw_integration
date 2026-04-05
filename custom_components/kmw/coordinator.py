"""DataUpdateCoordinator for Kachelmann Wetter integration."""

import asyncio
import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_API_KEY,
    CONF_FORECAST,
    CONF_FORECAST_DEFAULT,
    DOMAIN,
    UPDATE_INTERVAL,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)

API_BASE = "https://api.kachelmannwetter.com/v02"


class KmwDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Kachelmann Wetter data for one location."""

    HTTP_OK = 200
    HTTP_OK_MAX = 299

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        subentry: ConfigSubentry,
    ) -> None:
        """Initialize Kachelmann Wetter data updater for a single location."""
        self._config_entry: ConfigEntry = config_entry
        self._clientsession: ClientSession = async_get_clientsession(hass)
        self._api_key: str = config_entry.data[CONF_API_KEY]

        self._latitude: float = subentry.data["latitude"]
        self._longitude: float = subentry.data["longitude"]
        self._location_name: str = subentry.title

        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=self._location_name,
            manufacturer="Kachelmann Wetter",
            model="Weather API",
            entry_type=DeviceEntryType.SERVICE,
        )

        _LOGGER.debug(
            "Checking for new data for %s (%s, %s) every %s",
            self._location_name,
            self._latitude,
            self._longitude,
            UPDATE_INTERVAL,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{subentry.subentry_id}",
            update_interval=UPDATE_INTERVAL,
        )

    @property
    def location_name(self) -> str:
        """Return the location name."""
        return self._location_name

    @property
    def latitude(self) -> float:
        """Return the latitude."""
        return self._latitude

    @property
    def longitude(self) -> float:
        """Return the longitude."""
        return self._longitude

    async def _async_get_json(
        self, url: str, *, raise_on_error: bool = False
    ) -> dict | None:
        """Fetch JSON from the API."""
        headers = {"Accept": "application/json", "X-API-Key": self._api_key}
        response = await self._clientsession.get(url, headers=headers)
        if self.HTTP_OK <= response.status <= self.HTTP_OK_MAX:
            return await response.json(content_type=None)
        if raise_on_error:
            msg = f"Unexpected status code {response.status} from {url}."
            raise UpdateFailed(msg)
        return None

    async def _async_update_data(self) -> dict:
        """Fetch data from Kachelmann Wetter API."""
        try:
            conf_forecast = self._config_entry.options.get(
                CONF_FORECAST, CONF_FORECAST_DEFAULT
            )

            if not conf_forecast:
                return {
                    "forecast": None,
                    "forecast_hourly": None,
                    "forecast_hourly_3h": None,
                    "current": None,
                }

            lat = self._latitude
            lon = self._longitude
            (
                forecast_data,
                forecast_hourly,
                forecast_hourly_3h,
                current_weather,
            ) = await asyncio.gather(
                self._async_get_json(
                    f"{API_BASE}/forecast/{lat}/{lon}/trend14days",
                    raise_on_error=True,
                ),
                self._async_get_json(
                    f"{API_BASE}/forecast/{lat}/{lon}/advanced/1h",
                ),
                self._async_get_json(
                    f"{API_BASE}/forecast/{lat}/{lon}/advanced/3h",
                ),
                self._async_get_json(
                    f"{API_BASE}/current/{lat}/{lon}",
                ),
            )

        except Exception as err:
            raise UpdateFailed(err) from err
        else:
            return {
                "forecast": forecast_data,
                "forecast_hourly": forecast_hourly,
                "forecast_hourly_3h": forecast_hourly_3h,
                "current": current_weather,
            }
