"""Unit tests for the Vedic Choghadiya engine.

DIVASTRO-103: slots are cut at the Swiss Ephemeris sunrise/sunset the Panchang
prints (it used to be a seasonal estimate ~20-50 min off), and the in-app tool
(/api/choghadiya) and the server-rendered /choghadiya pages share one
implementation. A throwaway SQLite database is used — never a real one.

    ~/.venvs/divineastro/bin/python -u -m tests.test_choghadiya
"""

import datetime as dt
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_chog_")
os.environ.setdefault("ASTRO_DATABASE_URL", f"sqlite:///{Path(_tmp).as_posix()}/t.db")

from fastapi.testclient import TestClient  # noqa: E402

from app import seo_cities, seo_pages  # noqa: E402
from app.astro import panchang  # noqa: E402
from app.astro.choghadiya import (  # noqa: E402
    DAY_SEQUENCE, NIGHT_SEQUENCE, get_choghadiya_schedule,
)
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)

IST = "Asia/Kolkata"
CITIES = ["new-delhi", "mumbai", "chennai", "guwahati"]
DATES = ["2026-06-21", "2026-12-21", "2026-10-03"]      # summer, winter, the bug report date

# Classical sequence: the day starts with the weekday lord's choghadiya, the
# night with the lord five places on; each then runs through the fixed cycle.
DAY_CYCLE = ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]
NIGHT_CYCLE = ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"]
DAY_START = ["Udveg", "Amrit", "Rog", "Labh", "Shubh", "Char", "Kaal"]     # Sun..Sat
NIGHT_START = ["Shubh", "Char", "Kaal", "Udveg", "Amrit", "Rog", "Labh"]   # Sun..Sat


def _city(slug):
    return seo_cities.BY_SLUG[slug]


def _iso(s):
    return dt.datetime.fromisoformat(s)


class TestEphemerisBoundaries(unittest.TestCase):
    def test_slots_cut_at_ephemeris_sunrise_and_sunset(self):
        for slug in CITIES:
            c = _city(slug)
            for d in DATES:
                with self.subTest(city=slug, date=d):
                    rise, sset, nrise = panchang.sun_times(d, c.latitude, c.longitude, IST)
                    p = panchang.daily_panchang(d, c.latitude, c.longitude, IST)
                    # sun_times is exactly what the Panchang prints
                    self.assertEqual(rise.isoformat(), p["sun"]["rise"])
                    self.assertEqual(sset.isoformat(), p["sun"]["set"])
                    self.assertEqual(nrise.isoformat(), p["sun"]["next_rise"])

                    r = get_choghadiya_schedule(d, c.latitude, c.longitude, IST)
                    day, night = r["day_slots"], r["night_slots"]
                    self.assertEqual((len(day), len(night)), (8, 8))
                    self.assertEqual(_iso(day[0]["start_iso"]), rise)
                    self.assertEqual(_iso(day[-1]["end_iso"]), sset)
                    self.assertEqual(_iso(night[0]["start_iso"]), sset)
                    self.assertEqual(_iso(night[-1]["end_iso"]), nrise)
                    self.assertEqual(r["sunrise"], rise.strftime("%H:%M"))
                    self.assertEqual(r["sunset"], sset.strftime("%H:%M"))

                    slots = day + night
                    for a, b in zip(slots, slots[1:]):
                        self.assertEqual(a["end_iso"], b["start_iso"])      # contiguous
                    for s in slots:
                        self.assertLess(_iso(s["start_iso"]), _iso(s["end_iso"]))
                    # equal eighths (within a microsecond of rounding)
                    for part in (day, night):
                        lens = [(_iso(s["end_iso"]) - _iso(s["start_iso"])).total_seconds() for s in part]
                        self.assertLess(max(lens) - min(lens), 1e-5)

    def test_delhi_bug_report_date(self):
        # Delhi, 3 Oct 2026: ephemeris sunrise ~06:14, sunset ~18:0x. The old
        # seasonal formula gave 05:53 / 18:48.
        r = get_choghadiya_schedule("2026-10-03", 28.6139, 77.2090, IST)
        self.assertTrue("06:12" <= r["day_slots"][0]["start"] <= "06:16", r["sunrise"])
        self.assertTrue("17:55" <= r["sunset"] <= "18:05", r["sunset"])

    def test_summer_day_longer_than_winter(self):
        s = get_choghadiya_schedule("2026-06-21", 28.6139, 77.2090, IST)
        w = get_choghadiya_schedule("2026-12-21", 28.6139, 77.2090, IST)
        dur = lambda r: _iso(r["day_slots"][-1]["end_iso"]) - _iso(r["day_slots"][0]["start_iso"])  # noqa: E731
        self.assertGreater(dur(s) - dur(w), dt.timedelta(hours=3))

    def test_polar_night_is_an_error_not_garbage(self):
        with self.assertRaises(ValueError):
            get_choghadiya_schedule("2026-12-21", 78.22, 15.65, "Arctic/Longyearbyen")


class TestSequence(unittest.TestCase):
    def test_tables_follow_the_classical_cycle(self):
        for v in range(7):
            with self.subTest(vara=v):
                for table, cycle, starts in ((DAY_SEQUENCE, DAY_CYCLE, DAY_START),
                                             (NIGHT_SEQUENCE, NIGHT_CYCLE, NIGHT_START)):
                    seq = table[v]
                    self.assertEqual(seq[0], starts[v])
                    k = cycle.index(seq[0])
                    self.assertEqual(seq, [cycle[(k + i) % 7] for i in range(8)])

    def test_all_seven_weekdays(self):
        # 2026-10-04 is a Sunday
        names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for v in range(7):
            d = dt.date(2026, 10, 4) + dt.timedelta(days=v)
            with self.subTest(date=d):
                r = get_choghadiya_schedule(d)
                self.assertEqual(r["weekday"], names[v])
                self.assertEqual([s["name"] for s in r["day_slots"]],
                                 [DAY_CYCLE[(DAY_CYCLE.index(DAY_START[v]) + i) % 7] for i in range(8)])
                self.assertEqual([s["name"] for s in r["night_slots"]],
                                 [NIGHT_CYCLE[(NIGHT_CYCLE.index(NIGHT_START[v]) + i) % 7] for i in range(8)])
                self.assertEqual([s["index"] for s in r["day_slots"] + r["night_slots"]],
                                 list(range(1, 17)))

    def test_sunday_choghadiya_sequence(self):
        # 2026-08-30 is a Sunday
        res = get_choghadiya_schedule(target_date="2026-08-30", lang="en")
        self.assertEqual(res["weekday"], "Sunday")
        self.assertEqual(res["day_slots"][0]["name"], "Udveg")
        self.assertEqual(res["night_slots"][0]["name"], "Shubh")

    def test_active_slot_detection(self):
        tz = dt.timezone(dt.timedelta(hours=5, minutes=30))
        now = dt.datetime(2026, 8, 30, 10, 30, tzinfo=tz)
        res = get_choghadiya_schedule(target_date="2026-08-30", now_dt=now, lang="en")
        self.assertTrue(res["active_slot"]["is_current"])
        self.assertTrue(res["active_slot"]["start_iso"] <= now.isoformat() < res["active_slot"]["end_iso"])

    def test_hindi_localization(self):
        res = get_choghadiya_schedule(target_date="2026-08-30", lang="hi")
        self.assertEqual(res["weekday_hi"], "रविवार")
        self.assertEqual(res["day_slots"][0]["name_label"], "उद्वेग")
        self.assertIn("अति शुभ", [s["quality_label"] for s in res["day_slots"]])


class TestToolAndSeoPageAgree(unittest.TestCase):
    def test_api_and_seo_slots_identical(self):
        for slug in CITIES:
            c = _city(slug)
            for d in DATES:
                with self.subTest(city=slug, date=d):
                    res = client.get("/api/choghadiya", params={
                        "date": d, "latitude": c.latitude, "longitude": c.longitude,
                        "timezone": IST})
                    self.assertEqual(res.status_code, 200, res.text)
                    api = res.json()
                    p = panchang.daily_panchang(d, c.latitude, c.longitude, c.timezone)
                    seo_day, seo_night = seo_pages.choghadiya_slots(p)
                    for a, s in zip(api["day_slots"] + api["night_slots"], seo_day + seo_night):
                        self.assertEqual(a["name"], s["name"])
                        self.assertEqual(_iso(a["start_iso"]), s["start"])
                        self.assertEqual(_iso(a["end_iso"]), s["end"])

    def test_rendered_page_matches_api_today(self):
        today = dt.datetime.now(ZoneInfo(IST)).date()
        for slug in CITIES:
            c = _city(slug)
            with self.subTest(city=slug):
                html = client.get(f"/choghadiya/{slug}").text
                api = client.get("/api/choghadiya", params={
                    "date": today.isoformat(), "latitude": c.latitude,
                    "longitude": c.longitude, "timezone": IST}).json()
                page_starts = re.findall(r"<tr><td>(\d{1,2}:\d{2} [AP]M)", html)
                api_starts = [dt.datetime.strptime(s["start"], "%H:%M").strftime("%I:%M %p").lstrip("0")
                              for s in api["day_slots"] + api["night_slots"]]
                self.assertEqual(page_starts, api_starts)


class TestNoApproximation(unittest.TestCase):
    def test_seasonal_formula_is_gone(self):
        for path in (ROOT / "app").rglob("*.py"):
            self.assertNotIn("_approx_sun_times", path.read_text(encoding="utf-8"), str(path))

    def test_tool_defaults_to_local_not_utc_date(self):
        js = (ROOT / "app" / "static" / "tools.js").read_text(encoding="utf-8")
        block = js[js.index("#open-choghadiya"):js.index("function renderChoghadiya")]
        self.assertNotIn("toISOString", block)
        self.assertIn("Asia/Kolkata", js[js.index("const choToday"):js.index("#open-choghadiya")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
