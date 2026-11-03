# Hiconics iEasy+ for Home Assistant

Read-only Home Assistant integration for Midea / Hiconics PowerInfi hybrid inverters and batteries that are monitored through the **iEasy+** mobile app.

It logs in to the same cloud the app uses, polls once a minute and creates sensors for the battery, the grid (per phase), the load and the PV input. It never writes settings to the inverter.

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

The first station on the account and its first inverter are used.

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

## Sensors

| Group | Sensors |
|---|---|
| Battery | SOC, SOH, temperature, voltage, current, power, charge/discharge today and total |
| Grid | active power (raw, import is negative), import power, export power, power and voltage per phase (A/B/C), frequency, import/export today and total |
| Load | load power, backup load power, load today/total, backup load total |
| PV | PV power, PV1/PV2 power, PV today/total |

The `*_total` energy sensors are `total_increasing` and can be used directly in the Energy dashboard (solar: *PV total*, battery: *Battery charge total* / *Battery discharge total*).

Phase letters are the inverter's own labels. On the tested installation the app's phase order did not match the grid meter (A=L1, C=L2), so check yours against your meter before relying on per-phase values.

## Notes

- Update interval: 60 s. The cloud itself updates about once a minute.
- The login token lasts about 24 hours; the integration logs in again automatically.
- Brand icon: Home Assistant 2026.3+ shows it from `custom_components/ieasy/brand/`.

## License

MIT
