"""Public sample reports (DIVASTRO-151): GET /samples/<sku>.pdf.

Each of the four reports (Career, Marriage, Wealth, Life Book) in English and Hindi,
built by the REAL builder on one fixed fictional chart with the model forced off and
`sample=True`. Checked here: valid PDF, as long as the paid report built the normal
way, the watermark and footer line on EVERY page (text pulled out of the PDF itself),
the chart drawings, no error words, a paid report with NO watermark, 404 for anything
that is not one of the four, caching and the build lock, the per-address rate limit,
and that the visit beacon does not treat the file as a page.

    ~/.venvs/divineastro/bin/python -u -m tests.test_sample_reports
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("ASTRO_SECRET_KEY", "ci")
_TMP = tempfile.mkdtemp(prefix="astro_samples_test_")
os.environ["ASTRO_SAMPLES_DIR"] = _TMP

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, chart_service, llm, pdf_report, sample_reports  # noqa: E402
from app.main import app  # noqa: E402
from tests import pdf_text  # noqa: E402
from tests.test_report_pdfs import BAD_WORDS, HAS_DEVA, MIN_PAGES, _strings  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
LANGS = ("en", "hi") if HAS_DEVA else ("en",)
FOOTER_EN = "Sample for illustration, cast for a fictional chart. Your report is cast from your own birth details."
DEVA = re.compile(r"[ऀ-ॿ]")


def _pages(pdf: bytes) -> int:
    return int(re.findall(rb"/Count\s+(\d+)", pdf)[0])


def _real(session, sku: str, lang: str) -> bytes:
    """The paid report, built the normal way (no sample mode), for the same chart."""
    token = llm.FORCE_OFF.set(True)
    try:
        if sku == "life_book":
            return pdf_report.life_book_pdf(session, language=lang)
        return pdf_report.single_question_pdf(session, sku, language=lang)
    finally:
        llm.FORCE_OFF.reset(token)


def _spy_compile():
    """Wraps pdf_report._compile, keeping the data handed to Typst."""
    seen = []
    real = pdf_report._compile

    def spy(body, data, files=None):
        seen.append((data, dict(files or {})))
        return real(body, data, files)
    return seen, mock.patch.object(pdf_report, "_compile", spy)


@unittest.skipIf(chart_service.ChartBuilder is None, "stellium ephemeris engine not available")
class SampleReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sample_reports._memory.clear()
        sample_reports._rate.clear()
        cls.session = chart_service.build(chart_service.BirthData(**sample_reports.DEMO_BIRTH))
        cls.pdfs = {}
        for sku in sample_reports.SKUS:
            for lang in LANGS:
                r = client.get(f"/samples/{sku}.pdf", params={"lang": lang})
                assert r.status_code == 200, (sku, lang, r.status_code, r.text[:200])
                cls.pdfs[(sku, lang)] = r.content
        cls.real = {}
        sample_reports._rate.clear()

    def setUp(self):
        sample_reports._rate.clear()

    def test_the_demo_chart_is_fictional_and_fixed(self):
        b = sample_reports.DEMO_BIRTH
        self.assertEqual((b["name"], b["date"], b["time"], b["place"]),
                         ("Sample Customer", "1990-08-15", "10:30", "New Delhi, India"))

    def test_every_sample_is_a_valid_pdf_as_long_as_the_paid_report(self):
        for (sku, lang), pdf in self.pdfs.items():
            with self.subTest(sku=sku, lang=lang):
                self.assertTrue(pdf.startswith(b"%PDF-"))
                self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))
                real = self.real.setdefault((sku, lang), _real(self.session, sku, lang))
                self.assertGreaterEqual(_pages(pdf), MIN_PAGES[sku])
                self.assertEqual(_pages(pdf), _pages(real), "a sample must be the full report, not an excerpt")

    def test_every_page_carries_the_watermark_and_the_footer(self):
        for (sku, lang), pdf in self.pdfs.items():
            pages = pdf_text.pages_text(pdf)
            self.assertEqual(len(pages), _pages(pdf))
            with self.subTest(sku=sku, lang=lang):
                if lang == "en":
                    for n, text in enumerate(pages, 1):
                        self.assertIn(FOOTER_EN, text, f"page {n} has no sample footer")
                        self.assertIn("SAMPLE", text, f"page {n} has no watermark")
                else:
                    # Typst writes shaped Devanagari as glyph clusters, so the Hindi footer does not
                    # extract as clean words. Its extraction is the same on every page, though: the
                    # tail of each page must equal the cover's, and be Devanagari.
                    tail = pages[0][-130:]
                    self.assertRegex(tail, DEVA)
                    for n, text in enumerate(pages, 1):
                        self.assertEqual(text[-130:], tail, f"page {n} has no sample footer and watermark")

    def test_the_hindi_footer_and_watermark_are_what_is_typeset(self):
        seen, patch = _spy_compile()
        with patch:
            sample_reports.build("sq_career", "hi")
        data = seen[0][0]
        if HAS_DEVA:
            self.assertEqual(data["sample"]["mark"], "नमूना")
            self.assertIn("काल्पनिक कुंडली", data["sample"]["footer"])
        else:
            self.assertEqual(data["sample"]["mark"], "SAMPLE")        # the builder fell back to English

    def test_a_paid_report_has_no_watermark_and_no_footer(self):
        for sku in sample_reports.SKUS:
            for lang in LANGS:
                with self.subTest(sku=sku, lang=lang):
                    seen, patch = _spy_compile()
                    with patch:
                        paid = _real(self.session, sku, lang)
                    self.assertIsNone(seen[0][0]["sample"], "a paid report must not carry sample data")
                    text = "\n".join(pdf_text.pages_text(paid))
                    self.assertNotIn("SAMPLE", text)
                    self.assertNotIn("fictional chart", text)
                    sample = self.pdfs[(sku, lang)]
                    if lang == "hi":
                        sample_tail = pdf_text.pages_text(sample)[0][-130:]
                        self.assertNotIn(sample_tail, text)

    def test_the_sample_is_the_real_builder_with_the_model_off(self):
        # Even with a model configured, the sample must not call one.
        seen, patch = _spy_compile()
        with patch, mock.patch.object(llm, "_anthropic_ready", lambda: True), \
                mock.patch("anthropic.Anthropic", side_effect=AssertionError("a model was called")):
            sample_reports.build("life_book", "en")
        flat = " ".join(_strings(seen[0][0]["houses_detailed"]))
        self.assertIn("rule engine", flat)
        # ...and the switch is scoped: afterwards the default provider is untouched.
        with mock.patch.object(llm, "_anthropic_ready", lambda: True):
            self.assertEqual(llm.default_provider(), "anthropic")

    def test_chart_drawings_are_embedded_and_the_text_is_clean(self):
        for sku in sample_reports.SKUS:
            for lang in LANGS:
                with self.subTest(sku=sku, lang=lang):
                    seen, patch = _spy_compile()
                    with patch:
                        pdf = sample_reports.build(sku, lang)
                    data, files = seen[0]
                    for key in ("d1_north", "d1_south", "d9_north", "d9_south"):
                        self.assertEqual(data[key], f"{key}.svg")
                        self.assertGreater(len(files[data[key]]), 2000)
                    self.assertGreaterEqual(len(re.findall(rb"/Subtype\s*/Form", pdf)), 1)
                    for text in _strings(data):
                        self.assertIsNone(BAD_WORDS.search(text), text[:160])
                    self.assertNotIn("Test Native", " ".join(_strings(data)))
                    self.assertIn("Sample Customer", " ".join(_strings(data)))
                    english = "\n".join(pdf_text.pages_text(pdf)) if lang == "en" else ""
                    for bad in ("Traceback", "nan", "None"):
                        self.assertNotRegex(english, rf"\b{bad}\b")

    @unittest.skipUnless(HAS_DEVA, "no Devanagari font on this machine")
    def test_hindi_samples_are_in_devanagari(self):
        for sku in sample_reports.SKUS:
            with self.subTest(sku=sku):
                seen, patch = _spy_compile()
                with patch:
                    sample_reports.build(sku, "hi")
                data = seen[0][0]
                self.assertEqual(data["lang"], "hi")
                self.assertGreater(len(DEVA.findall(" ".join(_strings(data)))), 400)

    def test_hindi_without_a_devanagari_font_falls_back_to_english_and_says_so(self):
        seen, patch = _spy_compile()
        with patch, mock.patch.object(pdf_report, "devanagari_font", lambda: None):
            sample_reports.build("sq_career", "hi")
        data = seen[0][0]
        self.assertEqual(data["lang"], "en")
        self.assertEqual(data["sample"]["mark"], "SAMPLE")
        self.assertIn("Hindi font", " ".join(_strings(data["about"])))

    # ---- the route -------------------------------------------------------

    def test_headers(self):
        r = client.get("/samples/sq_career.pdf")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["content-type"], "application/pdf")
        self.assertEqual(r.headers["content-disposition"],
                         'inline; filename="Divine-Astro-sample-career-report.pdf"')
        self.assertIn("public", r.headers["cache-control"])
        self.assertIn("max-age=86400", r.headers["cache-control"])
        r = client.get("/samples/life_book.pdf", params={"lang": "hi"})
        self.assertIn("life-book-hindi", r.headers["content-disposition"])
        self.assertNotIn("set-cookie", r.headers)

    def test_unknown_skus_and_other_files_are_404(self):
        for path in ("/samples/nope.pdf", "/samples/k3.pdf", "/samples/k5.pdf", "/samples/k3q3.pdf",
                     "/samples/q_pack_5.pdf", "/samples/../etc/passwd.pdf", "/samples/life_book.txt",
                     "/samples/sq_career.pdf/x", "/samples/.pdf"):
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 404, path)

    def test_a_language_other_than_hindi_is_english(self):
        a = client.get("/samples/sq_wealth_business.pdf", params={"lang": "kn"}).content
        b = client.get("/samples/sq_wealth_business.pdf").content
        self.assertIs(a, b) if a is b else self.assertEqual(a, b)
        self.assertEqual(a, self.pdfs[("sq_wealth_business", "en")])

    def test_no_login_is_needed(self):
        fresh = TestClient(app, raise_server_exceptions=False)      # no cookies at all
        self.assertEqual(fresh.get("/samples/life_book.pdf").status_code, 200)

    def test_the_second_request_does_not_rebuild(self):
        before = sample_reports.builds
        with mock.patch.object(sample_reports, "build", side_effect=AssertionError("rebuilt")):
            for _ in range(3):
                self.assertEqual(client.get("/samples/sq_career.pdf").status_code, 200)
        self.assertEqual(sample_reports.builds, before)

    def test_it_is_kept_on_disk_so_a_restart_does_not_rebuild(self):
        path = sample_reports._path("sq_career", "en")
        self.assertTrue(path.is_file())
        self.assertTrue(str(path).startswith(_TMP), "samples must not be written into the git tree")
        sample_reports._memory.clear()
        with mock.patch.object(sample_reports, "build", side_effect=AssertionError("rebuilt")):
            self.assertEqual(client.get("/samples/sq_career.pdf").content, path.read_bytes())

    def test_a_stale_disk_copy_is_rebuilt(self):
        path = sample_reports._path("sq_career", "en")
        old = time.time() - sample_reports.MAX_AGE_S - 60
        os.utime(path, (old, old))
        sample_reports._memory.clear()
        before = sample_reports.builds
        self.assertEqual(client.get("/samples/sq_career.pdf").status_code, 200)
        self.assertEqual(sample_reports.builds, before + 1)

    def test_concurrent_first_requests_build_once(self):
        sample_reports._memory.clear()
        for f in Path(_TMP).glob("sq_wealth_business.*"):
            f.unlink()
        calls = []
        real = sample_reports.build

        def slow(sku, lang):
            calls.append((sku, lang))
            time.sleep(0.3)
            return real(sku, lang)
        got = []
        with mock.patch.object(sample_reports, "build", slow):
            threads = [threading.Thread(target=lambda: got.append(sample_reports.get_pdf("sq_wealth_business", "en")))
                       for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        self.assertEqual(len(calls), 1, calls)
        self.assertEqual(len({len(g) for g in got}), 1)
        self.assertEqual(len(got), 5)

    def test_one_address_cannot_ask_without_limit(self):
        sample_reports._rate.clear()
        codes = [client.get("/samples/sq_career.pdf").status_code for _ in range(sample_reports.RATE_MAX + 3)]
        self.assertEqual(codes[:sample_reports.RATE_MAX], [200] * sample_reports.RATE_MAX)
        self.assertEqual(codes[sample_reports.RATE_MAX:], [429] * 3)
        self.assertEqual(client.get("/samples/sq_career.pdf").headers.get("retry-after"), "60")
        # another address is not affected, and the window ends
        self.assertTrue(sample_reports._rate_ok("203.0.113.9"))
        key = next(iter(sample_reports._rate))
        start, n = sample_reports._rate[key]
        sample_reports._rate[key] = (start - sample_reports.RATE_WINDOW_S - 1, n)
        self.assertEqual(client.get("/samples/sq_career.pdf").status_code, 200)

    def test_the_visit_beacon_does_not_count_it_as_a_page(self):
        for sku in sample_reports.SKUS:
            self.assertFalse(analytics.is_public_page(f"/samples/{sku}.pdf"))
            self.assertFalse(analytics.is_public_page(f"/hi/samples/{sku}.pdf"))

    def test_the_click_event_is_known_and_labelled(self):
        self.assertIn("sample_view", analytics.EVENT_NAMES)
        self.assertEqual(analytics.parse_event({"name": "sample_view", "detail": "sq_career"}),
                         ("sample_view", "sq_career"))
        for sku in sample_reports.SKUS:
            self.assertIn(("sample_view", sku), analytics.EVENT_LABELS)
        self.assertIn(("sample_view", ""), analytics.EVENT_LABELS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
