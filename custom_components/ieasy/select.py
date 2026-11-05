"""Settings with a fixed list of options as select entities: TOU and SG Ready slot modes, working mode,
user scenario, grid level, manual charge control, SG Ready mode."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity

from .const import DOMAIN, SG_READY_SLOTS, TOU_SLOTS
from .entity import IEasySettingEntity
from .texts import OPTION_LABELS

# (point code, unique-id key, name, option labels key in texts.OPTION_LABELS)
SELECTS = (
    *((fun, f"tou_t{i}_function_set", f"TOU T{i} function", "tou_function")
      for i, (fun, *_) in enumerate(TOU_SLOTS, start=1)),
    ("22084", "working_mode_set", "Working mode", "working_mode"),
    ("13596", "user_scenario_set", "User scenario", "user_scenario"),
    ("23102", "grid_level_set", "Grid level", "grid_level"),
    ("13771", "charge_control_set", "Manual charge control", "charge_control"),
    ("23140", "sg_ready_mode_set", "SG Ready mode", "sg_ready_mode"),
    *((mode, f"sg_ready_t{i}_mode_set", f"SG Ready T{i} mode", "sg_ready_slot_mode")
      for i, (mode, *_) in enumerate(SG_READY_SLOTS, start=1)),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(IEasyOptionSelect(coordinator, entry, *s) for s in SELECTS if s[0] in coordinator.settings)


class IEasyOptionSelect(IEasySettingEntity, SelectEntity):
    _entity_domain = "select"

    def __init__(self, coordinator, entry, code, key, name, labels_key) -> None:
        super().__init__(coordinator, entry, code, key, name)
        labels = OPTION_LABELS[labels_key]
        labels = labels.get(coordinator.language, labels["en"])
        # Only offer what this inverter's own setting tree offers for the point.
        offered = {str(o.get("code")) for o in self.node.get("typeCfgObj") or [] if isinstance(o, dict)}
        self._labels = {c: label for c, label in labels.items() if not offered or c in offered}
        self._attr_options = list(self._labels.values())

    @property
    def current_option(self):
        return self._labels.get(str(self.raw_value))

    async def async_select_option(self, option: str) -> None:
        code = next(c for c, label in self._labels.items() if label == option)
        await self._write(code)
