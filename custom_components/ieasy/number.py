"""Writable numeric settings: zero-export offset, peak-shaving limit, TOU slot power and SOC, SG Ready limits.

Every write goes through the app's setting-task API and is only accepted when the inverter
confirms the requested value. Writes are refused while "Settings unlocked" is off.
"""
from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTime
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, TOU_SLOTS
from .entity import IEasySettingEntity

W = UnitOfPower.WATT
# (point code, unique-id key, name, unit, step, upper cap). Limits come from the app's own config for the
# point; the cap only trims the peak-shaving limit, which the app allows up to 2^32-1 W.
NUMBERS = (
    ("22013", "zero_export_offset", "Zero-export offset", W, 10, None),
    ("23008", "peak_shaving_limit", "Peak shaving power limit", W, 100, 9450),
    *((power, f"tou_t{i}_power_set", f"TOU T{i} power limit", W, 100, None) for i, (_, _, _, power, _) in
      enumerate(TOU_SLOTS, start=1)),
    *((soc, f"tou_t{i}_soc_set", f"TOU T{i} SOC limit", PERCENTAGE, 1, None) for i, (_, _, _, _, soc) in
      enumerate(TOU_SLOTS, start=1)),
    ("23142", "sg_ready_low_soc_set", "SG Ready low SOC", PERCENTAGE, 1, None),
    ("23143", "sg_ready_high_soc_set", "SG Ready high SOC", PERCENTAGE, 1, None),
    ("23141", "sg_ready_cooling_time", "SG Ready smart mode cooling time", UnitOfTime.MINUTES, 1, None),
    ("23146", "sg_ready_export_threshold", "SG Ready grid export threshold", W, 100, None),
    ("23147", "sg_ready_import_threshold", "SG Ready grid import threshold", W, 100, None),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(IEasySettingNumber(coordinator, entry, *n) for n in NUMBERS if n[0] in coordinator.settings)


class IEasySettingNumber(IEasySettingEntity, NumberEntity):
    _entity_domain = "number"
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, entry, code, key, name, unit, step, cap) -> None:
        super().__init__(coordinator, entry, code, key, name)
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = NumberDeviceClass.POWER if unit == W else None
        self._attr_native_step = step
        cfg = self.node.get("typeCfgObj") if isinstance(self.node.get("typeCfgObj"), dict) else {}
        self._attr_native_min_value = float(cfg.get("min") or 0)
        high = float(cfg.get("max") or 100)
        self._attr_native_max_value = min(high, cap) if cap else high

    @property
    def native_value(self):
        try:
            return None if self.raw_value is None else float(self.raw_value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        if not self._attr_native_min_value <= value <= self._attr_native_max_value:
            raise HomeAssistantError(f"{self.name} must be between {self._attr_native_min_value:.0f} and "
                                     f"{self._attr_native_max_value:.0f}")
        await self._write(str(int(value)))
