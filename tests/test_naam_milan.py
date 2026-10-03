"""Naam se Kundali Milan (DIVASTRO-115).

Pins the syllable reading (Devanagari and Latin), the documented rules
(conjuncts, nukta, ब→व, श, Abhijit, nearest syllable), unknown/empty input,
that the score is exactly the matching engine's for the derived nakshatras,
and the privacy promises: no name in share links, logs, cache or third-party
scripts on a result.

    ~/.venvs/divineastro/bin/python -u -m tests.test_naam_milan
"""

from __future__ import annotations

import logging
from urllib.parse import quote
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_naam_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import naam_milan, share  # noqa: E402
from app.astro import matching, namakshar  # noqa: E402
from app.chart_service import SIGNS  # noqa: E402
from app.main import app  # noqa: E402
from tests.test_seo_pages import check, failures  # noqa: E402
from tests import test_seo_pages as seo_tests  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
seo_tests.client = client


def look(name: str):
    m = namakshar.lookup(name)
    return None if m is None else (m.nakshatra.name, m.pada, SIGNS[m.sign], m.syllable)


def main() -> int:
    print("\n1. Devanagari")
    cases = {
        "राम": ("Chitra", 3, "Libra", "रा"),
        "सीता": ("Shatabhisha", 3, "Aquarius", "सी"),
        "प्रिया": ("Uttara Phalguni", 4, "Virgo", "पी"),        # conjunct: first consonant
        "अर्जुन": ("Krittika", 1, "Aries", "अ"),
        "आरती": ("Krittika", 1, "Aries", "अ"),                  # आ = अ
        "ऐश्वर्या": ("Krittika", 4, "Taurus", "ए"),              # ऐ = ए
        "चेतन": ("Ashwini", 2, "Aries", "चे"),
        "लक्ष्मी": ("Ashwini", 4, "Aries", "ला"),               # inherent a = ा
        "क्षितिज": ("Mrigashira", 4, "Gemini", "की"),
        "कृष्ण": ("Mrigashira", 4, "Gemini", "की"),              # ृ read as "ri"
        "ऋषि": ("Chitra", 4, "Libra", "री"),
        "ज़ोया": ("Uttara Ashadha", 4, "Capricorn", "जो"),       # nukta dropped; Abhijit
        "बबीता": ("Rohini", 2, "Taurus", "वा"),                 # ब = व
        "शिव": ("Shatabhisha", 3, "Aquarius", "सी"),             # श + i = सी
        "श्याम": ("Hasta", 2, "Virgo", "ष"),                     # श + a = ष
        "धीरज": ("Purva Ashadha", 2, "Sagittarius", "धा"),       # nearest same consonant
        "  रोहित ": ("Swati", 3, "Libra", "रो"),
        "मोहन": ("Purva Phalguni", 1, "Leo", "मो"),
    }
    for name, want in cases.items():
        got = look(name)
        check(f"{name.strip()} → {want[3]} {want[0]} {want[1]} ({want[2]})", got == want, str(got))
    m = namakshar.lookup("धीरज")
    check("धीरज is flagged approximate (nearest)", m.via == "nearest" and not m.exact)
    check("ज़ोया is flagged as Abhijit", namakshar.lookup("ज़ोया").via == "abhijit")
    check("राम is exact", namakshar.lookup("राम").exact)

    print("\n2. Latin")
    latin = {
        "Ram": ("Chitra", 3, "Libra", "रा"),
        "Sita": ("Shatabhisha", 3, "Aquarius", "सी"),
        "Priya": ("Uttara Phalguni", 4, "Virgo", "पी"),
        "Arjun": ("Krittika", 1, "Aries", "अ"),
        "Shyam": ("Hasta", 2, "Virgo", "ष"),
        "Swati": ("Shatabhisha", 2, "Aquarius", "सा"),
        "Rohit": ("Swati", 3, "Libra", "रो"),
        "Aishwarya": ("Krittika", 4, "Taurus", "ए"),
        "Chhavi": ("Ardra", 4, "Gemini", "छ"),
        "Bharat": ("Mula", 3, "Sagittarius", "भा"),
        "Kavya": ("Mrigashira", 3, "Gemini", "का"),
        "mohan": ("Purva Phalguni", 1, "Leo", "मो"),
    }
    for name, want in latin.items():
        got = look(name)
        check(f"{name} → {want[3]} {want[0]} {want[1]} ({want[2]})", got == want, str(got))
    tina = namakshar.lookup("Tina")
    check("Tina: त read first, ट offered as an alternative",
          tina.syllable == "ती" and tina.via == "latin"
          and [(n.name, p) for n, p in tina.alternatives] == [("Purva Phalguni", 3)])
    deepak = namakshar.lookup("Deepak")
    check("Deepak: द first, ड alternative", deepak.syllable == "दी"
          and [(n.name, p) for n, p in deepak.alternatives] == [("Ashlesha", 1)])

    print("\n3. Unknown and empty input")
    for bad in ("", "   ", "123", "!!!", "😀", "ॐ", None):
        check(f"{bad!r} → None", namakshar.lookup(bad) is None)
    for params in ({"boy": "123", "girl": "Sita"}, {"boy": "", "girl": ""},
                   {"boy": "x" * 500, "girl": "y"}, {"boy_pada": "nonsense-9"}):
        r = client.get("/naam-se-kundali-milan", params=params)
        check(f"{list(params)} handled: 200 and no crash", r.status_code == 200, str(r.status_code))
    r = client.get("/naam-se-kundali-milan", params={"boy": "123", "girl": "Sita"})
    check("unreadable name asks for a syllable and gives no total",
          "Could not read a first syllable" in r.text and "Total:" not in r.text)
    r = client.get("/naam-se-kundali-milan", params={"boy": "123", "boy_pada": "chitra-3",
                                                     "girl": "Sita"})
    check("a chosen syllable rescues an unreadable name", "Total:" in r.text)

    print("\n4. Same score as the matching engine")
    pairs = [("Ram", "Sita"), ("राम", "सीता"), ("Arjun", "Priya"), ("मोहन", "राधा"),
             ("Shiv", "Parvati"), ("Rohit", "Rohini")]
    for boy, girl in pairs:
        g, b = namakshar.lookup(boy), namakshar.lookup(girl)
        want = matching.ashtakoot(namakshar.moon_bundle(g.nakshatra, g.pada),
                                  namakshar.moon_bundle(b.nakshatra, b.pada))
        got = naam_milan.compute(g, b)
        check(f"{boy} + {girl}: compute() is the engine's result ({want['total']:g})",
              got == want)
        prof = matching.moon_profile(namakshar.moon_bundle(g.nakshatra, g.pada))
        check(f"{boy}: synthetic Moon reads back as {g.nakshatra.name} {g.pada}",
              (prof["nakshatra"], prof["pada"], prof["rashi"]) ==
              (g.nakshatra.name, g.pada, SIGNS[g.sign]) and prof["name"] == "")
        html = client.get("/naam-se-kundali-milan", params={"boy": boy, "girl": girl}).text
        check(f"{boy} + {girl}: page shows the total {want['total']:g} / 36",
              f"Total: {want['total']:g} / 36" in html)
    html = client.get("/hi/naam-se-kundali-milan", params={"boy": "राम", "girl": "सीता"}).text
    want = naam_milan.compute(namakshar.lookup("राम"), namakshar.lookup("सीता"), "hi")
    check("Hindi result: total and Hindi koota labels",
          f"कुल गुण: {want['total']:g} / 36" in html and "नाड़ी" in html and "भकूट" in html)
    check("Mangal dosha is N/A on a result",
          "Mangal dosha: not applicable" in client.get(
              "/naam-se-kundali-milan", params={"boy": "Ram", "girl": "Sita"}).text
          and "मांगलिक दोष: लागू नहीं" in html)
    html = client.get("/naam-se-kundali-milan",
                      params={"boy": "Tina", "girl": "Sita", "boy_pada": "purva-phalguni-3"}).text
    check("a chosen pada overrides the name and stays selected",
          'value="purva-phalguni-3" selected' in html and "You chose this syllable" in html)
    html = client.get("/naam-se-kundali-milan", params={"boy": "Tina", "girl": "Sita"}).text
    check("an ambiguous Latin name explains itself and offers the alternative first",
          "cannot settle this syllable" in html
          and html.index('value="purva-phalguni-3"') < html.index('value="ashwini-1"'))

    print("\n5. The bare page")
    for path in ("/naam-se-kundali-milan", "/hi/naam-se-kundali-milan"):
        html = seo_tests.common(path, path, path, ["नाम से कुंडली मिलान", 'name="boy"',
                                                   'name="girl"', 'method="get"'])
        check(f"{path}: CTA to birth-chart milan", 'href="/?open=milan' in html)
        check(f"{path}: shortcut caveat", "traditional shortcut" in html
              or "पारंपरिक शॉर्टकट" in html)
        check(f"{path}: indexable", "noindex" not in html)

    print("\n6. Privacy")
    secret_en, secret_hi = "Zxqvorine", "ज़ैनबुन्निसा"
    records: list[str] = []

    class Grab(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            # The test's own HTTP client (httpx) logs the URL it requests; that
            # is this process playing the browser, not the server.
            if record.name.startswith(("httpx", "httpcore")):
                return
            try:
                records.append(record.getMessage() + " " + repr(record.args))
            except Exception:  # noqa: BLE001
                records.append(str(record.msg))

    root = logging.getLogger()
    handler, old = Grab(level=logging.DEBUG), root.level
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    try:
        r = client.get("/naam-se-kundali-milan", params={"boy": secret_en, "girl": "Sita"})
        r_hi = client.get("/hi/naam-se-kundali-milan", params={"boy": "राम", "girl": secret_hi})
    finally:
        root.removeHandler(handler)
        root.setLevel(old)
    enc_hi = quote(secret_hi)
    check("names are not logged", not any(s in x for x in records for s in (secret_en, secret_hi, enc_hi)),
          str([x for x in records if secret_en in x][:2]))
    for resp, secret in ((r, secret_en), (r_hi, secret_hi)):
        html = resp.text
        shares = re.findall(r'class="share-wa" href="([^"]+)"', html)
        check("result keeps the WhatsApp button", len(shares) == 1)
        check("share link carries no name and no query from the form",
              all(secret not in s and "boy" not in s and "girl" not in s for s in shares))
        check("result is no-store", resp.headers.get("cache-control") == "no-store")
        check("result sends Referrer-Policy: no-referrer",
              resp.headers.get("referrer-policy") == "no-referrer")
        check("referrer meta comes before any subresource",
              html.index('name="referrer" content="no-referrer"') < html.index("/static/"))
        check("result is noindex", 'content="noindex"' in html
              and resp.headers.get("x-robots-tag") == "noindex")
        check("no AdSense script on a result", "adsbygoogle.js" not in html)
        check("address bar query is dropped", "history.replaceState" in html)
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', html).group(1)
        check("canonical has no query", "?" not in canon)
    for p in ("/naam-se-kundali-milan", "/hi/naam-se-kundali-milan"):
        text = share.seo_share_text(p) or ""
        check(f"share text for {p} is generic", bool(text) and secret_en not in text)
    caddy = (ROOT / "Caddyfile").read_text(encoding="utf-8")
    check("Caddy access log filters every form parameter",
          all(f"delete {p}" in caddy for p in naam_milan.PARAMS))
    ci = (ROOT / ".github" / "workflows").glob("*.yml")
    check("both suites are in the CI unit list", any(
        "test_naam_milan" in f.read_text() and "test_nakshatra_rashi_pages" in f.read_text()
        for f in ci))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("naam milan: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
