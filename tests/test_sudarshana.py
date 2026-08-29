"""Unit tests for the Sudarshana Chakra Triple-Lagna Synthesis Engine."""

import unittest
from app.astro import sudarshana


class TestSudarshana(unittest.TestCase):
    def setUp(self):
        self.bundle = {
            "meta": {"zodiac": "sidereal", "ayanamsa": "lahiri"},
            "objects": {
                "ASC": {"longitude": 15.0},      # Aries (0)
                "Moon": {"longitude": 45.0},     # Taurus (1)
                "Sun": {"longitude": 135.0},     # Leo (4)
                "Jupiter": {"longitude": 280.0}, # Capricorn (9)
                "Venus": {"longitude": 340.0},   # Pisces (11)
                "Mars": {"longitude": 200.0},    # Libra (6)
                "Saturn": {"longitude": 310.0},  # Aquarius (10)
                "Mercury": {"longitude": 140.0}, # Leo (4)
                "True Node": {"longitude": 190.0},
            }
        }

    def test_sudarshana_lagnas(self):
        data = sudarshana.get_sudarshana_data(self.bundle, lang="en")
        lagnas = data["lagnas"]
        self.assertEqual(lagnas["janma"]["sign"], "Aries")
        self.assertEqual(lagnas["chandra"]["sign"], "Taurus")
        self.assertEqual(lagnas["surya"]["sign"], "Leo")

    def test_sudarshana_houses_synthesis(self):
        data = sudarshana.get_sudarshana_data(self.bundle, lang="en")
        houses = data["houses"]
        self.assertEqual(len(houses), 12)
        
        for h in houses:
            self.assertIn("janma_tier", h)
            self.assertIn("chandra_tier", h)
            self.assertIn("surya_tier", h)
            self.assertTrue(1 <= h["score"] <= 5)
            self.assertIn(h["verdict_code"], ("strong", "average", "weak"))

    def test_hindi_localization(self):
        data_hi = sudarshana.get_sudarshana_data(self.bundle, lang="hi")
        self.assertTrue(any("\u0900" <= c <= "\u097F" for c in data_hi["summary"]))
        self.assertTrue(any("\u0900" <= c <= "\u097F" for c in data_hi["houses"][0]["title"]))


if __name__ == "__main__":
    unittest.main()
