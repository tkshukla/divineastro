"""Question first (DIVASTRO-167): the pieces a browser test cannot pin cheaply.

1. The content pages' "Have a question about your own chart?" strip: on the festival
   pages (hub, festival, festival-in-a-city) and both matching pages, exactly once,
   straight after the WhatsApp top bar and nowhere else; 2-3 plain links to
   /?ask=<question>&lang=<page lang>&utm_medium=ask (no utm_source: the visit stays
   "internal"); marriage questions on the matching pages; "free, no sign-in" only
   while the guest answer is on; all 13 languages.
2. The app: the home question box comes before the kundali button; every string it
   uses exists, translated, in all 13 language files; app.js reads ?ask= and reports
   the new events; visit.js never sends the question.
3. Analytics: ask_box_shown / ask_chip / ask_start are events with labels, and the
   admin funnel shows box -> start -> chart -> asked in that order.

    ~/.venvs/divineastro/bin/python -u -m tests.test_ask_first
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if "ASTRO_DATABASE_URL" not in os.environ:
    _tmp = tempfile.mkdtemp(prefix="astro_askfirst_")
    os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, guest, i18n, stay_strip  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
STATIC = ROOT / "app" / "static"
STRIP = '<nav class="ask-strip"'
BAR = '<div class="wa-top">'
HREF = re.compile(r'<a class="ask-strip-chip" href="([^"]+)">([^<]+)</a>')

# path -> kind
WITH = {
    "/vrat-tyohar": "tyohar",
    "/tyohar/diwali-2026": "tyohar",
    "/tyohar/ahoi-ashtami-2026/mumbai": "tyohar",
    "/kundali-milan": "milan",
    "/naam-se-kundali-milan": "naam-milan",
    "/naam-se-kundali-milan?boy=Rahul&girl=Priya": "naam-milan",
}
WITHOUT = ("/panchang", "/rashifal", "/muhurat/vivah-2026", "/nakshatra", "/katha/abhimanyu-chakravyuh", "/free-kundali")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def prefixed(path: str, lang: str) -> str:
    return path if lang == "en" else f"/{lang}{path}"


def page_checks() -> None:
    print("\n1. The question strip on the content pages")
    for lang in ("en", "hi", "pa", "ta"):
        for path, kind in WITH.items():
            url = prefixed(path, lang)
            r = client.get(url)
            body = r.text
            tag = f"{url}"
            check(f"{tag}: 200 and the strip exactly once", r.status_code == 200 and body.count(STRIP) == 1,
                  f"{r.status_code} x{body.count(STRIP)}")
            if STRIP not in body:
                continue
            at = body.index(STRIP)
            bar_end = body.rfind("</div>", 0, at)
            check(f"{tag}: straight after the WhatsApp top bar",
                  body.rfind(BAR, 0, at) >= 0 and body[bar_end:at].strip() == "</div>",
                  body[max(0, at - 80):at])
            strip = body[at:body.index("</nav>", at)]
            links = HREF.findall(strip)
            check(f"{tag}: 2-3 question links", 2 <= len(links) <= 3, str(len(links)))
            want = [stay_strip._tx(k, lang) for k in stay_strip.ASK_QUESTIONS[kind]]
            for href, text in links:
                u = urlsplit(html.unescape(href))
                qs = parse_qs(u.query)
                ok = (u.path == "/" and not u.netloc and qs.get("ask") == [html.unescape(text)]
                      and qs.get("lang") == [lang] and qs.get("utm_medium") == ["ask"]
                      and qs.get("utm_campaign") == [kind] and "utm_source" not in qs)
                check(f"{tag}: '{html.unescape(text)}' -> /?ask=..&lang={lang}&utm_medium=ask", ok, href)
            check(f"{tag}: the page's own questions", [html.unescape(t) for _h, t in links] == want)
            check(f"{tag}: no script in it (CSP)", "<script" not in strip and "onclick" not in strip)
            head = stay_strip._tx("ask_head", lang)
            check(f"{tag}: heading in the page's language", html.escape(head) in strip, head)
        if lang == "en":
            milan = HREF.findall(client.get("/kundali-milan").text)
            check("the matching page asks about marriage",
                  all("marri" in t.lower() or "mangal" in t.lower() for _h, t in milan), str(milan))
    for path in WITHOUT:
        r = client.get(path)
        check(f"{path}: no strip (only festival and matching pages)",
              r.status_code == 200 and STRIP not in r.text, str(r.status_code))

    page = client.get("/tyohar/diwali-2026").text
    first = page.index(STRIP)
    check("the page's own answer box comes first", page.find('<div class="box') < first)

    # The promise follows app/guest.py: no "free, no sign-in" while the guest answer is off.
    on = stay_strip.ask_strip(lang="en", kind="tyohar")
    old = guest.GUEST_ANSWERS
    try:
        guest.GUEST_ANSWERS = 0
        off = stay_strip.ask_strip(lang="en", kind="tyohar")
    finally:
        guest.GUEST_ANSWERS = old
    check("guest answer on: 'Ask free, no sign-in'", ("Ask free, no sign-in" in on) == (old > 0))
    check("guest answer off: no sign-in promise, just 'Ask the AI astrologer'",
          "no sign-in" not in off and "Ask the AI astrologer" in off)


def text_checks() -> None:
    print("\n2. 13 languages")
    keys = [k for k in stay_strip.TEXT["en"] if k.startswith("ask_")]
    check("the strip has its 8 strings", len(keys) == 8, str(keys))
    for code in i18n.CODES:
        table = stay_strip.TEXT.get(code, {})
        missing = [k for k in keys if not table.get(k)]
        same = [k for k in keys if code != "en" and table.get(k) == stay_strip.TEXT["en"][k]]
        check(f"{code}: every strip string, translated", not missing and not same, f"{missing} {same}")

    app_keys = ["askBoxTitle", "askBoxTitleGuest", "askBoxTitleLeft", "askBoxLabel", "askBoxPh", "askBoxGo",
                "askBoxTopics", "askChipMarriage", "askQMarriage", "askChipCareer", "askQCareer",
                "askChipMoney", "askQMoney", "askChipHealth", "askQHealth", "askChipMuhurat", "askQMuhurat",
                "askPendingNote"]
    en = json.loads((STATIC / "i18n" / "en.json").read_text(encoding="utf-8"))
    for code in i18n.CODES:
        t = json.loads((STATIC / "i18n" / f"{code}.json").read_text(encoding="utf-8"))
        missing = [k for k in app_keys if not t.get(k)]
        same = [k for k in app_keys if code != "en" and t.get(k) == en.get(k)]
        check(f"{code}.json: the question box strings, translated", not missing and not same, f"{missing} {same}")
        check(f"{code}.json: '{{n}}' kept in the balance heading", "{n}" in (t.get("askBoxTitleLeft") or ""))
    check("English heading: 'Ask your question — free, no sign-in'",
          en["askBoxTitleGuest"] == "Ask your question — free, no sign-in")


def app_checks() -> None:
    print("\n3. The app")
    index = (STATIC / "index.html").read_text(encoding="utf-8")
    home = index[index.index('id="stage-home"'):index.index('id="home-footer"')]
    order = ["home-tagline", "ask-box", "ask-home-q", "ask-home-go", "ask-chips", "home-cta", "free-badge", "today-strip"]
    pos = [home.find(f'id="{i}"') for i in order]
    check("home: tagline > question box (field, Ask, chips) > kundali button > badge > Today",
          all(p >= 0 for p in pos) and pos == sorted(pos), str(dict(zip(order, pos))))
    chips = re.findall(r'class="ask-chip" data-topic="(\w+)"', home)
    check("five topic chips", chips == ["marriage", "career", "money", "health", "muhurat"], str(chips))
    check("the birth step has the waiting question", 'id="ask-pending"' in index and 'id="ask-pending-q"' in index)
    check("no inline script added to the home box", "<script" not in home[home.index('id="ask-box"'):home.index('id="home-cta"')])
    app_js = (STATIC / "app.js").read_text(encoding="utf-8")
    for needle, what in (('daTrack?.("ask_box_shown", "home")', "ask_box_shown home"),
                         ('daTrack?.("ask_chip", b.dataset.topic)', "ask_chip <topic>"),
                         ('daTrack?.("ask_start", from)', "ask_start <from>"),
                         ('params.get("ask")', "reads ?ask="),
                         ('=== "ask" ? "page" : "link"', "page vs link from utm_medium"),
                         ('$("#ask-form").requestSubmit()', "sends through the chat's own form (ask_sent, guest path)")):
        check(f"app.js: {what}", needle in app_js)
    visit = (STATIC / "visit.js").read_text(encoding="utf-8")
    check("visit.js drops ?ask= from what it reports", "p.delete('ask')" in visit)


def analytics_checks() -> None:
    print("\n4. Analytics")
    for name in ("ask_box_shown", "ask_chip", "ask_start"):
        check(f"{name} is an event", name in analytics.EVENT_NAMES)
        check(f"{name} has a plain label", (name, "") in analytics.EVENT_LABELS)
    for d in ("marriage", "career", "money", "health", "muhurat"):
        check(f"ask_chip/{d} labelled", ("ask_chip", d) in analytics.EVENT_LABELS)
    for d in ("home", "page", "link"):
        check(f"ask_start/{d} labelled", ("ask_start", d) in analytics.EVENT_LABELS)
    check("ask_box_shown/home labelled", ("ask_box_shown", "home") in analytics.EVENT_LABELS)
    funnel = [n for _l, n, _d in analytics.APP_FUNNEL]
    steps = ["ask_box_shown", "ask_start", "chart_cast", "ask_sent"]
    check("the funnel: box -> start -> chart -> asked, in that order",
          all(s in funnel for s in steps) and [funnel.index(s) for s in steps] == sorted(funnel.index(s) for s in steps),
          str(funnel))
    check("a forged detail is cut to the event's length", analytics.parse_event({"name": "ask_start", "detail": "x" * 60})
          == ("ask_start", "x" * 40))


def main() -> int:
    page_checks()
    text_checks()
    app_checks()
    analytics_checks()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("question first: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
