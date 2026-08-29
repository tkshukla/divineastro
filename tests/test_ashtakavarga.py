"""Unit tests for the Parashari Ashtakavarga calculation engine."""

import unittest
from app.astro.ashtakavarga import calculate_ashtakavarga


class TestAshtakavarga(unittest.TestCase):
    def setUp(self):
        # Realistic Sidereal Natal Chart planetary placements
        self.sample_bundle = {
            "objects": {
                "ASC": {"sign": "Aries"},
                "Sun": {"sign": "Taurus"},
                "Moon": {"sign": "Cancer"},
                "Mars": {"sign": "Leo"},
                "Mercury": {"sign": "Taurus"},
                "Jupiter": {"sign": "Scorpio"},
                "Venus": {"sign": "Gemini"},
                "Saturn": {"sign": "Aquarius"},
            }
        }

    def test_sav_sum_is_337(self):
        res = calculate_ashtakavarga(self.sample_bundle, lang="en")
        self.assertEqual(res["total_bindus"], 337)
        self.assertEqual(sum(res["sav_by_sign"]), 337)
        self.assertEqual(sum(h["bindus"] for h in res["sav_by_house"]), 337)

    def test_bav_planet_totals(self):
        res = calculate_ashtakavarga(self.sample_bundle, lang="en")
        bav = res["bav"]
        self.assertEqual(sum(bav["Sun"]), 48)
        self.assertEqual(sum(bav["Moon"]), 49)
        self.assertEqual(sum(bav["Mars"]), 39)
        self.assertEqual(sum(bav["Mercury"]), 54)
        self.assertEqual(sum(bav["Jupiter"]), 56)
        self.assertEqual(sum(bav["Venus"]), 52)
        self.assertEqual(sum(bav["Saturn"]), 39)

    def test_hindi_localization(self):
        res = calculate_ashtakavarga(self.sample_bundle, lang="hi")
        self.assertEqual(res["total_bindus"], 337)
        self.assertIn("बिंदु", res["financial_note"])
        self.assertTrue(len(res["table"]["rows"]) == 12)
        self.assertIn("कुल योग", res["table"]["headers"])


if __name__ == "__main__":
    unittest.main()
