"""DIVASTRO-171: the kundali (chart) PDF in all thirteen site languages.

A paying user wrote that "Download Kundali" offered English and Hindi only. Since
DIVASTRO-124 it also printed kn te ta ml bn or; this adds pa ne as mr gu (labels
in app/lang_data/<code>.py, PDF_LABELS / PDF_VOCAB). For every language whose
script font is on this machine (gated per font, as HAS_DEVA gates Hindi — a bare
CI runner has none of them) the PDF is built with NO model and NO network, and:

  * the headings, row labels and table headers handed to Typst are the
    language's own (pdf_i18n), never the English edition's
  * the PDF's text is in the language's script: every Indic letter Typst wrote
    is in that script's Unicode block, and there are plenty of them
  * none of the English section headings is printed
  * the script's font is embedded (Noto Serif Gurmukhi / Gujarati / Bengali for
    pa / gu / as; the Hindi Devanagari face for mr / ne)
  * pdf_report.pdf_languages() lists every language whose font exists — all
    thirteen on a machine with fonts-noto-core (the production image)
  * the template is forced left-to-right (Typst counts "pa" as RTL)

    ~/.venvs/divineastro/bin/python -u -m tests.test_pdf_languages
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import socket
import sys
import unicodedata
import unittest
import zlib
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("ASTRO_SECRET_KEY", "ci")

from app import chart_service, lang_data, llm, pdf_i18n, pdf_report  # noqa: E402
from app.chart_service import BirthData, build  # noqa: E402
from tests.pdf_text import pages_text  # noqa: E402

WHEN = dt.datetime(2026, 10, 9, 12, 0)
ALL = ("en", "hi", "kn", "te", "ta", "ml", "bn", "or", "pa", "ne", "as", "mr", "gu")
NEW = ("pa", "ne", "as", "mr", "gu")
DEVANAGARI = ((0x0900, 0x097F),)
BLOCKS = {**lang_data.BLOCKS, "hi": DEVANAGARI}
# The embedded face a language's text must come out in (a prefix of the PDF BaseFont name).
EMBED = {"pa": b"NotoSerifGurmukhi", "gu": b"NotoSerifGujarati", "as": b"NotoSerifBengali",
         "bn": b"NotoSerifBengali", "kn": b"NotoSerifKannada", "te": b"NotoSerifTelugu",
         "ta": b"NotoSerifTamil", "ml": b"NotoSerifMalayalam", "or": b"NotoSansOriya"}
EN_HEADINGS = [pdf_report._LOCALIZED_TEXTS["en"][k] for k in pdf_i18n.TEXT_KEYS]


def has_font(code: str) -> bool:
    if code == "en":
        return True
    if code == "hi":
        return pdf_report.devanagari_font() is not None
    return pdf_report.script_font(code) is not None


AVAILABLE = tuple(c for c in ALL if has_font(c))


def _birth() -> BirthData:
    return BirthData(name="Test Native", date="1990-01-01", time="12:00",
                     latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata",
                     place="New Delhi, India", zodiac="sidereal", ayanamsa="lahiri",
                     house_system="Whole Sign")


def _fonts(pdf: bytes) -> set[bytes]:
    names = set(re.findall(rb"/BaseFont\s*/[A-Z]{6}\+([A-Za-z0-9-]+)", pdf))
    for raw in re.findall(rb"stream\r?\n(.*?)endstream", pdf, re.S):
        try:
            names |= set(re.findall(rb"/BaseFont\s*/[A-Z]{6}\+([A-Za-z0-9-]+)", zlib.decompress(raw)))
        except Exception:
            pass
    return names


def _indic_letters(text: str) -> list[str]:
    return [c for c in text if 0x0900 <= ord(c) <= 0x0DFF and unicodedata.category(c)[0] in "LM"]


def _in_block(c: str, code: str) -> bool:
    return any(lo <= ord(c) <= hi for lo, hi in BLOCKS[code])


class Built:
    def __init__(self, session, code: str):
        real = pdf_report._compile
        self.data = None

        def spy(body, data, files=None):
            self.data = json.loads(json.dumps(data, ensure_ascii=False))
            return real(body, data, files)

        with mock.patch.object(pdf_report, "_compile", spy):
            self.pdf = pdf_report.chart_pdf(session, brand="Divine Astro", site="divineastro.org",
                                            when=WHEN, language=code)
        self.text = " ".join(pages_text(self.pdf))


@unittest.skipIf(chart_service.ChartBuilder is None, "stellium ephemeris engine not available")
class KundaliPdfLanguages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = build(_birth())
        cls._patches = [mock.patch.object(llm, "default_provider", lambda: "off")]

        def no_net(*a, **k):
            raise OSError("network is disabled in this test")
        cls._patches += [mock.patch.object(socket, "create_connection", no_net),
                         mock.patch.object(socket.socket, "connect", no_net)]
        for p in cls._patches:
            p.start()
        cls.built: dict[str, Built] = {}
        skipped = [c for c in ALL if c not in AVAILABLE]
        if skipped:
            print(f"  (no script font on this machine for {' '.join(skipped)}: those are skipped)")

    @classmethod
    def tearDownClass(cls):
        for p in cls._patches:
            p.stop()

    def get(self, code: str) -> Built:
        if code not in self.built:
            self.built[code] = Built(self.session, code)
        return self.built[code]

    # ------------------------------------------------------------ registry
    def test_the_five_new_languages_have_complete_tables(self):
        for code in NEW:
            with self.subTest(code=code):
                self.assertIn(code, pdf_i18n.REGIONAL, "not READY 'pdf' or a table is incomplete")
                self.assertIn("pdf", lang_data.load(code).READY)
                for key, en in pdf_i18n.ENGLISH.items():
                    value = pdf_i18n.label(code, key)
                    if isinstance(en, list):
                        self.assertIsInstance(value, list, key)
                        self.assertEqual(len(value), len(en), key)
                    else:
                        self.assertIsInstance(value, str, key)
                self.assertEqual(set(pdf_i18n.VOCAB[code]), set(pdf_i18n.VOCAB["kn"]))

    def test_pdf_languages_lists_every_language_with_a_font(self):
        langs = pdf_report.pdf_languages()
        self.assertEqual(langs, [c for c in ALL if c in AVAILABLE and (c in ("en", "hi") or c in pdf_i18n.REGIONAL)])
        if len(AVAILABLE) == len(ALL):
            self.assertEqual(langs, list(ALL), "all thirteen fonts are here, so all thirteen are offered")
        from app.main import _pdf_lang
        for code in NEW:
            self.assertEqual(_pdf_lang(code), code if code in AVAILABLE else "en")

    def test_marathi_and_nepali_use_the_hindi_devanagari_face(self):
        for code in ("mr", "ne"):
            self.assertEqual(pdf_report.script_font(code), pdf_report.devanagari_font())

    def test_template_is_left_to_right(self):
        # Typst infers the direction from `lang` and treats "pa" as RTL; the
        # whole Punjabi report came out mirrored before `dir: ltr`.
        self.assertIn("dir: ltr", pdf_report._template(""))

    def test_engine_words_translate(self):
        for code in NEW:
            with self.subTest(code=code):
                self.assertEqual(pdf_i18n.translate("triplicity_ruler", code),
                                 pdf_i18n.VOCAB[code]["triplicity"])
                self.assertTrue(pdf_i18n.translate("Mars R", code).startswith(
                    pdf_i18n._proper(code)["Mars"]))
                self.assertNotIn("Leo", pdf_i18n.translate("12°04' Leo", code))

    # ------------------------------------------------------------ PDFs
    def test_every_language_builds(self):
        for code in AVAILABLE:
            with self.subTest(code=code):
                out = self.get(code)
                self.assertTrue(out.pdf.startswith(b"%PDF-"))
                self.assertEqual(out.data["lang"], code)

    def test_labels_handed_to_typst_are_the_languages_own(self):
        for code in AVAILABLE:
            if code in ("en", "hi"):
                continue
            with self.subTest(code=code):
                d = self.get(code).data
                self.assertEqual(d["texts"], pdf_i18n.texts(code))
                self.assertEqual(d["title"], pdf_i18n.label(code, "title"))
                for table, key in (("positions", "positions_headers"), ("houses", "houses_headers"),
                                   ("aspects", "aspects_headers"), ("vargas", "vargas_headers"),
                                   ("yogas", "yogas_headers")):
                    self.assertEqual(d[table]["headers"], list(pdf_i18n.label(code, key)), table)
                self.assertEqual(d["dasha"]["table"]["headers"], list(pdf_i18n.label(code, "dasha_headers")))
                self.assertEqual(d["dasha"]["antardasha"]["headers"],
                                 list(pdf_i18n.label(code, "antardasha_headers")))
                labels = [r[0] for r in d["birth"]] + [r[0] for r in d["cover"]] + \
                         [r[0] for r in d["dasha"]["summary"]]
                for text in [*d["texts"].values(), *labels]:
                    letters = [c for c in text if unicodedata.category(c)[0] in "LM"]
                    native = [c for c in letters if _in_block(c, code)]
                    # "(D1)", "(UT)": a few Latin letters in brackets, the rest the script
                    self.assertGreater(len(native), len(letters) // 2, text)

    def test_cells_are_translated(self):
        for code in AVAILABLE:
            if code in ("en", "hi"):
                continue
            with self.subTest(code=code):
                d = self.get(code).data
                for table in ("positions", "houses", "vargas"):
                    for row in d[table]["rows"]:
                        for cell in row:
                            self.assertIsNone(re.search(r"[A-Za-z]{4,}", re.sub(r"\(.*?\)", "", cell)),
                                              f"{table}: {cell!r} left in English")
                for row in d["birth"]:
                    self.assertNotIn("triplicity", row[1])

    def test_pdf_text_is_in_the_languages_script(self):
        for code in AVAILABLE:
            with self.subTest(code=code):
                text = self.get(code).text
                letters = _indic_letters(text)
                if code == "en":
                    self.assertEqual(letters, [], "Indic letters in the English PDF")
                    continue
                stray = sorted({c for c in letters if not _in_block(c, code)})
                self.assertEqual(stray, [], f"letters of another script: {''.join(stray)}")
                self.assertGreater(len(letters), 1500, "too little text in the script")

    def test_no_english_heading_is_printed(self):
        for code in AVAILABLE:
            with self.subTest(code=code):
                text = re.sub(r"\s+", " ", self.get(code).text)
                if code == "en":
                    self.assertIn("Planetary Positions", text)
                    continue
                left = [h for h in EN_HEADINGS if h in text]
                self.assertEqual(left, [], "English headings in the PDF")
                for word in ("triplicity_ruler", "Sidereal ·", "House Placements", "Yogini Dasha"):
                    self.assertNotIn(word, text)

    def test_the_scripts_font_is_embedded(self):
        for code in AVAILABLE:
            if code in ("en",):
                continue
            with self.subTest(code=code):
                fonts = _fonts(self.get(code).pdf)
                if code in ("hi", "mr", "ne"):
                    want = re.sub(rb"[^A-Za-z]", b"", pdf_report.devanagari_font().encode())
                    self.assertTrue(any(f.replace(b"-", b"").startswith(want) for f in fonts), str(fonts))
                else:
                    self.assertTrue(any(f.startswith(EMBED[code]) for f in fonts), str(fonts))


if __name__ == "__main__":
    unittest.main(verbosity=2)
