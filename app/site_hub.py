"""/sitemap: a plain HTML map of the whole site, in every translated language
(DIVASTRO-133).

Crawlers find pages through links, and until now the only way into the ~110
city pages and the muhurat / vrat / nakshatra sections from outside the app was
the app itself. This page links to every section index and, in one block, to the
Panchang page of every city (each of those links on to Rahu Kaal and Choghadiya
for the same city). Every server-rendered page links here from its footer.

    /sitemap  /hi/sitemap  /kn/sitemap ...   (same shape as the other pages)
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import (i18n, muhurat_pages, nakshatra_pages, rashifal_pages, recurring_pages, seo_cities,
               seo_pages, vrat_pages)
from .hub_text import label
from .seo_pages import EN, HI, _e, _path, _render

router = APIRouter()
i18n.LOCALIZABLE_ROOTS.add("sitemap")


def page_path(lang: str = EN) -> str:
    return i18n.prefix(lang) + "/sitemap"


def sitemap_paths() -> list[str]:
    return [page_path(lang) for lang in i18n.ordered(seo_pages.TRANSLATED)]


def _links(items: list[tuple[str, str]]) -> str:
    return '<ul class="links">' + "".join(
        f'<li><a href="{_e(href)}">{text}</a></li>' for text, href in items) + "</ul>"


def _section(title: str, items: list[tuple[str, str]]) -> str:
    return f"<h2>{title}</h2>\n{_links(items)}\n"


def _katha(lang: str) -> str:
    from .katha import page_path as katha_path
    return katha_path(None, lang if lang in (HI, EN) else EN)


def _body(lang: str) -> str:
    # The English paths are written bare; _render localizes links itself for the
    # regional languages (i18n.localize_links), but we build them with the real
    # prefix here so the page is correct before that runs.
    names = i18n.names(lang)
    out = [f"<h1>{label('sitemap', lang)}</h1>", f"<p>{label('intro', lang)}</p>"]

    out.append(_section(label("panchang", lang), [
        (label("panchang", lang), _path("panchang", seo_cities.DEFAULT, lang)),
        (label("rahu", lang), _path("rahu-kaal", seo_cities.DEFAULT, lang)),
        (label("choghadiya", lang), _path("choghadiya", seo_cities.DEFAULT, lang)),
    ]))

    cities = []
    for state, group in seo_cities.by_state():
        cities.append(f"<dt>{_e(seo_cities.state_name(state, lang))}</dt><dd>" + _links([
            (_e(seo_cities.city_name(c, lang)), _path("panchang", c, lang)) for c in group])
            + "</dd>")
    out.append(f'<h2>{label("cities", lang)}</h2>\n<dl class="cities">{"".join(cities)}</dl>\n')

    signs = [(_e(names.RASHI.get(r.english, r.english)), rashifal_pages.path(r, lang))
             for r in rashifal_pages.RASHIS]
    out.append(_section(label("rashifal", lang),
                        [(label("rashifal", lang), rashifal_pages.path(None, lang))] + signs))

    vrat = [(label("vrat", lang), vrat_pages.hub_path(lang))]
    for y in vrat_pages.YEARS:
        vrat.append((f"{label('vrat', lang)} {y}", vrat_pages.year_path(y, lang)))
        vrat.append((f"{label('ekadashi', lang)} {y}", vrat_pages.ekadashi_path(y, lang)))
    out.append(_section(label("vrat", lang), vrat))

    muhurat = [(f"{_e(muhurat_pages._tx(f'kind.{k}', lang))} {y}",
                muhurat_pages.page_path(k, y, lang))
               for y in muhurat_pages.YEARS for k in muhurat_pages.KINDS]
    out.append(_section(label("muhurat", lang), muhurat))

    out.append(_section(*recurring_pages.hub_items(lang)))      # DIVASTRO-141

    out.append(_section(f"{label('nakshatra', lang)} / {label('rashi', lang)}", [
        (label("nakshatra", lang), nakshatra_pages.nak_path(None, lang)),
        (label("rashi", lang), nakshatra_pages.rashi_path(None, lang)),
        (label("naam", lang), nakshatra_pages.milan_path(lang)),
    ]))

    out.append(_section(label("katha", lang), [(label("katha", lang), _katha(lang))]))

    out.append(_section(label("tools", lang), [
        (label("kundali", lang), i18n.prefix(lang) + "/free-kundali"),
        (label("milan", lang), i18n.prefix(lang) + "/kundali-milan"),
        (label("rahu", lang), _path("rahu-kaal", seo_cities.DEFAULT, lang)),
        (label("choghadiya", lang), _path("choghadiya", seo_cities.DEFAULT, lang)),
    ]))
    return "\n".join(out)


def _page(lang: str) -> HTMLResponse:
    name = label("sitemap", lang)
    title = " · ".join(label(k, lang) for k in ("sitemap", "panchang", "rashifal", "vrat", "muhurat"))
    return _render(
        title=f"{title} | Divine Astro".replace("&amp;", "&"), description=label("intro", lang).replace("&amp;", "&"),
        path=page_path(lang), crumbs=[(name, page_path(lang))], body=_body(lang),
        lang=lang, alt="twin")


@router.get("/sitemap", response_class=HTMLResponse)
def hub() -> HTMLResponse:
    return _page(EN)


@router.get("/hi/sitemap", response_class=HTMLResponse)
def hub_hi() -> HTMLResponse:
    return _page(HI)


@router.get("/{lang:xlang}/sitemap", response_class=HTMLResponse)
def hub_lang(lang: str) -> HTMLResponse:
    return _page(lang)
