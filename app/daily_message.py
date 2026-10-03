"""The daily Panchang message for the Telegram and WhatsApp channels (DIVASTRO-113).

    channel_message(day, lat, lon, tz, lang, channel) -> str
    build(day, lat, lon, tz, lang)                    -> {"title", "body", "url"}

One short, forwardable post a day, for New Delhi unless told otherwise:

    date + vaar · tithi (with its end time) · nakshatra · sunrise / sunset ·
    Rahu Kaal · Abhijit · today's vrat/festivals with their first validated
    timing, or their tithi span when they have none (app/astro/festivals.py — the same data as /vrat-tyohar) · one line
    on where the Moon is, linking to today's rashifal · links to /panchang,
    /vrat-tyohar and /rashifal.

Every link carries utm_source=<channel>&utm_medium=channel&utm_campaign=
daily-<date>, so the admin Traffic panel attributes the visits. The Hindi post
is full Devanagari (times as "सुबह 6:14", as the Hindi pages print them) and
links to the /hi/ pages; the English one links to the English pages.

`channel` picks the markup:
  * "telegram" — HTML parse mode: text escaped, bold as <b>…</b>;
  * "whatsapp" — *bold*, the one markup WhatsApp renders (anything else would
    show raw);
  * "plain"    — no markup at all.

Times come from the same engine and the same formatting helpers as the
server-rendered /panchang pages, so the post and the site always agree.
"""

from __future__ import annotations

import datetime as dt
import html
from urllib.parse import urlencode

from . import rashifal_pages, seo_cities, seo_pages, vrat_pages
from .astro import festivals
from .astro import panchang as panchang_engine
from .astro.names_hi import NAKSHATRAS_HI, PAKSHA_HI, TITHI_HI, VARA_HI

EN, HI = seo_pages.EN, seo_pages.HI
CHANNELS = ("telegram", "whatsapp", "plain")
TELEGRAM_LIMIT = 4096          # sendMessage text limit, after entity parsing
CITY = seo_cities.DEFAULT      # New Delhi

# Bold markers, swapped for the channel's own markup at the very end (after
# Telegram's HTML escaping, which leaves these control characters alone).
_B, _EB = "\x01", "\x02"


def _bold(text: str) -> str:
    return f"{_B}{text}{_EB}"


def utm_url(path: str, channel: str, day: dt.date) -> str:
    """Absolute divineastro.org URL tagged for this channel and day."""
    source = "whatsapp" if channel == "whatsapp" else "telegram"
    query = urlencode({"utm_source": source, "utm_medium": "channel",
                       "utm_campaign": f"daily-{day.isoformat()}"})
    return f"{seo_pages.SITE_URL}{path}?{query}"


def _path(page: str, lang: str) -> str:
    return f"/hi/{page}" if lang == HI else f"/{page}"


def _at(iso: str | None, day: dt.date, lang: str) -> str:
    return seo_pages._time(iso, day, lang)


def _span(window: dict | None, day: dt.date, lang: str) -> str:
    return seo_pages._span(window, day, lang)


def _current(entries: list[dict], moment: str) -> tuple[dict | None, dict | None]:
    """The limb prevailing at `moment` (sunrise) and the one after it."""
    for i, e in enumerate(entries):
        if e["starts"] <= moment < e["ends"] or (i == 0 and moment < e["starts"]):
            return e, entries[i + 1] if i + 1 < len(entries) else None
    return (entries[0] if entries else None), None


def _tithi_name(t: dict, lang: str, paksha: bool = True) -> str:
    if lang == HI:
        name = TITHI_HI.get(t["name"], t["name"])
        return f"{PAKSHA_HI.get(t['paksha'], t['paksha'])} {name}" if paksha else name
    return f"{t['paksha']} {t['name']}" if paksha else t["name"]


def _nak_name(n: dict, lang: str) -> str:
    return NAKSHATRAS_HI.get(n["name"], n["name"]) if lang == HI else n["name"]


def _until(name: str, nxt_name: str | None, end_iso: str, day: dt.date, lang: str) -> str:
    """'Krishna Saptami till 8:00 AM, then Ashtami'."""
    end = _at(end_iso, day, lang)
    if lang == HI:
        return f"{name} {end} तक" + (f", फिर {nxt_name}" if nxt_name else "")
    return f"{name} till {end}" + (f", then {nxt_name}" if nxt_name else "")


def _rashi_name(sign: int, lang: str) -> str:
    r = rashifal_pages.RASHIS[sign]
    return r.name_hi if lang == HI else f"{r.name} ({r.english})"


def _moon_line(day: dt.date, lang: str) -> str:
    """Where the Moon is today (the basis of the rashifal), one sentence."""
    segs = rashifal_pages.sky(day)["moon"]
    if len(segs) == 1:
        sign = _rashi_name(segs[0]["sign"], lang)
        return (f"आज चंद्रमा {sign} राशि में है।" if lang == HI
                else f"The Moon is in {sign} all day.")
    when = seo_pages._clock(segs[0]["until"], lang)
    a, b = _rashi_name(segs[0]["sign"], lang), _rashi_name(segs[1]["sign"], lang)
    return (f"आज {when} पर चंद्रमा {a} से {b} राशि में जाएगा।" if lang == HI
            else f"The Moon moves from {a} into {b} at {when}.")


def _festival_lines(day: dt.date, lat: float, lon: float, tz: str, lang: str) -> list[str]:
    try:
        rows = festivals.on(day, lat, lon, tz)
    except Exception:                                  # pragma: no cover - defensive
        return []
    lines = []
    for o in rows:
        lines.append(f"• {_bold(vrat_pages._name(o, lang))}")
        if o["timings"]:
            lines.append(f"   {vrat_pages._timing_text(o['timings'][0], day, lang)}")
        elif o.get("tithi"):
            # No puja window of its own (Jitiya, Kalashtami...): its tithi span.
            lines.append(f"   {vrat_pages._tithi_text(o, lang)}")
    return lines


def _date_line(day: dt.date, lang: str) -> str:
    weekday = day.strftime("%A")
    if lang == HI:
        return f"{seo_pages._long_date(day, HI)}, {VARA_HI.get(weekday, weekday)}"
    return f"{weekday}, {seo_pages._long_date(day, EN)}"


def _render(text: str, channel: str) -> str:
    if channel == "telegram":
        return html.escape(text, quote=False).replace(_B, "<b>").replace(_EB, "</b>")
    if channel == "whatsapp":
        return text.replace(_B, "*").replace(_EB, "*")
    return text.replace(_B, "").replace(_EB, "")


def channel_message(day: dt.date, lat: float = CITY.latitude, lon: float = CITY.longitude,
                    tz: str = CITY.timezone, lang: str = HI, channel: str = "plain",
                    place: tuple[str, str] | None = None) -> str:
    """The full daily post for `channel` ("telegram" | "whatsapp" | "plain").

    `place` is (English, Hindi) for the location line; it defaults to New
    Delhi, which is also the default location.
    """
    if channel not in CHANNELS:
        raise ValueError(f"unknown channel {channel!r}")
    hi = lang == HI
    place = place or (CITY.name, CITY.name_hi)
    p = panchang_engine.daily_panchang(day, lat, lon, tz)
    sunrise = p["sun"]["rise"] or f"{day.isoformat()}T06:00:00"
    m = p["muhurta"]

    tithi, tithi_next = _current(p["tithi"], sunrise)
    nak, nak_next = _current(p["nakshatra"], sunrise)

    lines = [
        _bold("🪔 आज का पंचांग" if hi else "🪔 Today's Panchang"),
        f"📅 {_date_line(day, lang)}",
        f"📍 {place[1] if hi else place[0]}",
        "",
    ]
    if tithi:
        lines.append(("🌙 तिथि: " if hi else "🌙 Tithi: ") + _until(
            _tithi_name(tithi, lang), _tithi_name(tithi_next, lang, paksha=False)
            if tithi_next else None, tithi["ends"], day, lang))
    if nak:
        lines.append(("⭐ नक्षत्र: " if hi else "⭐ Nakshatra: ") + _until(
            _nak_name(nak, lang), _nak_name(nak_next, lang) if nak_next else None,
            nak["ends"], day, lang))
    lines.append(("🌅 सूर्योदय: " if hi else "🌅 Sunrise: ") + _at(p["sun"]["rise"], day, lang))
    lines.append(("🌇 सूर्यास्त: " if hi else "🌇 Sunset: ") + _at(p["sun"]["set"], day, lang))
    if m.get("rahu_kaal"):
        lines.append(("⏰ राहु काल: " if hi else "⏰ Rahu Kaal: ") + _span(m["rahu_kaal"], day, lang))
    if m.get("abhijit"):
        lines.append(("✨ अभिजित मुहूर्त: " if hi else "✨ Abhijit Muhurat: ")
                     + _span(m["abhijit"], day, lang))

    fest = _festival_lines(day, lat, lon, tz, lang)
    if fest:
        lines += ["", _bold("🙏 आज के व्रत-त्योहार" if hi else "🙏 Vrat & festivals today"), *fest]

    lines += [
        "",
        "🔮 " + _moon_line(day, lang) + (" अपनी राशि का आज का राशिफल पढ़ें:" if hi
                                         else " Read today's rashifal for your sign:"),
        utm_url(_path("rashifal", lang), channel, day),
        "",
        ("📖 पूरा पंचांग, चौघड़िया: " if hi else "📖 Full Panchang & Choghadiya: ")
        + utm_url(_path("panchang", lang), channel, day),
        ("🪔 व्रत-त्योहार कैलेंडर: " if hi else "🪔 Vrat & festival calendar: ")
        + utm_url(_path("vrat-tyohar", lang), channel, day),
    ]
    return _render("\n".join(lines), channel)


def build(day: dt.date, lat: float = CITY.latitude, lon: float = CITY.longitude,
          tz: str = CITY.timezone, lang: str = HI, channel: str = "plain") -> dict:
    """{title, body, url}: the same message, split for callers that want a
    headline and a link of their own (e.g. a push notification)."""
    hi = lang == HI
    title = (f"आज का पंचांग · {_date_line(day, lang)}" if hi
             else f"Today's Panchang · {_date_line(day, lang)}")
    return {"title": title,
            "body": channel_message(day, lat, lon, tz, lang, channel),
            "url": utm_url(_path("panchang", lang), channel, day)}


def _compact_span(window: dict | None) -> str:
    """'9:12–10:41 AM' (one AM/PM when both ends share it) for the image card."""
    if not window:
        return "—"
    a = seo_pages._clock(seo_pages._local(window["start"]), EN)
    b = seo_pages._clock(seo_pages._local(window["end"]), EN)
    return f"{a[:-3]}–{b}" if a[-2:] == b[-2:] else f"{a}–{b}"


def card_text(day: dt.date, lat: float = CITY.latitude, lon: float = CITY.longitude,
              tz: str = CITY.timezone, place: str = CITY.name) -> tuple[str, str, str]:
    """(eyebrow, headline, subline) for the English-only image card
    (app/social_card.py cannot shape Devanagari)."""
    p = panchang_engine.daily_panchang(day, lat, lon, tz)
    rows = festivals.on(day, lat, lon, tz)
    eyebrow = f"{day.strftime('%a')} {day.day} {day.strftime('%b %Y')} · {place}"
    if rows:
        names = [o["name_en"] for o in rows]
        headline = " & ".join(names[:2]) + (" & more" if len(names) > 2 else "")
        if len(headline) > 55:
            headline = names[0]
    else:
        headline = "Today's Panchang"
    sub = (f"Rahu Kaal {_compact_span(p['muhurta'].get('rahu_kaal'))}"
           f" · Sunrise {_at(p['sun']['rise'], day, EN)}")
    return eyebrow, headline, sub
