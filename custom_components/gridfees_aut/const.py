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
    SUPPLY_GRID: "Regular grid supply",
    SUPPLY_EEG_LOCAL: "Local EEG",
    SUPPLY_EEG_REGIONAL: "Regional EEG",
}

REGIONS = {
    "BGLD": "Burgenland",
    "KTN": "Carinthia",
    "KLAGENFURT": "Klagenfurt",
    "NOE": "Lower Austria",
    "OOE": "Upper Austria",
    "LINZ": "Linz",
    "SBG": "Salzburg",
    "STMK": "Styria",
    "GRAZ": "Graz",
    "TIROL": "Tyrol",
    "INNSBRUCK": "Innsbruck",
    "VBG": "Vorarlberg",
    "WIEN": "Vienna",
    "KLEINWALSERTAL": "Kleinwalsertal",
}
