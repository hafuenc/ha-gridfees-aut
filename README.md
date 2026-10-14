# Gridfees AUT

Home Assistant integration for Austrian variable electricity grid fees and levies,
expressed in EUR/kWh excluding VAT.

## Status: 0.1.1 — configuration scaffold

This development version provides an English setup flow for tariff profiles.
Select a grid area, supply type, and applicable tax and SNAP settings. Multiple
different profiles can be configured; identical profiles are rejected.

**Price calculations, sensors, and time series are not implemented yet.**
The initial setup verifies that the integration loads and saves a tariff profile.
To change a profile in this version, remove it and create a new one.

## Manual installation and verification

1. Copy the entire `custom_components/gridfees_aut` folder into the Home Assistant
   configuration directory. The resulting path must be
   `<config>/custom_components/gridfees_aut/manifest.json`.
2. Restart Home Assistant.
3. Open **Settings → Devices & services → Add integration** and search for
   **Gridfees AUT**.
4. Select a grid area and supply type, then confirm the tariff assumptions.
5. Verify that the profile appears under Devices & services. This version does
   not create devices or entities.
6. Optionally add a different profile and remove it. Adding an identical profile
   should display an already-configured message.

The files must be installed on the Home Assistant system. When working through
Home Assistant Cloud, use an available file editor with upload support or
Studio Code Server to transfer them.

The repository includes the initial HACS metadata. HACS distribution requires a
public repository; this project is not currently listed in the HACS default catalog.

## Planned calculation scope

- 14 Austrian grid tariff areas.
- Grid level 7, non-metered capacity, single tariff.
- Regular grid supply and allocated local or regional renewable energy community
  (EEG) energy.
- Grid usage fees, grid loss fees, electricity tax, and variable components of the
  renewable support contribution, with a combined total.
- Current price sensors and calculated time series.
- Tariff boundaries evaluated in `Europe/Vienna`, including daylight saving time.
- No extrapolation into years without supported tariff data.

The scope excludes the energy purchase price, VAT, fixed basic and capacity
charges, metering charges, local levies, biomass subsidies, and renewable support
lump sums. Hypothetical winter tariff scenarios are outside the regular model.

## Development

Integration files are located in `custom_components/gridfees_aut/`.
`manifest.json` defines the version, and `config_flow.py` implements setup.
`strings.json` and `translations/en.json` contain the English interface text.

Python syntax, JSON files, and matching interface text have been checked locally.
Runtime verification in Home Assistant remains pending.

References: [Config flow](https://developers.home-assistant.io/docs/core/integration/config_flow/)
and [Manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/).
