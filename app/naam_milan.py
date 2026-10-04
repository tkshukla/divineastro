"""Naam se Kundali Milan — /naam-se-kundali-milan and /hi/… (DIVASTRO-115).

The traditional shortcut when birth details are unknown: the first syllable
of each name (namakshar) is looked up in the 108-pada table, which gives a
nakshatra pada and so a Moon sign, and the 36-point Ashtakoot is computed from
those two "Moons" by the same engine the birth-chart Kundali Milan uses
(`astro.matching.ashtakoot`), so the two tools can never score the same pair
of nakshatras differently. The syllable rules and their limits are in
astro/namakshar.py and are explained on the page.

Privacy — names are personal data, so:
  * they are never stored, logged or put in a share link. The WhatsApp button
    shares the bare page URL; the form is a plain GET (the page is
    server-rendered and works without JavaScript), so the result response
    is `no-store`, `noindex`, sets `Referrer-Policy: no-referrer` (also as the
    first <meta>, so even the stylesheet request does not carry the URL), and
    loads no third-party script (no AdSense on a result). A one-line inline
    script then drops the query from the address bar, so a copied or shared
    address bar URL carries no names either. The Caddy access log filters
    the `boy`/`girl` parameters out (see Caddyfile).
  * the engine is handed a synthetic chart bundle with an empty name.
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

from . import i18n
from .astro import matching
from .astro.namakshar import (ABHIJIT, Match, all_padas, from_pada_id, lookup,
                              match_for_pada, moon_bundle, pada_id, sign_padas)
# DIVASTRO-123: the page's text is naam_milan_text.TEXT; nakshatra/rashi names
# are nakshatra_pages' (names_i18n for every language).
from . import seo_text
from .naam_milan_text import ENGINE, TEXT
from .nakshatra_pages import (RASHIS, kundali_cta, milan_path, nak_path, rashi_path, shell)
from .nakshatra_pages import _nak_label, _rashi_pill, _sign_name
from .seo_pages import BRAND, _e

router = APIRouter()

MAX_NAME = 60
PARAMS = ("boy", "girl", "boy_pada", "girl_pada")   # the Caddyfile log filter lists these
# The languages matching.ashtakoot writes its koota labels and notes in; any
# other language labels the kootas from names_<code>.KOOTA (notes stay English).
ENGINE_LANGS = ("en", "hi")

_STRIP_QUERY = ("<script>try{history.replaceState(null,'',location.pathname)}catch(e){}"
                "</script>")


def _tx(key: str, lang: str, **values) -> str:
    """This page's text for `key` in `lang` (naam_milan_text.TEXT), formatted."""
    return i18n.fmt(key, lang, TEXT, **values)


def _sign_label(index: int, lang: str) -> str:
    return _sign_name(index, lang)


def resolve(name: str, pada_value: str) -> Match | None:
    """A chosen pada wins (the reader corrected the syllable); otherwise the name."""
    chosen = from_pada_id(pada_value)
    if chosen:
        return match_for_pada(*chosen)
    return lookup(name)


def compute(groom: Match, bride: Match, lang: str = "en") -> dict:
    """Ashtakoot for the two name-derived Moons — the matching engine, unchanged."""
    return matching.ashtakoot(moon_bundle(groom.nakshatra, groom.pada),
                              moon_bundle(bride.nakshatra, bride.pada), lang=lang)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def _options(selected: Match | None, lang: str) -> str:
    """Every one of the 108 syllables, the likely alternatives first."""
    def opt(n, p, sel=False):
        dev, lat = n.syllables[p - 1]
        sign = _sign_label(n.pada_sign(p), lang)
        text = f"{i18n.akshar(dev, lang)} ({lat}) — {_nak_label(n, lang)} {p} · {sign}"
        return (f'<option value="{pada_id(n, p)}"' + (" selected" if sel else "")
                + f">{_e(text)}</option>")

    out = [f'<option value="">{_e(_tx("auto", lang))}</option>']
    if selected is not None and selected.alternatives:
        head = _tx("alt_head", lang)
        out.append(f'<optgroup label="{_e(head)}">'
                   + "".join(opt(n, p) for n, p in selected.alternatives) + "</optgroup>")
    head = _tx("all_head", lang)
    chosen = selected.via == "chosen" if selected else False
    out.append(f'<optgroup label="{_e(head)}">' + "".join(
        opt(n, p, chosen and n == selected.nakshatra and p == selected.pada)
        for n, p in all_padas()) + "</optgroup>")
    return "".join(out)


def _form(lang: str, boy: str = "", girl: str = "", gm: Match | None = None,
          bm: Match | None = None, show_pick: bool = False) -> str:
    lb, lg = _tx("boy_label", lang), _tx("girl_label", lang)
    ph_b, ph_g = _tx("boy_ph", lang), _tx("girl_ph", lang)
    pick, btn = _tx("pick", lang), _tx("button", lang)
    picks = ""
    if show_pick:
        picks = (f'<label>{_e(pick)} — {_e(lb)}<select name="boy_pada">{_options(gm, lang)}'
                 f'</select></label><label>{_e(pick)} — {_e(lg)}<select name="girl_pada">'
                 f"{_options(bm, lang)}</select></label>")
    return (f'<form class="milan" method="get" action="{milan_path(lang)}" autocomplete="off">'
            f'<label>{_e(lb)}<input name="boy" maxlength="{MAX_NAME}" value="{_e(boy)}" '
            f'placeholder="{_e(ph_b)}"/></label>'
            f'<label>{_e(lg)}<input name="girl" maxlength="{MAX_NAME}" value="{_e(girl)}" '
            f'placeholder="{_e(ph_g)}"/></label>{picks}'
            f'<button type="submit">{_e(btn)}</button></form>')


def _via_note(m: Match, lang: str) -> str:
    if f"via.{m.via}" in TEXT["en"]:
        return f"<small>{_e(_tx(f'via.{m.via}', lang))}</small>"
    return ""


def _person_row(label: str, raw: str, m: Match | None, lang: str) -> str:
    if m is None:
        msg = _tx("unreadable", lang)
        return f'<tr><th scope="row">{_e(label)}</th><td colspan="3" class="bad">{_e(msg)}</td></tr>'
    n, p = m.nakshatra, m.pada
    sl = i18n.akshar_lang(lang)
    used = f'<span class="syl" lang="{sl}">{_e(i18n.akshar(m.akshar, lang))}</span>'
    if m.syllable != m.akshar:
        used += f' → <span class="syl" lang="{sl}">{_e(i18n.akshar(m.syllable, lang))}</span>'
    return (f'<tr><th scope="row">{_e(label)}</th><td>{used}{_via_note(m, lang)}</td>'
            f'<td><a href="{nak_path(n, lang)}">{_e(_nak_label(n, lang))}</a> '
            f'<small>{_tx("pada", lang)} {p}</small></td>'
            f'<td><a href="{rashi_path(RASHIS[m.sign], lang)}">{_e(_sign_label(m.sign, lang))}'
            "</a></td></tr>")


def _result(boy: str, girl: str, gm: Match | None, bm: Match | None, lang: str) -> str:
    head = _tx("res.head", lang)
    people = (_person_row(_tx("boy", lang), boy, gm, lang)
              + _person_row(_tx("girl", lang), girl, bm, lang))
    out = [f"<h2>{_tx('result', lang)}</h2>",
           f'<div class="scroll"><table>{head}{people}</table></div>']
    if gm and bm:
        res = compute(gm, bm, lang)
        names = i18n.names(lang)
        rows = "".join(
            f'<tr><td><strong>{_e(_koota_label(k, lang, names))}</strong></td>'
            f'<td>{k["score"]:g} / {k["max"]:g}</td>'
            f'<td>{_e(k["note"])}</td></tr>' for k in res["kootas"])
        th = _tx("res.th", lang)
        total = f"{res['total']:g} / {res['maximum']:g}"
        verdict, band_note, conv_note = _verdict(res, lang)
        out.append(f'<div class="box"><p class="total"><strong>{_tx("total", lang)}: '
                   f'{_e(total)}</strong> — {_e(verdict)}</p><p>{_e(band_note)}</p>'
                   f"</div>")
        out.append(f'<div class="scroll"><table>{th}{rows}</table></div>')
        out.append(f'<p class="note">{_e(conv_note)}</p>')
        out.append(f'<div class="box"><p>{_tx("mangal", lang)}</p></div>')
    out.append(_caveat(lang))
    out.append(f'<a class="cta" href="{_e(i18n.app_link(lang, "open=milan"))}">'
               + _e(_tx("res.cta", lang)) + "</a>")
    return "".join(out)


def _verdict(res: dict, lang: str) -> tuple[str, str, str]:
    """The engine's verdict, band note and convention note (en, hi); for another
    language seo_text's km.band<i> and naam_milan_text.ENGINE where it has them."""
    own = ENGINE.get(lang)
    if lang in ENGINE_LANGS or not own:
        return res["verdict"], res["band_note"], res["convention_note"]
    i = next((i for i, b in enumerate(matching.SCORE_BANDS) if res["total"] < b[0]),
             len(matching.SCORE_BANDS) - 1)
    return (i18n.t(f"km.band{i}", lang, seo_text.TEXT), own.get(f"band_note{i}", res["band_note"]),
            own.get("convention_note", res["convention_note"]))


def _koota_label(k: dict, lang: str, names) -> str:
    """The engine's label in its own languages, names_<code>.KOOTA elsewhere."""
    if lang in ENGINE_LANGS:
        return k["label"]
    return names.KOOTA.get(k.get("key"), k["label"])


def _caveat(lang: str) -> str:
    return _tx("caveat", lang)


def _rashi_syllables(lang: str) -> str:
    head = _tx("syl.head", lang)
    rows = "".join(
        f'<tr><td><a href="{rashi_path(r, lang)}">{_e(_rashi_pill(r, lang))}'
        f'</a></td><td lang="{i18n.akshar_lang(lang)}">'
        f'{_e(i18n.akshar(" ".join(n.syllables[p - 1][0] for n, p in sign_padas(r.index)), lang))}'
        "</td></tr>" for r in RASHIS)
    return f'<div class="scroll"><table>{head}{rows}</table></div>'


def _explainer(lang: str) -> str:
    abhijit = i18n.akshar(" ".join(d for d, _ in ABHIJIT), lang)
    return _tx("explainer", lang, abhijit=abhijit, syllables=_rashi_syllables(lang),
               href=nak_path(None, lang))


def render(lang: str, boy: str | None, girl: str | None, boy_pada: str | None,
           girl_pada: str | None) -> HTMLResponse:
    boy = (boy or "").strip()[:MAX_NAME]
    girl = (girl or "").strip()[:MAX_NAME]
    asked = any(x for x in (boy, girl, boy_pada, girl_pada))
    title = _tx("title", lang, brand=BRAND)
    description = _tx("desc", lang)
    gm = bm = None
    result = ""
    if asked:
        gm, bm = resolve(boy, boy_pada or ""), resolve(girl, girl_pada or "")
        result = _result(boy, girl, gm, bm, lang)
    body = f"""
{_tx("h1", lang)}
{_tx("sub", lang)}
{_tx("intro", lang)}
{_form(lang, boy, girl, gm, bm, show_pick=asked)}
{result}
{'' if asked else _caveat(lang)}
{_explainer(lang)}
<a class="cta" href="{_e(i18n.app_link(lang, 'open=milan'))}">{_e(_tx("open_milan", lang))}</a>
{kundali_cta(lang)}"""
    crumbs = [(_tx("crumb", lang), milan_path(lang))]
    kw = {}
    if asked:
        kw = dict(cache=False, ads=False,
                  head_first='<meta name="referrer" content="no-referrer"/>\n'
                             '<meta name="robots" content="noindex"/>\n' + _STRIP_QUERY + "\n",
                  headers={"Referrer-Policy": "no-referrer", "X-Robots-Tag": "noindex"})
    return shell(lang=lang, en_path=milan_path("en"), hi_path=milan_path("hi"), title=title,
                 description=description, crumbs=crumbs, body=body, **kw)


# No max_length on the parameters: a 422 would echo the name back in its JSON
# body. render() truncates instead.
@router.get("/naam-se-kundali-milan", response_class=HTMLResponse)
def naam_milan(boy: str | None = Query(None),
               girl: str | None = Query(None),
               boy_pada: str | None = Query(None),
               girl_pada: str | None = Query(None)) -> HTMLResponse:
    return render("en", boy, girl, boy_pada, girl_pada)


@router.get("/hi/naam-se-kundali-milan", response_class=HTMLResponse)
def naam_milan_hi(boy: str | None = Query(None),
                  girl: str | None = Query(None),
                  boy_pada: str | None = Query(None),
                  girl_pada: str | None = Query(None)) -> HTMLResponse:
    return render("hi", boy, girl, boy_pada, girl_pada)


# DIVASTRO-121: /kn/naam-se-kundali-milan etc. — the TRANSLATED set is
# nakshatra_pages.TRANSLATED (this page shares its shell).
@router.get("/{lang:xlang}/naam-se-kundali-milan", response_class=HTMLResponse)
def naam_milan_lang(lang: str,
                    boy: str | None = Query(None),
                    girl: str | None = Query(None),
                    boy_pada: str | None = Query(None),
                    girl_pada: str | None = Query(None)) -> HTMLResponse:
    return render(lang, boy, girl, boy_pada, girl_pada)
