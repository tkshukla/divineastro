"""Nakshatra and Rashi pages (DIVASTRO-115).

Every page is read as raw HTML (the crawler's view) through the shared checks
of tests/test_seo_pages.py. On top of that it pins what makes the pages
trustworthy: the facts must agree with the engines (matching.py's gana / yoni
/ nadi / varna, chart_service's Vimshottari lords), the 108 syllables must
cover the 108 padas exactly once, and each rashi must hold exactly nine padas.

No server needed (FastAPI's in-process client). A throwaway SQLite database is
used — never a real one.

    ~/.venvs/divineastro/bin/python -u -m tests.test_nakshatra_rashi_pages
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_nakshatra_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, nakshatra_pages as npg, seo_pages, share  # noqa: E402
from app.astro import matching, namakshar  # noqa: E402
from app.chart_service import NAKSHATRAS, SIGNS, VIMSHOTTARI  # noqa: E402
from app.main import app  # noqa: E402
from app.nakshatra_text import NAKSHATRA_TRAITS, RASHI_TRAITS  # noqa: E402
from app.rashifal_pages import RASHIS  # noqa: E402
from tests.test_seo_pages import canonical, check, failures, title  # noqa: E402
from tests import test_seo_pages as seo_tests  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
seo_tests.client = client

SITE = seo_pages.SITE_URL
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
N = namakshar.NAKSHATRA_LIST


def hreflang(html: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"', html))


def pair_checks(path: str, en: str, hi: str, lang: str, html: str) -> None:
    alt = hreflang(html)
    check(f"{path}: hreflang en/hi/x-default",
          alt.get("en-IN") == SITE + en and alt.get("hi-IN") == SITE + hi
          and alt.get("x-default") == SITE + en, str(alt))
    check(f"{path}: html lang", f'<html lang="{lang}-IN">' in html)
    check(f"{path}: WhatsApp share button", 'class="share-wa"' in html)
    if lang == "hi":
        body = html.split('<main class="seo">')[1]
        check(f"{path}: body is mostly Hindi", len(DEVANAGARI.findall(body)) > 400)


def main() -> int:
    print("\n1. Tables agree with the engines")
    check("27 nakshatras, in chart_service order", [n.name for n in N] == NAKSHATRAS)
    check("slugs are unique and URL-safe",
          len({n.slug for n in N}) == 27 and all(re.fullmatch(r"[a-z-]+", n.slug) for n in N))
    check("first and last slugs", N[0].slug == "ashwini" and N[-1].slug == "revati")
    for n in N:
        if (n.gana != matching.GANA_OF_NAKSHATRA[n.name]
                or n.yoni != matching.YONI_OF_NAKSHATRA[n.name]
                or n.nadi != matching.NADI_OF_NAKSHATRA[n.name]
                or n.lord != VIMSHOTTARI[n.index % 9][0]):
            check(f"{n.name}: gana/yoni/nadi/lord match the engines", False)
    check("gana, yoni, nadi from matching.py; lord from VIMSHOTTARI (all 27)",
          not any("match the engines" in f for f in failures))
    check("Ashwini lord Ketu, Bharani Venus, Revati Mercury (spot check)",
          (N[0].lord, N[1].lord, N[26].lord) == ("Ketu", "Venus", "Mercury"))
    check("Ashwini syllables चु चे चो ला",
          [d for d, _ in N[0].syllables] == ["चु", "चे", "चो", "ला"])
    check("every nakshatra has a deity and symbol in both languages",
          all(n.deity and n.symbol and DEVANAGARI.search(n.deity_hi)
              and DEVANAGARI.search(n.symbol_hi) for n in N))

    print("\n2. 108 padas, 108 syllables, 9 per sign")
    syl = [(n.index, p, d) for n in N for p, (d, _) in enumerate(n.syllables, 1)]
    check("4 syllables per nakshatra, 108 in all",
          all(len(n.syllables) == 4 for n in N) and len(syl) == 108)
    check("every Devanagari syllable is distinct (no traditional repeats in this list)",
          len({d for *_, d in syl}) == 108)
    check("the lookup table maps all 108 padas exactly once",
          sorted(namakshar.TABLE.values()) == sorted((i, p) for i, p, _ in syl))
    check("every syllable looks itself up", all(
        (namakshar.lookup(d).nakshatra.index, namakshar.lookup(d).pada) == (i, p)
        for i, p, d in syl))
    # Latin transliterations collide by design (Ta = टा / ता); the dropdown
    # exists for that. Pin the known set so a new collision is noticed.
    latin: dict[str, list[str]] = {}
    for n in N:
        for d, lat in n.syllables:
            latin.setdefault(lat, []).append(d)
    repeats = {k for k, v in latin.items() if len(v) > 1}
    check("Latin repeats are exactly the known ट/त, ड/द, ध/ढ, ठ/थ, ण/न ones",
          repeats == {"Ta", "Ti", "Tu", "Te", "To", "Da", "Di", "Du", "De", "Do", "Dha", "Tha",
                      "Na"},
          str(sorted(repeats)))
    check("Abhijit syllables do not collide with the 108",
          not set(namakshar.ABHIJIT_KEYS) & set(namakshar.TABLE))
    covered = []
    for s in range(12):
        padas = namakshar.sign_padas(s)
        check(f"{SIGNS[s]}: 9 padas", len(padas) == 9)
        for n, p in padas:
            if n.pada_sign(p) != s:
                check(f"{n.name} {p} lies in {SIGNS[s]}", False)
        covered += [(n.index, p) for n, p in padas]
    check("the 12 signs cover the 108 padas exactly once",
          sorted(covered) == sorted((i, p) for i, p, _ in syl))
    for n in N:
        lon = namakshar.pada_longitude(n.index, 1)
        nak = matching.nakshatra_at(lon)
        if (nak["name"], nak["pada"]) != (n.name, 1):
            check(f"{n.name}: pada midpoint reads back through matching.nakshatra_at", False)
    check("pada midpoints read back through matching.nakshatra_at",
          not any("reads back" in f for f in failures))
    check("Krittika spans Mesh and Vrishabh; Chitra spans Kanya and Tula",
          N[2].signs == [0, 1] and N[13].signs == [5, 6])

    print("\n3. Trait texts")
    fear = re.compile(r"\b(death|disease|die|accident|guarantee|curse|evil|unlucky)\b|मृत्यु|रोग|अशुभ",
                      re.I)
    for name, bank, keys in (("NAKSHATRA_TRAITS", NAKSHATRA_TRAITS, [n.slug for n in N]),
                             ("RASHI_TRAITS", RASHI_TRAITS, [r.slug for r in RASHIS])):
        check(f"{name}: one entry per slug", sorted(bank) == sorted(keys))
        for k, v in bank.items():
            words = len(v["en"].split())
            if not 80 <= words <= 150:
                check(f"{name}[{k}] English is 80–150 words", False, str(words))
            if not (DEVANAGARI.search(v["hi"]) and 60 <= len(v["hi"].split()) <= 180):
                check(f"{name}[{k}] Hindi text present", False)
            if fear.search(v["en"]) or fear.search(v["hi"]):
                check(f"{name}[{k}] avoids fear words", False)
        check(f"{name}: lengths, Hindi and tone", not any(name in f for f in failures))

    print("\n4. Every page, both languages")
    for lang in npg.LANGS:
        for n in (None, *N):
            path = npg.nak_path(n, lang)
            must = ["नक्षत्र" if lang == "hi" else "Nakshatra"]
            if n:
                must += [n.name_hi if lang == "hi" else n.name, n.syllables[0][0],
                         f'href="{"/hi" if lang == "hi" else ""}/rashifal/'
                         f'{RASHIS[n.signs[0]].slug}"']
            html = seo_tests.common(path, path, path, must)
            pair_checks(path, npg.nak_path(n, "en"), npg.nak_path(n, "hi"), lang, html)
            check(f"{path}: kundali CTA", 'class="cta" href="/?open=kundali"' in html)
            check(f"{path}: today's nakshatra box", "New Delhi" in html or "नई दिल्ली" in html)
        for r in (None, *RASHIS):
            path = npg.rashi_path(r, lang)
            must = ["राशि" if lang == "hi" else "Rashi"]
            if r:
                must += [r.name_hi if lang == "hi" else r.english,
                         f'href="{"/hi" if lang == "hi" else ""}/rashifal/{r.slug}"']
            html = seo_tests.common(path, path, path, must)
            pair_checks(path, npg.rashi_path(r, "en"), npg.rashi_path(r, "hi"), lang, html)
            if r:
                for n, _ in namakshar.sign_padas(r.index):
                    if f'href="{npg.nak_path(n, lang)}"' not in html:
                        check(f"{path}: links {n.name}", False)
    titles = {title(client.get(p).text) for p in npg.sitemap_paths()}
    # 42 per TRANSLATED language (en, hi; + ta, ml since DIVASTRO-123)
    total = 42 * len(npg.TRANSLATED)
    check(f"titles are unique across all {total} pages", len(titles) == total, str(len(titles)))

    print("\n5. Facts on the page")
    html = client.get("/nakshatra/ashwini").text
    check("Ashwini: Ketu, Deva, Horse, Adi, span 0°00′–13°20′ Mesh",
          all(x in html for x in ("Ketu", "Deva", "Horse", "Adi", "0°00′ Mesh (Aries) – 13°20′ Mesh (Aries)")))
    html = client.get("/nakshatra/krittika").text
    check("Krittika span crosses into Vrishabh",
          "26°40′ Mesh (Aries) – 10°00′ Vrishabh (Taurus)" in html)
    html = client.get("/nakshatra/revati").text
    check("Revati ends at 30°00′ Meen", "30°00′ Meen (Pisces)" in html)
    html = client.get("/hi/nakshatra/ashwini").text
    check("Hindi Ashwini: केतु, देव, चु चे चो ला",
          all(x in html for x in ("केतु", "देव", "चु चे चो ला")))
    html = client.get("/rashi/mesh").text
    check("Mesh: Mars, Fire, Movable, Ashwini/Bharani/Krittika 1",
          all(x in html for x in ("Mars", "Fire", "Movable", "/nakshatra/ashwini",
                                  "/nakshatra/bharani", "/nakshatra/krittika")))
    real = npg._today
    npg._today = lambda: dt.date(2026, 10, 3)
    try:
        t = npg.today_nakshatra(dt.date(2026, 10, 3))
        check("today's nakshatra computed", t is not None)
        if t:
            own = client.get(npg.nak_path(t, "en")).text
            other = next(n for n in N if n != t)
            check("today's own page says the Moon is in it",
                  f"Today the Moon is in {t.name}" in own)
            check("another page names today's nakshatra with a link",
                  f'href="/nakshatra/{t.slug}"><strong>{t.name}' in
                  client.get(npg.nak_path(other, "en")).text)
    finally:
        npg._today = real

    print("\n6. Redirects and 404s")
    for src, dst in (("/nakshatra/aswini", "/nakshatra/ashwini"),
                     ("/hi/nakshatra/moola", "/hi/nakshatra/mula"),
                     ("/nakshatra/purvaphalguni", "/nakshatra/purva-phalguni"),
                     ("/rashi/aries", "/rashi/mesh"), ("/hi/rashi/Pisces", "/hi/rashi/meen")):
        resp = client.get(src, follow_redirects=False)
        check(f"{src} → 301 {dst}", resp.status_code == 301 and resp.headers["location"] == dst,
              f"{resp.status_code} {resp.headers.get('location')}")
        check(f"beacon rejects alias {src}", not analytics.is_public_page(src))
    for bad in ("/nakshatra/atlantis", "/hi/rashi/atlantis"):
        resp = client.get(bad)
        check(f"{bad} is a non-cacheable 404",
              resp.status_code == 404 and resp.headers.get("cache-control") == "no-store")
        check(f"beacon rejects {bad}", not analytics.is_public_page(bad))

    print("\n7. Wiring: sitemap, beacon, share, cross-links")
    root = ET.fromstring(client.get("/sitemap.xml").content)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [e.text for e in root.findall("s:url/s:loc", ns)]
    want = {SITE + p for p in npg.sitemap_paths()}
    check(f"sitemap lists all {42 * len(npg.TRANSLATED)} DIVASTRO-115 URLs",
          len(want) == 42 * len(npg.TRANSLATED) and want <= set(locs),
          str(sorted(want - set(locs))[:5]))
    check("sitemap has no duplicates", len(locs) == len(set(locs)))
    check("beacon still accepts /rashifal/mesh and rejects /rashi-foo",
          analytics.is_public_page("/rashifal/mesh") and not analytics.is_public_page("/rashi-foo"))
    for p in ("/nakshatra", "/hi/nakshatra/revati", "/rashi/kumbh", "/naam-se-kundali-milan",
              "/hi/naam-se-kundali-milan"):
        check(f"beacon accepts {p}", analytics.is_public_page(p))
        check(f"share text for {p}", bool(share.seo_share_text(p)))
    check("no share text for an unknown nakshatra", share.seo_share_text("/nakshatra/x") is None)
    check("rashifal sign page links its rashi page",
          'href="/rashi/mesh"' in client.get("/rashifal/mesh").text
          and 'href="/hi/rashi/meen"' in client.get("/hi/rashifal/meen").text)
    check("kundali-milan explainer links naam milan",
          'href="/naam-se-kundali-milan"' in client.get("/kundali-milan").text
          and 'href="/hi/naam-se-kundali-milan"' in client.get("/hi/kundali-milan").text)
    check("canonical of /hi/rashi is itself",
          canonical(client.get("/hi/rashi").text) == SITE + "/hi/rashi")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("nakshatra & rashi pages: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
