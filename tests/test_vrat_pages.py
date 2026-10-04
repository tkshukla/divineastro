"""The vrat / tyohar pages and the Today-strip endpoint (DIVASTRO-111).

Reads the HTML exactly as a crawler gets it. Pins: every page renders in both
languages (Devanagari on the Hindi copy, Hindi clock words like "शाम"),
hreflang pairs point at each other, every page is in the sitemap and accepted
by the visit beacon, carries the share button, AdSense and the footer, unknown
URLs 404, nothing switched off in astro.festivals.OMITTED appears anywhere,
and the dates/timings printed are the validated ones (tests/test_festivals.py).

No server needed (FastAPI's in-process client). A throwaway SQLite database.

    ~/.venvs/divineastro/bin/python -u -m tests.test_vrat_pages
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_vrat_pages_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, i18n, seo_pages, vrat_pages  # noqa: E402
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


def _alts(html: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html))


def main() -> int:
    print("1. Every page renders, both languages")
    t0 = time.time()
    first = client.get("/vrat-tyohar")
    took = time.time() - t0
    check("/vrat-tyohar: 200, first render < 1.5 s (cold year cache)",
          first.status_code == 200 and took < 1.5, f"{took:.2f}s")
    paths = vrat_pages.page_paths()
    check("pages cover hub, 2 years, 2 Ekadashi lists and festivals, EN + HI",
          len(paths) > 60 and "/hi/vrat-tyohar" in paths and "/tyohar/diwali-2026" in paths
          and "/hi/ekadashi-2027" in paths, str(len(paths)))
    pages = {}
    for p in paths:
        r = client.get(p)
        pages[p] = r.text
        if r.status_code != 200 or not r.headers["content-type"].startswith("text/html"):
            check(f"{p}: 200 text/html", False, str(r.status_code))
    check(f"all {len(paths)} pages 200 text/html", all(p in pages for p in paths)
          and not [f for f in failures if f.endswith("200 text/html")])
    print(f"     (all pages: {time.time() - t0:.1f}s)")

    print("2. Shell: language, hreflang, beacon, AdSense, share, footer")
    for p, html in pages.items():
        lang, en_path = i18n.strip_prefix(p)          # /hi, /ta, /ml (DIVASTRO-123)
        hi = lang == "hi"
        alts = _alts(html)
        problems = []
        if alts.get("en") != SITE + en_path or alts.get("hi") != SITE + "/hi" + en_path \
                or alts.get(lang, SITE + p) != SITE + p:
            problems.append("hreflang")
        if f'<link rel="canonical" href="{SITE}{p}"/>' not in html:
            problems.append("canonical")
        if "/static/visit.js" not in html:
            problems.append("beacon")
        if seo_pages.ADSENSE_CLIENT not in html:
            problems.append("adsense")
        if 'class="share-wa"' not in html:
            problems.append("share")
        if 'class="site-footer"' not in html:
            problems.append("footer")
        if hi and (not DEVANAGARI.search(re.sub(r"<[^>]+>", "", html.split("<main", 1)[1]))
                   or 'lang="hi"' not in html or "नियम और शर्तें" not in html):
            problems.append("hindi")
        if problems:
            check(f"{p}: shell", False, ", ".join(problems))
    check("every page: hreflang pair, canonical, beacon, AdSense, share, footer(lang)",
          not [f for f in failures if f.endswith(": shell")])

    print("3. Sitemap and beacon")
    sm = client.get("/sitemap.xml").text
    missing = [p for p in paths if f"<loc>{SITE}{p}</loc>" not in sm]
    check("every page is in sitemap.xml", not missing, str(missing[:3]))
    check("seo_pages.sitemap_paths() includes them", set(paths) <= set(seo_pages.sitemap_paths()))
    check("beacon accepts every page", all(analytics.is_public_page(p) for p in paths))
    for bad in ("/vrat-tyohar/2031", "/tyohar/diwali-2031", "/tyohar/not-a-festival-2026",
                "/ekadashi-2025", "/hi/tyohar/holi-2026"):
        check(f"beacon rejects {bad}", not analytics.is_public_page(bad))

    print("4. 404s")
    for bad in ("/vrat-tyohar/2031", "/vrat-tyohar/abc", "/hi/vrat-tyohar/1999",
                "/tyohar/diwali-2031", "/tyohar/not-a-festival-2026", "/tyohar/diwali",
                "/ekadashi-2025", "/hi/ekadashi-abc", "/tyohar/holi-2026"):
        r = client.get(bad)
        check(f"{bad} -> 404, not cached", r.status_code == 404
              and r.headers.get("cache-control") == "no-store", str(r.status_code))

    print("5. Validated content (New Delhi)")
    d = pages["/tyohar/diwali-2026"]
    check("Diwali 2026: 8 November, Lakshmi puja 5:54 PM – 7:50 PM",
          "8 November 2026" in d and "Lakshmi puja muhurat: 5:54 PM – 7:50 PM" in d)
    dh = pages["/hi/tyohar/diwali-2026"]
    check("Hindi Diwali: 8 नवंबर, शाम 5:54 – शाम 7:50",
          "8 नवंबर 2026" in dh and "लक्ष्मी पूजा मुहूर्त: शाम 5:54 – शाम 7:50" in dh)
    k = pages["/tyohar/karwa-chauth-2026"]
    check("Karwa Chauth 2026: 29 October, moonrise 8:16/8:17 PM",
          "29 October 2026" in k and re.search(r"Moonrise: 8:1[67] PM", k) is not None)
    e = pages["/ekadashi-2026"]
    rows = re.findall(r'<tr data-date="(2026-[0-9-]+)">', e)
    check("Ekadashi 2026 lists 24 fasts", len(rows) == 24, str(len(rows)))
    check("Papankusha 22 Oct with parana 23 Oct 6:27 AM – 8:42 AM",
          '<tr data-date="2026-10-22">' in e and re.search(
              r"Papankusha Ekadashi.*?23 Oct, Friday, 6:2[678] AM – 8:4[123] AM", e, re.S)
          is not None)
    check("Hindi Ekadashi page: पापांकुशा एकादशी and सुबह times",
          "पापांकुशा एकादशी" in pages["/hi/ekadashi-2026"]
          and "सुबह 6:" in pages["/hi/ekadashi-2026"])
    y = pages["/vrat-tyohar/2026"]
    check("2026 calendar has 12 month headings and links to festival pages",
          len(re.findall(r"<h2>(January|February|March|April|May|June|July|August|September|"
                         r"October|November|December) 2026</h2>", y)) == 12
          and 'href="/tyohar/diwali-2026"' in y)
    hd = pages["/tyohar/holika-dahan-2026"]
    check("Holika Dahan 2026: 3 March, 6:22 PM - 8:50 PM, with the Drik note",
          "3 March 2026" in hd and re.search(r"Holika Dahan muhurat: 6:2[123] PM – 8:(49|50|51) PM", hd)
          is not None and "Drik" in hd)
    check("no page offers a Holi (colours) date", not any("/tyohar/holi-" in p for p in paths)
          and not any(">Holi<" in h or "Holi 2026" in h for h in pages.values()))
    check("Janmashtami page states the Smarta/Vaishnava convention",
          "Smarta" in pages["/tyohar/janmashtami-2026"]
          and "स्मार्त" in pages["/hi/tyohar/janmashtami-2026"])
    jp = pages["/tyohar/jivitputrika-2026"]
    check("Jivitputrika 2026 page: 3 October 2026, Saturday, nahay-khay/parana explained, "
          "no parana clock time",
          "3 October 2026, Saturday" in jp and "nahay-khay" in jp and "Parana (breaking" not in jp)
    jh = pages["/hi/tyohar/jivitputrika-2026"]
    check("Hindi Jivitputrika page: जीवित्पुत्रिका व्रत (जितिया), 3 अक्टूबर 2026, नहाय-खाय",
          "जीवित्पुत्रिका व्रत (जितिया)" in jh and "3 अक्टूबर 2026" in jh and "नहाय-खाय" in jh)
    new_slugs = ["jivitputrika", "hartalika-teej", "hariyali-teej", "kajari-teej", "nag-panchami",
                 "rishi-panchami", "anant-chaturdashi", "pitru-paksha", "sarva-pitru-amavasya",
                 "vat-savitri", "vat-purnima", "sheetala-ashtami", "gangaur", "ganga-dussehra",
                 "tulsi-vivah", "kartik-purnima", "dev-deepawali", "narak-chaturdashi", "lohri",
                 "gudi-padwa", "sakat-chauth", "mauni-amavasya", "hal-shashthi"]
    missing = [f"{pre}/tyohar/{s}-{y}" for s in new_slugs for y in vrat_pages.YEARS
               for pre in ("", "/hi") if f"{pre}/tyohar/{s}-{y}" not in pages]
    check(f"all {len(new_slugs)} new festivals have EN + HI pages for 2026 and 2027", not missing,
          str(missing[:4]))
    no_about = [s for s in new_slugs if s not in vrat_pages.ABOUT]
    check("each new festival page has its what/how text", not no_about, str(no_about))
    y26 = pages["/vrat-tyohar/2026"]
    check("2026 calendar lists Jivitputrika on 3 Oct, Kalashtami, Skanda Shashthi, Lohri",
          '<tr data-date="2026-10-03" data-key="jivitputrika">' in y26
          and 'data-key="kalashtami"' in y26 and 'data-key="skanda_shashthi"' in y26
          and 'href="/tyohar/lohri-2026"' in y26)
    sp = pages["/tyohar/sarva-pitru-amavasya-2026"]
    check("Sarva Pitru Amavasya 2026: 10 October, Kutup muhurat 11:44/11:45 AM",
          "10 October 2026" in sp and re.search(r"Kutup muhurat: 11:4[456] AM", sp) is not None)
    check("Vat Savitri and Vat Purnima pages label the two traditions",
          "Two traditions" in pages["/tyohar/vat-savitri-2026"]
          and "Two traditions" in pages["/tyohar/vat-purnima-2026"])
    check("every festival page says timings are for New Delhi and links to the Panchang tool",
          all("/?open=panchang" in pages[p] for p in paths if "/tyohar/" in p))

    print("6. Nothing switched off ever appears")
    obs26 = festivals.observances(dt.date(2026, 1, 1), dt.date(2026, 12, 31))
    keys = {o["key"] for o in obs26}
    for k_off, why in festivals.OMITTED.items():
        check(f"OMITTED {k_off} not computed", k_off not in keys)
    off_names = [s.name_en for s in festivals.FESTIVALS if s.key in festivals.OMITTED]
    check("Holi is switched off (only its date rule is unvalidated)", "holi" in festivals.OMITTED)
    leaked = [(p, n) for p, h in pages.items() for n in off_names if n in h]
    check("no omitted festival's name on any page", not leaked, str(leaked[:3]))
    labels = [festivals.LABELS[tk][0] for (k_, tk) in festivals.OMITTED_TIMINGS
              if tk not in ("ghatasthapana",)]
    ms = pages["/tyohar/makar-sankranti-2026"]
    check("Makar Sankranti page shows no unvalidated sankranti moment / punya kaal",
          not any(lbl in ms for lbl in labels), str([lbl for lbl in labels if lbl in ms]))
    cn = pages["/tyohar/chaitra-navratri-2026"]
    check("Chaitra Navratri page shows only the validated Abhijit ghatasthapana",
          "Ghatasthapana (Abhijit)" in cn and "Ghatasthapana muhurat:" not in cn)

    print("7. Hub: today / next 30 days")
    r = vrat_pages.render_hub("en", today=dt.date(2026, 10, 22))
    h = r.body.decode()
    check("on 22 Oct 2026 the hub leads with Papankusha Ekadashi and its parana",
          re.search(r'class="box today">.*?Papankusha Ekadashi.*?Parana', h, re.S) is not None)
    # 3 Oct 2026 used to be the "ordinary day" here - it is Jivitputrika (the
    # bug report that added it). 4 Oct 2026 has nothing.
    r = vrat_pages.render_hub("hi", today=dt.date(2026, 10, 4))
    h = r.body.decode()
    check("on an ordinary day (4 Oct 2026) the Hindi hub says so and names the next one",
          "आज कोई प्रमुख व्रत या त्योहार नहीं है" in h and "अगला:" in h)
    rows = re.findall(r'<tr data-date="([0-9-]+)"', h)
    check("the next-30-days table runs 5 Oct - 3 Nov",
          rows and min(rows) >= "2026-10-05" and max(rows) <= "2026-11-03", f"{rows[:1]}..{rows[-1:]}")
    for lang, name in (("en", "Jivitputrika Vrat (Jitiya)"), ("hi", "जीवित्पुत्रिका व्रत (जितिया)")):
        h = vrat_pages.render_hub(lang, today=dt.date(2026, 10, 3)).body.decode()
        pre = "/hi" if lang == "hi" else ""
        check(f"3 Oct 2026 ({lang}): the hub leads with {name}, linked to its page",
              re.search(r'class="box today">.*?<a href="' + pre + r'/tyohar/jivitputrika-2026">'
                        + re.escape(name), h, re.S) is not None)
    r = vrat_pages.render_hub("en", today=dt.date(2026, 12, 20))
    check("late December's next 30 days reach into 2027",
          "2027-01-" in r.body.decode())

    print("8. GET /api/vrat/today (home strip)")
    r = client.get("/api/vrat/today")
    j = r.json()
    check("200 JSON with date, items, urls", r.status_code == 200
          and set(j) >= {"date", "items", "url", "url_hi"}, str(j))
    check("urls point at the hub pages", j.get("url") == "/vrat-tyohar"
          and j.get("url_hi") == "/hi/vrat-tyohar")
    items = festivals.on(dt.date(2026, 10, 22))
    check("festivals.on(22 Oct 2026) -> Papankusha, with Hindi name",
          [(o["name_en"], o["name_hi"]) for o in items]
          == [("Papankusha Ekadashi", "पापांकुशा एकादशी")])
    check("'next' is null or the next observance with EN/HI names and short dates",
          j.get("next") is None if j.get("items") else
          (j.get("next") is not None and set(j["next"]) >= {"date", "name_en", "name_hi", "day_en", "day_hi"}
           and j["next"]["date"] > j["date"]), str(j.get("next")))
    # The endpoint on 3 Oct 2026 in New Delhi (clock pinned, whatever today is).
    class _Oct3(dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return dt.datetime(2026, 10, 3, 9, 0, tzinfo=tz)
    real_dt = vrat_pages.dt
    vrat_pages.dt = type("dtshim", (), {"datetime": _Oct3, "date": dt.date,
                                        "timedelta": dt.timedelta})
    try:
        j = client.get("/api/vrat/today?lat=28.6139&lon=77.209&tz=Asia/Kolkata").json()
    finally:
        vrat_pages.dt = real_dt
    first = (j.get("items") or [{}])[0]
    check("GET /api/vrat/today on 3 Oct 2026, New Delhi -> Jivitputrika first (the strip line)",
          j.get("date") == "2026-10-03" and first.get("key") == "jivitputrika"
          and first.get("name_hi") == "जीवित्पुत्रिका व्रत (जितिया)" and first.get("major") is True,
          str(j))
    r = client.get("/api/vrat/today?lat=19.076&lon=72.8777&tz=Asia/Kolkata")
    check("another city works", r.status_code == 200 and isinstance(r.json().get("items"), list))
    r = client.get("/api/vrat/today?lat=10&lon=10&tz=Not/AZone")
    check("a bad timezone fails silently (200, empty list)",
          r.status_code == 200 and r.json().get("items") == [], str(r.status_code))
    r = client.get("/api/vrat/today?lat=999&lon=0")
    check("out-of-range coordinates are rejected by validation", r.status_code == 422)

    print("9. GET /api/vrat/day (Panchang tool: one date's vrat/festivals with timings)")
    vrat_pages.dt = type("dtshim", (), {"datetime": _Oct3, "date": dt.date,
                                        "timedelta": dt.timedelta})
    try:
        delhi = "lat=28.6139&lon=77.209&tz=Asia/Kolkata"
        j = client.get(f"/api/vrat/day?date=2026-11-08&{delhi}").json()
        diwali = next((o for o in j.get("items", []) if o["key"] == "diwali"), {})
        lakshmi = next((t for t in diwali.get("timings", []) if t["key"] == "lakshmi_puja"), {})
        check("8 Nov 2026, New Delhi -> Diwali, linked to its EN/HI pages",
              diwali.get("name_hi") == "दीपावली (लक्ष्मी पूजा)" and diwali.get("url") == "/tyohar/diwali-2026"
              and diwali.get("url_hi") == "/hi/tyohar/diwali-2026", str(diwali)[:300])
        check("... Lakshmi puja muhurat 5:54-7:50 PM with both labels",
              lakshmi.get("start", "").startswith("2026-11-08T17:54")
              and lakshmi.get("end", "").startswith("2026-11-08T19:50")
              and lakshmi.get("label_en") == "Lakshmi puja muhurat"
              and lakshmi.get("label_hi") == "लक्ष्मी पूजा मुहूर्त", str(lakshmi))
        check("... headed with the date in EN and HI",
              j.get("day_en") == "8 November 2026" and j.get("day_hi") == "8 नवंबर 2026", str(j)[:200])
        j = client.get(f"/api/vrat/day?date=2026-11-20&{delhi}").json()
        parana = (j.get("items") or [{}])[0].get("timings", [{}])[0]
        check("20 Nov 2026: Ekadashi parana is the next day, with its short date",
              parana.get("key") == "parana" and parana.get("date") == "2026-11-21"
              and parana.get("day_en") == "21 Nov" and parana.get("day_hi") == "21 नवंबर", str(parana))
        j = client.get(f"/api/vrat/day?date=2026-10-29&{delhi}").json()
        sank = next((o for o in j.get("items", []) if o["key"] == "sankashti"), {})
        check("a minor vrat without a page links to the vrat-tyohar hub; moonrise is a single time",
              sank.get("url") == "/vrat-tyohar" and sank.get("url_hi") == "/hi/vrat-tyohar"
              and [t["key"] for t in sank.get("timings", [])] == ["moonrise"]
              and "at" in sank["timings"][0], str(sank))
        j = client.get(f"/api/vrat/day?date=2026-11-12&{delhi}").json()
        check("an ordinary date (12 Nov 2026) -> []", j.get("items") == [], str(j))
        for bad in ("2026-13-45", "yesterday", "2031-01-01", "1990-01-01"):
            r = client.get(f"/api/vrat/day?date={bad}&{delhi}")
            check(f"bad or far-off date {bad!r} -> 200 with an empty list",
                  r.status_code == 200 and r.json().get("items") == [], r.text[:120])
        r = client.get("/api/vrat/day?date=2026-11-08&lat=10&lon=10&tz=Not/AZone")
        check("a bad timezone -> 200 with an empty list",
              r.status_code == 200 and r.json().get("items") == [])
        j = client.get(f"/api/vrat/day?{delhi}").json()
        check("no date -> today at the place (3 Oct 2026: Jivitputrika)",
              j.get("date") == "2026-10-03"
              and any(o["key"] == "jivitputrika" for o in j.get("items", [])), str(j)[:200])
        j = client.get(f"/api/vrat/today?{delhi}").json()
        check("/api/vrat/today unchanged (names only, no timings)",
              set(j) >= {"date", "items", "next", "url", "url_hi"}
              and all(set(o) == {"key", "name_en", "name_hi", "major"} for o in j["items"]), str(j)[:200])
    finally:
        vrat_pages.dt = real_dt

    print("10. /panchang pages show today's vrat/festivals with their timings")
    real_today = seo_pages._today
    try:
        seo_pages._today = lambda: dt.date(2026, 11, 8)
        h = client.get("/panchang").text
        block = re.search(r"<h2>Vrat &amp; Festivals today</h2>(.*?)</div>", h, re.S)
        check("/panchang on Diwali: 'Vrat & Festivals today' block",
              block is not None, h[:200])
        block = block.group(1) if block else ""
        check("... Diwali linked to its page, Lakshmi puja muhurat 5:54 PM – 7:50 PM",
              '<a href="/tyohar/diwali-2026">Diwali (Lakshmi Puja)</a>' in block
              and "Lakshmi puja muhurat: 5:54 PM – 7:50 PM" in block, block[:400])
        h = client.get("/hi/panchang").text
        block = re.search(r"<h2>आज के व्रत-त्योहार</h2>(.*?)</div>", h, re.S)
        block = block.group(1) if block else ""
        check("/hi/panchang on Diwali: Devanagari block, Hindi link and times",
              '<a href="/hi/tyohar/diwali-2026">दीपावली (लक्ष्मी पूजा)</a>' in block
              and "लक्ष्मी पूजा मुहूर्त: शाम 5:54 – शाम 7:50" in block, block[:400])
        check("... with no Latin-script words in the block",
              not re.findall(r"[A-Za-z]{2,}", re.sub(r"<[^>]+>", "", block)), block[:400])
        h = client.get("/panchang/mumbai").text
        check("/panchang/mumbai on Diwali: the block with Mumbai's own times",
              "Vrat &amp; Festivals today" in h and "Lakshmi puja muhurat" in h)
        seo_pages._today = lambda: dt.date(2026, 11, 12)
        h = client.get("/panchang").text + client.get("/hi/panchang").text
        check("an ordinary day: no block at all",
              "Festivals today" not in h and "आज के व्रत-त्योहार" not in h)
    finally:
        seo_pages._today = real_today

    print()
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print("vrat pages: all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
