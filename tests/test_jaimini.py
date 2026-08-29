"""Unit tests for the Jaimini Astrology Engine (Chara Karakas & Arudha Padas)."""

import unittest
from app.astro import jaimini


class TestJaimini(unittest.TestCase):
    def setUp(self):
        # Sample sidereal Vedic chart bundle
        self.bundle = {
            "meta": {"zodiac": "sidereal", "ayanamsa": "lahiri"},
            "objects": {
                "ASC": {"longitude": 15.0},      # Aries (H1)
                "Sun": {"longitude": 28.5},      # Aries 28°30' (AK candidate)
                "Moon": {"longitude": 54.0},     # Taurus 24°00' (AmK candidate)
                "Mars": {"longitude": 110.0},    # Cancer 20°00' (BK candidate)
                "Mercury": {"longitude": 165.0}, # Virgo 15°00' (MK candidate)
                "Jupiter": {"longitude": 222.0}, # Scorpio 12°00' (PK candidate)
                "Venus": {"longitude": 278.0},   # Capricorn 8°00' (GK candidate)
                "Saturn": {"longitude": 332.0},  # Pisces 2°00' (DK candidate)
                "True Node": {"longitude": 190.0},
            }
        }

    def test_chara_karakas_ranking(self):
        data = jaimini.get_jaimini_data(self.bundle, lang="en")
        karakas = data["karakas"]
        self.assertEqual(len(karakas), 7)
        
        # In our mock data:
        # Sun has 28.5° -> AK (Atmakaraka)
        # Moon has 24.0° -> AmK (Amatyakaraka)
        # Mars has 20.0° -> BK (Bhratrikaraka)
        # Mercury has 15.0° -> MK (Matrikaraka)
        # Jupiter has 12.0° -> PK (Putrakaraka)
        # Venus has 8.0° -> GK (Gnatikaraka)
        # Saturn has 2.0° -> DK (Darakaraka)
        
        self.assertEqual(karakas[0]["code"], "AK")
        self.assertEqual(karakas[0]["planet"], "Sun")
        
        self.assertEqual(karakas[1]["code"], "AmK")
        self.assertEqual(karakas[1]["planet"], "Moon")
        
        self.assertEqual(karakas[6]["code"], "DK")
        self.assertEqual(karakas[6]["planet"], "Saturn")

    def test_karakamsha_calculation(self):
        data = jaimini.get_jaimini_data(self.bundle, lang="en")
        kl = data["karakamsha"]
        self.assertEqual(kl["atmakaraka"], "Sun")
        self.assertTrue(len(kl["sign"]) > 0)
        self.assertTrue(len(kl["summary"]) > 0)

    def test_arudha_padas_count(self):
        data = jaimini.get_jaimini_data(self.bundle, lang="en")
        arudhas = data["arudhas"]
        self.assertEqual(len(arudhas), 12)
        
        # A1 is Arudha Lagna (AL)
        self.assertEqual(arudhas[0]["code"], "AL")
        self.assertIn(arudhas[0]["sign"], jaimini.SIGNS)
        
        # A12 is Upapada Lagna (UL)
        self.assertEqual(arudhas[11]["code"], "UL")
        self.assertIn(arudhas[11]["sign"], jaimini.SIGNS)

    def test_hindi_localization(self):
        data_hi = jaimini.get_jaimini_data(self.bundle, lang="hi")
        self.assertTrue(any("\u0900" <= c <= "\u097F" for c in data_hi["karakas"][0]["title"]))
        self.assertTrue(any("\u0900" <= c <= "\u097F" for c in data_hi["karakamsha"]["summary"]))


if __name__ == "__main__":
    unittest.main()
