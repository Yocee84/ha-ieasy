"""Entity names and help texts per language (chosen in the config entry, not the HA UI language).

English names live next to the entity definitions; this file holds the other languages and the
help texts, which are keyed by the inverter's point code.
"""
from __future__ import annotations

from homeassistant.util import slugify

from .const import TOU_SLOTS

_PHASES = {"a": "A", "b": "B", "c": "C"}

HU_NAMES: dict[str, str] = {
    "battery_soc": "Akku töltöttség", "battery_soh": "Akku állapot (SOH)", "battery_temperature": "Akku hőmérséklet",
    "battery_voltage": "Akku feszültség", "battery_current": "Akku áram", "battery_power": "Akku teljesítmény",
    "battery_charge_today": "Akku töltés ma", "battery_discharge_today": "Akku kisütés ma",
    "battery_charge_total": "Akku töltés összesen", "battery_discharge_total": "Akku kisütés összesen",
    "battery_remaining_energy": "Akku maradék energia", "battery_nominal_energy": "Akku névleges energia",
    "battery_modules": "Akku modulok száma", "battery_type": "Akku típus", "battery_status": "Akku állapotkód",
    "grid_active_power": "Hálózati teljesítmény (nyers, vétel negatív)", "grid_import_power": "Hálózati vétel",
    "grid_export_power": "Hálózati betáplálás", "grid_frequency": "Hálózati frekvencia",
    "grid_reactive_power": "Hálózati meddő teljesítmény", "grid_power_factor": "Hálózati teljesítménytényező",
    "grid_import_today": "Hálózati vétel ma", "grid_export_today": "Hálózati betáplálás ma",
    "grid_import_total": "Hálózati vétel összesen", "grid_export_total": "Hálózati betáplálás összesen",
    "grid_import_month": "Hálózati vétel e hónapban", "grid_export_month": "Hálózati betáplálás e hónapban",
    "grid_import_year": "Hálózati vétel idén", "grid_export_year": "Hálózati betáplálás idén",
    "grid_status": "Hálózat állapotkód",
    "load_power": "Fogyasztás", "backup_load_power": "Backup fogyasztás", "load_today": "Fogyasztás ma",
    "load_total": "Fogyasztás összesen", "backup_load_total": "Backup fogyasztás összesen",
    "load_month": "Fogyasztás e hónapban", "load_year": "Fogyasztás idén", "backup_load_today": "Backup fogyasztás ma",
    "pv_power": "Napelem teljesítmény", "pv_today": "Napelem ma", "pv_total": "Napelem összesen",
    "pv_month": "Napelem e hónapban", "pv_year": "Napelem idén",
    "flow_inverter_state": "Inverter állapotkód", "flow_pv_state": "Napelem állapotkód", "flow_eps_state": "EPS állapotkód",
    "setting_working_mode": "Üzemmód (0 önfogyasztás, 1 eladás előbb, 2 backup)",
    "setting_user_scenario": "Felhasználói forgatókönyv (5 betáplálás, 7 nulla export)",
    "setting_cutoff_soc": "Kisütési alsó határ (SOC)", "setting_feed_enable": "Betáplálás engedélyezve",
    "setting_feed_power_limit": "Betáplálási teljesítménykorlát", "setting_grid_charging": "Hálózati töltés engedélyezve",
    "setting_grid_charging_power_limit": "Hálózati töltés teljesítménykorlát",
    "setting_peak_shaving": "Csúcslevágás engedélyezve", "setting_tou_enabled": "TOU engedélyezve",
    "setting_tou_days": "TOU aktív napok (1 hétfő .. 7 vasárnap)",
    "setting_pv_priority": "Napelem prioritás (0 akku, 1 fogyasztás)", "setting_max_power": "Maximális teljesítmény",
    "setting_peak_shaving_power_limit": "Csúcslevágás teljesítménykorlát", "setting_pv_input_limit": "Napelem bemeneti korlát",
    "setting_battery_type": "Akku típus (0 lítium BMS-sel, 2 feszültség mód, 99 nincs)",
    "setting_battery_activation": "Akku aktiválás engedélyezve", "setting_battery_pack_number": "Akku csomagok száma",
    "setting_battery_charge_current_limit": "Akku töltőáram korlát",
    "setting_battery_discharge_current_limit": "Akku kisütőáram korlát",
    "setting_pcs_stop_soc": "Inverter leállási SOC", "setting_pcs_recovery_soc": "Inverter visszakapcsolási SOC",
    "setting_low_battery_alarm_soc": "Alacsony akku riasztási SOC", "setting_battery_economy_mode": "Akku gazdaságos mód",
    "setting_winter_mode": "Téli mód", "setting_battery_warm_mode": "Akku melegítési mód (0 fűtés, 1 hőn tartás)",
    "setting_battery_heating": "Akku fűtés engedélyezve", "setting_battery_heating_min_soc": "Akku fűtés minimum SOC",
    "setting_battery_heating_target": "Akku fűtés célhőmérséklet",
    "setting_sg_ready_mode": "SG Ready mód (0 ki, 1 okos, 2 ütemezett)", "setting_sg_ready_low_soc": "SG Ready alsó SOC",
    "setting_sg_ready_high_soc": "SG Ready felső SOC", "setting_overload_enabled": "Túlterhelés engedélyezve",
    "setting_insulation_monitoring": "Szigetelésfigyelés engedélyezve", "setting_buzzer": "Hangjelzés engedélyezve",
    "zero_export_offset": "Nulla-export eltolás", "peak_shaving_limit": "Csúcslevágás teljesítménykorlát",
    "tou_enabled_set": "TOU engedélyezve", "peak_shaving_set": "Csúcslevágás", "grid_charging_set": "Hálózati töltés",
    "settings_unlocked": "Beállítások feloldva",
}
for _p, _P in _PHASES.items():
    HU_NAMES.update({
        f"grid_power_{_p}": f"Hálózati teljesítmény {_P} fázis", f"grid_voltage_{_p}": f"Hálózati feszültség {_P} fázis",
        f"grid_current_{_p}": f"Hálózati áram {_P} fázis", f"backup_voltage_{_p}": f"Backup feszültség {_P} fázis",
        f"backup_current_{_p}": f"Backup áram {_P} fázis", f"backup_power_{_p}": f"Backup teljesítmény {_P} fázis",
    })
HU_NAMES.update({"grid_frequency_b": "Hálózati frekvencia B fázis", "grid_frequency_c": "Hálózati frekvencia C fázis"})
for _n in "123":
    HU_NAMES.update({f"pv{_n}_power": f"PV{_n} teljesítmény", f"pv{_n}_voltage": f"PV{_n} feszültség",
                     f"pv{_n}_current": f"PV{_n} áram"})
for _i in range(1, 7):
    for _suffix, _word in (("function", "mód"), ("start", "kezdete"), ("end", "vége"),
                           ("power", "teljesítménykorlát"), ("soc", "SOC-határ")):
        HU_NAMES[f"tou_t{_i}_{_suffix}_set"] = f"TOU {_i}. sáv {_word}"
        HU_NAMES[f"setting_tou_t{_i}_{_suffix}"] = f"TOU {_i}. sáv {_word}"
    HU_NAMES[f"setting_tou_t{_i}_function"] = f"TOU {_i}. sáv mód (0 üresjárat, 1 töltés, 2 kisütés)"

# Help texts, keyed by point code: (English, Hungarian).
HELP: dict[str, tuple[str, str]] = {
    "22013": ("Offset of the zero-export control: instead of exactly 0 W the inverter aims at this much grid import, "
              "as a margin against feeding power back. App range 0-600 W.",
              "A nulla-export szabályozás eltolása: a gép nem pontosan 0 W-ra, hanem ennyi hálózati vételre szabályoz, "
              "hogy biztosan ne tápláljon vissza. Az app szerinti tartomány 0-600 W."),
    "23007": ("Peak shaving: when on, the battery covers the load above the peak shaving power limit, so grid import "
              "stays under that limit.",
              "Csúcslevágás: bekapcsolva a csúcslevágási korlát feletti fogyasztást az akku fedezi, így a hálózati "
              "vétel a korlát alatt marad."),
    "23008": ("Grid import above this power is covered from the battery while peak shaving is on. Minimum 1000 W.",
              "Csúcslevágás bekapcsolva: az e feletti hálózati vételt az akku fedezi. Legalább 1000 W."),
    "22975": ("Allows charging the battery from the grid (for example in a TOU slot set to charge).",
              "Engedélyezi az akku töltését a hálózatról (például egy töltésre állított TOU-sávban)."),
    "22992": ("Maximum power for charging the battery from the grid. Read-only here: the inverter does not confirm a "
              "write to this point, so it could not be verified.",
              "Az akku hálózati töltésének legnagyobb teljesítménye. Itt csak olvasható: erre a pontra a gép nem "
              "igazolja vissza az írást, így nem lehetne ellenőrizni."),
    "23011": ("Time-of-use schedule: when on, the battery follows the six time slots T1-T6.",
              "Időzóna-ütemezés (TOU): bekapcsolva az akku a hat idősáv (T1-T6) szerint működik."),
    "23048": ("Days of the week the TOU schedule is active on (1 Monday .. 7 Sunday).",
              "A hét azon napjai, amikor a TOU-ütemezés aktív (1 hétfő .. 7 vasárnap)."),
    "22084": ("Working mode of the inverter as set in the app.", "A gép üzemmódja, ahogy az appban be van állítva."),
    "13596": ("User scenario from the app's quick setup (5 feed-in, 7 zero export).",
              "Felhasználói forgatókönyv az app gyorsbeállításából (5 betáplálás, 7 nulla export)."),
    "22085": ("The battery is not discharged below this SOC in normal operation.",
              "Normál működésben az akku ennél a töltöttségnél lejjebb nem sül ki."),
    "13617": ("Whether feeding power into the grid is allowed.", "Engedélyezett-e a betáplálás a hálózatba."),
    "13634": ("Maximum power fed into the grid.", "A hálózatba táplált teljesítmény felső korlátja."),
    "23006": ("Where PV power goes first: the battery or the load.",
              "Hová megy először a napelem teljesítménye: az akkuba vagy a fogyasztókhoz."),
    "22087": ("Maximum power setting from the app's quick setup.", "Maximális teljesítmény az app gyorsbeállításából."),
    "13709": ("Upper limit of the PV input power.", "A napelem bemeneti teljesítmény felső korlátja."),
    "22970": ("Battery type the inverter is configured for.", "Az akku típusa, amire a gép be van állítva."),
    "22974": ("Whether battery activation is enabled.", "Engedélyezett-e az akku aktiválása."),
    "15036": ("Number of battery packs configured.", "A beállított akkucsomagok száma."),
    "13755": ("Upper limit of the battery charge current.", "Az akku töltőáramának felső korlátja."),
    "13754": ("Upper limit of the battery discharge current.", "Az akku kisütőáramának felső korlátja."),
    "23000": ("The inverter stops working from the battery at this SOC.",
              "Ennél a töltöttségnél a gép leáll az akkuról való működéssel."),
    "23001": ("After a stop, the inverter works from the battery again above this SOC.",
              "Leállás után e töltöttség felett indul újra az akkuról való működés."),
    "23002": ("Low battery alarm threshold.", "Alacsony akkutöltöttség riasztási küszöbe."),
    "22981": ("Battery economy mode as set in the app.", "Akku gazdaságos mód, ahogy az appban be van állítva."),
    "22985": ("Winter mode as set in the app.", "Téli mód, ahogy az appban be van állítva."),
    "15060": ("Battery warming: heating or keeping warm (insulation).", "Akku melegítés: fűtés vagy hőn tartás."),
    "15061": ("Whether the battery heater is allowed to run.", "Engedélyezett-e az akku fűtése."),
    "15062": ("The battery heater only runs above this SOC.", "Az akku fűtése csak e töltöttség felett működik."),
    "15063": ("Target temperature of the battery heater.", "Az akku fűtésének célhőmérséklete."),
    "23140": ("SG Ready signal (heat pump control): off, smart (SOC based) or schedule.",
              "SG Ready jel (hőszivattyú-vezérlés): ki, okos (töltöttség alapján) vagy ütemezett."),
    "23142": ("SG Ready smart mode: lower SOC threshold.", "SG Ready okos mód: alsó töltöttségi küszöb."),
    "23143": ("SG Ready smart mode: upper SOC threshold.", "SG Ready okos mód: felső töltöttségi küszöb."),
    "22048": ("Whether short overload operation is allowed.", "Engedélyezett-e a rövid túlterheléses működés."),
    "13602": ("Insulation resistance monitoring of the PV side.", "A napelem oldal szigetelési ellenállásának figyelése."),
    "22011": ("Buzzer of the inverter.", "A gép hangjelzése."),
}
for _i, (_fun, _start, _end, _power, _soc) in enumerate(TOU_SLOTS, start=1):
    _a = "az" if _i in (1, 5) else "a"  # Hungarian article: "az 1.", "az 5.", "a 2."
    HELP[_fun] = (f"What the battery does in slot T{_i}: idle, charge or discharge.",
                  f"Mit csinál az akku {_a} {_i}. sávban: üresjárat, töltés vagy kisütés.")
    HELP[_start] = (f"Start of slot T{_i} (HH:MM). Keep the slots from overlapping.",
                    f"{_a.capitalize()} {_i}. sáv kezdete (ÓÓ:PP). A sávok ne fedjék egymást.")
    HELP[_end] = (f"End of slot T{_i} (HH:MM). Keep the slots from overlapping.",
                  f"{_a.capitalize()} {_i}. sáv vége (ÓÓ:PP). A sávok ne fedjék egymást.")
    HELP[_power] = (f"Maximum charge or discharge power of the battery in slot T{_i}.",
                    f"Az akku legnagyobb töltő- vagy kisütő teljesítménye {_a} {_i}. sávban.")
    HELP[_soc] = (f"SOC limit of slot T{_i}: discharging goes down to it, charging goes up to it.",
                  f"{_a.capitalize()} {_i}. sáv töltöttségi határa: kisütésnél eddig sül ki, töltésnél eddig töltődik.")

UNLOCK_HELP = ("While off, every write from Home Assistant is refused, automations included. Turn on to change "
               "settings; it turns itself off again after 5 minutes.",
               "Kikapcsolva minden írást elutasít, az automatizmusokét is. Bekapcsolva lehet beállítást "
               "módosítani; 5 perc után magától kikapcsol.")

SELECT_LABELS = {"en": {"0": "Idle", "1": "Charge", "2": "Discharge"},
                 "hu": {"0": "Üresjárat", "1": "Töltés", "2": "Kisütés"}}


def name(key: str, english: str, language: str) -> str:
    return HU_NAMES.get(key, english) if language == "hu" else english


def help_attrs(code: str | None, language: str, texts: tuple[str, str] | None = None) -> dict[str, str]:
    """Extra state attributes with the help text in the chosen language (empty if there is none)."""
    texts = texts or HELP.get(code or "")
    if not texts:
        return {}
    return {"leírás": texts[1]} if language == "hu" else {"description": texts[0]}


def english_entity_id(domain: str, coordinator, english: str) -> str:
    """Entity IDs stay English whatever the language, so automations do not depend on it."""
    return f"{domain}.{slugify((coordinator.station.get('stationName') or 'iEasy') + ' ' + english)}"
