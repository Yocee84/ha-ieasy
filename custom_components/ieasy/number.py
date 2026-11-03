"""The only writable value: the grid zero-export offset (point 22013).

Every write goes through the app's setting-task API and is only accepted when the inverter
confirms the requested value.
"""
from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfPower
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import IEasyApiError
from .const import DOMAIN

OFFSET_POINT = "22013"


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IEasyOffsetNumber(coordinator, entry)])


class IEasyOffsetNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Zero-export offset"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = NumberDeviceClass.POWER
    _attr_mode = NumberMode.BOX
    _attr_native_step = 10

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator)
        sn = coordinator.device.get("deviceSn", entry.entry_id)
        self._attr_unique_id = f"{sn}_zero_export_offset"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, sn)})
        node = coordinator.settings.get(OFFSET_POINT) or {}
        cfg = node.get("typeCfgObj") if isinstance(node.get("typeCfgObj"), dict) else {}
        # Limits come from the app's own config for this point (0-600 W on MEI2-HT6H-AIO).
        self._attr_native_min_value = float(cfg.get("min") or 0)
        self._attr_native_max_value = float(cfg.get("max") or 600)

    @property
    def native_value(self):
        value = ((self.coordinator.data or {}).get("settings") or {}).get(OFFSET_POINT)
        try:
            return None if value is None else float(value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        if not self._attr_native_min_value <= value <= self._attr_native_max_value:
            raise HomeAssistantError(f"Offset must be between {self._attr_native_min_value:.0f} and "
                                     f"{self._attr_native_max_value:.0f} W")
        node = self.coordinator.settings.get(OFFSET_POINT)
        if not node:
            raise HomeAssistantError("Offset setting not found on this inverter")
        try:
            await self.coordinator.api.write_point(self.coordinator.device["deviceId"],
                                                   self.coordinator.device["deviceSn"], node, str(int(value)))
        except IEasyApiError as err:
            raise HomeAssistantError(str(err)) from err
        self.coordinator.refresh_settings_next()
        await self.coordinator.async_request_refresh()
