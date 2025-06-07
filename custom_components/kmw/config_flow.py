"""Config flow to configure Kachelmann Wetter component."""

from __future__ import annotations

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_API_KEY,
    CONF_CURRENT_WEATHER,
    CONF_CURRENT_WEATHER_DEFAULT,
    CONF_CURRENT_WEATHER_FORECAST,
    CONF_FORECAST,
    CONF_FORECAST_DEFAULT,
    CONF_MODEL,
    CONF_MODEL_DEFAULT,
    DOMAIN,
)


class KmwFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Kachelmann Wetter component."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the Kachelmann Wetter flow."""
        self._name: str = "Kachelmann Wetter"
        self._api_key: str | None = None
        self._model: str = CONF_MODEL_DEFAULT

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> Any:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            self._api_key = user_input[CONF_API_KEY]
            self._model = CONF_MODEL_DEFAULT
            self._name = "Kachelmann Wetter"

            # Direkter Sprung zum Erstellen des Eintrags,
            # Überspringen von name und options
            return self.async_create_entry(
                title=self._name,
                data={
                    CONF_API_KEY: self._api_key,
                    CONF_MODEL: self._model,
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

    async def async_step_name(self, user_input: dict[str, Any] | None = None) -> Any:
        """Handle the step to name the instance."""
        if user_input is not None:
            self._name = user_input[CONF_NAME]
            return await self.async_step_options()

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Kachelmann Wetter"): cv.string,
            }
        )

        return self.async_show_form(step_id="name", data_schema=schema, last_step=False)

    async def async_step_options(self, user_input: dict[str, Any] | None = None) -> Any:
        """Handle the step for options."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._name,
                data={
                    CONF_API_KEY: self._api_key,
                    CONF_MODEL: self._model,
                },
                options={
                    CONF_CURRENT_WEATHER: user_input.get(
                        CONF_CURRENT_WEATHER, CONF_CURRENT_WEATHER_DEFAULT
                    ),
                    CONF_FORECAST: user_input.get(CONF_FORECAST, CONF_FORECAST_DEFAULT),
                },
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_CURRENT_WEATHER,
                    default=CONF_CURRENT_WEATHER_DEFAULT,
                ): vol.In([CONF_CURRENT_WEATHER_FORECAST]),
                vol.Required(CONF_FORECAST, default=CONF_FORECAST_DEFAULT): bool,
            }
        )

        return self.async_show_form(
            step_id="options", data_schema=schema, last_step=True
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return KmwOptionsFlowHandler(config_entry)


class KmwOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Kachelmann Wetter component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> Any:
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
