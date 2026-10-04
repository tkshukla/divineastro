"""DIVASTRO-123: the server-rendered SEO pages in Bengali (bn) and Odia (or).

1. Tables: every per-language table of the text modules has a "bn" and an "or"
   entry with all the "en" keys (and the hi-only keys), the same {placeholders},
   no Devanagari, and its own script (Bengali U+0980-09FF, Odia U+0B00-0B7F).
2. Pages: /bn/... and /or/... copies are indexable (no noindex, no
   "translation coming soon" note), in the sitemap, listed in reciprocal
   hreflang on every copy, written in their script, and carry no run of
   English words in the body (brand, URLs and numbers allowed).

    ~/.venvs/divineastro/bin/python -u -m tests.test_i18n_bn_or
"""

from __future__ import annotations

import html as htmllib
import os
import re
import string
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if "ASTRO_DATABASE_URL" not in os.environ:
    _tmp = tempfile.mkdtemp(prefix="astro_bnor_")
    os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import (i18n, muhurat_pages, seo_cities, muhurat_text, naam_milan_text,  # noqa: E402
                 nakshatra_page_text, nakshatra_pages, nakshatra_text, rashifal_pages,
                 rashifal_text, seo_pages, seo_text, vrat_pages, vrat_text)
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
LANGS = ("bn", "or")
SCRIPT = {"bn": (0x0980, 0x09FF), "or": (0x0B00, 0x0B7F)}
TEXT_MODULES = (seo_text, rashifal_text, vrat_text, muhurat_text, nakshatra_page_text,
                nakshatra_text, naam_milan_text)
PAGE_MODULES = {"seo_pages": seo_pages, "rashifal_pages": rashifal_pages,
                "vrat_pages": vrat_pages, "muhurat_pages": muhurat_pages,
                "nakshatra_pages": nakshatra_pages}

# English paths fetched as /bn/... and /or/...: every page of the sitemap
# (city pages only for Kolkata and Bhubaneswar), katha excepted.
OUR_CITIES = ("kolkata", "bhubaneswar")
MODULE_ROOTS = ("/panchang", "/rahu-kaal", "/choghadiya", "/kundali-milan", "/free-kundali",
                "/rashifal", "/vrat-tyohar", "/ekadashi-", "/tyohar/", "/muhurat/", "/nakshatra",
                "/rashi", "/naam-se-kundali-milan")


def en_pages() -> list[str]:
    slugs = {c.slug for c in seo_cities.CITIES}
    out = []
    for p in seo_pages.sitemap_paths():
        if i18n.strip_prefix(p)[0] != "en" or not p.startswith(MODULE_ROOTS):
            continue
        last = p.rstrip("/").rsplit("/", 1)[-1]
        if last in slugs and last not in OUR_CITIES:
            continue
        out.append(p)
    return out


# Indexable copies need not be the only ones checked for English text.
NOINDEX_PAGES = ["/naam-se-kundali-milan?boy=Rahul&girl=Priya"]
# Latin words allowed inside a body (brand, products, URL-ish tokens).
ALLOWED_LATIN = re.compile(r"\b(?:Divine\s*Astro|divineastro\.org|WhatsApp|Swiss\s+Ephemeris|"
                           r"PDF|IST|UPI)\b|https?://\S+|\S+@\S+")
# Values the builders pass in the page language: {city} (seo_pages._city_vars),
# {local} (the rashi in the page script) and {tone} (rashifal_pages).
NATIVE_FIELDS = {"city", "local", "tone"}
# hi-only keys a language may leave out ("home" falls back to i18n.CHROME).
OPTIONAL_KEYS = {"home"}
# Four or more Latin words in a row on one line: an English phrase. (A name such
# as "Uttara Bhadrapada Nakshatra" in a subtitle, or a syllable "Chu", is fine.)
LATIN_RUN = re.compile(r"\b[A-Za-z][A-Za-z'’]*(?:(?:[^\S\n]+|[^\S\n]*[,:;\-–—/&()]+[^\S\n]*)"
                       r"[A-Za-z][A-Za-z'’]*){3,}")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def fields(s: str) -> set[str]:
    return {f for _, f, _, _ in string.Formatter().parse(s) if f is not None}


def has_script(s: str, lang: str) -> bool:
    lo, hi = SCRIPT[lang]
    return any(lo <= ord(c) <= hi for c in s)


def devanagari(s: str) -> bool:
    """Devanagari letters; the danda । ॥ (U+0964/5) is shared by Bengali and Odia."""
    return any(0x0900 <= ord(c) <= 0x097F and c not in "\u0964\u0965" for c in s)


def lang_tables(obj, path: str):
    """Every dict below `obj` that is keyed by language ("en" and "hi")."""
    if isinstance(obj, dict):
        if "en" in obj and "hi" in obj:
            yield path, obj
            return
        for k, v in obj.items():
            yield from lang_tables(v, f"{path}[{k!r}]")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from lang_tables(v, f"{path}[{i}]")


def compare(path: str, ref, got, lang: str, problems: list[str], hi=None) -> None:
    """`got` (the bn/or value) has the shape, keys and placeholders of `ref`."""
    if isinstance(ref, str):
        if not isinstance(got, str) or not got:
            problems.append(f"{path}: missing/empty")
            return
        # The en placeholders; a translation may drop one that would print English
        # or Devanagari ({name_hi}, {city_hi}, {desc}) and use what hi uses or the
        # native {city} instead — never invent one.
        allowed = fields(ref) | (fields(hi) if isinstance(hi, str) else set()) | NATIVE_FIELDS
        if not fields(got) <= allowed:
            problems.append(f"{path}: placeholders {sorted(fields(got) - allowed)} not in en/hi")
        if devanagari(got):
            problems.append(f"{path}: Devanagari")
        bare = re.sub(r"<[^>]+>|\{[^}]*\}|&\w+;", "", got)
        code_like = re.fullmatch(r"[\w/.:#?=&-]*", got) is not None   # a path, a language code
        if (re.search(r"[^\W\d_]", bare) and not has_script(bare, lang) and not code_like
                and got != hi and not ALLOWED_LATIN.fullmatch(bare.strip())):
            problems.append(f"{path}: not in {lang} script: {got[:60]!r}")
        if "&" in re.sub(r"&(?:\w+|#\d+);", "", got) and "<" in ref:
            problems.append(f"{path}: unescaped & in HTML")
    elif isinstance(ref, dict):
        if not isinstance(got, dict):
            problems.append(f"{path}: not a dict")
            return
        for k, v in ref.items():
            if k not in got:
                problems.append(f"{path}[{k!r}]: missing")
            else:
                compare(f"{path}[{k!r}]", v, got[k], lang, problems,
                        hi.get(k) if isinstance(hi, dict) else None)
    elif isinstance(ref, (list, tuple)):
        if not isinstance(got, (list, tuple)) or len(got) != len(ref):
            problems.append(f"{path}: length {len(got) if hasattr(got, '__len__') else '?'} != {len(ref)}")
            return
        for i, (a, b) in enumerate(zip(ref, got)):
            compare(f"{path}[{i}]", a, b, lang, problems,
                    hi[i] if isinstance(hi, (list, tuple)) and len(hi) == len(ref) else None)


def body_text(page: str) -> str:
    page = re.sub(r"(?s)<head>.*?</head>|<script.*?</script>|<style.*?</style>", " ", page)
    page = re.sub(r'(?s)<details class="lang-picker".*?</details>', " ", page)
    page = re.sub(r'(?s)<p class="legal-entity">.*?</p>', " ", page)
    page = re.sub(r"<[^>]+>", "\n", page)
    return htmllib.unescape(page)


# City and state names stay English until seo_cities has bn/or spellings.
PLACE_NAMES = re.compile("|".join(sorted(
    {re.escape(c.name) for c in seo_cities.CITIES} | {re.escape(c.state) for c in seo_cities.CITIES},
    key=len, reverse=True)))


def latin_runs(text: str) -> list[str]:
    text = PLACE_NAMES.sub(" ", ALLOWED_LATIN.sub(" ", text))
    # A list of Latin letters ("T, D, N, Th, Dh" in the naam milan explainer) is not a phrase.
    return [m.group(0) for m in LATIN_RUN.finditer(text)
            if any(len(w) > 2 for w in re.findall(r"[A-Za-z'’]+", m.group(0)))]


def alternates(page: str) -> dict[str, str]:
    """hreflang -> href; a regional code (bn-IN, used by the region=True pages)
    is read as its language."""
    return {code.removesuffix("-IN"): href for code, href in
            re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', page)}


def main() -> int:
    print("\n1. Tables: bn and or entries with every en key and the same placeholders")
    for mod in TEXT_MODULES:
        for name in dir(mod):
            if not name.isupper():
                continue
            for path, table in lang_tables(getattr(mod, name), f"{mod.__name__.split('.')[-1]}.{name}"):
                for lang in LANGS:
                    problems: list[str] = []
                    if lang not in table:
                        problems.append(f"{path}: no {lang!r} entry")
                    else:
                        compare(f"{path}[{lang!r}]", table["en"], table[lang], lang, problems,
                                table["hi"])
                        # keys only Hindi has (word forms the builder asks for)
                        if isinstance(table["hi"], dict) and isinstance(table["en"], dict):
                            for k in set(table["hi"]) - set(table["en"]) - OPTIONAL_KEYS:
                                if k not in table[lang]:
                                    problems.append(f"{path}[{lang!r}][{k!r}]: hi-only key missing")
                                else:
                                    compare(f"{path}[{lang!r}][{k!r}]", table["hi"][k], table[lang][k],
                                            lang, problems)
                    check(f"{path} {lang}", not problems, "; ".join(problems[:5]))

    from app.astro import festivals
    from app.astro.namakshar import BY_SLUG as NAK_BY_SLUG
    want_rule = ({"tithi", "month"} | {f"rule.{k}" for k in festivals.RULE_TEXT}
                 | {f"key.{k}" for k in ("ekadashi", "makar_sankranti", "lohri", "holi")})
    for lang in LANGS:
        rule = vrat_text.RULE.get(lang, {})
        check(f"vrat_text.RULE {lang}: every festivals.RULE_TEXT kind + the four own-worded rules",
              set(rule) == want_rule and not any(devanagari(v) for v in rule.values())
              and all(has_script(v, lang) for k, v in rule.items() if k != "tithi"),
              str(want_rule ^ set(rule)))
        for field in ("deity", "symbol"):
            local = nakshatra_text.NAKSHATRA_LOCAL[field].get(lang, {})
            check(f"nakshatra_text.NAKSHATRA_LOCAL {field} {lang}: all 27, in script",
                  set(local) == set(NAK_BY_SLUG) and all(has_script(v, lang) for v in local.values()))
        check(f"nakshatra_text.SYLLABLE_SCRIPT {lang}: namakshar syllables in script",
              all(has_script(nakshatra_pages._syl(d, lang), lang)
                  and not devanagari(nakshatra_pages._syl(d, lang))
                  for n in NAK_BY_SLUG.values() for d, _ in n.syllables))

    print("\n2. Every page module: bn and or translated (katha not)")
    for name, mod in PAGE_MODULES.items():
        check(f"{name}.TRANSLATED has bn, or", {"bn", "or"} <= set(mod.TRANSLATED), str(mod.TRANSLATED))
    from app import katha
    check("katha stays en/hi", set(katha.TRANSLATED) == {"en", "hi"})

    print("\n3. Pages: indexable, reciprocal hreflang, in the sitemap, in script, no English")
    sitemap = client.get("/sitemap.xml").text
    pages = en_pages()
    print(f"  ({len(pages)} English paths)")
    for en_path in pages:
        en_alts = alternates(client.get(en_path).text)
        for lang in LANGS:
            path = i18n.localized_path(en_path, lang)
            r = client.get(path)
            page = r.text
            problems = []
            if r.status_code != 200:
                problems.append(f"status {r.status_code}")
            if re.search(r'<meta name="robots" content="noindex', page):
                problems.append("noindex")
            if "lp-notice" in page:
                problems.append("translation notice shown")
            if not re.search(rf'<html lang="{lang}', page):
                problems.append("html lang")
            alts = alternates(page)
            for code in ("en", "hi", "bn", "or"):
                want = SITE + i18n.localized_path(en_path, code)
                if alts.get(code) != want or en_alts.get(code) != want:
                    problems.append(f"hreflang {code}: {alts.get(code)} / en copy {en_alts.get(code)}")
            if f"<loc>{SITE}{path}</loc>" not in sitemap:
                problems.append("not in sitemap")
            m = re.search(r"<title>([^<]*)</title>", page)
            title = htmllib.unescape(m.group(1)) if m else ""
            if not has_script(title, lang) or devanagari(title):
                problems.append(f"title not in script: {title!r}")
            text = body_text(page)
            if devanagari(text):
                problems.append("Devanagari in body: " + "".join(c for c in text if devanagari(c))[:20])
            native = sum(1 for c in text if has_script(c, lang))
            latin = sum(1 for c in PLACE_NAMES.sub("", ALLOWED_LATIN.sub("", text))
                        if c.isascii() and c.isalpha())
            if native < 10 * max(latin, 1):
                problems.append(f"script ratio native={native} latin={latin}")
            runs = latin_runs(text)
            if runs:
                problems.append(f"English in body: {runs[:3]}")
            check(f"{path}  [{title[:70]}]", not problems, "; ".join(problems[:4]))
    # Result pages (query string) are noindex; their koota notes come from the
    # matching engine (English/Hindi only), so only check they render.
    for en_path in NOINDEX_PAGES:
        for lang in LANGS:
            path = i18n.localized_path(en_path, lang)
            r = client.get(path)
            check(f"{path}: 200, noindex", r.status_code == 200
                  and 'content="noindex' in r.text)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("bn/or SEO pages: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
