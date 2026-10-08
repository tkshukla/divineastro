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

from . import i18n, lang_data, seo_cities
from .astro import matching
from .astro.namakshar import (BY_NAME, BY_SLUG, NAK_MIN, NAKSHATRA_LIST, PADA_MIN, SIGN_MIN,
                              Nakshatra, sign_padas)
from .chart_service import DOMICILE, ELEMENT, MODALITY, VIMSHOTTARI
# DIVASTRO-123: every word of these pages is in nakshatra_page_text.TEXT (and the
# trait paragraphs in nakshatra_text), per language; names from names_i18n.
from .nakshatra_page_text import TEXT
from .nakshatra_text import FACTS, NAKSHATRA_TRAITS, RASHI_TRAITS
from .rashifal_pages import BY_SLUG as RASHI_BY_SLUG, RASHIS, Rashi, path as rashifal_path
from .seo_pages import (ADSENSE_CLIENT, BRAND, SITE_URL, _STYLE, _cache_headers, _e, _footer,
                        _panchang, _strip, _today, page_language_bits)
from .share import seo_share

router = APIRouter()

LANGS = ("en", "hi")
NAAM_MILAN = "/naam-se-kundali-milan"
# DIVASTRO-121: the languages these pages (and naam_milan.py's, which share this
# shell) are really written in — see app/i18n.py. Other registry languages get
# /<code>/nakshatra etc. with the English text, noindex, and no sitemap/hreflang
# entry until their code is added here.
# DIVASTRO-143: + every new language whose app/lang_data/<code>.py READY includes "nakshatra".
TRANSLATED = lang_data.translated("nakshatra", i18n.BASE_TRANSLATED, lang_data.LEGACY_CODES)  # DIVASTRO-123/143
i18n.LOCALIZABLE_ROOTS.update({"nakshatra", "rashi", NAAM_MILAN.strip("/")})

DASHA_YEARS = dict(VIMSHOTTARI)


def _tx(key: str, lang: str, **values) -> str:
    """This module's text for `key` in `lang` (nakshatra_page_text.TEXT), formatted."""
    return i18n.fmt(key, lang, TEXT, **values)


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


def rashi_name(r: Rashi, lang: str) -> str:
    """'Mesh' / 'मेष' / the names_<code> word: the Rashi's own `name_<lang>`, its
    Indian name in English, else names_<code>.RASHI."""
    own = getattr(r, f"name_{lang}", None)
    if own:
        return own
    if lang == i18n.DEFAULT:
        return r.name
    return i18n.names(lang).RASHI.get(r.english, r.name)


def _sign_name(index: int, lang: str) -> str:
    r = RASHIS[index]
    return _tx("sign", lang, name=rashi_name(r, lang), english=r.english)


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
    return i18n.names(lang).GRAHA.get(name, name)


def _nak_label(n: Nakshatra, lang: str) -> str:
    """The nakshatra's own `name_<lang>` (namakshar has name_hi), else names_<code>."""
    return getattr(n, f"name_{lang}", None) or i18n.names(lang).NAKSHATRAS.get(n.name, n.name)


def _own(obj, field: str, lang: str) -> str:
    """`obj.<field>_<lang>` (deity_hi, symbol_hi) if the data has it, else
    nakshatra_text.FACTS[lang] (DIVASTRO-123: the regional languages), else English."""
    return (getattr(obj, f"{field}_{lang}", None)
            or FACTS.get(lang, {}).get(f"{field}.{getattr(obj, 'slug', '')}")
            or getattr(obj, field))


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
<meta property="og:image" content="{site}/static/og-card.jpg"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="og:locale" content="{og_locale}"/>
<meta name="twitter:card" content="summary_large_image"/>
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
  {body}{strip}
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
    # `hi_path` is kept for callers; every copy's URL is the English one localized.
    own = i18n.localized_path(en_path, lang)
    canonical = SITE_URL + own
    bits = page_language_bits(lang=lang, path=own, has_twin=status == 200,
                              translated=TRANSLATED, region=True, lang_paths={"en": en_path})
    home = TEXT[lang]["home"] if i18n.has("home", lang, TEXT) else i18n.chrome("home", lang)
    trail = [(home, "/")] + crumbs
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
        strip=_strip(lang=lang, path=own, title=title) if share and status == 200 else "",
        footer=_footer(lang))
    out = _cache_headers() if cache else {"Cache-Control": "no-store"}
    out.update(headers or {})
    return HTMLResponse(page, status_code=status, headers=out)


def kundali_cta(lang: str) -> str:
    return f'<a class="cta" href="/?open=kundali">{_e(_tx("kundali_cta", lang))}</a>'


def _links(items: list[tuple[str, str]], head: str) -> str:
    li = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in items)
    return f'<h2>{_e(head)}</h2><ul class="links">{li}</ul>'


def _more(lang: str) -> str:
    pre = _pre(lang)
    return _links([(pre + "/nakshatra", _tx("more.naks", lang)),
                   (pre + "/rashi", _tx("more.rashis", lang)),
                   (milan_path(lang), _tx("more.milan", lang)),
                   (pre + "/kundali-milan", _tx("more.kundali_milan", lang)),
                   (pre + "/rashifal", _tx("more.rashifal", lang)),
                   (pre + "/panchang", _tx("more.panchang", lang))],
                  _tx("more.heading", lang))


def _nak_list(current: Nakshatra | None, lang: str) -> str:
    items = "".join(
        f'<li><a href="{nak_path(n, lang)}"' + (' aria-current="page"' if n == current else "")
        + f'>{n.index + 1}. {_e(_nak_label(n, lang))}</a></li>' for n in NAKSHATRA_LIST)
    return f'<h2>{_tx("list.naks", lang)}</h2><ul class="links">{items}</ul>'


def _rashi_pill(r: Rashi, lang: str) -> str:
    return _tx("sign.pill", lang, name=rashi_name(r, lang), english=r.english)


def _rashi_list(current: Rashi | None, lang: str) -> str:
    items = "".join(
        f'<li><a href="{rashi_path(r, lang)}"' + (' aria-current="page"' if r == current else "")
        + f'>{_e(_rashi_pill(r, lang))}</a></li>'
        for r in RASHIS)
    return f'<h2>{_tx("list.rashis", lang)}</h2><ul class="links">{items}</ul>'


def _today_box(n: Nakshatra | None, day: dt.date, lang: str) -> str:
    t = today_nakshatra(day)
    pan = _pre(lang) + "/panchang"
    if t is None:
        return ""
    if n is not None and t == n:
        lead = _tx("today.same", lang, name=_e(_nak_label(n, lang)))
    else:
        lead = _tx("today.other", lang, href=nak_path(t, lang), name=_e(_nak_label(t, lang)))
    tail = _tx("today.tail", lang, pan=pan)
    return f'<div class="box"><p>{lead}{tail}</p></div>'


# --------------------------------------------------------------------------
# Nakshatra pages
# --------------------------------------------------------------------------

def _facts(n: Nakshatra, lang: str) -> str:
    names = i18n.names(lang)
    yoni, gender = n.yoni
    signs = n.signs
    sign_links = ", ".join(
        f'<a href="{rashi_path(RASHIS[s], lang)}">{_e(_sign_name(s, lang))}</a>' for s in signs)
    varnas = ", ".join(
        dict.fromkeys(
            names.VARNA.get(v, v)
            for v in (matching.VARNA_OF_RASHI[RASHIS[s].english] for s in signs)))
    nadi = n.nadi
    humour = matching.NADI_HUMOUR[nadi]
    rows = [
        ("f.number", _tx("f.number_v", lang, n=n.index + 1)),
        ("f.span", _e(span_text(n, lang))),
        ("f.rashi", sign_links),
        ("f.lord", _tx("f.lord_v", lang, lord=_e(_planet(n.lord, lang)),
                       years=DASHA_YEARS[n.lord])),
        ("f.deity", _e(_own(n, "deity", lang))),
        ("f.symbol", _e(_own(n, "symbol", lang))),
        ("f.gana", _tx("f.gana_v", lang, gana=_e(names.GANA.get(n.gana, n.gana)),
                       gana_hi=i18n.names("hi").GANA[n.gana])),
        ("f.yoni", f"{_e(names.YONI.get(yoni, yoni))} <small>{_tx(f'gender.{gender}', lang)}</small>"),
        ("f.nadi", f"{_e(names.NADI.get(nadi, nadi))} <small>{_tx(f'humour.{humour}', lang)}</small>"),
        ("f.varna", _e(varnas)),
        ("f.syl", _tx("f.syl_v", lang, syl=_e(i18n.akshar(" ".join(d for d, _ in n.syllables), lang)),
                      lat=_e(", ".join(l for _, l in n.syllables)))),
    ]
    body = "".join(f'<tr><th scope="row">{_tx(k, lang)}</th><td>{v}</td></tr>' for k, v in rows)
    return f'<div class="scroll"><table>{body}</table></div>'


def _pada_table(n: Nakshatra, lang: str) -> str:
    head = _tx("pada.head", lang)
    rows = []
    for p in range(1, 5):
        start = n.start_min + (p - 1) * PADA_MIN
        sign = n.pada_sign(p)
        dev, lat = n.syllables[p - 1]
        rows.append(
            f"<tr><td>{p}</td><td>{_e(_point(start, lang))} – "
            f"{_e(_point(start + PADA_MIN, lang, end=True))}</td>"
            f'<td><a href="{rashi_path(RASHIS[sign], lang)}">{_e(_sign_name(sign, lang))}</a></td>'
            f'<td><span class="syl" lang="{i18n.akshar_lang(lang)}">{_e(i18n.akshar(dev, lang))}</span> <small>{_e(lat)}</small></td></tr>')
    return (f"<h2>{_tx('pada.title', lang)}</h2><div class=\"scroll\"><table>{head}"
            f"{''.join(rows)}</table></div>" + _tx("pada.note", lang))


def _related(n: Nakshatra, lang: str) -> str:
    items = []
    for s in n.signs:
        r = RASHIS[s]
        items.append((rashifal_path(r, lang), _tx("rel.rashifal", lang, name=rashi_name(r, lang))))
    prev_n = NAKSHATRA_LIST[(n.index - 1) % 27]
    next_n = NAKSHATRA_LIST[(n.index + 1) % 27]
    items += [(nak_path(prev_n, lang), ("← " + _nak_label(prev_n, lang))),
              (nak_path(next_n, lang), (_nak_label(next_n, lang) + " →")),
              (milan_path(lang), _tx("more.milan", lang)),
              (_pre(lang) + "/panchang", _tx("more.panchang", lang))]
    return _links(items, _tx("rel.heading", lang))


@functools.lru_cache(maxsize=128)
def _nak_page(day: dt.date, slug: str, lang: str) -> tuple[str, str, str]:
    n = BY_SLUG[slug]
    names = i18n.names(lang)
    syl = i18n.akshar(" ".join(d for d, _ in n.syllables), lang)
    lat = ", ".join(l for _, l in n.syllables)
    deity = _own(n, "deity", lang)
    raw = {"name": _nak_label(n, lang), "name_en": n.name, "name_hi": n.name_hi, "syl": syl,
           "lat": lat, "span": span_text(n, lang), "lord": _planet(n.lord, lang),
           "deity": deity, "deity_short": deity.split(",")[0],
           "gana": names.GANA.get(n.gana, n.gana), "nadi": names.NADI.get(n.nadi, n.nadi),
           "yoni": names.YONI.get(n.yoni[0], n.yoni[0]), "brand": BRAND}
    title = _tx("nak.title", lang, **raw)
    description = _tx("nak.desc", lang, **raw)
    esc = {k: _e(v) for k, v in raw.items()}
    body = f"""
{_tx("nak.h1", lang, **esc)}
{_tx("nak.sub", lang, **esc)}
{_today_box(n, day, lang)}
{_facts(n, lang)}
<h2>{_tx("trait_head", lang)}</h2>
<p>{_e(i18n.pick(NAKSHATRA_TRAITS[n.slug], lang))}</p>
{_tx("nak.trait_note", lang)}
{_pada_table(n, lang)}
{kundali_cta(lang)}
{_related(n, lang)}
{_nak_list(n, lang)}"""
    return title, description, body


@functools.lru_cache(maxsize=8)
def _nak_index(day: dt.date, lang: str) -> tuple[str, str, str]:
    names = i18n.names(lang)
    rows = []
    for n in NAKSHATRA_LIST:
        signs = " / ".join(rashi_name(RASHIS[s], lang) for s in n.signs)
        gana = names.GANA.get(n.gana, n.gana)
        rows.append(
            f'<tr><td>{n.index + 1}</td><td><a href="{nak_path(n, lang)}">'
            f"{_e(_nak_label(n, lang))}</a></td><td>{_e(signs)}</td>"
            f"<td>{_e(_planet(n.lord, lang))}</td><td>{_e(gana)}</td>"
            f'<td lang="{i18n.akshar_lang(lang)}">'
            f'{_e(i18n.akshar(" ".join(d for d, _ in n.syllables), lang))}</td></tr>')
    title = _tx("ni.title", lang, brand=BRAND)
    description = _tx("ni.desc", lang)
    body = f"""
{_tx("ni.h1", lang)}
{_tx("ni.sub", lang)}
{_tx("ni.intro", lang)}
{_today_box(None, day, lang)}
<div class="scroll"><table>{_tx("ni.head", lang)}{''.join(rows)}</table></div>
{kundali_cta(lang)}
{_more(lang)}"""
    return title, description, body


def _crumb_nak(lang: str) -> tuple[str, str]:
    return _tx("crumb.naks", lang), nak_path(None, lang)


def _crumb_rashi(lang: str) -> tuple[str, str]:
    return _tx("crumb.rashis", lang), rashi_path(None, lang)


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
    if kind == "nakshatra":
        head = _tx("nf.nak", lang)
        lst, crumb = _nak_list(None, lang), _crumb_nak(lang)
    else:
        head = _tx("nf.rashi", lang)
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
    lord = DOMICILE[r.english]
    element = ELEMENT[r.english]
    varna = matching.VARNA_OF_RASHI[r.english]
    span = f"{r.index * 30}° – {r.index * 30 + 30}°"
    padas = sign_padas(r.index)
    naks = list(dict.fromkeys(n for n, _ in padas))
    nak_links = ", ".join(f'<a href="{nak_path(n, lang)}">{_e(_nak_label(n, lang))}</a>'
                          for n in naks)
    syl = i18n.akshar(" ".join(n.syllables[p - 1][0] for n, p in padas), lang)
    rows = [("r.number", _tx("r.number_v", lang, n=r.index + 1)),
            ("r.span", span),
            ("r.lord", _e(_planet(lord, lang))),
            ("r.element", _tx(f"element.{element}", lang)),
            ("r.quality", _tx(f"quality.{MODALITY[r.english]}", lang)),
            ("r.varna", i18n.names(lang).VARNA.get(varna, varna)),
            ("r.naks", nak_links),
            ("r.syl", _tx("r.syl_v", lang, syl=_e(syl)))]
    body = "".join(f'<tr><th scope="row">{_tx(k, lang)}</th><td>{v}</td></tr>' for k, v in rows)
    return f'<div class="scroll"><table>{body}</table></div>'


def _rashi_padas(r: Rashi, lang: str) -> str:
    head = _tx("rp.head", lang)
    rows = []
    for i, (n, p) in enumerate(sign_padas(r.index)):
        lo, hi_m = i * PADA_MIN, (i + 1) * PADA_MIN
        dev, lat = n.syllables[p - 1]
        rows.append(f'<tr><td><a href="{nak_path(n, lang)}">{_e(_nak_label(n, lang))}</a></td>'
                    f"<td>{p}</td><td>{_deg(lo)} – {_deg(hi_m)}</td>"
                    f'<td><span class="syl" lang="{i18n.akshar_lang(lang)}">{_e(i18n.akshar(dev, lang))}</span> <small>{_e(lat)}</small>'
                    "</td></tr>")
    return (f"<h2>{_tx('rp.title', lang)}</h2><div class=\"scroll\"><table>{head}"
            f"{''.join(rows)}</table></div>")


@functools.lru_cache(maxsize=64)
def _rashi_page(slug: str, lang: str) -> tuple[str, str, str]:
    r = RASHI_BY_SLUG[slug]
    lord = DOMICILE[r.english]
    padas = sign_padas(r.index)
    element = _tx(f"element.{ELEMENT[r.english]}", lang)
    quality = _tx(f"quality.{MODALITY[r.english]}", lang)
    raw = {"name": rashi_name(r, lang), "name_en": r.name, "name_hi": r.name_hi,
           "english": r.english, "lord": _planet(lord, lang), "element": element,
           "element_lower": element.lower(), "quality": quality, "quality_lower": quality.lower(),
           "syl": i18n.akshar(" ".join(n.syllables[p - 1][0] for n, p in padas), lang),
           "lat": ", ".join(n.syllables[p - 1][1] for n, p in padas), "brand": BRAND}
    title = _tx("rs.title", lang, **raw)
    description = _tx("rs.desc", lang, **raw)
    esc = {k: _e(v) for k, v in raw.items()}
    today = _tx("rs.today", lang, **raw)
    body = f"""
{_tx("rs.h1", lang, **esc)}
{_tx("rs.sub", lang, **esc)}
<div class="box"><p><a href="{rashifal_path(r, lang)}"><strong>{_e(today)}</strong></a></p></div>
{_rashi_facts(r, lang)}
<h2>{_tx("trait_head", lang)}</h2>
<p>{_e(i18n.pick(RASHI_TRAITS[r.slug], lang))}</p>
{_tx("rs.note", lang)}
{_rashi_padas(r, lang)}
{kundali_cta(lang)}
{_rashi_list(r, lang)}
{_more(lang)}"""
    return title, description, body


@functools.lru_cache(maxsize=4)
def _rashi_index(lang: str) -> tuple[str, str, str]:
    rows = []
    for r in RASHIS:
        padas = sign_padas(r.index)
        naks = list(dict.fromkeys(n for n, _ in padas))
        name = _tx("ri.name", lang, name=_e(rashi_name(r, lang)), name_en=_e(r.name),
                   english=_e(r.english))
        rows.append(
            f'<tr><td><a href="{rashi_path(r, lang)}">{name}</a></td>'
            f"<td>{_e(_planet(DOMICILE[r.english], lang))}</td>"
            f"<td>{_tx('element.' + ELEMENT[r.english], lang)}</td>"
            f"<td>{_e(', '.join(_nak_label(n, lang) for n in naks))}</td>"
            f'<td lang="{i18n.akshar_lang(lang)}">'
            f'{_e(i18n.akshar(" ".join(n.syllables[p - 1][0] for n, p in padas), lang))}</td></tr>')
    title = _tx("ri.title", lang, brand=BRAND)
    description = _tx("ri.desc", lang)
    body = f"""
{_tx("ri.h1", lang)}
{_tx("ri.sub", lang)}
{_tx("ri.intro", lang)}
<div class="scroll"><table>{_tx("ri.head", lang)}{''.join(rows)}</table></div>
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
                 crumbs=[_crumb_rashi(lang), (rashi_name(r, lang), rashi_path(r, lang))],
                 body=body)


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
