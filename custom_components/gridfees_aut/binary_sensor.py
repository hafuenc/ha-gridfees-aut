"""Expose whether SNAP or the optional WiNAP simulation currently applies."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GridfeesConfigEntry
from .coordinator import GridfeesCoordinator
from .entity import GridfeesEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GridfeesConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the profile's summer and winter status entities."""
    async_add_entities([
        GridfeesSnapSensor(entry.runtime_data),
        GridfeesWinapSensor(entry.runtime_data),
    ])


class GridfeesSnapSensor(GridfeesEntity, BinarySensorEntity):
    """True only while the selected profile receives the SNAP tariff."""

    _attr_translation_key = "snap_active"
    _attr_icon = "mdi:white-balance-sunny"
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator: GridfeesCoordinator) -> None:
        """Initialize a stable SNAP status identity."""
        super().__init__(coordinator, "snap_active")

    @property
    def is_on(self) -> bool | None:
        """Read status from the same snapshot as the price sensors."""
        if self.coordinator.data is None or self.coordinator.data.current is None:
            return None
        return self.coordinator.data.current.snap_active


class GridfeesWinapSensor(GridfeesEntity, BinarySensorEntity):
    """True only while the selected profile receives the simulated winter price."""

    _attr_translation_key = "winap_active"
    _attr_icon = "mdi:weather-night"
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator: GridfeesCoordinator) -> None:
        """Add a stable winter status identity without renaming existing entities."""
        super().__init__(coordinator, "winap_active")

    @property
    def is_on(self) -> bool | None:
        """Read simulation status from the snapshot used by Total grid fees."""
        if self.coordinator.data is None or self.coordinator.data.current is None:
            return None
        return self.coordinator.data.current.winap_simulated_active
