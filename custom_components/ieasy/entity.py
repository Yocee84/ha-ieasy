"""Shared base for the writable setting entities (number, switch, select, time)."""
from __future__ import annotations

from typing import Any

from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import IEasyApiError
from .const import DOMAIN
from .texts import english_entity_id, help_attrs, name as localized


class IEasySettingEntity(CoordinatorEntity):
    """One setting point of the inverter. Reads come from the settings tree, writes go through the coordinator."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    _entity_domain = ""  # set by each platform

    def __init__(self, coordinator, entry, code: str, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._code = code
        sn = coordinator.device.get("deviceSn", entry.entry_id)
        self._attr_unique_id = f"{sn}_{key}"
        self._attr_name = localized(key, name, coordinator.language)
        self.entity_id = english_entity_id(self._entity_domain, coordinator, name)
        self._attr_extra_state_attributes = help_attrs(code, coordinator.language)
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, sn)})

    @property
    def node(self) -> dict[str, Any]:
        return self.coordinator.settings.get(self._code) or {}

    @property
    def available(self) -> bool:
        return super().available and bool(self.node)

    @property
    def raw_value(self) -> Any:
        return ((self.coordinator.data or {}).get("settings") or {}).get(self._code)

    async def _write(self, value: str) -> None:
        try:
            await self.coordinator.write_setting(self._code, value)
        except IEasyApiError as err:
            raise HomeAssistantError(str(err)) from err
