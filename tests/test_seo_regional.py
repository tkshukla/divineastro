"""DIVASTRO-123: the server-rendered SEO pages in the six regional languages.

Kannada (kn), Telugu (te), Tamil (ta), Malayalam (ml), Bengali (bn) and Odia
(or), one parametrised suite (it replaces the three per-pair suites the
translation branches added: test_seo_kn_te, test_i18n_ta_ml, test_i18n_bn_or,
and keeps every one of their checks, now run for all six):

1. Text tables (app/*_text.py, i18n.CHROME): every table has every language
   with every English key, the same {placeholders} (those of the en / hi /
   _native value, a names_<code> label, or a value the builder passes in the
   page language), no Devanagari, no other Indic script, the language's own
   script, Latin only for a few fixed tokens (IST, PDF, D9 ...). The generic
   walk checks the shape of every nested en/hi table too.
2. The shared hooks: nakshatra_text.FACTS (deity/symbol of all 27),
   i18n.akshar (the 108 namakshar syllables in the script), vrat_text.RULES
   ("how the date is fixed"), choghadiya description_<code>, naam_milan_text
   .ENGINE, and the native city / state names (seo_city_names).
3. TRANSLATED: every page module has the six (katha does not).
4. Pages: /<code>/... of every module (a sample, plus every sitemap page for
   two of the language's own cities) are 200, indexable (no noindex, no
   "translation coming soon"), carry reciprocal hreflang with the English copy
   listing every translated language, are in sitemap.xml, have a title in the
   script, and a <main> written in the script: no Devanagari, no run of
   English words (city and state names included: they are native now).
5. Native city names (DIVASTRO-123): the title, H1, breadcrumb (and its
   JSON-LD), the date line and the city index of a city page name the city in
   the page's script, never in English; URLs keep the English slug.

    ~/.venvs/divineastro/bin/python -u -m tests.test_seo_regional          # all six
    ~/.venvs/divineastro/bin/python -u -m tests.test_seo_regional ta ml    # some
"""

from __future__ import annotations

import html as htmlmod
import json
import os
import re
import string
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if "ASTRO_DATABASE_URL" not in os.environ:
    _tmp = tempfile.mkdtemp(prefix="astro_regional_")
    os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import (i18n, katha, muhurat_pages, muhurat_text, naam_milan_text,  # noqa: E402
                 nakshatra_page_text, nakshatra_pages, nakshatra_text, rashifal_pages,
                 rashifal_text, seo_cities, seo_city_names, seo_pages, seo_text, vrat_pages,
                 vrat_text)
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
ALL = ("kn", "te", "ta", "ml", "bn", "or")
LANGS = tuple(a for a in sys.argv[1:] if a in ALL) or ALL
RANGE = {"kn": (0x0C80, 0x0CFF), "te": (0x0C00, 0x0C7F), "ta": (0x0B80, 0x0BFF),
         "ml": (0x0D00, 0x0D7F), "bn": (0x0980, 0x09FF), "or": (0x0B00, 0x0B7F)}
SCRIPT = {"kn": "KANNADA", "te": "TELUGU", "ta": "TAMIL", "ml": "MALAYALAM", "bn": "BENGALI",
          "or": "ORIYA"}
# Two of each language's own cities: every sitemap page of theirs is checked.
OWN_CITIES = {"kn": ("bengaluru", "mysuru"), "te": ("hyderabad", "visakhapatnam"),
              "ta": ("chennai", "madurai"), "ml": ("kochi", "thiruvananthapuram"),
              "bn": ("kolkata", "howrah"), "or": ("bhubaneswar", "cuttack")}
DEVANAGARI = re.compile(r"[ऀ-ॣ०-ॿ]")          # the danda । ॥ is shared by bn/or
TEXT_MODULES = (seo_text, rashifal_text, vrat_text, muhurat_text, nakshatra_page_text,
                nakshatra_text, naam_milan_text)
MODULES = {"seo_pages": seo_pages, "rashifal_pages": rashifal_pages, "vrat_pages": vrat_pages,
           "nakshatra_pages": nakshatra_pages, "muhurat_pages": muhurat_pages}

# Latin tokens a regional string may contain.
LATIN_OK = {"IST", "PDF", "AI", "KP", "N", "E", "WhatsApp", "Divine", "Astro", "B", "D", "Th", "Dh",
            "T", "b", "s", "S", "sh", "Sh", "v", "Swiss", "Ephemeris", "Lahiri", "UPI",
            "Ram", "Sita", "Rahul", "Priya", "Kshitij"}   # example names (the naam-milan form)
LATIN_OK |= {f"D{n}" for n in (1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60)}
ALLOWED_LATIN = re.compile(r"\b(?:Divine\s*Astro|divineastro\.org|WhatsApp|Swiss\s+Ephemeris|"
                           r"PDF|IST|UPI|AI|Rahul|Priya)\b|https?://\S+|\S+@\S+")
# Values the builders pass in the page language: {city} (seo_pages._city_vars),
# {local} (the rashi in the page script), {tone} (rashifal_pages).
NATIVE_FIELDS = {"city", "local", "tone"}
OPTIONAL_KEYS = {"home"}          # hi-only keys a language may leave out (i18n.CHROME has it)


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
    lo, hi = RANGE[lang]
    return any(lo <= ord(c) <= hi for c in s)


def devanagari(s: str) -> bool:
    return bool(DEVANAGARI.search(s))


# An element marked lang="en" (the English name under a heading, as the Hindi
# pages carry it) is English on purpose; the script checks skip it.
LANG_EN = re.compile(r'<(\w+)\b[^>]*\blang="en"[^>]*>.*?</\1>', re.S)


def visible(s: str) -> str:
    """A template's reader-visible text: no tags, no placeholders, entities decoded."""
    s = LANG_EN.sub(" ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\{[^{}]*\}", " ", s)
    return htmlmod.unescape(s)


def script_problems(s: str, lang: str) -> list[str]:
    """Letters of another script, or Latin words outside LATIN_OK."""
    text = visible(s)
    bad = sorted({c for c in text if unicodedata.category(c)[0] in "LM"
                  and SCRIPT[lang] not in unicodedata.name(c, "")
                  and "LATIN" not in unicodedata.name(c, "")})
    latin = [w for w in re.findall(r"[A-Za-z]+", text) if w not in LATIN_OK]
    return ([f"foreign script {''.join(bad)!r}"] if bad else []) + ([f"Latin {latin[:5]}"] if latin else [])


# --------------------------------------------------------------------------
# 1. Text tables
# --------------------------------------------------------------------------

def table_fields(*tables) -> set[str]:
    """Every placeholder the en / hi / _native values of a table use: a builder
    passes a page's whole set of values to each key (muhurat's {noun}, the
    nakshatra page's {name}), so a translation may use any of them."""
    out: set[str] = set()
    for t in tables:
        for v in (t.values() if isinstance(t, dict) else ()):
            if isinstance(v, str):
                out |= fields(v)
    return out


def check_strings(label: str, lang: str, values: dict, en: dict, allowed: dict | None = None,
                  extra: set[str] = frozenset()) -> None:
    """values ⊇ en's keys; placeholders allowed; no Devanagari; own script where there are words;
    nothing in another script, no Latin word outside LATIN_OK; no raw & in HTML."""
    missing = sorted(set(en) - {k for k, v in values.items() if v}, key=str)
    check(f"{label}[{lang}]: all {len(en)} English keys", not missing, str(missing[:8]))
    globs = set(i18n._name_vars(lang))
    # A page's builder passes the same values to all of its keys ("p.title",
    # "p.sub" ...): a placeholder another key of the same page uses is fine.
    page: dict[str, set] = {}
    for k, v in en.items():
        if isinstance(v, str):
            page.setdefault(str(k).split(".")[0], set()).update(fields(v))
    for k, v in (allowed or {}).items():
        page.setdefault(str(k).split(".")[0], set()).update(v)
    bad_ph, deva, no_script, foreign = [], [], [], []
    for k, v in values.items():
        if not isinstance(v, str):
            continue
        ok_ph = (globs | fields(en.get(k, "")) | (allowed or {}).get(k, set()) | NATIVE_FIELDS | extra
                 | (page.get(str(k).split(".")[0], set()) if "." in str(k) else set()))
        if not fields(v) <= ok_ph:
            bad_ph.append((k, sorted(fields(v) - ok_ph)))
        if devanagari(v):
            deva.append(k)
        if v in i18n.CODES or str(k).endswith("_lang"):      # rashifal's sub_lang: a code
            continue
        bare = re.sub(r"<[^>]+>|\{[^}]*\}|&[a-z]+;|\bIST\b", " ", LANG_EN.sub(" ", v))
        if re.search(r"[A-Za-z]{2,}", bare) and not in_script(bare, lang):
            no_script.append(k)
        probs = script_problems(v, lang)
        if probs and visible(v).strip():
            foreign.append(f"{k}: {probs}")
        if re.search(r"&(?![a-z]+;|#\d+;)", v) and "<" in str(en.get(k, "")):
            foreign.append(f"{k}: raw &")
    check(f"{label}[{lang}]: placeholders match", not bad_ph, str(bad_ph[:5]))
    check(f"{label}[{lang}]: no Devanagari", not deva, str(deva[:5]))
    check(f"{label}[{lang}]: written in its own script", not no_script, str(no_script[:5]))
    check(f"{label}[{lang}]: {SCRIPT[lang].title()} script only", not foreign, str(foreign[:5]))


def text_table(label: str, table: dict, lang: str) -> None:
    allowed: dict[str, set] = {}
    for code in ("hi", "_native"):
        for k, v in table.get(code, {}).items():
            if isinstance(v, str):
                allowed.setdefault(k, set()).update(fields(v))
    check(f"{label}: has {lang}", lang in table)
    check_strings(label, lang, table.get(lang, {}), table["en"], allowed,
                  table_fields(table["en"], table.get("hi"), table.get("_native")))


def bank(label: str, table: dict, lang: str) -> None:
    """{item: {"en": ..., "hi": ..., "<code>": ...}}: every item has `lang`."""
    missing = [x for x, row in table.items() if not row.get(lang)]
    check(f"{label}: every entry has {lang}", not missing, str(missing[:5]))
    vals = {k: e.get(lang) for k, e in table.items() if e.get(lang)}
    check_strings(label, lang, vals, {k: e["en"] for k, e in table.items()},
                  {k: fields(e.get("hi", "")) for k, e in table.items()})


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


def compare(path: str, ref, got, lang: str, problems: list[str], hi=None,
            extra: set[str] = frozenset()) -> None:
    """`got` (the regional value) has the shape, keys and placeholders of `ref`."""
    if isinstance(ref, str):
        if not isinstance(got, str) or not got:
            problems.append(f"{path}: missing/empty")
            return
        allowed = fields(ref) | (fields(hi) if isinstance(hi, str) else set()) | NATIVE_FIELDS \
            | set(i18n._name_vars(lang)) | extra
        if not fields(got) <= allowed:
            problems.append(f"{path}: placeholders {sorted(fields(got) - allowed)} not in en/hi")
        if devanagari(got):
            problems.append(f"{path}: Devanagari")
        bare = ALLOWED_LATIN.sub("", re.sub(r"<[^>]+>|\{[^}]*\}|&\w+;", "", LANG_EN.sub("", got)))
        code_like = re.fullmatch(r"[\w/.:#?=&-]*", got) is not None   # a path, a language code
        if (re.search(r"[^\W\d_]", bare) and not in_script(bare, lang) and not code_like
                and got != hi):
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
                        hi.get(k) if isinstance(hi, dict) else None, extra)
    elif isinstance(ref, (list, tuple)):
        if not isinstance(got, (list, tuple)) or len(got) != len(ref):
            problems.append(f"{path}: length {len(got) if hasattr(got, '__len__') else '?'} != {len(ref)}")
            return
        for i, (a, b) in enumerate(zip(ref, got)):
            compare(f"{path}[{i}]", a, b, lang, problems,
                    hi[i] if isinstance(hi, (list, tuple)) and len(hi) == len(ref) else None, extra)


def tables(lang: str) -> None:
    print(f"\n1. [{lang}] Text tables")
    for label, table in (("seo_text.TEXT", seo_text.TEXT), ("rashifal_text.TEXT", rashifal_text.TEXT),
                         ("vrat_text.TEXT", vrat_text.TEXT), ("muhurat_text.TEXT", muhurat_text.TEXT),
                         ("nakshatra_page_text.TEXT", nakshatra_page_text.TEXT),
                         ("naam_milan_text.TEXT", naam_milan_text.TEXT), ("i18n.CHROME", i18n.CHROME),
                         ("vrat_text.ABOUT", vrat_text.ABOUT), ("vrat_text.NOTES", vrat_text.NOTES),
                         ("rashifal_text.TONE_LABEL", rashifal_text.TONE_LABEL)):
        text_table(label, table, lang)
    for name in ("MOON_HOUSE", "SATURN_HOUSE", "JUPITER_HOUSE", "RAHU_HOUSE", "KETU_LINE"):
        bank(f"rashifal_text.{name}", getattr(rashifal_text, name), lang)
    bank("nakshatra_text.NAKSHATRA_TRAITS", nakshatra_text.NAKSHATRA_TRAITS, lang)
    bank("nakshatra_text.RASHI_TRAITS", nakshatra_text.RASHI_TRAITS, lang)
    for label, table in (("seo_text.FAQ", seo_text.FAQ), ("rashifal_text.MORE_LINKS",
                                                          rashifal_text.MORE_LINKS)):
        got = table.get(lang, ())
        check(f"{label}[{lang}]: {len(table['en'])} entries", len(got) == len(table["en"])
              and all(all(pair) for pair in got))
        texts = [t for pair in got for t in pair if not t.startswith(("/", "{"))]
        check(f"{label}[{lang}]: own script, no Devanagari, no stray Latin",
              all(in_script(t, lang) and not devanagari(t) and not script_problems(t, lang)
                  for t in texts), str([t for t in texts if script_problems(t, lang)][:2]))
    # The generic walk: every nested en/hi table, its shape and the hi-only keys.
    for mod in TEXT_MODULES:
        for name in dir(mod):
            if not name.isupper():
                continue
            for path, table in lang_tables(getattr(mod, name), f"{mod.__name__.split('.')[-1]}.{name}"):
                problems: list[str] = []
                if lang not in table:
                    problems.append(f"{path}: no {lang!r} entry")
                else:
                    extra = table_fields(table["en"], table["hi"], table.get("_native"))
                    compare(f"{path}[{lang!r}]", table["en"], table[lang], lang, problems, table["hi"],
                            extra)
                    if isinstance(table["hi"], dict) and isinstance(table["en"], dict):
                        for k in set(table["hi"]) - set(table["en"]) - OPTIONAL_KEYS:
                            if k not in table[lang]:
                                problems.append(f"{path}[{lang!r}][{k!r}]: hi-only key missing")
                            else:
                                compare(f"{path}[{lang!r}][{k!r}]", table["hi"][k], table[lang][k],
                                        lang, problems)
                check(f"{path} {lang} (shape)", not problems, "; ".join(problems[:5]))


# --------------------------------------------------------------------------
# 2. Hooks
# --------------------------------------------------------------------------

def hooks(lang: str) -> None:
    from app.astro import choghadiya, festivals
    from app.astro.namakshar import ABHIJIT, NAKSHATRA_LIST
    print(f"\n2. [{lang}] Shared hooks")
    rules = vrat_text.RULES.get(lang, {})
    want = ({"head", "tithi"} | {f"rule.{k}" for k in festivals.RULE_TEXT}
            | {f"key.{k}" for k in ("ekadashi", "makar_sankranti", "lohri", "holi")})
    check(f"vrat_text.RULES[{lang}]: head, tithi, every festivals.RULE_TEXT kind, the four "
          "own-worded rules", set(rules) == want, str(want ^ set(rules)))
    check(f"vrat_text.RULES[{lang}]: placeholders", fields(rules.get("head", "")) == {"month"}
          and fields(rules.get("tithi", "")) == {"paksha", "tithi"}
          and not any(fields(v) for k, v in rules.items() if k not in ("head", "tithi")))
    check(f"vrat_text.RULES[{lang}]: own script, no Devanagari",
          all(in_script(v, lang) and not devanagari(v) for k, v in rules.items() if k != "tithi"))
    facts = nakshatra_text.FACTS.get(lang, {})
    for field in ("deity", "symbol"):
        vals = [facts.get(f"{field}.{n.slug}", "") for n in NAKSHATRA_LIST]
        check(f"nakshatra_text.FACTS[{lang}]: {field} of all 27, in script",
              all(in_script(v, lang) and not devanagari(v) and not script_problems(v, lang) for v in vals))
    check(f"nakshatra_text.FACTS[{lang}]: nothing but deity.<slug> / symbol.<slug>",
          set(facts) == {f"{f}.{n.slug}" for f in ("deity", "symbol") for n in NAKSHATRA_LIST})
    syl = [d for n in NAKSHATRA_LIST for d, _ in n.syllables] + [d for d, _ in ABHIJIT]
    out = [i18n.akshar(d, lang) for d in syl]
    check(f"i18n.akshar({lang}): all 112 namakshar syllables in script, no Devanagari",
          all(in_script(s, lang) and not devanagari(s) for s in out),
          str([s for s in out if devanagari(s)][:5]))
    check(f"i18n.akshar_lang({lang}) == {lang}", i18n.akshar_lang(lang) == lang)
    check(f"choghadiya description_{lang} for all 7", all(
        in_script(i.get(f"description_{lang}", ""), lang) and not devanagari(i[f"description_{lang}"])
        for i in choghadiya.CHOGHADIYA_INFO.values()))
    eng = naam_milan_text.ENGINE.get(lang)
    if lang in ("kn", "te") or eng:
        check(f"naam_milan_text.ENGINE[{lang}]: 4 band notes + convention note",
              eng is not None and {"band_note0", "band_note1", "band_note2", "band_note3",
                                   "convention_note"} <= set(eng)
              and all(in_script(v, lang) for v in eng.values()))
    # City and state names.
    names = seo_city_names.CITIES.get(lang, {})
    check(f"seo_city_names.CITIES[{lang}]: all {len(seo_cities.CITIES)} cities",
          set(names) == set(seo_cities.BY_SLUG), str(sorted(set(seo_cities.BY_SLUG) ^ set(names))[:5]))
    bad = [n for n in names.values() if not in_script(n, lang) or devanagari(n) or script_problems(n, lang)
           or re.search(r"[A-Za-z]", n)]
    check(f"seo_city_names.CITIES[{lang}]: native script only", not bad, str(bad[:5]))
    check(f"seo_city_names.CITIES[{lang}]: no two cities share a name",
          len(set(names.values())) == len(names))
    states = {c.state for c in seo_cities.CITIES}
    st = seo_city_names.STATES.get(lang, {})
    check(f"seo_city_names.STATES[{lang}]: all {len(states)} states/UTs, native script",
          states <= set(st) and all(in_script(v, lang) and not re.search(r"[A-Za-z]", v)
                                    and not devanagari(v) for v in st.values()))
    check(f"seo_cities.STATE_{lang.upper()} is that table",
          getattr(seo_cities, f"STATE_{lang.upper()}", None) is st)


# --------------------------------------------------------------------------
# 3 + 4. Flags and pages
# --------------------------------------------------------------------------

# English page paths, one or more per page type (the old kn/te and ta/ml samples).
SAMPLE = [
    "/panchang", "/panchang/bengaluru", "/panchang/hyderabad", "/panchang/chennai", "/panchang/kochi",
    "/rahu-kaal", "/rahu-kaal/bengaluru", "/rahu-kaal/hyderabad", "/rahu-kaal/chennai", "/rahu-kaal/kochi",
    "/choghadiya", "/choghadiya/chennai", "/choghadiya/madurai", "/kundali-milan", "/free-kundali",
    "/rashifal", "/rashifal/mesh", "/rashifal/kanya", "/rashifal/meen", "/vrat-tyohar",
    "/vrat-tyohar/2026", "/vrat-tyohar/hyderabad", "/vrat-tyohar/chennai", "/ekadashi-2026",
    "/tyohar/diwali-2026", "/tyohar/navratri-2026", "/tyohar/janmashtami-2026",
    "/muhurat/vivah-2026", "/muhurat/griha-pravesh-2026",
    "/nakshatra", "/nakshatra/ashwini", "/nakshatra/shravana", "/nakshatra/revati", "/rashi",
    "/rashi/mesh", "/naam-se-kundali-milan",
]
MODULE_ROOTS = ("/panchang", "/rahu-kaal", "/choghadiya", "/kundali-milan", "/free-kundali",
                "/rashifal", "/vrat-tyohar", "/ekadashi-", "/tyohar/", "/muhurat/", "/nakshatra",
                "/rashi", "/naam-se-kundali-milan")
# Rendered (noindex tool results): body checked, engine-written koota notes aside.
NOINDEX = ["/naam-se-kundali-milan?boy=Rahul&girl=Priya", "/naam-se-kundali-milan?boy=Ram&girl=Sita"]


def en_pages(lang: str) -> list[str]:
    """SAMPLE + every English sitemap page of the modules, city pages only for
    the language's own two cities."""
    slugs = set(seo_cities.BY_SLUG)
    out = list(SAMPLE)
    for p in seo_pages.sitemap_paths():
        if i18n.strip_prefix(p)[0] != "en" or not p.startswith(MODULE_ROOTS):
            continue
        last = p.rstrip("/").rsplit("/", 1)[-1]
        if last in slugs and last not in OWN_CITIES[lang]:
            continue
        out.append(p)
    return list(dict.fromkeys(out))


def main_nodes(page: str) -> list[str]:
    """The visible text nodes of <main>, without the picker, scripts and styles."""
    m = re.search(r"<main\b.*?</main>", page, re.S)
    s = m.group(0) if m else page
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r'<details class="lang-picker".*?</details>', " ", s, flags=re.S)
    s = re.sub(r'(?s)<p class="legal-entity">.*?</p>', " ", s)
    s = LANG_EN.sub(" ", s)
    return [t for t in (htmlmod.unescape(x).strip() for x in re.split(r"<[^>]+>", s)) if t]


def engine_notes(page: str) -> set[str]:
    """The naam-milan result's koota notes (matching.ashtakoot writes them in
    English or Hindi only - docs/i18n.md "APIs")."""
    return {htmlmod.unescape(c).strip() for c in re.findall(
        r"<tr><td><strong>[^<]*</strong></td><td>[^<]*</td><td>([^<]*)</td></tr>", page)}


ENGLISH_RUN = re.compile(r"[A-Za-z][A-Za-z'’]*(?:[\s,.:;()/–—&-]+[A-Za-z][A-Za-z'’]*){2,}")


def body_problems(page: str, lang: str, noindex: bool = False) -> list[str]:
    nodes = main_nodes(page)
    if noindex:
        notes = engine_notes(page)
        nodes = [n for n in nodes if n not in notes]
    text = "\n".join(nodes)
    problems = []
    if devanagari(text):
        problems.append("Devanagari in body: " + "".join(DEVANAGARI.findall(text))[:20])
    native = sum(1 for c in text if in_script(c, lang))
    latin = sum(1 for c in ALLOWED_LATIN.sub("", text) if c.isascii() and c.isalpha())
    if native < 10 * max(latin, 1):
        problems.append(f"script ratio native={native} latin={latin}")
    if not noindex and native < 200:
        problems.append(f"too little text in the script ({native})")
    runs = [r for n in nodes for r in ENGLISH_RUN.findall(ALLOWED_LATIN.sub(" ", n))
            if [w for w in re.findall(r"[A-Za-z]+", r) if w not in LATIN_OK and len(w) > 2]]
    if runs:
        problems.append(f"English left: {runs[:3]}")
    return problems


def alternates(page: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', page))


def flags() -> None:
    print("\n3. TRANSLATED")
    for name, mod in MODULES.items():
        check(f"{name}.TRANSLATED has {', '.join(LANGS)}", set(LANGS) <= set(mod.TRANSLATED),
              str(sorted(mod.TRANSLATED)))
    check("katha stays en/hi", set(katha.TRANSLATED) == {"en", "hi"})


def pages(lang: str, sitemap: str, en_alts_cache: dict) -> None:
    paths = en_pages(lang)
    print(f"\n4. [{lang}] Pages ({len(paths)} English paths)")
    for en_path in paths:
        if en_path not in en_alts_cache:
            en_alts_cache[en_path] = alternates(client.get(en_path).text)
        en_alts = en_alts_cache[en_path]
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
        if alts != en_alts:
            problems.append("hreflang differs from the English copy")
        codes = {k.split("-")[0] for k in alts}
        if not set(ALL) | {"en", "hi"} <= codes:
            problems.append(f"hreflang lacks {sorted(set(ALL) | {'en', 'hi'} - codes)}")
        if not any(k.split("-")[0] == lang and u == SITE + path for k, u in alts.items()):
            problems.append("no self hreflang")
        if f"<loc>{SITE}{path}</loc>" not in sitemap:
            problems.append("not in sitemap")
        m = re.search(r"<title>([^<]*)</title>", page)
        title = htmlmod.unescape(m.group(1)) if m else ""
        if not in_script(title, lang) or devanagari(title):
            problems.append(f"title not in script: {title!r}")
        problems += body_problems(page, lang)
        check(f"{path}  [{title[:60]}]", not problems, "; ".join(problems[:4]))
    for en_path in NOINDEX:
        path = i18n.localized_path(en_path, lang)
        r = client.get(path)
        check(f"{path}: 200, noindex", r.status_code == 200 and 'content="noindex' in r.text)
        problems = body_problems(r.text, lang, noindex=True)
        check(f"{path}: body in its script (koota notes aside)", not problems, "; ".join(problems[:3]))


# --------------------------------------------------------------------------
# 5. Native city names
# --------------------------------------------------------------------------

def jsonld_crumbs(page: str) -> list[str]:
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        data = json.loads(block.replace("<\\/", "</"))
        for node in data.get("@graph", [data]):
            if node.get("@type") == "BreadcrumbList":
                return [i["name"] for i in node["itemListElement"]]
    return []


def city_names(lang: str) -> None:
    print(f"\n5. [{lang}] Native city names")
    cities = [seo_cities.BY_SLUG[s] for s in (*OWN_CITIES[lang], "mumbai", "varanasi")]
    for c in cities:
        native = seo_cities.city_name(c, lang)
        check(f"{c.slug}: has a {lang} name", native != c.name and in_script(native, lang))
        for tool in ("panchang", "rahu-kaal", "choghadiya", "vrat-tyohar"):
            path = f"/{lang}/{tool}/{c.slug}"
            page = client.get(path).text
            title = htmlmod.unescape(re.search(r"<title>([^<]*)</title>", page).group(1))
            h1 = htmlmod.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S).group(1)))
            crumbs = re.search(r'<nav class="crumbs"[^>]*>(.*?)</nav>', page, re.S).group(1)
            ld = jsonld_crumbs(page)
            date = re.search(r'<p class="date">(.*?)</p>', page, re.S)
            problems = []
            for where, text in (("title", title), ("h1", h1)):
                if native not in text:
                    problems.append(f"{where} lacks {native}")
                if re.search(rf"\b{re.escape(c.name)}\b", text):
                    problems.append(f"{where} has English {c.name}")
            if f">{native}<" not in crumbs and not crumbs.rstrip().endswith(native):
                problems.append("breadcrumb")
            if not ld or ld[-1] != native:
                problems.append(f"JSON-LD breadcrumb {ld[-1:]}")
            if tool != "vrat-tyohar":
                want = f"{native}, {seo_cities.state_name(c.state, lang)}"
                if not date or want not in date.group(1):
                    problems.append(f"date line lacks {want!r}")
            if f'href="/{lang}/{tool}/{c.slug}"' not in page and tool != "vrat-tyohar":
                problems.append("slug URL changed")
            check(f"{path}: title, H1, breadcrumb, JSON-LD in {lang}", not problems, "; ".join(problems))
    # The city index of a tool page: every city by its native name, under native state headings.
    page = client.get(f"/{lang}/panchang").text
    idx = re.search(r'<dl class="cities">(.*?)</dl>', page, re.S).group(1)
    missing = [c.slug for c in seo_cities.CITIES
               if f'href="/{lang}/panchang/{c.slug}"' in idx
               and f">{htmlmod.escape(seo_cities.city_name(c, lang))}</a>" not in idx]
    check(f"/{lang}/panchang city index: native names", not missing, str(missing[:5]))
    dts = re.findall(r"<dt>([^<]*)</dt>", idx)
    check(f"/{lang}/panchang city index: native state headings",
          dts and all(in_script(d, lang) and not re.search(r"[A-Za-z]", d) for d in dts), str(dts[:3]))
    # English and Hindi pages are untouched by the regional names.
    en = client.get(f"/panchang/{cities[0].slug}").text
    hi = client.get(f"/hi/panchang/{cities[0].slug}").text
    check(f"/panchang/{cities[0].slug} (en, hi) keep City.name / name_hi",
          cities[0].name in en and seo_cities.city_name(cities[0], lang) not in en
          and cities[0].name_hi in hi and seo_cities.city_name(cities[0], lang) not in hi)


def main() -> int:
    for lang in LANGS:
        tables(lang)
        hooks(lang)
    flags()
    sitemap = client.get("/sitemap.xml").text
    cache: dict = {}
    for lang in LANGS:
        pages(lang, sitemap, cache)
        city_names(lang)
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print(f"regional SEO pages ({', '.join(LANGS)}): all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
