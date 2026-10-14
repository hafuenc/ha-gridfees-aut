"""Constants shared by the integration and its configuration flow."""

DOMAIN = "gridfees_aut"

CONF_REGION = "region"
CONF_SUPPLY_TYPE = "supply_type"
CONF_HOUSEHOLD = "household"
CONF_SNAP_ELIGIBLE = "snap_eligible"
CONF_EEG_TAX_EXEMPT = "eeg_tax_exempt"

SUPPLY_GRID = "grid"
SUPPLY_EEG_LOCAL = "eeg_local"
SUPPLY_EEG_REGIONAL = "eeg_regional"
SUPPLY_TYPES = (SUPPLY_GRID, SUPPLY_EEG_LOCAL, SUPPLY_EEG_REGIONAL)
SUPPLY_LABELS = {
    SUPPLY_GRID: "Netzbezug",
    SUPPLY_EEG_LOCAL: "EEG lokal",
    SUPPLY_EEG_REGIONAL: "EEG regional",
}

REGIONS = {
    "BGLD": "Burgenland",
    "KTN": "Kärnten",
    "KLAGENFURT": "Klagenfurt",
    "NOE": "Niederösterreich",
    "OOE": "Oberösterreich",
    "LINZ": "Linz",
    "SBG": "Salzburg",
    "STMK": "Steiermark",
    "GRAZ": "Graz",
    "TIROL": "Tirol",
    "INNSBRUCK": "Innsbruck",
    "VBG": "Vorarlberg",
    "WIEN": "Wien",
    "KLEINWALSERTAL": "Kleinwalsertal",
}
