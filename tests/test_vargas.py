"""Unit tests for the Parashari Shodashvarga divisional charts engine."""

import unittest
from app.astro.vargas import varga_sign, get_shodashvarga_data


class TestVargas(unittest.TestCase):
    def test_navamsha_calc(self):
        # 0° Aries (lon=0.0) in D9 -> Aries
        self.assertEqual(varga_sign(0.0, "D9"), "Aries")
        # 3°30' Aries (lon=3.5) in D9 -> Taurus
        self.assertEqual(varga_sign(3.5, "D9"), "Taurus")
        # 13.5° Leo (lon=133.5) -> Leo is fire sign (starts Aries); 13.5° is 5th navamsha -> Leo
        self.assertEqual(varga_sign(133.5, "D9"), "Leo")

    def test_dashamsha_calc(self):
        # 0° Aries in D10 -> Aries
        self.assertEqual(varga_sign(0.0, "D10"), "Aries")
        # 4° Aries in D10 -> Taurus
        self.assertEqual(varga_sign(4.0, "D10"), "Taurus")

    def test_shodashvarga_bundle(self):
        bundle = {
            "meta": {"zodiac": "sidereal", "ayanamsa": "lahiri"},
            "objects": {
                "ASC": {"longitude": 15.0},
                "Sun": {"longitude": 45.0},
                "Moon": {"longitude": 105.0},
                "Mars": {"longitude": 125.0},
                "Mercury": {"longitude": 50.0},
                "Jupiter": {"longitude": 220.0},
                "Venus": {"longitude": 75.0},
                "Saturn": {"longitude": 310.0},
                "True Node": {"longitude": 190.0},
            }
        }
        data = get_shodashvarga_data(bundle, lang="en")
        self.assertIn("D1", data["vargas"])
        self.assertIn("D9", data["vargas"])
        self.assertIn("D10", data["vargas"])
        self.assertEqual(len(data["available_codes"]), 6)


if __name__ == "__main__":
    unittest.main()
