"""TOU slot start and end times as time entities (HH:MM)."""
from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity

from .const import DOMAIN, TOU_SLOTS
from .entity import IEasySettingEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for i, (_, start, end, _, _) in enumerate(TOU_SLOTS, start=1):
        entities += [IEasyTouTime(coordinator, entry, start, f"tou_t{i}_start_set", f"TOU T{i} start"),
                     IEasyTouTime(coordinator, entry, end, f"tou_t{i}_end_set", f"TOU T{i} end")]
    async_add_entities(e for e in entities if e._code in coordinator.settings)


class IEasyTouTime(IEasySettingEntity, TimeEntity):
    _entity_domain = "time"
    @property
    def native_value(self):
        try:
            hours, minutes = str(self.raw_value).split(":")
            return time(int(hours), int(minutes))
        except (TypeError, ValueError):
            return None

    async def async_set_value(self, value: time) -> None:
        await self._write(value.strftime("%H:%M"))
