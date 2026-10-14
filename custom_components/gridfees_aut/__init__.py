"""Austrian grid fee calculations for Home Assistant."""

from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .calculator import TariffCalculator
from .coordinator import GridfeesCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]
GridfeesConfigEntry = ConfigEntry[GridfeesCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: GridfeesConfigEntry) -> bool:
    """Load the dataset and initialize the profile's entities."""
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
