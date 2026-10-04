"""DIVASTRO-123: the server-rendered SEO pages in Kannada and Telugu.

Two halves:

1. The text tables (app/*_text.py, i18n.CHROME): every table has a "kn" and a
   "te" entry with every English key, the same {placeholders} (any the en / hi /
   _native value of that key uses, or a names_<code> label), no Devanagari, and
   the language's own script.
2. The pages: /kn/... and /te/... of every module are indexable (no noindex, no
   "translation coming soon" note), listed in sitemap.xml, carry reciprocal
   hreflang with the English and Hindi copies, and their visible body text is
   written in Kannada (U+0C80-0CFF) / Telugu (U+0C00-0C7F) - no run of English
   words left over.

    ~/.venvs/divineastro/bin/python -u -m tests.test_seo_kn_te
"""

from __future__ import annotations

import html as htmlmod
import os
import re
import string
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_knte_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import (i18n, muhurat_pages, muhurat_text, naam_milan_text,  # noqa: E402
                 nakshatra_page_text, nakshatra_pages, nakshatra_text, rashifal_pages,
                 rashifal_text, seo_cities, seo_pages, seo_text, vrat_pages, vrat_text)
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
LANGS = ("kn", "te")
SCRIPT = {"kn": (0x0C80, 0x0CFF), "te": (0x0C00, 0x0C7F)}
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
MODULES = {"seo_pages": seo_pages, "rashifal_pages": rashifal_pages, "vrat_pages": vrat_pages,
           "nakshatra_pages": nakshatra_pages, "muhurat_pages": muhurat_pages}

# English page paths, one or more per page type.
PAGES = [
    "/panchang", "/panchang/bengaluru", "/panchang/hyderabad", "/rahu-kaal", "/rahu-kaal/bengaluru",
    "/rahu-kaal/hyderabad", "/choghadiya", "/choghadiya/chennai", "/kundali-milan", "/free-kundali",
    "/rashifal", "/rashifal/mesh", "/rashifal/kanya", "/vrat-tyohar", "/vrat-tyohar/2026",
    "/vrat-tyohar/hyderabad", "/ekadashi-2026", "/tyohar/diwali-2026",
    "/muhurat/vivah-2026", "/muhurat/griha-pravesh-2026",
    "/nakshatra", "/nakshatra/ashwini", "/nakshatra/revati", "/rashi", "/rashi/mesh",
    "/naam-se-kundali-milan",
]
# Rendered too (body text checked) but not in the sitemap / not indexable.
EXTRA = ["/naam-se-kundali-milan?boy=Rahul&girl=Priya"]


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def fields(s: str) -> set[str]:
    out = set()
    for _, name, _, _ in string.Formatter().parse(s):
        if name:
            out.add(name.split(".")[0].split("[")[0].split(":")[0])
    return out


def in_script(s: str, lang: str) -> bool:
    lo, hi = SCRIPT[lang]
    return any(lo <= ord(c) <= hi for c in s)


def latin_words(s: str) -> int:
    return len(re.findall(r"[A-Za-z]{2,}", s))


def check_strings(label: str, lang: str, values: dict, en: dict, allowed: dict | None = None) -> None:
    """values ⊇ en's keys; placeholders allowed; no Devanagari; own script where there are words."""
    missing = sorted(set(en) - set(values), key=str)
    check(f"{label}[{lang}]: all {len(en)} English keys", not missing, str(missing[:8]))
    globs = set(i18n._name_vars(lang))
    # A page's builder passes the same values to all of its keys ("p.title",
    # "p.sub" ...): a placeholder another key of the same page uses is fine.
    page = {}
    for k, v in en.items():
        if isinstance(v, str):
            page.setdefault(str(k).split(".")[0], set()).update(fields(v))
    for k, v in (allowed or {}).items():
        page.setdefault(str(k).split(".")[0], set()).update(v)
    bad_ph, deva, no_script = [], [], []
    for k, v in values.items():
        if not isinstance(v, str):
            continue
        ok_ph = (set(globs) | fields(en.get(k, "")) | (allowed or {}).get(k, set())
                 | (page.get(str(k).split(".")[0], set()) if "." in str(k) else set()))
        if not fields(v) <= ok_ph:
            bad_ph.append((k, sorted(fields(v) - ok_ph)))
        if DEVANAGARI.search(v):
            deva.append(k)
        bare = re.sub(r"<[^>]+>|\{[^}]*\}|&[a-z]+;|\bIST\b", " ", v)
        if latin_words(bare) and not in_script(bare, lang) and not str(k).endswith("_lang"):
            no_script.append(k)
    check(f"{label}[{lang}]: placeholders match", not bad_ph, str(bad_ph[:5]))
    check(f"{label}[{lang}]: no Devanagari", not deva, str(deva[:5]))
    check(f"{label}[{lang}]: written in its own script", not no_script, str(no_script[:5]))


def text_table(label: str, table: dict) -> None:
    allowed = {}
    for code in ("hi", "_native"):
        for k, v in table.get(code, {}).items():
            allowed.setdefault(k, set()).update(fields(v))
    for lang in LANGS:
        check(f"{label}: has {lang}", lang in table)
        check_strings(label, lang, table.get(lang, {}), table["en"], allowed)


def bank(label: str, table: dict) -> None:
    """{item: {"en": ..., "hi": ..., "kn": ...}}"""
    for lang in LANGS:
        vals = {k: e.get(lang) for k, e in table.items() if e.get(lang)}
        check_strings(label, lang, vals, {k: e["en"] for k, e in table.items()})


def tables() -> None:
    print("\n1. Text tables")
    text_table("seo_text.TEXT", seo_text.TEXT)
    text_table("rashifal_text.TEXT", rashifal_text.TEXT)
    text_table("vrat_text.TEXT", vrat_text.TEXT)
    text_table("muhurat_text.TEXT", muhurat_text.TEXT)
    text_table("nakshatra_page_text.TEXT", nakshatra_page_text.TEXT)
    text_table("naam_milan_text.TEXT", naam_milan_text.TEXT)
    text_table("i18n.CHROME", i18n.CHROME)
    text_table("vrat_text.ABOUT", vrat_text.ABOUT)
    text_table("vrat_text.NOTES", vrat_text.NOTES)
    text_table("rashifal_text.TONE_LABEL", rashifal_text.TONE_LABEL)
    for name in ("MOON_HOUSE", "SATURN_HOUSE", "JUPITER_HOUSE", "RAHU_HOUSE", "KETU_LINE"):
        bank(f"rashifal_text.{name}", getattr(rashifal_text, name))
    bank("nakshatra_text.NAKSHATRA_TRAITS", nakshatra_text.NAKSHATRA_TRAITS)
    bank("nakshatra_text.RASHI_TRAITS", nakshatra_text.RASHI_TRAITS)
    from app.astro import choghadiya, festivals, namakshar
    for lang in LANGS:
        rule = vrat_text.RULE.get(lang, {})
        check(f"vrat_text.RULE[{lang}]: every festivals.RULE_TEXT rule + amanta + ekadashi",
              set(festivals.RULE_TEXT) | {"amanta", "ekadashi"} <= set(rule))
        check(f"vrat_text.RULE[{lang}]: own script, no Devanagari",
              all(in_script(v, lang) and not DEVANAGARI.search(v) for v in rule.values()))
        check(f"choghadiya description_{lang} for all 7",
              all(in_script(i.get(f"description_{lang}", ""), lang) for i in choghadiya.CHOGHADIYA_INFO.values()))
        check(f"namakshar deity/symbol_{lang} for all 27",
              all(in_script(getattr(n, f"deity_{lang}"), lang) and in_script(getattr(n, f"symbol_{lang}"), lang)
                  for n in namakshar.NAKSHATRA_LIST))
        eng = naam_milan_text.ENGINE.get(lang, {})
        check(f"naam_milan_text.ENGINE[{lang}]: 4 band notes + convention note",
              {"band_note0", "band_note1", "band_note2", "band_note3", "convention_note"} <= set(eng)
              and all(in_script(v, lang) for v in eng.values()))
    for lang in LANGS:
        for label, table in (("seo_text.FAQ", seo_text.FAQ), ("rashifal_text.MORE_LINKS",
                                                              rashifal_text.MORE_LINKS)):
            got = table.get(lang, ())
            check(f"{label}[{lang}]: {len(table['en'])} entries", len(got) == len(table["en"]))
            flat = {str(i): " ".join(pair) for i, pair in enumerate(got)}
            check(f"{label}[{lang}]: own script, no Devanagari",
                  all(in_script(v, lang) and not DEVANAGARI.search(v) for v in flat.values()))


def body_text(html: str) -> list[str]:
    """The visible text nodes of <main>, without the picker, scripts and styles."""
    m = re.search(r"<main\b.*?</main>", html, re.S)
    s = m.group(0) if m else html
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r'<details class="lang-picker".*?</details>', " ", s, flags=re.S)
    return [t for t in (htmlmod.unescape(x).strip() for x in re.split(r"<[^>]+>", s)) if t]


# Latin text a translated page may still carry: the brand, place names (cities
# have no Kannada/Telugu names yet: seo_cities.name_<code>), units, the
# ephemeris, Latin-script names the user typed (naam milan).
_PLACES = sorted({c.name for c in seo_cities.CITIES} | {c.state for c in seo_cities.CITIES}
                 | {c.label for c in seo_cities.CITIES}, key=len, reverse=True)
ALLOWED_LATIN = re.compile("|".join([re.escape(p) for p in _PLACES]
                                    + [r"Divine Astro", r"\bIST\b", r"\bPDF\b", r"\bAI\b",
                                       r"\bRahul\b", r"\bPriya\b", r"Swiss Ephemeris"]))


def pages() -> None:
    print("\n2. Pages")
    sm = client.get("/sitemap.xml").text
    for en_path in PAGES:
        h_en = client.get(en_path).text
        want = None
        for lang in LANGS:
            path = i18n.localized_path(en_path, lang)
            r = client.get(path)
            h = r.text
            alts = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', h))
            alts_en = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', h_en))
            if want is None:
                want = alts_en
            ok = (r.status_code == 200 and re.search(r'<meta name="robots" content="noindex', h) is None
                  and "lp-notice" not in h and f'<html lang="{lang}' in h)
            check(f"{path}: 200, indexable, no notice", ok, str(r.status_code))
            check(f"{path}: hreflang reciprocal with {en_path}",
                  alts == alts_en and any(t.split("-")[0] == lang and u.endswith(path)
                                          for t, u in alts.items()) and
                  {"en", "hi", "kn", "te"} <= {k.split("-")[0] for k in alts}, str(alts))
            check(f"{path}: in sitemap.xml", f"<loc>{SITE}{path}</loc>" in sm)
            title = re.search(r"<title>(.*?)</title>", h, re.S).group(1)
            check(f"{path}: title in its script", in_script(title, lang)
                  and not DEVANAGARI.search(title), title)
            body_checks(path, h, lang)
    for en_path in EXTRA:
        for lang in LANGS:
            path = i18n.localized_path(en_path, lang)
            r = client.get(path)
            check(f"{path}: 200", r.status_code == 200)
            body_checks(path, r.text, lang, engine_notes=True)


def ENGINE_NOTES(h: str) -> set[str]:
    """The text of the result's engine-written koota notes (the koota table's
    last column). The verdict, band note and convention note are translated."""
    out = set()
    for cell in re.findall(r"<tr><td><strong>[^<]*</strong></td><td>[^<]*</td><td>([^<]*)</td></tr>", h):
        out.add(htmlmod.unescape(cell).strip())
    return out


def body_checks(path: str, h: str, lang: str, engine_notes: bool = False) -> None:
    """engine_notes: a naam-milan result (noindex) carries matching.ashtakoot's
    per-koota notes, which the engine writes in English or Hindi only
    (docs/i18n.md "APIs") - those nodes are left out here."""
    nodes = body_text(h)
    if engine_notes:
        notes = {strip for strip in ENGINE_NOTES(h)}
        nodes = [n for n in nodes if n not in notes]
    joined = " ".join(nodes)
    lo, hi = SCRIPT[lang]
    native = sum(1 for c in joined if lo <= ord(c) <= hi)
    latin = sum(1 for c in ALLOWED_LATIN.sub("", joined) if c.isascii() and c.isalpha())
    check(f"{path}: body mostly in its script", native > 4 * latin, f"{native} vs {latin} Latin")
    check(f"{path}: body has no Devanagari", not DEVANAGARI.search(joined),
          str(DEVANAGARI.findall(joined)[:5]))
    runs = [n for n in nodes
            if re.search(r"[A-Za-z]{2,}(?:[\s,.'’:;()–—-]+[A-Za-z]{2,}){3,}", ALLOWED_LATIN.sub("", n))]
    check(f"{path}: no run of English words in the body", not runs, str(runs[:3]))


def main() -> int:
    print("0. TRANSLATED")
    for name, mod in MODULES.items():
        check(f"{name}.TRANSLATED has kn and te", {"kn", "te"} <= set(mod.TRANSLATED))
    tables()
    pages()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("kn/te SEO pages: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
