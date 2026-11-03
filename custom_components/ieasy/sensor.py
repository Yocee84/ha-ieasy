"""Sensors for the iEasy+ snapshot."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity, SensorEntityDescription,
                                             SensorStateClass)
from homeassistant.const import (PERCENTAGE, EntityCategory, UnitOfElectricCurrent, UnitOfElectricPotential,
                                 UnitOfEnergy, UnitOfFrequency, UnitOfPower, UnitOfTemperature)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

W, KWH, V, A = UnitOfPower.WATT, UnitOfEnergy.KILO_WATT_HOUR, UnitOfElectricPotential.VOLT, UnitOfElectricCurrent.AMPERE
P, E, U, I = SensorDeviceClass.POWER, SensorDeviceClass.ENERGY, SensorDeviceClass.VOLTAGE, SensorDeviceClass.CURRENT
M, T = SensorStateClass.MEASUREMENT, SensorStateClass.TOTAL_INCREASING


@dataclass(frozen=True, kw_only=True)
class IEasySensorDescription(SensorEntityDescription):
    group: str
    field: str = ""
    value_fn: Callable[[dict[str, Any]], Any] | None = None


def _num(group: str, field: str, key: str, name: str, unit, dclass, sclass, **kw) -> IEasySensorDescription:
    return IEasySensorDescription(key=key, name=name, group=group, field=field, native_unit_of_measurement=unit,
                                  device_class=dclass, state_class=sclass, **kw)


SENSORS: tuple[IEasySensorDescription, ...] = (
    # Battery
    _num("battery", "soc", "battery_soc", "Battery SOC", PERCENTAGE, SensorDeviceClass.BATTERY, M),
    _num("battery", "soh", "battery_soh", "Battery SOH", PERCENTAGE, None, M),
    _num("battery", "batteryTemp", "battery_temperature", "Battery temperature", UnitOfTemperature.CELSIUS,
         SensorDeviceClass.TEMPERATURE, M),
    _num("battery", "batteryVoltage", "battery_voltage", "Battery voltage", V, U, M),
    _num("battery", "batteryCurrent", "battery_current", "Battery current", A, I, M),
    _num("battery", "batteryPower", "battery_power", "Battery power", W, P, M),
    _num("battery", "chargeEnergyToday", "battery_charge_today", "Battery charge today", KWH, E, T),
    _num("battery", "dischargeEnergyToday", "battery_discharge_today", "Battery discharge today", KWH, E, T),
    _num("battery", "chargeEnergyTotal", "battery_charge_total", "Battery charge total", KWH, E, T),
    _num("battery", "dischargeEnergyTotal", "battery_discharge_total", "Battery discharge total", KWH, E, T),
    # Grid (the API reports import as negative activePower)
    _num("grid", "activePower", "grid_active_power", "Grid active power (raw, import negative)", W, P, M),
    IEasySensorDescription(key="grid_import_power", name="Grid import power", group="grid",
                           value_fn=lambda d: max(0.0, -float(d["activePower"])), native_unit_of_measurement=W,
                           device_class=P, state_class=M),
    IEasySensorDescription(key="grid_export_power", name="Grid export power", group="grid",
                           value_fn=lambda d: max(0.0, float(d["activePower"])), native_unit_of_measurement=W,
                           device_class=P, state_class=M),
    _num("grid", "gridPowerA", "grid_power_a", "Grid power phase A", W, P, M),
    _num("grid", "gridPowerB", "grid_power_b", "Grid power phase B", W, P, M),
    _num("grid", "gridPowerC", "grid_power_c", "Grid power phase C", W, P, M),
    _num("grid", "gridVoltageA", "grid_voltage_a", "Grid voltage phase A", V, U, M),
    _num("grid", "gridVoltageB", "grid_voltage_b", "Grid voltage phase B", V, U, M),
    _num("grid", "gridVoltageC", "grid_voltage_c", "Grid voltage phase C", V, U, M),
    _num("grid", "gridFrequencyA", "grid_frequency", "Grid frequency", UnitOfFrequency.HERTZ,
         SensorDeviceClass.FREQUENCY, M),
    _num("grid", "buyDaily", "grid_import_today", "Grid import today", KWH, E, T),
    _num("grid", "sellDaily", "grid_export_today", "Grid export today", KWH, E, T),
    _num("grid", "buyTotal", "grid_import_total", "Grid import total", KWH, E, T),
    _num("grid", "sellTotal", "grid_export_total", "Grid export total", KWH, E, T),
    # Load
    _num("load", "normalLoadPower", "load_power", "Load power", W, P, M),
    _num("load", "backupActivePower", "backup_load_power", "Backup load power", W, P, M),
    _num("load", "normalUsedDaily", "load_today", "Load today", KWH, E, T),
    _num("load", "normalUsedTotal", "load_total", "Load total", KWH, E, T),
    _num("load", "backupUsedTotal", "backup_load_total", "Backup load total", KWH, E, T),
    # PV
    _num("flow", "solarPower", "pv_power", "PV power", W, P, M),
    _num("pv", "pvPower1", "pv1_power", "PV1 power", W, P, M),
    _num("pv", "pvPower2", "pv2_power", "PV2 power", W, P, M),
    _num("pv", "solarDaily", "pv_today", "PV today", KWH, E, T),
    _num("pv", "solarTotal", "pv_total", "PV total", KWH, E, T),
)


def _setting(code: str, key: str, name: str, unit=None, numeric: bool = True) -> IEasySensorDescription:
    return IEasySensorDescription(
        key=f"setting_{key}", name=name, group="settings", field=code, native_unit_of_measurement=unit,
        state_class=M if numeric and unit else None, entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=None if numeric else (lambda d, c=code: d.get(c)),
    )


# Current inverter settings, read from the app's settings tree (point code -> sensor).
SETTING_SENSORS: tuple[IEasySensorDescription, ...] = (
    _setting("22084", "working_mode", "Working mode (0 self use, 1 sell first, 2 backup)"),
    _setting("13596", "user_scenario", "User scenario (5 feed-in, 7 zero export)"),
    _setting("22085", "cutoff_soc", "Cut-off SOC", PERCENTAGE),
    _setting("13617", "feed_enable", "Feed-in enabled"),
    _setting("13634", "feed_power_limit", "Feed-in power limit", W),
    _setting("22975", "grid_charging", "Grid charging enabled"),
    _setting("22992", "grid_charging_power_limit", "Grid charging power limit", W),
    _setting("23007", "peak_shaving", "Peak shaving enabled"),
    _setting("23011", "tou_enabled", "TOU enabled"),
    *(s for i, (fun, start, end, power, soc) in enumerate((
        ("13779", "13763", "13764", "23024", "23036"), ("13780", "13765", "13766", "23026", "23037"),
        ("13781", "13767", "13768", "23028", "23038"), ("13782", "13769", "13770", "23030", "23039"),
        ("13783", "13775", "13776", "23032", "23040"), ("13784", "13777", "13778", "23034", "23041")), start=1)
      for s in (
          _setting(fun, f"tou_t{i}_function", f"TOU T{i} function (0 idle, 1 charge, 2 discharge)"),
          _setting(start, f"tou_t{i}_start", f"TOU T{i} start", numeric=False),
          _setting(end, f"tou_t{i}_end", f"TOU T{i} end", numeric=False),
          _setting(power, f"tou_t{i}_power", f"TOU T{i} power limit", W),
          _setting(soc, f"tou_t{i}_soc", f"TOU T{i} SOC limit", PERCENTAGE),
      )),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(IEasySensor(coordinator, entry, d) for d in SENSORS + SETTING_SENSORS)


class IEasySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: IEasySensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        sn = coordinator.device.get("deviceSn", entry.entry_id)
        self._attr_unique_id = f"{sn}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, sn)},
            name=coordinator.station.get("stationName") or "iEasy",
            manufacturer="Hiconics / Midea",
            model=coordinator.device.get("deviceModel"),
            serial_number=sn,
        )

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get(self.entity_description.group) or {}
        try:
            if self.entity_description.value_fn:
                return self.entity_description.value_fn(data)
            value = data.get(self.entity_description.field)
            return None if value is None else float(value)
        except (KeyError, TypeError, ValueError):
            return None
