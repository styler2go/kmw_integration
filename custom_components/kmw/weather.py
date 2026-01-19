"""Support for Kachelmann Wetter service."""

from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, Any

from homeassistant.components.weather import (
    ATTR_FORECAST_CLOUD_COVERAGE,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_GUST_SPEED,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    SingleCoordinatorWeatherEntity,
)
from homeassistant.components.weather.const import (
    DOMAIN as WEATHER_DOMAIN,
)
from homeassistant.components.weather.const import (
    WeatherEntityFeature,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType

from .const import (
    ATTRIBUTION,
    CONDITIONS_MAP,
    CONF_CURRENT_WEATHER,
    CONF_CURRENT_WEATHER_DEFAULT,
    CONF_FORECAST,
    CONF_FORECAST_DEFAULT,
    DOMAIN,
    KMW_CLOUD_COVERAGE,
    KMW_DATETIME,
    KMW_FORECAST_DATA,
    KMW_PRECIPITATION,
    KMW_PRECIPITATION_PROBABILITY_1MM,
    KMW_PRECIPITATION_PROBABILITY_10MM,
    KMW_RISKS,
    KMW_SUN_HOURS,
    KMW_TEMPERATURE_MAX,
    KMW_TEMPERATURE_MIN,
    KMW_WEATHER_SYMBOL,
    KMW_WIND_DIRECTION,
    KMW_WIND_GUST,
)
from .coordinator import KmwDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.device_registry import DeviceInfo

_LOGGER = logging.getLogger(__name__)

MORNING_START = 5
MORNING_END = 12
AFTERNOON_START = 12
AFTERNOON_END = 17
EVENING_START = 17
EVENING_END = 22


class ForecastMode(Enum):
    """The forecast mode of a Weather entity."""

    DAILY = 1
    HOURLY = 2


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a weather entity from a config_entry."""
    coordinator: KmwDataUpdateCoordinator = config_entry.runtime_data
    entity_registry = er.async_get(hass)

    device = {
        "identifiers": {(DOMAIN, config_entry.unique_id)},
        "name": config_entry.title,
        "manufacturer": "Kachelmann Wetter",
        "model": "Weather API",
        "entry_type": DeviceEntryType.SERVICE,
    }

    # Remove hourly entity from legacy config entries
    if hourly_entity_id := entity_registry.async_get_entity_id(
        WEATHER_DOMAIN,
        DOMAIN,
        f"{config_entry.unique_id}-hourly",
    ):
        entity_registry.async_remove(hourly_entity_id)

    # Remove daily entity from legacy config entries
    if daily_entity_id := entity_registry.async_get_entity_id(
        WEATHER_DOMAIN,
        DOMAIN,
        f"{config_entry.unique_id}-daily",
    ):
        entity_registry.async_remove(daily_entity_id)

    async_add_entities(
        [
            KachelmannWeather(
                hass,
                coordinator,
                config_entry.unique_id,
                config_entry,
                device,
            ),
        ]
    )


class KachelmannWeather(SingleCoordinatorWeatherEntity[KmwDataUpdateCoordinator]):
    """Implementation of a Kachelmann Wetter weather condition."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: KmwDataUpdateCoordinator,
        unique_id: str,
        config: ConfigEntry,
        device: DeviceInfo,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._hass: HomeAssistant = hass
        self._attr_unique_id = unique_id
        self._config: ConfigEntry = config
        self._attr_device_info = device
        self._conf_current_weather: str = self._config.options.get(
            CONF_CURRENT_WEATHER, CONF_CURRENT_WEATHER_DEFAULT
        )

        name = self._config.title

        if name is None:
            name = self.hass.config.location_name

        if name is None:
            name = "Kachelmann Wetter"

        self._attr_name = name

        self._attr_entity_registry_enabled_default = True

        self._attr_supported_features = 0
        if self._config.options.get(CONF_FORECAST, CONF_FORECAST_DEFAULT):
            self._attr_supported_features |= WeatherEntityFeature.FORECAST_DAILY
            self._attr_supported_features |= WeatherEntityFeature.FORECAST_HOURLY

        self._attr_native_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_native_pressure_unit = UnitOfPressure.HPA
        self._attr_native_visibility_unit = UnitOfLength.KILOMETERS
        self._attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
        self._attr_native_precipitation_unit = UnitOfLength.MILLIMETERS

        self._attr_attribution = ATTRIBUTION

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("current") is not None
        )

    def _get_current_data(self) -> dict | None:
        """Get the current day's data."""
        current_data = self.coordinator.data.get("current")
        if not current_data or not current_data.get(KMW_FORECAST_DATA):
            return None

        return current_data[KMW_FORECAST_DATA]

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        temp = current_day_data.get("weatherSymbol")
        if not temp:
            return None

        return CONDITIONS_MAP.get(temp["value"])

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature in native units (Tageshöchstwert)."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        temp = current_day_data.get("temp")
        if not temp:
            return None

        return temp["value"]

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure in native units."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        data = current_day_data.get("pressureMsl")
        if not data:
            return None

        return data["value"]

    @property
    def humidity(self) -> float | None:
        """Return the pressure in native units."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        data = current_day_data.get("humidityRelative")
        if not data:
            return None

        return data["value"]

    @property
    def cloud_coverage(self) -> float | None:
        """Return the pressure in native units."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        data = current_day_data.get("cloudCoverage")
        if not data:
            return None

        return data["value"]

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the wind gust speed in native units."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        data = current_day_data.get("windGust")
        if not data:
            return None

        return data["value"]

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed in native units."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        data = current_day_data.get("windSpeed")
        if not data:
            return None

        return data["value"]

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        data = current_day_data.get("windDirection")
        if not data:
            return None

        return data["value"]

    @property
    def native_precipitation_rate(self) -> float | None:
        """Return the precipitation rate in native units."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        data = current_day_data.get("prec1h")
        if not data:
            return None

        if data["value"] == 0.0:
            return None

        return data["value"]

    @property
    def sun_hours(self) -> float | None:
        """Return the sun hours for the current day."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return None

        data = current_day_data.get("sunHours")
        if not data:
            return None

        return data["value"]

    @property
    def risks(self) -> list:
        """Return weather risks for the current day."""
        current_day_data = self._get_current_data()
        if not current_day_data:
            return []
        return current_day_data.get(KMW_RISKS, [])

    @callback
    def _async_forecast_daily(self) -> list[dict[str, Any]] | None:
        if not self._config.options.get(CONF_FORECAST, CONF_FORECAST_DEFAULT):
            return None
        forecast_data = self.coordinator.data.get("forecast")
        if not forecast_data or not forecast_data.get(KMW_FORECAST_DATA):
            return None
        result = []
        for day_data in forecast_data[KMW_FORECAST_DATA]:
            forecast_item = {
                ATTR_FORECAST_TIME: day_data.get(KMW_DATETIME),
                ATTR_FORECAST_NATIVE_TEMP: day_data.get(KMW_TEMPERATURE_MAX),
                ATTR_FORECAST_NATIVE_TEMP_LOW: day_data.get(KMW_TEMPERATURE_MIN),
                ATTR_FORECAST_NATIVE_PRECIPITATION: day_data.get(KMW_PRECIPITATION),
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: (
                    day_data.get(KMW_PRECIPITATION_PROBABILITY_1MM)
                ),
                ATTR_FORECAST_NATIVE_WIND_GUST_SPEED: day_data.get(KMW_WIND_GUST),
                ATTR_FORECAST_WIND_BEARING: day_data.get(KMW_WIND_DIRECTION),
                ATTR_FORECAST_CLOUD_COVERAGE: day_data.get(KMW_CLOUD_COVERAGE),
                "precipitation_probability_1mm": (
                    day_data.get(KMW_PRECIPITATION_PROBABILITY_1MM)
                ),
                "precipitation_probability_10mm": (
                    day_data.get(KMW_PRECIPITATION_PROBABILITY_10MM)
                ),
                "sun_hours": day_data.get(KMW_SUN_HOURS),
                "weather_symbol": day_data.get(KMW_WEATHER_SYMBOL),
                "risks": day_data.get(KMW_RISKS, []),
            }
            weather_symbol = day_data.get(KMW_WEATHER_SYMBOL)
            if weather_symbol:
                forecast_item[ATTR_FORECAST_CONDITION] = CONDITIONS_MAP.get(
                    weather_symbol
                )
            result.append(forecast_item)
        return result

    @callback
    def _async_forecast_hourly(self) -> list[dict[str, Any]] | None:
        """Return the hourly forecast in native units."""
        forecast_data = self.coordinator.data.get("forecast_hourly")
        if not forecast_data or not forecast_data.get("data"):
            return None
        return [
            {
                ATTR_FORECAST_TIME: hour.get("dateTime"),
                ATTR_FORECAST_NATIVE_TEMP: hour.get("temp"),
                ATTR_FORECAST_NATIVE_PRECIPITATION: hour.get("precCurrent"),
                ATTR_FORECAST_CLOUD_COVERAGE: hour.get("cloudCoverage"),
                ATTR_FORECAST_NATIVE_WIND_SPEED: hour.get("windSpeed"),
                ATTR_FORECAST_NATIVE_WIND_GUST_SPEED: hour.get("windGust"),
                ATTR_FORECAST_WIND_BEARING: hour.get("windDirection"),
                ATTR_FORECAST_CONDITION: CONDITIONS_MAP.get(hour.get("weatherSymbol")),
                "pressure_msl": hour.get("pressureMsl"),
                "humidity_relative": hour.get("humidityRelative"),
                "dewpoint": hour.get("dewpoint"),
                "cloud_coverage_low": hour.get("cloudCoverageLow"),
                "cloud_coverage_medium": hour.get("cloudCoverageMedium"),
                "cloud_coverage_high": hour.get("cloudCoverageHigh"),
                "sun_hours": hour.get("sunHours"),
                "global_radiation": hour.get("globalRadiation"),
                "prec_6h": hour.get("prec6h"),
                "prec_12h": hour.get("prec12h"),
                "prec_24h": hour.get("prec24h"),
                "prec_total": hour.get("precTotal"),
                "snow_amount": hour.get("snowAmount"),
                "snow_height": hour.get("snowHeight"),
                "wmo_code": hour.get("wmoCode"),
            }
            for hour in forecast_data["data"]
        ]

    @property
    def forecast(self) -> list[dict[str, Any]] | None:
        """Return the daily forecast for the Home Assistant weather card."""
        return self._async_forecast_daily()

    @property
    def forecast_hourly(self) -> list[dict[str, Any]] | None:
        """Return the hourly forecast for the Home Assistant weather card."""
        return self._async_forecast_hourly()
