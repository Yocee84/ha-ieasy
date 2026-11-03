"""Config flow: account + password, verified by a real login."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import IEasyApi, IEasyAuthError
from .const import CONF_BASE_URL, CONF_SITE_NAME, DEFAULT_BASE_URL, DEFAULT_SITE_NAME, DOMAIN

SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
    vol.Optional(CONF_SITE_NAME, default=DEFAULT_SITE_NAME): str,
})


class IEasyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            api = IEasyApi(async_get_clientsession(self.hass), user_input[CONF_BASE_URL],
                           user_input[CONF_SITE_NAME], user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
            try:
                await api.login()
                station = await api.first_station()
            except IEasyAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(str(station["stationNo"]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"iEasy {station.get('stationName', '')}", data=user_input)
        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)
