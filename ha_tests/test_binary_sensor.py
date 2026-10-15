"""Check the winter status entity against actual tariff snapshots."""

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

from custom_components.gridfees_aut.binary_sensor import (
    GridfeesWinapSensor,
    async_setup_entry,
)
from custom_components.gridfees_aut.calculator import TariffCalculator, TariffProfile

DATASET = Path(__file__).resolve().parents[1] / 'custom_components/gridfees_aut/tariffs.json'
VIENNA = ZoneInfo('Europe/Vienna')


class BinarySensorTests(unittest.IsolatedAsyncioTestCase):
    def coordinator(self, moment, enabled=True, supply='grid'):
        calculator = TariffCalculator.from_file(DATASET)
        profile = TariffProfile('STMK',supply,simulate_winap=enabled)
        return SimpleNamespace(
            entry=SimpleNamespace(entry_id='existing-profile-id'),
            profile=profile,
            calculator=calculator,
            data=calculator.snapshot(datetime.fromisoformat(moment).replace(tzinfo=VIENNA),profile),
            last_update_success=True,
        )

    async def test_both_indicators_registered_enabled_with_distinct_stable_ids(self):
        coordinator = self.coordinator('2026-10-15T23:00')
        add = MagicMock()
        await async_setup_entry(MagicMock(),SimpleNamespace(runtime_data=coordinator),add)
        sensors = add.call_args.args[0]
        self.assertEqual([s.unique_id for s in sensors],[
            'existing-profile-id_snap_active','existing-profile-id_winap_active',
        ])
        self.assertTrue(all(s.entity_registry_enabled_default for s in sensors))
        self.assertEqual([s.is_on for s in sensors],[False,True])

    async def test_winter_state_follows_setting_window_and_supply_type(self):
        for moment,enabled,supply,expected in (
            ('2026-10-15T23:00',True,'grid',True),
            ('2026-10-16T04:59',True,'grid',True),
            ('2026-10-16T05:00',True,'grid',False),
            ('2026-10-15T23:00',False,'grid',False),
            ('2026-07-15T12:00',True,'grid',False),
            ('2026-10-15T23:00',True,'eeg_local',False),
            ('2026-10-15T23:00',True,'eeg_regional',False),
        ):
            with self.subTest(moment=moment,enabled=enabled,supply=supply):
                sensor = GridfeesWinapSensor(self.coordinator(moment,enabled,supply))
                self.assertEqual(sensor.is_on,expected)
                self.assertTrue(sensor.available)

    async def test_unsupported_rates_and_failed_updates_are_unavailable(self):
        coordinator = self.coordinator('2027-01-01T01:00')
        sensor = GridfeesWinapSensor(coordinator)
        self.assertIsNone(sensor.is_on)
        self.assertFalse(sensor.available)
        coordinator.data = None
        self.assertIsNone(sensor.is_on)
        self.assertFalse(sensor.available)
        coordinator = self.coordinator('2026-10-15T23:00')
        coordinator.last_update_success = False
        self.assertFalse(GridfeesWinapSensor(coordinator).available)
