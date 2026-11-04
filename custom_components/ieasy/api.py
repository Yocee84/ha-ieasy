"""Minimal client for the iEasy+ cloud API (reverse engineered from the app).

Everything is read-only except write_point(), which the setting entities use through the
coordinator (behind the "Settings unlocked" switch).
"""
from __future__ import annotations

import asyncio
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
        # Writes are serialised: the task is found again by its name, which only has 1 s resolution.
        self._write_lock = asyncio.Lock()
        self._last_task_name = ""

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

    async def settings(self, device_sn: str) -> dict[str, dict[str, Any]]:
        """All setting points of the inverter (the app's remote-settings tree), keyed by point code."""
        data = await self.call("deve/v1/setting/task/tree/v1", {"sn": device_sn, "type": "APP_CFG"})
        points: dict[str, dict[str, Any]] = {}
        stack = list((data or {}).get("nodeList") or [])
        while stack:
            node = stack.pop()
            if node.get("nodeType") == "POINT" and node.get("code"):
                points.setdefault(str(node["code"]), node)
            stack.extend(node.get("children") or [])
        return points

    async def write_point(self, device_id: str, device_sn: str, node: dict[str, Any], value: str) -> str:
        """Write one setting point the way the app does and return the value the inverter confirmed.

        Raises IEasyApiError if the task fails or the confirmed value differs from the requested one.
        """
        async with self._write_lock:
            return await self._write_point_locked(device_id, device_sn, node, value)

    def _task_name(self, device_sn: str) -> tuple[str, str]:
        now = datetime.now().astimezone()
        offset = now.strftime("%z")
        tz = f"UTC{offset[:3]}:{offset[3:]}"
        return f"{now.strftime('%Y/%m/%d %H:%M:%S')} {tz} _ [{device_sn}]", tz

    async def _write_point_locked(self, device_id: str, device_sn: str, node: dict[str, Any], value: str) -> str:
        task_name, tz = self._task_name(device_sn)
        while task_name == self._last_task_name:
            await asyncio.sleep(0.2)
            task_name, tz = self._task_name(device_sn)
        self._last_task_name = task_name
        item = {
            "code": str(node["code"]), "attrField": node.get("attrField"), "langKey": node.get("langKey"),
            "value": node.get("value"), "settingValue": str(value), "needReply": 1,
            "pointName": node.get("attrField"), "type": node.get("type"), "typeCfg": node.get("typeCfg"),
            "customFlag": node.get("customFlag", 0),
        }
        body = {
            "deviceList": [{"deviceId": device_id, "taskName": task_name, "timeZone": tz}],
            "taskName": task_name, "retryType": 1, "retryValue": 1, "timeZone": tz, "settingInfoList": [item],
        }
        await self.call("deve/v1/setting/task/new/apply/v1", body)
        for _ in range(15):
            await asyncio.sleep(2)
            # Newer tasks (another write from the app) push ours down the list, so look further than the top one.
            tasks = await self.call("deve/v1/setting/task/query", {"deviceId": device_id, "pageIndex": 1, "pageSize": 10})
            record = next((r for r in (tasks or {}).get("records") or [] if r.get("taskName") == task_name), None)
            if not record:
                continue
            detail = await self.call("deve/v1/setting/task/app/detail", {"id": record["id"]})
            for entry in (detail or {}).get("executeList") or []:
                if (str(entry.get("point")) != str(node["code"]) or str(entry.get("settingValue")) != str(value)
                        or entry.get("executeStatus") in (None, 0)):
                    continue
                result = str(entry.get("resultValue"))
                if entry.get("executeStatus") != 1 or result != str(value):
                    raise IEasyApiError(f"write {node['code']}={value} not confirmed (status "
                                        f"{entry.get('executeStatus')}, inverter reports {result})")
                return result
        raise IEasyApiError(f"write {node['code']}={value}: no confirmation from the inverter in 30 s")

    async def snapshot(self, station_no: str, device_sn: str) -> dict[str, dict[str, Any]]:
        """All read endpoints in one dict: flow, battery, grid, load, pv."""
        body = {"stationNo": station_no, "deviceSn": device_sn}
        out: dict[str, dict[str, Any]] = {}
        out["flow"] = await self.call("deve/v1/station/overview/energyFlow", {"stationNo": station_no}) or {}
        for key in ("battery", "grid", "load", "pv"):
            data = await self.call(f"deve/v1/energy/detail/{key}", body)
            out[key] = data[0] if isinstance(data, list) and data else {}
        return out
