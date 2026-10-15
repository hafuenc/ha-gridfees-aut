"""Keep the English interface copy and legal link placeholders in sync."""

import ast
import json
from pathlib import Path
import re
import unittest

INTEGRATION = Path(__file__).resolve().parents[1] / 'custom_components/gridfees_aut'


class SetupCopyTests(unittest.TestCase):
    def test_translation_matches_source_and_resolves_every_legal_link(self):
        source = json.loads((INTEGRATION / 'strings.json').read_text(encoding='utf-8'))
        english = json.loads((INTEGRATION / 'translations/en.json').read_text(encoding='utf-8'))
        self.assertEqual(source,english)
        tree = ast.parse((INTEGRATION / 'config_flow.py').read_text(encoding='utf-8'))
        placeholders = next(
            ast.literal_eval(kw.value)
            for node in ast.walk(tree) if isinstance(node,ast.Call)
            for kw in node.keywords if kw.arg == 'description_placeholders'
        )
        descriptions = source['config']['step']['tariff']['data_description']
        used = set(re.findall(r'\{(\w+)\}', '\n'.join(descriptions.values())))
        self.assertEqual(used,set(placeholders))
        self.assertTrue(all(url.startswith('https://') for url in placeholders.values()))
        self.assertIn('1 October 2027',descriptions['simulate_winap'])

