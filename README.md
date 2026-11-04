# Hiconics iEasy+ for Home Assistant

Home Assistant integration for Midea / Hiconics PowerInfi hybrid inverters and batteries that are monitored through the **iEasy+** mobile app.

It logs in to the same cloud the app uses, polls once a minute and creates sensors for the battery, the grid (per phase), the load, the backup output and the PV strings, plus diagnostic sensors with the current inverter settings (working mode, TOU slots, battery limits, SG Ready).

A few settings are **writable**: zero-export offset, peak shaving on/off and limit, grid charging on/off, TOU on/off, and the six TOU slots (function, start, end, power, SOC). A write is sent the same way the app does it and only counts as done when the inverter confirms the new value; otherwise Home Assistant shows an error.

Writes are protected by a **Settings unlocked** switch. It is off after every start, and turns itself off again 5 minutes after being switched on; while it is off every write is refused, including writes from automations (an automation that changes a setting turns the switch on first). Quick repeated changes of one value (stepping a number box) are debounced: only the last value is sent, 2 s after the last change.

> Unofficial. Not affiliated with Midea or Hiconics. The cloud API is undocumented and was worked out from the app, so it can change without notice.

## Tested with

- Midea PowerInfi G2, inverter model `MEI2-HT6H-AIO`, 10.2 kWh LFP battery (2 modules), EU site
- iEasy+ app 1.1.5 (Android)
- Home Assistant 2026.9

Other models that show up in iEasy+ will probably work; the sensors that a model does not report stay unavailable.

## Installation

### HACS

1. HACS → three dots → **Custom repositories**
2. Add this repository's URL, type **Integration**
3. Install **Hiconics iEasy+** and restart Home Assistant

### Manual

Copy `custom_components/ieasy` into your `config/custom_components/` folder and restart Home Assistant.

## Configuration

Settings → Devices & services → **Add integration** → *Hiconics iEasy+*

| Field | Value |
|---|---|
| Account | the email address you use in the iEasy+ app |
| Password | your iEasy+ password |
| Server URL | `https://ieasy.midea.com/` (default, same for every region) |
| Site name | pick the region you chose in the app (default: Europe) |
| Language | language of the entity names and help texts: English or Magyar (Hungarian) |

The first station on the account and its first inverter are used.

### Language and help texts

Entity names and help texts follow the language chosen for the integration, not the Home Assistant UI language. It can be changed later under the integration's **Configure** button; the integration reloads. Entries created before 0.3.0 follow the Home Assistant language if it is English or Hungarian.

Every setting entity carries a short help text in the `description` attribute (`leírás` in Hungarian); open the entity to read it. Entity IDs stay English in both languages, so automations do not depend on the language.

### Regions

Every production region in iEasy+ 1.1.5 uses the same server, `https://ieasy.midea.com`; only the site name differs. Choose the one matching the region you selected at login in the app:

| Region in the app | Site name |
|---|---|
| Europe | `INFO_REGION_COUNTRY_R_Europe` |
| Australia | `INFO_REGION_COUNTRY_C_Australia` |
| New Zealand | `Modbus_New_Zealand` |
| North America | `Modbus_North_America` |
| Latin America | `Register_Latin_America` |
| Asia Pacific & Central Asia | `Register_Asia_Pacific_Central_Asia` |
| India | `INFO_REGION_COUNTRY_C_India` |
| Africa | `INFO_REGION_COUNTRY_R_Africa` |

The list comes from the app and from the public endpoint `https://ess-eu.hiconics.com/v1/sys/index/server/sites` (header `ems_app_id: 1017`). Only Europe has been tested so far.

## Entities

| Group | Entities |
|---|---|
| Battery | SOC, SOH, temperature, voltage, current, power, remaining and nominal energy, charge/discharge today and total, modules, type, status code |
| Grid | active power (raw, import is negative), import power, export power, power, voltage and current per phase (A/B/C), frequency, reactive power, power factor, import/export today, month, year and total, status code |
| Load | load power, backup load power, load today/month/year/total, backup load today/total |
| Backup (EPS) output | voltage, current and power per phase |
| PV | PV power, PV1-PV3 power, voltage and current, PV today/month/year/total |
| States (diagnostic) | inverter, PV and EPS state codes |
| Settings (diagnostic) | working mode, user scenario, cut-off SOC, feed-in enabled/limit, grid charging enabled/limit, peak shaving enabled/limit, TOU enabled, TOU active days, TOU T1-T6 function/start/end/power/SOC, PV priority, max power, PV input limit, battery type/activation/packs, charge and discharge current limits, PCS stop/recovery SOC, low battery alarm SOC, economy mode, winter mode, battery heating, SG Ready mode and SOC limits, overload, insulation monitoring, buzzer |
| Writable (configuration) | Settings unlocked (switch), zero-export offset, peak shaving limit, TOU T1-T6 power and SOC (number); TOU enabled, peak shaving, grid charging (switch); TOU T1-T6 function (select); TOU T1-T6 start and end (time) |

The grid charging power limit stays read-only: the app sends it without asking the inverter for a confirmation, so a write could not be verified.

Settings are re-read every 10 minutes and right after a write.

The `*_total` energy sensors are `total_increasing` and can be used directly in the Energy dashboard (solar: *PV total*, battery: *Battery charge total* / *Battery discharge total*).

Phase letters are the inverter's own labels. On the tested installation the app's phase order did not match the grid meter (A=L1, C=L2), so check yours against your meter before relying on per-phase values.

## Notes

- Update interval: 60 s. The cloud itself updates about once a minute.
- Writing settings needs an account that can change settings in the app.
- The login token lasts about 24 hours; the integration logs in again automatically.
- Brand icon: Home Assistant 2026.3+ shows it from `custom_components/ieasy/brand/`.

## License

MIT
