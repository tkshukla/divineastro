"""Unit tests for the Vedic Choghadiya engine."""

import datetime as dt
import unittest
from app.astro.choghadiya import get_choghadiya_schedule


class TestChoghadiya(unittest.TestCase):
    def test_sunday_choghadiya_sequence(self):
        # 2026-08-30 is a Sunday
        res = get_choghadiya_schedule(target_date="2026-08-30", lang="en")
        self.assertEqual(res["weekday"], "Sunday")
        self.assertEqual(len(res["day_slots"]), 8)
        self.assertEqual(len(res["night_slots"]), 8)
        # Sunday first day slot is Udveg
        self.assertEqual(res["day_slots"][0]["name"], "Udveg")
        # Sunday first night slot is Shubh
        self.assertEqual(res["night_slots"][0]["name"], "Shubh")

    def test_active_slot_detection(self):
        # Specific time: 10:30 AM
        tz = dt.timezone(dt.timedelta(hours=5, minutes=30))
        now = dt.datetime(2026, 8, 30, 10, 30, tzinfo=tz)
        res = get_choghadiya_schedule(target_date="2026-08-30", now_dt=now, lang="en")
        self.assertIsNotNone(res["active_slot"])
        self.assertTrue(res["active_slot"]["is_current"])

    def test_hindi_localization(self):
        res = get_choghadiya_schedule(target_date="2026-08-30", lang="hi")
        self.assertEqual(res["weekday_hi"], "रविवार")
        self.assertEqual(res["day_slots"][0]["name_label"], "उद्वेग")
        self.assertIn("अति शुभ", [s["quality_label"] for s in res["day_slots"]])


if __name__ == "__main__":
    unittest.main()
