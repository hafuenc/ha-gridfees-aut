"""Check generated names and recognition of earlier default titles."""

from pathlib import Path
import sys
import unittest

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components/gridfees_aut"
sys.path.insert(0, str(INTEGRATION))
from const import REGIONS, SUPPLY_TYPES, legacy_profile_titles, profile_title  # noqa: E402


class ProfileNameTests(unittest.TestCase):
    def test_requested_default_name(self) -> None:
        self.assertEqual(
            profile_title("STMK", "grid"),
            "gridfees Steiermark Regular grid supply",
        )

    def test_all_profiles_have_prefix_and_distinct_names(self) -> None:
        names = {
            profile_title(region, supply)
            for region in REGIONS
            for supply in SUPPLY_TYPES
        }
        self.assertEqual(len(names), 42)
        self.assertTrue(all(name.startswith("gridfees ") for name in names))
        self.assertEqual(REGIONS["KTN"], "Kärnten")
        self.assertEqual(REGIONS["NOE"], "Niederösterreich")
        self.assertEqual(REGIONS["OOE"], "Oberösterreich")
        self.assertEqual(REGIONS["WIEN"], "Wien")

    def test_only_generated_legacy_titles_are_recognized(self) -> None:
        titles = legacy_profile_titles("STMK", "grid")
        self.assertIn("Styria · Regular grid supply", titles)
        self.assertIn("Steiermark · grid", titles)
        self.assertIn("Steiermark · Netzbezug", titles)
        self.assertNotIn("My home", titles)
        self.assertNotIn("gridfees Steiermark Regular grid supply", titles)


if __name__ == "__main__":
    unittest.main()
