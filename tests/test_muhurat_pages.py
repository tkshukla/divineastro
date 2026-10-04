"""The year-long Vivah / Griha Pravesh muhurat pages (DIVASTRO-109).

Reads the HTML exactly as a crawler gets it. Pins: both languages render with
Devanagari on the Hindi copy, hreflang pairs point at each other, the pages are
in the sitemap and accepted by the visit beacon, and - the point of the ticket -
no date listed on a page falls inside a period the engine itself says is barred
(Chaturmas, Kharmas, Pitru Paksha, ...), with the excluded periods spelled out
from the computed runs.

No server needed (FastAPI's in-process client). A throwaway SQLite database.

    ~/.venvs/divineastro/bin/python -u -m tests.test_muhurat_pages
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_muhurat_pages_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, i18n, muhurat_pages, muhurat_text, seo_pages  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
ROW_DATE = re.compile(r'<tr data-date="(\d{4}-\d\d-\d\d)">')


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def main() -> int:
    print("1. Every page renders, both languages")
    t0 = time.time()
    pages = {}
    for path in muhurat_pages.page_paths():
        r = client.get(path)
        pages[path] = r.text
        check(f"{path}: 200 text/html",
              r.status_code == 200 and r.headers["content-type"].startswith("text/html"),
              str(r.status_code))
    print(f"     (first render of all pages: {time.time() - t0:.1f}s)")
    t1 = time.time()
    client.get("/muhurat/vivah-2026")
    check("second request is served from the cache (<0.5s)", time.time() - t1 < 0.5,
          f"{time.time() - t1:.2f}s")

    print("\n2. Shell: hreflang, lang, beacon, AdSense, footer, CTA")
    for path, html in pages.items():
        lang, en_path = i18n.strip_prefix(path)       # DIVASTRO-123: also /kn/, /te/
        hi = lang == "hi"
        check(f"{path}: html lang", f'<html lang="{i18n.get(lang).bcp47}">' in html)
        check(f"{path}: canonical is itself", f'<link rel="canonical" href="{SITE}{path}"/>' in html)
        check(f"{path}: hreflang en/hi/x-default (+ every translated copy)",
              f'hreflang="en-IN" href="{SITE}{en_path}"' in html
              and f'hreflang="hi-IN" href="{SITE}/hi{en_path}"' in html
              and all(f'hreflang="{i18n.get(c).bcp47}" href="{SITE}{i18n.localized_path(en_path, c)}"'
                      in html for c in muhurat_pages.TRANSLATED)
              and f'hreflang="x-default" href="{SITE}{en_path}"' in html)
        check(f"{path}: visit.js beacon", '<script src="/static/visit.js" defer>' in html)
        check(f"{path}: AdSense", f"client={seo_pages.ADSENSE_CLIENT}" in html)
        check(f"{path}: footer", 'class="site-footer"' in html and "/privacy" in html)
        check(f"{path}: CTA into the Muhurat Finder", 'href="/?open=muhurat"' in html
              or f'href="/?open=muhurat&amp;lang={lang}"' in html)
        check(f"{path}: has date rows", len(ROW_DATE.findall(html)) > 5)
        if hi:
            body = html.split("<main", 1)[1]
            check(f"{path}: Devanagari body", len(DEVANAGARI.findall(body)) > 300)
            check(f"{path}: Hindi month/tithi names", "नवंबर" in body and "शुक्ल" in body and "नक्षत्र" in body)
        check(f"{path}: says timings vary by city",
              ("vary by city" in html) or ("दूसरे शहर" in html)
              or (lang not in ("en", "hi") and muhurat_text.TEXT[lang]["note"].split("</strong>")[0]
                  in html))

    print("\n3. No listed date inside an excluded period; periods explained")
    from app.astro import muhurat
    for path, html in pages.items():
        kind, _, year = path.rsplit("/", 1)[1].rpartition("-")
        event = muhurat_pages.KINDS[kind].event
        dates = [dt.date.fromisoformat(d) for d in ROW_DATE.findall(html)]
        data = muhurat_pages._year_data(kind, int(year))
        inside = [d for d in dates for s, e, _k in data["spans"] if s <= d <= e]
        check(f"{path}: no date inside a computed excluded run", not inside, str(inside[:3]))
        bad = [d for d in dates[::7]
               if muhurat.evaluate_day(event, d, *muhurat_pages_city())["excluded"]]
        check(f"{path}: sampled dates re-checked by the engine", not bad, str(bad))
    en = pages["/muhurat/vivah-2026"]
    check("vivah 2026: Chaturmas explained with computed dates",
          "<strong>Chaturmas</strong>, 25 Jul – 20 Nov" in en,
          re.search(r"<strong>Chaturmas</strong>[^<]*", en).group(0) if "Chaturmas</strong>" in en else "")
    check("vivah 2026: Pitru Paksha explained", "<strong>Pitru Paksha</strong>, 26 Sep – 10 Oct" in en)
    check("vivah 2026: Kharmas crossing the year shows its year",
          re.search(r"<strong>Kharmas</strong>, \d+ Dec 2026 – \d+ Jan 2027", en) is not None)
    dates26 = [dt.date.fromisoformat(d) for d in ROW_DATE.findall(en)]
    months = sorted({d.month for d in dates26})
    check("vivah 2026: open months match the published lists",
          months == [2, 3, 4, 5, 6, 7, 11, 12], str(months))
    check("vivah 2026: nothing Aug-Oct, nothing 21 Nov-",
          not [d for d in dates26 if dt.date(2026, 7, 25) <= d <= dt.date(2026, 11, 20)])
    check("vivah 2026: an empty month says why", "No vivah muhurat in September 2026 — Chaturmas" in en)
    hi = pages["/hi/muhurat/vivah-2026"]
    check("hi vivah 2026: periods in Hindi", "<strong>चातुर्मास</strong>" in hi
          and "<strong>पितृ पक्ष</strong>" in hi)
    check("hi and en list the same dates", ROW_DATE.findall(hi) == ROW_DATE.findall(en))

    print("\n4. Sitemap and beacon")
    sm = client.get("/sitemap.xml").text
    for path in muhurat_pages.page_paths():
        check(f"sitemap lists {path}", f"<loc>{SITE}{path}</loc>" in sm)
        check(f"beacon accepts {path}", analytics.is_public_page(path))
    for bad in ("/muhurat/vivah-2025", "/muhurat/foo-2026", "/hi/muhurat/x", "/muhurat/"):
        check(f"beacon rejects {bad}", not analytics.is_public_page(bad))
    r = client.get("/muhurat/vivah-2031")
    check("unknown year is a real 404", r.status_code == 404)
    r = client.get("/hi/muhurat/nothing-2026")
    check("unknown kind is a real 404", r.status_code == 404)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("muhurat pages: all green")
    return 0


def muhurat_pages_city():
    c = muhurat_pages.CITY
    return (c.latitude, c.longitude, c.timezone)


if __name__ == "__main__":
    raise SystemExit(main())
