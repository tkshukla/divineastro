"""The daily Rashifal pages (DIVASTRO-105).

Like tests/test_seo_pages.py, every page check reads the raw HTML exactly as a
crawler gets it. On top of that it pins what makes these pages more than copy:
the Moon-transit house each sign is told about is checked against an
independent Swiss Ephemeris calculation for fixed dates (one with a Moon sign
change in the evening, one without), and the phrase bank must cover every
house in both languages.

No server needed (FastAPI's in-process client). A throwaway SQLite database is
used — never a real one.

    ~/.venvs/divineastro/bin/python -u -m tests.test_rashifal_pages
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_rashifal_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

import swisseph as swe  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, rashifal_pages as rp, seo_pages  # noqa: E402
from app.astro import panchang as panchang_engine  # noqa: E402
from app.main import app  # noqa: E402
from tests.test_seo_pages import canonical, check, failures, title  # noqa: E402
from tests import test_seo_pages as seo_tests  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
seo_tests.client = client

SITE = seo_pages.SITE_URL
IST = ZoneInfo("Asia/Kolkata")
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
TODAY = dt.datetime.now(IST).date()


def hreflang(html: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"', html))


def independent_moon_sign(moment: dt.datetime) -> int:
    """Sidereal (Lahiri) Moon sign straight from swisseph — not via the app."""
    panchang_engine._ephemeris()                       # only points swisseph at its data files
    u = moment.astimezone(dt.timezone.utc)
    jd = swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
    return int(lon % 360 // 30)


def main() -> int:
    print("\n1. Every sign, both languages")
    for lang in rp.LANGS:
        for r in (None, *rp.RASHIS):
            path = rp.path(r, lang)
            must = (["राशिफल"] if lang == "hi" else ["Rashifal"])
            if r:
                must.append(r.name_hi if lang == "hi" else r.english)
            html = seo_tests.common(path, path, path, must)
            alt = hreflang(html)
            check(f"{path}: hreflang en/hi/x-default",
                  alt.get("en-IN") == SITE + rp.path(r, "en")
                  and alt.get("hi-IN") == SITE + rp.path(r, "hi")
                  and alt.get("x-default") == SITE + rp.path(r, "en"), str(alt))
            check(f"{path}: html lang", f'<html lang="{"hi" if lang == "hi" else "en"}-IN">' in html)
            check(f"{path}: shows today's date",
                  rp._date_text(TODAY, lang) in html, rp._date_text(TODAY, lang))
            check(f"{path}: CTA is /?open=kundali", 'class="cta" href="/?open=kundali"' in html)
            check(f"{path}: personal-reading line",
                  ("पूरी जन्म कुंडली" if lang == "hi" else "full birth") in html)
            if r:
                others = [o for o in rp.RASHIS if o != r]
                check(f"{path}: links the other 11 signs",
                      all(f'href="{rp.path(o, lang)}"' in html for o in others))
                body = html.split('<main class="seo">')[1]
                dev = len(DEVANAGARI.findall(body))
                if lang == "hi":
                    check(f"{path}: body is mostly Hindi", dev > 400, str(dev))
                check(f"{path}: no invented lucky number/colour",
                      not re.search(r"lucky|शुभ अंक|शुभ रंग", html, re.I))

    titles = {title(client.get(rp.path(r, lang)).text) for lang in rp.LANGS for r in rp.RASHIS}
    check("titles are unique across the 24 sign pages", len(titles) == 24, str(len(titles)))
    t = title(client.get("/rashifal/mesh").text)
    check("EN title format", t.startswith(f"Mesh Rashifal Today, {rp._date_text(TODAY, 'en', True)} "
                                          "— Aries Daily Horoscope"), t)

    print("\n2. Redirects and 404s")
    for lang in rp.LANGS:
        for r in rp.RASHIS:
            src = rp.path(r, lang).replace(r.slug, r.english.lower())
            resp = client.get(src, follow_redirects=False)
            check(f"{src} → 301 {rp.path(r, lang)}",
                  resp.status_code == 301 and resp.headers.get("location") == rp.path(r, lang),
                  f"{resp.status_code} {resp.headers.get('location')}")
        bad = rp.path(None, lang) + "/atlantis"
        resp = client.get(bad)
        check(f"{bad} is a 404, not cacheable",
              resp.status_code == 404 and resp.headers.get("cache-control") == "no-store",
              f"{resp.status_code} {resp.headers.get('cache-control')}")
        check(f"beacon rejects {bad}", not analytics.is_public_page(bad))
    check("beacon rejects a redirecting alias", not analytics.is_public_page("/rashifal/aries"))

    print("\n3. sitemap.xml")
    root = ET.fromstring(client.get("/sitemap.xml").content)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [e.text for e in root.findall("s:url/s:loc", ns)]
    want = {SITE + p for p in rp.sitemap_paths()}
    n_urls = 13 * len(rp.TRANSLATED)          # index + 12 signs, per translated language
    check(f"sitemap lists all {n_urls} rashifal URLs", len(want) == n_urls and want <= set(locs),
          str(sorted(want - set(locs))[:5]))
    check("sitemap still has no duplicates", len(locs) == len(set(locs)))

    print("\n4. Computed, not invented")
    # 4 Oct 2026: the Moon leaves Gemini for Cancer in the evening (IST);
    # 3 Oct 2026: Gemini all day.
    for day in (dt.date(2026, 10, 3), dt.date(2026, 10, 4)):
        start = dt.datetime.combine(day, dt.time(), IST)
        s_first = independent_moon_sign(start)
        s_last = independent_moon_sign(start + dt.timedelta(hours=23, minutes=59, seconds=59))
        sky = rp.sky(day)
        segs = sky["moon"]
        check(f"{day}: Moon sign(s) match swisseph",
              [x["sign"] for x in segs] == ([s_first] if s_first == s_last else [s_first, s_last]),
              f"{[x['sign'] for x in segs]} vs {s_first},{s_last}")
        if len(segs) == 2:
            change = segs[0]["until"]
            check(f"{day}: sign flips at the reported ingress ({change:%H:%M:%S})",
                  independent_moon_sign(change - dt.timedelta(seconds=30)) == s_first
                  and independent_moon_sign(change + dt.timedelta(seconds=30)) == s_last)
        for r in rp.RASHIS:
            got = [x["house"] for x in rp.reading(r, day)["moon"]]
            exp = [(x["sign"] - r.index) % 12 + 1 for x in segs]
            if got != exp:
                check(f"{day} {r.slug}: Moon house", False, f"{got} != {exp}")
        mesh = rp.reading(rp.BY_SLUG["mesh"], day)
        check(f"{day}: Mesh Moon house from janma rashi = {(s_first - 0) % 12 + 1}",
              mesh["moon"][0]["house"] == s_first % 12 + 1)

    # Freeze "today" and read it back off the page.
    real_today = rp._today
    rp._today = lambda: dt.date(2026, 10, 4)
    try:
        html = client.get("/rashifal/mesh").text
        html_hi = client.get("/hi/rashifal/mesh").text
        ingress = rp.sky(dt.date(2026, 10, 4))["moon"][0]["until"]
        clock = seo_pages._clock(ingress)
        check("frozen 4 Oct: page shows 4 October 2026", "4 October 2026" in html)
        check("frozen 4 Oct: Mesh told 3rd then 4th house, with the IST time",
              f"Until {clock} IST" in html and "your 3rd house" in html
              and f"From {clock} IST" in html and "your 4th house" in html, clock)
        check("frozen 4 Oct: Hindi page has both parts",
              f"{clock} (IST) तक" in html_hi and "तीसरे भाव" in html_hi and "चौथे भाव" in html_hi)
        check("frozen 4 Oct: both phrase-bank paragraphs present",
              rp.MOON_HOUSE[3]["en"] in html.replace("&#x27;", "'")
              and rp.MOON_HOUSE[4]["en"] in html.replace("&#x27;", "'"))
    finally:
        rp._today = real_today

    # Slow planets and Sade Sati agree with the panchang engine's own rule.
    day = dt.date(2026, 10, 3)
    sky = rp.sky(day)
    for r in rp.RASHIS:
        ss = panchang_engine.sade_sati_for_moon_sign(
            r.index, dt.datetime.combine(day, dt.time(12), IST), window_years=3)
        reading = rp.reading(r, day)
        if (reading["saturn"] != ss["saturn"]["house_from_moon"]
                or bool(reading["sade_sati_phase"]) != ss["running"]):
            check(f"{r.slug}: Saturn/Sade Sati agree with panchang.sade_sati_for_moon_sign",
                  False, f"{reading['saturn']} {reading['sade_sati_phase']} vs {ss['running']}")
    check("Saturn house and Sade Sati agree with the engine for all 12 signs",
          not any("Sade Sati agree" in f for f in failures))
    check("Rahu and Ketu are always 7 houses apart",
          all((rp.reading(r, day)["ketu"] - rp.reading(r, day)["rahu"]) % 12 == 6 for r in rp.RASHIS))

    print("\n5. Phrase bank")
    for name, bank in (("MOON_HOUSE", rp.MOON_HOUSE), ("SATURN_HOUSE", rp.SATURN_HOUSE),
                       ("JUPITER_HOUSE", rp.JUPITER_HOUSE), ("RAHU_HOUSE", rp.RAHU_HOUSE)):
        complete = (set(bank) == set(range(1, 13))
                    and all(bank[h]["en"].strip() and DEVANAGARI.search(bank[h]["hi"])
                            and not re.search(r"[A-Za-z]{3,}", bank[h]["hi"])
                            for h in bank))
        check(f"{name}: houses 1–12 in English and Hindi", complete)
    check("Moon scheme: 1,3,6,7,10,11 favourable; 4,8,12 take it easy; 2,5,9 mixed",
          [rp.moon_tone(h) for h in range(1, 13)] ==
          ["good", "mixed", "good", "easy", "mixed", "good", "good", "easy", "mixed", "good",
           "good", "easy"])
    fear = re.compile(r"\b(death|disease|die|accident|guarantee|curse)\b|मृत्यु|रोग", re.I)
    check("phrase bank avoids fear words and guarantees", not any(
        fear.search(v) for bank in (rp.MOON_HOUSE, rp.SATURN_HOUSE, rp.JUPITER_HOUSE,
                                    rp.RAHU_HOUSE) for e in bank.values() for v in e.values()))

    print("\n6. Wiring")
    tools_js = (ROOT / "app" / "static" / "tools.js").read_text(encoding="utf-8")
    check("tools.js handles ?open=kundali", "kundali: '#home-cta'" in tools_js)
    check("panchang page cross-links /rashifal", 'href="/rashifal"' in client.get("/panchang").text)
    for p in ("/rashifal", "/hi/rashifal/meen"):
        check(f"beacon accepts {p}", analytics.is_public_page(p))
    check("canonical of /hi/rashifal is itself",
          canonical(client.get("/hi/rashifal").text) == SITE + "/hi/rashifal")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("rashifal pages: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
