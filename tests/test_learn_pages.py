"""The /learn explainer pages (DIVASTRO-142).

Every claim a page makes about a calculation is checked here against the engine,
not against a copy: the worked examples are compared with the engine functions
called directly, the tables with the engine's own tables, and the whole family
is shown to be invisible (404, absent from the sitemap, hub, footer and beacon)
unless ASTRO_LEARN_PAGES=1.

No server needed (FastAPI's in-process client). A throwaway SQLite database is
used — never a real one.

    ~/.venvs/divineastro/bin/python -u -m tests.test_learn_pages
"""

from __future__ import annotations

import datetime as dt
import html as htmllib
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

_tmp = tempfile.mkdtemp(prefix="astro_learn_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ.pop("ASTRO_LEARN_PAGES", None)          # the default: hidden

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, i18n, learn_pages as L, nakshatra_pages, seo_cities, seo_pages  # noqa: E402
from app.astro import choghadiya as chog, doshas, festivals, vargas  # noqa: E402
from app.astro import panchang as P  # noqa: E402
from app.astro.namakshar import NAKSHATRA_LIST  # noqa: E402
from app.chart_service import NAKSHATRAS, SIGNS  # noqa: E402
from app.learn_text import CLAIMS, PAGES, SLUGS, UI  # noqa: E402
from app.main import app  # noqa: E402
from tests.test_seo_pages import canonical, check, failures  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
SITE = seo_pages.SITE_URL
IST = ZoneInfo("Asia/Kolkata")
TODAY = dt.datetime.now(IST).date()
DEL = seo_cities.DEFAULT
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
REVIEW = ROOT / "docs" / "learn-pages-review.md"
REGIONAL = [c for c in i18n.CODES if c not in ("en", "hi")]


def engine_day(day: dt.date = TODAY) -> dict:
    """The engine's own panchang for New Delhi, called directly (not through the page cache)."""
    return P.daily_panchang(day, DEL.latitude, DEL.longitude, DEL.timezone)


def clock(iso_or_dt, lang: str = "en") -> str:
    m = iso_or_dt if isinstance(iso_or_dt, dt.datetime) else dt.datetime.fromisoformat(iso_or_dt)
    return i18n.format_time(m.astimezone(IST), lang)


def body_of(html: str) -> str:
    return html.split('<main class="seo">')[1].split("</main>")[0]


def text_of(html: str) -> str:
    return htmllib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body_of(html))))


def h1(html: str) -> str:
    m = re.search(r"<h1>(.*?)</h1>", html, re.S)
    return htmllib.unescape(m.group(1)) if m else ""


def title(html: str) -> str:
    return htmllib.unescape(re.search(r"<title>(.*?)</title>", html, re.S).group(1))


def desc(html: str) -> str:
    return htmllib.unescape(re.search(r'<meta name="description" content="([^"]*)"', html).group(1))


def jsonld(html: str) -> list[dict]:
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1))["@graph"]


def table_after(html: str, heading: str) -> list[list[str]]:
    """Rows (header row first) of the table right after the <h2> that contains `heading`."""
    i = html.index(heading)
    seg = html[i:html.index("</table>", i)]
    rows = re.findall(r"<tr>(.*?)</tr>", seg, re.S)
    return [[htmllib.unescape(re.sub(r"<[^>]+>", "", c)).strip()
             for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)] for r in rows]


def get(path: str) -> str:
    r = client.get(path)
    assert r.status_code == 200, (path, r.status_code)
    return r.text


def page(slug: str, lang: str = "en") -> str:
    return get(f"{i18n.prefix(lang)}/learn/{slug}")


def main() -> int:
    # ------------------------------------------------------------------ hidden
    print("\n1. Hidden by default (ASTRO_LEARN_PAGES unset)")
    check("the switch is off", not L.enabled())
    paths = [L.page_path(None, lang) for lang in ("en", "hi", "kn")] + [
        L.page_path(s, lang) for s in SLUGS for lang in ("en", "hi", "kn")]
    codes = {p: client.get(p).status_code for p in paths}
    check("every /learn URL (en, hi, kn; index and 11 pages) is a real 404",
          set(codes.values()) == {404}, str({c for c in codes.values()}))
    check("a 404, not a soft page: no HTML shell",
          "<html" not in client.get("/learn/what-is-tithi").text)
    off_sitemap = client.get("/sitemap.xml").text
    check("sitemap.xml has no /learn URL", "/learn" not in off_sitemap)
    check("/sitemap hub has no /learn link", "/learn" not in client.get("/sitemap").text
          and "/learn" not in client.get("/hi/sitemap").text)
    check("footer has no /learn link", "/learn" not in client.get("/panchang").text
          and "/learn" not in client.get("/hi/panchang").text)
    check("beacon treats /learn pages as non-public",
          not any(analytics.is_public_page(p) for p in paths))
    check("sitemap_paths() is empty", L.sitemap_paths() == [])

    # ----------------------------------------------------------------- enabled
    os.environ["ASTRO_LEARN_PAGES"] = "1"
    print("\n2. Enabled: every page renders")
    check("11 slugs", len(SLUGS) == 11 and len(set(SLUGS)) == 11)
    check("the 11 slugs the brief asks for", set(SLUGS) == {
        "what-is-panchang", "what-is-tithi", "what-is-nakshatra", "what-is-yoga-and-karana",
        "what-is-rahu-kaal", "what-is-choghadiya", "what-is-abhijit-muhurat",
        "what-is-brahma-muhurta", "what-is-pradosh-kaal", "what-is-sade-sati",
        "what-is-mangal-dosha"})
    pages: dict[tuple[str, str], str] = {}
    for lang in ("en", "hi"):
        r = client.get(L.page_path(None, lang))
        check(f"{L.page_path(None, lang)}: 200 html", r.status_code == 200
              and r.headers["content-type"].startswith("text/html"))
        idx = r.text
        check(f"{lang} index links all 11 pages",
              all(f'href="{L.page_path(s, lang)}"' in idx for s in SLUGS))
        for s in SLUGS:
            path = L.page_path(s, lang)
            r = client.get(path)
            ok = r.status_code == 200 and r.headers["content-type"].startswith("text/html")
            check(f"{path}: 200 html", ok, str(r.status_code))
            pages[(s, lang)] = r.text
    check("unknown slug is a real 404 that still lists the pages",
          client.get("/learn/what-is-nothing").status_code == 404
          and 'href="/learn/what-is-tithi"' in client.get("/learn/what-is-nothing").text)

    print("\n3. Head: unique titles, descriptions and h1; canonical; hreflang; beacon")
    for lang in ("en", "hi"):
        ts = [title(pages[(s, lang)]) for s in SLUGS]
        ds = [desc(pages[(s, lang)]) for s in SLUGS]
        hs = [h1(pages[(s, lang)]) for s in SLUGS]
        check(f"{lang}: 11 unique titles", len(set(ts)) == 11)
        check(f"{lang}: 11 unique descriptions", len(set(ds)) == 11)
        check(f"{lang}: 11 unique h1", len(set(hs)) == 11)
        check(f"{lang}: description 60 to 200 characters", all(60 <= len(d) <= 200 for d in ds),
              str([len(d) for d in ds]))
        check(f"{lang}: title at most 110 characters", all(len(t) <= 110 for t in ts),
              str([len(t) for t in ts]))
        for s in SLUGS:
            html = pages[(s, lang)]
            path = L.page_path(s, lang)
            check(f"{path}: canonical is itself", canonical(html) == SITE + path, str(canonical(html)))
            alt = dict(re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"', html))
            check(f"{path}: hreflang en, hi, x-default (the same set on both copies) and nothing else",
                  alt == {"en": SITE + L.page_path(s, "en"), "hi": SITE + L.page_path(s, "hi"),
                          "x-default": SITE + L.page_path(s, "en")}, str(alt))
            check(f"{path}: indexable (no robots noindex)", 'name="robots"' not in html)
            check(f"{path}: visit beacon and it counts as public",
                  'src="/static/visit.js"' in html and analytics.is_public_page(path))
            check(f"{path}: private short cache",
                  "private" in client.get(path).headers["cache-control"])
    for s in SLUGS:
        check(f"{s}: h1/title/description are the text in learn_text",
              h1(pages[(s, "en")]) == PAGES[s]["en"]["h1"]
              and desc(pages[(s, "en")]) == PAGES[s]["en"]["desc"])

    print("\n4. JSON-LD parses; FAQPage matches the visible questions")
    for lang in ("en", "hi"):
        for s in SLUGS:
            html, path = pages[(s, lang)], L.page_path(s, lang)
            try:
                graph = jsonld(html)
            except ValueError as exc:
                check(f"{path}: JSON-LD parses", False, str(exc))
                continue
            types = [n["@type"] for n in graph]
            check(f"{path}: WebPage, BreadcrumbList, FAQPage",
                  {"WebPage", "BreadcrumbList", "FAQPage"} <= set(types), str(types))
            faq = next(n for n in graph if n["@type"] == "FAQPage")
            qs = faq["mainEntity"]
            check(f"{path}: 3 or 4 questions", 3 <= len(qs) <= 4, str(len(qs)))
            text = text_of(html)
            check(f"{path}: every FAQ question and answer is visible on the page",
                  all(q["name"] in text and q["acceptedAnswer"]["text"] in text for q in qs))
            check(f"{path}: FAQ is the text in learn_text",
                  [(q["name"], q["acceptedAnswer"]["text"]) for q in qs] == list(PAGES[s][lang]["faq"]))

    print("\n5. The direct answer comes first and is two sentences")
    for lang, end in (("en", ". "), ("hi", "। ")):
        for s in SLUGS:
            a = PAGES[s][lang]["answer"]
            html = pages[(s, lang)]
            first_box = re.search(r'<h1>.*?</h1>\s*<div class="box"><p>(.*?)</p>', html, re.S)
            check(f"{s} [{lang}]: the box right under the h1 is the direct answer",
                  first_box is not None and htmllib.unescape(first_box.group(1)) == a)
            check(f"{s} [{lang}]: exactly two sentences", a.count(end) == 1 and a.rstrip()[-1] in ".।",
                  a)
            check(f"{s} [{lang}]: method, worked example, use and FAQ sections follow",
                  html.index(UI[lang]["h.method"]) < html.index(UI[lang]["h.use"])
                  < html.index(UI[lang]["h.faq"]))
    check("Hindi pages are mostly Hindi",
          all(len(DEVANAGARI.findall(body_of(pages[(s, "hi")]))) > 400 for s in SLUGS))

    print("\n6. Tone: no fear language, no remedy selling, nothing prescriptive")
    fear = re.compile(r"\b(doom|curse[ds]?|danger\w*|beware|wrath|disaster|ruin\w*|dread\w*|fear\w*|"
                      r"terrible|malefic|afflict\w*|suffer\w*|calamit\w*|inauspicious period|"
                      r"you must|you should)\b", re.I)
    sell = re.compile(r"(₹|\bRs\.?\s*\d|\bbuy\b|\bbook a\b|consult an astrologer|pooja kit)", re.I)
    for s in SLUGS:
        blob = " ".join(
            [PAGES[s]["en"]["answer"], *PAGES[s]["en"]["method"], PAGES[s]["en"].get("convention", ""),
             *PAGES[s]["en"]["use"], *(q + " " + a for q, a in PAGES[s]["en"]["faq"])])
        bad = fear.findall(blob) + sell.findall(blob)
        check(f"{s}: no fear or selling words (en)", not bad, str(bad))
    sade, mangal = PAGES["what-is-sade-sati"]["en"], PAGES["what-is-mangal-dosha"]["en"]
    for name, p in (("sade-sati", sade), ("mangal-dosha", mangal)):
        blob = " ".join([p["answer"], *p["method"], p["convention"], *p["use"]])
        check(f"{name}: says traditions differ", "differ" in blob)
        check(f"{name}: says it is not a prediction", "not a prediction" in blob
              or "is not a prediction" in blob or "not a prediction that" in blob)
        check(f"{name}: names no remedy it recommends", "does not recommend any ritual" in blob)

    # ----------------------------------------------------------- live examples
    print("\n7. Worked examples equal the engine (called directly, for today in New Delhi)")
    eng = engine_day()
    vara = eng["vara"]["index"]
    en = {s: text_of(pages[(s, "en")]) for s in SLUGS}
    hi = {s: text_of(pages[(s, "hi")]) for s in SLUGS}
    nm = i18n.names("en")
    nmh = i18n.names("hi")
    day_str = f"{TODAY.day} {TODAY.strftime('%B %Y')}"

    # panchang
    t0, k0, y0, c0 = eng["tithi"][0], eng["nakshatra"][0], eng["yoga"][0], eng["karana"][0]

    def when(entry_end: str, lang: str = "en") -> str:
        m = dt.datetime.fromisoformat(entry_end).astimezone(IST)
        base = clock(m, lang)
        return base + (f" ({i18n.format_date(m.date(), lang, short=True)})" if m.date() != TODAY else "")

    pan = en["what-is-panchang"]
    check("panchang: today's tithi, nakshatra, yoga, karana and their end times are the engine's",
          f"the tithi at sunrise is {t0['paksha']} {t0['name']}, until {when(t0['ends'])}" in pan
          and f"The nakshatra is {k0['name']}, until {when(k0['ends'])}" in pan
          and f"The yoga is {y0['name']}, until {when(y0['ends'])}" in pan
          and f"the karana is {c0['name']}, until {when(c0['ends'])}" in pan, pan[:900])
    check("panchang: sunrise and sunset are the engine's",
          f"Sunrise is at {clock(eng['sun']['rise'])} and sunset at {clock(eng['sun']['set'])}" in pan)
    check("panchang: date and weekday", f"({eng['vara']['weekday']}, {day_str})" in pan)
    check("panchang [hi]: the same values in Hindi",
          nmh.tithi_label(t0["paksha"], t0["name"]) in hi["what-is-panchang"]
          and nmh.NAKSHATRAS[k0["name"]] in hi["what-is-panchang"]
          and clock(eng["sun"]["rise"], "hi") in hi["what-is-panchang"])
    tithi = en["what-is-tithi"]
    check("tithi: today's tithi and its start and end",
          f"is {t0['paksha']} {t0['name']}. It runs from {when(t0['starts'])} to {when(t0['ends'])}" in tithi, tithi[:700])
    if len(eng["tithi"]) > 1:
        t1 = eng["tithi"][1]
        check("tithi: the next tithi is named", f"followed by {t1['paksha']} {t1['name']}" in tithi)
    nak = en["what-is-nakshatra"]
    check("nakshatra: today's nakshatra, pada and end time",
          f"the Moon is in {k0['name']} nakshatra at sunrise, in pada {k0['pada']}. "
          f"{k0['name']} ends at {when(k0['ends'])}" in nak, nak[:600])
    yk = en["what-is-yoga-and-karana"]
    check("yoga & karana: today's yoga and karana",
          f"the yoga at sunrise is {y0['name']}, until {when(y0['ends'])}" in yk
          and f"The karana at sunrise is {c0['name']}, until {when(c0['ends'])}" in yk)

    # rahu kaal
    rk = eng["muhurta"]["rahu_kaal"]
    span = f"{clock(rk['start'])} – {clock(rk['end'])}"
    check("rahu kaal: today's window equals the engine's",
          f"Rahu Kaal is {span}." in en["what-is-rahu-kaal"], en["what-is-rahu-kaal"][:700])
    check("rahu kaal: part number is RAHU_SEGMENT + 1 and the minutes are the engine's",
          f"part {P.RAHU_SEGMENT[vara] + 1} of 8" in en["what-is-rahu-kaal"]
          and f"each part is {rk['duration_minutes']:.0f} minutes" in en["what-is-rahu-kaal"])
    check("rahu kaal [hi]: window in Hindi", f"{clock(rk['start'], 'hi')} – {clock(rk['end'], 'hi')}"
          in hi["what-is-rahu-kaal"])

    # choghadiya
    sched = chog.get_choghadiya_schedule(TODAY, DEL.latitude, DEL.longitude, DEL.timezone)
    d0 = sched["day_slots"][0]
    check("choghadiya: first slot name and time equal get_choghadiya_schedule",
          f"first choghadiya of the day is {d0['name']}, {clock(d0['start_iso'])} – {clock(d0['end_iso'])}"
          in en["what-is-choghadiya"], en["what-is-choghadiya"][:600])

    # abhijit
    ab = eng["muhurta"]["abhijit"]
    if vara != P.ABHIJIT_EXCLUDED_VARA:
        check("abhijit: today's window equals the engine's",
              f"Abhijit Muhurat is {clock(ab['start'])} – {clock(ab['end'])}." in en["what-is-abhijit-muhurat"])
    else:
        nxt = engine_day(TODAY + dt.timedelta(days=1))["muhurta"]["abhijit"]
        check("abhijit (a Wednesday): says none today and gives tomorrow's engine window",
              "does not give an Abhijit Muhurat on Wednesdays" in en["what-is-abhijit-muhurat"]
              and f"{clock(nxt['start'])} – {clock(nxt['end'])}" in en["what-is-abhijit-muhurat"]
              and f"{nxt['duration_minutes']:.0f} minutes long" in en["what-is-abhijit-muhurat"],
              en["what-is-abhijit-muhurat"][:500])
    # Abhijit on a non-Wednesday and a Wednesday, whatever today is
    wed = TODAY + dt.timedelta(days=(2 - TODAY.weekday()) % 7)
    check("abhijit: the engine omits Wednesday and gives 1/15 of daylight on the other days",
          engine_day(wed)["muhurta"]["abhijit"] is None
          and all(abs(engine_day(wed + dt.timedelta(days=i))["muhurta"]["abhijit"]["duration_minutes"]
                      - engine_day(wed + dt.timedelta(days=i))["sun"]["day_length_minutes"] / 15) < 0.1
                  for i in (1, 2)))
    for off, label in ((0, "a Wednesday"), (1, "a Thursday")):     # both branches, whatever today is
        d = wed + dt.timedelta(days=off)
        key, vals = L.live_values("what-is-abhijit-muhurat", d, "en")
        e = engine_day(d)["muhurta"]["abhijit"]
        if off == 0:
            n1 = engine_day(d + dt.timedelta(days=1))["muhurta"]["abhijit"]
            check(f"abhijit live example on {label}: the 'none' sentence plus the next day's engine window",
                  key == "live_none" and vals["abhijit2"] == f"{clock(n1['start'])} – {clock(n1['end'])}")
        else:
            check(f"abhijit live example on {label}: the engine's window and minutes",
                  key == "live" and vals["abhijit"] == f"{clock(e['start'])} – {clock(e['end'])}"
                  and vals["minutes"] == f"{e['duration_minutes']:.0f}")
    a8 = engine_day(wed + dt.timedelta(days=1))
    rise, setd = (dt.datetime.fromisoformat(a8["sun"][k]) for k in ("rise", "set"))
    mid = rise + (setd - rise) / 2
    ast, aen = (dt.datetime.fromisoformat(a8["muhurta"]["abhijit"][k]) for k in ("start", "end"))
    check("abhijit: the 8th of 15 daylight parts is centred on the sunrise-sunset midpoint",
          abs((ast + (aen - ast) / 2 - mid).total_seconds()) < 2)

    # brahma muhurta: our definition equals festivals.Day.night_muhurta(14)
    ss_prev, b_start, b_end, b_sunrise = L._brahma(TODAY)
    fd = festivals._day(TODAY - dt.timedelta(days=1), DEL.latitude, DEL.longitude, DEL.timezone)
    fs, fe = (P._from_jd(j, IST) for j in fd.night_muhurta(14))
    check("brahma muhurta: equals festivals.Day.night_muhurta(14) (within 2 s)",
          abs((fs - b_start).total_seconds()) < 2 and abs((fe - b_end).total_seconds()) < 2)
    check("brahma muhurta: it ends one fifteenth of the night before sunrise, and the night ends at the "
          "panchang's sunrise",
          abs((b_sunrise - b_end) - (b_sunrise - ss_prev) / 15).total_seconds() < 1
          and b_sunrise.isoformat() == eng["sun"]["rise"])
    check("brahma muhurta: the page prints it",
          f"Brahma Muhurta is {clock(b_start)} – {clock(b_end)}" in en["what-is-brahma-muhurta"],
          en["what-is-brahma-muhurta"][:500])

    # pradosh
    fday = festivals._day(TODAY, DEL.latitude, DEL.longitude, DEL.timezone)
    p_end = P._from_jd(fday.sunset + 3 * fday.night_len / 15.0, IST)
    p_start = P._from_jd(fday.sunset, IST)
    pr = en["what-is-pradosh-kaal"]
    check("pradosh: printed window is sunset to sunset + 3 night muhurtas (festivals.Day)",
          f"as printed, is {clock(p_start)} – {clock(p_end)}" in pr, pr[:600])
    w = festivals._window(fday, "pradosh", DEL.latitude, DEL.longitude)
    check("pradosh: the day-deciding window is sunset + 96 minutes (festivals._window)",
          abs((w[1] - w[0]) * 1440 - 96) < 1e-6
          and f"decide the day is {clock(p_start)} – {clock(P._from_jd(w[1], IST))}" in pr)
    check("pradosh: the sunset is the panchang's", f"sunset is at {clock(eng['sun']['set'])}" in pr)

    # sade sati
    saturn = P.sade_sati_for_moon_sign(0, dt.datetime(TODAY.year, TODAY.month, TODAY.day, tzinfo=IST),
                                       timezone="Asia/Kolkata", window_years=1.0)["saturn"]
    s_idx = SIGNS.index(saturn["sign"])
    running = []
    for m in range(12):
        r = P.sade_sati_for_moon_sign(m, dt.datetime(TODAY.year, TODAY.month, TODAY.day, tzinfo=IST),
                                      timezone="Asia/Kolkata", window_years=1.0)
        if r["running"]:
            running.append(m)
    check("sade sati: the signs the page names are exactly the Moon signs for which the engine says "
          "Sade Sati is running (all 12 checked)",
          running == sorted([(s_idx - 1) % 12, s_idx, (s_idx + 1) % 12]), f"{running} vs Saturn {s_idx}")
    ss = en["what-is-sade-sati"]
    names3 = [nakshatra_pages._sign_name(m, "en") for m in sorted(running, key=lambda m: ((m - s_idx + 1) % 12))]
    check("sade sati: Saturn's sign and motion, and the three Moon signs, are on the page",
          f"Saturn is in the sidereal sign {nakshatra_pages._sign_name(s_idx, 'en')}, "
          f"{'moving backward (retrograde)' if saturn['retrograde'] else 'moving forward (direct)'}" in ss
          and all(n in ss.split("Sade Sati is running for")[1][:200] for n in names3), ss[:600])
    rows = table_after(pages[("what-is-sade-sati", "en")], "The signs Saturn passes through")
    check("sade sati: table has 12 Moon signs and the rows follow (m + 11, m, m + 1)",
          len(rows) == 13 and all(
              [r[1], r[2], r[3]] == [nakshatra_pages._sign_name((m + 11) % 12, "en"),
                                      nakshatra_pages._sign_name(m, "en"),
                                      nakshatra_pages._sign_name((m + 1) % 12, "en")]
              for m, r in enumerate(rows[1:])))

    # mangal dosha
    check("mangal: houses counted are the engine's MANGLIK_HOUSES",
          doshas.MANGLIK_HOUSES == {1, 2, 4, 7, 8, 12}
          and "1, 2, 4, 7, 8 and 12" in PAGES["what-is-mangal-dosha"]["en"]["method"][0]
          and "1st, 2nd, 4th, 7th, 8th or 12th" in PAGES["what-is-mangal-dosha"]["en"]["answer"])
    check("mangal: Jupiter aspects 5/7/9 and the Moon 7, as the page states",
          vargas.GRAHA_DRISHTI["Jupiter"] == (5, 7, 9) and vargas.DEFAULT_DRISHTI == (7,)
          and "Moon" not in vargas.GRAHA_DRISHTI)
    res = [doshas.analyze_manglik(L.mangal_session(c)) for c in L.MANGAL_CHARTS]
    check("mangal: example 1 is Manglik with score 1.3 (Lagna 1.0 + Venus 0.3), nothing cancels",
          res[0]["is_manglik"] and not res[0]["is_cancelled"] and res[0]["score"] == 1.3
          and res[0]["houses"] == {"from_lagna": 7, "from_moon": 6, "from_venus": 4}, str(res[0]))
    check("mangal: example 2 is cancelled (Mars in Capricorn, 7th house), score 0",
          res[1]["is_cancelled"] and not res[1]["is_manglik"] and res[1]["score"] == 0.0
          and {L.cancel_key(c) for c in res[1]["cancellations"]} == {"cancel.dignified", "cancel.7"},
          str(res[1]))
    mg = en["what-is-mangal-dosha"]
    check("mangal: the page prints the engine's results for both charts",
          "Mars is in house 7 counted from the Lagna, 6 from the Moon and 4 from Venus" in mg
          and "Result: Manglik, score 1.3" in mg and "Mars in the 7th house, in Cancer or Capricorn" in mg)
    # every cancellation the engine can emit maps to a line on the page (probe each rule)
    probes = [
        {"lagna": "Aries", "Mars": "Aries", "Moon": "Taurus", "Venus": "Cancer", "Jupiter": "Leo"},
        {"lagna": "Aries", "Mars": "Gemini", "Moon": "Taurus", "Venus": "Cancer", "Jupiter": "Leo"},
        {"lagna": "Cancer", "Mars": "Libra", "Moon": "Aries", "Venus": "Aries", "Jupiter": "Taurus"},
        {"lagna": "Aries", "Mars": "Libra", "Moon": "Taurus", "Venus": "Cancer", "Jupiter": "Libra"},
        {"lagna": "Aries", "Mars": "Libra", "Moon": "Libra", "Venus": "Cancer", "Jupiter": "Leo"},
        {"lagna": "Aries", "Mars": "Libra", "Moon": "Aries", "Venus": "Cancer", "Jupiter": "Leo"},
    ]
    seen = set()
    for pr_ in probes:
        for msg in doshas.analyze_manglik(L.mangal_session(pr_))["cancellations"]:
            seen.add(L.cancel_key(msg))
    check("mangal: every cancellation message the engine produced here is one the page lists",
          None not in seen and {"cancel.dignified", "cancel.jupiter", "cancel.moon"} <= seen, str(seen))
    src = Path(doshas.__file__).read_text(encoding="utf-8")
    check("mangal: the engine has exactly the 8 cancellation rules the page lists",
          src.count("cancellations.append(") == 8)

    # ----------------------------------------------------------------- tables
    print("\n8. Tables are complete and agree with the engine's own tables")
    t = table_after(pages[("what-is-nakshatra", "en")], "The 27 nakshatras")
    check("27 nakshatras, in chart_service order, with the engine's spans",
          len(t) == 28 and [r[1] for r in t[1:]] == NAKSHATRAS
          and all(r[2] == nakshatra_pages.span_text(n, "en") for r, n in zip(t[1:], NAKSHATRA_LIST)))
    check("nakshatra table links every /nakshatra/<slug> page",
          all(f'href="/nakshatra/{n.slug}"' in pages[("what-is-nakshatra", "en")] for n in NAKSHATRA_LIST)
          and all(f'href="/hi/nakshatra/{n.slug}"' in pages[("what-is-nakshatra", "hi")]
                  for n in NAKSHATRA_LIST))
    check("each nakshatra spans 13°20′ (NAK_MIN = 800) and 4 padas of 3°20′",
          all(n.start_min == i * 800 for i, n in enumerate(NAKSHATRA_LIST)))
    t = table_after(pages[("what-is-tithi", "en")], "The 30 tithis")
    names30 = [P._tithi_label(i)[0] for i in range(30)]
    check("30 tithis: names and pakshas from the engine's _tithi_label, angles i*12 to (i+1)*12",
          len(t) == 31 and [r[2] for r in t[1:]] == names30
          and [r[1] for r in t[1:]] == [P._tithi_label(i)[1] for i in range(30)]
          and [r[3] for r in t[1:]] == [f"{i * 12}° – {(i + 1) * 12}°" for i in range(30)])
    check("tithi 15 is Shukla Purnima, 30 is Krishna Amavasya",
          t[15][1:3] == ["Shukla", "Purnima"] and t[30][1:3] == ["Krishna", "Amavasya"])
    check("tithi table in Hindi has 30 rows",
          len(table_after(pages[("what-is-tithi", "hi")], "30 तिथियाँ")) == 31)
    t = table_after(pages[("what-is-yoga-and-karana", "en")], "The 27 yogas")
    check("27 yogas in engine order", len(t) == 28 and [r[1] for r in t[1:]] == P.YOGA_NAMES)
    t = table_after(pages[("what-is-yoga-and-karana", "en")], "The karanas")
    karanas = [r[1] for r in t[1:]]
    check("11 karana names: 7 movable then Kimstughna and 3 fixed",
          len(karanas) == 11 and set(karanas) == set(P.MOVABLE_KARANAS) | set(P.FIXED_KARANAS)
          and P._karana_name(0) == "Kimstughna" and P._karana_name(57) == "Shakuni"
          and P._karana_name(58) == "Chatushpada" and P._karana_name(59) == "Naga"
          and [P._karana_name(i) for i in range(1, 8)] == P.MOVABLE_KARANAS
          and P._karana_name(56) == "Vishti")
    t = table_after(pages[("what-is-rahu-kaal", "en")], "Rahu Kaal by weekday")
    check("7 weekdays, part = RAHU_SEGMENT + 1, in Sunday-first order",
          len(t) == 8 and [r[0] for r in t[1:]] == P.VARA_ENGLISH
          and [int(r[1]) for r in t[1:]] == [s + 1 for s in P.RAHU_SEGMENT]
          and [int(r[1]) for r in t[1:]] == [8, 2, 7, 5, 6, 4, 3])
    live_ok = True
    for r in t[1:]:
        # "4:29 PM – 5:56 PM (11 Oct)": the engine's Rahu Kaal for that date
        d_label = re.search(r"\((\d+) (\w+)\)", r[2])
        d = next(TODAY + dt.timedelta(days=o) for o in range(7)
                 if f"{(TODAY + dt.timedelta(days=o)).day} {(TODAY + dt.timedelta(days=o)).strftime('%b')}" == f"{d_label.group(1)} {d_label.group(2)}")
        q = engine_day(d)["muhurta"]["rahu_kaal"]
        live_ok &= r[2].startswith(f"{clock(q['start'])} – {clock(q['end'])}") and \
            P.VARA_ENGLISH[engine_day(d)["vara"]["index"]] == r[0]
    check("each weekday's live time is the engine's Rahu Kaal for that date", live_ok)
    names = table_after(pages[("what-is-choghadiya", "en")], "The seven names")
    info = chog.CHOGHADIYA_INFO
    check("choghadiya: seven names with the engine's ruler and quality",
          len(names) == 8 and [r[0] for r in names[1:]] == list(info)
          and all(r[1] == info[r[0]]["ruler"] and r[2].lower() == info[r[0]]["quality"]
                  for r in names[1:]))
    day_t = table_after(pages[("what-is-choghadiya", "en")], "Daytime sequence by weekday")
    night_t = table_after(pages[("what-is-choghadiya", "en")], "Night-time sequence by weekday")
    check("choghadiya: 7 weekdays x 8 parts, day and night, equal to the engine's tables",
          len(day_t) == 8 and len(night_t) == 8
          and [r[1].split(" → ") for r in day_t[1:]] == [chog.DAY_SEQUENCE[v] for v in range(7)]
          and [r[1].split(" → ") for r in night_t[1:]] == [chog.NIGHT_SEQUENCE[v] for v in range(7)])
    day_cycle = ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]
    night_cycle = ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"]
    ruler_of = {n: i["ruler"] for n, i in info.items()}
    ok = True
    for v in range(7):
        day_seq, night_seq = chog.DAY_SEQUENCE[v], chog.NIGHT_SEQUENCE[v]
        ok &= ruler_of[day_seq[0]] == P.VARA_LORDS[v]                       # day starts with the weekday ruler
        ok &= ruler_of[night_seq[0]] == P.VARA_LORDS[(v + 4) % 7]           # night: the ruler 4 days on
        for seq, cyc in ((day_seq, day_cycle), (night_seq, night_cycle)):
            ok &= all(seq[i + 1] == cyc[(cyc.index(seq[i]) + 1) % 7] for i in range(7))
        ok &= day_seq[7] == day_seq[0] and night_seq[7] == night_seq[0]
    check("choghadiya: the page's stated rules (day and night cycles; day starts with weekday ruler; night starts "
          "with the ruler four days on; first name returns as the 8th) hold for all 7 weekdays", ok)
    today_t = table_after(pages[("what-is-choghadiya", "en")], "eight daytime choghadiya")
    check("choghadiya: today's table has the 8 engine day slots, in order",
          len(today_t) == 9 and [r[1] for r in today_t[1:]] == [s["name"] for s in sched["day_slots"]]
          and [r[0] for r in today_t[1:]] == [f"{clock(s['start_iso'])} – {clock(s['end_iso'])}"
                                              for s in sched["day_slots"]])
    check("choghadiya: 8 choghadiya of the day and 8 of the night exist in the engine",
          len(sched["day_slots"]) == 8 and len(sched["night_slots"]) == 8)
    t = table_after(pages[("what-is-abhijit-muhurat", "en")], "Abhijit Muhurat by weekday")
    check("abhijit: 7 weekdays, only Wednesday is No",
          len(t) == 8 and [r[1] for r in t[1:]] == ["Yes", "Yes", "Yes", "No", "Yes", "Yes", "Yes"]
          and P.ABHIJIT_EXCLUDED_VARA == 3 and P.ABHIJIT_MUHURTA == 8)
    t = table_after(pages[("what-is-pradosh-kaal", "en")], "Where Pradosh Kaal matters")
    specs = {s.key: s for s in [*festivals.RECURRING, *festivals.FESTIVALS] if s.rule == "pradosh"}
    check("pradosh: one row per observance the engine tests at Pradosh",
          len(t) == len(specs) + 1 and {r[0] for r in t[1:]} == {s.name_en for s in specs.values()}
          and len(specs) >= 6)
    check("pradosh: Diwali needs Krishna Amavasya, Pradosh Vrat needs Trayodashi (both pakshas)",
          dict((r[0], r[1]) for r in t[1:])["Diwali (Lakshmi Puja)"] == "Krishna Amavasya"
          and dict((r[0], r[1]) for r in t[1:])["Pradosh Vrat"] == "Shukla Trayodashi · Krishna Trayodashi")
    t = table_after(pages[("what-is-panchang", "en")], "The five limbs")
    check("five limbs: divisions and sizes match the engine (30 x 12, 27 x 13°20′, 27 x 13°20′, 60 x 6, 7)",
          len(t) == 6 and [r[0] for r in t[1:]] == ["Tithi", "Vara", "Nakshatra", "Yoga", "Karana"]
          and 360 / 30 == 12 and abs(360 / 27 - 13 - 20 / 60) < 1e-9 and 360 / 60 == 6
          and len(P.TITHI_NAMES) == 15 and len(P.YOGA_NAMES) == 27 and len(P.VARA_NAMES) == 7
          and len(P.MOVABLE_KARANAS) + len(P.FIXED_KARANAS) == 11)
    t = table_after(pages[("what-is-mangal-dosha", "en")], "What the engine checks")
    check("mangal: weights Lagna 1.0, Moon 0.5, Venus 0.3 are the ones in doshas.py",
          [r[1] for r in t[1:]] == ["1.0", "0.5", "0.3"]
          and "int(is_manglik_lagna) * 1.0 + int(is_manglik_moon) * 0.5 + int(is_manglik_venus) * 0.3"
          in src)
    check("hindi pages carry the same table sizes",
          len(table_after(pages[("what-is-rahu-kaal", "hi")], "वार के अनुसार राहु काल")) == 8
          and len(table_after(pages[("what-is-nakshatra", "hi")], "27 नक्षत्र")) == 28
          and len(table_after(pages[("what-is-choghadiya", "hi")], "सात नाम")) == 8)

    # ------------------------------------------------------------------ links
    print("\n9. Links to the tools and the city Panchang")
    want = {
        "what-is-panchang": ["/panchang"], "what-is-tithi": ["/panchang", "/vrat-tyohar"],
        "what-is-nakshatra": ["/nakshatra", "/panchang"], "what-is-yoga-and-karana": ["/panchang"],
        "what-is-rahu-kaal": ["/rahu-kaal", "/panchang"], "what-is-choghadiya": ["/choghadiya", "/panchang"],
        "what-is-abhijit-muhurat": ["/panchang", "/rahu-kaal"], "what-is-brahma-muhurta": ["/panchang"],
        "what-is-pradosh-kaal": ["/panchang", "/vrat-tyohar"], "what-is-sade-sati": ["/free-kundali"],
        "what-is-mangal-dosha": ["/free-kundali", "/kundali-milan"],
    }
    for s in SLUGS:
        for lang in ("en", "hi"):
            html, pre = pages[(s, lang)], i18n.prefix(lang)
            check(f"{s} [{lang}]: links the matching tool(s)",
                  all(f'href="{pre}{p}"' in html for p in want[s]))
            check(f"{s} [{lang}]: links a city Panchang and the CTA into the app",
                  f'href="{pre}/panchang/mumbai"' in html and 'class="cta" href="/?open=' in html)
            check(f"{s} [{lang}]: links the other 10 explainers and the index",
                  all(f'href="{L.page_path(o, lang)}"' in html for o in SLUGS if o != s)
                  and f'href="{L.page_path(None, lang)}"' in html)
    check("rahu kaal and choghadiya pages also link their city pages",
          'href="/rahu-kaal/mumbai"' in pages[("what-is-rahu-kaal", "en")]
          and 'href="/choghadiya/mumbai"' in pages[("what-is-choghadiya", "en")])
    internal = set()
    for (s, lang), html in pages.items():
        for href in re.findall(r'href="(/[^"#?]*)', html):
            internal.add(href)
    broken = sorted(h for h in internal if h.startswith(("/learn", "/hi/learn", "/panchang", "/hi/panchang",
                                                         "/rahu-kaal", "/choghadiya", "/nakshatra",
                                                         "/hi/nakshatra", "/vrat-tyohar", "/hi/vrat-tyohar",
                                                         "/free-kundali", "/hi/free-kundali",
                                                         "/kundali-milan", "/hi/kundali-milan",
                                                         "/sitemap", "/hi/sitemap"))
                    and client.get(h).status_code != 200)
    check("every internal link on the /learn pages resolves to a 200", not broken, str(broken[:5]))

    # --------------------------------------------------------------- regional
    print("\n10. Untranslated languages: English text, noindex, no hreflang, not in the sitemap")
    for code in REGIONAL:
        for s in (None, "what-is-rahu-kaal"):
            path = L.page_path(s, code)
            r = client.get(path)
            html = r.text
            check(f"{path}: 200", r.status_code == 200)
            check(f"{path}: noindex, follow", '<meta name="robots" content="noindex, follow"/>' in html)
            check(f"{path}: canonical is itself", canonical(html) == SITE + path)
            check(f"{path}: no hreflang alternates", 'rel="alternate" hreflang' not in html)
            check(f"{path}: English body", ("Rahu Kaal" in html) if s else ("Learn" in html))
            check(f"{path}: beacon counts it", analytics.is_public_page(path))
    check("a regional copy keeps the reader in their language",
          'href="/kn/panchang/mumbai"' in client.get("/kn/learn/what-is-rahu-kaal").text
          and 'href="/kn/learn/what-is-tithi"' in client.get("/kn/learn/what-is-rahu-kaal").text)

    # ---------------------------------------------- sitemap, hub, footer, beacon
    print("\n11. Sitemap, hub, footer and beacon include the family only when enabled")
    root = ET.fromstring(client.get("/sitemap.xml").text)
    locs = [e.text for e in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    learn_locs = sorted(u for u in locs if "/learn" in u)
    expected = sorted(SITE + p for p in [L.page_path(s, lang) for lang in ("en", "hi")
                                         for s in (None, *SLUGS)])
    check("sitemap.xml lists exactly the 24 canonical en/hi URLs", learn_locs == expected,
          str(len(learn_locs)))
    check("sitemap.xml lists no regional /learn copy", not any(f"/{c}/learn" in u for u in locs
                                                                for c in REGIONAL))
    check("sitemap.xml still has no duplicates", len(locs) == len(set(locs)))
    pr = seo_pages.sitemap_priority
    check("priorities: index 0.8, pages 0.7", pr("/learn") == 0.8 and pr("/learn/what-is-tithi") == 0.7)
    hub, hubhi = client.get("/sitemap").text, client.get("/hi/sitemap").text
    check("hub links the index and all 11 pages (en and hi)",
          all(f'href="{L.page_path(s, "en")}"' in hub for s in (None, *SLUGS))
          and all(f'href="{L.page_path(s, "hi")}"' in hubhi for s in (None, *SLUGS)))
    check("hub of a regional language has no /learn block (its copies are noindex)",
          "/learn" not in client.get("/kn/sitemap").text)
    check("footer of en and hi pages links /learn; regional footers do not",
          'href="/learn">Learn</a>' in client.get("/panchang").text
          and 'href="/hi/learn">जानें</a>' in client.get("/hi/panchang").text
          and "/learn" not in client.get("/kn/panchang").text)
    check("beacon: every canonical URL is public, and only those",
          all(analytics.is_public_page(p) for p in L.sitemap_paths())
          and not analytics.is_public_page("/learn/what-is-nothing")
          and not analytics.is_public_page("/learn/")
          and not analytics.is_public_page("/hi/learn/what-is-nothing"))

    # ----------------------------------------------------------------- review
    print("\n12. The owner's review document")
    doc = REVIEW.read_text(encoding="utf-8") if REVIEW.exists() else ""
    check("docs/learn-pages-review.md exists and equals review_markdown() (regenerate with "
          "`python -m app.learn_pages > docs/learn-pages-review.md`)", doc == L.review_markdown())
    check("NEEDS OWNER REVIEW at the top and in every page section",
          doc.count("NEEDS OWNER REVIEW") >= 12 and "NEEDS OWNER REVIEW" in doc[:400])
    for s in SLUGS:
        sec = doc.split(f"\n## {s}\n")[1].split("\n---\n")[0]
        e = PAGES[s]["en"]
        check(f"{s}: verbatim direct answer, method, convention and FAQ are in the review",
              e["answer"] in sec and all(m in sec for m in e["method"])
              and all(q in sec and a in sec for q, a in e["faq"]))
        check(f"{s}: a claims table with at least 4 sourced claims",
              len(CLAIMS[s]) >= 4 and all(c and src for c, src in CLAIMS[s]))
        check(f"{s}: rule tables are in the review",
              all(UI['en'][hk].format(city='New Delhi') in sec for hk, *_ in L.tables_for(s, "en")))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("learn pages: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
