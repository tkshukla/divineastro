"""The server-rendered tool pages, sitemap.xml and robots.txt (DIVASTRO-100).

The whole point of these pages is that the content is in the raw HTML, so
every check here reads the HTML exactly as a crawler gets it — no browser, no
script. It also pins the pieces that fail silently: a canonical URL that points
at the wrong copy, a sitemap that is not valid XML, a CTA into the app whose
?open= key tools.js does not know, an AdSense id that drifted from index.html.

No server needed (FastAPI's in-process client). A throwaway SQLite database is
used — never a real one.

    ~/.venvs/divineastro/bin/python -u -m tests.test_seo_pages
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_seo_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, seo_cities, seo_pages  # noqa: E402
from app.astro import matching  # noqa: E402
from app.astro import panchang as panchang_engine  # noqa: E402
from app.main import ADSENSE_PUBLISHER, app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []

SITE = seo_pages.SITE_URL
TIME = re.compile(r"\b(1[0-2]|[1-9]):[0-5]\d (AM|PM)\b")
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
TODAY = dt.datetime.now(ZoneInfo("Asia/Kolkata")).date()


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def canonical(html: str) -> str | None:
    m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    return m.group(1) if m else None


def title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    return m.group(1) if m else ""


def common(label: str, path: str, want_canonical: str, must: list[str]) -> str:
    """The checks every page shares. Returns the HTML for page-specific ones."""
    r = client.get(path)
    html = r.text
    check(f"{label}: 200 text/html",
          r.status_code == 200 and r.headers["content-type"].startswith("text/html"),
          f"{r.status_code} {r.headers.get('content-type')}")
    for needle in must:
        check(f"{label}: raw HTML contains {needle!r}", needle in html)
    check(f"{label}: canonical is {want_canonical}", canonical(html) == SITE + want_canonical,
          str(canonical(html)))
    check(f"{label}: loads the visit beacon", 'src="/static/visit.js"' in html)
    check(f"{label}: beacon accepts this path",
          analytics.is_public_page(path.rstrip("/") or "/"))
    check(f"{label}: has a meta description",
          bool(re.search(r'<meta name="description" content="[^"]{60,}"', html)))
    for prop in ("og:title", "og:description", "og:url", "og:image"):
        check(f"{label}: has {prop}", f'property="{prop}"' in html)
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    try:
        types = {node["@type"] for node in json.loads(m.group(1))["@graph"]} if m else set()
    except (ValueError, KeyError) as exc:
        types = {f"unparseable: {exc}"}
    check(f"{label}: JSON-LD WebPage + BreadcrumbList", {"WebPage", "BreadcrumbList"} <= types,
          str(types))
    check(f"{label}: AdSense head snippet",
          f'content="ca-{ADSENSE_PUBLISHER}"' in html
          and f"adsbygoogle.js?client=ca-{ADSENSE_PUBLISHER}" in html)
    check(f"{label}: favicon", 'rel="icon"' in html)
    for link in ("/terms", "/privacy", "/refund", "/contact"):
        check(f"{label}: footer links {link}", f'href="{link}"' in html)
    check(f"{label}: has a Hindi line", bool(DEVANAGARI.search(html)))
    check(f"{label}: CTA into the app", 'class="cta" href="/?open=' in html)
    cache = r.headers.get("cache-control", "")
    m = re.search(r"max-age=(\d+)", cache)
    check(f"{label}: short, private cache", "private" in cache and m and 0 < int(m.group(1)) <= 1800,
          cache)
    return html


def main() -> int:
    print("\n1. Panchang")
    html = common("/panchang", "/panchang", "/panchang",
                  ["Today's Panchang in New Delhi", "Tithi", "Nakshatra", "Yoga", "Karana",
                   "Sunrise", "Moonrise", "Rahu Kaal", "Yamaganda", "Gulika", "Abhijit"])
    check("/panchang: has clock times", len(TIME.findall(html)) >= 8)
    check("/panchang: shows today's IST date", f"{TODAY.day} {TODAY.strftime('%B %Y')}" in html)
    expected = panchang_engine.daily_panchang(TODAY, 28.6139, 77.2090, "Asia/Kolkata")
    check("/panchang: tithi and nakshatra match the engine",
          expected["summary"]["tithi"] in html and expected["summary"]["nakshatra"] in html)
    html = common("/panchang/mumbai", "/panchang/mumbai", "/panchang/mumbai",
                  ["Today's Panchang in Mumbai", "मुंबई", "Rahu Kaal"])
    check("titles are unique per city", title(html) != title(client.get("/panchang").text))
    html = client.get("/panchang/new-delhi").text
    check("/panchang/new-delhi canonicalises to /panchang (one page, not two)",
          canonical(html) == SITE + "/panchang", str(canonical(html)))

    print("\n2. Rahu Kaal")
    html = common("/rahu-kaal/kolkata", "/rahu-kaal/kolkata", "/rahu-kaal/kolkata",
                  ["Rahu Kaal Today in Kolkata", "What is Rahu Kaal?", "Yamaganda", "this week"])
    week = re.search(r"this week</h2>(.*?)</table>", html, re.S)
    check("/rahu-kaal: 7-day table", week is not None and week.group(1).count("<tr>") == 8)
    common("/rahu-kaal", "/rahu-kaal", "/rahu-kaal", ["Rahu Kaal Today in New Delhi"])

    print("\n3. Choghadiya")
    html = common("/choghadiya/chennai", "/choghadiya/chennai", "/choghadiya/chennai",
                  ["Choghadiya Today in Chennai", "Day Choghadiya", "Night Choghadiya",
                   "Amrit", "Labh"])
    check("/choghadiya: 16 slots", html.count("<tr><td>") == 16, str(html.count("<tr><td>")))
    common("/choghadiya", "/choghadiya", "/choghadiya", ["Choghadiya Today in New Delhi"])

    # The slots must be cut at the ephemeris sunrise (same as the panchang page)
    # and follow choghadiya.py's weekday sequences. 30 Aug 2026 is a Sunday.
    p = panchang_engine.daily_panchang("2026-08-30", 28.6139, 77.2090, "Asia/Kolkata")
    day, night = seo_pages.choghadiya_slots(p)
    check("choghadiya: Sunday starts Udveg by day, Shubh by night",
          day[0]["name"] == "Udveg" and night[0]["name"] == "Shubh")
    check("choghadiya: day starts at the panchang's sunrise",
          day[0]["start"] == dt.datetime.fromisoformat(p["sun"]["rise"]))
    check("choghadiya: slots are contiguous to the next sunrise",
          all(a["end"] == b["start"] for a, b in zip(day + night, (day + night)[1:]))
          and night[-1]["end"] == dt.datetime.fromisoformat(p["sun"]["next_rise"]))

    print("\n4. Kundali Milan")
    html = common("/kundali-milan", "/kundali-milan", "/kundali-milan",
                  ["Ashtakoot", "Nadi", "Bhakoot", "Mangal Dosha", "36", "/?open=milan"])
    check("kootas add up to the engine's maximum",
          sum(k[2] for k in seo_pages.KOOTAS) == matching.MAXIMUM_POINTS)
    check("kootas are the engine's eight",
          {k[0] for k in seo_pages.KOOTAS} == set(matching.KOOTA_LABELS_HI))
    check("score bands come from the engine (18–24, 25–32, 33–36)",
          all(b in html for b in ("Below 18", "18–24", "25–32", "33–36")))

    print("\n5. Unknown cities")
    for tool in ("panchang", "rahu-kaal", "choghadiya"):
        r = client.get(f"/{tool}/atlantis")
        check(f"/{tool}/atlantis is a 404", r.status_code == 404, str(r.status_code))
        check(f"/{tool}/atlantis is not cacheable", r.headers.get("cache-control") == "no-store")
    check("every curated city resolves", all(
        client.get(f"/panchang/{c.slug}").status_code == 200 for c in seo_cities.CITIES))
    check("city list is a sensible size, slugs unique",
          25 <= len(seo_cities.CITIES) <= 40
          and len(seo_cities.BY_SLUG) == len(seo_cities.CITIES))
    check("slugs are URL-safe", all(re.fullmatch(r"[a-z]+(-[a-z]+)*", c.slug)
                                    for c in seo_cities.CITIES))

    print("\n6. sitemap.xml and robots.txt")
    r = client.get("/sitemap.xml")
    check("sitemap: 200 application/xml",
          r.status_code == 200 and r.headers["content-type"].startswith("application/xml"))
    try:
        root = ET.fromstring(r.content)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [e.text for e in root.findall("s:url/s:loc", ns)]
        check("sitemap: valid XML in the sitemap namespace", bool(locs))
    except ET.ParseError as exc:
        locs = []
        check("sitemap: valid XML in the sitemap namespace", False, str(exc))
    want = {SITE + p for p in ("/", "/terms", "/privacy", "/refund", "/contact",
                               "/kundali-milan", "/panchang", "/rahu-kaal", "/choghadiya")}
    want |= {f"{SITE}/{t}/{c.slug}" for t in seo_pages.TOOLS for c in seo_cities.CITIES
             if c != seo_cities.DEFAULT}
    check("sitemap: lists home, legal pages and every tool×city", want <= set(locs),
          str(sorted(want - set(locs))[:5]))
    check("sitemap: no duplicate or non-canonical URLs",
          len(locs) == len(set(locs)) and f"{SITE}/panchang/new-delhi" not in locs)
    bad = [u for u in locs[:: max(1, len(locs) // 15)]
           if client.get(u.removeprefix(SITE) or "/").status_code != 200]
    check("sitemap: a sample of listed URLs all return 200", not bad, str(bad))

    r = client.get("/robots.txt")
    body = r.text
    check("robots: 200 text/plain",
          r.status_code == 200 and r.headers["content-type"].startswith("text/plain"))
    check("robots: Sitemap line", f"Sitemap: {SITE}/sitemap.xml" in body)
    check("robots: disallows /api/ and /admin",
          "Disallow: /api/" in body and "Disallow: /admin" in body)

    print("\n7. Nothing existing was shadowed")
    r = client.get("/api/panchang", params={"latitude": 28.6, "longitude": 77.2})
    check("/api/panchang is still the JSON API",
          r.status_code == 200 and r.headers["content-type"].startswith("application/json"))
    r = client.get("/")
    check("/ is still the app shell", r.status_code == 200 and 'id="open-panchang"' in r.text)
    check("/terms still served", client.get("/terms").status_code == 200)

    print("\n8. The app's deep links")
    tools_js = (ROOT / "app" / "static" / "tools.js").read_text(encoding="utf-8")
    index = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    block = re.search(r"const DEEP_LINKS = \{(.*?)\};", tools_js, re.S)
    keys = dict(re.findall(r"'?([\w-]+)'?:\s*'#([\w-]+)'", block.group(1))) if block else {}
    check("tools.js has a ?open= table", bool(keys), str(keys))
    check("every deep link targets a real home-page card",
          all(f'id="{target}"' in index for target in keys.values()), str(keys))
    used = set()
    for path in ("/panchang", "/rahu-kaal", "/choghadiya", "/kundali-milan"):
        used |= set(re.findall(r'href="/\?open=([\w-]+)"', client.get(path).text))
    check("every ?open= the pages use is one tools.js handles",
          {"panchang", "choghadiya", "milan"} <= used <= set(keys),
          f"used {sorted(used)}, unhandled {sorted(used - set(keys))}")
    check("AdSense id matches index.html", f"client=ca-{ADSENSE_PUBLISHER}" in index
          and seo_pages.ADSENSE_CLIENT == f"ca-{ADSENSE_PUBLISHER}")

    for bad in ("/panchang/atlantis", "/kundali-milan/mumbai", "/rahu-kaal/x/y", "/sitemap.xml"):
        check(f"beacon rejects {bad}", not analytics.is_public_page(bad))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("seo pages: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
