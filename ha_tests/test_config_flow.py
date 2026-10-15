"""Exercise setup, reconfiguration and migration with real Home Assistant APIs."""

import unittest
from unittest.mock import MagicMock, patch

from custom_components.gridfees_aut import async_migrate_entry
from custom_components.gridfees_aut.config_flow import GridfeesAutConfigFlow


class ConfigFlowTests(unittest.IsolatedAsyncioTestCase):
    def flow(self, source='user'):
        flow = GridfeesAutConfigFlow()
        flow.hass = MagicMock()
        flow.context = {'source':source}
        return flow

    async def test_regular_setup_defaults_and_saved_simulation(self):
        flow = self.flow()
        with patch.object(flow,'_async_current_entries',return_value=[]):
            form = await flow.async_step_user({'region':'STMK','supply_type':'grid'})
            self.assertEqual(form['step_id'],'tariff')
            values = form['data_schema']({})
            self.assertEqual(values,{'household':True,'snap_eligible':True,'simulate_winap':False})
            result = await flow.async_step_tariff({**values,'simulate_winap':True})
            self.assertEqual(result['type'],'create_entry')
            self.assertTrue(result['data']['simulate_winap'])
            self.assertEqual(result['title'],'gridfees Steiermark Regular grid supply')

    async def test_eeg_skips_assumptions(self):
        for supply in ('eeg_local','eeg_regional'):
            flow = self.flow()
            with patch.object(flow,'_async_current_entries',return_value=[]):
                result = await flow.async_step_user({'region':'STMK','supply_type':supply})
            self.assertEqual(result['type'],'create_entry')
            self.assertFalse(result['data']['simulate_winap'])
            self.assertFalse(result['data']['snap_eligible'])

    async def test_reconfigure_preserves_identity_and_saved_defaults(self):
        flow = self.flow('reconfigure')
        entry = MagicMock(entry_id='existing-id',data={
            'region':'STMK','supply_type':'grid','household':False,'snap_eligible':False,
        })
        with patch.object(flow,'_get_reconfigure_entry',return_value=entry), patch.object(flow,'_async_current_entries',return_value=[entry]), patch.object(flow,'async_update_reload_and_abort',return_value={'type':'abort','reason':'reconfigure_successful'}) as update:
            form = await flow.async_step_reconfigure()
            self.assertEqual(form['data_schema']({}),{'household':False,'snap_eligible':False,'simulate_winap':False})
            result = await flow.async_step_tariff({'household':False,'snap_eligible':False,'simulate_winap':True})
            self.assertEqual(result['reason'],'reconfigure_successful')
            update.assert_called_once_with(entry,data_updates={**entry.data,'simulate_winap':True},reason='reconfigure_successful')

    async def test_duplicate_reconfiguration_does_not_modify_either_entry(self):
        flow = self.flow('reconfigure')
        flow._profile = {'region':'STMK','supply_type':'grid'}
        current = MagicMock(data={**flow._profile,'simulate_winap':False})
        duplicate = MagicMock(data={**flow._profile,'simulate_winap':True})
        with patch.object(flow,'_get_reconfigure_entry',return_value=current), patch.object(flow,'_async_current_entries',return_value=[current,duplicate]), patch.object(flow,'async_update_reload_and_abort') as update:
            result = await flow.async_step_tariff({'household':True,'snap_eligible':True,'simulate_winap':True})
            self.assertEqual(result['reason'],'already_configured')
            update.assert_not_called()

    async def test_migrate_existing_profile_defaults_simulation_off(self):
        for supply in ('grid','eeg_local','eeg_regional'):
            hass = MagicMock()
            data = {'region':'STMK','supply_type':supply,'household':False,'snap_eligible':False}
            entry = MagicMock(version=1,minor_version=2,data=data)
            self.assertTrue(await async_migrate_entry(hass,entry))
            changes = hass.config_entries.async_update_entry.call_args.kwargs
            self.assertEqual(changes['minor_version'],3)
            self.assertFalse(changes['data']['simulate_winap'])
            self.assertEqual(changes['data']['region'],'STMK')
            if supply == 'grid':
                self.assertFalse(changes['data']['household'])

