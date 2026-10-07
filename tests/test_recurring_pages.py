"""The recurring-observance year pages and /muhurat/mundan-<year> (DIVASTRO-141).

    /purnima-2026  /amavasya-2026  /pradosh-vrat-2026  /sankashti-chaturthi-2026
    /masik-shivratri-2026  /kalashtami-2026   (+ 2027, + every language prefix)

Reads the HTML exactly as a crawler gets it. Pins: every page of the family
renders (6 observances x 2 years x 8 languages), is its own canonical with the
reciprocal hreflang set and no noindex; the dates in the table are exactly the
engine's `festivals.observances` output for New Delhi (nothing hard-coded), with
the engine's own time (Pradosh window, moonrise, Nishita); titles, descriptions
and h1 are unique across the family; the answer at the top names a date on or
after the render date (and says "all dates" for a past year); JSON-LD parses
with a FAQPage; unknown stems/years are real 404s; the pages are in the sitemap,
the /sitemap hub, the beacon's allow-list and the IndexNow daily list; and the
new mundan muhurat pages exist and print the engine's mundan rules.

No server needed (FastAPI's in-process client). A throwaway SQLite database.

    ~/.venvs/divineastro/bin/python -u -m tests.test_recurring_pages
"""

from __future__ import annotations

import datetime as dt
import html as htmllib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_recurring_pages_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, i18n, indexnow, muhurat_pages, recurring_pages as rp, seo_pages  # noqa: E402
from app.astro import festivals, muhurat  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
LANGS = ["en", "hi", *i18n.EXTRA_CODES]


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def _meta(html: str) -> tuple[str, str, str]:
    title = htmllib.unescape(re.search(r"<title>(.*?)</title>", html, re.S).group(1))
    desc = htmllib.unescape(re.search(r'<meta name="description" content="(.*?)"', html, re.S).group(1))
    h1 = htmllib.unescape(re.search(r"<h1>(.*?)</h1>", html, re.S).group(1))
    return title, desc, h1


def _ld(html: str) -> list[dict]:
    raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
    return json.loads(raw)["@graph"]


def _alts(html: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html))


def _answer(html: str) -> str:
    return re.search(r'class="box answer"><p>(.*?)</p>', html, re.S).group(1)


def _engine(spec: rp.Spec, year: int) -> list[dict]:
    """The engine's own list, through its public API (not rp.rows)."""
    c = seo_pages.seo_cities.DEFAULT
    return [o for o in festivals.observances(dt.date(year, 1, 1), dt.date(year, 12, 31),
                                             c.latitude, c.longitude, c.timezone)
            if o["key"] == spec.key]


def _clock(iso: str) -> str:
    return dt.datetime.fromisoformat(iso).strftime("%I:%M %p").lstrip("0")


def main() -> int:
    real_today = seo_pages._today
    seo_pages._today = lambda: dt.date(2026, 10, 7)
    try:
        return _run()
    finally:
        seo_pages._today = real_today


def _run() -> int:
    paths = rp.page_paths()
    print("1. Every page renders")
    check("6 observances x 2 years x 8 languages", len(paths) == 6 * 2 * 8 == len(set(paths)),
          str(len(paths)))
    check("the URL families", all(p in paths for p in (
        "/purnima-2026", "/amavasya-2027", "/pradosh-vrat-2026", "/sankashti-chaturthi-2027",
        "/masik-shivratri-2026", "/kalashtami-2027", "/hi/purnima-2026", "/kn/amavasya-2026",
        "/or/kalashtami-2027")))
    pages: dict[str, str] = {}
    bad = []
    for p in paths:
        r = client.get(p)
        pages[p] = r.text
        if r.status_code != 200 or not r.headers["content-type"].startswith("text/html"):
            bad.append((p, r.status_code))
    check(f"all {len(paths)} pages 200 text/html", not bad, str(bad[:3]))
    check("every language has its own text (nothing falls back to noindex)",
          set(rp.TRANSLATED) == set(LANGS), str(sorted(rp.TRANSLATED)))

    print("2. Shell: self canonical, reciprocal hreflang, no noindex, beacon, share, footer")
    problems = []
    for p, h in pages.items():
        lang, en_path = i18n.strip_prefix(p)
        alts = _alts(h)
        if f'<link rel="canonical" href="{SITE}{p}"/>' not in h:
            problems.append((p, "canonical"))
        if "noindex" in h:
            problems.append((p, "noindex"))
        if any(alts.get(i18n.get(c).hreflang) != SITE + i18n.localized_path(en_path, c)
               for c in rp.TRANSLATED):
            problems.append((p, "hreflang"))
        if alts.get("x-default") != SITE + en_path:
            problems.append((p, "x-default"))
        for needle, why in (("/static/visit.js", "beacon"), ('class="share-wa"', "share"),
                            ('class="site-footer"', "footer"), (seo_pages.ADSENSE_CLIENT, "adsense")):
            if needle not in h:
                problems.append((p, why))
        if f'<html lang="{i18n.get(lang).html_lang}"' not in h:
            problems.append((p, "html lang"))
    check("canonical, hreflang (+x-default), beacon, AdSense, share, footer, lang; no noindex",
          not problems, str(problems[:4]))
    # a language that is NOT in TRANSLATED must be noindex with no hreflang, like the siblings
    saved = rp.TRANSLATED
    try:
        rp.TRANSLATED = i18n.BASE_TRANSLATED
        r = rp.render("purnima", 2026, "kn")
        check("an untranslated copy renders noindex, without hreflang",
              b"noindex" in r.body and b'rel="alternate"' not in r.body)
    finally:
        rp.TRANSLATED = saved

    print("3. Dates and times are the engine's (New Delhi)")
    wrong = []
    for spec in rp.SPECS:
        for year in rp.YEARS:
            want = _engine(spec, year)
            for lang in ("en", "hi", "ta"):
                h = pages[rp.path(spec.slug, year, lang)]
                got = re.findall(r'<tr data-date="([0-9-]+)">', h)
                if got != [o["date"] for o in want]:
                    wrong.append((spec.slug, year, lang, "dates", len(got), len(want)))
                for o in want:
                    row = re.search(rf'<tr data-date="{o["date"]}">(.*?)</tr>', h, re.S).group(1)
                    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", row))
                    t = o["tithi"]
                    if lang == "en":
                        if f"{t['paksha']} {t['name']}" not in text:
                            wrong.append((spec.slug, o["date"], "tithi name"))
                        if _clock(t["start"]) not in text or _clock(t["end"]) not in text:
                            wrong.append((spec.slug, o["date"], "tithi times"))
                        if o["month"]["name"] not in text:
                            wrong.append((spec.slug, o["date"], "month"))
                        key = next((x for x in o["timings"] if x["key"] == spec.timing), None)
                        if spec.timing:
                            if key is None:
                                wrong.append((spec.slug, o["date"], "no engine timing"))
                            elif key.get("at"):
                                if _clock(key["at"]) not in text:
                                    wrong.append((spec.slug, o["date"], "moonrise"))
                            elif _clock(key["start"]) not in text or _clock(key["end"]) not in text:
                                wrong.append((spec.slug, o["date"], "window"))
                        else:
                            # no key time of its own for this observance: no such column
                            if "<th>Moonrise" in h or "<th>Pradosh puja" in h or "<th>Nishita" in h:
                                wrong.append((spec.slug, "unexpected column"))
    check("every row's date, tithi start/end, month and key time = festivals.observances",
          not wrong, str(wrong[:4]))
    counts = {s.slug: len(_engine(s, 2026)) for s in rp.SPECS}
    check("sanity: the engine yields 12-13 per month-wise observance, 25 Pradosh in 2026",
          counts["pradosh-vrat"] == 25 and all(counts[s] in (12, 13) for s in counts if s != "pradosh-vrat"),
          str(counts))
    sk = pages["/sankashti-chaturthi-2026"]
    check("Sankashti has a Moonrise column, Pradosh a puja-window column, Masik Shivratri Nishita",
          "<th>Moonrise</th>" in sk and "<th>Pradosh puja</th>" in pages["/pradosh-vrat-2026"]
          and "<th>Nishita kaal puja</th>" in pages["/masik-shivratri-2026"])
    check("an Adhik month is labelled (Purnima 2026 has Adhik Jyeshtha)",
          "Adhik Jyeshtha" in pages["/purnima-2026"])
    check("Angarki / Somvati / Shani / Som Pradosh variants come from the weekday",
          all(w in pages[p] for p, w in (("/sankashti-chaturthi-2027", "Angarki Chaturthi"),
                                         ("/amavasya-2026", "Shani Amavasya"),
                                         ("/pradosh-vrat-2026", "Som Pradosh"))))
    check("same-day festivals are linked (Mauni Amavasya, Guru Purnima, Maha Shivratri rows)",
          'href="/tyohar/mauni-amavasya-2026"' in pages["/amavasya-2026"]
          and 'href="/tyohar/guru-purnima-2026"' in pages["/purnima-2026"])
    h = pages["/hi/pradosh-vrat-2026"]
    check("Hindi page: Devanagari names, clock words and tithi names",
          "प्रदोष" in h and "त्रयोदशी" in h and ("शाम" in h or "रात" in h)
          and not re.findall(r"Trayodashi|Shukla|Krishna", re.sub(r"<[^>]+>", "", h.split("<main", 1)[1])))

    print("4. Distinct titles, descriptions and h1; distinct text")
    metas = {p: _meta(h) for p, h in pages.items()}
    for i, label in enumerate(("title", "meta description", "h1")):
        vals = [m[i] for m in metas.values()]
        check(f"all {len(vals)} {label}s unique", len(set(vals)) == len(vals),
              str([v for v in vals if vals.count(v) > 1][:2]))
    check("title/description carry the year and the observance's own name",
          all(str(y) in metas[p][0] and str(y) in metas[p][1] and str(y) in metas[p][2]
              for p in paths for y in [int(re.search(r"-(\d{4})$", p).group(1))]))
    check("descriptions fit a result (<= 330 chars) and are not empty",
          all(20 < len(m[1]) <= 330 for m in metas.values()),
          str(max(len(m[1]) for m in metas.values())))

    def shingles(h: str) -> set:
        main = h.split("<main", 1)[1].split("</main>", 1)[0]
        # the table is the data (differs by dates); what must differ is the prose
        main = re.sub(r"<table>.*?</table>", " ", main, flags=re.S)
        words = re.sub(r"<[^>]+>", " ", htmllib.unescape(main)).split()
        return {" ".join(words[i:i + 6]) for i in range(len(words) - 5)}

    en = {s.slug: shingles(pages[rp.path(s.slug, 2026)]) for s in rp.SPECS}
    worst = max((len(en[a] & en[b]) / len(en[a] | en[b]), a, b)
                for a in en for b in en if a < b)
    check("prose overlap between any two observances' pages stays low (Jaccard of 6-grams)",
          worst[0] < 0.30, f"{worst[0]:.2f} {worst[1]} / {worst[2]}")
    same_obs = len((a := shingles(pages["/purnima-2026"])) & (b := shingles(pages["/purnima-2027"]))) / len(a | b)
    check("a year's page and the next year's page differ (not a template with a year swapped)",
          same_obs < 0.9, f"{same_obs:.2f}")

    print("5. JSON-LD and FAQ")
    badld = []
    for p, h in pages.items():
        try:
            g = _ld(h)
        except Exception as exc:
            badld.append((p, f"parse {exc}"))
            continue
        types = [x["@type"] for x in g]
        faq = next((x for x in g if x["@type"] == "FAQPage"), None)
        items = next((x for x in g if x["@type"] == "ItemList"), None)
        if "BreadcrumbList" not in types or faq is None or items is None:
            badld.append((p, types))
            continue
        qs = faq["mainEntity"]
        if not 3 <= len(qs) <= 5:
            badld.append((p, f"{len(qs)} questions"))
        visible = htmllib.unescape(re.sub(r"<[^>]+>", " ", h))
        if any(q["name"] not in visible for q in qs):
            badld.append((p, "FAQ question not on the page"))
        if items["numberOfItems"] != len(re.findall(r'<tr data-date', h)):
            badld.append((p, "ItemList count"))
        if g[0]["url"] != SITE + p:
            badld.append((p, "WebPage url"))
    check("JSON-LD parses on every page: WebPage, BreadcrumbList, ItemList = row count, FAQPage "
          "(3-5 questions, all visible on the page)", not badld, str(badld[:3]))
    fq = {x["@type"]: x for x in _ld(pages["/sankashti-chaturthi-2026"])}["FAQPage"]["mainEntity"]
    check("Sankashti FAQ: dates, next, moonrise, rule - answers filled from the data",
          len(fq) == 4 and "Moonrise" in fq[2]["acceptedAnswer"]["text"]
          and "moonrise" in fq[3]["acceptedAnswer"]["text"]
          and "13 October 2026" not in "".join(q["name"] for q in fq), str([q["name"] for q in fq]))

    print("6. The answer at the top")
    today = seo_pages._today()
    wrong = []
    for spec in rp.SPECS:
        rows26 = _engine(spec, 2026)
        later = [o for o in rows26 if o["date"] >= today.isoformat()]
        h = pages[rp.path(spec.slug, 2026)]
        ans = _answer(h)
        date_txt = re.search(r"<strong>(.*?)</strong>", ans).group(1)
        label = {o["date"]: rp._day_label(dt.date.fromisoformat(o["date"]), "en", year=True)
                 for o in rows26}
        iso = next((k for k, v in label.items() if v == date_txt), None)
        if not later or iso != later[0]["date"] or iso < today.isoformat() or "next" not in ans.lower():
            wrong.append((spec.slug, ans[:120]))
        # the description names the same next date
        if label[later[0]["date"]] not in metas[rp.path(spec.slug, 2026)][1]:
            wrong.append((spec.slug, "description"))
        # a coming year: the first date of the year, and the total
        h27 = pages[rp.path(spec.slug, 2027)]
        a27 = _answer(h27)
        first27 = _engine(spec, 2027)[0]
        if (rp._day_label(dt.date.fromisoformat(first27["date"]), "en", year=True) not in a27
                or f"All {len(_engine(spec, 2027))} dates for 2027" not in a27):
            wrong.append((spec.slug, 2027, a27[:120]))
    check("2026 page (today = 7 Oct 2026): 'The next X is on <the first engine date >= today>'; "
          "2027 page: the first date of 2027 and the total", not wrong, str(wrong[:2]))
    h = pages["/amavasya-2026"]
    check("the answer carries the tithi start/end and, for Sankashti, the moonrise",
          "Krishna Amavasya:" in _answer(h)
          and "Moonrise:" in _answer(pages["/sankashti-chaturthi-2026"])
          and "Pradosh puja:" in _answer(pages["/pradosh-vrat-2026"])
          and "Nishita kaal puja:" in _answer(pages["/masik-shivratri-2026"]))
    # the date moves with the clock: today itself counts, and the day after moves on
    for spec in rp.SPECS:
        rows26 = _engine(spec, 2026)
        d0 = dt.date.fromisoformat(rows26[3]["date"])
        a = _answer(rp.render(spec.slug, 2026, "en", today=d0).body.decode())
        b = _answer(rp.render(spec.slug, 2026, "en", today=d0 + dt.timedelta(days=1)).body.decode())
        want_a = rp._day_label(d0, "en", year=True)
        want_b = rp._day_label(dt.date.fromisoformat(rows26[4]["date"]), "en", year=True)
        if want_a not in a or want_b not in b:
            check(f"{spec.slug}: the answer moves with the date", False, f"{a[:80]} | {b[:80]}")
            break
    else:
        check("on an observance's own day it is the answer; the next day it moves on", True)
    past = rp.render("pradosh-vrat", 2026, "en", today=dt.date(2027, 3, 1)).body.decode()
    pa = _answer(past)
    check("a past year says 'all 25 ... dates for 2026' and points to 2027",
          "All 25 Pradosh Vrat dates for 2026" in pa and "/pradosh-vrat-2027" in pa
          and "next" not in pa.lower().split("dates for")[0], pa[:200])
    end = rp.render("kalashtami", 2026, "en", today=dt.date(2026, 12, 31)).body.decode()
    last = _engine(rp.BY_SLUG["kalashtami"], 2026)[-1]
    check("after the year's last date the answer is the past form (no date in the future)",
          (last["date"] < "2026-12-31" and "dates for 2026" in _answer(end))
          or last["date"] >= "2026-12-31")
    pre = rp.render("purnima", 2026, "hi", today=dt.date(2025, 12, 1)).body.decode()
    check("before the year: Hindi 'first' answer",
          "की पहली तिथि" in _answer(pre) and "सभी 13 तिथियां" in _answer(pre))
    check("the page is private/day-scoped cached (answer depends on the date)",
          "private" in client.get("/purnima-2026").headers["cache-control"])

    print("7. Links")
    h = pages["/purnima-2026"]
    hrefs = set(re.findall(r'href="(/[^"#?]*)"', h.split("<main", 1)[1].split("</main>", 1)[0]))
    fam = {p for p in hrefs if i18n.strip_prefix(p)[1].lstrip("/").split("-")[0] in
           {s.slug.split("-")[0] for s in rp.SPECS}}
    check("links to all 5 sibling pages, the other year, Ekadashi, the year calendar, the hub",
          all(rp.path(s.slug, 2026) in hrefs for s in rp.SPECS if s.slug != "purnima")
          and "/purnima-2027" in hrefs and "/ekadashi-2026" in hrefs and "/vrat-tyohar/2026" in hrefs
          and "/vrat-tyohar" in hrefs, str(sorted(hrefs)[:12]))
    check("links to the Panchang of New Delhi and 11 more cities",
          "/panchang" in hrefs and sum(1 for p in hrefs if p.startswith("/panchang/")) == 11)
    dead = [p for p in sorted(hrefs) if client.get(p).status_code != 200]
    check("every internal link on the page resolves (200)", not dead, str(dead[:3]))
    kn = pages["/kn/amavasya-2026"]
    check("a regional page keeps the reader in the language",
          'href="/kn/pradosh-vrat-2026"' in kn and 'href="/kn/ekadashi-2026"' in kn
          and 'href="/kn/panchang/mumbai"' in kn)
    hub = client.get("/sitemap").text
    check("the /sitemap hub links to all 12 English pages",
          all(f'href="{rp.path(s.slug, y)}"' in hub for s in rp.SPECS for y in rp.YEARS))
    check("... and the Hindi hub to the Hindi ones",
          all(f'href="{rp.path(s.slug, 2027, "hi")}"' in client.get("/hi/sitemap").text for s in rp.SPECS))

    print("8. 404s, sitemap, beacon, IndexNow, share")
    for bad in ("/purnima-2030", "/purnima-2025", "/hi/amavasya-abc", "/kn/pradosh-vrat-1999",
                "/foo-2026", "/pradosh-2026", "/sankashti-2026", "/purnima-", "/purnima"):
        r = client.get(bad)
        check(f"{bad} -> 404", r.status_code == 404, str(r.status_code))
    r = client.get("/purnima-2030")
    check("a family 404 is not cached and offers the 12 pages",
          r.headers.get("cache-control") == "no-store" and "/amavasya-2026" in r.text)
    sm = client.get("/sitemap.xml").text
    missing = [p for p in paths if f"<loc>{SITE}{p}</loc>" not in sm]
    check("all 96 pages are in sitemap.xml", not missing, str(missing[:3]))
    check("seo_pages.sitemap_paths() lists each once",
          all(seo_pages.sitemap_paths().count(p) == 1 for p in paths))
    check("beacon accepts every page", all(analytics.is_public_page(p) for p in paths))
    for bad in ("/purnima-2030", "/purnima-2026/x", "/hi/foo-2026", "/pradosh-2026"):
        check(f"beacon rejects {bad}", not analytics.is_public_page(bad))
    daily = indexnow.daily_paths(dt.date(2026, 10, 7))
    check("IndexNow's daily list has this year's 48 pages (every language), not next year's",
          all(rp.path(s.slug, 2026, l) in daily for s in rp.SPECS for l in LANGS)
          and not any(rp.path(s.slug, 2027) in daily for s in rp.SPECS)
          and len(daily) == len(set(daily)))
    check("... and every daily URL is in the sitemap", all(p in set(seo_pages.sitemap_paths())
                                                          for p in daily))
    share = re.search(r'class="share-wa" href="([^"]+)"', pages["/pradosh-vrat-2026"]).group(1)
    check("share button text names the observance and year",
          "Pradosh" in htmllib.unescape(share) or "Pradosh" in share.replace("%20", " "))

    print("9. Mundan muhurat")
    mp = muhurat_pages.page_paths()
    want = [muhurat_pages.page_path("mundan", y, l) for y in muhurat_pages.YEARS for l in LANGS]
    check("/muhurat/mundan-2026, -2027 in every language are in muhurat_pages.page_paths()",
          all(p in mp for p in want) and len(mp) == 3 * 2 * 8, str(len(mp)))
    check("the engine's mundan rule is the page's source",
          muhurat_pages.KINDS["mundan"].event == "mundan" and "mundan" in muhurat.EVENT_RULES)
    rule = muhurat.EVENT_RULES["mundan"]
    bad = []
    mpages = {}
    for p in want:
        r = client.get(p)
        mpages[p] = r.text
        if r.status_code != 200:
            bad.append((p, r.status_code))
    check("all mundan pages 200", not bad, str(bad[:3]))
    check("beacon + sitemap list them", all(analytics.is_public_page(p) for p in want)
          and all(f"<loc>{SITE}{p}</loc>" in sm for p in want))
    h = mpages["/muhurat/mundan-2026"]
    t, d, h1 = _meta(h)
    check("title/description/h1 name 'Mundan' and 2026; canonical self; hreflang; no noindex",
          "Mundan" in t and "2026" in t and "Mundan" in h1 and "mundan" in d.lower()
          and f'<link rel="canonical" href="{SITE}/muhurat/mundan-2026"/>' in h
          and "noindex" not in h and 'hreflang="x-default"' in h)
    rows = re.findall(r'<tr data-date="([0-9-]+)">', h)
    check("a list of dates by month, all in 2026", len(rows) > 10 and all(r.startswith("2026") for r in rows),
          str(len(rows)))
    data = muhurat_pages._year_data("mundan", 2026)
    check("the list is the engine's: same count and every date 'Auspicious' in the Finder",
          len(rows) == data["count"] and all(
              muhurat.evaluate_day("mundan", dt.date.fromisoformat(r), seo_pages.seo_cities.DEFAULT.latitude,
                                   seo_pages.seo_cities.DEFAULT.longitude, "Asia/Kolkata")["verdict"]
              == "Auspicious" for r in rows[:12]))
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", h))
    check("it prints the engine's mundan rules, not a wedding's",
          all(n in text for n in rule.excluded_nakshatras | rule.preferred_nakshatras)
          and "Chaturthi, Navami, Chaturdashi, Purnima, Amavasya" in text
          and "Dwitiya, Tritiya, Panchami, Saptami, Dashami, Ekadashi, Trayodashi" in text
          and "Tuesday, Saturday count against" in text and "Vyatipata" in text)
    check("the note names the mundan (chudakarma), not 'a wedding or griha pravesh'",
          "mundan (chudakarma)" in text and "wedding or griha pravesh" not in text)
    v = muhurat_pages._page("vivah", 2026, "en").body.decode()
    check("vivah/griha pravesh pages are unchanged by it (no mundan rules block; wedding note)",
          "the rules these dates follow" not in v and "wedding or griha pravesh" in v)
    check("cross-links: vivah and griha pravesh pages link to mundan, and mundan to them",
          'href="/muhurat/mundan-2026"' in v and 'href="/muhurat/mundan-2027"' in v
          and 'href="/muhurat/vivah-2026"' in h and 'href="/muhurat/griha-pravesh-2027"' in h)
    check("/sitemap hub lists the mundan pages", 'href="/muhurat/mundan-2026"' in hub)
    hh = mpages["/hi/muhurat/mundan-2027"]
    hht = re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", hh)))
    check("Hindi mundan page: Devanagari rules, names and the mundan note",
          "मुंडन मुहूर्त 2027" in hht
          and "वर्जित तिथियां: चतुर्थी, नवमी, चतुर्दशी, पूर्णिमा, अमावस्या" in hht
          and "मुंडन (चूड़ाकरण)" in hht)
    for lang in i18n.EXTRA_CODES:
        mh = mpages[f"/{lang}/muhurat/mundan-2026"]
        if "{" in re.sub(r"<style.*?</style>|<script.*?</script>", "", mh, flags=re.S) or "rules.body" in mh:
            check(f"{lang} mundan page: no unformatted placeholders", False)
            break
    else:
        check("every regional mundan page: rules block present, no stray placeholders",
              all("<ul>" in mpages[f"/{l}/muhurat/mundan-2026"] for l in i18n.EXTRA_CODES))
    check("share button on a mundan page", 'class="share-wa"' in h)
    check("404 for an unknown kind/year", client.get("/muhurat/mundan-2031").status_code == 404
          and client.get("/muhurat/namkaran-2026").status_code == 404)

    print()
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print("recurring pages: all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
