"""/pricing: every product and its price on one public page (DIVASTRO-149).

    /pricing      /hi/pricing      (and /<code>/pricing for the other registry languages)

Until this page existed the app showed no rupee amount to anyone who was not
signed in: the store opened only after sign-in. This page lists the whole billing
catalogue - question packs (with the price per question), the single-topic
reports, the Life Book and the hand-written kundali - so a visitor, a search engine
and an assistant can all see what Divine Astro costs.

**Nothing is typed here that the catalogue already knows.** Every price, title,
description, credit count and the free allowance is read from app/billing.py at
render time (billing.PRODUCTS, billing.FREE_QUESTIONS, billing.ASTROLOGER,
billing.TURNAROUND_DAYS), so the page cannot drift from what the store charges.
What a product delivers is the catalogue's own blurb. The payment sentence follows
the gateway that is really active (gateways.active()).

The words around those facts are pricing_text.TEXT (English and Hindi). Another
registry language renders the English text under its own prefix, noindex, with the
"translation coming soon" notice and no hreflang or sitemap entry (TRANSLATED).

The shell is seo_pages._render, like /learn and /purnima-2026. The small script
/static/pricing.js reports the page view and taps on the call to action
(analytics events pricing_view / plans_click).
"""

from __future__ import annotations

import datetime as dt

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import billing, gateways, i18n, sample_reports, seo_pages
from .pricing_text import TEXT
from .seo_pages import BRAND, EN, HI, SITE_URL, _e, _render

router = APIRouter()
i18n.LOCALIZABLE_ROOTS.add("pricing")

# Only the languages pricing_text is really written in.
TRANSLATED = i18n.BASE_TRANSLATED

# The catalogue's `kind` -> the section it is listed under, in page order. A kind
# missing here still gets listed (under "more"): no product may go unlisted.
SECTIONS = (
    ("single_question", "reports"),
    ("questions", "packs"),
    ("kundali_book", "book"),
    ("kundali", "kundali"),
)


def page_path(lang: str = EN) -> str:
    return i18n.prefix(lang) + "/pricing"


def sitemap_paths() -> list[str]:
    """For sitemap.xml: the canonical page in each translated language."""
    return [page_path(lang) for lang in i18n.ordered(TRANSLATED)]


def is_public_path(path: str) -> bool:
    """For the visit beacon (analytics.is_public_page): /pricing in any language."""
    return i18n.strip_prefix(path)[1] == "/pricing"


def _tx(key: str, lang: str, **values) -> str:
    return i18n.fmt(key, lang, TEXT, **values)


def _money(rupees: float) -> str:
    """₹111, ₹1,100 (a whole number of rupees, as the store shows it)."""
    return f"₹{int(rupees):,}"


def _each(per_question: float) -> str:
    return f"{per_question:.2f}"


def _title(p: dict, lang: str) -> str:
    return (p.get("title_hi") if lang == HI else None) or p["title"]


def _blurb(p: dict, lang: str) -> str:
    return (p.get("blurb_hi") if lang == HI else None) or p["blurb"]


def _sections(products: list[dict]) -> list[tuple[str, list[dict]]]:
    out = []
    seen: set[str] = set()
    for kind, key in SECTIONS:
        items = [p for p in products if p["kind"] == kind]
        seen.update(p["sku"] for p in items)
        if items:
            out.append((key, items))
    rest = [p for p in products if p["sku"] not in seen]
    if rest:
        out.append(("more", rest))
    return out


def _facts(products: list[dict]) -> dict:
    """The catalogue figures the sentences quote."""
    packs = sorted((p for p in products if p["kind"] == "questions"), key=lambda p: p["credits"])
    reports = [p for p in products if p["kind"] == "single_question"]
    book = next((p for p in products if p["kind"] == "kundali_book"), None)
    return {
        "free": billing.FREE_QUESTIONS,
        "pack_from": min((p["rupees"] for p in packs), default=0),
        "report_from": min((p["rupees"] for p in reports), default=0),
        "book": book["rupees"] if book else 0,
        "astrologer": billing.ASTROLOGER,
        "days": billing.TURNAROUND_DAYS,
        "packs": packs,
    }


def _pack_sentence(packs: list[dict], lang: str) -> str:
    return "; ".join(
        _tx("pack_item", lang, count=p["credits"], price=f"{p['rupees']:,}",
            each=_each(p["per_question"])) for p in packs)


def _payment_text(lang: str) -> str:
    gw = gateways.active()
    if gw.key == "upi_manual":
        return _tx("pay.upi", lang)
    if gw.key == "test":
        return _tx("pay.test", lang)
    return _tx("pay.gateway", lang, gateway=gw.label)


def _offer_live(p: dict) -> bool:
    """The Diwali offer applies to this product right now, as the catalogue says. The struck
    price is the catalogue's own list_amount_paise (never typed or computed here)."""
    return bool(p["offer"]["active"] and p.get("list_amount_paise")
                and p["list_amount_paise"] > p["amount_paise"])


def _offer_date(offer: dict, lang: str, *, short: bool) -> str:
    """The real end date of the offer (offer.ends_at, India time), in the page language."""
    ends = dt.datetime.fromisoformat(offer["ends_at"]).astimezone(billing.IST)
    return i18n.format_date(ends.date(), lang, short=short)


def _offer_of(products: list[dict]) -> dict | None:
    """The live offer ({active, name, ends_at}) or None. Nothing of the offer is rendered
    unless this is not None, so after the end the page is the plain regular-price page."""
    return next((p["offer"] for p in products if p["offer"]["active"] and p["offer"]["ends_at"]), None)


def _banner(offer: dict | None, lang: str) -> str:
    if not offer:
        return ""
    return (f'<p class="pr-offer" data-offer-banner><span class="pr-pill" data-offer-pill>'
            f'{_e(_tx("offer.pill", lang, date=_offer_date(offer, lang, short=True)))}</span> '
            f'<span>{_e(_tx("offer.banner", lang, date=_offer_date(offer, lang, short=False)))}</span></p>')


def _explanation(offer: dict | None, lang: str) -> str:
    if not offer:
        return ""
    date = _offer_date(offer, lang, short=False)
    return (f'<h2 id="diwali-offer">{_e(_tx("offer.h2", lang))}</h2>'
            f'<div class="box" data-offer-about><p>{_e(_tx("offer.p1", lang, date=date))}</p>'
            f'<p>{_e(_tx("offer.p2", lang))}</p></div>')


def _cache_control(offer: dict | None, now: dt.datetime, default: str) -> str:
    """While the offer is live the page may be cached for at most 300 s AND never past the end
    instant, so a cached copy cannot show "offer active" after ends_at (private: browsers only;
    Caddy does no caching). Once it is over, the shell's own header (up to 30 min) is fine:
    there is nothing time-boxed left on the page."""
    if not offer:
        return default
    left = (dt.datetime.fromisoformat(offer["ends_at"]) - now).total_seconds()
    return f"private, max-age={max(1, min(300, int(left)))}"


def _table(items: list[dict], lang: str) -> str:
    """Name and what it delivers on the left, the price on the right: two columns
    stay readable at 360px, where a third (the description) would squeeze the price."""
    rows = []
    for p in items:
        extra = ""
        if p["kind"] == "questions" and p.get("per_question"):
            extra = f"<small>{_e(_tx('per_q', lang, value=_each(p['per_question'])))}</small>"
        flag = ""
        if p["kind"] == "questions" and p.get("highlight"):
            flag = f' <span class="pr-flag">{_e(_tx("popular", lang))}</span>'
        sample = ""
        if p["sku"] in sample_reports.SKUS:       # DIVASTRO-151: only products with an automatic sample
            href = f"/samples/{p['sku']}.pdf" + ("?lang=hi" if lang == HI else "")
            sample = (f'<span class="pr-sample"><a href="{_e(href)}" target="_blank" rel="noopener" '
                      f'data-sample="{_e(p["sku"])}">{_e(_tx("sample.link", lang))}</a> '
                      f'<small>{_e(_tx("sample.note", lang))}</small></span>')
        was = ""
        if _offer_live(p):                         # DIVASTRO-152: only while the offer is live
            if p["kind"] == "questions" and p.get("list_per_question"):
                extra = (f"<small><s class=\"was\">₹{_e(_each(p['list_per_question']))}</s> "
                         f"{_e(_tx('per_q', lang, value=_each(p['per_question'])))}</small>")
            pct = round((1 - p["amount_paise"] / p["list_amount_paise"]) * 100)
            was = (f'<s class="was"><span class="sr-only">{_e(_tx("offer.was", lang))} </span>'
                   f'{_e(_money(p["list_amount_paise"] / 100))}</s>'
                   f'<span class="sr-only">, {_e(_tx("offer.now", lang))} </span>')
            extra += f'<span class="pr-save">{_e(_tx("offer.save", lang, n=pct))}</span>'
        rows.append(
            f'<tr id="{_e(p["sku"])}" data-sku="{_e(p["sku"])}">'
            f'<td class="pr-name">{_e(_title(p, lang))}{flag}'
            f'<span class="pr-what">{_e(_blurb(p, lang))}</span>{sample}</td>'
            f'<td class="pr-price">{was}<b>{_e(_money(p["rupees"]))}</b>{extra}</td></tr>')
    head = f"<tr><th>{_e(_tx('th.product', lang))}</th><th>{_e(_tx('th.price', lang))}</th></tr>"
    return f'<div class="scroll"><table class="pr-table">{head}{"".join(rows)}</table></div>'


def _product_ld(p: dict, lang: str, canonical: str) -> dict:
    offer = {
        "@type": "Offer",
        "price": str(p["rupees"]),
        "priceCurrency": "INR",
        "availability": "https://schema.org/InStock",
        "url": f"{canonical}#{p['sku']}",
        "seller": {"@type": "Organization", "name": BRAND},
    }
    # Only while the offer is live, and only the real end date: after it the
    # price above is the list price and carries no expiry.
    if p["offer"]["active"] and p["offer"]["ends_at"]:
        offer["priceValidUntil"] = p["offer"]["ends_at"]
    return {
        "@type": "Product",
        "@id": f"{canonical}#{p['sku']}",
        "name": _title(p, lang),
        "description": _blurb(p, lang),
        "sku": p["sku"],
        "brand": {"@type": "Brand", "name": BRAND},
        "offers": offer,
    }


_CSS = """<style>
.seo .pr-table td.pr-name { font-weight: 600; }
.seo .pr-table .pr-what { display: block; margin-top: 3px; color: var(--ink-dim); font-weight: 400;
                          font-size: 14px; line-height: 1.55; }
.seo .pr-table td.pr-price { white-space: nowrap; text-align: right; width: 1%; }
.seo .pr-table th:last-child { text-align: right; }
.seo .pr-table td.pr-price b { color: var(--gold-soft); font-size: 17px; }
.seo .pr-table .pr-sample { display: block; margin-top: 5px; font-weight: 400; font-size: 14px; }
.seo .pr-table .pr-sample small { color: var(--ink-dim); font-size: 13px; }
.seo .pr-table td.pr-price s.was { display: block; color: var(--ink-faint); font-size: 14px;
                                    font-weight: 400; text-decoration-thickness: 1px; }
.seo .pr-table td.pr-price small { display: block; }
.seo .pr-table td.pr-price small s.was { display: inline; font-size: inherit; }
.seo .pr-save { display: block; width: fit-content; margin: 4px 0 0 auto; padding: 0 8px; border-radius: 999px;
                background: rgba(var(--gold-rgb), 0.16); color: var(--gold-soft);
                font-size: 12px; font-weight: 600; line-height: 1.6; }
.seo .pr-offer { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; margin: 14px 0 16px;
                 padding: 9px 12px; border: 1px solid rgba(var(--gold-rgb), 0.35); border-radius: 12px;
                 background: rgba(var(--gold-rgb), 0.07); color: var(--ink-dim); font-size: 15px; line-height: 1.5; }
.seo .pr-pill { display: inline-block; padding: 1px 10px; border-radius: 999px; white-space: nowrap;
                border: 1px solid var(--gold); color: var(--gold-soft); font-size: 12.5px; font-weight: 600; }
.seo .sr-only { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; border: 0;
                overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; }
.seo .pr-flag { display: inline-block; margin-left: 6px; padding: 1px 8px; border-radius: 999px;
                border: 1px solid var(--gold); color: var(--gold); font-size: 11.5px;
                font-weight: 500; white-space: nowrap; }
</style>"""


def render(lang: str = EN) -> HTMLResponse:
    cl = lang if lang in TRANSLATED else EN
    now = billing._now()                      # one instant for the page and its Cache-Control
    products = billing.catalogue(now=now)
    offer = _offer_of(products)
    f = _facts(products)
    canonical = SITE_URL + page_path(lang)
    values = {"brand": BRAND, "free": f["free"], "pack_from": f["pack_from"],
              "report_from": f["report_from"], "book": f["book"]}

    title = _tx("title", cl, **values)
    desc = _tx("desc", cl, **values)
    h1 = _tx("h1", cl)

    blocks = [f"<h1>{_e(h1)}</h1>", _CSS, _banner(offer, cl),
              f"<p>{_e(_tx('lead', cl, **values))}</p>", _explanation(offer, cl)]
    blocks.append(f"<h2>{_e(_tx('free.h2', cl))}</h2>"
                  f'<div class="box"><p>{_e(_tx("free.p", cl, **values))}</p></div>')

    for key, items in _sections(products):
        h2_id = ' id="handwritten"' if key == "kundali" else ""
        blocks.append(f"<h2{h2_id}>{_e(_tx(key + '.h2', cl))}</h2>" if key != "more" else "")
        if key == "kundali":
            blocks.append("<p>" + _e(
                _tx("kundali.p", cl, astrologer=f["astrologer"], days=f["days"]) if f["astrologer"]
                else _tx("kundali.p0", cl)) + "</p>")
            blocks.append(f'<p class="hw-texts">{_e(_tx("kundali.texts", cl))}</p>')
        elif _has(key + ".p"):
            blocks.append(f"<p>{_e(_tx(key + '.p', cl))}</p>")
        blocks.append(_table(items, cl))

    pay = _payment_text(cl)
    blocks.append(f"<h2>{_e(_tx('pay.h2', cl))}</h2><p>{_e(pay)}</p>"
                  f"<p>{_e(_tx('pay.orders', cl))}</p>")
    blocks.append(f"<h2>{_e(_tx('refund.h2', cl))}</h2><p>" + _tx(
        "refund.p", cl,
        refund=f'<a href="/refund">{_tx("refund.link", cl)}</a>',
        terms=f'<a href="/terms">{_tx("terms.link", cl)}</a>') + "</p>")

    faq_items = (
        (_tx("faq.free_q", cl), _tx("faq.free_a", cl, **values)),
        (_tx("faq.cost_q", cl), _tx("faq.cost_a", cl, packs=_pack_sentence(f["packs"], cl))),
        (_tx("faq.pay_q", cl), pay),
        (_tx("faq.refund_q", cl), _tx("faq.refund_a", cl)),
    )
    faq_html, faq_ld = seo_pages._faq(faq_items)
    blocks.append(f"<h2>{_e(_tx('faq.h2', cl))}</h2>{faq_html}")

    cta = seo_pages._app_link("kundali", lang)
    blocks.append(f'<a class="cta big" id="pricing-cta" data-plans="cta" href="{_e(cta)}">'
                  f"{_e(_tx('cta', cl))}</a>"
                  f'<p style="text-align:center">{_e(_tx("cta.sub", cl))}</p>')

    pre = i18n.prefix(lang)
    related = [(f"{pre}/free-kundali", "related.kundali"), (f"{pre}/kundali-milan", "related.milan"),
               (f"{pre}/panchang", "related.panchang"), (f"{pre}/sitemap", "related.sitemap")]
    lis = "".join(f'<li><a href="{_e(h)}">{_e(_tx(k, cl))}</a></li>' for h, k in related)
    blocks.append(f"<h2>{_e(_tx('related.h2', cl))}</h2><ul class=\"links\">{lis}</ul>")
    blocks.append('<script src="/static/pricing.js" defer></script>')

    product_ld = [_product_ld(p, cl, canonical) for p in products]
    resp = _render(title=title, description=desc, path=page_path(lang),
                   crumbs=[(_tx("crumb", cl), page_path(lang))],
                   body="\n".join(b for b in blocks if b), lang=lang, alt="twin",
                   extra_ld=(*product_ld, faq_ld), translated=TRANSLATED)
    resp.headers["Cache-Control"] = _cache_control(offer, now, resp.headers["Cache-Control"])
    return resp


def _has(key: str) -> bool:
    return key in TEXT["en"]


@router.get("/pricing", response_class=HTMLResponse)
def pricing() -> HTMLResponse:
    return render(EN)


@router.get("/hi/pricing", response_class=HTMLResponse)
def pricing_hi() -> HTMLResponse:
    return render(HI)


@router.get("/{lang:xlang}/pricing", response_class=HTMLResponse)
def pricing_lang(lang: str) -> HTMLResponse:
    return render(lang)
