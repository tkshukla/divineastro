"""Name tables for the site languages (DIVASTRO-123; pa ne as mr gu DIVASTRO-143).

app/astro/names_i18n.names_for(lang) gives one interface over names_hi.py,
festivals.py, matching.py (en/hi) and names_{kn,te,ta,ml,bn,or}.py. This
checks every table has exactly English's keys, every value is non-empty and in
its own script (no Devanagari leaking into a regional table), festivals.py's
keys and Ekadashi names are all covered, and add_names() mirrors add_hindi().

    ~/.venvs/divineastro/bin/python -u -m tests.test_names_i18n
"""

import copy
import datetime as dt
import sys
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import lang_data  # noqa: E402
from app.astro import festivals as F  # noqa: E402
from app.astro import matching as M  # noqa: E402
from app.astro import names_hi  # noqa: E402
from app.astro.choghadiya import CHOGHADIYA_INFO  # noqa: E402
from app.astro.names_i18n import (  # noqa: E402
    LANGS, REGIONAL_LANGS, TABLES, TEXTS, add_names, names_for,
)
from app.astro.panchang import LUNAR_MONTHS, TITHI_NAMES, YOGA_NAMES, daily_panchang  # noqa: E402
from app.chart_service import NAKSHATRAS, SIGNS  # noqa: E402

DELHI = (28.6139, 77.2090, "Asia/Kolkata")

SCRIPT = {
    "hi": (0x0900, 0x097F),
    "kn": (0x0C80, 0x0CFF),
    "te": (0x0C00, 0x0C7F),
    "ta": (0x0B80, 0x0BFF),
    "ml": (0x0D00, 0x0D7F),
    "bn": (0x0980, 0x09FF),
    "or": (0x0B00, 0x0B7F),
    "pa": (0x0A00, 0x0A7F),
    "gu": (0x0A80, 0x0AFF),
    "as": (0x0980, 0x09FF),          # Assamese is written in the Bengali block (ৰ ৱ included)
    "mr": (0x0900, 0x097F),
    "ne": (0x0900, 0x097F),
}
DEVANAGARI = (0x0900, 0x097F)
DANDA = {"।", "॥"}          # shared by Bengali, Odia, Punjabi, Gujarati, Marathi, Nepali and Assamese
JOINERS = {"‌", "‍"}
# Punctuation used in the tables besides ASCII.
EXTRA_PUNCT = {"—", "–", "·"}

# DIVASTRO-143: a new language's names_<code>.py is filled by a translator; what it leaves
# out is English (names_i18n._over_english). The own-script checks apply to the languages
# whose tables are complete: the six older ones, and a new one once READY includes "app".
COMPLETE = tuple(c for c in REGIONAL_LANGS
                 if c in lang_data.LEGACY_CODES or c in lang_data.ready("app"))
DEVANAGARI_LANGS = ("hi", "mr", "ne")

# Tables whose keys may differ from English (empty for some languages, or with
# optional extra keys).
OPTIONAL = {"SOLAR_MASA", "REGIONAL_NOTE"}


def _values(table):
    return list(table) if isinstance(table, tuple) else list(table.values())


def _strings(n):
    for name in TABLES:
        for v in _values(getattr(n, name)):
            yield name, v
    for name in TEXTS:
        yield name, getattr(n, name)


def _bad_chars(code: str, text: str) -> list[str]:
    lo, hi = SCRIPT[code]
    bad = []
    for ch in text:
        cp = ord(ch)
        if lo <= cp <= hi:
            continue
        if ch.isspace() or ch in JOINERS or ch in EXTRA_PUNCT:
            continue
        if cp < 0x80 and not ch.isalpha():       # ASCII digits and punctuation
            continue
        if ch in DANDA and code in ("bn", "or", "hi", "as", "mr", "ne", "pa", "gu"):
            continue
        bad.append(f"{ch} U+{cp:04X} {unicodedata.name(ch, '?')}")
    return bad


class TestShape(unittest.TestCase):
    def test_english_reference_sizes(self):
        en = names_for("en")
        self.assertEqual(set(en.TITHI), set(TITHI_NAMES) | {"Amavasya"})
        self.assertEqual(len(en.TITHI), 16)            # 30 tithis, 16 distinct names
        self.assertEqual(list(en.NAKSHATRAS), NAKSHATRAS)
        self.assertEqual(len(en.VARA), 7)
        self.assertEqual(list(en.YOGA), YOGA_NAMES)
        self.assertEqual(len(en.KARANA), 11)
        self.assertEqual(set(en.PAKSHA), {"Shukla", "Krishna"})
        self.assertEqual(list(en.MASA), LUNAR_MONTHS)
        self.assertEqual(list(en.RASHI), SIGNS)
        self.assertEqual(set(en.GRAHA), {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                                          "Venus", "Saturn", "Rahu", "Ketu"})
        self.assertEqual(set(en.CHOGHADIYA), set(CHOGHADIYA_INFO))
        self.assertEqual(set(en.CHOGHADIYA_QUALITY),
                         {v["quality"] for v in CHOGHADIYA_INFO.values()})
        self.assertEqual(set(en.FESTIVAL_TIMINGS), set(F.LABELS))
        self.assertEqual(set(en.KOOTA), set(M.KOOTA_LABELS_HI))
        self.assertEqual(set(en.GANA), set(M.GANA_ORDER))
        self.assertEqual(set(en.NADI), set(M.NADI_HUMOUR))
        self.assertEqual(set(en.VARNA), set(M.VARNA_RANK))
        self.assertEqual(set(en.VASHYA), set(M.VASHYA_GROUPS))
        self.assertEqual(set(en.YONI), {y for y, _ in M.YONI_OF_NAKSHATRA.values()})
        self.assertEqual(set(en.TARA), set(M.TARA_NAMES))
        self.assertEqual(len(en.MONTHS), 12)
        self.assertTrue({"rahu_kaal", "yamaganda", "gulika", "abhijit", "brahma_muhurta",
                         "pradosh", "nishita", "sunrise", "sunset", "moonrise", "moonset",
                         "parana", "durmuhurtam", "varjyam"} <= set(en.TIMINGS))

    def test_every_language_has_englishs_keys(self):
        en = names_for("en")
        for code in LANGS:
            n = names_for(code)
            for name in TABLES:
                if name in OPTIONAL:
                    continue
                with self.subTest(lang=code, table=name):
                    ref, got = getattr(en, name), getattr(n, name)
                    if isinstance(ref, tuple):
                        self.assertEqual(len(got), len(ref))
                    elif name == "CLOCK":
                        self.assertTrue(set(ref) <= set(got))
                    else:
                        self.assertEqual(set(got), set(ref))

    def test_optional_tables_only_use_known_keys(self):
        en = names_for("en")
        for code in LANGS:
            n = names_for(code)
            with self.subTest(lang=code):
                self.assertTrue(set(n.SOLAR_MASA) <= set(SIGNS))
                self.assertTrue(set(n.REGIONAL_NOTE) <= set(en.FESTIVALS))
        for code in ("ta", "ml", "bn", "or"):
            self.assertEqual(list(names_for(code).SOLAR_MASA), SIGNS, code)

    def test_values_non_empty_and_distinct(self):
        for code in LANGS:
            n = names_for(code)
            for name, v in _strings(n):
                with self.subTest(lang=code, table=name, value=v):
                    self.assertIsInstance(v, str)
                    self.assertTrue(v.strip())
                    self.assertEqual(v, v.strip())
            for name in ("TITHI", "NAKSHATRAS", "VARA", "YOGA", "KARANA", "MASA", "RASHI",
                         "GRAHA", "CHOGHADIYA", "WEEKDAY", "MONTHS", "EKADASHI", "YONI"):
                vals = _values(getattr(n, name))
                with self.subTest(lang=code, table=name):
                    self.assertEqual(len(vals), len(set(vals)))


class TestScript(unittest.TestCase):
    def test_regional_values_in_own_script(self):
        for code in COMPLETE + ("hi",):
            n = names_for(code)
            lo, hi = SCRIPT[code]
            for name, v in _strings(n):
                with self.subTest(lang=code, table=name, value=v):
                    self.assertEqual(_bad_chars(code, v), [])
                    self.assertTrue(any(lo <= ord(c) <= hi for c in v))

    def test_no_devanagari_in_regional_tables(self):
        for code in COMPLETE:
            if code in DEVANAGARI_LANGS:
                continue
            for name, v in _strings(names_for(code)):
                leaked = [c for c in v if DEVANAGARI[0] <= ord(c) <= DEVANAGARI[1]
                          and c not in DANDA]
                with self.subTest(lang=code, table=name, value=v):
                    self.assertEqual(leaked, [])

    def test_english_is_ascii_words(self):
        for name, v in _strings(names_for("en")):
            with self.subTest(table=name, value=v):
                self.assertTrue(all(ord(c) < 0x80 or c in EXTRA_PUNCT for c in v))

    def test_regional_conventions(self):
        ta, te, kn, ml = (names_for(c) for c in ("ta", "te", "kn", "ml"))
        bn, or_ = names_for("bn"), names_for("or")
        self.assertEqual(ta.TIMINGS["rahu_kaal"], "ராகு காலம்")
        self.assertEqual(ta.TIMINGS["yamaganda"], "எமகண்டம்")
        self.assertEqual(ta.TIMINGS["gulika"], "குளிகை")
        self.assertEqual(ta.NAKSHATRAS["Shravana"], "திருவோணம்")
        self.assertEqual(ta.NAKSHATRAS["Ardra"], "திருவாதிரை")
        self.assertEqual(ta.SOLAR_MASA["Aries"], "சித்திரை")
        self.assertEqual(ta.FESTIVALS["dussehra"], "விஜயதசமி")
        self.assertEqual(te.TIMINGS["rahu_kaal"], "రాహుకాలం")
        self.assertEqual(te.TIMINGS["durmuhurtam"], "దుర్ముహూర్తం")
        self.assertEqual(te.TIMINGS["varjyam"], "వర్జ్యం")
        self.assertEqual(te.MASA["Chaitra"], "చైత్రము")
        self.assertEqual(te.VARA["Sunday"], "ఆదివారం")
        self.assertEqual(kn.TIMINGS["rahu_kaal"], "ರಾಹು ಕಾಲ")
        self.assertEqual(kn.TIMINGS["yamaganda"], "ಯಮಗಂಡ ಕಾಲ")
        self.assertEqual(kn.TIMINGS["gulika"], "ಗುಳಿಕ ಕಾಲ")
        self.assertEqual(ml.TIMINGS["yamaganda"], "യമകണ്ടം")
        self.assertEqual(ml.NAKSHATRAS["Purva Bhadrapada"], "പൂരുരുട്ടാതി")
        self.assertEqual(ml.SOLAR_MASA["Leo"], "ചിങ്ങം")
        self.assertEqual(bn.FESTIVALS["dussehra"], "বিজয়া দশমী")
        self.assertEqual(bn.FESTIVALS["navratri"], "শারদীয় নবরাত্রি আরম্ভ")
        self.assertEqual(bn.REGIONAL_NOTE["navratri"], "দুর্গাপূজা")
        self.assertEqual(bn.SOLAR_MASA["Aries"], "বৈশাখ")
        self.assertEqual(or_.TIMINGS["rahu_kaal"], "ରାହୁ କାଳ")
        self.assertEqual(or_.SOLAR_MASA["Aries"], "ବୈଶାଖ")


class TestFestivals(unittest.TestCase):
    def test_every_festival_key_and_name_covered(self):
        keys = {s.key for s in F.RECURRING + F.FESTIVALS}
        keys |= {"makar_sankranti", "lohri", "holi", "ekadashi"} | set(F.OMITTED)
        ekadashis = {en for en, _ in list(F.EKADASHI_NAMES.values())
                     + list(F.ADHIKA_EKADASHI_NAMES.values())}
        self.assertEqual(len(ekadashis), 26)
        en = names_for("en")
        names_en = {s.name_en for s in F.RECURRING + F.FESTIVALS}
        self.assertEqual({en.FESTIVALS[s.key] for s in F.RECURRING + F.FESTIVALS}, names_en)
        for code in LANGS:
            n = names_for(code)
            with self.subTest(lang=code):
                self.assertTrue(keys <= set(n.FESTIVALS), keys - set(n.FESTIVALS))
                self.assertEqual(set(n.EKADASHI), ekadashis)

    def test_hindi_matches_festivals_py(self):
        hi = names_for("hi")
        for s in F.RECURRING + F.FESTIVALS:
            self.assertEqual(hi.FESTIVALS[s.key], s.name_hi)
        for en_name, hi_name in F.EKADASHI_NAMES.values():
            self.assertEqual(hi.EKADASHI[en_name], hi_name)
            self.assertEqual(hi.festival("ekadashi", en_name), hi_name)

    def test_a_year_of_observances_resolves_in_every_language(self):
        obs = F.observances(dt.date(2026, 1, 1), dt.date(2026, 12, 31), *DELHI)
        self.assertGreater(len(obs), 100)
        for code in REGIONAL_LANGS:
            n = names_for(code)
            lo, hi = SCRIPT[code]
            for o in obs:
                name = n.festival_name(o)
                with self.subTest(lang=code, key=o["key"], name_en=o["name_en"]):
                    if code in COMPLETE:       # a new language is English until its names are written
                        self.assertTrue(any(lo <= ord(c) <= hi for c in name), name)
                    else:
                        self.assertTrue(name)
                    for t in o["timings"]:
                        self.assertIn(t["key"], n.FESTIVAL_TIMINGS)
            # the generic word for an unnamed Ekadashi
            self.assertEqual(n.festival("ekadashi"), n.FESTIVALS["ekadashi"])
        self.assertEqual(names_for("en").festival_name(obs[0]), obs[0]["name_en"])


class TestInterface(unittest.TestCase):
    def test_unknown_language_is_english(self):
        en = names_for("en")
        for code in (None, "", "fr", "xx", "hindi"):
            self.assertIs(names_for(code), en)
        self.assertIs(names_for("TA"), names_for("ta"))

    def test_tables_are_read_only(self):
        with self.assertRaises(TypeError):
            names_for("ta").TITHI["Ashtami"] = "x"

    def test_clock(self):
        at = lambda h, m: dt.datetime(2026, 1, 1, h, m)  # noqa: E731
        self.assertEqual(names_for("en").clock(at(6, 29)), "6:29 AM")
        self.assertEqual(names_for("hi").clock(at(6, 29)), "सुबह 6:29")
        self.assertEqual(names_for("hi").clock(at(17, 0)), "शाम 5:00")
        self.assertEqual(names_for("ta").clock(at(6, 14)), "காலை 6:14")
        self.assertEqual(names_for("te").clock(at(13, 5)), "మధ్యాహ్నం 1:05")
        self.assertEqual(names_for("bn").clock(at(17, 0)), "বিকেল 5:00")
        self.assertEqual(names_for("bn").clock(at(19, 0)), "সন্ধ্যা 7:00")
        self.assertEqual(names_for("ml").clock(at(23, 30)), "രാത്രി 11:30")

    def test_tithi_label(self):
        self.assertEqual(names_for("ta").tithi_label("Krishna", "Ashtami"), "தேய்பிறை அஷ்டமி")
        self.assertEqual(names_for("te").tithi_label("Shukla", "Pratipada"), "శుద్ధ పాడ్యమి")
        self.assertEqual(names_for("hi").tithi_label("Krishna", "Ashtami"), "कृष्ण अष्टमी")

    def test_module_names_mirror_names_hi(self):
        import importlib
        public_hi = {k[:-3] for k in vars(names_hi) if k.endswith("_HI")}
        for code in REGIONAL_LANGS:
            mod = importlib.import_module(f"app.astro.names_{code}")
            suffix = code.upper()
            with self.subTest(lang=code):
                for base in public_hi:
                    self.assertTrue(hasattr(mod, f"{base}_{suffix}"), f"{base}_{suffix}")
                self.assertTrue(callable(getattr(mod, f"add_{code}")))


class TestNewLanguageFallback(unittest.TestCase):
    """DIVASTRO-143: pa ne as mr gu start as English with holes filled in key by key."""

    def test_an_unfilled_new_language_is_english_never_a_keyerror(self):
        en = names_for("en")
        for code in lang_data.NEW_CODES:
            if code in lang_data.ready("app"):
                continue
            n = names_for(code)
            with self.subTest(lang=code):
                self.assertEqual(n.code, code)
                self.assertEqual(n.TITHI, en.TITHI)
                self.assertEqual(n.MONTHS, en.MONTHS)
                self.assertEqual(n.TIMINGS["rahu_kaal"], "Rahu Kaal")
                self.assertEqual(n.clock_word(7), en.CLOCK["morning"])

    def test_a_filled_value_wins_and_a_hole_stays_english(self):
        from app.astro import names_i18n
        mod = type("M", (), {})()
        for name in TABLES + TEXTS:
            setattr(mod, f"{name}_ZZ", {} if name not in ("MONTHS",) else ["", "फ़रवरी"])
        mod.TITHI_ZZ = {"Ashtami": "अष्टमी", "Navami": ""}
        mod.NOTE_POLAR_ZZ = ""
        values = {name: getattr(mod, f"{name}_ZZ") for name in TABLES + TEXTS}
        got = names_i18n._over_english(values)
        en = names_for("en")
        self.assertEqual(got["TITHI"]["Ashtami"], "अष्टमी")
        self.assertEqual(got["TITHI"]["Navami"], "Navami")
        self.assertEqual(got["MONTHS"][1], "फ़रवरी")
        self.assertEqual(got["MONTHS"][0], en.MONTHS[0])
        self.assertEqual(len(got["MONTHS"]), 12)
        self.assertEqual(got["NOTE_POLAR"], en.NOTE_POLAR)

    def test_the_script_block_table_matches_the_registry_of_blocks(self):
        for code, rng in SCRIPT.items():
            self.assertEqual(((rng[0], rng[1]),), lang_data.BLOCKS[code], code)


class TestAddNames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.day = daily_panchang("2026-10-07", *DELHI)          # a Wednesday
        cls.polar = daily_panchang("2026-06-21", 78.2232, 15.6267, "Arctic/Longyearbyen")

    def test_hindi_is_add_hindi(self):
        for p in (self.day, self.polar):
            self.assertEqual(add_names(copy.deepcopy(p), "hi"),
                             names_hi.add_hindi(copy.deepcopy(p)))

    def test_english_and_unknown_are_no_ops(self):
        for code in ("en", "fr"):
            self.assertEqual(add_names(copy.deepcopy(self.day), code), self.day)

    def test_regional_fields(self):
        for code in REGIONAL_LANGS:
            n = names_for(code)
            p = add_names(copy.deepcopy(self.day), code)
            with self.subTest(lang=code):
                for row in p["tithi"]:
                    self.assertEqual(row[f"name_{code}"], n.TITHI[row["name"]])
                    self.assertEqual(row[f"label_{code}"],
                                     n.tithi_label(row["paksha"], row["name"]))
                for key, table in (("nakshatra", n.NAKSHATRAS), ("yoga", n.YOGA),
                                   ("karana", n.KARANA)):
                    for row in p[key]:
                        self.assertEqual(row[f"name_{code}"], table[row["name"]])
                self.assertEqual(p["vara"][f"name_{code}"], n.VARA["Wednesday"])
                self.assertEqual(p[f"notes_{code}"], [n.NOTE_WEDNESDAY])
                # additive: the English fields are untouched
                self.assertEqual([r["name"] for r in p["tithi"]],
                                 [r["name"] for r in self.day["tithi"]])
                polar = add_names(copy.deepcopy(self.polar), code)
                self.assertEqual(polar[f"notes_{code}"], [n.NOTE_POLAR])

    def test_per_language_helpers(self):
        import importlib
        for code in REGIONAL_LANGS:
            helper = getattr(importlib.import_module(f"app.astro.names_{code}"), f"add_{code}")
            self.assertEqual(helper(copy.deepcopy(self.day)),
                             add_names(copy.deepcopy(self.day), code))


if __name__ == "__main__":
    unittest.main(verbosity=2)
