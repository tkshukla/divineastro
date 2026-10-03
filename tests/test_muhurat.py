"""Test suite for Muhurat Finder engine.

DIVASTRO-109 adds the classical period exclusions (Chaturmas, Kharmas, Adhik
Maas, Pitru Paksha, Shukra/Guru asta). The expectations below are taken from
published 2026-27 vivah / griha pravesh lists for New Delhi (Drik Panchang,
cross-read with SmartPuja and Hindi news almanac round-ups, 2026-10-03):

    vivah 2026 open months:  Feb Mar Apr May Jun Jul Nov Dec  (none in Jan:
        Shukra asta; none Aug-Oct: Guru asta + Chaturmas; first Nov date 21st)
    vivah 2027 open months:  Jan-Jul, Nov, Dec
    griha pravesh 2026 open: Feb Mar Apr May Jun Jul Nov Dec

Exact days are NOT compared - sources differ by lagna and time-of-day rules,
and this engine scores the sunrise limbs - but no date may fall in a period
every source bars, and the set of open months must agree.

    ~/.venvs/divineastro/bin/python -u -m tests.test_muhurat
"""

import datetime as dt
import sys
import unittest
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.astro import muhurat  # noqa: E402
from app.astro import panchang  # noqa: E402

DELHI = (28.6139, 77.2090, "Asia/Kolkata")


@lru_cache(maxsize=None)
def _year(event: str, start: dt.date, end: dt.date) -> tuple:
    """Scan through the public API in <= 90-day chunks, as a client would."""
    out = []
    cur = start
    while cur <= end:
        stop = min(end, cur + dt.timedelta(days=muhurat.MAX_SCAN_DAYS - 1))
        out += muhurat.find_muhurat(event, cur, stop, *DELHI)
        cur = stop + dt.timedelta(days=1)
    return tuple(out)


def _auspicious(event, start, end):
    return [dt.date.fromisoformat(r["date"]) for r in _year(event, start, end)
            if r["verdict"] == "Auspicious"]


def _day(event, date, language="en"):
    return muhurat.find_muhurat(event, date, date, *DELHI, language=language)[0]


def _keys(event, date):
    return [p["key"] for p in _day(event, date)["excluded_periods"]]


class TestMuhurat(unittest.TestCase):
    def test_muhurat_marriage_scan(self):
        if panchang.swe is None:
            self.skipTest("swisseph engine not available in local environment")
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
        self.assertTrue(any("ऀ" <= c <= "ॿ" for c in res_hi[0]["verdict"]))
        self.assertTrue(any("ऀ" <= c <= "ॿ" for c in res_hi[0]["vara"]))

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


@unittest.skipIf(panchang.swe is None, "swisseph engine not available")
class TestLunarMonthAndCombustion(unittest.TestCase):
    def _month(self, y, m, d):
        import swisseph as swe
        return panchang.lunar_month_at(swe.julday(y, m, d, 6.0))

    def test_amanta_month_names_2026(self):
        self.assertEqual(self._month(2026, 4, 1)["name"], "Chaitra")
        self.assertEqual(self._month(2026, 7, 20)["name"], "Ashadha")
        self.assertEqual(self._month(2026, 10, 1)["name"], "Bhadrapada")
        self.assertEqual(self._month(2026, 11, 15)["name"], "Kartika")

    def test_adhik_jyeshtha_2026(self):
        m = self._month(2026, 5, 25)
        self.assertEqual((m["name"], m["adhika"]), ("Jyeshtha", True))
        m = self._month(2026, 6, 25)
        self.assertEqual((m["name"], m["adhika"]), ("Jyeshtha", False))
        self.assertFalse(self._month(2027, 5, 25)["adhika"])

    def test_combustion_matches_drik_delhi_2026(self):
        import swisseph as swe

        def jd(y, m, d):
            return swe.julday(y, m, d, 1.0)
        lat = DELHI[0]
        # Guru asta: Drik 15 Jul - 12 Aug 2026 (New Delhi).
        self.assertFalse(panchang.is_combust(jd(2026, 7, 10), "jupiter", lat))
        self.assertTrue(panchang.is_combust(jd(2026, 7, 20), "jupiter", lat))
        self.assertTrue(panchang.is_combust(jd(2026, 8, 10), "jupiter", lat))
        self.assertFalse(panchang.is_combust(jd(2026, 8, 15), "jupiter", lat))
        # Shukra asta (retrograde, 8 kalamsha): Drik 12 - 29 Oct 2026.
        self.assertFalse(panchang.is_combust(jd(2026, 10, 8), "venus", lat))
        self.assertTrue(panchang.is_combust(jd(2026, 10, 20), "venus", lat))
        self.assertFalse(panchang.is_combust(jd(2026, 11, 2), "venus", lat))
        # Shukra asta (direct, 10 kalamsha): Drik 11 Dec 2025 - 1 Feb 2026.
        self.assertTrue(panchang.is_combust(jd(2026, 1, 10), "venus", lat))
        self.assertFalse(panchang.is_combust(jd(2026, 3, 1), "venus", lat))

    def test_orbs_are_the_classical_figures(self):
        self.assertEqual(panchang.KALAMSHA,
                         {"venus": 10.0, "venus_retrograde": 8.0, "jupiter": 11.0})


@unittest.skipIf(panchang.swe is None, "swisseph engine not available")
class TestPeriodRules(unittest.TestCase):
    def test_chaturmas_boundaries_2026(self):
        # Devshayani Ekadashi 25 Jul 2026, Devuthani Ekadashi 20 Nov 2026.
        self.assertNotIn("chaturmas", _keys("marriage", dt.date(2026, 7, 24)))
        self.assertIn("chaturmas", _keys("marriage", dt.date(2026, 7, 25)))
        self.assertIn("chaturmas", _keys("marriage", dt.date(2026, 11, 20)))
        self.assertNotIn("chaturmas", _keys("marriage", dt.date(2026, 11, 21)))

    def test_pitru_paksha_2026(self):
        # Bhadrapada Purnima 26 Sep -> Sarva Pitru Amavasya 10 Oct 2026.
        self.assertNotIn("pitru_paksha", _keys("marriage", dt.date(2026, 9, 25)))
        self.assertIn("pitru_paksha", _keys("marriage", dt.date(2026, 9, 26)))
        self.assertIn("pitru_paksha", _keys("marriage", dt.date(2026, 10, 10)))
        self.assertNotIn("pitru_paksha", _keys("marriage", dt.date(2026, 10, 11)))

    def test_kharmas(self):
        self.assertIn("kharmas", _keys("marriage", dt.date(2026, 3, 20)))
        self.assertIn("kharmas", _keys("marriage", dt.date(2026, 12, 25)))
        self.assertIn("kharmas", _keys("marriage", dt.date(2027, 1, 10)))
        self.assertNotIn("kharmas", _keys("marriage", dt.date(2027, 1, 20)))
        self.assertNotIn("kharmas", _keys("marriage", dt.date(2026, 4, 20)))

    def test_asta_margin_vriddhatva_shishutva(self):
        # Guru asta begins ~14/15 Jul 2026; Drik bars vivah from 12 Jul
        # (3 days of Vriddhatva Brihaspati). 3 days, not more.
        self.assertEqual(muhurat.ASTA_MARGIN_DAYS, 3)
        self.assertIn("guru_asta", _keys("marriage", dt.date(2026, 7, 12)))
        self.assertNotIn("guru_asta", _keys("marriage", dt.date(2026, 7, 8)))
        # Shukra uday (retrograde asta ends ~28/29 Oct 2026) + 3 days shishutva.
        self.assertIn("shukra_asta", _keys("marriage", dt.date(2026, 10, 31)))
        self.assertNotIn("shukra_asta", _keys("marriage", dt.date(2026, 11, 3)))

    def test_adhik_maas(self):
        self.assertIn("adhik_maas", _keys("griha_pravesh", dt.date(2026, 6, 1)))
        self.assertNotIn("adhik_maas", _keys("griha_pravesh", dt.date(2026, 6, 20)))

    def test_event_applicability(self):
        aug = dt.date(2026, 8, 20)                  # Chaturmas, not Pitru Paksha
        self.assertEqual(_keys("namkaran", aug), [])
        self.assertEqual(_keys("general", aug), [])
        self.assertEqual(_keys("mundan", aug), ["chaturmas"])
        pitru = dt.date(2026, 10, 1)
        self.assertEqual(_keys("general", pitru), ["pitru_paksha"])
        self.assertEqual(_keys("namkaran", pitru), [])

    def test_reasons_and_response_shape(self):
        r = _day("marriage", dt.date(2026, 8, 20))
        for key in ("date", "vara", "tithi", "nakshatra", "yoga", "karana", "score",
                    "verdict", "badge", "abhijit", "rahu_kaal", "reasons",
                    "sunrise", "sunset"):
            self.assertIn(key, r)
        self.assertTrue(r["excluded"])
        self.assertEqual(r["verdict"], "Inauspicious")
        self.assertIn({"key": "chaturmas", "name": "Chaturmas"}, r["excluded_periods"])
        self.assertTrue(any(x.startswith("Chaturmas") for x in r["reasons"]))
        hi = _day("marriage", dt.date(2026, 8, 20), language="hi")
        self.assertIn({"key": "chaturmas", "name": "चातुर्मास"}, hi["excluded_periods"])
        ok = _day("marriage", dt.date(2026, 11, 25))
        self.assertFalse(ok["excluded"])
        self.assertEqual(ok["excluded_periods"], [])

    def test_amavasya_is_not_scored_as_purnima(self):
        # 10 Oct 2026 sunrise tithi is Amavasya; it must never be "Favourable".
        r = _day("namkaran", dt.date(2026, 10, 10))
        self.assertEqual(r["tithi"], "Amavasya")
        self.assertTrue(any("Inauspicious tithi" in x for x in r["reasons"]))


@unittest.skipIf(panchang.swe is None, "swisseph engine not available")
class TestPublishedListExpectations(unittest.TestCase):
    Y26 = (dt.date(2026, 1, 1), dt.date(2026, 12, 31))
    Y27 = (dt.date(2027, 1, 1), dt.date(2027, 12, 31))

    def _none_between(self, dates, a, b, label):
        bad = [d for d in dates if a <= d <= b]
        self.assertEqual(bad, [], f"{label}: dates inside {a}..{b}")

    def test_vivah_2026_open_months(self):
        dates = _auspicious("marriage", *self.Y26)
        self.assertEqual(sorted({d.month for d in dates}), [2, 3, 4, 5, 6, 7, 11, 12])

    def test_vivah_2026_no_dates_in_barred_periods(self):
        dates = _auspicious("marriage", *self.Y26)
        self._none_between(dates, dt.date(2026, 1, 1), dt.date(2026, 2, 1), "Shukra asta")
        self._none_between(dates, dt.date(2026, 3, 15), dt.date(2026, 4, 14), "Kharmas (Meena)")
        self._none_between(dates, dt.date(2026, 5, 17), dt.date(2026, 6, 15), "Adhik Jyeshtha")
        self._none_between(dates, dt.date(2026, 7, 12), dt.date(2026, 8, 12), "Guru asta + vriddhatva")
        self._none_between(dates, dt.date(2026, 7, 25), dt.date(2026, 11, 20), "Chaturmas")
        self._none_between(dates, dt.date(2026, 9, 26), dt.date(2026, 10, 10), "Pitru Paksha")
        self._none_between(dates, dt.date(2026, 12, 17), dt.date(2026, 12, 31), "Kharmas (Dhanu)")
        self.assertTrue(any(d.month == 11 for d in dates))
        self.assertTrue(any(d.month == 12 for d in dates))

    def test_vivah_2027_open_months_and_kharmas(self):
        dates = _auspicious("marriage", *self.Y27)
        self.assertEqual(sorted({d.month for d in dates}), [1, 2, 3, 4, 5, 6, 7, 11, 12])
        self._none_between(dates, dt.date(2027, 1, 1), dt.date(2027, 1, 14), "Kharmas (Dhanu)")
        self._none_between(dates, dt.date(2027, 7, 15), dt.date(2027, 11, 9), "Chaturmas")

    def test_griha_pravesh_2026(self):
        dates = _auspicious("griha_pravesh", *self.Y26)
        self.assertEqual(sorted({d.month for d in dates}), [2, 3, 4, 5, 6, 7, 11, 12])
        self._none_between(dates, dt.date(2026, 7, 25), dt.date(2026, 11, 20), "Chaturmas")
        self._none_between(dates, dt.date(2026, 9, 26), dt.date(2026, 10, 10), "Pitru Paksha")
        self._none_between(dates, dt.date(2026, 12, 17), dt.date(2026, 12, 31), "Kharmas")


if __name__ == "__main__":
    unittest.main()
