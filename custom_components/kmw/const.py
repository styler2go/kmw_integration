"""Constants for Kachelmann Wetter component."""

import logging
from datetime import timedelta

from homeassistant.components.weather import (
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
)

DOMAIN = "kmw"

ATTRIBUTION = "Quelle: Kachelmann Wetter"

CONF_API_KEY = "api_key"
CONF_CURRENT_WEATHER = "current_weather"
CONF_CURRENT_WEATHER_FORECAST = "current"
CONF_CURRENT_WEATHER_DEFAULT = CONF_CURRENT_WEATHER_FORECAST
CONF_FORECAST = "forecast"
CONF_FORECAST_DEFAULT = True
CONF_MODEL = "model"
CONF_MODEL_DEFAULT = "SWISS1X1"

# URL für 14-Tage-Trend
URL_3DAY_FORECAST = (
    "https://api.kachelmannwetter.com/v02/forecast/{lat}/{lon}/trend14days"
)

UPDATE_INTERVAL = timedelta(seconds=610)

CONDITION_PARTLYCLOUDY_THRESHOLD = 25
CONDITION_CLOUDY_THRESHOLD = 75

MEASUREMENTS_MAX_AGE = 3

KMW_MEASUREMENT = 0
KMW_FORECAST = 1

KMW_MEASUREMENT_DATETIME = "datetime"

# Mapping for Kachelmann Wetter weather symbols
CONDITIONS_MAP = {
    "clearnight": ATTR_CONDITION_SUNNY,  # Clear night (special case for night)
    "sunshine": ATTR_CONDITION_SUNNY,
    "partlycloudy": ATTR_CONDITION_PARTLYCLOUDY,
    "cloudy": ATTR_CONDITION_CLOUDY,
    "fog": ATTR_CONDITION_FOG,
    "showers": ATTR_CONDITION_RAINY,
    "rain": ATTR_CONDITION_POURING,
    "snowshowers": ATTR_CONDITION_SNOWY,
    "snow": ATTR_CONDITION_SNOWY,
    "sleet": ATTR_CONDITION_SNOWY_RAINY,
    "hail": ATTR_CONDITION_HAIL,
    "thunderstorm": ATTR_CONDITION_LIGHTNING_RAINY,
    "windy": ATTR_CONDITION_WINDY,
}

# Forecast-Daten-Key
KMW_FORECAST_DATA = "data"

# Daten-Feld-Konstanten für 14-Tage-Trend
KMW_TEMPERATURE_MAX = "tempMax"
KMW_TEMPERATURE_MIN = "tempMin"
KMW_PRECIPITATION = "prec"
KMW_PRECIPITATION_PROBABILITY_1MM = "precProb1mm"
KMW_PRECIPITATION_PROBABILITY_10MM = "precProb10mm"
KMW_PRECIPITATION_PROBABILITY = "precProb1mm"  # Standardmäßig 1mm
KMW_WIND_GUST = "windGust"
KMW_WIND_DIRECTION = "windDirection"
KMW_WEATHER_SYMBOL = "weatherSymbol"
KMW_CLOUD_COVERAGE = "cloudCoverageEighths"
KMW_SUN_HOURS = "sunHours"
KMW_DATETIME = "dateTime"
KMW_RISKS = "risks"

# Time of day segments
KMW_TOD_NIGHT = "night"
KMW_TOD_MORNING = "morning"
KMW_TOD_AFTERNOON = "afternoon"
KMW_TOD_EVENING = "evening"

SOURCE_STATIONSLEXIKON = 0
SOURCE_MOSMIX_STATIONSKATALOG = 1

_LOGGER = logging.getLogger(".")
