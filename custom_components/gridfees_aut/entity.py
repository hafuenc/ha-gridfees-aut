"""Shared identity, availability and metadata for a tariff profile."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, profile_title
from .coordinator import GridfeesCoordinator


class GridfeesEntity(CoordinatorEntity[GridfeesCoordinator]):
    """An entity belonging to a virtual tariff profile service."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GridfeesCoordinator, key: str) -> None:
        """Keep identities stable across reloads and integration upgrades."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=profile_title(coordinator.profile.region, coordinator.profile.supply_type),
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Gridfees AUT",
            model="Grid level 7 · single tariff",
        )
        self._attr_extra_state_attributes = {
            "grid_area": coordinator.profile.region,
            "supply_type": coordinator.profile.supply_type,
            "vat_included": False,
            "tariff_valid_from": coordinator.calculator.valid_from.isoformat(),
            "tariff_valid_until": coordinator.calculator.valid_until.isoformat(),
        }

    @property
    def available(self) -> bool:
        """Avoid reporting zero or a stale price outside supported tariff dates."""
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.current is not None
        )
