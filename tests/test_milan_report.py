"""DIVASTRO-156: the ₹51 detailed Kundali Milan report.

In process (TestClient, a throwaway SQLite database, the test gateway, the console
mail transport):

  1. The product: sku milan_report, ₹51 on the Diwali offer, ₹91 list price (~80%
     above, like the other reports), its own kind, English and Hindi words; in the
     catalogue; ₹91 once the offer is off.
  2. The order carries BOTH people: /api/orders refuses the report without them (or
     with details that cannot be matched), refuses them on any other product and on an
     admin manual sale, and freezes them on Order.order_data with the order's email.
  3. Delivery: paying emails the PDF (attachment) to the ORDER's address, once; an
     account with no email still gets it in My orders; /api/pdf/milan/<id> is 402
     unpaid, 404 for someone else's order, a PDF in English and Hindi when paid.
  4. The content is the engine's: the eight kootas and the total exactly as
     astro.matching scores them, Manglik for both and the pair verdict, the planetary
     table, and the wedding dates are the /muhurat/vivah engine's dates; no error words.
  5. The sample (/samples/milan_report.pdf, watermarked) and the public cards:
     /kundali-milan (every language, its own words), a naam-milan result, /pricing.
  6. Analytics events, the app strings in all 13 languages, the migration up and down.

    ASTRO_SECRET_KEY=ci python -u -m tests.test_milan_report
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_tmp = tempfile.mkdtemp(prefix="astro_milan_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_SAMPLES_DIR"] = _tmp
os.environ.update({
    "ASTRO_DEV_LOGIN": "1", "ASTRO_COOKIE_SECURE": "0", "ASTRO_GATEWAY": "test",
    "ASTRO_SMTP_HOST": "console", "ASTRO_ADMIN_EMAILS": "owner@example.com",
    "ASTRO_EMAIL_ANSWER_WORKER": "0", "ASTRO_OFFER_ENDS": "2099-01-01T00:00:00+05:30",
})
for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ASTRO_OFFER_OFF"):
    os.environ.pop(k, None)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import inspect  # noqa: E402

from app import analytics, billing, mail, milan_report, muhurat_pages, pdf_report, sample_reports  # noqa: E402
from app.astro import matching  # noqa: E402
from app.db import Order, User, session as db_session  # noqa: E402
from app.main import app  # noqa: E402
from tests import pdf_text  # noqa: E402

failures: list[str] = []
CHROME = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/126.0 Mobile Safari/537.36")
GROOM = {"name": "Ravi", "date": "1990-08-15", "time": "10:30", "time_known": True,
         "place": "New Delhi, India", "latitude": 28.6139, "longitude": 77.209, "timezone": "Asia/Kolkata"}
BRIDE = {"name": "Asha", "date": "1992-03-04", "time": "06:15", "time_known": True,
         "place": "Mumbai, India", "latitude": 19.076, "longitude": 72.8777, "timezone": "Asia/Kolkata"}
PAIR = {"groom": GROOM, "bride": BRIDE, "lang": "en"}
BAD_WORDS = re.compile(r"\bNone\b|\bnan\b|Traceback|TypeError|KeyError|\bundefined\b|TODO|lorem", re.I)
LANGS = ("en", "hi", "kn", "te", "ta", "ml", "bn", "or", "pa", "ne", "as", "mr", "gu")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def browser(email: str) -> TestClient:
    c = TestClient(app, client=("203.0.113.9", 40000), headers={"User-Agent": CHROME})
    r = c.post("/api/auth/dev", json={"email": email})
    assert r.status_code == 200, r.text
    return c


def order_row(order_id: int) -> Order:
    with db_session() as db:
        return db.get(Order, order_id)


def mails_to(addr: str) -> list:
    return [m for m in mail.OUTBOX if addr in m[0]]


def wait_for_mail(addr: str, n: int = 1, seconds: float = 90) -> list:
    end = time.time() + seconds
    while time.time() < end:
        got = mails_to(addr)
        if len(got) >= n:
            return got
        time.sleep(0.25)
    return mails_to(addr)


def strings(obj) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for v in obj.values() for s in strings(v)]
    if isinstance(obj, (list, tuple)):
        return [s for v in obj for s in strings(v)]
    return []


def spy_compile():
    seen = []
    real = pdf_report._compile

    def spy(body, data, files=None):
        seen.append((data, dict(files or {})))
        return real(body, data, files)
    return seen, mock.patch.object(pdf_report, "_compile", spy)


# ---------------------------------------------------------------- 1. product
def part1_product() -> None:
    print("\n1. The product")
    p = billing.PRODUCTS.get("milan_report")
    check("milan_report is in PRODUCTS", p is not None)
    check("offer price ₹51 (5100 paise), list ₹91 (9100)", p.offer_paise == 5100 and p.list_paise == 9100
          and billing.LIST_PRICES_PAISE["milan_report"] == 9100)
    check("the list price is ~80% above the offer, like the other reports' list prices",
          1.7 <= p.list_paise / p.offer_paise <= 1.9
          and all(1.7 <= billing.PRODUCTS[s].list_paise / billing.PRODUCTS[s].offer_paise <= 1.9
                  for s in ("sq_career", "life_book")))
    check("its own kind, no credits, on the offer", p.kind == "milan_report" == billing.MILAN_KIND
          and p.credits == 0 and p.on_offer)
    check("English and Hindi title and description",
          "Kundali Milan" in p.title and "मिलान" in p.title_hi and "koota" in p.blurb and "कूट" in p.blurb_hi)
    cat = {x["sku"]: x for x in billing.catalogue()}
    m = cat.get("milan_report") or {}
    check("in the catalogue at ₹51 with the struck ₹91 while the offer is live",
          m.get("amount_paise") == 5100 and m.get("list_amount_paise") == 9100 and m.get("rupees") == 51)
    with mock.patch.dict(os.environ, {"ASTRO_OFFER_OFF": "1"}):
        m = {x["sku"]: x for x in billing.catalogue()}["milan_report"]
        check("after the offer: ₹91 and nothing struck", m["amount_paise"] == 9100 and m["list_amount_paise"] is None)
    api = TestClient(app).get("/api/products").json()["products"]
    check("/api/products lists it", any(x["sku"] == "milan_report" for x in api))


# ---------------------------------------------------------------- 2. order data
def part2_order() -> tuple[TestClient, int]:
    print("\n2. The order carries both people")
    c = browser("milan.buyer@example.com")
    r = c.post("/api/orders", json={"sku": "milan_report"})
    check("no birth details: 400", r.status_code == 400, r.text[:120])
    r = c.post("/api/orders", json={"sku": "milan_report", "milan": {"groom": GROOM}})
    check("one person only: 400", r.status_code == 400, r.text[:120])
    bad = {**PAIR, "bride": {**BRIDE, "date": "not-a-date"}}
    r = c.post("/api/orders", json={"sku": "milan_report", "milan": bad})
    check("an unreadable date: 400 naming it", r.status_code == 400 and "bride" in r.text, r.text[:160])
    r = c.post("/api/orders", json={"sku": "milan_report",
                                   "milan": {**PAIR, "groom": {**GROOM, "latitude": 999}}})
    check("coordinates out of range: 400", r.status_code == 400, r.text[:120])
    r = c.post("/api/orders", json={"sku": "sq_career", "milan": PAIR})
    check("two people on another product: 400", r.status_code == 400, r.text[:120])

    r = c.post("/api/orders", json={"sku": "milan_report", "milan": {**PAIR, "lang": "hi"}})
    check("both people: 200, ₹51", r.status_code == 200 and r.json()["order"]["amount_paise"] == 5100, r.text[:200])
    oid = r.json()["order"]["id"]
    o = order_row(oid)
    data = json.loads(o.order_data)
    check("order_data holds both people, cleaned", data["milan"]["groom"]["name"] == "Ravi"
          and data["milan"]["bride"]["date"] == "1992-03-04" and data["milan"]["bride"]["time"] == "06:15"
          and data["milan"]["groom"]["latitude"] == 28.6139, str(data)[:200])
    check("...with the report language and the ORDER's email", data["lang"] == "hi"
          and data["email"] == "milan.buyer@example.com")
    check("the order's email is what delivery reads", milan_report.order_email(o) == "milan.buyer@example.com")
    check("a per-order email column (guest checkout) would win",
          milan_report.order_email(type("O", (), {"email": "guest@example.com", "order_data": o.order_data})())
          == "guest@example.com")
    check("an unknown time is noon, kept as unknown",
          milan_report.clean_pair({**PAIR, "bride": {**BRIDE, "time_known": False}})["bride"]["time"] == "12:00")
    check("markup in a name is neutralised",
          "*" not in milan_report.clean_pair({**PAIR, "groom": {**GROOM, "name": "**Ra_vi**"}})["groom"]["name"])

    with db_session() as db:
        user = db.query(User).filter(User.email == "milan.buyer@example.com").one()
        try:
            billing.create_manual_order(db, user, user, sku="milan_report", amount_paise=5100)
            refused = False
        except ValueError:
            refused = True
    check("an admin manual sale of it is refused (it has no birth details)", refused)
    return c, oid


# ---------------------------------------------------------------- 3. delivery
def part3_delivery(c: TestClient, oid: int) -> None:
    print("\n3. Delivery")
    r = c.get(f"/api/pdf/milan/{oid}")
    check("unpaid: 402", r.status_code == 402, str(r.status_code))
    other = browser("someone.else@example.com")
    check("someone else's order: 404", other.get(f"/api/pdf/milan/{oid}").status_code == 404)

    # A later change lets a guest give the address: the ORDER's address is used, not the account's.
    with db_session() as db:
        o = db.get(Order, oid)
        d = json.loads(o.order_data)
        d["email"] = "order.address@example.com"
        o.order_data = json.dumps(d)
        db.commit()
    mail.OUTBOX.clear()
    r = c.post("/api/orders/confirm", json={"order_id": oid, "payload": {}})
    check("paid through the test gateway", r.status_code == 200 and r.json()["order"]["status"] == "paid", r.text[:200])
    got = wait_for_mail("order.address@example.com")
    check("the PDF is emailed to the order's address", len(got) == 1, str([m[0] for m in mail.OUTBOX]))
    check("...and not to the account's", not mails_to("milan.buyer@example.com"))
    if got:
        m = got[0]
        att = (m.attachments or [None])[0]
        check("one PDF attachment, named for the pair", att is not None and att[1] == "application/pdf"
              and att[2].startswith(b"%PDF-") and "Ravi" in att[0] and "Asha" in att[0], str(att and att[:2]))
        check("Hindi order: Hindi subject", "कुंडली मिलान" in m[1], m[1])
    time.sleep(0.5)
    data = json.loads(order_row(oid).order_data)
    check("the order records when it was emailed", bool(data.get("emailed_at")))
    check("delivering again is a no-op (once per order)", milan_report.deliver(oid) is False)
    with db_session() as db:
        billing.mark_paid(db, db.get(Order, oid), "again")
    time.sleep(1)
    check("a second payment confirmation does not email again", len(mails_to("order.address@example.com")) == 1)

    r = c.get(f"/api/pdf/milan/{oid}")
    check("paid: the owner downloads a PDF", r.status_code == 200 and r.content.startswith(b"%PDF-")
          and "attachment" in r.headers.get("content-disposition", ""), str(r.status_code))
    r = c.get(f"/api/pdf/milan/{oid}?lang=en")
    text = "\n".join(pdf_text.pages_text(r.content))
    check("?lang=en prints English", "Detailed Kundali Milan Report" in text)
    orders = c.get("/api/orders").json()["orders"]
    row = next(o for o in orders if o["id"] == oid)
    check("My orders: paid, with the pair's names", row["status"] == "paid" and row["pair"] == "Ravi & Asha", str(row))

    # An account with no email address (a phone account): nothing is emailed, the PDF is in My orders.
    with db_session() as db:
        u = db.query(User).filter(User.email == "someone.else@example.com").one()
        u.provider = "phone"
        db.commit()
    mail.OUTBOX.clear()
    r = other.post("/api/orders", json={"sku": "milan_report", "milan": PAIR})
    o2 = r.json()["order"]["id"]
    check("no email on the order", json.loads(order_row(o2).order_data)["email"] == "")
    other.post("/api/orders/confirm", json={"order_id": o2, "payload": {}})
    time.sleep(1)
    check("...nothing emailed", not mail.OUTBOX)
    check("...and it downloads from My orders", other.get(f"/api/pdf/milan/{o2}").status_code == 200)


# ---------------------------------------------------------------- 4. content
def part4_content() -> None:
    print("\n4. The content is the engine's")
    pair = milan_report.clean_pair(PAIR)
    groom, bride = milan_report.cast(pair)
    want = matching.match(groom, bride, lang="en")
    seen, patch = spy_compile()
    today = dt.date(2026, 10, 21)
    with patch:
        pdf = milan_report.milan_report_pdf(pair, language="en", today=today)
    data, files = seen[0]
    rows = data["koota_table"]["rows"]
    check("eight kootas, in the engine's order with its labels",
          [r[0] for r in rows] == [k["label"] for k in want["ashtakoot"]["kootas"]] and len(rows) == 8)
    check("each koota's points are the engine's",
          [r[3] for r in rows] == [f"{k['score']:g} / {k['max']:g}" for k in want["ashtakoot"]["kootas"]])
    check("each koota explained: what it measures + the engine's own note",
          all(any(k["note"] in s for s in strings(blk)) for k, (_, blk) in zip(want["ashtakoot"]["kootas"], data["kootas"])))
    check("the total is the engine's", data["total"] == f"{want['ashtakoot']['total']:g} / 36")
    mangal = " ".join(strings(data["mangal"]))
    check("Manglik for both and the pair verdict",
          "Ravi" in mangal and "Asha" in mangal and want["mangal"]["pair"]["note"] in mangal)
    check("the planetary table: six rows for both charts", len(data["planets"]["rows"]) == 6
          and all(len(r) == 3 for r in data["planets"]["rows"]))
    check("both D1 drawings embedded", sorted(files) == ["bride_d1.svg", "groom_d1.svg"])
    wd = data["wedding"]["rows"]
    check("15 months of wedding dates", len(wd) == milan_report.WEDDING_MONTHS, str(len(wd)))
    yd = muhurat_pages._year_data("vivah", 2026)
    nov = [d["date"].day for d in yd["months"][11]]
    nov_row = next(r for r in wd if r[0].startswith("November 2026"))
    check("...the vivah engine's own dates (November 2026)",
          nov_row[1].split(" ")[0].rstrip(",") == str(nov[0]) and nov_row[2] == str(len(nov)), f"{nov_row} {nov}")
    check("no error words in what is typeset", not any(BAD_WORDS.search(s) for s in strings(data)))
    check("it says it is the rule engine's, not a model's", "No AI model" in " ".join(strings(data["about"])))
    check("a valid PDF of at least 4 pages", pdf.startswith(b"%PDF-") and len(pdf_text.pages_text(pdf)) >= 4)
    no_time = milan_report.clean_pair({**PAIR, "bride": {**BRIDE, "time_known": False}})
    seen, patch = spy_compile()
    with patch:
        milan_report.milan_report_pdf(no_time, language="en", today=today)
    data = seen[0][0]
    check("a birth time missing: no lagna-based lines or drawing for that chart, and it says so",
          sorted(seen[0][1]) == ["groom_d1.svg"] and data["planets"]["rows"][0][2] == "—"
          and "noon was used" in " ".join(strings(data["mangal"])))
    if pdf_report.devanagari_font():
        seen, patch = spy_compile()
        with patch:
            milan_report.milan_report_pdf(pair, language="hi", today=today)
        hi = " ".join(strings(seen[0][0]))
        check("Hindi report in Devanagari", seen[0][0]["lang"] == "hi" and len(re.findall(r"[ऀ-ॿ]", hi)) > 800)


# ---------------------------------------------------------------- 5. sample + public cards
def part5_pages() -> None:
    print("\n5. Sample and public cards")
    c = TestClient(app)
    r = c.get("/samples/milan_report.pdf")
    check("sample: 200 PDF, inline, named", r.status_code == 200 and r.content.startswith(b"%PDF-")
          and "kundali-milan-report" in r.headers["content-disposition"])
    pages = pdf_text.pages_text(r.content)
    check("sample: watermark and footer on every page", all("SAMPLE" in p and "fictional chart" in p for p in pages))
    check("sample: the fictional pair", "Arjun" in pages[0] and "Meera" in pages[0])
    check("sample in Hindi", c.get("/samples/milan_report.pdf?lang=hi").status_code == 200)

    h = c.get("/kundali-milan").text
    check("/kundali-milan: the card with its words", 'data-milan-report="page"' in h
          and "Detailed matching report" in h and "guna by guna, Manglik dosh, compatibility" in h)
    check("...₹51 with the struck ₹91 while the offer is live", "<b>₹51</b>" in h and "₹91</s>" in h)
    check("...the button opens the matching tool, a sample link, the tracker",
          'href="/?open=milan" data-milan-report-go' in h and "/samples/milan_report.pdf" in h
          and "/static/milanreport.js" in h)
    resp = c.get("/kundali-milan")
    check("...its cache never outlives the offer (max 300 s)",
          re.search(r"max-age=(\d+)", resp.headers["cache-control"])
          and int(re.search(r"max-age=(\d+)", resp.headers["cache-control"]).group(1)) <= 300)
    with mock.patch.dict(os.environ, {"ASTRO_OFFER_OFF": "1"}):
        h2 = c.get("/kundali-milan").text
        check("offer off: ₹91, nothing struck", "<b>₹91</b>" in h2 and "₹91</s>" not in h2)
    h = c.get("/hi/kundali-milan").text
    check("/hi/kundali-milan: Hindi card, Hindi sample", "विस्तृत मिलान रिपोर्ट" in h
          and "/samples/milan_report.pdf?lang=hi" in h and "open=milan&amp;lang=hi" in h)
    from app.seo_text import TEXT
    bad = []
    for lang in LANGS:
        page = c.get(f"/{lang}/kundali-milan" if lang not in ("en", "hi") else
                     ("/kundali-milan" if lang == "en" else "/hi/kundali-milan")).text
        words = TEXT[lang]
        title = words.get("km.rpt.title")
        if not title or (lang != "en" and title == TEXT["en"]["km.rpt.title"]) or title not in page:
            bad.append(lang)
    check("every language's /kundali-milan shows the card in its own words", not bad, str(bad))
    n = c.get("/naam-se-kundali-milan", params={"boy": "Ram", "girl": "Sita"}).text
    check("naam milan result: the card, detail 'naam'", 'data-milan-report="naam"' in n and "₹51" in n)
    check("naam milan without a result: no card", "data-milan-report" not in c.get("/naam-se-kundali-milan").text)

    p = c.get("/pricing").text
    row = re.search(r'<tr id="milan_report".*?</tr>', p, re.S)
    check("/pricing lists it with ₹51, the struck ₹91 and a sample",
          row and "<b>₹51</b>" in row.group(0) and "₹91" in row.group(0)
          and "/samples/milan_report.pdf" in row.group(0), row.group(0)[:200] if row else "no row")
    check("/pricing: its section heading", "Kundali Milan report" in p)
    check("/hi/pricing: Hindi", "विस्तृत कुंडली मिलान रिपोर्ट" in c.get("/hi/pricing").text)


# ---------------------------------------------------------------- 6. events, strings, migration
def part6_rest() -> None:
    print("\n6. Events, strings, migration")
    for name in ("milan_report_shown", "milan_report_click"):
        check(f"{name} is a known event", name in analytics.EVENT_NAMES
              and analytics.parse_event({"name": name, "detail": "app"}) == (name, "app"))
        check(f"{name} is labelled and in the funnel",
              all((name, d) in analytics.EVENT_LABELS for d in ("", "app", "page", "naam"))
              and name in [n for _l, n, _d in analytics.APP_FUNNEL])
    check("the sample view is labelled", ("sample_view", "milan_report") in analytics.EVENT_LABELS)
    check("the sample exists for it", "milan_report" in sample_reports.SKUS)

    root = Path(__file__).resolve().parent.parent / "app" / "static" / "i18n"
    en = json.loads((root / "en.json").read_text(encoding="utf-8"))
    keys = [k for k in en if k.startswith("acct.milanRpt")]
    check("the app's milan report strings", len(keys) == 11, str(keys))
    bad = []
    for lang in LANGS:
        d = json.loads((root / f"{lang}.json").read_text(encoding="utf-8"))
        for k in keys:
            v = d.get(k, "")
            ph = set(re.findall(r"\{\w+\}", en[k]))
            if not v or (lang != "en" and v == en[k]) or set(re.findall(r"\{\w+\}", v)) != ph:
                bad.append(f"{lang}:{k}")
    check("...in all 13 languages, translated, placeholders kept", not bad, str(bad[:10]))
    js = (root.parent / "account.js").read_text(encoding="utf-8")
    used = set(re.findall(r'at\("(milanRpt\w+)"\)', js))
    check("every string account.js reads exists", used and all(f"acct.{k}" in en for k in used), str(used))

    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine
    proj = Path(__file__).resolve().parent.parent
    url = f"sqlite:///{Path(_tmp).as_posix()}/mig.db"
    cfg = Config(str(proj / "alembic.ini"))
    cfg.set_main_option("script_location", str(proj / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    app_url = os.environ["ASTRO_DATABASE_URL"]
    os.environ["ASTRO_DATABASE_URL"] = url
    try:
        command.upgrade(cfg, "head")
        eng = create_engine(url)
        cols = [c["name"] for c in inspect(eng).get_columns("orders")]
        check("migration up: orders.order_data", "order_data" in cols)
        eng.dispose()
        command.downgrade(cfg, "-1")
        eng = create_engine(url)
        cols = [c["name"] for c in inspect(eng).get_columns("orders")]
        check("migration down: gone", "order_data" not in cols)
        eng.dispose()
        command.upgrade(cfg, "head")
    finally:
        os.environ["ASTRO_DATABASE_URL"] = app_url


def main() -> int:
    part1_product()
    c, oid = part2_order()
    part3_delivery(c, oid)
    part4_content()
    part5_pages()
    part6_rest()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
