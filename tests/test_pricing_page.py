"""/pricing: the public price list (DIVASTRO-149).

Every price on the page is compared with the billing catalogue, which is the one
source of truth, and the page is shown to follow the catalogue and the free
allowance when those change. Also: the JSON-LD parses and quotes the same prices,
titles / canonicals are unique, a regional prefix renders noindex English with the
notice, and the page is wired into the sitemap, the /sitemap hub, the shared
footer, the visit beacon and the analytics vocabulary.

No server needed (in-process client, throwaway SQLite).

    ~/.venvs/divineastro/bin/python -u -m tests.test_pricing_page
"""

from __future__ import annotations

import dataclasses
import html as htmllib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_pricing_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, billing, i18n, pricing_pages, seo_pages  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def get(path: str):
    return client.get(path)


def title(h: str) -> str:
    return htmllib.unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1))


def h1(h: str) -> str:
    return htmllib.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S).group(1)))


def desc(h: str) -> str:
    return htmllib.unescape(re.search(r'<meta name="description" content="([^"]*)"', h).group(1))


def canonical(h: str) -> str | None:
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    return m.group(1) if m else None


def graph(h: str) -> list[dict]:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    out = []
    for b in blocks:
        data = json.loads(b)
        out += data["@graph"] if "@graph" in data else [data]
    return out


def rows(h: str) -> dict[str, str]:
    """sku -> the price cell's text, from the page's tables."""
    out = {}
    for sku, cell in re.findall(r'<tr id="([a-z0-9_]+)" data-sku="[^"]+">.*?<td class="pr-price"><b>(.*?)</b>', h, re.S):
        out[sku] = htmllib.unescape(cell)
    return out


def rupees(n: int) -> str:
    return f"₹{n:,}"


print("\n1. The page renders in English and Hindi")
en, hi = get("/pricing"), get("/hi/pricing")
check("/pricing is 200 HTML", en.status_code == 200 and "text/html" in en.headers["content-type"])
check("/hi/pricing is 200 HTML", hi.status_code == 200)
check("English is indexable (no noindex)", "noindex" not in en.text.split("</head>")[0])
check("Hindi is indexable", "noindex" not in hi.text.split("</head>")[0])
check("Hindi page is in Hindi", re.search(r"[ऀ-ॿ]", h1(hi.text)) is not None, h1(hi.text))
check("English h1", h1(en.text) == "Divine Astro prices", h1(en.text))

print("\n2. Every catalogue product is listed, at the catalogue price")
catalogue = billing.catalogue()
for label, page in (("en", en.text), ("hi", hi.text)):
    listed = rows(page)
    check(f"[{label}] every sku is on the page",
          set(listed) == {p["sku"] for p in catalogue}, f"missing {sorted({p['sku'] for p in catalogue} - set(listed))}")
    wrong = {p["sku"]: (listed.get(p["sku"]), rupees(p["rupees"])) for p in catalogue
             if listed.get(p["sku"]) != rupees(p["rupees"])}
    check(f"[{label}] every price equals the catalogue's", not wrong, str(wrong))
for p in catalogue:
    check(f"English page names '{p['title']}'", htmllib.escape(p["title"]) in en.text or p["title"] in en.text)
    check(f"Hindi page names '{p['title_hi']}'", p["title_hi"] in hi.text)
packs = [p for p in catalogue if p["kind"] == "questions"]
for p in packs:
    each = f"₹{p['per_question']:.2f}"
    check(f"price per question {each} shown for {p['sku']}", each in en.text)
check("the free allowance is billing.FREE_QUESTIONS",
      f"{billing.FREE_QUESTIONS} free questions" in en.text, str(billing.FREE_QUESTIONS))
check("the page links the refund policy and the terms",
      'href="/refund"' in en.text and 'href="/terms"' in en.text)
check("the call to action goes to the app's free kundali",
      'id="pricing-cta"' in en.text and 'href="/?open=kundali"' in en.text)
check("the page script is the static file, with no inline script",
      '<script src="/static/pricing.js"' in en.text)
check("the astrologer and turnaround come from billing",
      billing.ASTROLOGER in en.text and f"about {billing.TURNAROUND_DAYS} days" in en.text)
check("no claim about page counts for the reports or the book",
      not re.search(r"\b\d+\+? ?-?pages?\b", re.sub(r"Hand-written Kundali . \d pages", "", en.text.split("<h1")[1].split("<footer")[0])))

print("\n3. The page follows the catalogue and the settings")
saved_products, saved_free = dict(billing.PRODUCTS), billing.FREE_QUESTIONS
try:
    billing.PRODUCTS["q10"] = dataclasses.replace(billing.PRODUCTS["q10"], amount_paise=12300)
    billing.FREE_QUESTIONS = 7
    h = get("/pricing").text
    check("a changed catalogue price shows on the page", rows(h)["q10"] == "₹123", rows(h).get("q10"))
    check("a changed free allowance shows on the page", "7 free questions" in h)
    ld = [n for n in graph(h) if n.get("@type") == "Product" and n["sku"] == "q10"][0]
    check("and in the Offer markup", ld["offers"]["price"] == "123", str(ld["offers"]))
finally:
    billing.PRODUCTS.clear()
    billing.PRODUCTS.update(saved_products)
    billing.FREE_QUESTIONS = saved_free
check("(catalogue restored)", rows(get("/pricing").text)["q10"] == "₹111")

print("\n4. JSON-LD")
for label, page in (("en", en.text), ("hi", hi.text)):
    nodes = graph(page)
    types = [n.get("@type") for n in nodes]
    products = [n for n in nodes if n.get("@type") == "Product"]
    check(f"[{label}] one Product per catalogue entry", len(products) == len(catalogue), str(len(products)))
    bad = [p["sku"] for p in products
           if p["offers"]["priceCurrency"] != "INR"
           or p["offers"]["price"] != str(billing.PRODUCTS[p["sku"]].rupees)]
    check(f"[{label}] every Offer is INR at the catalogue price", not bad, str(bad))
    faq = [n for n in nodes if n.get("@type") == "FAQPage"]
    check(f"[{label}] a FAQPage with 3-4 questions",
          len(faq) == 1 and 3 <= len(faq[0]["mainEntity"]) <= 4)
    visible = htmllib.unescape(re.sub(r"<[^>]+>", " ", page))
    check(f"[{label}] every FAQ question is visible on the page",
          all(q["name"] in visible for q in faq[0]["mainEntity"]))
    check(f"[{label}] WebPage and BreadcrumbList present", "WebPage" in types and "BreadcrumbList" in types)

print("\n5. Self canonical, unique title / description / h1")
check("English canonical is itself", canonical(en.text) == seo_pages.SITE_URL + "/pricing", str(canonical(en.text)))
check("Hindi canonical is itself", canonical(hi.text) == seo_pages.SITE_URL + "/hi/pricing", str(canonical(hi.text)))
check("titles differ", title(en.text) != title(hi.text))
check("descriptions differ", desc(en.text) != desc(hi.text))
check("h1s differ", h1(en.text) != h1(hi.text))
other = [get(p).text for p in ("/free-kundali", "/kundali-milan", "/sitemap", "/refund")]
check("the title is unique among sibling pages", title(en.text) not in [title(o) for o in other])
check("the description is unique among sibling pages", desc(en.text) not in [desc(o) for o in other])
check("hreflang pairs en and hi", 'rel="alternate" hreflang="hi"' in en.text and 'rel="alternate" hreflang="en"' in hi.text)
check("the description quotes real prices",
      f"₹{min(p['rupees'] for p in packs)}" in desc(en.text) and f"₹{billing.PRODUCTS['life_book'].rupees}" in desc(en.text),
      desc(en.text))

print("\n6. Another language: English body, noindex, the notice")
for code in ("kn", "pa"):
    r = get(f"/{code}/pricing")
    head = r.text.split("</head>")[0]
    check(f"/{code}/pricing is 200", r.status_code == 200)
    check(f"/{code}/pricing is noindex", "noindex" in head)
    check(f"/{code}/pricing carries its own canonical", canonical(r.text) == f"{seo_pages.SITE_URL}/{code}/pricing")
    check(f"/{code}/pricing shows the English text", h1(r.text) == "Divine Astro prices", h1(r.text))
    check(f"/{code}/pricing has the translation notice", 'class="notice"' in r.text or "notice" in r.text)
    check(f"/{code}/pricing has no hreflang alternates", 'rel="alternate" hreflang' not in r.text)
    check(f"/{code}/pricing still lists every price", set(rows(r.text)) == {p["sku"] for p in catalogue})

print("\n7. Sitemap, hub, footer, beacon, analytics")
xml = get("/sitemap.xml").text
check("sitemap.xml lists /pricing and /hi/pricing",
      "<loc>https://divineastro.org/pricing</loc>" in xml.replace(seo_pages.SITE_URL, "https://divineastro.org")
      and "/hi/pricing</loc>" in xml)
check("sitemap.xml does not list the untranslated copies", "/kn/pricing" not in xml)
m = re.search(r"<loc>[^<]*/pricing</loc><priority>([\d.]+)</priority>", xml)
check("a low priority", m is not None and float(m.group(1)) <= 0.4, str(m and m.group(1)))
check("sitemap_paths() has them", "/pricing" in seo_pages.sitemap_paths() and "/hi/pricing" in seo_pages.sitemap_paths())
hub = get("/sitemap").text
check("the /sitemap hub links /pricing", 'href="/pricing"' in hub)
check("the Hindi hub links /hi/pricing", 'href="/hi/pricing"' in get("/hi/sitemap").text)
for path in ("/panchang", "/hi/panchang", "/rashifal", "/kn/panchang", "/pricing"):
    r = get(path)
    pre = i18n.strip_prefix(path)[0]
    want = f'href="{i18n.prefix(pre)}/pricing"'
    foot = r.text.split('<footer class="site-footer">')[-1]
    check(f"the footer of {path} links {want}", want in foot)
check("the home page footer links /pricing", 'href="/pricing"' in get("/").text)
check("the beacon accepts /pricing, /hi/pricing and a regional copy",
      all(analytics.is_public_page(p) for p in ("/pricing", "/hi/pricing", "/kn/pricing")))
check("the beacon still rejects unknown paths", not analytics.is_public_page("/pricing/x"))
check("pricing_pages.is_public_path agrees", pricing_pages.is_public_path("/hi/pricing") and not pricing_pages.is_public_path("/x"))
for name in ("pricing_view", "plans_click", "offer_shown", "offer_click"):
    check(f"event '{name}' is accepted", analytics.parse_event({"name": name, "detail": "x"}) == (name, "x"))
labels = analytics.EVENT_LABELS
for key in (("pricing_view", "home"), ("pricing_view", "page"), ("plans_click", ""), ("offer_shown", ""),
            ("offer_click", ""), ("offer_shown", "low_credits"), ("offer_click", "life_book_dashboard"),
            ("offer_shown", "sq_career"), ("offer_click", "life_book")):
    check(f"plain-words label for {key}", bool(labels.get(key)))
check("the in-app funnel kept its steps and gained the new ones",
      all(s in [n for _l, n, _d in analytics.APP_FUNNEL] for s in
          ("home_cta", "chart_cast", "signup", "ask_sent", "store_open", "checkout_start", "paid",
           "pricing_view", "offer_click")))
js = (ROOT / "app" / "static" / "pricing.js").read_text(encoding="utf-8")
check("pricing.js reports pricing_view and plans_click through daTrack",
      "daTrack" in js and "'pricing_view'" in js and "'plans_click'" in js)

print("\n8. Product wording stays inside what the code delivers")
for p in catalogue:
    text = f"{p['blurb']} {p['blurb_hi']}"
    check(f"{p['sku']}: no page-count or turnaround promise in the blurb",
          not re.search(r"\b(\d+\+?[- ]?page|2-page|35\+|5-year|full year|personally)", text, re.I), p["blurb"])

print()
if failures:
    print(f"{len(failures)} FAILED")
    sys.exit(1)
print("pricing page: all green")
