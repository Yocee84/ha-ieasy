"""The write lock ("Settings unlocked") and the on/off settings: TOU, peak shaving, grid charging."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, UNLOCK_SECONDS
from .entity import IEasySettingEntity
from .texts import UNLOCK_HELP, english_entity_id, help_attrs, name as localized

SWITCHES = (
    ("23011", "tou_enabled_set", "TOU enabled"),
    ("23007", "peak_shaving_set", "Peak shaving"),
    ("22975", "grid_charging_set", "Grid charging"),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IEasyUnlockSwitch(coordinator, entry),
                        *(IEasySettingSwitch(coordinator, entry, *s) for s in SWITCHES if s[0] in coordinator.settings)])


class IEasyUnlockSwitch(CoordinatorEntity, SwitchEntity):
    """Local only: while off, every write is refused. Turns itself off after UNLOCK_SECONDS."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:lock-open-variant"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator)
        sn = coordinator.device.get("deviceSn", entry.entry_id)
        self._attr_unique_id = f"{sn}_settings_unlocked"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, sn)})
        self._attr_name = localized("settings_unlocked", "Settings unlocked", coordinator.language)
        self.entity_id = english_entity_id("switch", coordinator, "Settings unlocked")
        self._attr_extra_state_attributes = {**help_attrs(None, coordinator.language, UNLOCK_HELP),
                                             "relocks_after_seconds": UNLOCK_SECONDS}

    @property
    def available(self) -> bool:
        return True

    @property
    def is_on(self) -> bool:
        return self.coordinator.unlocked

    async def async_turn_on(self, **kwargs) -> None:
        self.coordinator.set_unlocked(True)

    async def async_turn_off(self, **kwargs) -> None:
        self.coordinator.set_unlocked(False)


class IEasySettingSwitch(IEasySettingEntity, SwitchEntity):
    _entity_domain = "switch"

    @property
    def is_on(self):
        return None if self.raw_value is None else str(self.raw_value) == "1"

    async def async_turn_on(self, **kwargs) -> None:
        await self._write("1")

    async def async_turn_off(self, **kwargs) -> None:
        await self._write("0")
