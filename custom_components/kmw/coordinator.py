"""DataUpdateCoordinator for Kachelmann Wetter integration."""

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
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


class KmwDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Kachelmann Wetter data."""

    HTTP_OK = 200
    HTTP_OK_MAX = 299
    HTTP_NOT_MODIFIED = 304

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize global Kachelmann Wetter data updater."""
        self._config_entry: ConfigEntry = config_entry
        self._clientsession: ClientSession = async_get_clientsession(hass)
        self._hass = hass
        self._last_forecast: dict | None = None
        self._last_forecast_etag: str | None = None

        _LOGGER.debug(
            "Checking for new data for %s every %s",
            self._config_entry.title,
            UPDATE_INTERVAL,
        )

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)

    async def _async_update_data(self) -> dict:
        """Fetch data from Kachelmann Wetter API."""
        try:
            conf_forecast = self._config_entry.options.get(
                CONF_FORECAST, CONF_FORECAST_DEFAULT
            )

            # Get coordinates from Home Assistant configuration
            latitude = self._hass.config.latitude
            longitude = self._hass.config.longitude

            # Get API key from config entry
            api_key = self._config_entry.data[CONF_API_KEY]

            forecast_data = None
            forecast_hourly = None
            current_weather = None

            if conf_forecast:
                forecast_data = await self.async_fetch_3day_forecast(
                    latitude, longitude, api_key
                )
                forecast_hourly = await self.async_fetch_hourly_forecast(
                    latitude, longitude, api_key
                )
                current_weather = await self.async_fetch_current_weather(
                    latitude, longitude, api_key
                )
            else:
                forecast_data = None
                forecast_hourly = None
                current_weather = None

            return {
                "forecast": forecast_data,
                "forecast_hourly": forecast_hourly,
                "current": current_weather,
            }

        except Exception as err:
            raise UpdateFailed(err) from err

    async def async_fetch_3day_forecast(
        self, latitude: float, longitude: float, api_key: str
    ) -> dict | None:
        """Fetch 14-day trend forecast data from Kachelmann Wetter API."""
        url = f"https://api.kachelmannwetter.com/v02/forecast/{latitude}/{longitude}/trend14days"
        headers = {
            "Accept": "application/json",
            "X-API-Key": api_key,
        }
        response = await self._clientsession.get(url, headers=headers)
        if self.HTTP_OK <= response.status <= self.HTTP_OK_MAX:
            _LOGGER.debug("Forecast successfully fetched from %s.", url)
            return await response.json()
        msg = f"Unexpected status code {response.status} from {url}."
        raise UpdateFailed(msg)

    async def async_fetch_hourly_forecast(
        self, latitude: float, longitude: float, api_key: str
    ) -> dict | None:
        """Fetch hourly forecast data from Kachelmann Wetter API."""
        url = f"https://api.kachelmannwetter.com/v02/forecast/{latitude}/{longitude}/advanced/1h"
        headers = {
            "Accept": "application/json",
            "X-API-Key": api_key,
        }
        response = await self._clientsession.get(url, headers=headers)
        if self.HTTP_OK <= response.status <= self.HTTP_OK_MAX:
            return await response.json()
        return None

    async def async_fetch_current_weather(
        self, latitude: float, longitude: float, api_key: str
    ) -> dict | None:
        """Fetch current weather data from Kachelmann Wetter API."""
        url = f"https://api.kachelmannwetter.com/v02/current/{latitude}/{longitude}"
        headers = {
            "Accept": "application/json",
            "X-API-Key": api_key,
        }
        response = await self._clientsession.get(url, headers=headers)
        if self.HTTP_OK <= response.status <= self.HTTP_OK_MAX:
            return await response.json()
        return None
