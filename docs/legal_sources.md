# Legal sources

This document identifies the legal texts and dated versions used for the
supported 2022–2026 tariff dataset. Official German names are retained for grid
areas, taxes, contributions, and fee components.

## Systemnutzungsentgelte-Verordnung 2018 (SNE-V 2018)

Relevant provisions:

- § 2: definitions, including Arbeitspreis (AP) and Sommer-Nieder-Arbeitspreis (SNAP).
- § 5 Abs. 1: Netznutzungsentgelt tables; the integration covers Netzebene 7,
  non-metered capacity, single tariff (bb).
- § 5 Abs. 1a: reductions for allocated local and regional EEG energy.
- § 5 Abs. 1b: SNAP rates and eligibility in the 2026 version.
- § 6: Netzverlustentgelt tables.

| Consolidated version | Use in the dataset |
| --- | --- |
| [2022-01-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010107&FassungVom=2022-01-01) | 2022 grid usage and loss rates |
| [2023-01-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010107&FassungVom=2023-01-01) | Initial 2023 grid usage and loss rates |
| [2023-03-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010107&FassungVom=2023-03-01) | March 2023 grid loss rate change |
| [2024-01-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010107&FassungVom=2024-01-01) | 2024 grid usage and loss rates |
| [2025-01-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010107&FassungVom=2025-01-01) | 2025 grid usage and loss rates |
| [2026-01-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010107&FassungVom=2026-01-01) | 2026 grid usage and loss rates |
| [2026-04-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010107&FassungVom=2026-04-01) | 2026 consolidated version including SNAP |

Grid area labels follow the ordinance: Burgenland, Kärnten, Klagenfurt,
Niederösterreich, Oberösterreich, Linz, Salzburg, Steiermark, Graz, Tirol,
Innsbruck, Vorarlberg, Wien, and Kleinwalsertal.

## Erneuerbaren-Förderbeitrag

- [Erneuerbaren-Förderbeitragsverordnung 2025, BGBl. II Nr. 419/2024](https://www.ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2024_II_419/BGBLA_2024_II_419.html).
- [Erneuerbaren-Förderbeitragsverordnung 2026, BGBl. II Nr. 301/2025](https://www.ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2025_II_301/BGBLA_2025_II_301.html).

For each year, § 2 Abs. 2 and 3 provide the Netznutzungsentgelt and
Netzverlustentgelt contribution components. The integration includes the
variable Arbeitspreis components for Netzebene 7 bb, not the fixed components.

## Elektrizitätsabgabegesetz (ElAbgG)

Relevant provisions:

- § 1: taxable transactions and tax territory; Abs. 3 is relevant to Kleinwalsertal.
- § 2: exemptions, including qualifying EEG energy.
- § 4: tax base and rates.
- § 7: effective dates and temporary rates; Abs. 16 includes the 2026 household rule.

Dated consolidated texts:

- [ElAbgG, 2022-01-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=10005027&FassungVom=2022-01-01).
- [ElAbgG, 2022-05-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=10005027&FassungVom=2022-05-01).
- [ElAbgG, 2025-01-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=10005027&FassungVom=2025-01-01).
- [ElAbgG, 2026-04-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=10005027&FassungVom=2026-04-01).

For the 2026 household rate, § 7 Abs. 16 ElAbgG refers to eligible natural persons
under [§ 4 Abs. 1 Stromkostenzuschussgesetz (SKZG)](https://www.ris.bka.gv.at/eli/bgbl/i/2022/156/P4/NOR40250760).
[Anlage I to § 4 SKZG](https://ris.bka.gv.at/eli/bgbl/i/2022/156/ANL1/NOR40250766)
lists the eligible standard load profiles H0, HA, and HF. These eligibility criteria
are selected by the user, not checked by the integration.

The household rate is not a tax exemption. The EEG exemption must be enabled
explicitly when its conditions are met; it is off by default for new profiles.
Existing saved assumptions are retained during upgrades.

## Erneuerbaren-Ausbau-Gesetz (EAG)

- [EAG, consolidated version of 2026-04-01](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20011619&FassungVom=2026-04-01).
- § 75: Erneuerbaren-Förderbeitrag; Abs. 5 is relevant to the EEG exemption.

## Scope

The sensors represent variable net prices per kWh. They do not represent a
complete electricity bill. Fixed Grund-/Leistungspreise, Entgelte für
Messleistungen, Erneuerbaren-Förderpauschale, local levies, biomass subsidies,
the energy purchase price, VAT, and foreign taxes or levies are not included.
Hypothetical winter tariff reductions are not applied. Dates outside the
supported dataset do not receive extrapolated prices.
