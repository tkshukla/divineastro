"""DIVASTRO-123: the server-rendered pages in Tamil (ta) and Malayalam (ml).

Pins that the translation is complete and that the pages are switched on for
search engines:

1. Every text table has "ta" and "ml" entries covering every English key
   (TEXT dicts, FAQ, festival ABOUT/NOTES, nakshatra/rashi traits, rashifal
   phrase banks, ...), with no placeholder the builder does not supply.
2. The text is in its own script: no Devanagari, no other Indic script, and
   Latin only for a few fixed tokens (IST, PDF, AI, KP, D9 ...).
3. Every module lists ta and ml in TRANSLATED (katha does not).
4. A sample of pages per module, in ta and ml: 200, <html lang>, indexable
   (no noindex, no "translation coming soon"), reciprocal hreflang with the
   English page, listed in sitemap.xml, and no run of English words left in
   <main> (city and state names, which have no Tamil/Malayalam field yet,
   excepted).

    ~/.venvs/divineastro/bin/python -u -m tests.test_i18n_ta_ml
"""

from __future__ import annotations

import html as htmllib
import os
import re
import string
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_taml_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import (i18n, katha, muhurat_pages, muhurat_text, naam_milan_text,  # noqa: E402
                 nakshatra_page_text, nakshatra_pages, nakshatra_text, rashifal_pages,
                 rashifal_text, seo_cities, seo_pages, seo_text, vrat_pages, vrat_text)
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
LANGS = ("ta", "ml")
SCRIPT = {"ta": "TAMIL", "ml": "MALAYALAM"}
RANGE = {"ta": (0x0B80, 0x0BFF), "ml": (0x0D00, 0x0D7F)}
# Latin tokens a Tamil/Malayalam string may contain.
LATIN_OK = {"IST", "PDF", "AI", "KP", "N", "E", "WhatsApp", "Divine", "Astro", "B", "D", "Th", "Dh",
            "T", "b", "s", "S", "sh", "Sh", "v", "Swiss", "Ephemeris", "Lahiri", "UPI",
            "Ram", "Sita"}              # example names typed into the naam-milan form
LATIN_OK |= {f"D{n}" for n in (1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60)}
# Placeholders a template may use beyond those of the table's en/hi/_native
# templates (the builders pass a page's whole set of values to each key).
EXTRA_VARS = {
    "rashifal_text": {"local"},
}


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def placeholders(s: str) -> set[str]:
    return {f for _, f, _, _ in string.Formatter().parse(s) if f}


def visible(s: str) -> str:
    """A template's reader-visible text: no tags, no placeholders, entities decoded."""
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\{[^{}]*\}", " ", s)
    return htmllib.unescape(s)


def script_problems(s: str, lang: str) -> list[str]:
    text = visible(s)
    bad = []
    for c in text:
        if unicodedata.category(c)[0] not in "LM":
            continue
        name = unicodedata.name(c, "")
        if SCRIPT[lang] in name or "LATIN" in name:
            continue
        bad.append(c)
    latin = [w for w in re.findall(r"[A-Za-z]+", text) if w not in LATIN_OK]
    return ([f"foreign script {''.join(sorted(set(bad)))!r}"] if bad else []) + \
        ([f"Latin {latin[:5]}"] if latin else [])


def name_vars(lang: str) -> set[str]:
    return set(i18n.name_vars(lang))


# --------------------------------------------------------------------------
# 1 + 2. The tables
# --------------------------------------------------------------------------

def check_text_table(label: str, table: dict, module: str) -> None:
    """A {"en": {...}, "hi": {...}, "_native": {...}, "ta": {...}} TEXT table."""
    en = table["en"]
    for lang in LANGS:
        mine = table.get(lang, {})
        missing = sorted(k for k in en if not mine.get(k))
        check(f"{label}[{lang}]: all {len(en)} English keys", not missing, str(missing[:8]))
        bad_ph, bad_script = [], []
        allowed = name_vars(lang) | EXTRA_VARS.get(module, set())
        for code in ("en", "hi", i18n.NATIVE):
            for v in table.get(code, {}).values():
                if isinstance(v, str):
                    allowed |= placeholders(v)
        for key, value in mine.items():
            extra = placeholders(value) - allowed
            if extra:
                bad_ph.append(f"{key}: {sorted(extra)}")
            if value in i18n.CODES:          # e.g. rashifal's sub_lang: a language code
                continue
            probs = script_problems(value, lang)
            if probs and visible(value).strip():
                bad_script.append(f"{key}: {probs}")
            if re.search(r"&(?![a-z]+;|#\d+;)", value):
                bad_script.append(f"{key}: raw &")
        check(f"{label}[{lang}]: no unknown placeholder", not bad_ph, str(bad_ph[:5]))
        check(f"{label}[{lang}]: {SCRIPT[lang].title()} script only", not bad_script,
              str(bad_script[:5]))


def check_entries(label: str, entries: dict, keys: tuple = ()) -> None:
    """{x: {"en": ..., "hi": ...}} (traits, phrase banks): every x has ta/ml."""
    for lang in LANGS:
        missing = [x for x, row in entries.items() if not row.get(lang)]
        check(f"{label}: every entry has {lang}", not missing, str(missing[:5]))
        bad = []
        for x, row in entries.items():
            value = row.get(lang)
            if isinstance(value, str):
                extra = placeholders(value) - placeholders(row["en"]) - placeholders(row.get("hi", ""))
                probs = script_problems(value, lang)
                if extra or probs:
                    bad.append(f"{x}: {sorted(extra)} {probs}")
        check(f"{label}[{lang}]: placeholders and script", not bad, str(bad[:5]))


def check_per_lang(label: str, table: dict) -> None:
    """{"en": {x: text}, "hi": {...}} (festival ABOUT, NOTES): same x for ta/ml."""
    en = table["en"]
    for lang in LANGS:
        mine = table.get(lang, {})
        missing = sorted(x for x in en if not mine.get(x))
        check(f"{label}[{lang}]: all {len(en)} entries", not missing, str(missing[:6]))
        bad = []
        for x, value in mine.items():
            extra = placeholders(value) - placeholders(en.get(x, ""))
            probs = script_problems(value, lang)
            if extra or probs:
                bad.append(f"{x}: {sorted(extra)} {probs}")
        check(f"{label}[{lang}]: placeholders and script", not bad, str(bad[:5]))


def tables() -> None:
    print("\n1. Every table has ta and ml, complete and in script")
    check_text_table("seo_text.TEXT", seo_text.TEXT, "seo_text")
    for lang in LANGS:
        faq = seo_text.FAQ.get(lang, ())
        check(f"seo_text.FAQ[{lang}]: {len(seo_text.FAQ['en'])} Q&A pairs",
              len(faq) == len(seo_text.FAQ["en"]) and all(q and a for q, a in faq))
        bad = [q for q, a in faq if script_problems(q, lang) or script_problems(a, lang)]
        check(f"seo_text.FAQ[{lang}]: script", not bad, str(bad[:3]))

    check_text_table("rashifal_text.TEXT", rashifal_text.TEXT, "rashifal_text")
    for lang in LANGS:
        links = rashifal_text.MORE_LINKS.get(lang, ())
        check(f"rashifal_text.MORE_LINKS[{lang}]", bool(links)
              and all(not script_problems(text, lang) for _, text in links), str(links)[:200])
        tones = rashifal_text.TONE_LABEL.get(lang, {})
        check(f"rashifal_text.TONE_LABEL[{lang}]", set(tones) == set(rashifal_text.TONE_LABEL["en"])
              and all(not script_problems(v, lang) for v in tones.values()), str(tones))
    for name in ("MOON_HOUSE", "SATURN_HOUSE", "JUPITER_HOUSE", "RAHU_HOUSE", "KETU_LINE"):
        check_entries(f"rashifal_text.{name}", getattr(rashifal_text, name))

    check_text_table("vrat_text.TEXT", vrat_text.TEXT, "vrat_text")
    for name in ("ABOUT", "NOTES"):
        table = getattr(vrat_text, name)
        if "en" in table:
            check_per_lang(f"vrat_text.{name}", table)
        else:
            check_entries(f"vrat_text.{name}", table)

    check_text_table("muhurat_text.TEXT", muhurat_text.TEXT, "muhurat_text")
    check_text_table("nakshatra_page_text.TEXT", nakshatra_page_text.TEXT, "nakshatra_page_text")
    check_entries("nakshatra_text.NAKSHATRA_TRAITS", nakshatra_text.NAKSHATRA_TRAITS)
    check_entries("nakshatra_text.RASHI_TRAITS", nakshatra_text.RASHI_TRAITS)
    check_text_table("naam_milan_text.TEXT", naam_milan_text.TEXT, "naam_milan_text")


# --------------------------------------------------------------------------
# 3 + 4. The flags and the pages
# --------------------------------------------------------------------------

MODULES = {"seo_pages": seo_pages, "rashifal_pages": rashifal_pages, "vrat_pages": vrat_pages,
           "nakshatra_pages": nakshatra_pages, "muhurat_pages": muhurat_pages}
# English paths; every one exists in ta and ml.
PAGES = {
    "seo_pages": ["/panchang", "/panchang/chennai", "/panchang/kochi", "/rahu-kaal/chennai",
                  "/rahu-kaal/kochi", "/choghadiya/madurai", "/kundali-milan", "/free-kundali"],
    "rashifal_pages": ["/rashifal", "/rashifal/mesh", "/rashifal/meen"],
    "vrat_pages": ["/vrat-tyohar", "/vrat-tyohar/2026", "/vrat-tyohar/chennai", "/ekadashi-2026",
                   "/tyohar/diwali-2026", "/tyohar/navratri-2026", "/tyohar/janmashtami-2026"],
    "nakshatra_pages": ["/nakshatra", "/nakshatra/ashwini", "/nakshatra/shravana", "/rashi",
                        "/rashi/mesh", "/naam-se-kundali-milan"],
    "muhurat_pages": ["/muhurat/vivah-2026", "/muhurat/griha-pravesh-2026"],
}

# Place names have no Tamil/Malayalam field yet (seo_cities name_<code>):
# they may stay in Latin script. Built once from the city list.
PLACE_WORDS = {w for c in seo_cities.CITIES for w in re.findall(r"[A-Za-z]+", f"{c.name} {c.state}")}
PLACE_WORDS |= {"India", "Delhi", "New"}


def main_text(page: str) -> str:
    m = re.search(r"<main[^>]*>(.*)</main>", page, re.S)
    body = m.group(1) if m else page
    body = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", body, flags=re.S)
    body = re.sub(r'<details class="lang-picker".*?</details>', " ", body, flags=re.S)
    return htmllib.unescape(re.sub(r"<[^>]+>", " ", body))


def english_runs(text: str) -> list[str]:
    """Runs of 3+ Latin words that are not place names or allowed tokens."""
    runs = re.findall(r"[A-Za-z][A-Za-z'’]*(?:[\s,.:;()/–—-]+[A-Za-z][A-Za-z'’]*){2,}", text)
    return [r for r in runs
            if [w for w in re.findall(r"[A-Za-z]+", r) if w not in PLACE_WORDS | LATIN_OK]]


def alternates(page: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', page))


def pages() -> None:
    print("\n3. TRANSLATED")
    for name, mod in MODULES.items():
        check(f"{name}.TRANSLATED has ta and ml", {"en", "hi", "ta", "ml"} <= set(mod.TRANSLATED),
              str(sorted(mod.TRANSLATED)))
    check("katha stays en/hi", not ({"ta", "ml"} & set(katha.TRANSLATED)))

    print("\n4. Pages: indexable, reciprocal hreflang, in the sitemap, no English left")
    sitemap = client.get("/sitemap.xml").text
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sitemap))
    for name, en_paths in PAGES.items():
        for en_path in en_paths:
            en_alts = alternates(client.get(en_path).text)
            for lang in LANGS:
                path = i18n.localized_path(en_path, lang)
                r = client.get(path)
                h = r.text
                problems = []
                if r.status_code != 200:
                    problems.append(f"status {r.status_code}")
                if not re.search(rf'<html lang="{lang}', h):
                    problems.append("html lang")
                if re.search(r'<meta name="robots" content="noindex', h):
                    problems.append("noindex")
                if "lp-notice" in h:
                    problems.append("coming-soon notice")
                alts = alternates(h)
                regional = any(k.endswith("-IN") for k in alts)
                want_self = SITE + path
                if alts.get(f"{lang}-IN" if regional else lang) != want_self:
                    problems.append(f"no self hreflang ({sorted(alts)})")
                if en_alts.get(f"{lang}-IN" if regional else lang) != want_self:
                    problems.append("English page does not list it")
                if alts != en_alts:
                    problems.append("hreflang sets differ from the English page")
                if want_self not in locs:
                    problems.append("not in sitemap")
                text = main_text(h)
                runs = english_runs(text)
                if runs:
                    problems.append(f"English left: {runs[:3]}")
                if re.search(r"[ऀ-ॿ]", text):
                    problems.append("Devanagari in body")
                lo, hi = RANGE[lang]
                if sum(lo <= ord(c) <= hi for c in text) < 200:
                    problems.append("too little text in the script")
                check(f"{name}: {path}", not problems, "; ".join(problems))
    # A naam-milan query result is a noindex tool page; it must still render.
    for lang in LANGS:
        r = client.get(f"/{lang}/naam-se-kundali-milan?boy=Ram&girl=Sita")
        check(f"/{lang}/naam-se-kundali-milan?boy=…: 200", r.status_code == 200)


def main() -> int:
    tables()
    pages()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("ta/ml: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
