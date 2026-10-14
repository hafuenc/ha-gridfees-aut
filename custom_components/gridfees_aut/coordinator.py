"""Coordinate price snapshots and refresh at hourly UTC boundaries."""

from datetime import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_utc_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .calculator import PriceBreakdown, TariffCalculator, TariffProfile
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GridfeesCoordinator(DataUpdateCoordinator[PriceBreakdown | None]):
    """Share one calculation across all entities in a tariff profile."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, calculator: TariffCalculator
    ) -> None:
        """Prepare the selected profile without reading files in the event loop."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, config_entry=entry, always_update=False
        )
        self.entry = entry
        self.calculator = calculator
        self.profile = TariffProfile(**entry.data)

    async def _async_update_data(self) -> PriceBreakdown | None:
        """Calculate now; unsupported dates deliberately produce unavailable entities."""
        return self.calculator.calculate(dt_util.utcnow(), self.profile)

    @callback
    def async_start(self) -> None:
        """Refresh on the hour, including Vienna midnight and SNAP boundaries."""
        self.entry.async_on_unload(
            async_track_utc_time_change(self.hass, self._async_tick, minute=0, second=0)
        )

    async def _async_tick(self, now: datetime) -> None:
        """Refresh directly at the boundary without request debouncing."""
        await self.async_refresh()
