"""Server-rendered public pages for the free tools, plus sitemap.xml and robots.txt.

Why these exist (DIVASTRO-100): the app is one single-page shell at `/`, so a
search engine sees one URL and a page of buttons. Panchang, Rahu Kaal and
Choghadiya are what people in India search for every morning, and none of it
was indexable. Each page here carries its content in the raw HTML — no script
has to run for a crawler (or a slow phone) to read today's tithi or Rahu Kaal.

DIVASTRO-106 added a full Hindi copy of every page under /hi/ (most of this
audience searches in Hindi), ~100 cities, and /free-kundali. Every page names
its other-language twin with reciprocal hreflang links and a visible switch.
The Hindi pages are written in Hindi, not machine-translated wrappers around
English: the limb names come from the same Hindi tables the app uses.

Everything shown is computed by the same engines the app uses
(`astro.panchang.daily_panchang` for the five limbs and the muhurta windows), so
a page can never disagree with the tool it links to on those numbers. Festival
names are deliberately NOT shown: `daily_panchang` reports the sunrise tithi,
which is the wrong rule for aparahna/pradosh-vyapini festivals (the 1-day-off
bug fixed in DIVASTRO-90 by separate helpers) — only the daily elements, which
the sunrise rule does get right, appear here.

Muhurat-of-the-year pages (vivah/griha pravesh 2026) were considered for
DIVASTRO-106 and deliberately not built: `astro.muhurat.find_muhurat` scores a
day on its sunrise tithi, nakshatra, vara, yoga and Bhadra only. It has no
notion of Chaturmas, Kharmas/Malmas, Pitru Paksha or Guru/Shukra asta, so it
rates ~10 days in every month of 2026 "Auspicious" for marriage — including
August to mid-November and mid-December to mid-January, when no Hindu
almanac lists a vivah muhurat. Fine as an in-app filter; wrong as a public list.

Rendering follows legal.py: a format-string shell, no template engine (Jinja is
not a dependency and this does not justify one). Every interpolated value goes
through `_e` even though the cities are curated — the habit is cheaper than the
audit.
"""

from __future__ import annotations

import datetime as dt
import functools
import html
import json
import math
from xml.sax.saxutils import escape as xml_escape
from zoneinfo import ZoneInfo

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from . import i18n, lang_data, seo_cities
from .astro import choghadiya as chog
from .astro import matching
from .astro import panchang as panchang_engine
# The Hindi limb names: one copy, shared with main.py, muhurat.py and /api/panchang.
# (Re-exported: tests and older callers import them from here.)
from .astro.names_hi import KARANA_HI, NAKSHATRAS_HI, TITHI_HI, VARA_HI, YOGA_HI  # noqa: F401
from .astro.vargas import DEFAULT_DIVISIONS
from .legal import ADDRESS, BRAND, EMAIL, LEGAL_NAME, PHONE, SITE, registration_inline
from .seo_cities import City
# DIVASTRO-123: every word of these pages is in seo_text.TEXT / FAQ, per language.
from .seo_text import FAQ, TEXT

router = APIRouter()

IST = ZoneInfo("Asia/Kolkata")
SITE_URL = SITE.rstrip("/")

# Same publisher as index.html. main.py owns ADSENSE_PUBLISHER for /ads.txt but
# importing main from here would be circular; tests/test_seo_pages.py checks
# the two agree.
ADSENSE_CLIENT = "ca-pub-1593974697916149"

EN, HI = "en", "hi"

# DIVASTRO-121: the languages this module's pages are really written in. Every
# registry language gets a page (/kn/panchang ...), but one whose language is
# not listed here renders the English text with noindex, no hreflang, no
# sitemap entry and a "translation coming soon" note (see app/i18n.py). A
# translation agent adds e.g. "kn" here once seo_text.TEXT["kn"] is written.
# DIVASTRO-143: + every new language whose app/lang_data/<code>.py READY includes "seo".
TRANSLATED = lang_data.translated("seo", i18n.BASE_TRANSLATED, lang_data.LEGACY_CODES)  # DIVASTRO-123/143
# First path segments served in every language by this module.
i18n.LOCALIZABLE_ROOTS.update({"panchang", "rahu-kaal", "choghadiya", "kundali-milan",
                               "free-kundali"})

# Tool slug -> (English name, Hindi name, the `?open=` key app.js deep-links to).
# The page text reads the names from seo_text ("tool.<slug>"); kept for callers.
TOOLS = {
    t: (TEXT["en"][f"tool.{t}"], TEXT["hi"][f"tool.{t}"], key)
    for t, key in (("panchang", "panchang"), ("rahu-kaal", "panchang"),
                   ("choghadiya", "choghadiya"))
}

# "Shukla paksha" with the word — what the Hindi pages print (vrat/rashifal use it).
PAKSHA_HI = {k: TEXT["hi"]["paksha.full"].format(paksha=v)
             for k, v in i18n.names(HI).PAKSHA.items()}

MONTHS_HI = tuple(i18n.names(HI).MONTHS)

# The English page glosses a few names with their Hindi in brackets
# ("Navami (नवमी)"). This says which language glosses which: only English, by Hindi.
GLOSS = {EN: HI}


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)


def _tx(key: str, lang: str, **values) -> str:
    """This module's text for `key` in `lang` (seo_text.TEXT), formatted."""
    return i18n.fmt(key, lang, TEXT, **values)


# --------------------------------------------------------------------------
# Dates, caching and time formatting
# --------------------------------------------------------------------------

def _today() -> dt.date:
    """Today in India. The container runs UTC; between 00:00 and 05:30 IST a
    server-local "today" would show yesterday's Rahu Kaal (same bug api_tools
    fixed for /api/panchang)."""
    return dt.datetime.now(IST).date()


def _cache_headers() -> dict[str, str]:
    """Cache until the next IST midnight, capped at 30 minutes.

    The content changes once a day, so a short max-age costs nothing — but it
    must never outlive the day it describes, or a cached copy would show
    yesterday's Rahu Kaal after midnight. `private` so a shared cache
    never serves one person's copy to another.
    """
    now = dt.datetime.now(IST)
    midnight = dt.datetime.combine(now.date() + dt.timedelta(days=1), dt.time(), IST)
    max_age = max(60, min(1800, int((midnight - now).total_seconds())))
    return {"Cache-Control": f"private, max-age={max_age}"}


@functools.lru_cache(maxsize=2048)
def _panchang(slug: str, day: dt.date) -> dict:
    """One city's almanac for one day. ~10 ms to compute, so this is not about
    a single visitor — it keeps a crawler walking all ~700 URLs, or a burst of
    WhatsApp shares, from recomputing the same day hundreds of times. Keyed on
    the date, so entries simply stop being asked for after midnight and age
    out of the LRU. Sized for every city's 7-day Rahu Kaal week (~114 x 7).
    The English and Hindi pages share an entry. Callers must treat the dict
    as read-only."""
    city = seo_cities.BY_SLUG[slug]
    return panchang_engine.daily_panchang(day, city.latitude, city.longitude, city.timezone)


def _local(iso: str | None) -> dt.datetime | None:
    return dt.datetime.fromisoformat(iso).astimezone(IST) if iso else None


def _clock(moment: dt.datetime, lang: str = EN) -> str:
    """'6:29 AM', or in Hindi 'सुबह 6:29' — the part-of-day word is how times
    are said and printed in Indian almanacs, and reads better than AM/PM
    (i18n.format_time; the words are names_<code>.CLOCK)."""
    return i18n.format_time(moment, lang)


def _short_date(day: dt.date, lang: str = EN) -> str:
    return i18n.format_date(day, lang, short=True)


def _time(iso: str | None, day: dt.date, lang: str = EN) -> str:
    """'6:29 AM', with the date added when it falls on another civil day —
    tithis and moonrise routinely do, and a bare '1:18 AM' would read as this
    morning rather than tonight."""
    moment = _local(iso)
    if moment is None:
        return "—"
    text = _clock(moment, lang)
    if moment.date() != day:
        text += f" ({_short_date(moment.date(), lang)})"
    return text


def _span(window: dict | None, day: dt.date, lang: str = EN) -> str:
    if not window:
        return "—"
    return f"{_time(window['start'], day, lang)} – {_time(window['end'], day, lang)}"


def _long_date(day: dt.date, lang: str = EN) -> str:
    return i18n.format_date(day, lang)


# --------------------------------------------------------------------------
# Page shell
# --------------------------------------------------------------------------

_STYLE = """
  body { overflow: auto; display: block; }
  .seo { max-width: 820px; margin: 0 auto; padding: 22px 16px 40px; }
  .seo .top { display: flex; justify-content: space-between; align-items: center;
              flex-wrap: wrap; gap: 12px; margin-bottom: 14px; }
  .seo .back { display: inline-block; color: var(--ink-faint);
               font-size: 13px; text-decoration: none; white-space: nowrap; }
  .seo .lang-switch { font-size: 13.5px; padding: 4px 12px; border: 1px solid var(--line);
                      border-radius: 999px; text-decoration: none; white-space: nowrap; }
  .seo .crumbs { font-size: 12.5px; color: var(--ink-faint); margin: 0 0 10px; }
  .seo .crumbs a { color: var(--ink-faint); }
  .seo h1 { font-family: var(--serif); font-weight: 400; font-size: 27px; line-height: 1.25;
            color: var(--gold-soft); margin: 0 0 4px; }
  .seo .hi { font-size: 18px; color: var(--gold); margin: 0 0 6px; }
  .seo .date { font-family: var(--mono); font-size: 13px; color: var(--ink-faint); margin: 0 0 18px; }
  .seo h2 { font-family: var(--serif); font-weight: 400; font-size: 20px; color: var(--gold);
            margin: 28px 0 10px; }
  .seo h3 { font-size: 16px; color: var(--ink); margin: 18px 0 6px; }
  .seo p, .seo li { color: var(--ink-dim); font-size: 15px; line-height: 1.7; }
  .seo strong { color: var(--ink); }
  .seo a { color: var(--cyan); }
  .seo .box { border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px;
              background: var(--inset-bg); margin: 16px 0; }
  .seo .scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .seo table { width: 100%; border-collapse: collapse; font-size: 14.5px; }
  .seo th, .seo td { text-align: left; padding: 9px 8px; border-bottom: 1px solid var(--line);
                     vertical-align: top; }
  .seo th { color: var(--ink-faint); font-weight: 500; white-space: nowrap; }
  .seo td { color: var(--ink); }
  .seo td small { color: var(--ink-faint); display: block; }
  /* Narrow phones: a long label or a long Tamil/Malayalam transition ("... till 2:52 AM, then ...")
     must wrap rather than push the fact table wider than the screen. */
  @media (max-width: 420px) {
    .seo th { white-space: normal; }
    .seo th, .seo td { overflow-wrap: anywhere; word-break: break-word; }
  }
  .seo .good { color: var(--green); } .seo .bad { color: var(--rose); }
  .seo .cta { display: block; text-align: center; margin: 24px 0; padding: 14px 18px;
              border-radius: 12px; font-weight: 600; text-decoration: none; color: #fff;
              background: linear-gradient(120deg, var(--primary-a), var(--primary-b)); }
  .seo .cta.big { font-size: 18px; padding: 18px 20px; }
  .seo .links { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; margin: 0; list-style: none; }
  .seo .links a { display: inline-block; padding: 6px 12px; border: 1px solid var(--line);
                  border-radius: 999px; font-size: 13.5px; text-decoration: none;
                  color: var(--ink-dim); }
  .seo .links a[aria-current] { color: var(--gold); border-color: var(--gold); }
  .seo dl.cities { margin: 0; }
  .seo dl.cities dt { font-size: 12.5px; color: var(--ink-faint); margin: 14px 0 6px;
                      letter-spacing: .03em; }
  .seo dl.cities dd { margin: 0; }
  .seo .faq h3 { margin-top: 20px; }
  .seo .stay { margin: 28px 0 8px; padding: 12px 14px; border: 1px solid var(--line);
               border-radius: 14px; background: var(--inset-bg); }
  .seo .stay h2 { font-family: var(--sans); font-size: 12.5px; font-weight: 500; letter-spacing: .04em;
                  color: var(--ink-faint); margin: 0 0 8px; }
  .seo .stay ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }
  .seo .stay li { margin: 0; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; }
  .seo .stay a, .seo .stay .stay-btn { display: inline-flex; align-items: center; gap: 6px; min-height: 40px;
        box-sizing: border-box; padding: 6px 14px; border: 1px solid var(--line); border-radius: 999px;
        font: inherit; font-size: 13.5px; line-height: 1.35; color: var(--ink-dim); background: transparent;
        text-decoration: none; cursor: pointer; }
  .seo .stay a:hover, .seo .stay .stay-btn:hover { border-color: var(--gold); color: var(--gold); }
  .seo .stay a:focus-visible, .seo .stay .stay-btn:focus-visible { outline: 3px solid var(--gold); outline-offset: 2px; }
  .seo .stay .stay-btn svg { flex: none; color: #1fae55; }
  .seo .stay .stay-btn[hidden] { display: none; }
  .seo .stay .stay-btn:disabled { opacity: .6; cursor: progress; }
  .seo .stay .stay-done { color: var(--gold); font-size: 13.5px; }
  .seo .stay .stay-note { flex-basis: 100%; color: var(--ink-faint); font-size: 12.5px; }
  @media (max-width: 639px) { .seo .stay li { flex-basis: 100%; }
        .seo .stay a, .seo .stay .stay-btn { width: 100%; } }
  .site-footer { margin: 30px auto 0; }
  .footer-sections { display: flex; flex-wrap: wrap; gap: 6px 14px; justify-content: center;
                     margin: 10px 0 0; font-size: 13px; }
  @media (min-width: 640px) { .seo { padding-top: 40px; } .seo h1 { font-size: 32px; } }
"""

_SHELL = """<!DOCTYPE html>
<html lang="{html_lang}"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{description}"/>
<link rel="canonical" href="{canonical}"/>
{alternates}{head_extras}<meta property="og:type" content="website"/>
<meta property="og:site_name" content="{brand}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{description}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:image" content="{site}/static/og-card.jpg"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="og:locale" content="{og_locale}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="google-adsense-account" content="{adsense}"/>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense}"
        crossorigin="anonymous"></script>
<script src="/static/visit.js" defer></script>   <!-- counts the page load: see analytics.py -->
<link rel="icon" href="/static/favicon.ico"/>
<link rel="apple-touch-icon" href="/static/apple-touch-icon.png"/>
<link rel="stylesheet" href="/static/styles.css"/>
<style>{style}</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body class="sacred">
<main class="seo">
  <div class="top"><a class="back" href="{home}">&larr; {brand}</a>{switch}</div>
  {share}<nav class="crumbs" aria-label="{crumb_label}">{crumbs}</nav>
  {notice}
  {body}{strip}
</main>
{footer}
</body></html>"""


def _share(path: str) -> str:
    """DIVASTRO-107: a plain wa.me "Share on WhatsApp" link, UTM-tagged (see share.py)."""
    from .share import seo_share
    return seo_share(path)


def _strip(*, lang: str, path: str, title: str) -> str:
    """DIVASTRO-135: the "stay in touch" strip (see stay_strip.py), shared by every shell."""
    from .stay_strip import stay_strip
    return stay_strip(lang=lang, path=path, title=title)


def _footer_sections(lang: str) -> str:
    """DIVASTRO-133: a compact block of plain links to the top sections and the
    crawlable /sitemap hub, so every server-rendered page links to them."""
    from .hub_text import label
    from .muhurat_pages import YEARS as muhurat_years
    pre = i18n.prefix(lang)
    items = [("sitemap", f"{pre}/sitemap"), ("panchang", f"{pre}/panchang"),
             ("rashifal", f"{pre}/rashifal"), ("vrat", f"{pre}/vrat-tyohar"),
             ("muhurat", f"{pre}/muhurat/vivah-{muhurat_years[-1]}"),
             ("nakshatra", f"{pre}/nakshatra"),
             ("katha", "/katha" if lang == HI else "/en/katha")]
    links = " ".join(f'<a href="{href}">{label(k, lang)}</a>' for k, href in items)
    from .learn_pages import footer_link   # '' unless ASTRO_LEARN_PAGES=1 (DIVASTRO-142)
    links += footer_link(lang)
    return f'<nav class="footer-sections" aria-label="{label("sitemap", lang)}">{links}</nav>\n  '


def _footer(lang: str = EN) -> str:
    """The same public footer as index.html — the links AdSense and payment
    underwriters look for, from the same constants the legal pages use. The
    legal pages themselves are English-only, so a translated footer translates
    the link text but points at the same pages (labels: i18n.CHROME)."""
    reg = registration_inline()
    keys = ("f_katha", "f_terms", "f_privacy", "f_refund", "f_contact", "f_feedback")
    labels = [i18n.chrome(k, lang) for k in keys]
    disclaimer = i18n.chrome("disclaimer", lang)
    links = "\n    ".join(f'<a href="{href}">{label}</a>' for href, label in zip(
        ("/katha" if lang == HI else "/en/katha", "/terms", "/privacy", "/refund", "/contact",
         "/feedback"), labels))
    return f"""<footer class="site-footer">
  <nav>
    {links}
  </nav>
  {_footer_sections(lang)}<p class="legal-entity">{_e(LEGAL_NAME)} · {_e(ADDRESS)} ·
    <a href="mailto:{_e(EMAIL)}">{_e(EMAIL)}</a> · {_e(PHONE)}</p>
  {f'<p class="legal-entity registrations">{_e(reg)}</p>' if reg else ''}
  <p class="disclaimer">{disclaimer}</p>
</footer>"""


def _alternates(en_path: str, translated=None, x_default: str = EN,
                lang_paths: dict | None = None) -> str:
    """Reciprocal hreflang: every translated copy carries the identical set,
    which is what makes Google treat them as one page in several languages
    rather than competing pages (a one-way hreflang is ignored). x-default is
    the English copy except where Hindi is the canonical one (the katha pages).
    Only languages in `translated` are listed (i18n.alternates)."""
    return i18n.alternates(en_path, translated or TRANSLATED, x_default, SITE_URL, lang_paths)


def page_language_bits(*, lang: str, path: str, has_twin: bool, translated=None,
                       x_default: str = EN, lang_paths: dict | None = None,
                       region: bool = False) -> dict:
    """The language-dependent parts of any server-rendered page, for every shell
    that is not `_render` (rashifal, nakshatra, muhurat, naam milan):

    alternates — hreflang links (only on a translated copy that has twins)
    head       — noindex for an untranslated copy, the script's web font, langpick.js
    picker     — the language picker for the top of the page
    notice     — "translation coming soon" in the page's script, or ''
    html_lang, og_locale, in_language — from the registry
    en_path    — the English URL of this page
    home       — the "← Divine Astro" link: the app, opened in `lang`
    """
    translated = translated or TRANSLATED
    en_path = (lang_paths or {}).get(EN) or i18n.strip_prefix(path)[1]
    L = i18n.get(lang)
    indexable = lang in translated
    return {
        "alternates": (i18n.alternates(en_path, translated, x_default, SITE_URL, lang_paths,
                                       region=region)
                       if has_twin and indexable else ""),
        "head": i18n.head_extras(lang, translated),
        "picker": i18n.picker(lang, i18n.picker_links(en_path, lang_paths)),
        "notice": i18n.notice(lang, translated),
        "html_lang": L.html_lang, "og_locale": L.og_locale, "in_language": L.bcp47,
        "en_path": en_path, "home": i18n.app_link(lang),
    }


def _render(*, title: str, description: str, path: str, crumbs: list[tuple[str, str]],
            body: str, lang: str = EN, alt: str | None = None, extra_ld: tuple = (),
            status: int = 200, cache: bool = True, x_default: str = EN,
            translated=None, lang_paths: dict | None = None) -> HTMLResponse:
    """`path` is this page's canonical path; `alt` any other-language twin (None
    for pages with no twin, i.e. the 404s — only its truthiness matters now:
    the twins are derived from the English path, or given in `lang_paths`
    for a module with its own URL scheme, like katha). `translated` is the
    calling module's TRANSLATED set (this module's by default)."""
    bits = page_language_bits(lang=lang, path=path, has_twin=bool(alt), translated=translated,
                              x_default=x_default, lang_paths=lang_paths)
    canonical = SITE_URL + path
    trail = [(i18n.chrome("home", lang), "/")] + crumbs
    crumb_html = " › ".join(
        f'<a href="{_e(href)}">{_e(name)}</a>' if i < len(trail) - 1 else _e(name)
        for i, (name, href) in enumerate(trail))
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": title, "description": description,
             "url": canonical, "inLanguage": bits["in_language"],
             "dateModified": _today().isoformat(),
             "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE_URL + "/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE_URL + href}
                for i, (name, href) in enumerate(trail)]},
            *extra_ld,
        ],
    }
    # "</" inside a JSON string would close the <script> element early.
    jsonld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    page = _SHELL.format(
        html_lang=bits["html_lang"], og_locale=bits["og_locale"],
        title=_e(title), description=_e(description), canonical=_e(canonical),
        alternates=bits["alternates"], head_extras=bits["head"], switch=bits["picker"],
        notice=bits["notice"], home=_e(i18n.app_link(lang)),
        crumb_label=_e(i18n.chrome("breadcrumb", lang)),
        brand=_e(BRAND), site=_e(SITE_URL), adsense=ADSENSE_CLIENT, style=_STYLE,
        jsonld=jsonld, crumbs=i18n.localize_links(crumb_html, lang),
        body=i18n.localize_links(body, lang), footer=_footer(lang),
        share=_share(path) if status == 200 else "",
        strip=_strip(lang=lang, path=path, title=title) if status == 200 else "")
    headers = _cache_headers() if cache else {"Cache-Control": "no-store"}
    return HTMLResponse(page, status_code=status, headers=headers)


# --------------------------------------------------------------------------
# Shared fragments
# --------------------------------------------------------------------------

def _prefix(lang: str) -> str:
    return i18n.prefix(lang)


def _path(tool: str, city: City, lang: str = EN) -> str:
    """The canonical URL for a tool in a city. The default city's page lives at
    the bare /tool URL, so /tool and /tool/new-delhi are one page to a search
    engine rather than two competing copies. Other languages' copies live under
    their prefix (/hi/, /kn/, ...)."""
    bare = f"/{tool}" if city == seo_cities.DEFAULT else f"/{tool}/{city.slug}"
    return _prefix(lang) + bare


def _app_link(key: str, lang: str = EN) -> str:
    """A deep link into the app (tools.js handles ?open=, app.js ?lang=)."""
    return i18n.app_link(lang, f"open={key}")


def _tool_name(tool: str, lang: str) -> str:
    return _tx(f"tool.{tool}", lang)


def _city_links(tool: str, current: City, lang: str = EN) -> str:
    """Every city, grouped by state — ~100 pills in one cloud is unusable."""
    groups = []
    for state, cities in seo_cities.by_state():
        items = "".join(
            f'<li><a href="{_path(tool, c, lang)}"'
            + (' aria-current="page"' if c == current else "")
            + f'>{_e(seo_cities.city_name(c, lang))}</a></li>'
            for c in cities)
        label = seo_cities.state_name(state, lang)
        groups.append(f'<dt>{_e(label)}</dt><dd><ul class="links">{items}</ul></dd>')
    heading = _tx("cities.heading", lang, tool=_tool_name(tool, lang))
    return f'<h2>{_e(heading)}</h2><dl class="cities">{"".join(groups)}</dl>'


def _tool_links(city: City, current: str, lang: str = EN) -> str:
    name = seo_cities.city_name(city, lang)
    pre = _prefix(lang)
    links = [(_path(t, city, lang), _tx("links.tool_in_city", lang, tool=_tool_name(t, lang),
                                        city=name))
             for t in TOOLS if t != current]
    if current != "kundali-milan":
        links.append((pre + "/kundali-milan", _tx("links.milan", lang)))
    if current != "free-kundali":
        links.append((pre + "/free-kundali", _tx("links.kundali", lang)))
    links.append((_app_link("muhurat", lang), _tx("links.muhurat", lang)))
    links.append((pre + "/rashifal", _tx("links.rashifal", lang)))
    links.append((_path("vrat-tyohar", city, lang), _tx("links.vrat", lang, city=name)))
    items = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in links)
    return f'<h2>{_tx("links.heading", lang)}</h2><ul class="links">{items}</ul>'


def _cta(tool: str, text: str, lang: str = EN, big: bool = False) -> str:
    """A button into the app's own tool stage (the ?open= deep link in tools.js)."""
    key = {"kundali-milan": "milan", "free-kundali": "kundali"}.get(tool) or TOOLS[tool][2]
    cls = "cta big" if big else "cta"
    return f'<a class="{cls}" href="{_e(_app_link(key, lang))}">{_e(text)}</a>'


def _not_found(tool: str, slug: str, lang: str = EN) -> HTMLResponse:
    """A real 404 status (so the URL never gets indexed) with a usable page,
    because the person who mistyped a city still wants a city."""
    key = TOOLS[tool][2]
    name = _tool_name(tool, lang)
    base = _prefix(lang) + f"/{tool}"
    body = (_tx("nf.body", lang, tool=_e(name), slug=_e(slug), app=_e(_app_link(key, lang)))
            + _city_links(tool, seo_cities.DEFAULT, lang))
    title = _tx("nf.title", lang, brand=BRAND)
    desc = _tx("nf.desc", lang, tool=name)
    return _render(title=title, description=desc, path=base, crumbs=[(name, base)], body=body,
                   lang=lang, status=404, cache=False)


def _gloss(lang: str, table: str, english: str) -> str:
    """' <span lang="hi">(नवमी)</span>' after a name on the English page; ''
    elsewhere (GLOSS)."""
    other = GLOSS.get(lang)
    value = getattr(i18n.names(other), table).get(english) if other else None
    return f' <span lang="{other}">({_e(value)})</span>' if value else ""


def _limb_rows(entries: list[dict], day: dt.date, table: str, lang: str = EN,
               gloss: bool = False) -> str:
    """'Navami until 3:54 AM (5 Oct), then Dashami' — a limb can change during
    the day, and the one that matters for an evening puja may be the second.
    Names come from names_<code>.<table> ('नवमी रात 3:54 (5 अक्टूबर) तक, फिर
    दशमी'); `gloss` adds the English page's Hindi in brackets."""
    names = getattr(i18n.names(lang), table)
    parts = []
    for i, entry in enumerate(entries):
        name = _e(names.get(entry["name"], entry["name"]))
        if gloss:
            name += _gloss(lang, table, entry["name"])
        if entry.get("pada"):
            name += f" · {_tx('limb.pada', lang)} {entry['pada']}"
        if i < len(entries) - 1:
            parts.append(_tx("limb.until", lang, name=name, time=_time(entry['ends'], day, lang)))
        else:
            parts.append(_tx("limb.then", lang, name=name) if i else name)
    return ", ".join(parts) if parts else "—"


def _when_heading(city: City, day: dt.date, p: dict, lang: str = EN) -> str:
    weekday = p["vara"]["weekday"]
    text = _tx("when", lang, vara=_e(i18n.names(lang).VARA.get(weekday, weekday)),
               date=_e(_long_date(day, lang)), place=_e(seo_cities.place(city, lang)))
    return f'<p class="date">{text}</p>'


def _tool_crumbs(tool: str, city: City, lang: str = EN) -> list[tuple[str, str]]:
    crumbs = [(_tool_name(tool, lang), _prefix(lang) + f"/{tool}")]
    if city != seo_cities.DEFAULT:
        crumbs.append((seo_cities.city_name(city, lang), _path(tool, city, lang)))
    return crumbs


def _city_vars(city: City, lang: str) -> dict:
    """The city's name for a template, raw: {city} in `lang`, {city_en}, {city_hi}."""
    return {"city": seo_cities.city_name(city, lang), "city_en": city.name,
            "city_hi": city.name_hi}


def _esc(values: dict) -> dict:
    return {k: _e(v) for k, v in values.items()}


def _vrat_block(city: City, day: dt.date, lang: str = EN) -> str:
    """Today's vrat/festivals with their puja muhurat, parana etc. for this
    city (DIVASTRO-111); empty on an ordinary day."""
    from . import vrat_pages            # vrat_pages imports this module: import late
    return vrat_pages.panchang_block(day, city.latitude, city.longitude, city.timezone, lang)


# --------------------------------------------------------------------------
# /panchang
# --------------------------------------------------------------------------

def _panchang_page(city: City, lang: str = EN) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    s, sun, moon, m = p["summary"], p["sun"], p["moon"], p["muhurta"]
    n, hi = i18n.names(lang), i18n.names(HI)
    pk = s["paksha"] or ""
    weekday = p["vara"]["weekday"]
    paksha = n.PAKSHA.get(pk, pk)
    names = {
        "vara": n.VARA.get(weekday, weekday), "weekday": weekday, "vara_en": p["vara"]["name"],
        "vara_hi": hi.VARA.get(weekday, ""),
        "tithi": n.TITHI.get(s["tithi"], s["tithi"]),
        "nakshatra": n.NAKSHATRAS.get(s["nakshatra"], s["nakshatra"]),
        "paksha": paksha, "paksha_en": pk,
        "paksha_full": _tx("paksha.full", lang, paksha=paksha) if pk else "",
        "paksha_hi_full": PAKSHA_HI.get(pk, ""),
    }
    rahu = _span(m["rahu_kaal"], day, lang)
    sunrise = _time(sun["rise"], day, lang)
    abhijit = (_span(m["abhijit"], day, lang) if m["abhijit"] else _tx("p.no_abhijit", lang))
    moonrise = _time(moon["rise"], day, lang) if moon["rise"] else _tx("p.no_moonrise", lang)
    moonset = _time(moon["set"], day, lang) if moon["set"] else _tx("p.no_moonset", lang)
    rows = [
        ("p.r_vara", _tx("p.v_vara", lang, **_esc(names))),
        ("p.r_tithi", _limb_rows(p["tithi"], day, "TITHI", lang, gloss=True)),
        ("p.r_paksha", _tx("p.v_paksha", lang, **_esc(names))),
        ("p.r_nakshatra", _limb_rows(p["nakshatra"], day, "NAKSHATRAS", lang, gloss=True)),
        ("p.r_yoga", _limb_rows(p["yoga"], day, "YOGA", lang)),
        ("p.r_karana", _limb_rows(p["karana"], day, "KARANA", lang)),
        ("p.r_sunrise", sunrise),
        ("p.r_sunset", _time(sun["set"], day, lang)),
        ("p.r_moonrise", moonrise),
        ("p.r_moonset", moonset),
        ("p.r_moon_sign", _e(n.RASHI.get(moon["sign"], moon["sign"]))),
        ("p.r_rahu", rahu),
        ("p.r_yama", _span(m["yamaganda"], day, lang)),
        ("p.r_gulika", _span(m["gulika_kaal"], day, lang)),
        ("p.r_abhijit", abhijit),
    ]
    table = "".join(f'<tr><th scope="row">{_e(_tx(k, lang))}</th><td>{v}</td></tr>'
                    for k, v in rows)
    date_text = _long_date(day, lang)
    cv = _city_vars(city, lang)
    raw = {**cv, **names, "date": date_text, "sunrise": sunrise, "rahu": rahu, "brand": BRAND}
    title = _tx("p.title", lang, **raw)
    description = _tx("p.desc", lang, **raw)
    v = {**_esc(cv), **_esc(names), "rahu": rahu, "place": _e(seo_cities.place(city, lang)),
         "lat": f"{city.latitude:.4f}", "lon": f"{city.longitude:.4f}"}
    body = f"""
{_tx("p.h1", lang, **v)}
{_tx("p.sub", lang, **v)}
{_when_heading(city, day, p, lang)}
{_tx("p.box", lang, **v)}
{_vrat_block(city, day, lang)}
<div class="scroll"><table>{table}</table></div>
{_tx("p.note", lang, **v)}
{_cta("panchang", _tx("p.cta", lang), lang)}
{_tx("p.limbs", lang)}
{_city_links("panchang", city, lang)}
{_tool_links(city, "panchang", lang)}"""
    return _render(title=title, description=description, path=_path("panchang", city, lang),
                   lang=lang, alt=_path("panchang", city, HI),
                   crumbs=_tool_crumbs("panchang", city, lang), body=body)


@router.get("/panchang", response_class=HTMLResponse)
def panchang_default() -> HTMLResponse:
    return _panchang_page(seo_cities.DEFAULT)


@router.get("/panchang/{slug}", response_class=HTMLResponse)
def panchang_city(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _panchang_page(city) if city else _not_found("panchang", slug)


@router.get("/hi/panchang", response_class=HTMLResponse)
def panchang_default_hi() -> HTMLResponse:
    return _panchang_page(seo_cities.DEFAULT, HI)


@router.get("/hi/panchang/{slug}", response_class=HTMLResponse)
def panchang_city_hi(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _panchang_page(city, HI) if city else _not_found("panchang", slug, HI)


# --------------------------------------------------------------------------
# /rahu-kaal
# --------------------------------------------------------------------------

def _rahu_week(city: City, day: dt.date, lang: str = EN) -> str:
    """A week ahead: the most-asked follow-up ("what about tomorrow?") answered
    on the page itself. Seven ~10 ms computations, all cached."""
    vara = i18n.names(lang).VARA
    rows = []
    for offset in range(7):
        d = day + dt.timedelta(days=offset)
        q = _panchang(city.slug, d)
        weekday = q['vara']['weekday']
        rows.append(f"<tr><td>{_e(vara.get(weekday, weekday))}<small>{_e(_short_date(d, lang))}</small></td>"
                    f"<td>{_span(q['muhurta']['rahu_kaal'], d, lang)}</td>"
                    f"<td>{_span(q['muhurta']['yamaganda'], d, lang)}</td>"
                    f"<td>{_span(q['muhurta']['gulika_kaal'], d, lang)}</td></tr>")
    return "".join(rows)


def _rahu_page(city: City, lang: str = EN) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    m, sun = p["muhurta"], p["sun"]
    weekday = p["vara"]["weekday"]
    date_text = _long_date(day, lang)
    rahu = _span(m["rahu_kaal"], day, lang)
    yama, gulika = _span(m["yamaganda"], day, lang), _span(m["gulika_kaal"], day, lang)
    cv = _city_vars(city, lang)
    title = _tx("rk.title", lang, **cv, rahu=rahu, date=date_text, brand=BRAND)
    description = _tx("rk.desc", lang, **cv, vara=i18n.names(lang).VARA.get(weekday, weekday),
                      date=date_text, rahu=rahu, yama=yama, gulika=gulika)
    abhijit = (_span(m['abhijit'], day, lang) if m['abhijit'] else _tx("rk.no_abhijit", lang))
    v = _esc(cv)
    body = f"""
{_tx("rk.h1", lang, **v)}
{_tx("rk.sub", lang, **v)}
{_when_heading(city, day, p, lang)}
<div class="scroll"><table>
<tr><th scope="row">{_tx("rk.r_rahu", lang)}</th><td class="bad"><strong>{rahu}</strong></td></tr>
<tr><th scope="row">{_tx("rk.r_yama", lang)}</th><td>{yama}</td></tr>
<tr><th scope="row">{_tx("rk.r_gulika", lang)}</th><td>{gulika}</td></tr>
<tr><th scope="row">{_tx("rk.r_abhijit", lang)}</th><td class="good">{abhijit}</td></tr>
<tr><th scope="row">{_tx("rk.r_sun", lang)}</th><td>{_time(sun['rise'], day, lang)} / {_time(sun['set'], day, lang)}</td></tr>
</table></div>
{_cta("rahu-kaal", _tx("rk.cta", lang), lang)}
{_tx("rk.about", lang)}
{_tx("rk.week_h2", lang, **v)}
<div class="scroll"><table>
<tr><th>{_tx("rk.th_day", lang)}</th><th>{_tx("rk.th_rahu", lang)}</th><th>{_tx("rk.th_yama", lang)}</th><th>{_tx("rk.th_gulika", lang)}</th></tr>
{_rahu_week(city, day, lang)}
</table></div>
{_city_links("rahu-kaal", city, lang)}
{_tool_links(city, "rahu-kaal", lang)}"""
    return _render(title=title, description=description, path=_path("rahu-kaal", city, lang),
                   lang=lang, alt=_path("rahu-kaal", city, HI),
                   crumbs=_tool_crumbs("rahu-kaal", city, lang), body=body)


@router.get("/rahu-kaal", response_class=HTMLResponse)
def rahu_default() -> HTMLResponse:
    return _rahu_page(seo_cities.DEFAULT)


@router.get("/rahu-kaal/{slug}", response_class=HTMLResponse)
def rahu_city(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _rahu_page(city) if city else _not_found("rahu-kaal", slug)


@router.get("/hi/rahu-kaal", response_class=HTMLResponse)
def rahu_default_hi() -> HTMLResponse:
    return _rahu_page(seo_cities.DEFAULT, HI)


@router.get("/hi/rahu-kaal/{slug}", response_class=HTMLResponse)
def rahu_city_hi(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _rahu_page(city, HI) if city else _not_found("rahu-kaal", slug, HI)


# --------------------------------------------------------------------------
# /choghadiya
# --------------------------------------------------------------------------

def choghadiya_slots(p: dict) -> tuple[list[dict], list[dict]]:
    """Day and night choghadiya from a `daily_panchang` result.

    Slots come from chog.day_night_slots, the same code /api/choghadiya uses,
    cut at the ephemeris sunrise/sunset this page's Panchang prints
    (DIVASTRO-103: both now agree to the second).
    """
    rise, sset, next_rise = (_local(p["sun"][k]) for k in ("rise", "set", "next_rise"))
    if not (rise and sset and next_rise):
        return [], []
    vara = p["vara"]["index"]                          # Sunday = 0, as choghadiya.py uses

    def run(parts: list) -> list[dict]:
        return [{"name": n, "start": s, "end": e, **chog.CHOGHADIYA_INFO[n]} for n, s, e in parts]

    day, night = chog.day_night_slots(vara, rise, sset, next_rise)
    return run(day), run(night)


def _slot_text(s: dict, field: str, lang: str, fallback: str) -> str:
    """A choghadiya's ruler/quality/description in `lang`: the engine's own
    `<field>_<lang>` (choghadiya.CHOGHADIYA_INFO has _hi), else `fallback`."""
    return s.get(f"{field}_{lang}") or fallback


def _chog_table(slots: list[dict], day: dt.date, lang: str = EN) -> str:
    n = i18n.names(lang)
    rows = []
    for s in slots:
        cls = {"auspicious": "good", "inauspicious": "bad"}.get(s["quality"], "")
        when = (f"{_time(s['start'].isoformat(), day, lang)} – "
                f"{_time(s['end'].isoformat(), day, lang)}")
        rows.append(_tx(
            "ch.row", lang, when=when, cls=cls,
            name=_e(n.CHOGHADIYA.get(s["name"], s["name"])), name_hi=_e(s["name_hi"]),
            ruler=_e(_slot_text(s, "ruler", lang, n.GRAHA.get(s["ruler"], s["ruler"]))),
            quality=_e(_slot_text(s, "quality", lang, n.CHOGHADIYA_QUALITY.get(s["quality"],
                                                                                s["quality"]))),
            desc=_e(_slot_text(s, "description", lang, s["description"]))))
    return '<div class="scroll"><table>' + _tx("ch.th", lang) + "".join(rows) + "</table></div>"


def _choghadiya_page(city: City, lang: str = EN) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    n = i18n.names(lang)
    day_slots, night_slots = choghadiya_slots(p)
    weekday = p["vara"]["weekday"]
    date_text = _long_date(day, lang)
    good = [s for s in day_slots if s["quality"] == "auspicious"]
    first_good = (_tx("ch.first_good", lang, name=n.CHOGHADIYA.get(good[0]["name"], good[0]["name"]),
                      time=_time(good[0]['start'].isoformat(), day, lang))
                  if good else _tx("ch.none", lang))
    sunrise = _time(p['sun']['rise'], day, lang)
    cv = _city_vars(city, lang)
    title = _tx("ch.title", lang, **cv, date=date_text, brand=BRAND)
    description = _tx("ch.desc", lang, **cv, vara=n.VARA.get(weekday, weekday), date=date_text,
                      sunrise=sunrise)
    v = _esc(cv)
    body = f"""
{_tx("ch.h1", lang, **v)}
{_tx("ch.sub", lang, **v)}
{_when_heading(city, day, p, lang)}
{_tx("ch.box", lang, sunrise=sunrise, sunset=_time(p['sun']['set'], day, lang), first_good=_e(first_good))}
{_tx("ch.day_h2", lang)}
{_chog_table(day_slots, day, lang)}
{_tx("ch.night_h2", lang)}
{_chog_table(night_slots, day, lang)}
{_cta("choghadiya", _tx("ch.cta", lang), lang)}
{_tx("ch.about", lang, **v)}
{_city_links("choghadiya", city, lang)}
{_tool_links(city, "choghadiya", lang)}"""
    return _render(title=title, description=description, path=_path("choghadiya", city, lang),
                   lang=lang, alt=_path("choghadiya", city, HI),
                   crumbs=_tool_crumbs("choghadiya", city, lang), body=body)


@router.get("/choghadiya", response_class=HTMLResponse)
def choghadiya_default() -> HTMLResponse:
    return _choghadiya_page(seo_cities.DEFAULT)


@router.get("/choghadiya/{slug}", response_class=HTMLResponse)
def choghadiya_city(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _choghadiya_page(city) if city else _not_found("choghadiya", slug)


@router.get("/hi/choghadiya", response_class=HTMLResponse)
def choghadiya_default_hi() -> HTMLResponse:
    return _choghadiya_page(seo_cities.DEFAULT, HI)


@router.get("/hi/choghadiya/{slug}", response_class=HTMLResponse)
def choghadiya_city_hi(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _choghadiya_page(city, HI) if city else _not_found("choghadiya", slug, HI)


# --------------------------------------------------------------------------
# /kundali-milan
# --------------------------------------------------------------------------

# Each koota's points. Its name and what it measures are seo_text keys
# "koota.<key>" / "koota_about.<key>"; a language without its own koota names
# shows names_<code>.KOOTA (Hindi: matching.KOOTA_LABELS_HI).
KOOTA_POINTS = (("varna", 1), ("vashya", 2), ("tara", 3), ("yoni", 4), ("graha_maitri", 5),
                ("gana", 6), ("bhakoot", 7), ("nadi", 8))
# (key, English name, points, what it measures). Points and Hindi labels are
# checked against astro/matching.py by the test, so this text cannot drift
# from what the matching tool actually scores.
KOOTAS = tuple((k, TEXT["en"][f"koota.{k}"], pts, TEXT["en"][f"koota_about.{k}"])
               for k, pts in KOOTA_POINTS)
# The same eight, in Hindi, keyed like KOOTAS (the test checks the keys match).
KOOTAS_HI = {k: TEXT["hi"][f"koota_about.{k}"] for k, _ in KOOTA_POINTS}


def _koota_name(key: str, lang: str) -> str:
    if i18n.has(f"koota.{key}", lang, TEXT):
        return TEXT[lang][f"koota.{key}"]
    return i18n.names(lang).KOOTA.get(key) or TEXT["en"][f"koota.{key}"]


def _score_bands(lang: str = EN) -> str:
    """The bands are read straight from the engine's table (upper bounds are
    exclusive ceilings, the last one 36.01), so the page and the verdict the
    tool prints can never disagree."""
    total = int(matching.MAXIMUM_POINTS)
    bands, low = [], 0
    for i, (ceiling, _verdict, _detail) in enumerate(matching.SCORE_BANDS):
        top = min(math.ceil(ceiling) - 1, total)
        rng = _tx("km.below", lang, n=top + 1) if low == 0 else f"{low}–{top}"
        bands.append(f"<tr><td>{rng}</td><td>{_e(_tx(f'km.band{i}', lang))}</td></tr>")
        low = top + 1
    return "".join(bands)


@router.get("/kundali-milan", response_class=HTMLResponse)
def kundali_milan() -> HTMLResponse:
    return _kundali_milan_page()


def _kundali_milan_page(lang: str = EN) -> HTMLResponse:
    hi = i18n.names(HI)
    rows = "".join(
        _tx("km.row", lang, name=_e(_koota_name(key, lang)), name_hi=_e(hi.KOOTA[key]),
            pts=pts, text=_e(_tx(f"koota_about.{key}", lang)))
        for key, pts in KOOTA_POINTS)
    total = int(matching.MAXIMUM_POINTS)
    ords = [_tx("km.ord1" if h == 1 else "km.ord2" if h == 2 else "km.ordn", lang, n=h)
            for h in matching.MANGAL_HOUSES]
    houses = ", ".join(ords[:-1]) + _tx("km.or", lang) + ords[-1]
    title = _tx("km.title", lang, total=total, brand=BRAND)
    description = _tx("km.desc", lang, total=total)
    body = f"""
{_tx("km.intro", lang, total=total)}
{_cta("kundali-milan", _tx("km.cta1", lang), lang)}
{_tx("km.naam", lang, href=_prefix(lang) + "/naam-se-kundali-milan")}
{_tx("km.kootas_h2", lang)}
<div class="scroll"><table>{_tx("km.th", lang)}
{rows}
<tr><td><strong>{_tx("km.total", lang)}</strong></td><td><strong>{total}</strong></td><td></td></tr></table></div>
{_tx("km.score_h2", lang)}
<div class="scroll"><table>{_tx("km.score_th", lang)}{_score_bands(lang)}</table></div>
{_tx("km.score_p", lang)}
{_tx("km.mangal", lang, houses=houses)}
{_tx("km.how", lang, total=total)}
{_cta("kundali-milan", _tx("km.cta2", lang), lang)}
{_tool_links(seo_cities.DEFAULT, "kundali-milan", lang)}"""
    path = _prefix(lang) + "/kundali-milan"
    return _render(title=title, description=description, path=path, lang=lang,
                   alt="/hi/kundali-milan", crumbs=[(_tx("km.crumb", lang), path)], body=body)


@router.get("/hi/kundali-milan", response_class=HTMLResponse)
def kundali_milan_hi() -> HTMLResponse:
    return _kundali_milan_page(HI)


# --------------------------------------------------------------------------
# /free-kundali
# --------------------------------------------------------------------------

# What the free chart actually contains, checked against the app: the varga
# list is the vargas engine's DEFAULT_DIVISIONS (what /api/vargas and the
# Vargas tab show), and the test pins that. Paid extras (the Life Book PDF
# with all sixteen vargas, single-question reports) are deliberately absent.
# Their names are seo_text keys "varga.<code>".

def _vargas(lang: str) -> str:
    return ", ".join(f"{code} {_tx(f'varga.{code}', lang)}" for code in DEFAULT_DIVISIONS)


FAQ_EN = FAQ["en"]
FAQ_HI = FAQ["hi"]


def _faq(items: tuple) -> tuple[str, dict]:
    """The FAQ as HTML and as FAQPage JSON-LD, from one list so the two can
    never say different things (Google requires the marked-up Q&A to be
    visible on the page)."""
    html_part = "".join(f"<h3>{_e(q)}</h3><p>{_e(a)}</p>" for q, a in items)
    ld = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in items]}
    return f'<div class="faq">{html_part}</div>', ld


@router.get("/free-kundali", response_class=HTMLResponse)
def free_kundali() -> HTMLResponse:
    return _free_kundali_page()


def _free_kundali_page(lang: str = EN) -> HTMLResponse:
    faq_html, faq_ld = _faq(i18n.pick(FAQ, lang))
    title = _tx("fk.title", lang, brand=BRAND)
    description = _tx("fk.desc", lang)
    body = f"""
{_tx("fk.intro", lang)}
{_cta("free-kundali", _tx("fk.cta1", lang), lang, big=True)}
{_tx("fk.need", lang)}

{_tx("fk.includes", lang, vargas=_e(_vargas(lang)))}

{_tx("fk.read", lang)}
{_cta("free-kundali", _tx("fk.cta2", lang), lang)}

{_tx("fk.faq_h2", lang)}
{faq_html}
{_tool_links(seo_cities.DEFAULT, "free-kundali", lang)}"""
    path = _prefix(lang) + "/free-kundali"
    return _render(title=title, description=description, path=path, lang=lang,
                   alt="/hi/free-kundali", crumbs=[(_tx("fk.crumb", lang), path)],
                   body=body, extra_ld=(faq_ld,))


@router.get("/hi/free-kundali", response_class=HTMLResponse)
def free_kundali_hi() -> HTMLResponse:
    return _free_kundali_page(HI)


# --------------------------------------------------------------------------
# DIVASTRO-121: the same pages in every other registry language
# --------------------------------------------------------------------------
# /{lang:xlang}/... matches exactly i18n.EXTRA_CODES (kn, te, ta, ml, bn, or);
# English and Hindi keep their own routes above. Every builder takes `lang`
# and reads its text from seo_text.TEXT[lang] (English per key until
# translated; astrology names already in the language's script). Until a
# language is added to TRANSLATED its pages are noindex with a "translation
# coming soon" note.

_CITY_BUILDERS = {"panchang": _panchang_page, "rahu-kaal": _rahu_page,
                  "choghadiya": _choghadiya_page}


def _city_page_lang(tool: str, lang: str, slug: str | None = None) -> HTMLResponse:
    city = seo_cities.DEFAULT if slug is None else seo_cities.get(slug)
    if city is None:
        return _not_found(tool, slug or "", lang)
    return _CITY_BUILDERS[tool](city, lang)


@router.get("/{lang:xlang}/panchang", response_class=HTMLResponse)
def panchang_default_lang(lang: str) -> HTMLResponse:
    return _city_page_lang("panchang", lang)


@router.get("/{lang:xlang}/panchang/{slug}", response_class=HTMLResponse)
def panchang_city_lang(lang: str, slug: str) -> HTMLResponse:
    return _city_page_lang("panchang", lang, slug)


@router.get("/{lang:xlang}/rahu-kaal", response_class=HTMLResponse)
def rahu_default_lang(lang: str) -> HTMLResponse:
    return _city_page_lang("rahu-kaal", lang)


@router.get("/{lang:xlang}/rahu-kaal/{slug}", response_class=HTMLResponse)
def rahu_city_lang(lang: str, slug: str) -> HTMLResponse:
    return _city_page_lang("rahu-kaal", lang, slug)


@router.get("/{lang:xlang}/choghadiya", response_class=HTMLResponse)
def choghadiya_default_lang(lang: str) -> HTMLResponse:
    return _city_page_lang("choghadiya", lang)


@router.get("/{lang:xlang}/choghadiya/{slug}", response_class=HTMLResponse)
def choghadiya_city_lang(lang: str, slug: str) -> HTMLResponse:
    return _city_page_lang("choghadiya", lang, slug)


@router.get("/{lang:xlang}/kundali-milan", response_class=HTMLResponse)
def kundali_milan_lang(lang: str) -> HTMLResponse:
    return _kundali_milan_page(lang)


@router.get("/{lang:xlang}/free-kundali", response_class=HTMLResponse)
def free_kundali_lang(lang: str) -> HTMLResponse:
    return _free_kundali_page(lang)


# --------------------------------------------------------------------------
# sitemap.xml and robots.txt
# --------------------------------------------------------------------------

STATIC_PATHS = ("/", "/kundali-milan", "/terms", "/privacy", "/refund", "/contact")
# Explainer pages that exist in every translated language (/x, /hi/x, ...).
BILINGUAL_PATHS = ("/kundali-milan", "/free-kundali")


def sitemap_paths() -> list[str]:
    """Every public URL this module serves that we want indexed, canonical
    form only. Other modules expose their own `sitemap_paths()`; `sitemap()`
    below just concatenates them."""
    # Only TRANSLATED languages: an untranslated copy is noindex and must not
    # be offered to crawlers (DIVASTRO-121).
    langs = i18n.ordered(TRANSLATED)
    paths = list(STATIC_PATHS) + ["/free-kundali"]
    paths += [i18n.prefix(lang) + p for lang in langs if lang != EN for p in BILINGUAL_PATHS]
    for lang in langs:
        for tool in TOOLS:
            paths += [_path(tool, c, lang) for c in seo_cities.CITIES]
    from .rashifal_pages import sitemap_paths as rashifal_paths  # lazy: it imports this module
    from .muhurat_pages import page_paths as muhurat_paths  # same: imports this module
    from .vrat_pages import page_paths as vrat_paths  # same: imports this module
    from .vrat_city_pages import page_paths as vrat_city_paths  # same (DIVASTRO-140)
    from .recurring_pages import page_paths as recurring_paths  # same (DIVASTRO-141)
    from .nakshatra_pages import sitemap_paths as nakshatra_paths  # same (DIVASTRO-115)
    from .katha import sitemap_paths as katha_paths  # same
    from .learn_pages import sitemap_paths as learn_paths  # same; [] unless ASTRO_LEARN_PAGES=1 (DIVASTRO-142)
    from .site_hub import sitemap_paths as hub_paths  # same (DIVASTRO-133)
    return (paths + hub_paths() + rashifal_paths() + muhurat_paths() + vrat_paths() + vrat_city_paths()
            + recurring_paths() + nakshatra_paths() + katha_paths()
            + learn_paths())


LEGAL_PATHS = frozenset({"/terms", "/privacy", "/refund", "/contact"})
# Pages whose content really changes every day (sitemap <lastmod> = today).
# Everything else gets no <lastmod>: a date that is always "today" teaches
# crawlers to ignore the field (DIVASTRO-133).
DAILY_ROOTS = frozenset(TOOLS) | {"rashifal"}


_TOP_CITY_SLUGS = frozenset(c.slug for c in seo_cities.CITIES[:20])


def _segments(path: str) -> list[str]:
    parts = [p for p in i18n.strip_prefix(path)[1].split("/") if p]
    return parts[1:] if parts[:1] == ["en"] else parts       # katha: /en/katha/<slug>


def sitemap_priority(path: str) -> float:
    """A crawl-priority hint (Bing and others read it; Google ignores it, so
    this is mostly about the ORDER of the file). Home first, then the tool and
    explainer pages, the section hubs, the dated/yearly pages, and last the
    long tail of city pages; the regional-language copies sit 0.1 below the
    English/Hindi originals."""
    if path == "/":
        return 1.0
    lang, bare = i18n.strip_prefix(path)
    if bare in LEGAL_PATHS:
        return 0.3
    parts = _segments(path)
    root = parts[0] if parts else ""
    if root in TOOLS or root in ("kundali-milan", "free-kundali") or root == "vrat-tyohar":
        if len(parts) == 1:
            score = 0.9
        elif root == "vrat-tyohar" and parts[1].isdigit():
            score = 0.7
        else:                                   # a city page of a tool
            score = 0.6 if parts[1] in _TOP_CITY_SLUGS else 0.5
    elif root == "tyohar" and len(parts) >= 3:  # a festival's city page (DIVASTRO-140)
        score = 0.5
    else:
        score = 0.8 if len(parts) <= 1 else 0.7
    return round(score - (0.1 if lang not in (EN, HI) else 0.0), 1)


def sitemap_lastmod(path: str, today: str) -> str | None:
    parts = _segments(path)
    return today if parts and parts[0] in DAILY_ROOTS else None


def sitemap_ordered() -> list[str]:
    """sitemap_paths() best pages first (stable, so the module order is kept
    within a tier). Crawlers with a daily URL budget read the file top-down."""
    return [p for p, _ in _ranked()]


def _ranked() -> tuple[tuple[str, float], ...]:
    """(path, priority), best first. The ranking is memoised on the path list
    itself, so it is recomputed only if the set of listed pages changes."""
    return _rank(tuple(sitemap_paths()))


@functools.lru_cache(maxsize=4)
def _rank(paths: tuple[str, ...]) -> tuple[tuple[str, float], ...]:
    ranked = [(p, sitemap_priority(p)) for p in paths]
    ranked.sort(key=lambda item: -item[1])
    return tuple(ranked)


@router.get("/sitemap.xml")
def sitemap() -> Response:
    today = _today().isoformat()
    urls = []
    for path, priority in _ranked():
        fields = f"<loc>{xml_escape(SITE_URL + path)}</loc>"
        lastmod = sitemap_lastmod(path, today)
        if lastmod:
            fields += f"<lastmod>{lastmod}</lastmod><changefreq>daily</changefreq>"
        fields += f"<priority>{priority:.1f}</priority>"
        urls.append(f"<url>{fields}</url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    return Response(xml, media_type="application/xml",
                    headers={"Cache-Control": "public, max-age=3600"})


@router.get("/robots.txt")
def robots() -> PlainTextResponse:
    """Crawl everything public; keep crawlers out of the JSON API (no value to a
    searcher, real cost to us) and the operator console."""
    body = ("User-agent: *\n"
            "Disallow: /api/\n"
            "Disallow: /admin\n"
            "Allow: /\n\n"
            f"Sitemap: {SITE_URL}/sitemap.xml\n")
    return PlainTextResponse(body, headers={"Cache-Control": "public, max-age=3600"})
