"""DIVASTRO-124: answers, PDFs, emails and push in Kannada, Telugu, Tamil,
Malayalam, Bengali and Odia.

  1. The narration prompt for each language carries the target-language
     instruction and the glossary (grahas, rashis, nakshatras, dasha words,
     Rahu Kaal, months) from the names tables.
  2. The date auditor reads dates written in each script (and in that script's
     digits), accepts the ones the facts allow, flags invented ones.
  3. End to end (TestClient, throwaway SQLite, the Anthropic SDK replaced by a
     fake — the real API is never called): a regional answer is the model's;
     with narration off, or when it fails, the English engine text comes with
     the "Answer shown in English" note in the reader's language.
  4. Sign-in email and push text in each language (script checks; the code is
     never in the subject).
  5. Kundali PDF in each language: renders, embeds the script's Noto font, is
     offered by the app (window.DA_PDF_LANGS) and served by /api/pdf/chart.

    python tests/test_regional_languages.py
"""

from __future__ import annotations

import datetime as dt
import json
import os
import random
import re
import sys
import tempfile
import types
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="astro_regional_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["ASTRO_GATEWAY"] = "test"
os.environ.pop("ANTHROPIC_API_KEY", None)        # never the real API

from fastapi.testclient import TestClient  # noqa: E402

from app import email_auth, i18n, llm, pdf_i18n, pdf_report, push_message  # noqa: E402
from app.astro.names_i18n import names_for  # noqa: E402
from app.main import app, _fallback_note, _pdf_lang  # noqa: E402

REGIONAL = ("kn", "te", "ta", "ml", "bn", "or")
# Unicode block of each script: every letter of the text must come from it.
BLOCK = {"kn": (0x0C80, 0x0CFF), "te": (0x0C00, 0x0C7F), "ta": (0x0B80, 0x0BFF),
         "ml": (0x0D00, 0x0D7F), "bn": (0x0980, 0x09FF), "or": (0x0B00, 0x0B7F)}
ZERO = {"kn": 0x0CE6, "te": 0x0C66, "ta": 0x0BE6, "ml": 0x0D66, "bn": 0x09E6, "or": 0x0B66}
FONT = {"kn": "Kannada", "te": "Telugu", "ta": "Tamil", "ml": "Malayalam", "bn": "Bengali",
        "or": "Oriya"}

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def in_script(text: str, code: str) -> bool:
    """True when `text` has letters of `code`'s script and none of another Indic one."""
    lo, hi = BLOCK[code]
    indic = [c for c in text if 0x0900 <= ord(c) <= 0x0D7F]
    return bool(indic) and all(lo <= ord(c) <= hi or c in "।॥" for c in indic)


def native_digits(s: str, code: str) -> str:
    return "".join(chr(ZERO[code] + int(c)) if c.isdigit() else c for c in s)


# --------------------------------------------------------------------------
# 1. Prompt
# --------------------------------------------------------------------------

def prompt_checks() -> None:
    print("\n1. Prompt: target language + glossary")
    analysis = {
        "topic_label": "Career", "verdict": "favourable", "score": 0.4,
        "evidence": [{"factor": "dasha", "detail": "Mars Capricorn 28°39' runs Jul 2026 to Jul 2045",
                      "score": 0.3}],
    }
    for code in REGIONAL:
        n = names_for(code)
        system = llm._system(code)
        prompt = llm._build_prompt(analysis, code, "When will my career grow?")
        check(f"{code}: system names the language and its script",
              llm.LANGUAGES[code] in system and "GLOSSARY" in system)
        wanted = [f"Mars={n.GRAHA['Mars']}", f"Capricorn={n.RASHI['Capricorn']}",
                  f"Rohini={n.NAKSHATRAS['Rohini']}", f"Rahu Kaal={n.TIMINGS['rahu_kaal']}",
                  f"October={n.MONTHS[9]}", "dasha=", "mahadasha=", "house="]
        missing = [w for w in wanted if w not in system]
        check(f"{code}: glossary has grahas, rashis, nakshatras, Rahu Kaal, months, dasha words",
              not missing, str(missing))
        check(f"{code}: no example year leaks into the glossary", not re.search(r"20\d\d", llm._glossary(code)))
        check(f"{code}: user prompt asks for the language",
              f"Write the answer in {llm.LANGUAGES[code]}" in prompt)
        check(f"{code}: allowed dates are listed in the target script too",
              f"{n.MONTHS[6]} 2026" in prompt and f"{n.MONTHS[6]} 2045" in prompt
              and "Jul 2026" in prompt)
    check("Hindi keeps its own note (no regional glossary)",
          "Capricorn=मकर" in llm._system("hi") and "GLOSSARY" not in llm._system("hi"))
    check("English has no glossary", "GLOSSARY" not in llm._system("en"))
    check("report prompts: regional glossary and language",
          llm._report_lang("ta") == llm.LANGUAGES["ta"] and "GLOSSARY" in llm._report_glossary("ta")
          and llm._report_glossary("en") == "")


# --------------------------------------------------------------------------
# 2. Date auditor
# --------------------------------------------------------------------------

def auditor_checks() -> None:
    print("\n2. Date auditor in every script")
    prompt = "The Mars period runs from Jul 2026 to Jul 2045; Saturn transits from Mar 2027."
    for code in ("hi",) + REGIONAL:
        M = names_for(code).MONTHS
        good = f"{M[6]} 2026 – {M[6]} 2045; {M[2]} 2027."
        meta: dict = {}
        llm._audit_dates(meta, prompt, good)
        check(f"{code}: dates the facts allow pass", "date_violations" not in meta, str(meta))
        meta = {}
        llm._audit_dates(meta, prompt, f"... {M[8]} 2026 ... {M[6]} 2045")
        check(f"{code}: an invented month is flagged", meta.get("date_violations") == ["Sep 2026"],
              str(meta))
        if code in ZERO:
            meta = {}
            llm._audit_dates(meta, prompt, f"{M[6]} {native_digits('2026', code)}; "
                                           f"{M[10]} {native_digits('2031', code)}")
            check(f"{code}: native digits are read", meta.get("date_violations") == ["Nov 2031"],
                  str(meta))
    # Year first with a case ending (Kannada), and a short month inside a word.
    meta = {}
    llm._audit_dates(meta, prompt, "2045ರ ಜುಲೈ ತನಕ; 2030ರ ಡಿಸೆಂಬರ್‌ನಲ್ಲಿ")
    check("kn: '2045ರ ಜುಲೈ' passes, '2030ರ ಡಿಸೆಂಬರ್‌ನಲ್ಲಿ' is flagged",
          meta.get("date_violations") == ["Dec 2030"], str(meta))
    meta = {}
    llm._audit_dates(meta, prompt, "2026ರ ಮೇಲೆ ಪರಿಣಾಮ; ஆகஸ்டு 2027")
    check("kn 'ಮೇಲೆ' is not May; Tamil variant spelling 'ஆகஸ்டு' is read",
          meta.get("date_violations") == ["Aug 2027"], str(meta))
    meta = {}
    llm._audit_dates(meta, prompt, "ಜುಲೈ 2026 ಆಗಸ್ಟ್ 2045")
    check("a month-first date's year is not reused year-first",
          meta.get("date_violations") == ["Aug 2045"], str(meta))
    meta = {}
    llm._audit_dates(meta, prompt, "This runs Jul 2026 to Jul 2045.")
    check("English still audited as before", "date_violations" not in meta, str(meta))


# --------------------------------------------------------------------------
# 3. End to end, with a fake Anthropic SDK
# --------------------------------------------------------------------------

class _FakeStream:
    def __init__(self, text: str):
        self.text_stream = iter([text[i:i + 50] for i in range(0, len(text), 50)])

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return types.SimpleNamespace(stop_reason="end_turn")


def fake_anthropic(answer: str, seen: list, fail: bool = False) -> types.ModuleType:
    mod = types.ModuleType("anthropic")

    class Anthropic:
        def __init__(self, *a, **k):
            def stream(**kwargs):
                seen.append(kwargs)
                if fail:
                    raise RuntimeError("API down")
                return _FakeStream(answer)
            self.beta = types.SimpleNamespace(messages=types.SimpleNamespace(stream=stream))

    mod.Anthropic = Anthropic
    return mod


def sse(text: str) -> list[tuple[str, dict]]:
    out = []
    for block in text.strip().split("\n\n"):
        ev = data = None
        for line in block.splitlines():
            if line.startswith("event: "):
                ev = line[7:]
            elif line.startswith("data: "):
                data = json.loads(line[6:])
        if ev:
            out.append((ev, data))
    return out


def e2e_checks(client: TestClient, sid: str) -> None:
    print("\n3. /api/ask and /api/ask/stream in Kannada")
    real_mod = sys.modules.get("anthropic")
    real_ollama = llm._ollama_models
    llm._ollama_models = lambda: []          # no local fallback in the test
    kn_answer = ("ನಿಮ್ಮ ವೃತ್ತಿಜೀವನದ ಬಗ್ಗೆ ಕುಂಡಲಿ ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳುತ್ತದೆ. " * 6).strip()
    try:
        for code in REGIONAL:
            note = _fallback_note(code)
            check(f"{code}: 'Answer shown in English' is in its own script",
                  note == i18n.get(code).english_answer and in_script(note, code), note)
        check("no note for English or Hindi", _fallback_note("en") is None and _fallback_note("hi") is None)

        r = client.post("/api/ask", json={"session_id": sid, "question": "How is my career?",
                                          "language": "kn", "provider": "off"})
        a = r.json()
        check("off: English engine text with the Kannada note",
              r.status_code == 200 and a.get("fallback_note") == i18n.get("kn").english_answer
              and a.get("answer") == a.get("answer_engine"), str(a.get("fallback_note")))

        seen: list = []
        sys.modules["anthropic"] = fake_anthropic(kn_answer, seen)
        r = client.post("/api/ask", json={"session_id": sid, "question": "How is my career?",
                                          "language": "kn", "provider": "anthropic"})
        a = r.json()
        check("model answer: the Kannada text, no fallback note",
              r.status_code == 200 and a.get("answer") == kn_answer and "fallback_note" not in a,
              str(a.get("llm_error")))
        check("the model was asked for Kannada with the glossary",
              seen and "Kannada" in seen[-1]["system"] and "ಕುಜ" in seen[-1]["system"])

        sys.modules["anthropic"] = fake_anthropic("", seen, fail=True)
        r = client.post("/api/ask", json={"session_id": sid, "question": "How is my career?",
                                          "language": "ta", "provider": "anthropic"})
        a = r.json()
        check("model failure: English engine text with the Tamil note",
              a.get("llm_error") and a.get("fallback_note") == i18n.get("ta").english_answer
              and a.get("answer") == a.get("answer_engine"))

        r = client.post("/api/ask/stream", json={"session_id": sid, "question": "How is my career?",
                                                 "language": "bn", "provider": "anthropic"})
        events = sse(r.text)
        kinds = [e for e, _ in events]
        check("stream: analysis carries the Bengali note, then the error, then done",
              events and events[0][1].get("fallback_note") == i18n.get("bn").english_answer
              and "error" in kinds and kinds[-1] == "done", str(kinds))
    finally:
        llm._ollama_models = real_ollama
        if real_mod is None:
            sys.modules.pop("anthropic", None)
        else:
            sys.modules["anthropic"] = real_mod


# --------------------------------------------------------------------------
# 4. Email and push
# --------------------------------------------------------------------------

def message_checks() -> None:
    print("\n4. Sign-in email and push text")
    code = "482913"
    for lang in REGIONAL:
        text, html = email_auth.compose(code, lang)
        subject = email_auth.subject(lang)
        first = text.split("\n\n—\n\n")[0]
        check(f"{lang}: email body opens in its script and carries the code",
              in_script(first, lang) and code in first, first[:60])
        check(f"{lang}: English follows", "Your Divine Astro sign-in code is" in text)
        check(f"{lang}: html has the code prominently once per language",
              html.count(f">{code}</p>") == 2 and in_script(html, lang))
        check(f"{lang}: subject in its script, never the code",
              in_script(subject, lang) and code not in subject and "Divine Astro" in subject, subject)
    check("en/hi subject unchanged", email_auth.subject("en") == email_auth.SUBJECT
          == email_auth.subject("hi"))

    day = dt.date(2026, 10, 6)                  # Indira Ekadashi (parana next morning)
    plain = dt.date(2026, 10, 14)
    for lang in REGIONAL:
        m = push_message.build(day, 28.6139, 77.2090, "Asia/Kolkata", lang, city="New Delhi, Delhi")
        check(f"{lang}: festival push in its script, link to /{lang}/",
              in_script(m["title"], lang) and in_script(m["body"].split(" · ")[0], lang)
              and m["path"].startswith(f"/{lang}/vrat-tyohar"), f"{m['title']} | {m['body']}")
        m = push_message.build(plain, 12.9716, 77.5946, "Asia/Kolkata", lang, city="Bengaluru")
        if not m["path"].startswith(f"/{lang}/vrat-tyohar"):
            check(f"{lang}: Rahu Kaal push in its script",
                  in_script(m["title"].replace("Bengaluru", ""), lang) and in_script(m["body"], lang)
                  and f"/{lang}/rahu-kaal" in m["path"], m["title"])


# --------------------------------------------------------------------------
# 5. PDFs
# --------------------------------------------------------------------------

def _pdf_fonts(data: bytes) -> set[str]:
    return set(re.findall(rb"/BaseFont\s*/[A-Z]{6}\+([A-Za-z0-9-]+)", data)) | \
        {m for s in re.findall(rb"stream\r?\n(.*?)endstream", data, re.S)
         for m in _inflate_fonts(s)}


def _inflate_fonts(raw: bytes) -> set[bytes]:
    try:
        return set(re.findall(rb"/BaseFont\s*/[A-Z]{6}\+([A-Za-z0-9-]+)", zlib.decompress(raw)))
    except Exception:
        return set()


def pdf_checks(client: TestClient, sid: str) -> None:
    print("\n5. Kundali PDF per language")
    langs = pdf_report.pdf_languages()
    check("all six regional languages are printable here", all(c in langs for c in REGIONAL),
          str(langs))
    index = client.get("/").text
    m = re.search(r"window\.DA_PDF_LANGS=(\[.*?\]);", index)
    check("index.html tells the app which PDF languages exist",
          m and json.loads(m.group(1)) == langs, m.group(1) if m else "missing")
    check("an unknown or font-less code gets English", _pdf_lang("xx") == "en" and _pdf_lang(None) == "en")
    for code in REGIONAL:
        r = client.get(f"/api/pdf/chart/{sid}?lang={code}")
        ok = r.status_code == 200 and r.content[:5] == b"%PDF-"
        fonts = _pdf_fonts(r.content) if ok else set()
        want = f"Noto{'Sans' if code == 'or' else 'Serif'}{FONT[code]}".encode()
        check(f"{code}: /api/pdf/chart renders and embeds {want.decode()}",
              ok and any(f.startswith(want) for f in fonts), str(sorted(fonts))[:200])
        labels = pdf_i18n.texts(code)
        check(f"{code}: every heading is in its script",
              all(in_script(re.sub(r"\(.*?\)|\d+", "", v), code) for v in labels.values()))
    check("pdf_i18n: cell vocabulary translates a retrograde planet and a degree",
          pdf_i18n.translate("Mars R", "ta").startswith(names_for("ta").GRAHA["Mars"])
          and pdf_i18n.translate("12°04' Leo", "kn") == "12°04' " + names_for("kn").RASHI["Leo"])


def main() -> int:
    prompt_checks()
    auditor_checks()
    message_checks()

    client = TestClient(app)
    email = f"regional{random.randint(10000, 99999)}@example.com"
    r = client.post("/api/auth/dev", json={"email": email, "name": "Regional Test"})
    check("dev sign-in", r.status_code == 200, r.text[:200])
    r = client.post("/api/chart", json={
        "name": "Sanskruti", "date": "1999-08-14", "time": "14:07",
        "place": "Pune, Maharashtra, India", "latitude": 18.5204, "longitude": 73.8567,
        "timezone": "Asia/Kolkata"})
    check("chart cast", r.status_code == 200, r.text[:200])
    sid = r.json()["session_id"]
    e2e_checks(client, sid)
    pdf_checks(client, sid)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("regional languages: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
