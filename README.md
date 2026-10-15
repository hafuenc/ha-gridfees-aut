# Gridfees AUT

> **🚧 Beta — under active development**
>
> This integration is still under development. Features, configuration options,
> and calculations may change, and errors may occur.
>
> All calculated prices and forecasts are provided for informational purposes
> only. Verify the results against the applicable regulations and your grid
> operator’s published tariffs before relying on them.
>
> **Use at your own risk.** This software is provided “as is”, without warranty
> of any kind. To the extent permitted by law, the authors and contributors
> accept no liability for errors, financial losses, or other damages arising
> from its use.

<img src="custom_components/gridfees_aut/brand/icon.png" alt="Gridfees AUT icon" width="128">

Home Assistant integration for Austrian variable grid fees and levies,
expressed in EUR/kWh excluding VAT.

## Status: 0.6.1 (Beta)

Configure a grid area and supply type. Regular grid supply profiles additionally
ask for the household load-profile rate, SNAP eligibility, and optional WiNAP
simulation. Local and regional
EEG profiles need no tax switches: Elektrizitätsabgabe is automatically zero for
their allocated EEG energy. Multiple different profiles can be configured;
identical profiles are rejected. To change the assumptions of an existing regular
grid profile, open its entry menu under **Settings → Devices & services → Gridfees
AUT** and select **Reconfigure**. The profile and its entity IDs are preserved.

The default profile and device name follows this pattern:

```text
gridfees Steiermark Regular grid supply
```

Grid areas use the German names from the ordinance. Interface instructions remain
English; official German names for Entgelte, Steuern, and Abgaben are retained.

## Sensors

Each profile registers six price sensors and one binary sensor:

| Entity | Unit | Enabled by default |
| --- | --- | --- |
| Total grid fees | EUR/kWh | Yes |
| Netznutzungsentgelt | EUR/kWh | No |
| Netzverlustentgelt | EUR/kWh | No |
| Elektrizitätsabgabe | EUR/kWh | No |
| Erneuerbaren-Förderbeitrag (Netznutzungsentgelt) | EUR/kWh | No |
| Erneuerbaren-Förderbeitrag (Netzverlustentgelt) | EUR/kWh | No |
| SNAP active | On/off | Yes |

The five detail sensors are registered as disabled entities. Enable only the
ones you need in **Settings → Devices & services → Entities**, including disabled
entities in the filter. Disabled entities do not publish state updates or create
new Recorder history/statistics. Their components remain included in Total grid fees.

Price sensors use measurement statistics. They represent unit prices, not
accumulated costs. The total is the sum of the five fee and levy components.

## Tax treatment

For **Regular grid supply**, the setup asks for:

- **Reduced Elektrizitätsabgabe for household load profiles**: selects the
  applicable reduced rate for eligible metering points with household load
  profiles **H0, HA, or HF**. For 2026, § 7 Abs. 16 ElAbgG refers to the eligible
  persons under § 4 Abs. 1 Stromkostenzuschussgesetz. The setup help includes
  links to both provisions. This selects a reduced rate, not a tax exemption.
- **Eligible for SNAP (Sommer-Nieder-Arbeitspreis)**: selects whether the published
  SNAP reduction can apply. See [§ 2 Abs. 1 Z 9 und § 5 Abs. 1b SNE-V 2018](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010107).
- **Simulate WiNAP (Winter-Nieder-Arbeitspreis)**: enables the optional winter
  scenario described below. It is **off by default** and independent of the
  summer SNAP setting.

For **Local EEG** and **Regional EEG**, Elektrizitätsabgabe is **automatically
zero** for allocated EEG energy. There is no exemption switch, household
rate question, or WiNAP simulation option. The household rate cannot change a
zero tax component.
SNAP does not apply to these profiles. The grid reduction and exemption from
Erneuerbaren-Förderbeitrag are also applied automatically.

This models qualifying renewable EEG energy consumed within the community with
fulfilled allocation, evidence, and procedural requirements. Before July 2022,
the historical EEG calculations assume qualifying photovoltaic generation.
The exemption does not extend to residual supply purchased from a regular supplier;
configure that portion as a separate Regular grid supply profile.

Kleinwalsertal is treated separately for Elektrizitätsabgabe.

## Supported tariffs

- 14 Austrian grid tariff areas: Burgenland, Kärnten, Klagenfurt, Niederösterreich,
  Oberösterreich, Linz, Salzburg, Steiermark, Graz, Tirol, Innsbruck, Vorarlberg,
  Wien, and Kleinwalsertal.
- Netzebene 7, non-metered capacity, single tariff.
- Regular grid supply and allocated local or regional EEG energy.
- Supported dates: **January 1, 2022 through December 31, 2026**.
- Tariff boundaries evaluated in `Europe/Vienna`, independently of the system's
  configured timezone. Forecast timestamps use the configured Home Assistant
  timezone; see below.

Prices are calculated when a profile loads and refreshed at each UTC hour
boundary. This covers Vienna midnight, seasonal tariff changes, and the 10:00 and
16:00 SNAP boundaries, as well as the 23:00 and 05:00 simulation boundaries.
Unchanged snapshots do not trigger unnecessary entity
updates within the same hour. The forecast advances hourly even when the current
unit price stays constant. The refresh timer is removed when a profile unloads.

SNAP (Sommer-Nieder-Arbeitspreis) applies to eligible regular grid supply during
the configured 2026 summer window. Published reduced Netznutzungsentgelt rates
are used directly. EEG profiles receive their applicable Netznutzungsentgelt
reduction instead; SNAP is not added. EEG reductions use commercial rounding to
two decimals in cents before conversion to EUR/kWh.

EEG profiles apply only to allocated community energy. Create a separate regular
grid supply profile for residual supply; joining an EEG does not make all energy
eligible for EEG rates.

The scope excludes the energy purchase price, VAT, fixed Grund-/Leistungspreise,
Entgelte für Messleistungen, local levies, biomass subsidies, and
Erneuerbaren-Förderpauschale. WiNAP is available only as the explicit simulation
option below; it is not part of the published tariff calculation.

**No extrapolation:** all price sensors and SNAP status become unavailable outside
the supported date range. Updated tariff data must be supplied in a new integration
version before 2027. The `tariff_valid_until` attribute is an exclusive boundary.

## Optional WiNAP simulation

**Simulate WiNAP (Winter-Nieder-Arbeitspreis)** is off by default. Enabling it
replaces only the variable Netznutzungsentgelt with the selected tariff's
published SNAP price during winter nights. Other fees, taxes, and contributions
remain calculated under their normal rules. This is a fictional scenario, not
an announced WiNAP rate or an estimate of the future rate.

The winter window covers nights **starting from 1 October through 31 March**,
from **23:00 to 05:00 the following day**, in Europe/Vienna. Consequently, the
first night starts at 23:00 on 1 October and the last night ends at 05:00 on
1 April. The overnight window follows local time through daylight saving changes.
The simulation uses SNAP prices available in the **2026** dataset; it does not
invent reduced prices for 2022–2025 or extend tariff validity into 2027.

The legal WiNAP first applies from **1 October 2027** under
[§ 7 Abs. 4 und § 32 Abs. 4 SNE-G-V, BGBl. II Nr. 299/2026](https://ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2026_II_299/BGBLA_2026_II_299.html).
Future published prices require a separate tariff-data update.

The switch is available only for **Regular grid supply**. It can be enabled
independently of summer SNAP eligibility; enabling it explicitly requests a
fictional scenario. Allocated EEG energy never receives a simulated WiNAP
reduction in addition to its existing EEG reduction.

Total grid fees and its seven-day forecast both use the selected scenario.
Price sensor attributes identify `winap_simulation_enabled`,
`winap_simulated_active`, and `pricing_mode` (`published_tariffs` or
`winap_simulation`). **SNAP active remains off during simulated winter nights**;
it continues to describe the actual summer SNAP window only. The simulation
markers remain in Recorder attributes so historical simulated prices can be
identified. Turning the simulation off does not rewrite recorded history.

## Seven-day forecast on Total grid fees

The **Total grid fees** sensor exposes its forecast in the `data` attribute.
It contains **periods of constant price**: consecutive hours with the same total
are combined, and a new row starts only when the price changes, such as at the
start or end of a SNAP window. With a constant price, one row covers all seven
days. The horizon starts at the beginning of the current UTC hour and extends
168 hours. The window advances on each hourly refresh. This is a rolling
seven-times-24-hour horizon, not seven local calendar dates.

Each row follows this format:

```yaml
data:
  - start_time: '2026-06-01T09:00:00+02:00'
    end_time: '2026-06-01T10:00:00+02:00'
    price_eur_per_kwh: 0.0918
  - start_time: '2026-06-01T10:00:00+02:00'
    end_time: '2026-06-01T16:00:00+02:00'
    price_eur_per_kwh: 0.0749
  - start_time: '2026-06-01T16:00:00+02:00'
    end_time: '2026-06-02T10:00:00+02:00'
    price_eur_per_kwh: 0.0918
  # Further price periods continue through the seven-day horizon.
```

This example uses a regular Burgenland household profile. All values are net
**grid fees and levies**, not exchange energy prices. Forecasts use the selected
profile's SNAP, EEG, tax, and optional WiNAP simulation assumptions. They are calculated from the supported
tariff schedule rather than estimated market prices.

Additional attributes identify `forecast_start`, `forecast_end`, `forecast_hours`,
`forecast_interval_mode: change_of_value`, `forecast_timezone`, `tariff_timezone`, and
`forecast_complete`. If any forecast hour falls outside supported tariff dates,
the `price_eur_per_kwh` field for that row is `null` and `forecast_complete` is `false`.
The window still covers 168 hours; consecutive unsupported hours form one null
period. Missing rates are never replaced by zero or carried forward from another year.

Only Total grid fees carries the forecast. It is available to dashboard cards,
templates, and automations through the live `data` attribute. The forecast table
and its metadata are excluded from Recorder history to avoid storing a large
rolling table every hour. The sensor's current price and its measurement
statistics remain recordable according to your Recorder configuration. Historical
forecast tables are therefore not available through the history API.

### Clock and timezone

The integration already reads Home Assistant's current system clock as an aware
UTC instant. The PC used to configure the integration does not supply its clock.

**Tariff calculation always uses Europe/Vienna.** A 10:00 SNAP boundary means
10:00 in Austria. Substituting another system timezone for tariff rules would
shift the applicable price, so that is not used as a calculation setting.

**Forecast timestamps use Home Assistant's configured timezone** from
**Settings → System → General**. If it is Europe/Vienna, the timestamps use the
correct +01:00/+02:00 offset. If it is UTC or another timezone, the same instants
are displayed in that timezone with unchanged prices. Timezone changes take
effect on the next refresh or integration reload.

The calculation advances in UTC to avoid duplicate or missing physical hours at
clock changes, then combines equal prices. Periods may span a clock change and
therefore have different UTC offsets at their start and end. The rolling horizon
always covers 168 actual hours, including weeks with a daylight saving change.

## Installation and verification

### HACS (recommended)

Requires Home Assistant **2026.3 or newer** and a configured HACS installation.
This repository is added as a **custom repository**; it is not yet included in
the HACS default catalog.

1. Open **HACS → ⋮ → Custom repositories**.
2. Enter `https://github.com/hafuenc/ha-gridfees-aut`, select **Integration**,
   and click **Add**.
3. Find **Gridfees AUT** in HACS, open it, and select **Download**. Choose the
   latest released version.
4. Restart Home Assistant.
5. Open **Settings → Devices & services → Add integration → Gridfees AUT**
   and configure a tariff profile.

For future versions, use the update offered by HACS and restart Home Assistant.
HACS manages the integration files; tariff profile settings remain in Home Assistant.

#### Moving an existing manual installation to HACS

Keep your configured Gridfees AUT profiles and the existing
`/config/custom_components/gridfees_aut` folder. Add the custom repository and
download the release through HACS as above, then restart Home Assistant.
HACS replaces the integration files in the same folder. Existing settings,
entity IDs, and history are preserved; no new tariff profile is needed.
Any personal edits to the integration files will be replaced by the release.

### Manual installation

1. Copy the entire `custom_components/gridfees_aut` folder into the Home Assistant
   configuration directory. The resulting path must be
   `<config>/custom_components/gridfees_aut/manifest.json`.
2. Include `brand/icon.png` and `translations/en.json` in their respective subfolders.
3. Restart Home Assistant and reload the browser page.
4. Open **Settings → Devices & services → Add integration** and search for
   **Gridfees AUT**.
5. Select a grid area and supply type. For regular grid supply, confirm the
   household load-profile rate, SNAP assumptions, and optional WiNAP simulation. EEG profiles finish directly
   after the grid area and supply type selection.
6. Open the profile and verify Total grid fees and SNAP active. The five detail
   sensors are available as disabled entities and can be enabled individually.
7. For a Burgenland regular household profile, the 2026 total outside SNAP hours
   is **0.09180 EUR/kWh**; during eligible SNAP hours it is **0.07490 EUR/kWh**.
   Enable the five detail sensors if you want to inspect the sum.

The files must be installed on the Home Assistant system. When working through
Home Assistant Cloud, use an available file editor with upload support or
Studio Code Server to transfer them.

The integration icon is packaged in `brand/icon.png`. Home Assistant 2026.3 or
newer supports these local brand images. No extra image configuration is needed.

### Updating from an earlier version

For **0.6.0**, install the HACS update and restart Home Assistant. Existing
profiles, enabled entities, entity IDs, and saved household/SNAP choices are
preserved. WiNAP simulation is initially off. To enable it for an existing
regular grid profile, select **Reconfigure** in that entry's menu. No profile
removal, manual file copying, or initial setup is required after an update.
The project is marked Beta in the documentation; releases use normal GitHub
release tags so HACS offers them without enabling prerelease downloads.

Replace the integration files, including subfolders, and restart Home Assistant.
Version 0.5.2 restores the `service` integration type so Gridfees AUT appears in
**Add integration**. Version 0.5.1 used `entity`, which Home Assistant excludes
from that list. Home Assistant controls the **Services** heading based on this
type. Existing profiles and entity IDs are preserved. For this update alone,
replace `manifest.json`, restart Home Assistant, and refresh the browser page.

Version 0.4.0 adds the forecast automatically to existing Total grid fees sensors;
no profile recreation is needed for the forecast. Verify `data` under
**Developer tools → States** after updating.

Existing profiles receive the new official component names and generated device
names. Generated profile titles from older versions are updated; custom titles
and user-assigned device names are preserved. Entity unique IDs and existing
entity IDs remain stable, so existing references continue to work.

Home Assistant preserves the enabled/disabled state of entities that are already
registered. **If your five detail sensors were created enabled in 0.2.x, disable
those you do not need once in the entity settings.** The new defaults apply when
entities are first registered. Previously recorded history is not deleted.

Version 0.5.0 automatically migrates existing profiles and removes the retired
EEG exemption setting. All local and regional EEG profiles, including those that
previously had the exemption switched off, now use zero Elektrizitätsabgabe.
The current total and its seven-day forecast are recalculated. Regular grid supply
keeps its saved household and SNAP choices. Profile recreation is not required,
and existing entity IDs and historical records remain unchanged.

HACS distribution requires a public repository and a published GitHub release.
See [Release preparation](docs/releasing.md) for the maintainer workflow.

## Legal sources and tariff data

See [Legal sources](docs/legal_sources.md) for all dated links and the provisions
used for the dataset:

- **Systemnutzungsentgelte-Verordnung 2018 (SNE-V 2018)**, §§ 2, 5, and 6;
  all relevant consolidated versions from 2022 through April 2026.
- **Erneuerbaren-Förderbeitragsverordnung 2025**, BGBl. II Nr. 419/2024,
  and **Erneuerbaren-Förderbeitragsverordnung 2026**, BGBl. II Nr. 301/2025,
  § 2 Abs. 2 and 3, Netzebene 7 bb.
- **Elektrizitätsabgabegesetz (ElAbgG)**, §§ 1, 2, 4, and 7, including
  Kleinwalsertal, EEG exemptions, and the 2026 household rate in § 7 Abs. 16.
- **Erneuerbaren-Ausbau-Gesetz (EAG)**, § 75 Abs. 5.
- **Systemnutzungsentgelte-Grundsatzverordnung (SNE-G-V)**, § 7 Abs. 4 and
  § 32 Abs. 4, for the WiNAP simulation window and first legal application date.

`custom_components/gridfees_aut/tariffs.json` contains the dated rates, EEG
factors, and SNAP windows. The optional winter scenario uses those SNAP prices
without adding a fictional rate to the legal tariff dataset. Netznutzungsentgelt and Netzverlustentgelt are stored
in cents/kWh; Elektrizitätsabgabe and Erneuerbaren-Förderbeitrag components are
stored in EUR/kWh. Decimal strings preserve published precision.

For updates, add the new dated rates, check all applicable tax and support rules,
and extend the dataset's exclusive `valid_until` boundary only when the required
rates are available. Update the regression fixtures and integration version too.

## Development and checks

Run the offline tests from the repository root:

```sh
python -m unittest discover -s tests -v
```

Tests cover the 84 region/period tariff records across all three supply types,
explicit reference prices, tariff and tax boundaries, SNAP, WiNAP simulation, EEG, rounding,
Kleinwalsertal, timezone conversion, unsupported years, invalid inputs, standard
automatic EEG exemption, legacy profile normalization, and generated profile names.

Forecast tests also cover the requested EUR/kWh-only attribute format,
hourly rolling updates when the current price does not change, 168-hour windows
across both daylight saving changes, different display timezones, and unsupported
future rates. The calculation engine additionally supports custom interval-start
time series; a separate Home Assistant action for arbitrary ranges is not exposed.

The calculation tests, HACS validation, and Home Assistant hassfest checks run
on GitHub for pushes and pull requests. Setup, reconfiguration and migration
tests also run against Home Assistant 2026.3, the minimum supported version.
Version 0.5.2 was also checked in Home
Assistant: it appears in Add integration and opens the tariff setup dialog.

References: [Config flow](https://developers.home-assistant.io/docs/core/integration/config_flow/),
[Sensor entities](https://developers.home-assistant.io/docs/core/entity/sensor/),
[Disabled entities](https://developers.home-assistant.io/docs/entity_registry_disabled_by/),
and [Brand images](https://developers.home-assistant.io/docs/core/integration/brand_images/).
