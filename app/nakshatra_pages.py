"""Nakshatra and Rashi reference pages — DIVASTRO-115.

    /nakshatra, /nakshatra/<slug>  (27: ashwini … revati)   + /hi/ copies
    /rashi, /rashi/<slug>          (12, the rashifal slugs)   + /hi/ copies

"Ashwini nakshatra", "Rohini nakshatra gana", "Mesh rashi naam akshar" are
evergreen searches; these pages answer them in the raw HTML, EN and HI, in the
same style as the rashifal pages (rashifal_pages.py, whose shell pattern and
sign slugs this module reuses).

**Nothing that an engine knows is re-typed here.** Gana, yoni and nadi come
from astro/matching.py's Ashtakoot tables, the varna from its rashi table, the
ruling planet from chart_service.VIMSHOTTARI (the dasha engine's table) and the
spans, padas and rashis are geometry — see astro/namakshar.py, which also
holds the one curated table (deity, symbol, the 108 namakshar syllables) with
its sources. The trait texts live in nakshatra_text.py.

The only "live" fact is today's nakshatra (at sunrise in New Delhi, from the
same cached daily panchang the rashifal and /panchang pages read), so the
pages are cached until IST midnight like the rest of the SEO pages.

The Naam se Kundali Milan page (naam_milan.py) borrows this module's shell and
is listed in its sitemap/public-path set, so seo_pages, analytics and share
each need only one lazy hook for all of DIVASTRO-115.
"""

from __future__ import annotations

import datetime as dt
import functools
import json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from . import i18n, seo_cities
from .astro import matching
from .astro.namakshar import (BY_NAME, BY_SLUG, NAK_MIN, NAKSHATRA_LIST, PADA_MIN, SIGN_MIN,
                              Nakshatra, sign_padas)
from .chart_service import DOMICILE, ELEMENT, MODALITY, VIMSHOTTARI
from .nakshatra_text import NAKSHATRA_TRAITS, RASHI_TRAITS
from .rashifal_pages import BY_SLUG as RASHI_BY_SLUG, RASHIS, Rashi, path as rashifal_path
from .seo_pages import (ADSENSE_CLIENT, BRAND, SITE_URL, _STYLE, _cache_headers, _e, _footer,
                        _panchang, _today, page_language_bits)
from .share import seo_share

router = APIRouter()

LANGS = ("en", "hi")
NAAM_MILAN = "/naam-se-kundali-milan"
# DIVASTRO-121: the languages these pages (and naam_milan.py's, which share this
# shell) are really written in — see app/i18n.py. Other registry languages get
# /<code>/nakshatra etc. with the English text, noindex, and no sitemap/hreflang
# entry until their code is added here.
TRANSLATED = i18n.BASE_TRANSLATED
i18n.LOCALIZABLE_ROOTS.update({"nakshatra", "rashi", NAAM_MILAN.strip("/")})

ELEMENT_HI = {"Fire": "अग्नि", "Earth": "पृथ्वी", "Air": "वायु", "Water": "जल"}
QUALITY = {"Cardinal": ("Movable (Chara)", "चर"), "Fixed": ("Fixed (Sthira)", "स्थिर"),
           "Mutable": ("Dual (Dwiswabhava)", "द्विस्वभाव")}
YONI_GENDER_HI = {"male": "पुरुष", "female": "स्त्री"}
DASHA_YEARS = dict(VIMSHOTTARI)


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

def _pre(lang: str) -> str:
    return i18n.prefix(lang)


def nak_path(n: Nakshatra | None, lang: str) -> str:
    return f"{_pre(lang)}/nakshatra" + (f"/{n.slug}" if n else "")


def rashi_path(r: Rashi | None, lang: str) -> str:
    return f"{_pre(lang)}/rashi" + (f"/{r.slug}" if r else "")


def milan_path(lang: str) -> str:
    return _pre(lang) + NAAM_MILAN


def sitemap_paths() -> list[str]:
    """All canonical URLs of DIVASTRO-115: 28 + 13 + 1 per TRANSLATED language."""
    out = []
    for lang in i18n.ordered(TRANSLATED):
        out += [nak_path(n, lang) for n in (None, *NAKSHATRA_LIST)]
        out += [rashi_path(r, lang) for r in (None, *RASHIS)]
        out.append(milan_path(lang))
    return out


PUBLIC_PATHS = frozenset(sitemap_paths())


def is_public_path(p: str) -> bool:
    """For analytics.is_public_page: only the canonical URLs count."""
    return p in PUBLIC_PATHS


def share_text(path: str) -> str | None:
    """For share.seo_share_text. Built from the path alone — the Naam Milan
    result's names are in the query string and never reach here."""
    parts = [p for p in i18n.strip_prefix(path)[1].split("/") if p]
    if parts == ["naam-se-kundali-milan"]:
        return "Naam se Kundali Milan — match by first letters, free · नाम से कुंडली मिलान:"
    if parts == ["nakshatra"]:
        return "All 27 nakshatras — deity, gana, name letters · 27 नक्षत्र और उनके नामाक्षर:"
    if parts == ["rashi"]:
        return "All 12 rashis — lord, nakshatras, name letters · 12 राशियाँ और उनके नामाक्षर:"
    if len(parts) == 2 and parts[0] == "nakshatra" and parts[1] in BY_SLUG:
        n = BY_SLUG[parts[1]]
        return f"{n.name} nakshatra — traits & name letters · {n.name_hi} नक्षत्र:"
    if len(parts) == 2 and parts[0] == "rashi" and parts[1] in RASHI_BY_SLUG:
        r = RASHI_BY_SLUG[parts[1]]
        return f"{r.name} rashi ({r.english}) — traits & name letters · {r.name_hi} राशि:"
    return None


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------

def _deg(minutes: int) -> str:
    """Arc-minutes from 0° Aries -> "13°20′ Aries"-style text, sign-relative."""
    return f"{minutes // 60}°{minutes % 60:02d}′"


def _sign_name(index: int, lang: str) -> str:
    r = RASHIS[index]
    return r.name_hi if lang == "hi" else f"{r.name} ({r.english})"


def _point(minutes: int, lang: str, end: bool = False) -> str:
    """A sidereal longitude as degrees within its sign. An end point that falls
    exactly on a sign boundary is written as 30°00′ of the earlier sign."""
    sign, within = divmod(minutes, SIGN_MIN)
    if end and within == 0:
        sign, within = sign - 1, SIGN_MIN
    return f"{_deg(within)} {_sign_name(sign % 12, lang)}"


def span_text(n: Nakshatra, lang: str) -> str:
    return f"{_point(n.start_min, lang)} – {_point(n.start_min + NAK_MIN, lang, end=True)}"


def _planet(name: str, lang: str) -> str:
    return matching.PLANET_HI.get(name, name) if lang == "hi" else name


def _nak_label(n: Nakshatra, lang: str) -> str:
    return n.name_hi if lang == "hi" else n.name


def today_nakshatra(day: dt.date) -> Nakshatra | None:
    """The nakshatra at sunrise in New Delhi — the one /panchang shows."""
    name = (_panchang(seo_cities.DEFAULT.slug, day).get("summary") or {}).get("nakshatra")
    return BY_NAME.get(name)


# --------------------------------------------------------------------------
# Shell (the rashifal_pages pattern, with an optional extra <head> block)
# --------------------------------------------------------------------------

_EXTRA_STYLE = """
  .seo .note { font-size: 13.5px; color: var(--ink-faint); }
  .seo .syl { font-size: 20px; color: var(--gold-soft); letter-spacing: .04em; }
  .seo .lang-switch { font-size: 13.5px; }
  .seo form.milan { display: grid; gap: 12px; margin: 16px 0; }
  .seo form.milan label { display: grid; gap: 4px; font-size: 14px; color: var(--ink-dim); }
  .seo form.milan input, .seo form.milan select { font: inherit; padding: 10px 12px;
      border-radius: 10px; border: 1px solid var(--line); background: var(--inset-bg);
      color: var(--ink); max-width: 100%; }
  .seo form.milan button { font: inherit; font-weight: 600; padding: 12px 16px; border: 0;
      border-radius: 12px; color: #fff; cursor: pointer;
      background: linear-gradient(120deg, var(--primary-a), var(--primary-b)); }
  .seo .total { font-size: 22px; color: var(--gold-soft); }
"""

_SHELL = """<!DOCTYPE html>
<html lang="{html_lang}"><head><meta charset="utf-8"/>
{head_first}<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{description}"/>
<link rel="canonical" href="{canonical}"/>
{alternates}{head_extras}<meta property="og:type" content="article"/>
<meta property="og:site_name" content="{brand}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{description}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:image" content="{site}/static/icon-512.png"/>
<meta property="og:locale" content="{og_locale}"/>
<meta name="twitter:card" content="summary"/>
<meta name="google-adsense-account" content="{adsense}"/>
{ads}<script src="/static/visit.js" defer></script>   <!-- counts the page load: see analytics.py -->
<link rel="icon" href="/static/favicon.ico"/>
<link rel="apple-touch-icon" href="/static/apple-touch-icon.png"/>
<link rel="stylesheet" href="/static/styles.css"/>
<style>{style}</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body class="sacred">
<main class="seo">
  <div class="top"><a class="back" href="{home}">&larr; {brand}</a>{picker}</div>
  <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
  {notice}
  {body}
</main>
{footer}
</body></html>"""

_ADS = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?'
        'client={adsense}"\n        crossorigin="anonymous"></script>\n')


def shell(*, lang: str, en_path: str, hi_path: str, title: str, description: str,
          crumbs: list[tuple[str, str]], body: str, status: int = 200, cache: bool = True,
          head_first: str = "", ads: bool = True, share: bool = True,
          headers: dict[str, str] | None = None) -> HTMLResponse:
    """One page. `head_first` goes straight after <meta charset> (the Naam
    Milan result uses it for its referrer policy, which must precede every
    subresource). `ads=False` drops the AdSense script — never load a third
    party on a URL that carries a person's name."""
    own = hi_path if lang == "hi" else i18n.localized_path(en_path, lang)
    canonical = SITE_URL + own
    bits = page_language_bits(lang=lang, path=own, has_twin=status == 200,
                              translated=TRANSLATED, region=True, lang_paths={"en": en_path})
    trail = [("मुख्य पृष्ठ" if lang == "hi" else i18n.chrome("home", lang), "/")] + crumbs
    crumb_html = " › ".join(
        f'<a href="{_e(href)}">{_e(name)}</a>' if i < len(trail) - 1 else _e(name)
        for i, (name, href) in enumerate(trail))
    in_lang = bits["in_language"]
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": title, "description": description, "url": canonical,
             "inLanguage": in_lang,
             "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE_URL + "/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE_URL + href}
                for i, (name, href) in enumerate(trail)]},
        ],
    }
    jsonld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    page = _SHELL.format(
        html_lang=in_lang, head_first=head_first, title=_e(title), description=_e(description),
        canonical=_e(canonical), alternates=bits["alternates"],
        # No web font either where there are no ads: a URL carrying a person's
        # name loads nothing from a third party (system fonts render the script).
        head_extras=(bits["head"] if ads else
                     i18n.robots_meta(lang, TRANSLATED) + i18n.LANGPICK_SCRIPT),
        og_locale=bits["og_locale"], brand=_e(BRAND), site=_e(SITE_URL),
        home=_e(bits["home"]), picker=bits["picker"], notice=bits["notice"],
        adsense=ADSENSE_CLIENT, ads=_ADS.format(adsense=ADSENSE_CLIENT) if ads else "",
        style=_STYLE + _EXTRA_STYLE, jsonld=jsonld, crumbs=i18n.localize_links(crumb_html, lang),
        body=(seo_share(own) if share and status == 200 else "")
        + i18n.localize_links(body, lang),
        footer=_footer(lang))
    out = _cache_headers() if cache else {"Cache-Control": "no-store"}
    out.update(headers or {})
    return HTMLResponse(page, status_code=status, headers=out)


def kundali_cta(lang: str) -> str:
    text = ("अपनी मुफ़्त कुंडली बनाएँ — जानें आपका जन्म नक्षत्र और चंद्र राशि" if lang == "hi"
            else "Get your free kundali — find your exact birth nakshatra and Moon sign")
    return f'<a class="cta" href="/?open=kundali">{_e(text)}</a>'


def _links(items: list[tuple[str, str]], head: str) -> str:
    li = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in items)
    return f'<h2>{_e(head)}</h2><ul class="links">{li}</ul>'


def _more(lang: str) -> str:
    if lang == "hi":
        return _links([("/hi/nakshatra", "सभी 27 नक्षत्र"), ("/hi/rashi", "सभी 12 राशियाँ"),
                       (milan_path("hi"), "नाम से कुंडली मिलान"),
                       ("/hi/kundali-milan", "कुंडली मिलान (36 गुण)"),
                       ("/hi/rashifal", "आज का राशिफल"), ("/hi/panchang", "आज का पंचांग")],
                      "और भी")
    return _links([("/nakshatra", "All 27 nakshatras"), ("/rashi", "All 12 rashis"),
                   (milan_path("en"), "Naam se Kundali Milan"),
                   ("/kundali-milan", "Kundali Milan (36 guna)"),
                   ("/rashifal", "Today's Rashifal"), ("/panchang", "Today's Panchang")],
                  "More free tools")


def _nak_list(current: Nakshatra | None, lang: str) -> str:
    items = "".join(
        f'<li><a href="{nak_path(n, lang)}"' + (' aria-current="page"' if n == current else "")
        + f'>{n.index + 1}. {_e(_nak_label(n, lang))}</a></li>' for n in NAKSHATRA_LIST)
    head = "सभी 27 नक्षत्र" if lang == "hi" else "All 27 nakshatras"
    return f'<h2>{head}</h2><ul class="links">{items}</ul>'


def _rashi_list(current: Rashi | None, lang: str) -> str:
    items = "".join(
        f'<li><a href="{rashi_path(r, lang)}"' + (' aria-current="page"' if r == current else "")
        + f'>{_e(r.name_hi if lang == "hi" else f"{r.name} · {r.english}")}</a></li>'
        for r in RASHIS)
    head = "सभी 12 राशियाँ" if lang == "hi" else "All 12 rashis"
    return f'<h2>{head}</h2><ul class="links">{items}</ul>'


def _today_box(n: Nakshatra | None, day: dt.date, lang: str) -> str:
    t = today_nakshatra(day)
    pan = "/hi/panchang" if lang == "hi" else "/panchang"
    if t is None:
        return ""
    if lang == "hi":
        if n is not None and t == n:
            lead = f"<strong>आज (नई दिल्ली में सूर्योदय के समय) चंद्रमा {_e(n.name_hi)} नक्षत्र में है।</strong>"
        else:
            lead = (f'आज का नक्षत्र (नई दिल्ली में सूर्योदय के समय) '
                    f'<a href="{nak_path(t, lang)}"><strong>{_e(t.name_hi)}</strong></a> है।')
        tail = f' नक्षत्र का समाप्ति-समय, तिथि और राहु काल <a href="{pan}">आज के पंचांग</a> में देखें।'
    else:
        if n is not None and t == n:
            lead = f"<strong>Today the Moon is in {_e(n.name)} (at sunrise in New Delhi).</strong>"
        else:
            lead = (f"Today's nakshatra is <a href=\"{nak_path(t, lang)}\"><strong>{_e(t.name)}"
                    "</strong></a> (at sunrise in New Delhi).")
        tail = (f' Its end time, the tithi and Rahu Kaal are on <a href="{pan}">today\'s '
                "Panchang</a>.")
    return f'<div class="box"><p>{lead}{tail}</p></div>'


# --------------------------------------------------------------------------
# Nakshatra pages
# --------------------------------------------------------------------------

def _facts(n: Nakshatra, lang: str) -> str:
    hi = lang == "hi"
    yoni, gender = n.yoni
    signs = n.signs
    sign_links = ", ".join(
        f'<a href="{rashi_path(RASHIS[s], lang)}">{_e(_sign_name(s, lang))}</a>' for s in signs)
    varnas = ", ".join(
        dict.fromkeys(
            (matching.VARNA_HI[v] if hi else v)
            for v in (matching.VARNA_OF_RASHI[RASHIS[s].english] for s in signs)))
    nadi = n.nadi
    humour = matching.NADI_HUMOUR[nadi]
    if hi:
        rows = [
            ("क्रम", f"27 में से {n.index + 1}वाँ"),
            ("अंश (निरयण)", _e(span_text(n, lang))),
            ("राशि", sign_links),
            ("स्वामी ग्रह (विंशोत्तरी)", f"{_e(_planet(n.lord, lang))} "
             f"<small>महादशा {DASHA_YEARS[n.lord]} वर्ष</small>"),
            ("देवता", _e(n.deity_hi)),
            ("प्रतीक", _e(n.symbol_hi)),
            ("गण", _e(matching.GANA_HI[n.gana])),
            ("योनि", f"{_e(matching.YONI_HI[yoni])} <small>{YONI_GENDER_HI[gender]}</small>"),
            ("नाड़ी", f"{_e(matching.NADI_HI[nadi])} <small>{matching.NADI_HUMOUR_HI[humour]}</small>"),
            ("वर्ण (राशि से, गुण मिलान में)", _e(varnas)),
            ("नामाक्षर", f'<span class="syl">{_e(" ".join(d for d, _ in n.syllables))}</span>'),
        ]
    else:
        rows = [
            ("Number", f"{n.index + 1} of 27"),
            ("Span (sidereal)", _e(span_text(n, lang))),
            ("Rashi", sign_links),
            ("Ruling planet (Vimshottari lord)", f"{_e(n.lord)} "
             f"<small>{DASHA_YEARS[n.lord]}-year mahadasha</small>"),
            ("Deity", _e(n.deity)),
            ("Symbol", _e(n.symbol)),
            ("Gana", f"{_e(n.gana)} <small lang=\"hi\">{matching.GANA_HI[n.gana]}</small>"),
            ("Yoni (animal)", f"{_e(yoni)} <small>{gender}</small>"),
            ("Nadi", f"{_e(nadi)} <small>{humour}</small>"),
            ("Varna (from its rashi, as used in Guna Milan)", _e(varnas)),
            ("Name syllables (namakshar)",
             f'<span class="syl" lang="hi">{_e(" ".join(d for d, _ in n.syllables))}</span> '
             f'<small>{_e(", ".join(l for _, l in n.syllables))}</small>'),
        ]
    body = "".join(f'<tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rows)
    return f'<div class="scroll"><table>{body}</table></div>'


def _pada_table(n: Nakshatra, lang: str) -> str:
    hi = lang == "hi"
    head = ("<tr><th>चरण</th><th>अंश</th><th>राशि</th><th>नामाक्षर</th></tr>" if hi else
            "<tr><th>Pada</th><th>Span</th><th>Rashi</th><th>Name syllable</th></tr>")
    rows = []
    for p in range(1, 5):
        start = n.start_min + (p - 1) * PADA_MIN
        sign = n.pada_sign(p)
        dev, lat = n.syllables[p - 1]
        rows.append(
            f"<tr><td>{p}</td><td>{_e(_point(start, lang))} – "
            f"{_e(_point(start + PADA_MIN, lang, end=True))}</td>"
            f'<td><a href="{rashi_path(RASHIS[sign], lang)}">{_e(_sign_name(sign, lang))}</a></td>'
            f'<td><span class="syl" lang="hi">{_e(dev)}</span> <small>{_e(lat)}</small></td></tr>')
    title = "चार चरण और नामाक्षर" if hi else "The four padas and their name syllables"
    note = ("<p class=\"note\">परंपरा में बच्चे का नाम जन्म नक्षत्र के चरण के अक्षर से रखा जाता है "
            "(नामाक्षर)। अक्षर ड्रिक पंचांग में प्रकाशित स्वर-सिद्धांत की 108 चरण-अक्षरों की सूची "
            "(अवकहड़ा चक्र) के अनुसार हैं।</p>" if hi else
            "<p class=\"note\">Traditionally a child's name begins with the syllable of the pada the "
            "Moon occupied at birth (namakshar). Syllables follow the 108-pada Swar Siddhanta list "
            "(the Avakahada Chakra) as published by Drik Panchang.</p>")
    return (f"<h2>{title}</h2><div class=\"scroll\"><table>{head}{''.join(rows)}</table></div>"
            + note)


def _related(n: Nakshatra, lang: str) -> str:
    hi = lang == "hi"
    items = []
    for s in n.signs:
        r = RASHIS[s]
        items.append((rashifal_path(r, lang),
                      f"आज का {r.name_hi} राशिफल" if hi else f"Today's {r.name} Rashifal"))
    prev_n = NAKSHATRA_LIST[(n.index - 1) % 27]
    next_n = NAKSHATRA_LIST[(n.index + 1) % 27]
    items += [(nak_path(prev_n, lang), ("← " + _nak_label(prev_n, lang))),
              (nak_path(next_n, lang), (_nak_label(next_n, lang) + " →")),
              (milan_path(lang), "नाम से कुंडली मिलान" if hi else "Naam se Kundali Milan"),
              ("/hi/panchang" if hi else "/panchang", "आज का पंचांग" if hi else "Today's Panchang")]
    return _links(items, "संबंधित" if hi else "Related")


@functools.lru_cache(maxsize=128)
def _nak_page(day: dt.date, slug: str, lang: str) -> tuple[str, str, str]:
    n = BY_SLUG[slug]
    hi = lang == "hi"
    syl = " ".join(d for d, _ in n.syllables)
    lat = ", ".join(l for _, l in n.syllables)
    if hi:
        title = (f"{n.name_hi} नक्षत्र — देवता, स्वामी, गण, योनि, नाड़ी और नामाक्षर ({syl}) | "
                 f"{BRAND}")
        description = (f"{n.name_hi} नक्षत्र ({n.name}): {span_text(n, lang)}, स्वामी "
                       f"{_planet(n.lord, lang)}, देवता {n.deity_hi}, {matching.GANA_HI[n.gana]} "
                       f"गण, नाड़ी {matching.NADI_HI[n.nadi]}। नामाक्षर {syl} और स्वभाव।")
        h1, sub = f"{n.name_hi} नक्षत्र", f"{n.name} Nakshatra"
    else:
        title = (f"{n.name} Nakshatra — Deity, Lord, Gana, Yoni, Nadi & Name Letters "
                 f"({lat}) | {BRAND}")
        description = (f"{n.name} nakshatra ({n.name_hi}): {span_text(n, lang)}, ruled by "
                       f"{n.lord}, deity {n.deity.split(',')[0]}, {n.gana} gana, {n.nadi} nadi, "
                       f"{n.yoni[0]} yoni. Name syllables {lat} and traits.")
        h1, sub = f"{n.name} Nakshatra", f"{n.name_hi} नक्षत्र"
    trait_head = "स्वभाव" if hi else "Nature and traits"
    trait_note = ("<p class=\"note\">ये पारंपरिक प्रवृत्तियाँ हैं, निर्णय नहीं। आपकी पूरी कुंडली — "
                  "लग्न, ग्रह और दशा — व्यक्तिगत चित्र देती है।</p>" if hi else
                  "<p class=\"note\">These are traditional tendencies, not verdicts. Your full "
                  "kundali — ascendant, planets and dasha — gives the personal picture.</p>")
    body = f"""
<h1>{_e(h1)}</h1>
<p class="hi" lang="{'en' if hi else 'hi'}">{_e(sub)}</p>
{_today_box(n, day, lang)}
{_facts(n, lang)}
<h2>{trait_head}</h2>
<p>{_e(i18n.pick(NAKSHATRA_TRAITS[n.slug], lang))}</p>
{trait_note}
{_pada_table(n, lang)}
{kundali_cta(lang)}
{_related(n, lang)}
{_nak_list(n, lang)}"""
    return title, description, body


@functools.lru_cache(maxsize=8)
def _nak_index(day: dt.date, lang: str) -> tuple[str, str, str]:
    hi = lang == "hi"
    head = ("<tr><th>#</th><th>नक्षत्र</th><th>राशि</th><th>स्वामी</th><th>गण</th>"
            "<th>नामाक्षर</th></tr>" if hi else
            "<tr><th>#</th><th>Nakshatra</th><th>Rashi</th><th>Lord</th><th>Gana</th>"
            "<th>Name syllables</th></tr>")
    rows = []
    for n in NAKSHATRA_LIST:
        signs = " / ".join(RASHIS[s].name_hi if hi else RASHIS[s].name for s in n.signs)
        gana = matching.GANA_HI[n.gana] if hi else n.gana
        rows.append(
            f'<tr><td>{n.index + 1}</td><td><a href="{nak_path(n, lang)}">'
            f"{_e(_nak_label(n, lang))}</a></td><td>{_e(signs)}</td>"
            f"<td>{_e(_planet(n.lord, lang))}</td><td>{_e(gana)}</td>"
            f'<td lang="hi">{_e(" ".join(d for d, _ in n.syllables))}</td></tr>')
    if hi:
        title = f"27 नक्षत्र — नाम, स्वामी, देवता, गण और नामाक्षर की पूरी सूची | {BRAND}"
        description = ("अश्विनी से रेवती तक सभी 27 नक्षत्र: हर नक्षत्र के अंश, राशि, स्वामी ग्रह, "
                       "देवता, गण, योनि, नाड़ी और चारों चरणों के नामाक्षर — कुंडली मिलान की तालिकाओं "
                       "से मेल खाते हुए।")
        h1, sub = "27 नक्षत्र", "The 27 Nakshatras"
        intro = ("<p>वैदिक ज्योतिष में राशि-चक्र 27 नक्षत्रों में बँटा है — हर नक्षत्र 13°20′ का, "
                 "और हर नक्षत्र के 3°20′ के चार चरण। कुल 108 चरण 12 राशियों में बँटते हैं, हर राशि "
                 "में ठीक 9 चरण। आपका जन्म नक्षत्र वह है जिसमें जन्म के समय चंद्रमा था; उसी से "
                 "विंशोत्तरी दशा शुरू होती है और कुंडली मिलान के तारा, योनि, गण और नाड़ी कूट "
                 "देखे जाते हैं।</p>")
    else:
        title = f"The 27 Nakshatras — Lords, Deities, Gana & Name Syllables | {BRAND}"
        description = ("All 27 nakshatras from Ashwini to Revati: span, rashi, ruling planet, "
                       "deity, gana, yoni, nadi and the name syllables of all four padas — "
                       "consistent with our Kundali Milan tables.")
        h1, sub = "The 27 Nakshatras", "27 नक्षत्र"
        intro = ("<p>Vedic astrology divides the zodiac into 27 nakshatras (lunar mansions) of "
                 "13°20′ each, and each nakshatra into four padas of 3°20′. The 108 padas fall "
                 "exactly nine to a sign across the 12 rashis. Your birth nakshatra is the one the "
                 "Moon occupied when you were born: it starts your Vimshottari dasha and drives "
                 "the Tara, Yoni, Gana and Nadi kootas of Kundali Milan.</p>")
    body = f"""
<h1>{_e(h1)}</h1>
<p class="hi" lang="{'en' if hi else 'hi'}">{_e(sub)}</p>
{intro}
{_today_box(None, day, lang)}
<div class="scroll"><table>{head}{''.join(rows)}</table></div>
{kundali_cta(lang)}
{_more(lang)}"""
    return title, description, body


def _crumb_nak(lang: str) -> tuple[str, str]:
    return ("नक्षत्र", "/hi/nakshatra") if lang == "hi" else ("Nakshatras", "/nakshatra")


def _crumb_rashi(lang: str) -> tuple[str, str]:
    return ("राशियाँ", "/hi/rashi") if lang == "hi" else ("Rashis", "/rashi")


def render_nak_index(lang: str, day: dt.date | None = None) -> HTMLResponse:
    title, description, body = _nak_index(day or _today(), lang)
    return shell(lang=lang, en_path=nak_path(None, "en"), hi_path=nak_path(None, "hi"),
                 title=title, description=description, crumbs=[_crumb_nak(lang)], body=body)


def render_nak(slug: str, lang: str, day: dt.date | None = None) -> HTMLResponse:
    n = BY_SLUG[slug]
    title, description, body = _nak_page(day or _today(), slug, lang)
    return shell(lang=lang, en_path=nak_path(n, "en"), hi_path=nak_path(n, "hi"),
                 title=title, description=description,
                 crumbs=[_crumb_nak(lang), (_nak_label(n, lang), nak_path(n, lang))], body=body)


def _not_found(kind: str, slug: str, lang: str) -> HTMLResponse:
    hi = lang == "hi"
    if kind == "nakshatra":
        head = "नक्षत्र नहीं मिला" if hi else "Nakshatra not found"
        lst, crumb = _nak_list(None, lang), _crumb_nak(lang)
    else:
        head = "राशि नहीं मिली" if hi else "Rashi not found"
        lst, crumb = _rashi_list(None, lang), _crumb_rashi(lang)
    body = f"<h1>{head}</h1><p>“{_e(slug)}”</p>{lst}"
    base = f"/{kind}"
    return shell(lang=lang, en_path=base, hi_path="/hi" + base, title=f"{head} — {BRAND}",
                 description=head, crumbs=[crumb], body=body, status=404, cache=False)


def _alias(slug: str) -> str:
    return slug.lower().replace("_", "-").replace(" ", "-")


# Common alternative spellings -> canonical slug (301).
NAK_ALIASES = {
    "ashvini": "ashwini", "aswini": "ashwini", "kritika": "krittika", "mrigasira": "mrigashira",
    "mrigshira": "mrigashira", "aardra": "ardra", "arudra": "ardra", "pushyami": "pushya",
    "pushyam": "pushya", "aslesha": "ashlesha", "ashlesa": "ashlesha", "makha": "magha",
    "purvaphalguni": "purva-phalguni", "uttaraphalguni": "uttara-phalguni", "hastha": "hasta",
    "chithra": "chitra", "chitta": "chitra", "svati": "swati", "visakha": "vishakha",
    "vishaka": "vishakha", "anuradha": "anuradha", "jyeshta": "jyeshtha", "jyestha": "jyeshtha",
    "moola": "mula", "purvashadha": "purva-ashadha", "poorvashada": "purva-ashadha",
    "uttarashadha": "uttara-ashadha", "uthradam": "uttara-ashadha", "sravana": "shravana",
    "shravan": "shravana", "dhanishtha": "dhanishta", "shatabhishak": "shatabhisha",
    "satabhisha": "shatabhisha", "purvabhadrapada": "purva-bhadrapada",
    "uttarabhadrapada": "uttara-bhadrapada", "revathi": "revati",
}


def _resolve_nak(slug: str, lang: str):
    if slug in BY_SLUG:
        return render_nak(slug, lang)
    key = _alias(slug)
    target = key if key in BY_SLUG else NAK_ALIASES.get(key.replace("-", ""))
    if target is None:
        target = next((n.slug for n in NAKSHATRA_LIST if n.slug.replace("-", "") == key.replace("-", "")), None)
    if target:
        return RedirectResponse(nak_path(BY_SLUG[target], lang), status_code=301)
    return _not_found("nakshatra", slug, lang)


# --------------------------------------------------------------------------
# Rashi pages
# --------------------------------------------------------------------------

def _rashi_facts(r: Rashi, lang: str) -> str:
    hi = lang == "hi"
    lord = DOMICILE[r.english]
    element = ELEMENT[r.english]
    quality_en, quality_hi = QUALITY[MODALITY[r.english]]
    varna = matching.VARNA_OF_RASHI[r.english]
    span = f"{r.index * 30}° – {r.index * 30 + 30}°"
    padas = sign_padas(r.index)
    naks = list(dict.fromkeys(n for n, _ in padas))
    nak_links = ", ".join(f'<a href="{nak_path(n, lang)}">{_e(_nak_label(n, lang))}</a>'
                          for n in naks)
    syl = " ".join(n.syllables[p - 1][0] for n, p in padas)
    if hi:
        rows = [("क्रम", f"12 में से {r.index + 1}वीं"),
                ("अंश (निरयण राशि-चक्र)", span),
                ("स्वामी ग्रह", _e(_planet(lord, lang))),
                ("तत्व", ELEMENT_HI[element]),
                ("स्वभाव (गुण)", quality_hi),
                ("वर्ण (गुण मिलान में)", matching.VARNA_HI[varna]),
                ("नक्षत्र", nak_links),
                ("नामाक्षर", f'<span class="syl">{_e(syl)}</span>')]
    else:
        rows = [("Number", f"{r.index + 1} of 12"),
                ("Span (sidereal zodiac)", span),
                ("Sign lord", _e(lord)),
                ("Element", element),
                ("Quality", quality_en),
                ("Varna (used in Guna Milan)", varna),
                ("Nakshatras", nak_links),
                ("Name syllables (namakshar)", f'<span class="syl" lang="hi">{_e(syl)}</span>')]
    body = "".join(f'<tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rows)
    return f'<div class="scroll"><table>{body}</table></div>'


def _rashi_padas(r: Rashi, lang: str) -> str:
    hi = lang == "hi"
    head = ("<tr><th>नक्षत्र</th><th>चरण</th><th>अंश</th><th>नामाक्षर</th></tr>" if hi else
            "<tr><th>Nakshatra</th><th>Pada</th><th>Degrees in sign</th><th>Syllable</th></tr>")
    rows = []
    for i, (n, p) in enumerate(sign_padas(r.index)):
        lo, hi_m = i * PADA_MIN, (i + 1) * PADA_MIN
        dev, lat = n.syllables[p - 1]
        rows.append(f'<tr><td><a href="{nak_path(n, lang)}">{_e(_nak_label(n, lang))}</a></td>'
                    f"<td>{p}</td><td>{_deg(lo)} – {_deg(hi_m)}</td>"
                    f'<td><span class="syl" lang="hi">{_e(dev)}</span> <small>{_e(lat)}</small>'
                    "</td></tr>")
    title = ("इस राशि के 9 नक्षत्र-चरण" if hi else "The nine nakshatra padas in this sign")
    return f"<h2>{title}</h2><div class=\"scroll\"><table>{head}{''.join(rows)}</table></div>"


@functools.lru_cache(maxsize=64)
def _rashi_page(slug: str, lang: str) -> tuple[str, str, str]:
    r = RASHI_BY_SLUG[slug]
    hi = lang == "hi"
    lord = DOMICILE[r.english]
    padas = sign_padas(r.index)
    syl = " ".join(n.syllables[p - 1][0] for n, p in padas)
    lat = ", ".join(n.syllables[p - 1][1] for n, p in padas)
    if hi:
        title = f"{r.name_hi} राशि — स्वामी, तत्व, नक्षत्र, नामाक्षर ({syl}) और स्वभाव | {BRAND}"
        description = (f"{r.name_hi} राशि ({r.name}, {r.english}): स्वामी {_planet(lord, lang)}, "
                       f"{ELEMENT_HI[ELEMENT[r.english]]} तत्व, {QUALITY[MODALITY[r.english]][1]} "
                       f"स्वभाव। इसके 9 नक्षत्र-चरण, नामाक्षर {syl} और स्वभाव।")
        h1, sub = f"{r.name_hi} राशि", f"{r.name} Rashi · {r.english}"
        today = f"आज का {r.name_hi} राशिफल पढ़ें"
    else:
        title = (f"{r.name} Rashi ({r.english}) — Lord, Element, Nakshatras & Name Letters | "
                 f"{BRAND}")
        description = (f"{r.name} rashi ({r.english} Moon sign, {r.name_hi}): ruled by {lord}, "
                       f"{ELEMENT[r.english].lower()} element, {QUALITY[MODALITY[r.english]][0].lower()}"
                       f" quality. Its 9 nakshatra padas, name syllables ({lat}) and traits.")
        h1, sub = f"{r.name} Rashi — {r.english} Moon Sign", f"{r.name_hi} राशि"
        today = f"Read today's {r.name} Rashifal"
    trait_head = "स्वभाव" if hi else "Nature and traits"
    note = ("<p class=\"note\">वैदिक ज्योतिष में राशि का अर्थ प्रायः चंद्र राशि होता है — जन्म के समय "
            "चंद्रमा जिस राशि में था। यह अक्सर पश्चिमी सूर्य राशि से अलग होती है।</p>" if hi else
            "<p class=\"note\">In Vedic astrology \"rashi\" usually means the Moon sign — the sign "
            "the Moon occupied at birth, in the sidereal zodiac. It is often different from a "
            "Western sun sign.</p>")
    body = f"""
<h1>{_e(h1)}</h1>
<p class="hi" lang="{'en' if hi else 'hi'}">{_e(sub)}</p>
<div class="box"><p><a href="{rashifal_path(r, lang)}"><strong>{_e(today)}</strong></a></p></div>
{_rashi_facts(r, lang)}
<h2>{trait_head}</h2>
<p>{_e(i18n.pick(RASHI_TRAITS[r.slug], lang))}</p>
{note}
{_rashi_padas(r, lang)}
{kundali_cta(lang)}
{_rashi_list(r, lang)}
{_more(lang)}"""
    return title, description, body


@functools.lru_cache(maxsize=4)
def _rashi_index(lang: str) -> tuple[str, str, str]:
    hi = lang == "hi"
    head = ("<tr><th>राशि</th><th>स्वामी</th><th>तत्व</th><th>नक्षत्र</th><th>नामाक्षर</th></tr>"
            if hi else
            "<tr><th>Rashi</th><th>Lord</th><th>Element</th><th>Nakshatras</th>"
            "<th>Name syllables</th></tr>")
    rows = []
    for r in RASHIS:
        padas = sign_padas(r.index)
        naks = list(dict.fromkeys(n for n, _ in padas))
        name = (f"{r.name_hi} <small>{_e(r.name)}</small>" if hi
                else f"{_e(r.name)} <small>{_e(r.english)}</small>")
        el = ELEMENT[r.english]
        rows.append(
            f'<tr><td><a href="{rashi_path(r, lang)}">{name}</a></td>'
            f"<td>{_e(_planet(DOMICILE[r.english], lang))}</td>"
            f"<td>{ELEMENT_HI[el] if hi else el}</td>"
            f"<td>{_e(', '.join(_nak_label(n, lang) for n in naks))}</td>"
            f'<td lang="hi">{_e(" ".join(n.syllables[p - 1][0] for n, p in padas))}</td></tr>')
    if hi:
        title = f"12 राशियाँ — स्वामी, तत्व, नक्षत्र और नामाक्षर की पूरी सूची | {BRAND}"
        description = ("मेष से मीन तक सभी 12 राशियाँ: हर राशि का स्वामी ग्रह, तत्व, स्वभाव, उसमें "
                       "आने वाले 9 नक्षत्र-चरण और नाम के पहले अक्षर (नामाक्षर)।")
        h1, sub = "12 राशियाँ", "The 12 Rashis (Moon signs)"
        intro = ("<p>हर राशि 30° की है और उसमें ठीक 9 नक्षत्र-चरण आते हैं। आपकी राशि (चंद्र राशि) "
                 "वह है जिसमें जन्म के समय चंद्रमा था — राशिफल, साढ़ेसाती और कुंडली मिलान इसी से "
                 "देखे जाते हैं।</p>")
    else:
        title = f"The 12 Rashis — Lords, Elements, Nakshatras & Name Letters | {BRAND}"
        description = ("All 12 rashis (Vedic Moon signs) from Mesh to Meen: sign lord, element, "
                       "quality, the nine nakshatra padas in each and their name syllables "
                       "(namakshar).")
        h1, sub = "The 12 Rashis (Moon Signs)", "12 राशियाँ"
        intro = ("<p>Each rashi spans 30° of the sidereal zodiac and holds exactly nine nakshatra "
                 "padas. Your rashi is your Moon sign — the sign the Moon occupied at birth — and "
                 "it is what rashifal, Sade Sati and Kundali Milan are read from.</p>")
    body = f"""
<h1>{_e(h1)}</h1>
<p class="hi" lang="{'en' if hi else 'hi'}">{_e(sub)}</p>
{intro}
<div class="scroll"><table>{head}{''.join(rows)}</table></div>
{kundali_cta(lang)}
{_more(lang)}"""
    return title, description, body


def render_rashi_index(lang: str) -> HTMLResponse:
    title, description, body = _rashi_index(lang)
    return shell(lang=lang, en_path=rashi_path(None, "en"), hi_path=rashi_path(None, "hi"),
                 title=title, description=description, crumbs=[_crumb_rashi(lang)], body=body)


def render_rashi(slug: str, lang: str) -> HTMLResponse:
    r = RASHI_BY_SLUG[slug]
    title, description, body = _rashi_page(slug, lang)
    return shell(lang=lang, en_path=rashi_path(r, "en"), hi_path=rashi_path(r, "hi"),
                 title=title, description=description,
                 crumbs=[_crumb_rashi(lang), (r.name_hi if lang == "hi" else r.name,
                                              rashi_path(r, lang))], body=body)


def _resolve_rashi(slug: str, lang: str):
    if slug in RASHI_BY_SLUG:
        return render_rashi(slug, lang)
    key = _alias(slug)
    r = RASHI_BY_SLUG.get(key) or next((x for x in RASHIS if x.english_slug == key), None)
    if r:
        return RedirectResponse(rashi_path(r, lang), status_code=301)
    return _not_found("rashi", slug, lang)


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@router.get("/nakshatra", response_class=HTMLResponse)
def nakshatra_index() -> HTMLResponse:
    return render_nak_index("en")


@router.get("/hi/nakshatra", response_class=HTMLResponse)
def nakshatra_index_hi() -> HTMLResponse:
    return render_nak_index("hi")


@router.get("/nakshatra/{slug}", response_class=HTMLResponse)
def nakshatra_page(slug: str):
    return _resolve_nak(slug, "en")


@router.get("/hi/nakshatra/{slug}", response_class=HTMLResponse)
def nakshatra_page_hi(slug: str):
    return _resolve_nak(slug, "hi")


@router.get("/rashi", response_class=HTMLResponse)
def rashi_index() -> HTMLResponse:
    return render_rashi_index("en")


@router.get("/hi/rashi", response_class=HTMLResponse)
def rashi_index_hi() -> HTMLResponse:
    return render_rashi_index("hi")


@router.get("/rashi/{slug}", response_class=HTMLResponse)
def rashi_page(slug: str):
    return _resolve_rashi(slug, "en")


@router.get("/hi/rashi/{slug}", response_class=HTMLResponse)
def rashi_page_hi(slug: str):
    return _resolve_rashi(slug, "hi")


# DIVASTRO-121: the same pages under /kn/, /te/, ... (i18n.EXTRA_CODES).
@router.get("/{lang:xlang}/nakshatra", response_class=HTMLResponse)
def nakshatra_index_lang(lang: str) -> HTMLResponse:
    return render_nak_index(lang)


@router.get("/{lang:xlang}/nakshatra/{slug}", response_class=HTMLResponse)
def nakshatra_page_lang(lang: str, slug: str):
    return _resolve_nak(slug, lang)


@router.get("/{lang:xlang}/rashi", response_class=HTMLResponse)
def rashi_index_lang(lang: str) -> HTMLResponse:
    return render_rashi_index(lang)


@router.get("/{lang:xlang}/rashi/{slug}", response_class=HTMLResponse)
def rashi_page_lang(lang: str, slug: str):
    return _resolve_rashi(slug, lang)
