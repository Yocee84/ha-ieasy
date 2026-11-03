"""Hiconics iEasy+ cloud integration (read-only)."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IEasyApi, IEasyApiError, IEasyAuthError
from .const import (CONF_BASE_URL, CONF_SITE_NAME, DEFAULT_BASE_URL, DEFAULT_SITE_NAME, DOMAIN,
                    SCAN_INTERVAL_SECONDS)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]


class IEasyCoordinator(DataUpdateCoordinator):
    """Polls the cloud once a minute."""

    def __init__(self, hass: HomeAssistant, api: IEasyApi) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS))
        self.api = api
        self.station: dict = {}
        self.device: dict = {}

    async def _async_update_data(self) -> dict:
        try:
            if not self.station:
                self.station = await self.api.first_station()
                self.device = await self.api.first_inverter(self.station["stationNo"])
            return await self.api.snapshot(self.station["stationNo"], self.device["deviceSn"])
        except IEasyAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except (IEasyApiError, Exception) as err:  # network errors included
            raise UpdateFailed(str(err)) from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = IEasyApi(async_get_clientsession(hass), entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                   entry.data.get(CONF_SITE_NAME, DEFAULT_SITE_NAME),
                   entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    coordinator = IEasyCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
