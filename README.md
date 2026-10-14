# Gridfees AUT

Home Assistant integration for Austrian variable electricity grid fees and levies,
expressed in EUR/kWh excluding VAT.

## Status: 0.2.0 — price sensors

Configure a grid area, supply type, and applicable tax and SNAP settings. Multiple
different profiles can be configured; identical profiles are rejected. To change a
profile in this version, remove it and create a new one.

Each profile creates six price sensors and one binary sensor:

| Entity | Unit |
| --- | --- |
| Total grid fees and levies | EUR/kWh |
| Grid usage fee | EUR/kWh |
| Grid loss fee | EUR/kWh |
| Electricity tax | EUR/kWh |
| Renewable support contribution (grid usage) | EUR/kWh |
| Renewable support contribution (grid loss) | EUR/kWh |
| SNAP active | On/off |

Price sensors use measurement statistics. They represent unit prices, not
accumulated costs. The total is the sum of the five fee and levy components.

## Supported tariffs

- 14 Austrian grid tariff areas.
- Grid level 7, non-metered capacity, single tariff.
- Regular grid supply and allocated local or regional renewable energy community
  (EEG) energy.
- Supported dates: **January 1, 2022 through December 31, 2026**.
- Tariff boundaries evaluated in `Europe/Vienna`, independently of the system's
  configured timezone.

Prices are calculated when a profile loads and refreshed at each UTC hour
boundary. This covers Vienna midnight, seasonal tariff changes, and the 10:00 and
16:00 SNAP boundaries. Unchanged snapshots do not trigger unnecessary entity
updates. The refresh timer is removed when a profile unloads.

SNAP applies to eligible regular grid supply during the configured 2026 summer
window. The published reduced grid usage rates are used directly. EEG profiles
receive their applicable grid usage reduction instead; SNAP is not added. EEG
reductions use commercial rounding to two decimals in cents before conversion
to EUR/kWh. EEG electricity tax exemption is separate from the grid usage
reduction. Kleinwalsertal is treated separately for electricity tax.

EEG profiles apply only to allocated community energy. Create a separate regular
grid supply profile for residual supply; joining an EEG does not make all energy
eligible for EEG rates.

The scope excludes the energy purchase price, VAT, fixed basic and capacity
charges, metering charges, local levies, biomass subsidies, and renewable support
lump sums. Hypothetical winter tariff scenarios are outside the regular model.

**No extrapolation:** all price sensors and SNAP status become unavailable outside
the supported date range. Updated tariff data must be supplied in a new integration
version before 2027. The `tariff_valid_until` attribute is an exclusive boundary.

## Installation and verification

1. Copy the entire `custom_components/gridfees_aut` folder into the Home Assistant
   configuration directory. The resulting path must be
   `<config>/custom_components/gridfees_aut/manifest.json`.
2. Restart Home Assistant.
3. Open **Settings → Devices & services → Add integration** and search for
   **Gridfees AUT**.
4. Select a grid area and supply type, then confirm the tariff assumptions.
5. Open the profile and verify its six price sensors and SNAP status. Existing
   profiles from 0.1.x receive the sensors after updating the files and restarting.
6. Check that the total equals the five fee components. For a Burgenland regular
   household profile, the 2026 total outside SNAP hours is **0.09180 EUR/kWh**;
   during eligible SNAP hours it is **0.07490 EUR/kWh**.
7. Optionally add a different profile and remove it. Adding an identical profile
   should display an already-configured message.

The files must be installed on the Home Assistant system. When working through
Home Assistant Cloud, use an available file editor with upload support or
Studio Code Server to transfer them.

The repository includes initial HACS metadata. HACS distribution requires a
public repository; this project is not currently listed in the HACS default catalog.

## Tariff data and maintenance

`custom_components/gridfees_aut/tariffs.json` contains the dated grid usage and
loss rates, electricity tax rates, renewable support contribution rates, EEG
factors, and SNAP windows. Grid rates are stored in cents/kWh; tax and support
contributions are stored in EUR/kWh. Decimal strings preserve published precision.

For updates, add the new dated rates, check all applicable tax and support rules,
and extend the dataset's exclusive `valid_until` boundary only when the required
rates are available. Update the regression fixtures and integration version too.

Source references:

- [System Charges Ordinance, April 2026 consolidated version](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010107&FassungVom=2026-04-01),
  with historical grid tariff tables from January 2022, January/March 2023,
  January 2024, January 2025, and January 2026.
- Renewable support contribution ordinances: BGBl. II No. 419/2024 and
  No. 301/2025, section 2, grid level 7 bb).
- Electricity tax: ElAbgG sections 1, 2, 4, and 7.
- EEG support contribution exemption: EAG section 75(5).

## Development and checks

Run the offline calculation tests from the repository root:

```sh
python -m unittest discover -s tests -v
```

Tests cover the 84 region/period tariff records across all three supply types,
explicit reference prices, tariff and tax boundaries, SNAP, EEG, rounding,
Kleinwalsertal, timezone conversion, unsupported years, and invalid inputs.

The calculation engine also provides interval-start time series over a chosen
range. It steps in UTC, producing 92, 96, or 100 quarter-hour values per Vienna
day as appropriate. A Home Assistant action for requesting these series is not
yet exposed; the entities currently show the price applicable now.

Python syntax, JSON files, and English interface text are checked locally.
Runtime verification of entity setup and reload in Home Assistant remains pending.

References: [Config flow](https://developers.home-assistant.io/docs/core/integration/config_flow/),
[Sensor entities](https://developers.home-assistant.io/docs/core/entity/sensor/),
and [Manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/).
