"""The ₹51 Kundali Milan report card on the public matching pages (DIVASTRO-156).

    /kundali-milan (every language)              detail "page"
    /naam-se-kundali-milan, under a result       detail "naam"

The report is written from both people's BIRTH details, which only the app's
matching tool collects, so the card's button opens that tool (/?open=milan); the
card shown under the in-app result is the one that starts checkout. Everything a
customer is charged or shown comes from the catalogue (billing.catalogue): the
price in force and, only while the Diwali offer is live, the struck-through regular
price, exactly as /pricing prints them. The words are seo_text.TEXT "km.rpt.*" (all
13 languages). /static/milanreport.js reports milan_report_shown / _click.
"""

from __future__ import annotations

import datetime as dt

from . import billing, i18n
from .seo_text import TEXT

_CSS = """<style>
.seo .milan-rpt { margin: 18px 0; padding: 14px 16px; border: 1px solid rgba(var(--gold-rgb), 0.45);
                  border-radius: 14px; background: rgba(var(--gold-rgb), 0.07); }
.seo .milan-rpt .mr-head { margin: 0 0 6px; font-size: 16.5px; line-height: 1.45; }
.seo .milan-rpt .mr-price { white-space: nowrap; }
.seo .milan-rpt .mr-price b { color: var(--gold-soft); font-size: 18px; }
.seo .milan-rpt .mr-price s.was { color: var(--ink-faint); margin-right: 6px; font-size: 15px; }
.seo .milan-rpt .mr-how { margin: 4px 0 10px; color: var(--ink-dim); font-size: 14px; }
.seo .milan-rpt .cta { margin: 6px 0 4px; }
.seo .milan-rpt .mr-sample { display: block; margin-top: 2px; font-size: 14px; }
.seo .sr-only { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; border: 0;
                overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; }
</style>"""


def _e(value: object) -> str:
    import html
    return html.escape(str(value), quote=True)


def _tx(key: str, lang: str) -> str:
    return i18n.t(key, lang, TEXT)


def product(now: dt.datetime | None = None) -> dict | None:
    """The report as the catalogue prices it right now (None if it is not on sale)."""
    return next((p for p in billing.catalogue(now=now) if p["sku"] == billing.MILAN_SKU), None)


def price_html(p: dict, lang: str) -> str:
    """"<s>₹91</s> ₹51" while the offer is live, else "₹51" (catalogue figures only)."""
    now = f"<b>₹{p['rupees']:,}</b>"
    live = p["offer"]["active"] and p.get("list_amount_paise") and p["list_amount_paise"] > p["amount_paise"]
    if not live:
        return now
    return (f'<s class="was"><span class="sr-only">{_e(_tx("km.rpt.was", lang))} </span>'
            f'₹{p["list_amount_paise"] // 100:,}</s><span class="sr-only">, {_e(_tx("km.rpt.now", lang))} </span>'
            + now)


def card(lang: str, detail: str = "page", now: dt.datetime | None = None) -> str:
    """The card's HTML ("" when the product is not in the catalogue)."""
    p = product(now)
    if p is None:
        return ""
    sample = "/samples/milan_report.pdf" + ("?lang=hi" if lang == "hi" else "")
    go = i18n.app_link(lang, "open=milan")
    return (
        f'{_CSS}<div class="milan-rpt" data-milan-report="{_e(detail)}" id="milan-report">'
        f'<p class="mr-head"><strong>{_e(_tx("km.rpt.title", lang))}</strong> — '
        f'{_e(_tx("km.rpt.sub", lang))} — <span class="mr-price">{price_html(p, lang)}</span></p>'
        f'<p class="mr-how">{_e(_tx("km.rpt.how", lang))}</p>'
        f'<a class="cta" href="{_e(go)}" data-milan-report-go>{_e(_tx("km.rpt.btn", lang))}</a>'
        f'<a class="mr-sample" href="{_e(sample)}" target="_blank" rel="noopener" '
        f'data-sample="milan_report">{_e(_tx("km.rpt.sample", lang))}</a>'
        f'</div><script src="/static/milanreport.js" defer></script>')


def offer(now: dt.datetime | None = None) -> dict | None:
    """The live offer ({active, name, ends_at}) when the card's price is an offer price."""
    p = product(now)
    return p["offer"] if p and p["offer"]["active"] and p["offer"]["ends_at"] else None
