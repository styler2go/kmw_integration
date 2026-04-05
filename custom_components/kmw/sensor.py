"""Kachelmann Wetter: temp, risks & aktuelle Wetterdaten als Sensoren."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import KMW_FORECAST_DATA, KMW_TEMPERATURE_MAX
from .coordinator import KmwDataUpdateCoordinator

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo

    from . import KmwRuntimeData


@dataclass(frozen=True, kw_only=True)
class KmwCurrentSensorDescription(SensorEntityDescription):
    """Describes a KMW current-weather sensor."""

    api_field: str


CURRENT_SENSOR_DESCRIPTIONS: tuple[KmwCurrentSensorDescription, ...] = (
    KmwCurrentSensorDescription(
        key="current_temp",
        translation_key="current_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        api_field="temp",
    ),
    KmwCurrentSensorDescription(
        key="current_dewpoint",
        translation_key="current_dewpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        api_field="dewpoint",
    ),
    KmwCurrentSensorDescription(
        key="current_humidity",
        translation_key="current_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        api_field="humidityRelative",
    ),
    KmwCurrentSensorDescription(
        key="current_prec1h",
        translation_key="current_precip",
        native_unit_of_measurement="mm",
        api_field="prec1h",
    ),
    KmwCurrentSensorDescription(
        key="current_pressure",
        translation_key="current_pressure",
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        api_field="pressureMsl",
    ),
    KmwCurrentSensorDescription(
        key="current_sunhours",
        translation_key="current_sunhours",
        native_unit_of_measurement="h",
        api_field="sunHours",
    ),
    KmwCurrentSensorDescription(
        key="current_cloudcoverage",
        translation_key="current_cloudcoverage",
        native_unit_of_measurement=PERCENTAGE,
        api_field="cloudCoverage",
    ),
    KmwCurrentSensorDescription(
        key="current_snowamount",
        translation_key="current_snowamount",
        native_unit_of_measurement="mm",
        api_field="snowAmount",
    ),
    KmwCurrentSensorDescription(
        key="current_snowheight",
        translation_key="current_snowheight",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        api_field="snowHeight",
    ),
    KmwCurrentSensorDescription(
        key="current_windspeed",
        translation_key="current_windspeed",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        api_field="windSpeed",
    ),
    KmwCurrentSensorDescription(
        key="current_winddir",
        translation_key="current_winddir",
        native_unit_of_measurement="°",
        api_field="windDirection",
    ),
    KmwCurrentSensorDescription(
        key="current_windgust",
        translation_key="current_windgust",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        api_field="windGust",
    ),
    KmwCurrentSensorDescription(
        key="current_weathersymbol",
        translation_key="current_weathersymbol",
        api_field="weatherSymbol",
    ),
    KmwCurrentSensorDescription(
        key="current_wmocode",
        translation_key="current_wmocode",
        api_field="wmoCode",
    ),
    KmwCurrentSensorDescription(
        key="current_isday",
        translation_key="current_isday",
        api_field="isDay",
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable[[list[SensorEntity]], None],
) -> None:
    """Set up sensors from a config entry."""
    runtime_data: KmwRuntimeData = config_entry.runtime_data
    sensors: list[SensorEntity] = []

    for subentry_id, coordinator in runtime_data.coordinators.items():
        device_info = coordinator.device_info
        sensors.append(KmwTempMaxSensor(coordinator, subentry_id, device_info))
        sensors.append(KmwRiskSensor(coordinator, subentry_id, device_info))
        sensors.extend(
            KmwCurrentSensor(coordinator, subentry_id, device_info, desc)
            for desc in CURRENT_SENSOR_DESCRIPTIONS
        )

    async_add_entities(sensors)


class KmwBaseSensor(CoordinatorEntity[KmwDataUpdateCoordinator], SensorEntity):
    """Base class for KMW sensors with device_info and auto-updates."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KmwDataUpdateCoordinator,
        unique_id: str,  # noqa: ARG002
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = device_info


class KmwCurrentSensor(KmwBaseSensor):
    """Generic sensor for current weather data driven by SensorEntityDescription."""

    entity_description: KmwCurrentSensorDescription

    def __init__(
        self,
        coordinator: KmwDataUpdateCoordinator,
        unique_id: str,
        device_info: DeviceInfo,
        description: KmwCurrentSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, unique_id, device_info)
        self._attr_unique_id = f"{unique_id}_{description.key}"

    @property
    def available(self) -> bool:
        """Return True if current data is available."""
        current = self.coordinator.data.get("current")
        return current is not None and "data" in current

    @property
    def native_value(self) -> Any | None:
        """Return the sensor value from the current weather data."""
        data = self.coordinator.data.get("current", {}).get("data", {})
        return data.get(self.entity_description.api_field, {}).get("value")


class KmwTempMaxSensor(KmwBaseSensor):
    """Sensor for max temperature from daily forecast."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_translation_key = "tempmax"

    def __init__(
        self,
        coordinator: KmwDataUpdateCoordinator,
        unique_id: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id, device_info)
        self._attr_unique_id = f"{unique_id}_tempmax"

    @property
    def native_value(self) -> float | None:
        """Return the max temperature value."""
        forecast = self.coordinator.data.get("forecast")
        if forecast and forecast.get(KMW_FORECAST_DATA):
            return forecast[KMW_FORECAST_DATA][0].get(KMW_TEMPERATURE_MAX)
        return None


class KmwRiskSensor(KmwBaseSensor):
    """Sensor for risks from daily forecast."""

    _attr_translation_key = "risk"

    def __init__(
        self,
        coordinator: KmwDataUpdateCoordinator,
        unique_id: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id, device_info)
        self._attr_unique_id = f"{unique_id}_risk"

    @property
    def native_value(self) -> str | None:
        """Return the risk types as a comma-separated string."""
        forecast = self.coordinator.data.get("forecast")
        if forecast and forecast.get(KMW_FORECAST_DATA):
            risks = forecast[KMW_FORECAST_DATA][0].get("risks", [])
            if risks:
                return ", ".join(r.get("type", "") for r in risks)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes for the sensor."""
        forecast = self.coordinator.data.get("forecast")
        if forecast and forecast.get(KMW_FORECAST_DATA):
            return {"risks": forecast[KMW_FORECAST_DATA][0].get("risks", [])}
        return {}
