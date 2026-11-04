"""TOU slot function (idle / charge / discharge) as select entities."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity

from .const import DOMAIN, TOU_SLOTS
from .entity import IEasySettingEntity

LABELS = {"0": "Idle", "1": "Charge", "2": "Discharge"}


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(IEasyTouFunction(coordinator, entry, fun, f"tou_t{i}_function_set", f"TOU T{i} function")
                       for i, (fun, *_) in enumerate(TOU_SLOTS, start=1) if fun in coordinator.settings)


class IEasyTouFunction(IEasySettingEntity, SelectEntity):
    _attr_options = list(LABELS.values())

    @property
    def current_option(self):
        return LABELS.get(str(self.raw_value))

    async def async_select_option(self, option: str) -> None:
        code = next(c for c, label in LABELS.items() if label == option)
        await self._write(code)
