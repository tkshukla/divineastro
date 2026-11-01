"""DIVASTRO-168: a report for a chart cast without a name never prints "Native".

The birth form's name is optional and a blank one becomes the server's
placeholder "Native" (chart_service). Every PDF the site produces — the chart
report, Remedies, the three single-question reports, the Life Book and the
Kundali Milan report — is built here with a blank name, in English and Hindi,
with no model and no network, and checked for:

  * no "Native" / "नेटिव" in the text handed to the typesetter, in the text on
    the pages, or in the PDF's metadata
  * no "Name" / "नाम" row in the birth details
  * the neutral "Your kundali" / "आपकी कुंडली" on the cover instead
  * a real name still printed exactly as before

plus the model path (the prompts say "the person", and a stray "Native" in a
model's text is taken out) and the download file names.

    ASTRO_SECRET_KEY=ci ~/.venvs/divineastro/bin/python -u -m tests.test_anonymous_reports
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

from app import chart_service, llm, milan_report, pdf_report, person_name  # noqa: E402
from app.chart_service import BirthData, build  # noqa: E402
from tests import pdf_text  # noqa: E402

WHEN = dt.datetime(2026, 10, 9, 12, 0)
HAS_DEVA = pdf_report.devanagari_font() is not None
LANGS = ("en", "hi") if HAS_DEVA else ("en",)
NATIVE = re.compile(r"Native|नेटिव")
NAME_LABELS = ("Name", "नाम")
REAL = "Asha Verma"


def _birth(name: str) -> BirthData:
    return BirthData(
        name=name, date="1990-01-01", time="12:00",
        latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata",
        place="New Delhi, India", zodiac="sidereal", ayanamsa="lahiri", house_system="Whole Sign")


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, (list, tuple)):
        for v in node:
            yield from _strings(v)


def _capture(fn, *args, **kwargs):
    """(data handed to Typst, the PDF bytes)."""
    real, seen = pdf_report._compile, {}

    def spy(body, data, files=None):
        seen["data"] = json.loads(json.dumps(data, ensure_ascii=False))
        return real(body, data, files)

    with mock.patch.object(pdf_report, "_compile", spy):
        pdf = fn(*args, **kwargs)
    return seen["data"], pdf


def _metadata(pdf: bytes) -> str:
    """The Info dictionary and XMP packet, as text (Typst writes both uncompressed)."""
    out = []
    for m in re.finditer(rb"<x:xmpmeta.*?</x:xmpmeta>", pdf, re.S):
        out.append(m.group(0).decode("utf-8", "replace"))
    for m in re.finditer(rb"/(?:Title|Author|Subject|Keywords|Creator)\s*(\(.*?\)|<[0-9A-Fa-f]+>)", pdf):
        v = m.group(1)
        if v.startswith(b"<"):
            raw = bytes.fromhex(v[1:-1].decode())
            out.append(raw.decode("utf-16-be" if raw[:2] == b"\xfe\xff" else "latin-1", "replace"))
        else:
            out.append(v.decode("latin-1", "replace"))
    return "\n".join(out)


@unittest.skipIf(chart_service.ChartBuilder is None, "stellium ephemeris engine not available")
class AnonymousReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blank = build(_birth(""))
        cls.named = build(_birth(REAL))
        cls._patches = [mock.patch.object(llm, "default_provider", lambda: "off")]

        def no_net(*a, **k):
            raise OSError("network is disabled in this test")
        cls._patches += [mock.patch.object(socket, "create_connection", no_net),
                         mock.patch.object(socket.socket, "connect", no_net)]
        for p in cls._patches:
            p.start()

    @classmethod
    def tearDownClass(cls):
        for p in cls._patches:
            p.stop()

    # Each builder, in each language it is offered in.
    def builders(self, session):
        for lang in LANGS:
            yield f"chart/{lang}", lambda lang=lang: pdf_report.chart_pdf(
                session, brand="Divine Astro", site="divineastro.org", when=WHEN, language=lang)
            yield f"life_book/{lang}", lambda lang=lang: pdf_report.life_book_pdf(
                session, language=lang, when=WHEN)
            for topic in ("sq_career", "sq_marriage_timing", "sq_wealth_business"):
                yield f"{topic}/{lang}", lambda lang=lang, topic=topic: pdf_report.single_question_pdf(
                    session, topic, language=lang, when=WHEN)
        # The chart report also prints in the regional languages whose font is installed.
        for code in pdf_report.pdf_languages():
            if code in pdf_report.pdf_i18n.REGIONAL:
                yield f"chart/{code}", lambda code=code: pdf_report.chart_pdf(
                    session, brand="Divine Astro", site="divineastro.org", when=WHEN, language=code)
        yield "remedies/en", lambda: pdf_report.remedies_pdf(
            session, brand="Divine Astro", site="divineastro.org", language="en")

    def test_the_server_still_casts_an_unnamed_chart_as_native(self):
        # The placeholder is unchanged (the engine relies on it); only what is printed changes.
        self.assertEqual(self.blank.bundle["meta"]["name"], "Native")

    def test_no_report_prints_native_or_a_name_row_for_an_unnamed_chart(self):
        for label, fn in self.builders(self.blank):
            with self.subTest(report=label):
                data, pdf = _capture(fn)
                handed = "\n".join(_strings(data))
                self.assertIsNone(NATIVE.search(handed), label)
                for row in data.get("birth", []) + data.get("cover", []):
                    self.assertNotIn(row[0], NAME_LABELS, row)
                self.assertEqual(data["subject"], person_name.YOUR_KUNDALI[label.split("/")[1]])
                pages = "\n".join(pdf_text.pages_text(pdf))
                self.assertIsNone(NATIVE.search(pages), label)
                self.assertNotRegex(pages, r"(?m)^\s*(Name|नाम)\s*$")
                meta = _metadata(pdf)
                self.assertIsNone(NATIVE.search(meta), meta)
                self.assertIsNone(NATIVE.search(pdf.decode("latin-1")), "raw PDF bytes")

    def test_a_real_name_is_still_printed(self):
        for label, fn in self.builders(self.named):
            with self.subTest(report=label):
                data, pdf = _capture(fn)
                self.assertEqual(data["subject"], REAL)
                if not label.startswith("life_book"):     # the Life Book never had a name row
                    self.assertIn(REAL, [row[1] for row in data["birth"]])
                self.assertIn(REAL, "\n".join(pdf_text.pages_text(pdf)))

    def test_milan_with_both_names_left_out(self):
        pair = milan_report.clean_pair({
            "groom": dict(name="", date="1990-08-15", time="10:30", time_known=True, place="New Delhi",
                          latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata"),
            "bride": dict(name="", date="1993-02-11", time="07:45", time_known=True, place="Pune",
                          latitude=18.52, longitude=73.86, timezone="Asia/Kolkata"),
        })
        for lang in LANGS:
            with self.subTest(lang=lang):
                data, pdf = _capture(milan_report.milan_report_pdf, pair, language=lang)
                text = "\n".join(_strings(data)) + "\n".join(pdf_text.pages_text(pdf)) + _metadata(pdf)
                self.assertIsNone(NATIVE.search(text))
                self.assertNotIn("—  &", text)
        self.assertEqual(pdf_report.safe_filename("Divine-Astro", "kundali-milan", "", ""),
                         "Divine-Astro-kundali-milan.pdf")

    def test_download_file_names(self):
        # main.py's pdf routes: safe_filename(BRAND, kind, display_name(birth.name) or kind)
        for raw in ("", "  ", "Native", "native", "नेटिव"):
            self.assertIsNone(person_name.display_name(raw), raw)
            self.assertEqual(
                pdf_report.safe_filename("Divine Astro", "chart", person_name.display_name(raw) or "chart"),
                "Divine-Astro-chart-chart.pdf")
        self.assertEqual(
            pdf_report.safe_filename("Divine Astro", "chart", person_name.display_name(REAL) or "chart"),
            "Divine-Astro-chart-Asha-Verma.pdf")
        self.assertEqual(person_name.display_name({"name": "  Asha   Verma "}), REAL)


class _FakeClient:
    """anthropic.Anthropic() stand-in: records the prompt, answers with `reply`."""
    prompts: list[str] = []
    reply = ""

    def __init__(self, *a, **k):
        self.messages = self

    def create(self, **kw):
        _FakeClient.prompts.append(kw["messages"][0]["content"])
        block = mock.Mock(text=_FakeClient.reply)
        return mock.Mock(content=[block], stop_reason="end_turn")


class ModelText(unittest.TestCase):
    def _run(self, fn, name: str, reply: dict, language: str = "en"):
        _FakeClient.prompts, _FakeClient.reply = [], json.dumps(reply, ensure_ascii=False)
        analysis = {"meta": {"name": name, "local_time": "01 January 1990, 12:00",
                             "place": "New Delhi"}, "lagna": "Aries", "moon_sign": "Leo"}
        with mock.patch.object(llm, "default_provider", lambda: "anthropic"), \
                mock.patch.object(llm, "_chart_facts", lambda a: "FACTS"), \
                mock.patch("anthropic.Anthropic", _FakeClient):
            out = fn(analysis, language=language)
        return _FakeClient.prompts[0], out

    def test_prompts_say_the_person_for_a_blank_name(self):
        for fn in (llm.generate_kundali_narratives, llm.generate_kundali_interpretations):
            with self.subTest(fn=fn.__name__):
                prompt, _ = self._run(fn, "Native", {})
                self.assertNotIn("named Native", prompt)
                self.assertIn("for the person born on", prompt)
                self.assertIn("did not give a name", prompt)
                prompt, _ = self._run(fn, REAL, {})
                self.assertIn(f"a native named {REAL}", prompt)
                self.assertNotIn("did not give a name", prompt)

    def test_a_stray_native_in_model_text_is_taken_out(self):
        reply = {"houses_detailed": "Native's Lagna is strong. Dear Native, the Native will rise.",
                 "planets_detailed": "Mars gives Native courage; the native is bold.",
                 "yogas_remedies_detailed": "A native named Native should chant daily."}
        _, out = self._run(llm.generate_kundali_interpretations, "Native", reply)
        text = " ".join(out[k] for k in reply)
        self.assertNotIn("Native", text, text)
        self.assertEqual(out["houses_detailed"],
                         "The native's Lagna is strong. Dear reader, the native will rise.")
        self.assertEqual(out["planets_detailed"], "Mars gives the native courage; the native is bold.")
        self.assertEqual(out["yogas_remedies_detailed"], "A native should chant daily.")
        # The month-by-month forecast, too, and in Hindi.
        months = [{"month": "m", "prediction": "नेटिव के लिए शुभ। Native को लाभ।"}] * 12
        _, out = self._run(llm.generate_kundali_narratives, "Native",
                           {"varshphal": months, "key_periods": "Native", "house_summary": "x"}, "hi")
        self.assertEqual(out["varshphal"][0][1], "जातक के लिए शुभ। जातक को लाभ।")
        self.assertNotIn("Native", out["key_periods"])

    def test_a_named_chart_is_left_exactly_as_written(self):
        reply = {"houses_detailed": "Native American art; Native's view.", "planets_detailed": "p",
                 "yogas_remedies_detailed": "r"}
        _, out = self._run(llm.generate_kundali_interpretations, REAL, reply)
        self.assertEqual(out["houses_detailed"], reply["houses_detailed"])

    def test_scrub_keeps_ordinary_words(self):
        s = person_name.scrub_placeholder
        self.assertEqual(s("the native is calm. Native American"), "the native is calm. Native American")
        self.assertEqual(s("* Native gains wealth"), "* The native gains wealth")
        self.assertEqual(s("Nativity and natives"), "Nativity and natives")


if __name__ == "__main__":
    unittest.main(verbosity=2)
