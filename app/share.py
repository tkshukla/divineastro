"""WhatsApp share links (DIVASTRO-107).

This audience shares on WhatsApp, so the free tools carry a "Share on WhatsApp"
button where people naturally want to forward something: a Kundali Milan score,
today's Rahu Kaal / Panchang for their city, and the public SEO pages.

Every shared link carries `utm_source=whatsapp&utm_medium=share&utm_campaign=…`
so the visit beacon (static/visit.js -> analytics.classify_source) records the
landing as source "whatsapp", and the first-touch cookie stamps it on a sign-up.

Two pieces live here:

* `GET /api/share/cities` — the curated SEO city list (slug, names, centre),
  so the in-app buttons can link to /rahu-kaal/<slug> or /panchang/<slug> when
  the visitor's city has its own page. Tiny, static, and cacheable for a day.
* `whatsapp_href` / `seo_share` — the server-rendered link for the SEO pages.
  A plain wa.me link: it works without JavaScript and is what a crawler sees.

Nothing personal is ever put in a share text — no names, birth details or
places of birth. The in-app Milan text carries the score only.
"""

from __future__ import annotations

import html
from urllib.parse import quote, urlencode

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from . import seo_cities
from .legal import SITE

router = APIRouter(prefix="/api/share")

SITE_URL = SITE.rstrip("/")
WA_ME = "https://wa.me/?text="

# SEO tool slug -> (what the share text calls it, Hindi name).
SEO_TOOLS = {
    "panchang": ("Panchang", "पंचांग"),
    "rahu-kaal": ("Rahu Kaal", "राहु काल"),
    "choghadiya": ("Choghadiya", "चौघड़िया"),
    "kundali-milan": ("Kundali Milan", "कुंडली मिलान"),
}


def share_url(path: str, campaign: str) -> str:
    """An absolute divineastro.org URL tagged so analytics reads it as a WhatsApp share."""
    query = urlencode({"utm_source": "whatsapp", "utm_medium": "share", "utm_campaign": campaign})
    return f"{SITE_URL}{path}?{query}"


def whatsapp_href(text: str, url: str) -> str:
    """wa.me link whose prefilled message is `text` followed by `url`, fully encoded."""
    return WA_ME + quote(f"{text} {url}", safe="")


def _parts(path: str) -> list[str]:
    """Path segments without the /hi/ language prefix: a Hindi copy shares like its English twin."""
    parts = [p for p in path.split("/") if p]
    return parts[1:] if parts[:1] == ["hi"] else parts


def seo_share_text(path: str) -> str | None:
    """The message for an SEO page, from its path alone (/tool or /tool/<city>)."""
    parts = _parts(path)
    if not parts:
        return None
    if parts[0] == "free-kundali":
        return "Get your janam kundali free · अपनी जन्म कुंडली मुफ़्त में बनाएं:"
    if parts[0] == "rashifal":
        return "Today's Rashifal for every sign · आज का राशिफल:"
    if parts[0] == "muhurat" and len(parts) == 2:
        kind, _, year = parts[1].rpartition("-")
        names = {"vivah": ("Vivah muhurat", "विवाह मुहूर्त"),
                 "griha-pravesh": ("Griha Pravesh muhurat", "गृह प्रवेश मुहूर्त")}
        if kind not in names or not year.isdigit():
            return None
        name, name_hi = names[kind]
        return f"{name} {year} — all dates · {name_hi} {year} की तिथियां:"
    if parts[0] == "vrat-tyohar" and len(parts) == 1:
        return "Today's vrat & festivals with puja muhurat · आज के व्रत और त्योहार:"
    if parts[0] == "vrat-tyohar" and len(parts) == 2:
        if not parts[1].isdigit():
            return None
        return f"Vrat & festival calendar {parts[1]} · व्रत-त्योहार {parts[1]} की पूरी सूची:"
    if parts[0].startswith("ekadashi-") and len(parts) == 1:
        year = parts[0].removeprefix("ekadashi-")
        if not year.isdigit():
            return None
        return f"All Ekadashi {year} dates with parana time · एकादशी {year} व्रत और पारण समय:"
    if parts[0] == "tyohar" and len(parts) == 2:
        from .vrat_pages import festival_names   # lazy: vrat_pages imports this module
        slug, _, year = parts[1].rpartition("-")
        names = festival_names().get(slug)
        if names is None or not year.isdigit():
            return None
        return f"{names[0]} {year} — date & puja muhurat · {names[1]} {year} — तिथि और मुहूर्त:"
    if parts[0] not in SEO_TOOLS:
        return None
    name, name_hi = SEO_TOOLS[parts[0]]
    if parts[0] == "kundali-milan":
        return f"Check your Kundali Milan (36 guna) score free 💍 · {name_hi} मुफ़्त में देखें:"
    city = seo_cities.get(parts[1]) if len(parts) > 1 else seo_cities.DEFAULT
    if city is None:
        return None
    return f"Today's {name} in {city.name} · आज का {name_hi} — {city.name_hi}:"


def seo_share(path: str) -> str:
    """The share button for an SEO page: a plain wa.me link, no script needed."""
    text = seo_share_text(path)
    if text is None:
        return ""
    tool = _parts(path)[0]
    if tool.startswith("ekadashi-"):
        tool = "ekadashi"
    href = whatsapp_href(text, share_url(path, f"seo-{tool}"))
    label = "WhatsApp पर भेजें" if path.startswith("/hi/") else "Share on WhatsApp"
    return (f'<a class="share-wa" href="{html.escape(href)}" target="_blank" rel="noopener" '
            f'data-share="seo-{tool}">{_ICON}<span>{label}</span></a>')


# The WhatsApp glyph, simplified; decorative (the link text says what it does).
_ICON = ('<svg class="share-wa-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" '
         'focusable="false"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 '
         '10 0 1 0 12 2zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5'
         '-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7'
         '-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 '
         '0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2s.2-1.1.2-1.2-.2-.2-.5'
         '-.3z"/></svg>')


@router.get("/cities")
def share_cities() -> JSONResponse:
    """The SEO city list for the in-app share buttons. Changes only with a deploy."""
    body = {
        "default": seo_cities.DEFAULT.slug,
        "cities": [{"slug": c.slug, "name": c.name, "name_hi": c.name_hi,
                    "lat": c.latitude, "lon": c.longitude} for c in seo_cities.CITIES],
    }
    return JSONResponse(body, headers={"Cache-Control": "public, max-age=86400"})
