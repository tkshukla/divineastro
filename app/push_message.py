"""The one-line "today" message: a vrat/festival with its key timing, or else the
city's Rahu Kaal (DIVASTRO-112).

    build(day, lat, lon, tz, lang, *, city="", source="push",
          medium="notification", campaign="daily") -> {title, body, url, path}

Shared on purpose: the daily web push (app/push.py) sends it, and any other
daily channel (Telegram / WhatsApp broadcast) can send the very same text with
its own UTM tags. It knows nothing about push — no database, no network.

Every date and time comes from the same engines as the pages:
`astro.festivals.on` (rules validated against Drik Panchang; anything not
validated never comes out of it) and `astro.panchang.daily_panchang` for Rahu
Kaal. Times are printed as 24-hour HH:MM in the place's own timezone, which
reads the same in English and Hindi and fits a notification line.

    python -m app.push_message 2026-10-06 --lang hi       # preview
"""

from __future__ import annotations

import datetime as dt
import math
import os
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from . import seo_cities
from .astro import festivals
from .astro import panchang as panchang_engine

SITE_URL = os.environ.get("ASTRO_SITE_URL", "https://divineastro.org").rstrip("/")

MONTHS_HI = ("जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
             "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर")

# An SEO city counts as "the subscriber's city" within this distance (the same
# ~10 km idea as share.js's cityFor) — then the Rahu Kaal link is that city's
# own /rahu-kaal page and the Hindi text can use the city's Hindi name.
CITY_MATCH_KM = 15.0


def _km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def seo_city(lat: float, lon: float) -> seo_cities.City | None:
    """The SEO city whose centre is nearest (lat, lon), if within CITY_MATCH_KM."""
    best = min(seo_cities.CITIES, key=lambda c: _km(lat, lon, c.latitude, c.longitude))
    return best if _km(lat, lon, best.latitude, best.longitude) <= CITY_MATCH_KM else None


def city_name(lat: float, lon: float, label: str, lang: str) -> str:
    """'New Delhi' / 'नई दिल्ली': the picked label's first part, or the SEO
    city's Hindi name for a Hindi reader when the place is one of ours."""
    c = seo_city(lat, lon)
    if lang == "hi" and c:
        return c.name_hi
    short = (label or "").split(",")[0].strip()
    if short:
        return short
    if c:
        return c.name
    return "नई दिल्ली" if lang == "hi" else "New Delhi"


def _clock(iso: str, tz: str) -> dt.datetime:
    return dt.datetime.fromisoformat(iso).astimezone(ZoneInfo(tz))


def _hm(moment: dt.datetime) -> str:
    return moment.strftime("%H:%M")


def _short_date(day: dt.date, lang: str) -> str:
    return f"{day.day} {MONTHS_HI[day.month - 1] if lang == 'hi' else day.strftime('%b')}"


def timing_text(t: dict, day: dt.date, tz: str, lang: str) -> str:
    """'Parana (breaking the fast): 7 Oct, 06:17–08:37' — a validated timing,
    with the date added when it falls on another day (Ekadashi parana is the
    next morning)."""
    label = t.get("label_hi") if lang == "hi" else t.get("label_en")
    if t.get("at"):
        first = _clock(t["at"], tz)
        value = _hm(first)
    else:
        first = _clock(t["start"], tz)
        value = f"{_hm(first)}–{_hm(_clock(t['end'], tz))}"
    prefix = f"{_short_date(first.date(), lang)}, " if first.date() != day else ""
    return f"{label}: {prefix}{value}"


def _with_utm(path: str, source: str, medium: str, campaign: str) -> str:
    sep = "&" if "?" in path else "?"
    return path + sep + urlencode({"utm_source": source, "utm_medium": medium,
                                   "utm_campaign": campaign})


def rahu_kaal(day: dt.date, lat: float, lon: float, tz: str) -> tuple[str, str] | None:
    """('10:41', '12:10') in the place's timezone, or None."""
    p = panchang_engine.daily_panchang(day, lat, lon, tz)
    rk = (p.get("muhurta") or {}).get("rahu_kaal")
    if not rk or not rk.get("start") or not rk.get("end"):
        return None
    return _hm(_clock(rk["start"], tz)), _hm(_clock(rk["end"], tz))


def build(day: dt.date, lat: float, lon: float, tz: str, lang: str, *, city: str = "",
          source: str = "push", medium: str = "notification",
          campaign: str = "daily") -> dict:
    """Today's message for a place. `city` is the place's label as the visitor
    picked it ("Lucknow, Uttar Pradesh"); only its first part is printed.

    Returns {title, body, url (absolute, UTM-tagged), path (same, site-relative)}.
    """
    lang = "hi" if lang == "hi" else "en"
    hi = lang == "hi"
    name = city_name(lat, lon, city, lang)
    pre = "/hi" if hi else ""
    rk = rahu_kaal(day, lat, lon, tz)
    rk_text = f"{rk[0]}–{rk[1]}" if rk else "—"

    obs = festivals.on(day, lat, lon, tz)
    if obs:
        # A major festival first, else the engine's own order.
        obs = sorted(obs, key=lambda o: not o.get("major"))
        names = ", ".join((o["name_hi"] if hi else o["name_en"]) for o in obs[:2])
        title = f"आज: {names}" if hi else f"Today: {names}"
        timed = next((o for o in obs if o.get("timings")), None)
        if timed:
            body = f"{timing_text(timed['timings'][0], day, tz, lang)} · {name}"
        else:
            body = (f"राहु काल {rk_text} · {name}" if hi
                    else f"Rahu Kaal {rk_text} · {name}")
        path = f"{pre}/vrat-tyohar"
    else:
        if hi:
            title = f"आज का राहु काल: {rk_text} · {name}"
            body = "इस समय नया काम शुरू करने से बचें। आज का पूरा पंचांग देखें।"
        else:
            title = f"Today's Rahu Kaal in {name}: {rk_text}"
            body = "Avoid starting anything new in this window. Tap for today's full Panchang."
        c = seo_city(lat, lon)
        if c:
            path = f"{pre}/rahu-kaal" + ("" if c == seo_cities.DEFAULT else f"/{c.slug}")
        else:
            path = "/?open=panchang" + ("&lang=hi" if hi else "")
    path = _with_utm(path, source, medium, campaign)
    return {"title": title, "body": body, "url": SITE_URL + path, "path": path}


if __name__ == "__main__":                              # pragma: no cover - manual preview
    import argparse
    import json

    ap = argparse.ArgumentParser(description="Preview the daily message.")
    ap.add_argument("date", nargs="?", default=dt.date.today().isoformat())
    ap.add_argument("--lat", type=float, default=28.6139)
    ap.add_argument("--lon", type=float, default=77.2090)
    ap.add_argument("--tz", default="Asia/Kolkata")
    ap.add_argument("--city", default="New Delhi, Delhi")
    ap.add_argument("--lang", default="en", choices=("en", "hi"))
    a = ap.parse_args()
    print(json.dumps(build(dt.date.fromisoformat(a.date), a.lat, a.lon, a.tz, a.lang,
                           city=a.city), ensure_ascii=False, indent=2))
