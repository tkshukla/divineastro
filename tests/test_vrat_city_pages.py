"""City-specific festival timing pages (DIVASTRO-140).

/tyohar/<festival>-2026/<city> and /hi/... for the festivals whose timing is
location-dependent. Pins: the family exists for every listed festival x city in
English and Hindi; canonical is the page itself, hreflang is the en/hi pair, no
noindex; no two pages share a title, description, h1 or canonical; the times on
a page are the engine's for that city (asserted against astro.festivals, not
hard-coded) and differ between cities where the engine says they differ;
Event and FAQPage JSON-LD parse and carry the city's numbers; unknown city or
festival 404s (with a usable page), New Delhi redirects to the main page; the
sitemap and the visit beacon include the family, below the main pages in
priority; the main festival page lists the city pills.

No server needed. A throwaway SQLite database.

    ~/.venvs/divineastro/bin/python -u -m tests.test_vrat_city_pages
"""

from __future__ import annotations

import html as htmllib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_vrat_city_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, seo_cities, seo_pages, vrat_city_pages as vc, vrat_pages as vp  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
YEAR = vc.CITY_YEARS[0]


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def _meta(h: str, pat: str) -> str:
    m = re.search(pat, h, re.S)
    return htmllib.unescape(m.group(1)) if m else ""


def _title(h): return _meta(h, r"<title>(.*?)</title>")
def _desc(h): return _meta(h, r'<meta name="description" content="([^"]*)"')
def _canon(h): return _meta(h, r'<link rel="canonical" href="([^"]*)"')
def _h1(h): return _meta(h, r"<h1>(.*?)</h1>")


def _alts(h: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', h))


def _graph(h: str) -> list[dict]:
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    return json.loads(m.group(1))["@graph"] if m else []


def main() -> int:
    paths = vc.page_paths()
    n_fest, n_city = len(vc.FESTIVALS), len(vc.CITIES)

    print("1. The family")
    check("24 cities (the 25 listed minus New Delhi, which is the main page)", n_city == 24,
          str(n_city))
    check("every listed city exists in seo_cities", all(s in seo_cities.BY_SLUG for s in vc.CITY_SLUGS))
    check("festivals: the location-dependent ten", n_fest == 10, ", ".join(vc.FESTIVALS))
    check("paths = festivals x cities x 2 languages",
          len(paths) == n_fest * n_city * 2 and len(set(paths)) == len(paths), str(len(paths)))
    check("karwa-chauth in Bengaluru, en and hi, are in the family",
          "/tyohar/karwa-chauth-2026/bengaluru" in paths
          and "/hi/tyohar/karwa-chauth-2026/bengaluru" in paths)
    check("no New Delhi page, no regional-language path in the family",
          not any(p.endswith("/new-delhi") for p in paths)
          and all(p.startswith(("/tyohar/", "/hi/tyohar/")) for p in paths))

    print("2. Every page: 200, self-canonical, en/hi hreflang, indexable, JSON-LD")
    pages: dict[str, str] = {}
    # The family is rendered in-process (a TestClient request costs ~0.4 s of
    # portal start-up each; 480 of them would take ten minutes). The routes
    # themselves are exercised over HTTP for a sample of every festival and both
    # languages, then for every special case below.
    class _R:
        def __init__(self, resp):
            self.status_code, self.text = resp.status_code, resp.body.decode()
            self.headers = resp.headers

    def _lang_of(p):
        return "hi" if p.startswith("/hi/") else "en"

    for p in paths:
        slug_year, city_slug = p.split("/tyohar/")[1].split("/")
        slug, year = slug_year.rsplit("-", 1)
        r = _R(vc.render(slug, int(year), city_slug, _lang_of(p)))
        pages[p] = r.text
        h = r.text
        ok = r.status_code == 200 and _canon(h) == SITE + p
        alts = _alts(h)
        en = SITE + re.sub(r"^/hi", "", p)
        ok = ok and alts == {"en": en, "hi": SITE + "/hi" + re.sub(r"^/hi", "", p), "x-default": en}
        ok = ok and "noindex" not in h.lower() and "Cache-Control" in r.headers
        try:
            g = _graph(h)
            types = {x["@type"] for x in g}
            ok = ok and {"Event", "FAQPage", "BreadcrumbList", "WebPage"} <= types
        except Exception as exc:                       # noqa: BLE001
            ok = False
            print("   bad JSON-LD", p, exc)
        if not ok:
            check(f"{p} basics", False, f"{r.status_code} {_canon(h)} {alts}")
    check(f"all {len(paths)} pages: 200, self-canonical, en/hi hreflang, no noindex, Event+FAQPage",
          not [f for f in failures if f.endswith("basics")])

    sample = [p for p in paths if p.split("/")[-1] in ("bengaluru", "patna")][::3] + paths[:2]
    bad_http = [p for p in sample if client.get(p).text != pages[p]]
    check(f"HTTP routes serve the same HTML as render() ({len(sample)} sampled, en+hi)",
          not bad_http, str(bad_http[:2]))

    print("3. Distinct: title, description, h1, canonical")
    for field, fn in (("title", _title), ("description", _desc), ("h1", _h1), ("canonical", _canon)):
        vals = [fn(h) for h in pages.values()]
        check(f"{field}: {len(set(vals))} unique of {len(vals)}, none empty",
              len(set(vals)) == len(vals) and all(vals))
    bad = [p for p, h in pages.items() if not (
        vc.FESTIVALS[p.split("/tyohar/")[1].rsplit("-2026", 1)[0]]["name"][1 if p.startswith("/hi") else 0]
        in _h1(h) and str(YEAR) in _h1(h)
        and seo_cities.city_name(seo_cities.BY_SLUG[p.rsplit("/", 1)[1]],
                                 "hi" if p.startswith("/hi") else "en") in _h1(h))]
    check("every h1 carries festival, year and the city's own name", not bad, str(bad[:3]))
    long_ = [p for p, h in pages.items() if len(_desc(h)) > 320]
    check("descriptions stay under 320 characters", not long_, str(long_[:2]))

    print("4. The times are the engine's, and differ between cities")
    wrong = []
    for p, h in pages.items():
        lang = "hi" if p.startswith("/hi") else "en"
        slug = p.split("/tyohar/")[1].rsplit("-2026", 1)[0]
        city = seo_cities.BY_SLUG[p.rsplit("/", 1)[1]]
        o = vc.observance(slug, YEAR, city)
        text = htmllib.unescape(re.sub(r"<[^>]+>", " ", h))
        for t in o["timings"]:
            if vp._timing_text(t, vp._date(o), lang) not in text:
                wrong.append((p, t["key"]))
    check("every engine timing for the city is printed verbatim", not wrong, str(wrong[:3]))

    blr = vc.observance("karwa-chauth", YEAR, seo_cities.BY_SLUG["bengaluru"])
    dl = vc.observance("karwa-chauth", YEAR, vc.BASE)
    m_b = next(t for t in blr["timings"] if t["key"] == "moonrise")["at"]
    m_d = next(t for t in dl["timings"] if t["key"] == "moonrise")["at"]
    check("engine: Karwa Chauth moonrise Bengaluru != New Delhi", m_b != m_d, f"{m_b} {m_d}")
    h = pages["/tyohar/karwa-chauth-2026/bengaluru"]
    check("the Bengaluru page prints Bengaluru's moonrise, not Delhi's",
          vp._clock(m_b, vp._date(blr), "en") in _title(h)
          and vp._clock(m_d, vp._date(dl), "en") not in _title(h))
    delta = int((vc._minute(m_b) - vc._minute(m_d)).total_seconds() // 60)
    check("'how this differs from Delhi' states the engine's minute difference",
          f"{delta} minutes later than the New Delhi time" in htmllib.unescape(h), str(delta))
    for slug in vc.FESTIVALS:
        key = vc.FESTIVALS[slug]["lead"][0]
        vals = set()
        for c in vc.CITIES:
            t = vc._timing(vc.observance(slug, YEAR, c), key)
            vals.add(t.get("at") or t["start"])
        check(f"{slug}: the headline time differs across the 24 cities (>= 20 distinct)",
              len(vals) >= 20, str(len(vals)))

    print("5. JSON-LD carries the city's numbers")
    h = pages["/tyohar/karwa-chauth-2026/bengaluru"]
    g = _graph(h)
    ev = next(x for x in g if x["@type"] == "Event")
    faq = next(x for x in g if x["@type"] == "FAQPage")
    qs = [q["name"] for q in faq["mainEntity"]]
    check("Event: city, own url, start/end dates, Place + address",
          "Bengaluru" in ev["name"] and ev["url"] == SITE + "/tyohar/karwa-chauth-2026/bengaluru"
          and ev["startDate"] and ev["endDate"] and ev["location"]["@type"] == "Place"
          and ev["location"]["address"]["addressLocality"] == "Bengaluru"
          and ev["startDate"][:10] == blr["date"], str(ev)[:200])
    check("FAQPage: 'What time is moonrise in Bengaluru on Karwa Chauth 2026?'",
          "What time is moonrise in Bengaluru on Karwa Chauth 2026?" in qs, str(qs))
    ans = next(q["acceptedAnswer"]["text"] for q in faq["mainEntity"] if "moonrise" in q["name"])
    check("... answered with Bengaluru's engine moonrise", vp._clock(m_b, vp._date(blr), "en") in ans, ans)
    visible = htmllib.unescape(re.sub(r"<[^>]+>", " ", h))
    check("every FAQ answer is printed on the page", all(q["acceptedAnswer"]["text"] in visible
                                                         for q in faq["mainEntity"]))
    hi = pages["/hi/tyohar/karwa-chauth-2026/mumbai"]
    check("Hindi page: Devanagari h1, Hindi FAQ question",
          re.search(r"[ऀ-ॿ]", _h1(hi)) and any("मुंबई में करवा चौथ 2026 पर चांद कब निकलेगा?" == q["name"]
                                              for q in next(x for x in _graph(hi)
                                                            if x["@type"] == "FAQPage")["mainEntity"]))

    print("6. Links")
    h = pages["/tyohar/diwali-2026/mumbai"]
    links = set(re.findall(r'href="([^"]+)"', h))
    near = [l for l in links if l.startswith("/tyohar/diwali-2026/") and not l.endswith("mumbai")]
    check("main festival page, the city's hub and 6-8 nearby city variants linked",
          "/tyohar/diwali-2026" in links and "/vrat-tyohar/mumbai" in links
          and 6 <= len(near) + 1 <= 8, f"{len(near)} {near}")
    check("the city's other nine festivals are linked",
          all(f"/tyohar/{s}-2026/mumbai" in links for s in vc.FESTIVALS if s != "diwali"))
    check("shared shell: stay-in-touch strip and footer present",
          "Stay in touch" in h and "/privacy" in h)
    main_h = client.get("/tyohar/karwa-chauth-2026").text
    pills = [l for l in re.findall(r'href="(/tyohar/karwa-chauth-2026/[^"]+)"', main_h)]
    check("main festival page: 'Timings for your city' lists the 24 cities",
          "Timings for your city" in main_h and len(set(pills)) == 24, str(len(set(pills))))
    check("main Hindi page too; Holi (no city pages) has none",
          len(set(re.findall(r'href="(/hi/tyohar/karwa-chauth-2026/[^"]+)"',
                             client.get("/hi/tyohar/karwa-chauth-2026").text))) == 24
          and "/tyohar/holi-2026/" not in client.get("/tyohar/holi-2026").text)

    print("7. 404s and redirect")
    for bad_path in ("/tyohar/karwa-chauth-2026/atlantis", "/tyohar/holi-2026/mumbai",
                     "/tyohar/nonsense-2026/mumbai", "/tyohar/karwa-chauth-2027/mumbai",
                     "/tyohar/karwa-chauth/mumbai", "/hi/tyohar/karwa-chauth-2026/atlantis"):
        r = client.get(bad_path)
        check(f"{bad_path}: 404 with a usable page",
              r.status_code == 404 and "<h1>" in r.text and "/vrat-tyohar" in r.text, str(r.status_code))
    r = client.get("/tyohar/karwa-chauth-2026/new-delhi", follow_redirects=False)
    check("New Delhi redirects (301) to the main festival page",
          r.status_code == 301 and r.headers["location"] == "/tyohar/karwa-chauth-2026")
    r = client.get("/hi/tyohar/karwa-chauth-2026/new-delhi", follow_redirects=False)
    check("... and /hi/ to /hi/", r.status_code == 301
          and r.headers["location"] == "/hi/tyohar/karwa-chauth-2026")
    r = client.get("/kn/tyohar/diwali-2026/mumbai")
    check("a regional copy renders but is noindex with no hreflang",
          r.status_code == 200 and "noindex" in r.text and not _alts(r.text))

    print("8. Sitemap and beacon")
    sm = set(seo_pages.sitemap_paths())
    check("sitemap_paths includes every family page", set(paths) <= sm)
    xml = client.get("/sitemap.xml").text
    check("sitemap.xml lists them", all(SITE + p in xml for p in paths[:5] + paths[-5:]))
    check("priority below the main festival pages",
          seo_pages.sitemap_priority("/tyohar/diwali-2026/mumbai") < seo_pages.sitemap_priority(
              "/tyohar/diwali-2026")
          and seo_pages.sitemap_priority("/hi/tyohar/diwali-2026/mumbai") < seo_pages.sitemap_priority(
              "/hi/tyohar/diwali-2026"))
    check("visit beacon accepts them, rejects strangers",
          all(analytics.is_public_page(p) for p in paths[:3] + paths[-3:])
          and not analytics.is_public_page("/tyohar/diwali-2026/atlantis")
          and not analytics.is_public_page("/tyohar/holi-2026/mumbai"))

    print()
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print("vrat city pages: all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
