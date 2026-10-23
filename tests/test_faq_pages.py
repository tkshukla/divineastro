"""FAQ blocks + FAQPage JSON-LD on the SEO pages (DIVASTRO-165).

/kundali-milan, /naam-se-kundali-milan (and a result), /panchang and the city
panchang pages, /rashifal/<sign>, /muhurat/<kind>-<year>, /nakshatra/<slug>,
/vrat-tyohar (+ city) and the katha stories, in every language each page is
published in. For every page:

  * exactly one FAQPage, valid JSON-LD; mainEntity Questions with a name and an
    acceptedAnswer.text (Google's FAQPage requirements);
  * every question and answer is on the page, verbatim (visible == JSON-LD);
  * every number and clock time in an answer also appears in the page's own data
    (the page with its FAQ block and JSON-LD cut out), so no answer carries a
    figure the page does not show; and, per page type, the answer quotes the very
    cell the page prints (Rahu Kaal, sunrise, the first muhurat dates, the score ...);
  * no untranslated English question on a translated regional page;
  * the daily answers follow the day (panchang on two pinned days) and the response
    is never cached past IST midnight; muhurat stays a static yearly list;
  * the sitemap gives the changed pages a lastmod, and IndexNow --daily submits
    them once.

    ~/.venvs/divineastro/bin/python -u -m tests.test_faq_pages
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

_tmp = tempfile.mkdtemp(prefix="astro_faq_pages_")
os.environ.setdefault("ASTRO_DATABASE_URL", f"sqlite:///{Path(_tmp).as_posix()}/t.db")
os.environ["ASTRO_DAILY_STATE_DIR"] = _tmp               # daily_state bookkeeping (IndexNow)
os.environ["ASTRO_INDEXNOW_KEY"] = "faq-test-key-0123"

from fastapi.testclient import TestClient  # noqa: E402

from app import (i18n, indexnow, katha, muhurat_pages, nakshatra_pages, rashifal_pages,  # noqa: E402
                 seo_pages, vrat_pages)
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
FAQ_DIV = re.compile(r'<div class="faq">.*?</div>', re.S)
NUM = re.compile(r"\d+(?::\d{2})?")
LATIN_WORD = re.compile(r"[A-Za-z]{4,}")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def pin(day: dt.date) -> None:
    """Every module's `_today` -> `day` (they import seo_pages._today by name)."""
    for name, mod in list(sys.modules.items()):
        if name.startswith("app.") and callable(getattr(mod, "_today", None)):
            setattr(mod, "_today", lambda d=day: d)


def graph(page: str) -> list[dict] | None:
    m = LD.search(page)
    try:
        return json.loads(m.group(1))["@graph"] if m else None
    except ValueError:
        return None


def faq_of(page: str) -> list[tuple[str, str]] | None:
    g = graph(page)
    faqs = [n for n in (g or []) if n.get("@type") == "FAQPage"]
    if len(faqs) != 1:
        return None
    return [(q.get("name", ""), (q.get("acceptedAnswer") or {}).get("text", ""))
            for q in faqs[0].get("mainEntity") or []]


def rest_of(page: str) -> str:
    """The page as a reader sees its data: without the FAQ block or the JSON-LD,
    tags dropped, entities decoded."""
    text = FAQ_DIV.sub(" ", LD.sub(" ", page))
    return htmllib.unescape(re.sub(r"<[^>]+>", " ", text))


def problems(path: str, page: str, status: int) -> list[str]:
    out = []
    if status != 200:
        return [f"HTTP {status}"]
    g = graph(page)
    if g is None:
        return ["JSON-LD does not parse"]
    faqs = [n for n in g if n.get("@type") == "FAQPage"]
    if len(faqs) != 1:
        return [f"{len(faqs)} FAQPage nodes"]
    qs = faqs[0].get("mainEntity") or []
    if not 3 <= len(qs) <= 5:
        out.append(f"{len(qs)} questions")
    rest = rest_of(page)
    for q in qs:
        a = (q.get("acceptedAnswer") or {})
        if q.get("@type") != "Question" or not q.get("name") or a.get("@type") != "Answer" \
                or not a.get("text"):
            out.append(f"malformed {q.get('name')!r}")
            continue
        name, text = q["name"], a["text"]
        if f"<h3>{htmllib.escape(name, quote=True)}</h3>" not in page:
            out.append(f"question not visible: {name!r}")
        if f"<p>{htmllib.escape(text, quote=True)}</p>" not in page:
            out.append(f"answer not visible: {text[:50]!r}")
        if "<" in text or "&lt;" in text or "{" in text:
            out.append(f"markup or a hole in {text[:50]!r}")
        missing = [n for n in NUM.findall(text) if n not in rest]
        if missing:
            out.append(f"numbers not on the page {missing} in {text[:60]!r}")
    if page.count('<div class="faq">') != 1:
        out.append("FAQ block count")
    lang = i18n.strip_prefix(path)[0]
    if lang not in ("en", "hi") and not path.startswith(("/katha", "/en/katha")):
        english = [q["name"] for q in qs if len(LATIN_WORD.findall(q["name"])) >= 3]
        if english:
            out.append(f"English question on a {lang} page: {english[0]!r}")
    return out


def run(paths: list[str], label: str, budget_ms: float | None = None) -> dict[str, str]:
    bad, pages, slow = [], {}, []
    for p in paths:
        t0 = time.perf_counter()
        r = client.get(p)
        ms = (time.perf_counter() - t0) * 1000
        pages[p] = r.text
        probs = problems(p, r.text, r.status_code)
        if probs:
            bad.append((p, probs[:2]))
        if budget_ms is not None and ms > budget_ms:
            slow.append((p, round(ms)))
    check(f"{label}: {len(paths)} pages, one valid FAQPage each, visible == JSON-LD, "
          "numbers from the page", not bad, str(bad[:3]))
    if budget_ms is not None:
        check(f"{label}: every page renders within {budget_ms:.0f} ms (warm)", not slow, str(slow[:3]))
    return pages


def answers(page: str) -> dict[str, str]:
    return {q: a for q, a in faq_of(page) or []}


def main() -> int:
    day = dt.date(2026, 11, 8)                         # Diwali: festival blocks render too
    pin(day)
    langs = {
        "seo": i18n.ordered(seo_pages.TRANSLATED),
        "rashifal": i18n.ordered(rashifal_pages.TRANSLATED),
        "muhurat": i18n.ordered(muhurat_pages.TRANSLATED),
        "nakshatra": i18n.ordered(nakshatra_pages.TRANSLATED),
        "vrat": i18n.ordered(vrat_pages.TRANSLATED),
    }
    check("every page module is published in 13 languages", all(len(v) == 13 for v in langs.values()),
          str({k: len(v) for k, v in langs.items()}))
    pre = i18n.prefix

    print("1. /kundali-milan")
    km = run([pre(l) + "/kundali-milan" for l in langs["seo"]], "kundali-milan")
    a = answers(km["/kundali-milan"])
    gunas = a.get("How many gunas are needed for marriage?", "")
    check("the gunas answer gives the engine's 36 / 18 and its four bands",
          "Out of 36 gunas, 18 is the conventional minimum" in gunas
          and "Below 18: Not recommended; 18–24: Acceptable; 25–32: Good; 33–36: Excellent" in gunas, gunas)
    mangal = a.get("What is Manglik dosh and when is it cancelled?", "")
    check("the Manglik answer names the engine's houses and the both-Manglik cancellation",
          "1st, 2nd, 4th, 7th, 8th or 12th" in mangal and "both" in mangal, mangal)
    check("the Hindi page asks in Hindi", "विवाह के लिए कितने गुण मिलने चाहिए?" in answers(km["/hi/kundali-milan"]))

    print("2. /naam-se-kundali-milan and a result")
    nm = run([pre(l) + "/naam-se-kundali-milan" for l in langs["nakshatra"]], "naam milan")
    check("the bare page has the three general questions", len(faq_of(nm["/naam-se-kundali-milan"])) == 3)
    res_paths = [pre(l) + "/naam-se-kundali-milan?boy=Ram&girl=Sita" for l in langs["nakshatra"]]
    res = run(res_paths, "naam milan result")
    page = res[res_paths[0]]
    total = re.search(r'<p class="total"><strong>Total: ([\d.]+ / 36)</strong> — ([^<]+)</p>', page)
    a = answers(page)
    score = a.get("How many gunas match for this pair?", "")
    check("a result adds this pair's score: the same total and verdict as the result box",
          total is not None and score.startswith(f"{total.group(1).replace(' / ', ' of ')} gunas — "
                                                 f"{htmllib.unescape(total.group(2))}"), score)
    check("...and Nadi/Bhakoot points from the koota table",
          re.search(r"Nadi scores \d+ of 8 and Bhakoot \d+ of 7", a.get(
              "Is there Nadi or Bhakoot dosha in this match?", "")) is not None)
    check("no name in the result's FAQ (names are personal data)",
          all("Ram" not in q + x and "Sita" not in q + x for q, x in faq_of(page)))
    check("the result stays noindex / no-store",
          "noindex" in page and client.get(res_paths[0]).headers["cache-control"] == "no-store")

    print("3. /panchang and city panchang pages")
    cities = ("", "/mumbai", "/bengaluru", "/kolkata", "/pune")
    pan_paths = [pre(l) + "/panchang" + c for l in langs["seo"] for c in cities]
    for p in pan_paths[:3]:
        client.get(p)                                  # warm the day's almanac
    pan = run(pan_paths, "panchang", budget_ms=1000)
    page = pan["/panchang/mumbai"]
    a = answers(page)
    rahu = re.search(r"<th scope=\"row\">Rahu Kaal</th><td>([^<]+)</td>", page).group(1)
    sunrise = re.search(r"<th scope=\"row\">Sunrise</th><td>([^<]+)</td>", page).group(1)
    sunset = re.search(r"<th scope=\"row\">Sunset</th><td>([^<]+)</td>", page).group(1)
    rq = a.get("What is the Rahu Kaal time today in Mumbai?", "")
    sq = a.get("What time is sunrise and sunset today in Mumbai?", "")
    check("Rahu Kaal answer quotes the table's Rahu Kaal cell, with the date",
          htmllib.unescape(rahu) in rq and "8 November 2026" in rq, f"{rahu!r} / {rq!r}")
    check("sunrise answer quotes the table's sunrise and sunset", htmllib.unescape(sunrise) in sq
          and htmllib.unescape(sunset) in sq, sq)
    hi = answers(pan["/hi/panchang"])
    check("Hindi panchang questions are Hindi", "आज नई दिल्ली में राहु काल कब है?" in hi, str(list(hi)[:2]))
    r = client.get("/panchang")
    cc = r.headers["cache-control"]
    ist = dt.datetime.now(seo_pages.IST)
    left = (dt.datetime.combine(ist.date() + dt.timedelta(days=1), dt.time(), seo_pages.IST) - ist).total_seconds()
    max_age = int(re.search(r"max-age=(\d+)", cc).group(1))
    check("panchang is never cached past IST midnight (so the FAQ is today's)",
          cc.startswith("private") and max_age <= max(60, left) + 1, cc)
    pin(day + dt.timedelta(days=1))
    nxt = client.get("/panchang/mumbai").text
    na = answers(nxt)
    rahu2 = re.search(r"<th scope=\"row\">Rahu Kaal</th><td>([^<]+)</td>", nxt).group(1)
    check("the next day's FAQ is that day's (date and Rahu Kaal both follow the table)",
          "9 November 2026" in na.get("What is the Rahu Kaal time today in Mumbai?", "")
          and htmllib.unescape(rahu2) in na.get("What is the Rahu Kaal time today in Mumbai?", "")
          and na != a)
    pin(day)

    print("4. /rashifal/<sign>")
    ras = run([rashifal_pages.path(r, l) for l in langs["rashifal"] for r in rashifal_pages.RASHIS],
              "rashifal signs", budget_ms=1000)
    page = ras["/rashifal/mesh"]
    a = answers(page)
    today = a.get("What does today's Mesh rashifal say?", "")
    house = re.search(r"the Moon is in your (\d+\w\w) house from Mesh", page)
    check("today's answer: the summary box's house and tone, for the page's date",
          house is not None and f"your {house.group(1)} house from Mesh" in today
          and "Sunday, 8 November 2026" in today, today[:120])
    sade = a.get("Is Sade Sati running for Mesh?", "")
    check("Sade Sati answer = the page's Sade Sati box", htmllib.unescape(re.sub(
        r"<[^>]+>", "", re.search(r'<div class="box"><p>(<strong>(?:Sade Sati is running|No Sade Sati)'
                                   r'.*?)</p></div>', page).group(1))) in sade, sade)
    check("the rashifal index has no FAQ (not asked for)", faq_of(client.get("/rashifal").text) is None)

    print("5. /muhurat/<kind>-<year>")
    mu_paths = [muhurat_pages.page_path(k, y, l) for y in muhurat_pages.YEARS
                for k in muhurat_pages.KINDS for l in langs["muhurat"]]
    mu = run(mu_paths, "muhurat")
    for p in ("/muhurat/vivah-2026", "/muhurat/griha-pravesh-2027", "/muhurat/mundan-2026"):
        page = mu[p]
        rows = re.findall(r'<tr data-date="[\d-]+"><td>([^<]+)</td><td>([^<]+)</td>', page)
        first = ", ".join(f"{htmllib.unescape(d)} ({htmllib.unescape(w)})" for d, w in rows[:5])
        count = re.search(r"there are <strong>(\d+)</strong>", page).group(1)
        dates_a = next((x for q, x in faq_of(page) if q.endswith(" dates?")), "")
        check(f"{p}: the dates answer = the intro's count and the first five table rows, in order",
              f"There are {count} " in dates_a and dates_a.endswith(f"The first ones: {first}."), dates_a)
    check("muhurat stays a static yearly list (public, a day)",
          client.get("/muhurat/vivah-2026").headers["cache-control"] == "public, max-age=86400")

    print("6. /nakshatra/<slug>")
    nak_paths = [nakshatra_pages.nak_path(n, l) for l in langs["nakshatra"]
                 for n in nakshatra_pages.NAKSHATRA_LIST]
    nak = run(nak_paths, "nakshatra", budget_ms=1000)
    a = answers(nak["/nakshatra/rohini"])
    check("Rohini: the fact table's rashi, lord, gana, yoni, nadi and syllables",
          "falls in Vrishabh (Taurus)" in a.get("Which rashi is Rohini nakshatra in, and who rules it?", "")
          and "Moon (10-year mahadasha)" in a.get("Which rashi is Rohini nakshatra in, and who rules it?", "")
          and "Manushya gana, Serpent yoni and Antya nadi" in a.get(
              "What are the gana, yoni and nadi of Rohini nakshatra?", "")
          and "(O, Va, Vi, Vu)" in a.get("What are the name letters of Rohini nakshatra?", ""), str(a)[:200])
    check("the nakshatra index has no FAQ (not asked for)", faq_of(client.get("/nakshatra").text) is None)

    print("7. /vrat-tyohar and /vrat-tyohar/<city>")
    vr_paths = [vrat_pages.city_path(c, l) for l in langs["vrat"]
                for c in (vrat_pages.CITY, *[vrat_pages.seo_cities.BY_SLUG[s] for s in ("mumbai", "chennai")])]
    vr = run(vr_paths, "vrat hub")
    page = vr["/vrat-tyohar"]
    a = answers(page)
    today_a = a.get("Which vrat or festival is today in New Delhi?", "")
    check("today's answer names today's observances from the box (Diwali on 8 Nov 2026)",
          "Diwali" in today_a and "8 November 2026" in today_a, today_a)
    nxt = a.get("What are the next vrat and festivals in New Delhi?", "")
    first_rows = re.findall(r'<tr data-date="[\d-]+" data-key="[^"]+"><td>([^<]+)</td><td>(?:<a [^>]+>)?([^<]+)',
                            page)[:5]
    check("next answer = the first five rows of the 30-day table, with their days",
          nxt == "In the next 30 days in New Delhi: " + "; ".join(
              f"{htmllib.unescape(n)} — {htmllib.unescape(d)}" for d, n in first_rows) + ".", nxt)
    check("the year list keeps no FAQ (only the hub and city pages)",
          faq_of(client.get("/vrat-tyohar/2026").text) is None)

    print("8. katha stories")
    kp = [katha.page_path(s, l) for s in katha.STORIES for l in (katha.HI, katha.EN)]
    kt = run(kp, "katha")
    s = katha.STORIES["savitri-satyavan"]
    a = answers(kt["/katha/savitri-satyavan"])
    check("the story's summary, source and message, from its file",
          a.get(f"“{s.hi.title}” की कथा किस बारे में है?") == s.hi.summary
          and s.hi.source in a.get(f"“{s.hi.title}” की कथा किस ग्रंथ से है?", "")
          and "*" not in json.dumps(a, ensure_ascii=False), str(a)[:200])
    check("the katha index has no FAQ", faq_of(client.get("/katha").text) is None)

    print("9. pages that already had a FAQ keep exactly one")
    for p in ("/free-kundali", "/hi/free-kundali", "/pricing", "/tyohar/diwali-2026"):
        g = graph(client.get(p).text) or []
        check(f"{p}: one FAQPage", sum(n.get("@type") == "FAQPage" for n in g) == 1)

    print("10. sitemap lastmod and IndexNow")
    xml = client.get("/sitemap.xml").text
    by = {m.group(1): m.group(0) for m in re.finditer(r"<url><loc>([^<]+)</loc>.*?</url>", xml)}
    rel = seo_pages.FAQ_RELEASE
    for p in ("/kundali-milan", "/hi/naam-se-kundali-milan", "/muhurat/vivah-2026", "/nakshatra/rohini",
              "/ta/vrat-tyohar/mumbai", "/katha/savitri-satyavan", "/en/katha/savitri-satyavan"):
        check(f"sitemap: {p} has lastmod {rel} (no daily changefreq)",
              f"<lastmod>{rel}</lastmod>" in by.get(SITE + p, "") and "changefreq" not in by.get(SITE + p, ""))
    for p in ("/nakshatra", "/katha", "/vrat-tyohar/2026", "/terms"):
        check(f"sitemap: unchanged {p} has no lastmod", "<lastmod>" not in by.get(SITE + p, "x<lastmod>"))
    check("sitemap: the daily pages still say today + daily",
          f"<lastmod>{day.isoformat()}</lastmod><changefreq>daily</changefreq>" in by[SITE + "/panchang/mumbai"])
    release = dt.date.fromisoformat(rel)
    before = indexnow.daily_paths(release - dt.timedelta(days=1))
    on = indexnow.daily_paths(release)
    changed = [p for p in seo_pages.sitemap_paths() if seo_pages.content_changed(p)
               and not re.match(r"^(/[a-z]{2})?/vrat-tyohar/", p)]     # city pages: left to the sitemap
    check("IndexNow --daily: nothing extra before the release day; every changed page on it",
          "/kundali-milan" not in before and all(p in on for p in changed) and len(on) == len(set(on))
          and "/vrat-tyohar/mumbai" not in on and len(on) < 2500,
          f"{len(changed)} changed, {len(on)} daily")

    class Fake:
        def __init__(self):
            self.calls = []

        def __call__(self, endpoint, payload):
            self.calls.append(payload)
            return 200

    f = Fake()
    code = indexnow.main(["--daily", "--date", rel], transport=f)
    sent = {u for c in f.calls for u in c["urlList"]}
    check("the release day's --daily submits the changed pages", code == 0
          and SITE + "/nakshatra/rohini" in sent and SITE + "/hi/muhurat/mundan-2027" in sent)
    nxt_day = (release + dt.timedelta(days=1)).isoformat()
    f2 = Fake()
    indexnow.main(["--daily", "--date", nxt_day], transport=f2)
    sent2 = {u for c in f2.calls for u in c["urlList"]}
    check("...once: the next day's batch is back to the daily pages",
          SITE + "/nakshatra/rohini" not in sent2 and SITE + "/panchang" in sent2, str(len(sent2)))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
