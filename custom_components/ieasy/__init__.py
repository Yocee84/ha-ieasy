"""Hiconics iEasy+ cloud integration (read, plus a few settings writable behind an unlock switch)."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IEasyApi, IEasyApiError, IEasyAuthError
from .const import (CONF_BASE_URL, CONF_LANGUAGE, CONF_SITE_NAME, DEBOUNCE_SECONDS, DEFAULT_BASE_URL, DEFAULT_SITE_NAME, DOMAIN,
                    SCAN_INTERVAL_SECONDS, SETTINGS_EVERY, UNLOCK_SECONDS, LANGUAGES)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH, Platform.SELECT, Platform.TIME]


class IEasyCoordinator(DataUpdateCoordinator):
    """Polls the cloud once a minute."""

    def __init__(self, hass: HomeAssistant, api: IEasyApi, language: str) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS))
        self.api = api
        self.language = language
        self.station: dict = {}
        self.device: dict = {}
        self.settings: dict = {}
        self._polls = 0
        # Writes are refused while locked; unlocking lasts UNLOCK_SECONDS and always starts locked.
        self.unlocked = False
        self._relock = None
        self._write_gen: dict[str, int] = {}

    @callback
    def set_unlocked(self, unlocked: bool) -> None:
        self.cancel_relock()
        self.unlocked = unlocked
        if unlocked:
            self._relock = async_call_later(self.hass, UNLOCK_SECONDS, self._auto_lock)
        self.async_update_listeners()

    @callback
    def cancel_relock(self) -> None:
        if self._relock:
            self._relock()
            self._relock = None

    @callback
    def _auto_lock(self, _now) -> None:
        self._relock = None
        self.set_unlocked(False)

    async def write_setting(self, code: str, value: str) -> None:
        """Write one setting point after a short debounce; only the last of quick repeated changes is sent."""
        if not self.unlocked:
            raise HomeAssistantError("Settings are locked: turn on 'Settings unlocked' first")
        node = self.settings.get(code)
        if not node:
            raise HomeAssistantError(f"Setting {code} not found on this inverter")
        gen = self._write_gen[code] = self._write_gen.get(code, 0) + 1
        await asyncio.sleep(DEBOUNCE_SECONDS)
        if self._write_gen.get(code) != gen:
            return  # superseded by a newer value for the same setting
        if not self.unlocked:
            raise HomeAssistantError("Settings were locked again before the write was sent")
        result = await self.api.write_point(self.device["deviceId"], self.device["deviceSn"], node, value)
        node["value"] = result
        if self.data is not None:
            self.data.setdefault("settings", {})[code] = result
        self.async_update_listeners()
        self.refresh_settings_next()

    def refresh_settings_next(self) -> None:
        """Make the next poll re-read the settings tree (used after a write)."""
        self._polls = 0

    async def _async_update_data(self) -> dict:
        try:
            if not self.station:
                self.station = await self.api.first_station()
                self.device = await self.api.first_inverter(self.station["stationNo"])
            data = await self.api.snapshot(self.station["stationNo"], self.device["deviceSn"])
            # The settings tree is large (~400 kB), so read it every SETTINGS_EVERY polls only.
            if self._polls % SETTINGS_EVERY == 0 or not self.settings:
                try:
                    self.settings = await self.api.settings(self.device["deviceSn"])
                except IEasyApiError as err:
                    _LOGGER.warning("Could not read inverter settings: %s", err)
            self._polls += 1
            data["settings"] = {code: node.get("value") for code, node in self.settings.items()}
            return data
        except IEasyAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except (IEasyApiError, Exception) as err:  # network errors included
            raise UpdateFailed(str(err)) from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = IEasyApi(async_get_clientsession(hass), entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                   entry.data.get(CONF_SITE_NAME, DEFAULT_SITE_NAME),
                   entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    coordinator = IEasyCoordinator(hass, api, entry_language(hass, entry))
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_options_updated))
    return True


def entry_language(hass: HomeAssistant, entry: ConfigEntry) -> str:
    """Options win over the setup choice; entries made before 0.3.0 follow the HA language if it is supported."""
    language = entry.options.get(CONF_LANGUAGE) or entry.data.get(CONF_LANGUAGE)
    if language in LANGUAGES:
        return language
    ha_language = (hass.config.language or "en").split("-")[0]
    return ha_language if ha_language in LANGUAGES else "en"


async def _options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id).cancel_relock()
    return ok
