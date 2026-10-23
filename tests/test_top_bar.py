"""The WhatsApp bar under the answer box (DIVASTRO-164).

"Forward to family" and "Join our WhatsApp channel" sit straight under the
answer a visitor came for, on every content page type, not only in the strip
at the foot. Pins: the bar is there exactly once, right after the answer box;
its share text is the page's own (the strip's: the title, which carries the
answer) tagged utm_campaign=top-share; both links carry data-detail="top" for
strip.js; all 13 languages have both labels; the admin report has labels for
the top taps; and the daily WhatsApp channel post ends with the forward line.

No server needed (FastAPI's in-process client), throwaway SQLite database.

    ~/.venvs/divineastro/bin/python -u -m tests.test_top_bar
"""

from __future__ import annotations

import datetime as dt
import html
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if "ASTRO_DATABASE_URL" not in os.environ:
    _tmp = tempfile.mkdtemp(prefix="astro_topbar_")
    os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, daily_message, i18n, katha, stay_strip  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []

BAR = '<div class="wa-top">'
WA = "https://wa.me/?text="


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def _after_box(before: str) -> bool:
    """The bar follows the close of a .box with no heading in between."""
    return (before.rstrip().endswith("</div>")
            and before.rfind('<div class="box') > max(before.rfind("<h2"), before.rfind("<h3")))


def _after_first_para(before: str) -> bool:
    """Katha: after the story's first paragraph (the source line, then one <p>)."""
    tail = before[before.rfind('<p class="date">'):]
    return before.endswith("</p>") and tail.count("<p>") == 1


def _after_cta(before: str) -> bool:
    return before.rstrip().endswith("</a>") and before.rfind('class="cta"') > before.rfind("<h2")


def _after_form(before: str) -> bool:
    return before.rstrip().endswith("</form>")


KATHA = sorted(katha.STORIES)[0]
# (path, where it must sit, a time the page's answer gives that the share text must carry)
PAGES = (
    ("/hi/tyohar/karwa-chauth-2026/lucknow", _after_box, True),     # tyohar city, Hindi
    ("/tyohar/karwa-chauth-2026/lucknow", _after_box, True),        # tyohar city, English
    ("/tyohar/diwali-2026", _after_box, False),                     # tyohar
    ("/hi/tyohar/diwali-2026", _after_box, False),
    ("/kn/tyohar/diwali-2026", _after_box, False),                  # a regional language
    ("/vrat-tyohar", _after_box, False),                            # vrat hub
    ("/hi/vrat-tyohar/lucknow", _after_box, False),                 # vrat city
    ("/purnima-2026", _after_box, False),                           # recurring date page
    ("/hi/amavasya-2026", _after_box, False),
    ("/muhurat/vivah-2026", _after_box, False),                     # muhurat
    ("/hi/muhurat/griha-pravesh-2026", _after_box, False),
    (f"/katha/{KATHA}", _after_first_para, False),                  # katha (Hindi canonical)
    (f"/en/katha/{KATHA}", _after_first_para, False),
    ("/panchang", _after_box, False),                               # panchang
    ("/hi/panchang/lucknow", _after_box, False),                    # city panchang
    ("/ta/panchang/chennai", _after_box, False),
    ("/kundali-milan", _after_cta, False),                          # kundali milan
    ("/mr/kundali-milan", _after_cta, False),
    ("/naam-se-kundali-milan", _after_form, False),                 # naam se milan (no result yet)
    ("/hi/naam-se-kundali-milan", _after_form, False),
)

_HREF = re.compile(r'<a class="share-wa" href="([^"]+)"[^>]*data-strip="(strip_\w+)" data-detail="(\w+)"')


def bar_links(page: str) -> dict[str, tuple[str, str]]:
    """strip event name -> (href, detail) for the links inside the top bar."""
    i = page.find(BAR)
    chunk = page[i:page.find("</div>", i)]
    return {m.group(2): (html.unescape(m.group(1)), m.group(3)) for m in _HREF.finditer(chunk)}


def page_checks() -> None:
    print("\n1. The bar on every page type, right under the answer")
    for path, where, timed in PAGES:
        r = client.get(path)
        page = r.text
        check(f"{path}: 200", r.status_code == 200, str(r.status_code))
        check(f"{path}: exactly one bar", page.count(BAR) == 1, str(page.count(BAR)))
        i = page.find(BAR)
        check(f"{path}: straight after the answer ({where.__name__})", i > 0 and where(page[:i]),
              page[max(0, i - 120):i])
        check(f"{path}: above the strip at the foot",
              0 < i < page.find('id="stay-strip"'), "")
        links = bar_links(page)
        share, chan = links.get("strip_share"), links.get("strip_channel")
        check(f"{path}: two links, both detail=top",
              bool(share and chan) and share[1] == chan[1] == "top", str(links))
        if not (share and chan):
            continue
        check(f"{path}: channel link", chan[0] == stay_strip.CHANNEL_URL, chan[0])
        raw = share[0][len(WA):]
        check(f"{path}: a fully encoded wa.me link",
              share[0].startswith(WA) and not re.search(r"[\s#&?]", raw), share[0][:80])
        text = unquote(raw)
        url = text.rsplit(" ", 1)[-1]
        q = parse_qs(urlsplit(url).query)
        title = html.unescape(re.search(r"<title>(.*?)</title>", page, re.S).group(1))
        check(f"{path}: the share text is the page's (its title, as the strip's)",
              text == f"{title} {url}", text[:120])
        check(f"{path}: links this page, utm_campaign=top-share",
              urlsplit(url).path == path and q == {"utm_source": ["whatsapp"], "utm_medium": ["share"],
                                                     "utm_campaign": ["top-share"]}, url)
        if timed:
            box = page[page.find('<div class="box answer">'):i]
            times = set(re.findall(r"\d{1,2}:\d{2}", text))
            check(f"{path}: the share text carries the answer's time",
                  bool(times) and all(t in box for t in times), str(times))
        # the bottom strip is unchanged: its own share keeps page-share, no detail
        strip = page[page.find('id="stay-strip"'):]
        check(f"{path}: the foot strip still shares with page-share",
              "utm_campaign%3Dpage-share" in strip and 'data-detail' not in strip)

    # A Naam Milan result: under the score box, and never the names in the shared URL.
    r = client.get("/hi/naam-se-kundali-milan?boy=Ram&girl=Sita")
    page = r.text
    i = page.find(BAR)
    check("naam milan result: one bar, under the score box",
          page.count(BAR) == 1 and 'class="total"' in page[page.rfind('<div class="box', 0, i):i]
          and page[:i].rstrip().endswith("</div>"), page[max(0, i - 120):i])
    share = bar_links(page).get("strip_share", ("", ""))[0]
    check("naam milan result: no names in the share link",
          "Ram" not in unquote(share) and "Sita" not in unquote(share), unquote(share)[-120:])


def text_checks() -> None:
    print("\n2. 13 languages")
    codes = i18n.CODES
    check("13 languages", len(codes) == 13, str(codes))
    for code in codes:
        fw, ch = stay_strip.TEXT.get(code, {}).get("forward"), stay_strip.TEXT.get(code, {}).get("channel")
        check(f"{code}: both labels", bool(fw) and bool(ch), f"{fw} / {ch}")
        if code != "en":
            check(f"{code}: translated", fw != stay_strip.TEXT["en"]["forward"], fw or "")
    for code in ("en", "hi", "pa", "as"):
        page = client.get(("" if code == "en" else f"/{code}") + "/tyohar/diwali-2026").text
        check(f"{code}: the bar shows its own text",
              f"<span>{html.escape(stay_strip.TEXT[code]['forward'])}</span>" in page)


def analytics_checks() -> None:
    print("\n3. Analytics")
    for name in ("strip_share", "strip_channel"):
        check(f"{name} is an event", name in analytics.EVENT_NAMES)
        check(f"{name}/top has its own label", (name, "top") in analytics.EVENT_LABELS)
    js = (ROOT / "app/static/strip.js").read_text(encoding="utf-8")
    check("strip.js sends the link's data-detail", "dataset.detail" in js and ".wa-top" in js)


def post_checks() -> None:
    print("\n4. The daily WhatsApp channel post")
    day = dt.date(2026, 10, 24)
    for lang in ("hi", "en"):
        wa = daily_message.channel_message(day, lang=lang, channel="whatsapp")
        check(f"{lang}: ends with the forward line and the channel link",
              wa.rstrip().endswith(stay_strip.forward_line(lang)), wa.splitlines()[-1])
        tg = daily_message.channel_message(day, lang=lang, channel="telegram")
        check(f"{lang}: Telegram keeps its own line, no WhatsApp link",
              stay_strip.CHANNEL_URL not in tg)
    check("hi forward line is Hindi", "परिवार" in stay_strip.forward_line("hi"))


def main() -> int:
    page_checks()
    text_checks()
    analytics_checks()
    post_checks()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("top bar: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
