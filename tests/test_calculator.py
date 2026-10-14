"""Offline regression, calendar and tariff-boundary checks."""

import csv
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys
import unittest
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components/gridfees_aut"
# Exercise the calculation module independently of the Home Assistant runtime.
sys.path.insert(0, str(INTEGRATION))
from calculator import TariffCalculator, TariffProfile  # noqa: E402

VIENNA = ZoneInfo("Europe/Vienna")


def local(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=VIENNA)


class CalculatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.calculator = TariffCalculator.from_file(INTEGRATION / "tariffs.json")
        with (ROOT / "tests/fixtures/grid_tariffs.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            cls.reference = list(csv.DictReader(stream))

    def test_all_regions_periods_and_supply_types(self) -> None:
        self.assertEqual(len(self.reference), 84)
        self.assertEqual(len(self.calculator.regions), 14)
        for row in self.reference:
            for supply, column in (
                ("grid", "regular_total"),
                ("eeg_local", "local_total"),
                ("eeg_regional", "regional_total"),
            ):
                with self.subTest(date=row["valid_from"], region=row["region"], supply=supply):
                    price = self.calculator.calculate(
                        local(row["valid_from"] + "T09:00"),
                        TariffProfile(row["region"], supply),
                    )
                    self.assertEqual(price.total, Decimal(row[column]))
                    self.assertEqual(price.grid_loss, Decimal(row["grid_loss_ct"]) / 100)

    def test_independent_regression_values(self) -> None:
        for region, supply, expected in (
            ("BGLD", "grid", "0.07490"),
            ("BGLD", "eeg_local", "0.0364"),
            ("STMK", "eeg_regional", "0.06686"),
        ):
            with self.subTest(region=region, supply=supply):
                self.assertEqual(
                    self.calculator.calculate(
                        local("2026-04-01T10:00"), TariffProfile(region, supply)
                    ).total,
                    Decimal(expected),
                )

    def test_tax_and_tariff_change_dates(self) -> None:
        for moment, expected in (
            ("2022-04-30T23:59:59", "0.07337"),
            ("2022-05-01T00:00", "0.05937"),
            ("2023-02-28T23:59:59", "0.08404"),
            ("2023-03-01T00:00", "0.06199"),
            ("2025-01-01T00:00", "0.09556"),
            ("2026-01-01T00:00", "0.09180"),
        ):
            with self.subTest(moment=moment):
                self.assertEqual(
                    self.calculator.calculate(local(moment), TariffProfile("BGLD")).total,
                    Decimal(expected),
                )

    def test_snap_start_end_and_season(self) -> None:
        for moment, expected in (
            ("2025-04-01T12:00", False),
            ("2026-03-31T12:00", False),
            ("2026-04-01T09:59:59", False),
            ("2026-04-01T10:00", True),
            ("2026-09-30T15:59:59", True),
            ("2026-09-30T16:00", False),
            ("2026-10-01T12:00", False),
        ):
            with self.subTest(moment=moment):
                self.assertEqual(
                    self.calculator.calculate(local(moment), TariffProfile("WIEN")).snap_active,
                    expected,
                )

    def test_published_snap_prices_for_all_regions(self) -> None:
        for row in self.reference:
            if not row["snap_usage_ct"]:
                continue
            with self.subTest(region=row["region"]):
                moment = local("2026-07-01T10:00")
                price = self.calculator.calculate(moment, TariffProfile(row["region"]))
                self.assertEqual(price.grid_usage, Decimal(row["snap_usage_ct"]) / 100)
                plain = self.calculator.calculate(
                    moment, TariffProfile(row["region"], snap_eligible=False)
                )
                self.assertFalse(plain.snap_active)
                self.assertEqual(plain.grid_usage, Decimal(row["grid_usage_ct"]) / 100)

    def test_eeg_never_receives_snap_or_variable_support(self) -> None:
        for region in self.calculator.regions:
            for supply in ("eeg_local", "eeg_regional"):
                with self.subTest(region=region, supply=supply):
                    price = self.calculator.calculate(
                        local("2026-06-01T12:00"), TariffProfile(region, supply)
                    )
                    self.assertFalse(price.snap_active)
                    self.assertEqual(price.renewable_support_usage, 0)
                    self.assertEqual(price.renewable_support_loss, 0)
                    self.assertEqual(price.electricity_tax, 0)

    def test_household_tax_and_eeg_exemption_are_independent(self) -> None:
        moment = local("2026-06-01T09:00")
        household = self.calculator.calculate(moment, TariffProfile("BGLD"))
        other = self.calculator.calculate(moment, TariffProfile("BGLD", household=False))
        self.assertEqual(other.total - household.total, Decimal("0.0072"))
        exempt = self.calculator.calculate(moment, TariffProfile("BGLD", "eeg_local"))
        taxed = self.calculator.calculate(
            moment, TariffProfile("BGLD", "eeg_local", eeg_tax_exempt=False)
        )
        self.assertEqual(taxed.total - exempt.total, Decimal("0.001"))
        self.assertEqual(taxed.grid_usage, exempt.grid_usage)
        self.assertEqual(taxed.renewable_support_usage, 0)
        other_eeg = self.calculator.calculate(
            moment,
            TariffProfile("BGLD", "eeg_local", household=False, eeg_tax_exempt=False),
        )
        self.assertEqual(other_eeg.electricity_tax, Decimal("0.0082"))

    def test_kleinwalsertal_tax_exemption(self) -> None:
        for year in range(2022, 2027):
            for supply in ("grid", "eeg_local", "eeg_regional"):
                with self.subTest(year=year, supply=supply):
                    price = self.calculator.calculate(
                        local(f"{year}-06-01T12:00"),
                        TariffProfile("KLEINWALSERTAL", supply, household=False, eeg_tax_exempt=False),
                    )
                    self.assertEqual(price.electricity_tax, 0)

    def test_eeg_commercial_rounding(self) -> None:
        # 4.82 * 0.43 = 2.0726 ct -> 2.07 ct, not fractional-cent billing.
        price = self.calculator.calculate(
            local("2022-01-01T00:00"), TariffProfile("NOE", "eeg_local")
        )
        self.assertEqual(price.grid_usage, Decimal("0.0207"))
        # Synthetic half-cent boundary verifies half-up, rather than bankers' rounding.
        import json
        data = json.loads((INTEGRATION / "tariffs.json").read_text())
        data["grid_tariffs"][0]["regions"]["BGLD"]["grid_usage_ct"] = "0.5"
        price = TariffCalculator(data).calculate(
            local("2022-01-01T00:00"), TariffProfile("BGLD", "eeg_local")
        )
        self.assertEqual(price.grid_usage, Decimal("0.0022"))

    def test_unsupported_dates_and_vienna_year_boundary(self) -> None:
        profile = TariffProfile("STMK")
        for moment in ("2021-12-31T23:59:59", "2027-01-01T00:00", "2030-06-01T12:00"):
            with self.subTest(moment=moment):
                self.assertIsNone(self.calculator.calculate(local(moment), profile))
        self.assertIsNotNone(self.calculator.calculate(local("2022-01-01T00:00"), profile))
        self.assertIsNotNone(self.calculator.calculate(local("2026-12-31T23:59:59"), profile))
        self.assertIsNone(self.calculator.calculate(
            datetime(2026, 12, 31, 23, tzinfo=timezone.utc), profile
        ))

    def test_utc_and_vienna_are_equivalent(self) -> None:
        moment = local("2026-06-01T10:00")
        for region in self.calculator.regions:
            with self.subTest(region=region):
                profile = TariffProfile(region)
                self.assertEqual(
                    self.calculator.calculate(moment, profile),
                    self.calculator.calculate(moment.astimezone(timezone.utc), profile),
                )

    def test_daily_quarter_hour_series_handles_dst(self) -> None:
        for start, end, count in (
            ("2026-03-29T00:00", "2026-03-30T00:00", 92),
            ("2026-10-25T00:00", "2026-10-26T00:00", 100),
            ("2026-06-01T00:00", "2026-06-02T00:00", 96),
        ):
            with self.subTest(start=start):
                points = list(self.calculator.series(local(start), local(end), TariffProfile("WIEN")))
                self.assertEqual(len(points), count)
                utc_points = [time.astimezone(timezone.utc) for time, _ in points]
                self.assertEqual(len(set(utc_points)), count)
                self.assertTrue(all(
                    (right - left).total_seconds() == 900
                    for left, right in zip(utc_points, utc_points[1:])
                ))

    def test_series_snap_count_and_unsupported_intervals(self) -> None:
        points = list(self.calculator.series(
            local("2026-06-01T00:00"), local("2026-06-02T00:00"), TariffProfile("BGLD")
        ))
        self.assertEqual(sum(price.snap_active for _, price in points), 24)
        points = list(self.calculator.series(
            local("2026-12-31T23:45"), local("2027-01-01T00:15"), TariffProfile("BGLD")
        ))
        self.assertIsNotNone(points[0][1])
        self.assertIsNone(points[1][1])

    def test_rejects_invalid_inputs(self) -> None:
        profile = TariffProfile("BGLD")
        with self.assertRaises(ValueError):
            self.calculator.calculate(datetime(2026, 1, 1), profile)
        with self.assertRaises(ValueError):
            self.calculator.calculate(local("2026-01-01T00:00"), TariffProfile("UNKNOWN"))
        with self.assertRaises(ValueError):
            TariffProfile("BGLD", "unknown")
        with self.assertRaises(ValueError):
            TariffProfile("BGLD", household="false")
        for interval in (0, -15, 0.5, True):
            with self.subTest(interval=interval), self.assertRaises(ValueError):
                list(self.calculator.series(
                    local("2026-01-01T00:00"), local("2026-01-02T00:00"), profile, interval
                ))
        with self.assertRaises(ValueError):
            list(self.calculator.series(
                local("2026-01-02T00:00"), local("2026-01-01T00:00"), profile
            ))


if __name__ == "__main__":
    unittest.main()
