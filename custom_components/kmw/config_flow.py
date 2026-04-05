"""Config flow to configure Kachelmann Wetter component."""

from __future__ import annotations

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.zone import DOMAIN as ZONE_DOMAIN
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_NAME, CONF_ZONE
from homeassistant.core import callback
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import (
    CONF_API_KEY,
    CONF_CURRENT_WEATHER,
    CONF_CURRENT_WEATHER_DEFAULT,
    CONF_CURRENT_WEATHER_FORECAST,
    CONF_FORECAST,
    CONF_FORECAST_DEFAULT,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MODEL,
    CONF_MODEL_DEFAULT,
    DOMAIN,
    SUBENTRY_TYPE_LOCATION,
)


class KmwFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Kachelmann Wetter component."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Kachelmann Wetter",
                data={
                    CONF_API_KEY: user_input[CONF_API_KEY],
                    CONF_MODEL: CONF_MODEL_DEFAULT,
                },
                options={
                    CONF_CURRENT_WEATHER: CONF_CURRENT_WEATHER_DEFAULT,
                    CONF_FORECAST: CONF_FORECAST_DEFAULT,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors, last_step=True
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return KmwOptionsFlowHandler(config_entry)

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls,
        config_entry: ConfigEntry,  # noqa: ARG003
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this handler."""
        return {SUBENTRY_TYPE_LOCATION: KmwLocationSubentryFlowHandler}


class KmwOptionsFlowHandler(OptionsFlow):
    """Options flow for Kachelmann Wetter component."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_CURRENT_WEATHER,
                    default=self.config_entry.options.get(
                        CONF_CURRENT_WEATHER, CONF_CURRENT_WEATHER_DEFAULT
                    ),
                ): vol.In([CONF_CURRENT_WEATHER_FORECAST]),
                vol.Required(
                    CONF_FORECAST,
                    default=self.config_entry.options.get(
                        CONF_FORECAST, CONF_FORECAST_DEFAULT
                    ),
                ): bool,
                vol.Required(
                    CONF_MODEL,
                    default=self.config_entry.data.get(CONF_MODEL, CONF_MODEL_DEFAULT),
                ): cv.string,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)


class KmwLocationSubentryFlowHandler(ConfigSubentryFlow):
    """Handle subentry flow for adding a location/device."""

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> SubentryFlowResult:
        """Handle user step to add a new location."""
        return await self.async_step_add_location()

    def _resolve_location(
        self, user_input: dict[str, Any]
    ) -> tuple[float, float, str] | None:
        """Resolve lat/lon/name from input, zone as base with optional overrides."""
        zone_entity_id = user_input[CONF_ZONE]
        state = self.hass.states.get(zone_entity_id)
        if state is None:
            return None
        zone_lat = state.attributes.get("latitude")
        zone_lon = state.attributes.get("longitude")
        if zone_lat is None or zone_lon is None:
            return None

        # Optional overrides - use zone values as fallback
        lat = user_input.get(CONF_LATITUDE) or zone_lat
        lon = user_input.get(CONF_LONGITUDE) or zone_lon
        name = user_input.get(CONF_NAME) or state.name
        return (lat, lon, name)

    async def async_step_add_location(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a new location by selecting a zone."""
        if user_input is not None:
            resolved = self._resolve_location(user_input)
            if resolved is None:
                return self.async_show_form(
                    step_id="add_location",
                    data_schema=self._location_schema(),
                    errors={"base": "zone_not_found"},
                )
            lat, lon, title = resolved
            return self.async_create_entry(
                title=title,
                data={
                    CONF_ZONE: user_input[CONF_ZONE],
                    CONF_LATITUDE: lat,
                    CONF_LONGITUDE: lon,
                },
                unique_id=user_input[CONF_ZONE],
            )

        return self.async_show_form(
            step_id="add_location",
            data_schema=self._location_schema(),
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> SubentryFlowResult:
        """Reconfigure a location."""
        return await self.async_step_reconfigure_location()

    async def async_step_reconfigure_location(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Reconfigure an existing location."""
        if user_input is not None:
            resolved = self._resolve_location(user_input)
            if resolved is None:
                subentry = self._get_reconfigure_subentry()
                return self.async_show_form(
                    step_id="reconfigure_location",
                    data_schema=self._location_schema(
                        zone_default=subentry.data.get(CONF_ZONE),
                        name_default=subentry.title,
                        lat_default=subentry.data.get(CONF_LATITUDE),
                        lon_default=subentry.data.get(CONF_LONGITUDE),
                    ),
                    errors={"base": "zone_not_found"},
                )
            lat, lon, title = resolved
            return self.async_update_reload_and_abort(
                self._get_entry(),
                self._get_reconfigure_subentry(),
                title=title,
                data={
                    CONF_ZONE: user_input[CONF_ZONE],
                    CONF_LATITUDE: lat,
                    CONF_LONGITUDE: lon,
                },
                unique_id=user_input[CONF_ZONE],
            )

        subentry = self._get_reconfigure_subentry()
        return self.async_show_form(
            step_id="reconfigure_location",
            data_schema=self._location_schema(
                zone_default=subentry.data.get(CONF_ZONE),
                name_default=subentry.title,
                lat_default=subentry.data.get(CONF_LATITUDE),
                lon_default=subentry.data.get(CONF_LONGITUDE),
            ),
        )

    @staticmethod
    def _location_schema(
        *,
        zone_default: str | None = None,
        name_default: str | None = None,
        lat_default: float | None = None,
        lon_default: float | None = None,
    ) -> vol.Schema:
        """Return the location selection schema with optional overrides."""
        zone_selector = EntitySelector(
            EntitySelectorConfig(domain=ZONE_DOMAIN),
        )
        schema_dict: dict[vol.Marker, Any] = {}
        if zone_default:
            schema_dict[vol.Required(CONF_ZONE, default=zone_default)] = zone_selector
        else:
            schema_dict[vol.Required(CONF_ZONE)] = zone_selector

        # Optional overrides
        schema_dict[vol.Optional(CONF_NAME, default=name_default or "")] = cv.string
        schema_dict[vol.Optional(CONF_LATITUDE, default=lat_default)] = vol.Maybe(
            cv.latitude
        )
        schema_dict[vol.Optional(CONF_LONGITUDE, default=lon_default)] = vol.Maybe(
            cv.longitude
        )

        return vol.Schema(schema_dict)
