"""The paid PDFs: Life Book and the three single-topic reports (DIVASTRO-150).

Before this, life_book_pdf imported a module that does not exist (so its chart
drawings were silently dropped) and crashed in the 12-month section whenever no
narration model answered; single_question_pdf printed houses 1-5 for every
topic and had no chart drawings. These tests build every report in English and
Hindi with NO model and NO network, and check what a customer would see:

  * a valid PDF with at least the page count measured when this was written
    (Life Book 8, each report 5, cover included)
  * the chart drawings are embedded (Typst writes each SVG as a form XObject)
  * the text handed to the typesetter has no 'None' / 'nan' / 'Traceback' /
    placeholder, and every section is either present or listed under
    "About this edition" / "About this report" — none disappears silently
  * the topic reports show their own houses (career: 10th first), not 1-5
  * a model's text is used when one answers, the engine's own text when not
  * Hindi falls back to English, with a note, when the machine has no
    Devanagari font

    ~/.venvs/divineastro/bin/python -u -m tests.test_report_pdfs
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import socket
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("ASTRO_SECRET_KEY", "ci")

from app import chart_service, llm, pdf_report, report_text  # noqa: E402
from app.chart_service import BirthData, build  # noqa: E402

WHEN = dt.datetime(2026, 10, 9, 12, 0)     # fixed, so the dasha windows below do not drift with the calendar
MIN_PAGES = {"life_book": 8, "sq_career": 5, "sq_marriage_timing": 5, "sq_wealth_business": 5}
BAD_WORDS = re.compile(r"\bNone\b|\bnan\b|Traceback|TypeError|KeyError|\bundefined\b|TODO|lorem", re.I)


def _birth(zodiac: str = "sidereal") -> BirthData:
    return BirthData(
        name="Test Native", date="1990-01-01", time="12:00",
        latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata",
        place="New Delhi, India", zodiac=zodiac, ayanamsa="lahiri", house_system="Whole Sign")


def _strings(node):
    """Every string in the data handed to Typst."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, (list, tuple)):
        for v in node:
            yield from _strings(v)


class Captured:
    """Runs a builder, keeping the data and files given to Typst and the PDF."""

    def __init__(self, fn, *args, **kwargs):
        real = pdf_report._compile
        self.data = self.files = None

        def spy(body, data, files=None):
            self.data, self.files = json.loads(json.dumps(data, ensure_ascii=False)), dict(files or {})
            return real(body, data, files)

        with mock.patch.object(pdf_report, "_compile", spy):
            self.pdf = fn(*args, **kwargs)
        self.pages = int(re.findall(rb"/Count\s+(\d+)", self.pdf)[0])
        self.forms = len(re.findall(rb"/Subtype\s*/Form", self.pdf))


def _build(label: str, session, lang: str) -> Captured:
    if label == "life_book":
        return Captured(pdf_report.life_book_pdf, session, language=lang, when=WHEN)
    return Captured(pdf_report.single_question_pdf, session, label, language=lang, when=WHEN)


@unittest.skipIf(chart_service.ChartBuilder is None, "stellium ephemeris engine not available")
class ReportPdfs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = build(_birth())
        cls._provider = mock.patch.object(llm, "default_provider", lambda: "off")
        cls._provider.start()
        # No network of any kind: a builder that needs it fails here, not in production.
        def no_net(*a, **k):
            raise OSError("network is disabled in this test")
        cls._net = [mock.patch.object(socket, "create_connection", no_net),
                    mock.patch.object(socket.socket, "connect", no_net)]
        for p in cls._net:
            p.start()
        cls.built = {}

    @classmethod
    def tearDownClass(cls):
        for p in cls._net:
            p.stop()
        cls._provider.stop()

    def get(self, label: str, lang: str) -> Captured:
        key = (label, lang)
        if key not in self.built:
            self.built[key] = _build(label, self.session, lang)
        return self.built[key]

    def test_every_report_builds_in_english_and_hindi_without_a_model(self):
        for label, minimum in MIN_PAGES.items():
            for lang in ("en", "hi"):
                with self.subTest(report=label, lang=lang):
                    out = self.get(label, lang)
                    self.assertTrue(out.pdf.startswith(b"%PDF-"), "not a PDF")
                    self.assertTrue(out.pdf.rstrip().endswith(b"%%EOF"))
                    self.assertGreaterEqual(out.pages, minimum, f"{label} {lang}: {out.pages} pages")
                    self.assertLessEqual(out.pages, 30, "suspiciously long: a layout loop?")

    def test_chart_drawings_are_embedded(self):
        for label in MIN_PAGES:
            for lang in ("en", "hi"):
                with self.subTest(report=label, lang=lang):
                    out = self.get(label, lang)
                    for key in ("d1_north", "d1_south", "d9_north", "d9_south"):
                        name = out.data[key]
                        self.assertEqual(name, f"{key}.svg", f"{key} is missing from the data")
                        svg = out.files[name]
                        self.assertIn("<svg", svg)
                        self.assertGreater(len(svg), 2000, f"{key} looks empty")
                    self.assertGreaterEqual(out.forms, 1, "no SVG form XObject in the PDF")

    def test_no_error_or_placeholder_text(self):
        for label in MIN_PAGES:
            for lang in ("en", "hi"):
                with self.subTest(report=label, lang=lang):
                    for text in _strings(self.get(label, lang).data):
                        self.assertIsNone(BAD_WORDS.search(text), text[:160])

    def test_life_book_sections_are_present_without_a_model(self):
        for lang in ("en", "hi"):
            with self.subTest(lang=lang):
                d = self.get("life_book", lang).data
                self.assertTrue(d["houses_detailed"], "house readings vanished")
                self.assertTrue(d["planets_detailed"], "planet readings vanished")
                self.assertTrue(d["remedies_detailed"], "yogas and remedies vanished")
                self.assertEqual(len(d["varshphal"]), 2, "next-12-months sub-periods missing")
                self.assertIsNotNone(d["dasha"])
                self.assertTrue(d["ashtakavarga"]["rows"])
                self.assertEqual(d["omitted"], [], "nothing should be omitted for a sidereal chart")
                text = " ".join(_strings(d["houses_detailed"]))
                self.assertIn("Jupiter" if lang == "en" else "बृहस्पति", text)
                note = " ".join(_strings(d["houses_detailed"]))
                self.assertTrue("rule engine" in note or "नियम-आधारित" in note,
                                "the page must say the text is the engine's, not a model's")

    def test_life_book_builds_with_no_network_and_no_llm(self):
        # setUpClass already blocks sockets and forces provider "off"; building at
        # all (above) proves it. Assert the engine path was the one taken.
        with mock.patch("anthropic.Anthropic", side_effect=AssertionError("a model was called")):
            out = _build("life_book", self.session, "en")
        self.assertGreaterEqual(out.pages, MIN_PAGES["life_book"])
        self.assertIn("rule engine", " ".join(_strings(out.data["houses_detailed"])))

    def test_topic_reports_show_their_own_houses(self):
        first = {"sq_career": "10", "sq_marriage_timing": "7", "sq_wealth_business": "2"}
        for sku, house in first.items():
            with self.subTest(sku=sku):
                rows = self.get(sku, "en").data["houses"]["rows"]
                self.assertEqual(rows[0][0], house)
                self.assertEqual(len(rows), 5)
        career = {r[0] for r in self.get("sq_career", "en").data["houses"]["rows"]}
        self.assertEqual(career, {"10", "6", "11", "2", "1"})

    def test_topic_report_marks_the_periods_that_switch_the_topic_on(self):
        text = " ".join(_strings(self.get("sq_marriage_timing", "en").data["windows"]))
        self.assertIn("activates this topic", text)
        self.assertRegex(text, r"lord of the (seventh|fourth|second|eleventh|eighth) house")

    def test_a_model_answer_is_used_when_there_is_one(self):
        model_i = {"houses_detailed": "* MODEL-HOUSES", "planets_detailed": "* MODEL-PLANETS",
                   "yogas_remedies_detailed": "* MODEL-REMEDIES", "written_in": "en", "source": "model"}
        model_n = {"varshphal": [["Jan to Feb", "MODEL-MONTH"]] * 12, "key_periods": "MODEL-KEY",
                   "house_summary": "MODEL-SUMMARY", "written_in": "en", "source": "model"}
        with mock.patch.object(llm, "generate_kundali_interpretations", lambda *a, **k: model_i), \
                mock.patch.object(llm, "generate_kundali_narratives", lambda *a, **k: model_n):
            out = _build("life_book", self.session, "en")
        flat = " ".join(_strings(out.data))
        for marker in ("MODEL-HOUSES", "MODEL-PLANETS", "MODEL-REMEDIES", "MODEL-MONTH", "MODEL-KEY", "MODEL-SUMMARY"):
            self.assertIn(marker, flat)
        self.assertEqual(len(out.data["varshphal"]), 12)
        self.assertNotIn("rule engine", flat)

    def test_a_failed_model_call_falls_back_to_the_engine_text(self):
        with mock.patch.object(llm, "default_provider", lambda: "anthropic"), \
                mock.patch("anthropic.Anthropic", side_effect=RuntimeError("provider down")):
            out = _build("life_book", self.session, "en")
        flat = " ".join(_strings(out.data["houses_detailed"]))
        self.assertIn("rule engine", flat)
        self.assertEqual(len(out.data["varshphal"]), 2)

    def test_missing_pieces_are_listed_not_dropped(self):
        with mock.patch.object(pdf_report, "_vedic_svgs", lambda *a, **k: {}):
            out = _build("life_book", self.session, "en")
            sq = _build("sq_career", self.session, "en")
        self.assertEqual(out.data["d1_north"], "")
        self.assertEqual(out.forms, 0)
        listed = " ".join(_strings(out.data["omitted"]))
        self.assertIn("D1 North Indian", listed)
        self.assertIn("D9 South Indian", listed)
        self.assertIn("D1 North", " ".join(_strings(sq.data["about"])))
        self.assertGreaterEqual(out.pages, 6)

    def test_a_tropical_chart_says_why_the_dasha_is_missing(self):
        session = build(_birth("tropical"))
        out = Captured(pdf_report.life_book_pdf, session, language="en", when=WHEN)
        self.assertIsNone(out.data["dasha"])
        self.assertIn("tropical", " ".join(_strings(out.data["omitted"])))
        sq = Captured(pdf_report.single_question_pdf, session, "sq_career", language="en", when=WHEN)
        self.assertIn("sidereal", " ".join(_strings(sq.data["about"])))

    def test_hindi_without_a_devanagari_font_prints_english_and_says_so(self):
        with mock.patch.object(pdf_report, "devanagari_font", lambda: None):
            life = _build("life_book", self.session, "hi")
            sq = _build("sq_career", self.session, "hi")
        self.assertEqual(life.data["lang"], "en")
        self.assertEqual(sq.data["lang"], "en")
        self.assertIn("Hindi font", " ".join(_strings(life.data["omitted"])))
        self.assertIn("Hindi font", " ".join(_strings(sq.data["about"])))

    def test_hindi_reports_are_in_devanagari(self):
        for label in MIN_PAGES:
            with self.subTest(report=label):
                d = self.get(label, "hi").data
                self.assertEqual(d["lang"], "hi")
                flat = " ".join(_strings(d))
                self.assertGreater(len(re.findall(r"[ऀ-ॿ]", flat)), 400)

    def test_other_app_languages_get_english(self):
        # main._engine_lang sends anything but "hi" as "en"; the builder is robust to it too.
        out = Captured(pdf_report.single_question_pdf, self.session, "sq_career", language="kn", when=WHEN)
        self.assertEqual(out.data["lang"], "en")


class EngineText(unittest.TestCase):
    """report_text works on plain rows, so it needs no chart."""

    HOUSES = [[str(i), "Aries", "0", "Mars", "—"] for i in range(1, 13)]

    def test_topic_for(self):
        self.assertEqual(report_text.topic_for("sq_career"), "career")
        self.assertEqual(report_text.topic_for("sq_marriage_timing"), "marriage")
        self.assertEqual(report_text.topic_for("sq_wealth_business"), "wealth")
        self.assertEqual(report_text.topic_for(None), "career")

    def test_key_planets_name_the_reason(self):
        order, why = report_text.key_planets("career", self.HOUSES, False)
        self.assertEqual(order[0], "Mars")
        self.assertIn("lord of the tenth house", why["Mars"])
        self.assertIn("Saturn", order)
        self.assertIn("natural significator of your career", why["Saturn"])

    def test_house_reading_handles_an_empty_house_and_a_missing_lord(self):
        line = report_text.house_reading(3, self.HOUSES, {}, {}, False)
        self.assertIn("Third house", line)
        self.assertIn("No planet occupies it", line)
        self.assertEqual(report_text.house_reading(13, self.HOUSES, {}, {}, False), "")

    def test_nothing_in_the_hindi_text_is_left_in_english_letters_but_names(self):
        places = {"Mars": {"sign": "Aries", "house": 1, "retro": False}}
        line = report_text.house_reading(1, self.HOUSES, places, {}, True)
        self.assertRegex(line, r"[ऀ-ॿ]")
        self.assertNotIn("Aries", line)
        self.assertNotIn("Mars", line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
