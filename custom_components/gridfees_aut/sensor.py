"""Net price sensors for Austrian variable grid fees and levies."""

from decimal import Decimal
from typing import Any

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

    _unrecorded_attributes = frozenset(
        {
            "data",
            "forecast_start",
            "forecast_end",
            "forecast_hours",
            "forecast_interval_minutes",
            "forecast_timezone",
            "forecast_complete",
            "tariff_timezone",
        }
    )

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
            entity_registry_enabled_default=key == "total",
        )

    @property
    def native_value(self) -> Decimal | None:
        """Return the cached fee component or the combined total."""
        if self.coordinator.data is None or self.coordinator.data.current is None:
            return None
        return getattr(self.coordinator.data.current, self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose a seven-day forecast only on Total grid fees."""
        attributes = dict(self._attr_extra_state_attributes)
        if self.entity_description.key == "total" and self.coordinator.data is not None:
            attributes.update(self.coordinator.data.forecast_attributes())
        return attributes
