"""Check the opt-in winter scenario, transitions and unchanged legal tariffs."""

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys
import unittest
from zoneinfo import ZoneInfo

INTEGRATION = Path(__file__).resolve().parents[1] / 'custom_components/gridfees_aut'
sys.path.insert(0, str(INTEGRATION))
from calculator import TariffCalculator, TariffProfile  # noqa: E402

VIENNA = ZoneInfo('Europe/Vienna')


def local(value):
    return datetime.fromisoformat(value).replace(tzinfo=VIENNA)


class WinapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calculator = TariffCalculator.from_file(INTEGRATION / 'tariffs.json')

    def test_existing_profiles_default_off_and_keep_choices(self):
        profile = TariffProfile.from_config({
            'region':'STMK', 'supply_type':'grid', 'household':False,
            'snap_eligible':False,
        })
        self.assertFalse(profile.simulate_winap)
        self.assertFalse(profile.household)
        self.assertFalse(profile.snap_eligible)
        simulated = TariffProfile.from_config({**profile.as_config(), 'simulate_winap':True})
        self.assertTrue(simulated.simulate_winap)
        self.assertEqual(TariffProfile.from_config(simulated.as_config()), simulated)
        self.assertNotEqual(profile, simulated)
        with self.assertRaises(ValueError):
            TariffProfile('STMK', simulate_winap='false')

    def test_nights_starting_october_first_through_march_last(self):
        for moment, active in (
            ('2026-09-30T23:00',False),
            ('2026-10-01T00:00',False),
            ('2026-10-01T04:59:59',False),
            ('2026-10-01T22:59:59',False),
            ('2026-10-01T23:00',True),
            ('2026-10-02T00:00',True),
            ('2026-10-02T04:59:59',True),
            ('2026-10-02T05:00',False),
            ('2026-01-01T00:00',True),
            ('2026-03-31T23:00',True),
            ('2026-04-01T04:59:59',True),
            ('2026-04-01T05:00',False),
            ('2026-04-01T23:00',False),
            ('2026-07-01T23:00',False),
        ):
            with self.subTest(moment=moment):
                price = self.calculator.calculate(local(moment), TariffProfile('STMK',simulate_winap=True))
                self.assertEqual(price.winap_simulated_active,active)
                self.assertFalse(price.snap_active)

    def test_all_regions_borrow_published_snap_and_change_only_usage(self):
        for region in self.calculator.regions:
            for eligible in (True,False):
                with self.subTest(region=region, snap=eligible):
                    profile = TariffProfile(region,snap_eligible=eligible,simulate_winap=True)
                    night = self.calculator.calculate(local('2026-10-15T23:00'),profile)
                    plain = self.calculator.calculate(local('2026-10-15T22:00'),profile)
                    summer = self.calculator.calculate(local('2026-07-01T12:00'),TariffProfile(region))
                    self.assertEqual(night.grid_usage,summer.grid_usage)
                    self.assertFalse(night.snap_active)
                    self.assertTrue(night.winap_simulated_active)
                    for key in ('grid_loss','electricity_tax','renewable_support_usage','renewable_support_loss'):
                        self.assertEqual(getattr(night,key),getattr(plain,key))
        self.assertEqual(self.calculator.calculate(local('2026-10-15T23:00'),TariffProfile('STMK',simulate_winap=True)).total,Decimal('0.08116'))

    def test_eeg_never_gets_simulation_or_double_reduction(self):
        for supply in ('eeg_local','eeg_regional'):
            config = {'region':'STMK','supply_type':supply,'simulate_winap':True}
            self.assertFalse(TariffProfile.from_config(config).simulate_winap)
            for moment in ('2026-01-01T01:00','2026-07-01T12:00','2026-10-15T23:00'):
                self.assertEqual(
                    self.calculator.calculate(local(moment),TariffProfile('STMK',supply,simulate_winap=True)),
                    self.calculator.calculate(local(moment),TariffProfile('STMK',supply)),
                )

    def test_no_historical_or_future_rate_extrapolation(self):
        for year in range(2022,2026):
            moment = local(f'{year}-10-15T23:00')
            self.assertEqual(self.calculator.calculate(moment,TariffProfile('STMK',simulate_winap=True)),self.calculator.calculate(moment,TariffProfile('STMK')))
        self.assertIsNone(self.calculator.calculate(local('2027-10-01T23:00'),TariffProfile('STMK',simulate_winap=True)))

    def test_winter_clock_changes_keep_real_hours(self):
        for start,end,expected in (
            ('2026-03-28T23:00','2026-03-29T05:00',5),
            ('2026-10-24T23:00','2026-10-25T05:00',7),
        ):
            rows = list(self.calculator.series(local(start),local(end),TariffProfile('STMK',simulate_winap=True),60))
            self.assertEqual(len(rows),expected)
            self.assertTrue(all(p.winap_simulated_active and not p.snap_active for _,p in rows))
            self.assertEqual(len({t.astimezone(timezone.utc) for t,_ in rows}),expected)

    def test_forecast_uses_same_scenario_and_stops_at_five(self):
        profile = TariffProfile('STMK',simulate_winap=True)
        snapshot = self.calculator.snapshot(local('2026-10-15T23:34'),profile)
        rows = snapshot.forecast_attributes()['data']
        self.assertEqual(rows[0],{
            'start_time':'2026-10-15T23:00:00+02:00',
            'end_time':'2026-10-16T05:00:00+02:00',
            'price_eur_per_kwh':float(snapshot.current.total),
        })
        self.assertEqual(rows[1]['end_time'],'2026-10-16T23:00:00+02:00')
        self.assertEqual(rows[1]['price_eur_per_kwh'],0.09876)
        self.assertEqual(len(snapshot.forecast),168)

