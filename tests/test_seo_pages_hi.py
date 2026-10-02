"""DIVASTRO-106: the Hindi copies under /hi/, ~100 cities, /free-kundali.

Same approach as tests/test_seo_pages.py (whose `common` page checks this
reuses): read the raw HTML exactly as a crawler gets it, in-process, on a
throwaway SQLite database. On top of that it pins what fails silently for
bilingual SEO — an hreflang that only points one way, a Hindi page that is
English with a Hindi title, a city that 500s, a sitemap URL the visit beacon
would drop — and how long the pages take.

    ~/.venvs/divineastro/bin/python -u -m tests.test_seo_pages_hi
"""

from __future__ import annotations

import datetime as dt
import json
import re
import statistics
import time
import xml.etree.ElementTree as ET

from tests.test_seo_pages import (  # noqa: E402  (sets up the temp DB first)
    DEVANAGARI, ROOT, SITE, TODAY, canonical, check, client, common, failures, title)

from app import analytics, seo_cities, seo_pages  # noqa: E402
from app import main as app_main  # noqa: E402
from app.astro import choghadiya as chog  # noqa: E402
from app.astro import panchang as panchang_engine  # noqa: E402
from app.astro.muhurat import NAKSHATRAS_HI, TITHI_HI  # noqa: E402
from app.astro.vargas import DEFAULT_DIVISIONS  # noqa: E402
from app.chart_service import NAKSHATRAS  # noqa: E402

TOOLS = tuple(seo_pages.TOOLS)
# The 30 DIVASTRO-100 slugs: already indexed public URLs, so they may never go.
ORIGINAL_SLUGS = (
    "new-delhi mumbai kolkata chennai bengaluru hyderabad ahmedabad pune jaipur lucknow "
    "kanpur nagpur indore bhopal patna varanasi prayagraj surat vadodara chandigarh amritsar "
    "dehradun haridwar noida gurugram bhubaneswar guwahati ranchi kochi visakhapatnam").split()
LATIN = re.compile(r"[A-Za-z]")


def alternates(html: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"/>', html))


def main_text(html: str) -> str:
    """Visible text of <main>, tags and the English subtitle line dropped."""
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.S)
    body = m.group(1) if m else ""
    body = re.sub(r'<[^>]+lang="en"[^>]*>.*?</[^>]+>', " ", body, flags=re.S)
    return re.sub(r"<[^>]+>", " ", body)


def ld_graph(html: str) -> list[dict]:
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1))["@graph"] if m else []


def main() -> int:
    hi_pages = {
        "/hi/panchang": ["आज का पंचांग", "तिथि", "नक्षत्र", "योग", "करण", "सूर्योदय", "राहु काल",
                         "अभिजित", "पंचांग के पाँच अंग"],
        "/hi/panchang/mumbai": ["मुंबई में आज का पंचांग", "चंद्र राशि"],
        "/hi/rahu-kaal/kolkata": ["कोलकाता में आज का राहु काल", "राहु काल क्या है?", "यमगण्ड",
                                  "इस सप्ताह"],
        "/hi/choghadiya/chennai": ["चेन्नई में आज का चौघड़िया", "दिन का चौघड़िया",
                                   "रात का चौघड़िया", "अमृत", "लाभ"],
        "/hi/kundali-milan": ["अष्टकूट", "नाड़ी", "भकूट", "मांगलिक", "36"],
        "/hi/free-kundali": ["जन्म कुंडली", "विंशोत्तरी", "नवांश", "अक्सर पूछे जाने वाले प्रश्न"],
    }

    print("\n1. Hindi pages are Hindi")
    for path, must in hi_pages.items():
        html = common(path, path, path, must)
        check(f"{path}: <html lang=\"hi\">", '<html lang="hi">' in html)
        check(f"{path}: og:locale hi_IN", 'property="og:locale" content="hi_IN"' in html)
        check(f"{path}: JSON-LD inLanguage hi-IN",
              any(n.get("inLanguage") == "hi-IN" for n in ld_graph(html)))
        text = main_text(html)
        deva, latin = len(DEVANAGARI.findall(text)), len(LATIN.findall(text))
        check(f"{path}: body is mostly Devanagari", deva > 4 * latin, f"{deva} vs {latin}")
        check(f"{path}: Hindi footer", "गोपनीयता नीति" in html)
        check(f"{path}: Hindi title", bool(DEVANAGARI.search(title(html))))
    html = client.get("/hi/panchang").text
    p = panchang_engine.daily_panchang(TODAY, 28.6139, 77.2090, "Asia/Kolkata")
    tithi, nak = p["summary"]["tithi"], p["summary"]["nakshatra"]
    check("/hi/panchang: tithi and nakshatra in Hindi, from the engine",
          TITHI_HI[tithi] in html and NAKSHATRAS_HI[nak] in html, f"{tithi}/{nak}")
    table = re.search(r"<table>(.*?)</table>", html, re.S).group(1)
    check("/hi/panchang: no English limb names in the table",
          tithi not in table and nak not in table and " AM" not in table and " PM" not in table)
    check("/hi/panchang: Hindi clock times", len(re.findall(r"(सुबह|दोपहर|शाम|रात) \d{1,2}:\d\d",
                                                            table)) >= 8)
    html = client.get("/hi/choghadiya/chennai").text
    check("/hi/choghadiya: 16 slots", html.count("<tr><td>") == 16, str(html.count("<tr><td>")))
    check("/hi/choghadiya: Hindi slot descriptions",
          chog.CHOGHADIYA_INFO["Amrit"]["description_hi"] in html)
    html = client.get("/hi/rahu-kaal/kolkata").text
    week = re.search(r"इस सप्ताह का राहु काल</h2>(.*?)</table>", html, re.S)
    check("/hi/rahu-kaal: 7-day table", week is not None and week.group(1).count("<tr>") == 8)
    check("/hi/panchang/new-delhi canonicalises to /hi/panchang",
          canonical(client.get("/hi/panchang/new-delhi").text) == SITE + "/hi/panchang")

    print("\n2. hreflang pairs are reciprocal; every page has a language switch")
    pairs = [("/kundali-milan", "/hi/kundali-milan"), ("/free-kundali", "/hi/free-kundali")]
    for tool in TOOLS:
        for slug in ("new-delhi", "mumbai", "ayodhya", "puducherry"):
            city = seo_cities.BY_SLUG[slug]
            pairs.append((seo_pages._path(tool, city), seo_pages._path(tool, city, "hi")))
    bad = []
    for en, hi in pairs:
        h_en, h_hi = client.get(en).text, client.get(hi).text
        want = {"en": SITE + en, "hi": SITE + hi, "x-default": SITE + en}
        if not (alternates(h_en) == want == alternates(h_hi)
                and canonical(h_en) == SITE + en and canonical(h_hi) == SITE + hi
                and f'class="lang-switch" href="{hi}"' in h_en
                and f'class="lang-switch" href="{en}"' in h_hi):
            bad.append((en, alternates(h_en), alternates(h_hi)))
    check(f"hreflang en/hi/x-default identical on both copies, switch links ({len(pairs)} pairs)",
          not bad, str(bad[:2]))
    check("English pages keep lang=en-IN",
          '<html lang="en-IN">' in client.get("/panchang/mumbai").text)
    check("404 pages carry no hreflang (they have no twin)",
          not alternates(client.get("/hi/panchang/atlantis").text))

    print("\n3. Every city, every tool, both languages")
    errors, times = [], []
    for city in seo_cities.CITIES:
        for tool in TOOLS:
            for lang in ("en", "hi"):
                path = seo_pages._path(tool, city, lang)
                t0 = time.perf_counter()
                r = client.get(path)
                times.append((time.perf_counter() - t0, path))
                name = city.name_hi if lang == "hi" else city.name
                if r.status_code != 200 or name not in r.text or canonical(r.text) != SITE + path:
                    errors.append(f"{path} {r.status_code}")
    n = len(seo_cities.CITIES) * len(TOOLS) * 2
    check(f"all {n} city pages 200 with the city's name and own canonical", not errors,
          str(errors[:5]))
    cold = sorted(times, reverse=True)[0]
    print(f"     first render (engine cold): median {statistics.median(t for t, _ in times)*1000:.1f} ms,"
          f" slowest {cold[0]*1000:.0f} ms {cold[1]}")

    print("\n4. The city list")
    cities = seo_cities.CITIES
    check(f"about 100 cities ({len(cities)})", 90 <= len(cities) <= 130)
    check("slugs unique", len({c.slug for c in cities}) == len(cities))
    check("names unique", len({c.name for c in cities}) == len(cities)
          and len({c.name_hi for c in cities}) == len(cities))
    check("coordinates unique", len({(c.latitude, c.longitude) for c in cities}) == len(cities))
    outside = [c.slug for c in cities
               if not (6.5 <= c.latitude <= 35.7 and 68.0 <= c.longitude <= 97.5)]
    check("every city inside India's bounding box", not outside, str(outside))
    check("coordinates have at most 4 decimals", all(
        round(c.latitude, 4) == c.latitude and round(c.longitude, 4) == c.longitude
        for c in cities))
    check("every original DIVASTRO-100 slug still resolves (they are public URLs)",
          all(seo_cities.get(s) for s in ORIGINAL_SLUGS))
    check("default is still New Delhi", seo_cities.DEFAULT.slug == "new-delhi")
    check("every city has a Devanagari name", all(
        DEVANAGARI.search(c.name_hi) and not LATIN.search(c.name_hi) for c in cities))
    check("every state has a Hindi name", all(c.state in seo_cities.STATE_HI for c in cities))
    check("timezone is IST everywhere", {c.timezone for c in cities} == {"Asia/Kolkata"})
    groups = seo_cities.by_state()
    check("by_state covers every city once",
          sorted(c.slug for _, cs in groups for c in cs) == sorted(c.slug for c in cities))
    html = client.get("/panchang").text
    check("city index is grouped by state", html.count("<dt>") == len(groups)
          and "<dt>Uttar Pradesh</dt>" in html)
    check("Hindi city index uses Hindi state names",
          "<dt>उत्तर प्रदेश</dt>" in client.get("/hi/panchang").text)
    # Spot checks a typo would break: well-known cities at roughly the right place.
    known = {"new-delhi": (28.6, 77.2), "mumbai": (19.1, 72.9), "chennai": (13.1, 80.3),
             "ayodhya": (26.8, 82.2), "srinagar": (34.1, 74.8), "thiruvananthapuram": (8.5, 76.9),
             "kohima": (25.7, 94.1), "dwarka": (22.2, 69.0), "ujjain": (23.2, 75.8)}
    off = [s for s, (la, lo) in known.items()
           if abs(seo_cities.BY_SLUG[s].latitude - la) > 0.15
           or abs(seo_cities.BY_SLUG[s].longitude - lo) > 0.15]
    check("spot-checked cities are where they should be", not off, str(off))

    print("\n5. /free-kundali")
    for path, faq in (("/free-kundali", seo_pages.FAQ_EN), ("/hi/free-kundali", seo_pages.FAQ_HI)):
        must = (["Janam Kundali", "Lagna", "Vimshottari", "Navamsa", "North Indian", "South Indian",
                 "Manglik", "Sade Sati", "Kaal Sarp", "Lahiri", "How to read your kundali",
                 "Frequently asked questions"] if path == "/free-kundali" else [])
        html = common(path, path, path, must + ['class="cta big" href="/?open=kundali'])
        check(f"{path}: lists exactly the vargas the app shows",
              all(code in html for code in DEFAULT_DIVISIONS))
        graph = ld_graph(html)
        faqs = [n for n in graph if n.get("@type") == "FAQPage"]
        ok = len(faqs) == 1 and len(faqs[0]["mainEntity"]) == len(faq) >= 5 and all(
            q["@type"] == "Question" and q["acceptedAnswer"]["@type"] == "Answer"
            and q["acceptedAnswer"]["text"] for q in faqs[0]["mainEntity"])
        check(f"{path}: FAQPage JSON-LD, one Question per FAQ entry", ok)
        check(f"{path}: every marked-up question is visible on the page",
              ok and all(q["name"].replace("'", "&#x27;") in html for q in faqs[0]["mainEntity"]))
        text = main_text(html)
        check(f"{path}: substantial (> 700 words)", len(text.split()) > 700, str(len(text.split())))
    tools_js = (ROOT / "app" / "static" / "tools.js").read_text(encoding="utf-8")
    index = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
    check("tools.js maps ?open=kundali to the home CTA (the birth form)",
          re.search(r"kundali:\s*'#home-cta'", tools_js) is not None and 'id="home-cta"' in index)
    check("app.js honours ?lang= from the Hindi pages",
          'new URLSearchParams(location.search).get("lang")' in app_js)
    check("Hindi CTAs carry lang=hi", 'href="/?open=kundali&amp;lang=hi"'
          in client.get("/hi/free-kundali").text)

    print("\n6. Cross-links")
    for path in ("/panchang/mumbai", "/rahu-kaal", "/choghadiya/ayodhya", "/kundali-milan"):
        check(f"{path} links to /free-kundali", 'href="/free-kundali"' in client.get(path).text)
    for path in ("/hi/panchang/mumbai", "/hi/rahu-kaal", "/hi/choghadiya/ayodhya",
                 "/hi/kundali-milan"):
        check(f"{path} links to /hi/free-kundali",
              'href="/hi/free-kundali"' in client.get(path).text)
    html = client.get("/hi/panchang/mumbai").text
    check("Hindi pages link to Hindi city pages", 'href="/hi/panchang/ayodhya"' in html
          and 'href="/panchang/ayodhya"' not in html)

    print("\n7. Unknown and malformed URLs are 404s")
    for path in ("/hi/panchang/atlantis", "/hi/rahu-kaal/atlantis", "/hi/choghadiya/atlantis",
                 "/hi/kundali-milan/mumbai", "/free-kundali/mumbai", "/hi/free-kundali/x",
                 "/hi/rashi-unknown", "/hi/hi/panchang"):
        r = client.get(path)
        check(f"{path} is a 404", r.status_code == 404, str(r.status_code))
    r = client.get("/hi/panchang/atlantis")
    check("Hindi 404 is in Hindi and not cacheable",
          "शहर नहीं मिला" in r.text and r.headers.get("cache-control") == "no-store")

    print("\n8. sitemap.xml")
    r = client.get("/sitemap.xml")
    try:
        root = ET.fromstring(r.content)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [e.text for e in root.findall("s:url/s:loc", ns)]
        check("sitemap: valid XML", bool(locs))
    except ET.ParseError as exc:
        locs, root, ns = [], None, {}
        check("sitemap: valid XML", False, str(exc))
    want = {SITE + p for p in ("/free-kundali", "/hi/free-kundali", "/hi/kundali-milan",
                               "/hi/panchang", "/hi/rahu-kaal", "/hi/choghadiya")}
    want |= {SITE + seo_pages._path(t, c, lang) for t in TOOLS for c in seo_cities.CITIES
             for lang in ("en", "hi")}
    check("sitemap: every tool x city x language and the new explainers", want <= set(locs),
          str(sorted(want - set(locs))[:5]))
    check("sitemap: no duplicates, no non-canonical default-city URLs",
          len(locs) == len(set(locs)) and f"{SITE}/hi/panchang/new-delhi" not in locs)
    not_counted = [u for u in locs if not analytics.is_public_page(u.removeprefix(SITE) or "/")]
    check("sitemap: the visit beacon accepts every listed URL", not not_counted,
          str(not_counted[:5]))
    hi_daily = root.find(f"s:url[s:loc='{SITE}/hi/panchang/mumbai']", ns) if root is not None else None
    check("sitemap: Hindi tool pages marked daily",
          hi_daily is not None and hi_daily.find("s:changefreq", ns).text == "daily")
    sample = locs[:: max(1, len(locs) // 25)]
    bad = [u for u in sample if client.get(u.removeprefix(SITE) or "/").status_code != 200]
    check(f"sitemap: a sample of {len(sample)} listed URLs all return 200", not bad, str(bad))
    kinds: dict[str, int] = {}
    for u in locs:
        path = u.removeprefix(SITE)
        lang = "hi" if path.startswith("/hi/") else "en"
        bare = path.removeprefix("/hi") if lang == "hi" else path
        kind = bare.split("/")[1] or "home"
        kind = f"{kind}{'/<city>' if bare.count('/') > 1 else ''}"
        kinds[f"{lang} {kind}"] = kinds.get(f"{lang} {kind}", 0) + 1
    print(f"     {len(locs)} URLs: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))

    print("\n9. The visit beacon")
    for path in ("/hi/panchang", "/hi/panchang/ayodhya", "/hi/rahu-kaal/kohima",
                 "/hi/choghadiya", "/free-kundali", "/hi/free-kundali", "/hi/kundali-milan",
                 "/panchang/ayodhya"):
        check(f"beacon accepts {path}", analytics.is_public_page(path))
    for path in ("/hi", "/hi/", "/hi/terms", "/hi/kundali-milan/mumbai", "/hi/panchang/atlantis",
                 "/hi/hi/panchang", "/free-kundali/mumbai", "/hi/free-kundali/x", "/hindi/panchang"):
        check(f"beacon rejects {path}", not analytics.is_public_page(path))

    print("\n10. Hindi tables and formatting")
    check("YOGA_HI / KARANA_HI match main.py's copies",
          seo_pages.YOGA_HI == app_main.YOGA_HI and seo_pages.KARANA_HI == app_main.KARANA_HI)
    check("every engine yoga has a Hindi name",
          set(panchang_engine.YOGA_NAMES) <= set(seo_pages.YOGA_HI))
    check("every engine karana has a Hindi name",
          set(panchang_engine.MOVABLE_KARANAS + panchang_engine.FIXED_KARANAS)
          <= set(seo_pages.KARANA_HI))
    check("every tithi and nakshatra has a Hindi name",
          set(panchang_engine.TITHI_NAMES) | {"Amavasya"} <= set(TITHI_HI)
          and set(NAKSHATRAS) <= set(NAKSHATRAS_HI))
    check("Hindi koota text for exactly the eight kootas",
          set(seo_pages.KOOTAS_HI) == {k[0] for k in seo_pages.KOOTAS})
    ist = seo_pages.IST
    clocks = {(6, 29): "सुबह 6:29", (13, 5): "दोपहर 1:05", (18, 0): "शाम 6:00",
              (23, 10): "रात 11:10", (0, 30): "रात 12:30", (12, 0): "दोपहर 12:00"}
    got = {k: seo_pages._clock(dt.datetime(2026, 10, 3, *k, tzinfo=ist), "hi") for k in clocks}
    check("Hindi clock words", got == clocks, str(got))
    check("English clock unchanged",
          seo_pages._clock(dt.datetime(2026, 10, 3, 6, 29, tzinfo=ist)) == "6:29 AM")
    check("Hindi long date", seo_pages._long_date(dt.date(2026, 10, 3), "hi") == "3 अक्टूबर 2026")

    print("\n11. Render time (warm cache; the target is < 50 ms)")
    timed = ["/panchang", "/hi/panchang/mumbai", "/rahu-kaal/kolkata", "/hi/rahu-kaal/kolkata",
             "/choghadiya/chennai", "/hi/choghadiya/chennai", "/kundali-milan", "/hi/kundali-milan",
             "/free-kundali", "/hi/free-kundali", "/sitemap.xml"]
    results = {}
    for path in timed:
        client.get(path)
        runs = []
        for _ in range(5):
            t0 = time.perf_counter()
            client.get(path)
            runs.append(time.perf_counter() - t0)
        results[path] = statistics.median(runs) * 1000
    for path, ms in sorted(results.items(), key=lambda kv: -kv[1]):
        print(f"     {ms:6.1f} ms  {path}")
    check("every page renders in < 50 ms warm", max(results.values()) < 50,
          f"slowest {max(results.values()):.1f} ms")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("seo pages (hi / cities / free-kundali): all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
