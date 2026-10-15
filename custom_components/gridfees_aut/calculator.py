"""Time-dependent grid fees with decimal arithmetic and Vienna calendar rules."""

from dataclasses import dataclass
from collections.abc import Mapping
from datetime import date, datetime, timedelta, timezone, tzinfo
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
from typing import Any, Iterator
from zoneinfo import ZoneInfo

VIENNA = ZoneInfo("Europe/Vienna")
ZERO = Decimal("0")
HUNDRED = Decimal("100")


@dataclass(frozen=True)
class TariffProfile:
    """A single supply allocation and its applicable tax assumptions."""

    region: str
    supply_type: str = "grid"
    household: bool = True
    snap_eligible: bool = True
    simulate_winap: bool = False

    def __post_init__(self) -> None:
        """Reject unsupported supply types and non-boolean assumptions."""
        if self.supply_type not in ("grid", "eeg_local", "eeg_regional"):
            raise ValueError("Unknown supply type")
        for flag in (self.household, self.snap_eligible, self.simulate_winap):
            if not isinstance(flag, bool):
                raise ValueError("Tariff assumptions must be booleans")

    @classmethod
    def from_config(cls, data: Mapping[str, Any]) -> "TariffProfile":
        """Normalize current and legacy profiles, ignoring retired assumptions."""
        supply_type = data.get("supply_type", "grid")
        eeg = supply_type != "grid"
        return cls(
            region=data["region"],
            supply_type=supply_type,
            household=True if eeg else data.get("household", True),
            snap_eligible=False if eeg else data.get("snap_eligible", True),
            simulate_winap=False if eeg else data.get("simulate_winap", False),
        )

    def as_config(self) -> dict[str, str | bool]:
        """Serialize the supported fields for a saved config entry."""
        return {
            "region": self.region,
            "supply_type": self.supply_type,
            "household": self.household,
            "snap_eligible": self.snap_eligible,
            "simulate_winap": self.simulate_winap,
        }


@dataclass(frozen=True)
class PriceBreakdown:
    """Marginal prices in EUR/kWh excluding VAT."""

    grid_usage: Decimal
    grid_loss: Decimal
    electricity_tax: Decimal
    renewable_support_usage: Decimal
    renewable_support_loss: Decimal
    snap_active: bool
    winap_simulated_active: bool = False

    @property
    def total(self) -> Decimal:
        """Return the sum without introducing floating-point rounding."""
        return (
            self.grid_usage
            + self.grid_loss
            + self.electricity_tax
            + self.renewable_support_usage
            + self.renewable_support_loss
        )


@dataclass(frozen=True)
class PriceInterval:
    """A forecast interval with one net unit price, or no supported price."""

    start_time: str
    end_time: str
    price: Decimal | None

    def as_dict(self) -> dict[str, str | float | None]:
        """Expose the net price in EUR/kWh as a JSON-compatible number."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "price_eur_per_kwh": None if self.price is None else float(self.price),
        }


@dataclass(frozen=True)
class TariffSnapshot:
    """Current fees and a rolling 168-hour forecast from the same profile."""

    current: PriceBreakdown | None
    forecast: tuple[PriceInterval, ...]
    forecast_timezone: str

    def forecast_attributes(self) -> dict[str, Any]:
        """Expose contiguous periods, starting a new row only when price changes."""
        periods: list[PriceInterval] = []
        for interval in self.forecast:
            if (
                periods
                and periods[-1].price == interval.price
                and periods[-1].end_time == interval.start_time
            ):
                previous = periods[-1]
                periods[-1] = PriceInterval(
                    previous.start_time, interval.end_time, interval.price
                )
            else:
                periods.append(interval)
        return {
            "data": [interval.as_dict() for interval in periods],
            "forecast_start": self.forecast[0].start_time,
            "forecast_end": self.forecast[-1].end_time,
            "forecast_hours": 168,
            "forecast_interval_mode": "change_of_value",
            "forecast_timezone": self.forecast_timezone,
            "tariff_timezone": "Europe/Vienna",
            "forecast_complete": all(interval.price is not None for interval in self.forecast),
        }


def _in_vienna(moment: datetime) -> datetime:
    """Require an unambiguous instant and convert it to the tariff timezone."""
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("Timestamps must include a timezone")
    return moment.astimezone(VIENNA)


def _winter_night(local: datetime) -> bool:
    """Use nights starting October 1 through March 31, from 23:00 to 05:00."""
    if 5 <= local.hour < 23:
        return False
    night = local.date() - timedelta(days=1) if local.hour < 5 else local.date()
    return night.month in (10, 11, 12, 1, 2, 3)


class TariffCalculator:
    """Evaluate a versioned tariff dataset; never extrapolate unknown years."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Prepare dated tariff tables once, outside sensor property access."""
        self.valid_from = date.fromisoformat(data["valid_from"])
        self.valid_until = date.fromisoformat(data["valid_until"])
        self._grid = self._dated(data["grid_tariffs"])
        self._tax = self._dated(data["electricity_tax"])
        self._support = self._dated(data["renewable_support"])
        self._factors = {
            key: Decimal(value) for key, value in data["eeg_usage_factors"].items()
        }
        self._tax_exempt_regions = frozenset(data["electricity_tax_exempt_regions"])
        self._snap = [
            (
                date.fromisoformat(window["valid_from"]),
                date.fromisoformat(window["valid_until"]),
                window["start_hour"],
                window["end_hour"],
            )
            for window in data["snap_windows"]
        ]
        self.regions = frozenset(self._grid[0][1]["regions"])

    @classmethod
    def from_file(cls, path: Path) -> "TariffCalculator":
        """Load the packaged dataset; call in an executor from Home Assistant."""
        return cls(json.loads(path.read_text(encoding="utf-8")))

    @staticmethod
    def _dated(rows: list[dict[str, Any]]) -> list[tuple[date, dict[str, Any]]]:
        return sorted((date.fromisoformat(row["valid_from"]), row) for row in rows)

    @staticmethod
    def _at(rows: list[tuple[date, dict[str, Any]]], day: date) -> dict[str, Any]:
        for start, row in reversed(rows):
            if start <= day:
                return row
        raise ValueError("Missing tariff data for supported date")

    def calculate(
        self, moment: datetime, profile: TariffProfile
    ) -> PriceBreakdown | None:
        """Return the current tariff, or None outside the supported period."""
        local = _in_vienna(moment)
        if profile.region not in self.regions:
            raise ValueError("Unknown grid area")
        day = local.date()
        if not self.valid_from <= day < self.valid_until:
            return None

        tariff = self._at(self._grid, day)["regions"][profile.region]
        usage_ct = Decimal(tariff["grid_usage_ct"])
        loss = Decimal(tariff["grid_loss_ct"]) / HUNDRED
        eeg = profile.supply_type != "grid"
        snap = False
        winap_simulated = False
        if eeg:
            usage_ct = (usage_ct * self._factors[profile.supply_type]).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        elif profile.snap_eligible:
            snap = any(
                start <= day < end and start_hour <= local.hour < end_hour
                for start, end, start_hour, end_hour in self._snap
            )
            if snap:
                usage_ct = Decimal(tariff["snap_usage_ct"])

        # This opt-in scenario borrows a published SNAP price, not a WiNAP rate.
        # Earlier years have no SNAP price and are never extrapolated.
        if (
            not eeg
            and profile.simulate_winap
            and "snap_usage_ct" in tariff
            and _winter_night(local)
        ):
            usage_ct = Decimal(tariff["snap_usage_ct"])
            winap_simulated = True

        tax_row = self._at(self._tax, day)
        tax = Decimal(tax_row["household" if profile.household else "other"])
        if profile.region in self._tax_exempt_regions or eeg:
            tax = ZERO

        support = self._at(self._support, day)
        return PriceBreakdown(
            grid_usage=usage_ct / HUNDRED,
            grid_loss=loss,
            electricity_tax=tax,
            renewable_support_usage=ZERO if eeg else Decimal(support["grid_usage"]),
            renewable_support_loss=ZERO if eeg else Decimal(support["grid_loss"]),
            snap_active=snap,
            winap_simulated_active=winap_simulated,
        )

    def series(
        self,
        start: datetime,
        end: datetime,
        profile: TariffProfile,
        interval_minutes: int = 15,
    ) -> Iterator[tuple[datetime, PriceBreakdown | None]]:
        """Yield interval-start prices over [start, end), stepping in UTC."""
        if isinstance(interval_minutes, bool) or not isinstance(interval_minutes, int):
            raise ValueError("Interval must be a positive integer number of minutes")
        if interval_minutes <= 0:
            raise ValueError("Interval must be positive")
        current = _in_vienna(start).astimezone(timezone.utc)
        stop = _in_vienna(end).astimezone(timezone.utc)
        if stop < current:
            raise ValueError("End must not precede start")
        step = timedelta(minutes=interval_minutes)
        while current < stop:
            yield current.astimezone(VIENNA), self.calculate(current, profile)
            current += step

    def snapshot(
        self,
        moment: datetime,
        profile: TariffProfile,
        display_timezone: tzinfo = VIENNA,
    ) -> TariffSnapshot:
        """Calculate now and the current UTC hour plus the next 167 hours."""
        instant = _in_vienna(moment).astimezone(timezone.utc)
        start = instant.replace(minute=0, second=0, microsecond=0)
        hour = timedelta(hours=1)
        intervals = []
        for index in range(168):
            interval_start = start + index * hour
            price = self.calculate(interval_start, profile)
            intervals.append(
                PriceInterval(
                    start_time=interval_start.astimezone(display_timezone).isoformat(),
                    end_time=(interval_start + hour).astimezone(display_timezone).isoformat(),
                    price=None if price is None else price.total,
                )
            )
        return TariffSnapshot(
            current=self.calculate(instant, profile),
            forecast=tuple(intervals),
            forecast_timezone=str(display_timezone),
        )
