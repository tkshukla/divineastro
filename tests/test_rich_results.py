"""Rich results on the vrat/tyohar pages and the per-city vrat-tyohar pages (DIVASTRO-114).

Structured data is checked against the properties Google documents for each
rich result type (developers.google.com/search/docs/appearance/structured-data):

  Event    required: name, startDate (ISO 8601), location (Place with an
           address); recommended: description, endDate, eventAttendanceMode,
           eventStatus, image, organizer (offers/performer do not apply to a
           festival and are deliberately absent). startDate <= endDate, and a
           date-time carries the +05:30 offset.
  FAQPage  mainEntity: Questions, each with a name and acceptedAnswer.text;
           every question and answer must be visible on the page.
  ItemList itemListElement: ListItems with consecutive positions.

Also pins: no FAQ answer mentions a timing switched off in
festivals.OMITTED_TIMINGS (or an OMITTED festival); /vrat-tyohar/<city> for
every seo_cities city in both languages, timings computed for that city (an
Ekadashi parana, which starts at sunrise, differs between Mumbai and New
Delhi), New Delhi canonical at the bare URL, sitemap + beacon + share text,
404 for an unknown city, cross-links with /panchang/<city> and /rahu-kaal/<city>.

    ~/.venvs/divineastro/bin/python -u -m tests.test_rich_results
"""

from __future__ import annotations

import datetime as dt
import html as htmllib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_rich_results_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, i18n, seo_cities, seo_pages, share, vrat_pages  # noqa: E402
from app.astro import festivals  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def graph(page: str) -> list[dict]:
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
    return json.loads(m.group(1))["@graph"] if m else []


def nodes(page: str, kind: str) -> list[dict]:
    return [n for n in graph(page) if n.get("@type") == kind]


def _when(value: str) -> dt.datetime | dt.date | None:
    try:
        if "T" in value:
            return dt.datetime.fromisoformat(value)
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def event_problems(ev: dict) -> list[str]:
    """Google's Event requirements (required + the recommended ones we promise)."""
    out = []
    for key in ("name", "startDate", "location", "description", "endDate",
                "eventAttendanceMode", "eventStatus", "image", "organizer"):
        if not ev.get(key):
            out.append(f"missing {key}")
    loc = ev.get("location") or {}
    if loc.get("@type") != "Place" or not loc.get("name") or \
            (loc.get("address") or {}).get("@type") != "PostalAddress" or \
            loc["address"].get("addressCountry") != "IN":
        out.append("location is not a Place with PostalAddress addressCountry IN")
    start, end = _when(ev.get("startDate", "")), _when(ev.get("endDate", ""))
    if start is None or end is None:
        out.append(f"dates not ISO 8601: {ev.get('startDate')} / {ev.get('endDate')}")
    else:
        if isinstance(start, dt.datetime) != isinstance(end, dt.datetime):
            out.append("startDate/endDate mix a date and a date-time")
        elif isinstance(start, dt.datetime):
            if start.utcoffset() != dt.timedelta(hours=5, minutes=30) or \
                    end.utcoffset() != dt.timedelta(hours=5, minutes=30):
                out.append("date-time without the +05:30 offset")
            if end <= start:
                out.append("endDate not after startDate")
        elif end < start:
            out.append("endDate before startDate")
    if ev.get("eventAttendanceMode") != "https://schema.org/OfflineEventAttendanceMode":
        out.append("eventAttendanceMode")
    if ev.get("eventStatus") != "https://schema.org/EventScheduled":
        out.append("eventStatus")
    org = ev.get("organizer") or {}
    if org.get("@type") != "Organization" or not org.get("name") or not org.get("url", "").startswith(SITE):
        out.append("organizer")
    imgs = ev.get("image") or []
    if not imgs or not all(str(i).startswith(SITE + "/") for i in imgs):
        out.append("image")
    for absent in ("offers", "performer"):
        if absent in ev:
            out.append(f"invented {absent}")
    return out


def faq_problems(faq: dict, page: str) -> list[str]:
    out = []
    qs = faq.get("mainEntity") or []
    if not qs:
        out.append("no questions")
    for q in qs:
        a = (q.get("acceptedAnswer") or {}).get("text", "")
        if q.get("@type") != "Question" or not q.get("name") or \
                (q.get("acceptedAnswer") or {}).get("@type") != "Answer" or not a:
            out.append(f"malformed question {q.get('name')!r}")
            continue
        if f"<h3>{htmllib.escape(q['name'], quote=True)}</h3>" not in page:
            out.append(f"question not visible: {q['name']!r}")
        if f"<p>{htmllib.escape(a, quote=True)}</p>" not in page:
            out.append(f"answer not visible: {a[:60]!r}")
    return out


def omitted_labels(path: str) -> set[str]:
    """EN + HI labels of the timings switched off for this festival page's observance.
    A timing is printed as "<label>: <time>", so that is what must not appear (the
    Makar Sankranti RULE text may still name the punya kaal period, with no time)."""
    lang, bare = i18n.strip_prefix(path)          # /hi, /ta, /kn ... (DIVASTRO-123)
    slug, _, year = bare.removeprefix("/tyohar/").rpartition("-")
    key = vrat_pages.festival_index(int(year))[slug]["key"]
    own = i18n.names(lang).FESTIVAL_TIMINGS
    return {lbl for (k, tk) in festivals.OMITTED_TIMINGS if k == key
            for lbl in (*festivals.LABELS[tk], own.get(tk)) if lbl}


OMITTED_NAMES = {n for s in festivals.FESTIVALS if s.key in festivals.OMITTED
                 for n in (s.name_en, s.name_hi)}


def main() -> int:
    print("1. Event + FAQPage on festival pages (Diwali, Karwa Chauth, Jivitputrika 2026)")
    for slug in ("diwali", "karwa-chauth", "jivitputrika"):
        for pre in ("", "/hi"):
            p = f"{pre}/tyohar/{slug}-2026"
            r = client.get(p)
            page = r.text
            evs, faqs = nodes(page, "Event"), nodes(page, "FAQPage")
            check(f"{p}: 200, one Event and one FAQPage", r.status_code == 200
                  and len(evs) == 1 and len(faqs) == 1, f"{r.status_code} {len(evs)} {len(faqs)}")
            if not evs or not faqs:
                continue
            ev, faq = evs[0], faqs[0]
            probs = event_problems(ev)
            check(f"{p}: Event has Google's required + recommended fields", not probs, str(probs))
            check(f"{p}: Event url is the page, inLanguage matches",
                  ev.get("url") == SITE + p and ev.get("inLanguage") == ("hi-IN" if pre else "en-IN"))
            probs = faq_problems(faq, page)
            check(f"{p}: FAQ questions/answers all visible on the page", not probs, str(probs))
            answers = " ".join(q["acceptedAnswer"]["text"] for q in faq["mainEntity"])
            leaked = [lbl for lbl in omitted_labels(p) if f"{lbl}:" in answers] + \
                [n for n in OMITTED_NAMES if n in answers]
            check(f"{p}: no FAQ answer mentions an OMITTED timing or festival", not leaked, str(leaked))
            if pre:
                check(f"{p}: Hindi FAQ (Devanagari questions)",
                      all(DEVANAGARI.search(q["name"]) for q in faq["mainEntity"])
                      and "अक्सर पूछे जाने वाले प्रश्न" in page)

    d = client.get("/tyohar/diwali-2026").text
    ev, faq = nodes(d, "Event")[0], nodes(d, "FAQPage")[0]
    check("Diwali 2026 Event: the Lakshmi puja muhurat 5:54 PM - 7:50 PM, +05:30",
          ev["startDate"].startswith("2026-11-08T17:54") and ev["endDate"].startswith("2026-11-08T19:50")
          and ev["startDate"].endswith("+05:30"), f"{ev['startDate']} {ev['endDate']}")
    qa = {q["name"]: q["acceptedAnswer"]["text"] for q in faq["mainEntity"]}
    check("Diwali FAQ: when / puja muhurat / why, with the New Delhi times and the city note",
          qa.get("When is Diwali (Lakshmi Puja) 2026?") == "Diwali (Lakshmi Puja) 2026 is on Sunday, 8 November 2026."
          and "Lakshmi puja muhurat: 5:54 PM – 7:50 PM" in qa.get("What is the Diwali (Lakshmi Puja) 2026 puja muhurat?", "")
          and "vary by city" in qa.get("What is the Diwali (Lakshmi Puja) 2026 puja muhurat?", "")
          and "Pradosh kaal" in qa.get("Why is Diwali (Lakshmi Puja) 2026 observed on 8 Nov?", ""), str(qa))
    k = client.get("/tyohar/karwa-chauth-2026").text
    ev, faq = nodes(k, "Event")[0], nodes(k, "FAQPage")[0]
    check("Karwa Chauth 2026 Event: the evening puja window on 29 Oct (not the moonrise moment)",
          ev["startDate"].startswith("2026-10-29T") and ev["endDate"].startswith("2026-10-29T"),
          f"{ev['startDate']} {ev['endDate']}")
    check("Karwa Chauth FAQ answer includes moonrise",
          any(re.search(r"Moonrise: 8:1[67] PM", q["acceptedAnswer"]["text"]) for q in faq["mainEntity"]))
    j = client.get("/tyohar/jivitputrika-2026").text
    ev, faq = nodes(j, "Event")[0], nodes(j, "FAQPage")[0]
    check("Jivitputrika 2026 (no validated timing): a whole-day, date-only Event on 3 Oct",
          ev["startDate"] == "2026-10-03" and ev["endDate"] == "2026-10-03", str(ev)[:120])
    check("Jivitputrika FAQ: no timing question at all (parana time is OMITTED), no 'Parana'",
          len(faq["mainEntity"]) == 2 and "Parana" not in json.dumps(faq)
          and not any("muhurat" in q["name"] or "timings" in q["name"] for q in faq["mainEntity"]),
          str([q["name"] for q in faq["mainEntity"]]))
    pp = nodes(client.get("/tyohar/pitru-paksha-2026").text, "Event")[0]
    check("Pitru Paksha 2026 Event spans the fortnight: 27 Sep - 10 Oct (Sarva Pitru Amavasya)",
          pp["startDate"] == "2026-09-27" and pp["endDate"] == "2026-10-10", f"{pp['startDate']} {pp['endDate']}")

    print("2. Every festival page, both languages and years: valid Event + visible FAQ")
    bad = []
    fest_paths = [p for p in vrat_pages.page_paths() if "/tyohar/" in p]
    for p in fest_paths:
        page = client.get(p).text
        evs, faqs = nodes(page, "Event"), nodes(page, "FAQPage")
        probs = (event_problems(evs[0]) if len(evs) == 1 else ["event count"]) + \
                (faq_problems(faqs[0], page) if len(faqs) == 1 else ["faq count"])
        if faqs:
            answers = json.dumps(faqs[0], ensure_ascii=False)
            probs += [f"omitted {x}" for x in omitted_labels(p) if f"{x}:" in answers]
            probs += [f"omitted {x}" for x in OMITTED_NAMES if x in answers]
        if probs:
            bad.append((p, probs[:2]))
    check(f"all {len(fest_paths)} festival pages", not bad, str(bad[:3]))

    print("3. Year and Ekadashi lists: an ItemList, no Event spam")
    for p in ("/vrat-tyohar/2026", "/hi/vrat-tyohar/2027", "/ekadashi-2026", "/hi/ekadashi-2027"):
        page = client.get(p).text
        lists = nodes(page, "ItemList")
        il = lists[0] if lists else {}
        els = il.get("itemListElement", [])
        check(f"{p}: one ItemList, positions 1..n, numberOfItems = n, no Event nodes",
              len(lists) == 1 and els and [e["position"] for e in els] == list(range(1, len(els) + 1))
              and il.get("numberOfItems") == len(els) and all(e.get("@type") == "ListItem" and e.get("name") for e in els)
              and not nodes(page, "Event"), f"{len(els)} items")
    y = client.get("/vrat-tyohar/2026").text
    els = nodes(y, "ItemList")[0]["itemListElement"]
    check("2026 list links every major festival page (Diwali included)",
          any(e.get("url") == SITE + "/tyohar/diwali-2026" for e in els)
          and all(e["url"].startswith(SITE + "/tyohar/") for e in els))
    e = client.get("/ekadashi-2026").text
    check("Ekadashi 2026 ItemList has the 24 Ekadashis",
          nodes(e, "ItemList")[0]["numberOfItems"] == 24)

    print("4. /vrat-tyohar/<city>, both languages")
    city_paths = [vrat_pages.city_path(c, lang) for c in seo_cities.CITIES
                  if c != seo_cities.DEFAULT for lang in ("en", "hi")]
    check("226 city pages (113 cities x EN/HI; New Delhi is the bare /vrat-tyohar)",
          len(city_paths) == 226 and len(seo_cities.CITIES) == 114, str(len(city_paths)))
    vrat_pages._city_upcoming.cache_clear()
    t0 = time.time()
    r = client.get("/vrat-tyohar/varanasi")
    cold = time.time() - t0
    t0 = time.time()
    client.get("/vrat-tyohar/varanasi")
    warm = time.time() - t0
    check("a cold city page renders in < 1 s (31 days for one city, not a year)",
          r.status_code == 200 and cold < 1.0, f"cold {cold:.3f}s, warm {warm:.3f}s")
    for slug in ("mumbai", "kolkata", "chennai", "bengaluru", "jaipur"):
        city = seo_cities.BY_SLUG[slug]
        for lang, pre in (("en", ""), ("hi", "/hi")):
            p = f"{pre}/vrat-tyohar/{slug}"
            r = client.get(p)
            page = r.text
            name = city.name_hi if lang == "hi" else city.name
            probs = []
            if r.status_code != 200:
                probs.append(str(r.status_code))
            if f'<link rel="canonical" href="{SITE}{p}"/>' not in page:
                probs.append("canonical")
            if f"<h1>" not in page or name not in page.split("<h1>", 1)[1].split("</h1>", 1)[0]:
                probs.append("h1 city")
            if f"({name})</th>" not in page:
                probs.append("table header city")
            if f'href="{pre}/panchang/{slug}"' not in page or f'href="{pre}/rahu-kaal/{slug}"' not in page:
                probs.append("panchang/rahu-kaal links")
            if 'aria-current="page"' not in page or '<dl class="cities">' not in page:
                probs.append("city index")
            if ("Regional traditions may vary" not in page) if lang == "en" else ("क्षेत्रीय परंपराएं" not in page):
                probs.append("top note")
            if 'class="share-wa"' not in page:
                probs.append("share")
            if lang == "hi" and not DEVANAGARI.search(page.split("<h1>", 1)[1]):
                probs.append("hindi")
            check(f"{p}: 200, canonical, city in h1 + table, Panchang/Rahu Kaal links, index, note",
                  not probs, ", ".join(probs))

    print("5. City timings are the city's own")
    day = dt.date(2026, 10, 22)                         # Papankusha; parana 23 Oct after sunrise
    delhi = vrat_pages.render_hub("en", today=day).body.decode()
    mumbai = vrat_pages.render_hub("en", today=day, city=seo_cities.BY_SLUG["mumbai"]).body.decode()

    def parana(h: str) -> str:
        m = re.search(r'class="box today">.*?Parana[^:]*: ([^<]+)<', h, re.S)
        return m.group(1) if m else ""
    check("Papankusha parana in Mumbai differs from New Delhi (sunrise-based)",
          parana(delhi) and parana(mumbai) and parana(delhi) != parana(mumbai),
          f"Delhi {parana(delhi)!r} vs Mumbai {parana(mumbai)!r}")
    eng = festivals.window(day, day + dt.timedelta(days=30), 19.0760, 72.8777, "Asia/Kolkata")
    pe = next(t for o in eng if o["key"] == "ekadashi" for t in o["timings"] if t["key"] == "parana")
    check("... and it is the engine's Mumbai parana (festivals.window at Mumbai's coordinates)",
          vrat_pages._clock(pe["start"], dt.date.fromisoformat(pe["date"]), "en") in parana(mumbai),
          pe["start"])
    m2 = vrat_pages.render_hub("hi", today=day, city=seo_cities.BY_SLUG["kolkata"]).body.decode()
    check("Kolkata (Hindi): city name in the table header and a parana time",
          "(कोलकाता)</th>" in m2 and "पारण" in m2)
    # festivals.window == observances for New Delhi (same engine, just a shorter range)
    diffs = 0
    for start in (dt.date(2026, 1, 1), dt.date(2026, 3, 1), dt.date(2026, 10, 1), dt.date(2026, 12, 15)):
        end = start + dt.timedelta(days=30)
        a = [(o["date"], o["key"], [(t["key"], (t.get("start") or t.get("at") or "")[:16]) for t in o["timings"]])
             for o in festivals.window(start, end, 28.6139, 77.2090, "Asia/Kolkata")]
        b = [(o["date"], o["key"], [(t["key"], (t.get("start") or t.get("at") or "")[:16]) for t in o["timings"]])
             for o in festivals.observances(start, end)]
        diffs += a != b
    check("festivals.window agrees with observances() for New Delhi (to the minute)", diffs == 0, str(diffs))

    print("6. New Delhi canonical, 404s, sitemap, beacon, share, cross-links")
    for pre in ("", "/hi"):
        r = client.get(f"{pre}/vrat-tyohar/new-delhi")
        check(f"{pre}/vrat-tyohar/new-delhi: 200 with canonical {pre}/vrat-tyohar",
              r.status_code == 200 and f'<link rel="canonical" href="{SITE}{pre}/vrat-tyohar"/>' in r.text)
        r = client.get(f"{pre}/vrat-tyohar/atlantis")
        check(f"{pre}/vrat-tyohar/atlantis -> 404, not cached, with the city index",
              r.status_code == 404 and r.headers.get("cache-control") == "no-store"
              and '<dl class="cities">' in r.text, str(r.status_code))
    hub = client.get("/vrat-tyohar").text
    check("/vrat-tyohar hub: state-grouped index links every city page",
          all(f'href="{p}"' in hub for p in city_paths if not p.startswith("/hi/"))
          and "<dt>Maharashtra</dt>" in hub)
    hub_hi = client.get("/hi/vrat-tyohar").text
    check("/hi/vrat-tyohar hub: Hindi index links every Hindi city page",
          all(f'href="{p}"' in hub_hi for p in city_paths if p.startswith("/hi/")))
    sm = client.get("/sitemap.xml").text
    missing = [p for p in city_paths if f"<loc>{SITE}{p}</loc>" not in sm]
    check("sitemap lists all 226 city pages", not missing, str(missing[:3]))
    check("sitemap does not list the non-canonical /vrat-tyohar/new-delhi",
          "/vrat-tyohar/new-delhi<" not in sm)
    check("beacon accepts every city page (+ /vrat-tyohar/new-delhi)",
          all(analytics.is_public_page(p) for p in city_paths)
          and analytics.is_public_page("/vrat-tyohar/new-delhi"))
    for bad in ("/vrat-tyohar/atlantis", "/hi/vrat-tyohar/atlantis", "/vrat-tyohar/mumbai/x"):
        check(f"beacon rejects {bad}", not analytics.is_public_page(bad))
    txt = share.seo_share_text("/vrat-tyohar/mumbai")
    check("share text names the city in both languages",
          txt is not None and "Mumbai" in txt and "मुंबई" in txt, str(txt))
    check("share text for an unknown city is None", share.seo_share_text("/vrat-tyohar/atlantis") is None)
    pm = client.get("/panchang/mumbai").text
    check("/panchang/mumbai links to /vrat-tyohar/mumbai", 'href="/vrat-tyohar/mumbai"' in pm)
    pmh = client.get("/hi/rahu-kaal/mumbai").text
    check("/hi/rahu-kaal/mumbai links to /hi/vrat-tyohar/mumbai", 'href="/hi/vrat-tyohar/mumbai"' in pmh)
    check("/panchang (New Delhi) links to the bare /vrat-tyohar",
          'href="/vrat-tyohar"' in client.get("/panchang").text)

    print()
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print("rich results + city vrat pages: all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
