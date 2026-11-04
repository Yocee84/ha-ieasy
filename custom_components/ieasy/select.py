"""TOU slot function (idle / charge / discharge) as select entities."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity

from .const import DOMAIN, TOU_SLOTS
from .entity import IEasySettingEntity
from .texts import SELECT_LABELS


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(IEasyTouFunction(coordinator, entry, fun, f"tou_t{i}_function_set", f"TOU T{i} function")
                       for i, (fun, *_) in enumerate(TOU_SLOTS, start=1) if fun in coordinator.settings)


class IEasyTouFunction(IEasySettingEntity, SelectEntity):
    _entity_domain = "select"
    def __init__(self, coordinator, entry, code, key, name) -> None:
        super().__init__(coordinator, entry, code, key, name)
        self._labels = SELECT_LABELS.get(coordinator.language, SELECT_LABELS["en"])
        self._attr_options = list(self._labels.values())

    @property
    def current_option(self):
        return self._labels.get(str(self.raw_value))

    async def async_select_option(self, option: str) -> None:
        code = next(c for c, label in self._labels.items() if label == option)
        await self._write(code)
