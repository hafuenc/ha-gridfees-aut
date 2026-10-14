"""Net price sensors for Austrian variable grid fees and levies."""

from decimal import Decimal

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GridfeesConfigEntry
from .coordinator import GridfeesCoordinator
from .entity import GridfeesEntity

PARALLEL_UPDATES = 0
SENSOR_KEYS = (
    "total",
    "grid_usage",
    "grid_loss",
    "electricity_tax",
    "renewable_support_usage",
    "renewable_support_loss",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GridfeesConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create six sensors sharing the same calculated snapshot."""
    async_add_entities(GridfeesPriceSensor(entry.runtime_data, key) for key in SENSOR_KEYS)


class GridfeesPriceSensor(GridfeesEntity, SensorEntity):
    """A unit price, rather than an accumulated monetary amount."""

    def __init__(self, coordinator: GridfeesCoordinator, key: str) -> None:
        """Use measurement statistics and preserve the full underlying precision."""
        super().__init__(coordinator, key)
        self.entity_description = SensorEntityDescription(
            key=key,
            translation_key=key,
            native_unit_of_measurement="EUR/kWh",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=5,
            icon="mdi:cash",
        )

    @property
    def native_value(self) -> Decimal | None:
        """Return the cached fee component or the combined total."""
        if self.coordinator.data is None:
            return None
        return getattr(self.coordinator.data, self.entity_description.key)
