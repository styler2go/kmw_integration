"""Kachelmann Wetter: temp, risks & aktuelle Wetterdaten als Sensoren."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)

from .const import KMW_FORECAST_DATA, KMW_TEMPERATURE_MAX

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .coordinator import KmwDataUpdateCoordinator


def _get_coordinator(config_entry: Any) -> KmwDataUpdateCoordinator:
    return config_entry.runtime_data


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable[[list[SensorEntity]], None],
) -> None:
    """Set up Kachelmann Wetter sensors from a config entry."""
    coordinator: KmwDataUpdateCoordinator = _get_coordinator(config_entry)
    unique_id = config_entry.unique_id or "kmw_default"
    sensors = [
        KmwTempMaxSensor(coordinator, unique_id),
        KmwRiskSensor(coordinator, unique_id),
    ]
    current = coordinator.data.get("current", {})
    if current and "data" in current:
        sensors.extend(
            [
                KmwCurrentTempSensor(coordinator, unique_id),
                KmwCurrentDewpointSensor(coordinator, unique_id),
                KmwCurrentHumiditySensor(coordinator, unique_id),
                KmwCurrentPrecipSensor(coordinator, unique_id),
                KmwCurrentPressureSensor(coordinator, unique_id),
                KmwCurrentSunHoursSensor(coordinator, unique_id),
                KmwCurrentCloudCoverageSensor(coordinator, unique_id),
                KmwCurrentSnowAmountSensor(coordinator, unique_id),
                KmwCurrentSnowHeightSensor(coordinator, unique_id),
                KmwCurrentWindSpeedSensor(coordinator, unique_id),
                KmwCurrentWindDirectionSensor(coordinator, unique_id),
                KmwCurrentWindGustSensor(coordinator, unique_id),
                KmwCurrentWeatherSymbolSensor(coordinator, unique_id),
            ]
        )
    async_add_entities(sensors)


class KmwTempSensor(SensorEntity):
    """Sensor for Kachelmann Wetter temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_temp"
        self._attr_name = "Kachelmann Wetter Temperatur"

    @property
    def native_value(self) -> float | None:
        """Return the temperature value."""
        forecast = self._coordinator.data.get("forecast")
        if forecast and forecast.get(KMW_FORECAST_DATA):
            return forecast[KMW_FORECAST_DATA][0].get(KMW_TEMPERATURE_MAX)
        return None


class KmwTempMaxSensor(SensorEntity):
    """Sensor for Kachelmann Wetter max temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_tempmax"
        self._attr_name = "Kachelmann Wetter Tageshöchsttemperatur"

    @property
    def native_value(self) -> float | None:
        """Return the max temperature value."""
        forecast = self._coordinator.data.get("forecast")
        if forecast and forecast.get(KMW_FORECAST_DATA):
            return forecast[KMW_FORECAST_DATA][0].get(KMW_TEMPERATURE_MAX)
        return None


class KmwRiskSensor(SensorEntity):
    """Sensor for Kachelmann Wetter risks."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_risk"
        self._attr_name = "Kachelmann Wetter Risiken"

    @property
    def native_value(self) -> str | None:
        """Return the risk types as a comma-separated string."""
        forecast = self._coordinator.data.get("forecast")
        if forecast and forecast.get(KMW_FORECAST_DATA):
            risks = forecast[KMW_FORECAST_DATA][0].get("risks", [])
            if risks:
                return ", ".join(r.get("type", "") for r in risks)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes for the sensor."""
        forecast = self._coordinator.data.get("forecast")
        if forecast and forecast.get(KMW_FORECAST_DATA):
            return {"risks": forecast[KMW_FORECAST_DATA][0].get("risks", [])}
        return {}


class KmwCurrentTempSensor(SensorEntity):
    """Sensor for current temperature from Kachelmann Wetter."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_temp"
        self._attr_name = "Kachelmann Wetter Temperatur (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current temperature value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("temp", {}).get("value")


class KmwCurrentDewpointSensor(SensorEntity):
    """Sensor for current dewpoint from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_dewpoint"
        self._attr_name = "Kachelmann Wetter Taupunkt (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current dewpoint value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("dewpoint", {}).get("value")


class KmwCurrentHumiditySensor(SensorEntity):
    """Sensor for current relative humidity from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_humidity"
        self._attr_name = "Kachelmann Wetter Luftfeuchte (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current humidity value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("humidityRelative", {}).get("value")


class KmwCurrentPrecipSensor(SensorEntity):
    """Sensor for current precipitation (1h) from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = "mm"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_prec1h"
        self._attr_name = "Kachelmann Wetter Niederschlag 1h (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current precipitation value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("prec1h", {}).get("value")


class KmwCurrentPressureSensor(SensorEntity):
    """Sensor for current pressure (MSL) from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = UnitOfPressure.HPA
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_pressure"
        self._attr_name = "Kachelmann Wetter Luftdruck (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current pressure value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("pressureMsl", {}).get("value")


class KmwCurrentSunHoursSensor(SensorEntity):
    """Sensor for current sun hours from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = "h"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_sunhours"
        self._attr_name = "Kachelmann Wetter Sonnenstunden (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current sun hours value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("sunHours", {}).get("value")


class KmwCurrentCloudCoverageSensor(SensorEntity):
    """Sensor for current cloud coverage from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_cloudcoverage"
        self._attr_name = "Kachelmann Wetter Bewölkung (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current cloud coverage value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("cloudCoverage", {}).get("value")


class KmwCurrentSnowAmountSensor(SensorEntity):
    """Sensor for current snow amount from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = "mm"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_snowamount"
        self._attr_name = "Kachelmann Wetter Schneemenge (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current snow amount value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("snowAmount", {}).get("value")


class KmwCurrentSnowHeightSensor(SensorEntity):
    """Sensor for current snow height from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = UnitOfLength.MILLIMETERS
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_snowheight"
        self._attr_name = "Kachelmann Wetter Schneehöhe (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current snow height value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("snowHeight", {}).get("value")


class KmwCurrentWindSpeedSensor(SensorEntity):
    """Sensor for current wind speed from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = UnitOfSpeed.METERS_PER_SECOND
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_windspeed"
        self._attr_name = "Kachelmann Wetter Windgeschwindigkeit (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current wind speed value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("windSpeed", {}).get("value")


class KmwCurrentWindDirectionSensor(SensorEntity):
    """Sensor for current wind direction from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = "°"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_winddir"
        self._attr_name = "Kachelmann Wetter Windrichtung (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current wind direction value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("windDirection", {}).get("value")


class KmwCurrentWindGustSensor(SensorEntity):
    """Sensor for current wind gust from Kachelmann Wetter."""

    _attr_native_unit_of_measurement = UnitOfSpeed.METERS_PER_SECOND
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_windgust"
        self._attr_name = "Kachelmann Wetter Windböe (aktuell)"

    @property
    def native_value(self) -> float | None:
        """Return the current wind gust value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("windGust", {}).get("value")


class KmwCurrentWmoCodeSensor(SensorEntity):
    """Sensor for current WMO code from Kachelmann Wetter."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_wmocode"
        self._attr_name = "Kachelmann Wetter WMO-Code (aktuell)"

    @property
    def native_value(self) -> int | None:
        """Return the current WMO code value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("wmoCode", {}).get("value")


class KmwCurrentWeatherSymbolSensor(SensorEntity):
    """Sensor for current weather symbol from Kachelmann Wetter."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_weathersymbol"
        self._attr_name = "Kachelmann Wetter Wettersymbol (aktuell)"

    @property
    def native_value(self) -> str | None:
        """Return the current weather symbol value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("weatherSymbol", {}).get("value")


class KmwCurrentIsDaySensor(SensorEntity):
    """Sensor for current isDay flag from Kachelmann Wetter."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmwDataUpdateCoordinator, unique_id: str) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{unique_id}_current_isday"
        self._attr_name = "Kachelmann Wetter Tag/Nacht (aktuell)"

    @property
    def native_value(self) -> bool | None:
        """Return the current isDay value."""
        data = self._coordinator.data.get("current", {}).get("data", {})
        return data.get("isDay", {}).get("value")
