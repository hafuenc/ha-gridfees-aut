"""Austrian grid fee calculations for Home Assistant."""

from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .calculator import TariffCalculator, TariffProfile
from .const import CONF_REGION, CONF_SUPPLY_TYPE, legacy_profile_titles, profile_title
from .coordinator import GridfeesCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]
GridfeesConfigEntry = ConfigEntry[GridfeesCoordinator]


async def async_migrate_entry(hass: HomeAssistant, entry: GridfeesConfigEntry) -> bool:
    """Remove retired EEG tax settings without changing profile or entity IDs."""
    if entry.version != 1:
        return False
    if entry.minor_version < 2:
        hass.config_entries.async_update_entry(
            entry,
            data=TariffProfile.from_config(entry.data).as_config(),
            minor_version=2,
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: GridfeesConfigEntry) -> bool:
    """Load the dataset and initialize the profile's entities."""
    region = entry.data[CONF_REGION]
    supply_type = entry.data[CONF_SUPPLY_TYPE]
    if entry.title in legacy_profile_titles(region, supply_type):
        hass.config_entries.async_update_entry(
            entry, title=profile_title(region, supply_type)
        )
    calculator = await hass.async_add_executor_job(
        TariffCalculator.from_file, Path(__file__).with_name("tariffs.json")
    )
    coordinator = GridfeesCoordinator(hass, entry, calculator)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    coordinator.async_start()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GridfeesConfigEntry) -> bool:
    """Unload entities; registered timer cleanup runs when unload succeeds."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
