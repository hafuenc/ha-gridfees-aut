"""Constants shared by the integration and its configuration flow."""

DOMAIN = "gridfees_aut"

CONF_REGION = "region"
CONF_SUPPLY_TYPE = "supply_type"
CONF_HOUSEHOLD = "household"
CONF_SNAP_ELIGIBLE = "snap_eligible"

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


def profile_title(region: str, supply_type: str) -> str:
    """Build the default profile and device name using official grid area names."""
    return f"gridfees {REGIONS[region]} {SUPPLY_LABELS[supply_type]}"


def legacy_profile_titles(region: str, supply_type: str) -> set[str]:
    """Recognize generated titles from earlier versions without matching custom names."""
    old_areas = {
        "KTN": "Carinthia",
        "NOE": "Lower Austria",
        "OOE": "Upper Austria",
        "STMK": "Styria",
        "TIROL": "Tyrol",
        "WIEN": "Vienna",
    }
    old_labels = {
        SUPPLY_GRID: "Netzbezug",
        SUPPLY_EEG_LOCAL: "EEG lokal",
        SUPPLY_EEG_REGIONAL: "EEG regional",
    }
    return {
        f"{area} · {label}"
        for area in (REGIONS[region], old_areas.get(region, REGIONS[region]))
        for label in (supply_type, SUPPLY_LABELS[supply_type], old_labels[supply_type])
    }
