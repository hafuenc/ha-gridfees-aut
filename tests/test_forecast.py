"""Check the public forecast format, timezones and supported-date boundaries."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import unittest
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components/gridfees_aut"
sys.path.insert(0, str(INTEGRATION))
from calculator import TariffCalculator, TariffProfile  # noqa: E402

VIENNA = ZoneInfo("Europe/Vienna")


def vienna(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=VIENNA)


class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.calculator = TariffCalculator.from_file(INTEGRATION / "tariffs.json")

    def test_public_format_eur_per_kwh_only_and_rolling_horizon(self) -> None:
        snapshot = self.calculator.snapshot(
            vienna("2026-10-14T12:34:56"), TariffProfile("BGLD")
        )
        attributes = snapshot.forecast_attributes()
        rows = attributes["data"]
        self.assertEqual(len(rows), 168)
        self.assertEqual(rows[0], {
            "start_time": "2026-10-14T12:00:00+02:00",
            "end_time": "2026-10-14T13:00:00+02:00",
            "price_eur_per_kwh": 0.0918,
        })
        self.assertEqual(rows[-1]["end_time"], "2026-10-21T12:00:00+02:00")
        self.assertEqual(attributes["forecast_timezone"], "Europe/Vienna")
        self.assertEqual(attributes["tariff_timezone"], "Europe/Vienna")
        self.assertTrue(attributes["forecast_complete"])
        self.assertEqual(attributes["forecast_hours"], 168)
        self.assertEqual(attributes["forecast_interval_minutes"], 60)
        json.dumps(attributes, allow_nan=False)

    def test_forecast_advances_even_when_current_price_does_not_change(self) -> None:
        profile = TariffProfile("BGLD")
        first = self.calculator.snapshot(vienna("2026-10-14T12:00"), profile)
        same_hour = self.calculator.snapshot(vienna("2026-10-14T12:59"), profile)
        next_hour = self.calculator.snapshot(vienna("2026-10-14T13:00"), profile)
        self.assertEqual(first, same_hour)
        self.assertEqual(first.current, next_hour.current)
        self.assertNotEqual(first, next_hour)
        self.assertEqual(first.forecast[1:], next_hour.forecast[:-1])

    def test_system_timezone_only_changes_timestamp_representation(self) -> None:
        moment = vienna("2026-06-01T10:35")
        profile = TariffProfile("BGLD")
        reference = self.calculator.snapshot(moment, profile)
        for zone in (ZoneInfo("UTC"), ZoneInfo("America/New_York"), ZoneInfo("Asia/Kolkata")):
            with self.subTest(timezone=str(zone)):
                snapshot = self.calculator.snapshot(moment, profile, zone)
                self.assertEqual(reference.current, snapshot.current)
                self.assertEqual(snapshot.forecast_timezone, str(zone))
                for local, displayed in zip(reference.forecast, snapshot.forecast):
                    self.assertEqual(local.price, displayed.price)
                    self.assertEqual(
                        datetime.fromisoformat(local.start_time),
                        datetime.fromisoformat(displayed.start_time),
                    )
        utc = self.calculator.snapshot(moment, profile, ZoneInfo("UTC"))
        self.assertEqual(utc.forecast[0].start_time, "2026-06-01T08:00:00+00:00")
        self.assertEqual(utc.forecast[0].as_dict()["price_eur_per_kwh"], 0.0749)

    def test_vienna_dst_changes_keep_all_168_real_hours(self) -> None:
        for moment in ("2026-03-28T12:30", "2026-10-24T12:30"):
            with self.subTest(moment=moment):
                snapshot = self.calculator.snapshot(vienna(moment), TariffProfile("WIEN"))
                rows = snapshot.forecast
                self.assertEqual(len(rows), 168)
                starts = [datetime.fromisoformat(row.start_time) for row in rows]
                self.assertEqual(len(set(starts)), 168)
                self.assertEqual(
                    datetime.fromisoformat(rows[-1].end_time) - starts[0],
                    timedelta(hours=168),
                )
                for index, row in enumerate(rows):
                    self.assertEqual(
                        datetime.fromisoformat(row.end_time) - starts[index],
                        timedelta(hours=1),
                    )
                    if index:
                        self.assertEqual(starts[index] - starts[index - 1], timedelta(hours=1))
        autumn = self.calculator.snapshot(vienna("2026-10-24T12:30"), TariffProfile("WIEN"))
        repeated = [row.start_time for row in autumn.forecast if row.start_time.startswith("2026-10-25T02:")]
        self.assertEqual(repeated, ["2026-10-25T02:00:00+02:00", "2026-10-25T02:00:00+01:00"])
        spring = self.calculator.snapshot(vienna("2026-03-28T12:30"), TariffProfile("WIEN"))
        self.assertFalse(any(row.start_time.startswith("2026-03-29T02:") for row in spring.forecast))

    def test_snap_and_eeg_profile_settings_are_included(self) -> None:
        moment = vienna("2026-06-01T09:15")
        for profile in (
            TariffProfile("BGLD"),
            TariffProfile("BGLD", snap_eligible=False),
            TariffProfile("BGLD", "eeg_local"),
            TariffProfile("BGLD", "eeg_regional", household=False),
        ):
            with self.subTest(profile=profile):
                snapshot = self.calculator.snapshot(moment, profile)
                for row in snapshot.forecast:
                    expected = self.calculator.calculate(datetime.fromisoformat(row.start_time), profile)
                    self.assertEqual(row.price, expected.total)
        regular = self.calculator.snapshot(moment, TariffProfile("BGLD"))
        self.assertEqual(regular.forecast[0].as_dict()["price_eur_per_kwh"], 0.0918)
        self.assertEqual(regular.forecast[1].as_dict()["price_eur_per_kwh"], 0.0749)
        self.assertEqual(regular.forecast[7].as_dict()["price_eur_per_kwh"], 0.0918)

    def test_unsupported_future_intervals_are_null_not_zero_or_extrapolated(self) -> None:
        snapshot = self.calculator.snapshot(
            vienna("2026-12-31T23:30"), TariffProfile("BGLD")
        )
        attributes = snapshot.forecast_attributes()
        self.assertIsNotNone(snapshot.current)
        self.assertEqual(len(attributes["data"]), 168)
        self.assertFalse(attributes["forecast_complete"])
        self.assertEqual(attributes["data"][0]["price_eur_per_kwh"], 0.0918)
        for row in attributes["data"][1:]:
            self.assertIsNone(row["price_eur_per_kwh"])
        json.dumps(attributes, allow_nan=False)
        unsupported = self.calculator.snapshot(
            vienna("2027-01-01T00:00"), TariffProfile("BGLD")
        )
        self.assertIsNone(unsupported.current)
        self.assertTrue(all(row.price is None for row in unsupported.forecast))

    def test_naive_time_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.calculator.snapshot(datetime(2026, 10, 14, 12), TariffProfile("BGLD"))


if __name__ == "__main__":
    unittest.main()
