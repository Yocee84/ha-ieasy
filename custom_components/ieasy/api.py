"""Minimal read-only client for the iEasy+ cloud API (reverse engineered from the app)."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp

from .const import APP_ID, CODE_OK

_LOGGER = logging.getLogger(__name__)


class IEasyAuthError(Exception):
    """Login failed."""


class IEasyApiError(Exception):
    """API returned an error code."""


class IEasyApi:
    """Login, token refresh and the read endpoints the integration uses."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str, site_name: str,
                 account: str, password: str) -> None:
        self._session = session
        self._base = base_url if base_url.endswith("/") else base_url + "/"
        self._site = site_name
        self._account = account
        self._password = password
        self._token = ""

    def _headers(self) -> dict[str, str]:
        offset = datetime.now().astimezone().strftime("%z")
        return {
            "Content-Type": "application/json",
            "ems_app_id": APP_ID,
            "ems_language": "en_US",
            "ems_token": self._token,
            "ems_time_zone": f"UTC{offset[:3]}:{offset[3:]}",
            "ems_site_name": self._site,
        }

    async def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        async with self._session.post(self._base + path, json=body, headers=self._headers(),
                                      timeout=aiohttp.ClientTimeout(total=30)) as resp:
            return await resp.json(content_type=None)

    async def login(self) -> None:
        body = {
            "account": self._account,
            "password": self._password,
            "loginType": 0,
            "phoneInfo": {"brand": "HomeAssistant", "model": "ieasy", "osVersion": "1", "osName": "Android"},
        }
        self._token = ""
        res = await self._post("v1/sys/auth/login", body)
        token = (res.get("data") or {}).get("token") if isinstance(res, dict) else None
        if res.get("code") != CODE_OK or not token:
            raise IEasyAuthError(f"{res.get('code')}: {res.get('msg')}")
        self._token = token

    async def call(self, path: str, body: dict[str, Any]) -> Any:
        """POST with one automatic re-login when the token is missing or rejected."""
        if not self._token:
            await self.login()
        res = await self._post(path, body)
        if res.get("code") != CODE_OK and "UNAUTHORIZED" in str(res.get("code")):
            await self.login()
            res = await self._post(path, body)
        if res.get("code") != CODE_OK:
            raise IEasyApiError(f"{path}: {res.get('code')}: {res.get('msg')}")
        return res.get("data")

    async def first_station(self) -> dict[str, Any]:
        data = await self.call("deve/v1/web/station/list", {"pageNum": 1, "pageSize": 10})
        records = (data or {}).get("records") or []
        if not records:
            raise IEasyApiError("no station on this account")
        return records[0]

    async def first_inverter(self, station_no: str) -> dict[str, Any]:
        data = await self.call("deve/v1/web/station/getStationDeviceList",
                               {"stationNo": station_no, "pageNum": 1, "pageSize": 20})
        for dev in data or []:
            if dev.get("deviceType") == "Plant_Inverter":
                return dev
        raise IEasyApiError("no inverter in the station")

    async def snapshot(self, station_no: str, device_sn: str) -> dict[str, dict[str, Any]]:
        """All read endpoints in one dict: flow, battery, grid, load, pv."""
        body = {"stationNo": station_no, "deviceSn": device_sn}
        out: dict[str, dict[str, Any]] = {}
        out["flow"] = await self.call("deve/v1/station/overview/energyFlow", {"stationNo": station_no}) or {}
        for key in ("battery", "grid", "load", "pv"):
            data = await self.call(f"deve/v1/energy/detail/{key}", body)
            out[key] = data[0] if isinstance(data, list) and data else {}
        return out
