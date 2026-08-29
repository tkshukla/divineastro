"""Test suite for Muhurat Finder engine."""

import datetime as dt
import unittest

from app.astro import muhurat


class TestMuhurat(unittest.TestCase):
    def test_muhurat_marriage_scan(self):
        d_from = dt.date(2026, 9, 1)
        d_to = dt.date(2026, 9, 7)
        res_en = muhurat.find_muhurat(
            "marriage", d_from, d_to, 28.6139, 77.2090, "Asia/Kolkata", language="en"
        )
        self.assertEqual(len(res_en), 7)
        self.assertIn("date", res_en[0])
        self.assertIn("verdict", res_en[0])
        self.assertIn("score", res_en[0])
        self.assertIn(res_en[0]["verdict"], ("Auspicious", "Moderate", "Inauspicious"))
        
        # Test Hindi output
        res_hi = muhurat.find_muhurat(
            "marriage", d_from, d_to, 28.6139, 77.2090, "Asia/Kolkata", language="hi"
        )
        self.assertEqual(len(res_hi), 7)
        # Check Devanagari presence in verdict and vara
        self.assertTrue(any("\u0900" <= c <= "\u097F" for c in res_hi[0]["verdict"]))
        self.assertTrue(any("\u0900" <= c <= "\u097F" for c in res_hi[0]["vara"]))

    def test_invalid_range_and_event(self):
        d_from = dt.date(2026, 9, 10)
        d_to = dt.date(2026, 9, 1)
        with self.assertRaises(ValueError):
            muhurat.find_muhurat("marriage", d_from, d_to, 28.6139, 77.2090, "Asia/Kolkata")
            
        with self.assertRaises(ValueError):
            muhurat.find_muhurat("unknown_event", d_to, d_from, 28.6139, 77.2090, "Asia/Kolkata")

    def test_range_limit(self):
        d_from = dt.date(2026, 1, 1)
        d_to = dt.date(2026, 5, 1)  # > 90 days
        with self.assertRaises(ValueError):
            muhurat.find_muhurat("general", d_from, d_to, 28.6139, 77.2090, "Asia/Kolkata")


if __name__ == "__main__":
    unittest.main()
