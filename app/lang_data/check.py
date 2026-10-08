"""`python -m app.lang_data check <code>`: is the language's data complete and sound?

Per table (every constant in app/lang_data/<code>.py, names_<code>.py, static/i18n/<code>.json):

  missing        a key English has that the language does not
  empty          the key is there with "" (the skeleton's TODO value)
  extra          a key English does not have (a typo would never show)
  placeholders   the {names} in the value differ from the English value's (a missing
                 {city} prints a hole, an extra one raises KeyError at render time)
  same as English  the value is the English text, letters and all
  wrong script   letters outside the language's Unicode block(s) (digits, punctuation,
                 symbols, ASCII markup/placeholders and ALLOW_LATIN words are fine)
  html           the tag sequence differs from English (an unclosed or dropped tag)
  braces         a stray "{" or "}" that str.format would refuse

and, for the languages that are READY for a page module, that every table of the module
is clean (a language cannot go live half-written).

Exit status 0 only when nothing is reported.
"""

from __future__ import annotations

import importlib
import json
import re
import string
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from . import BLOCKS, PAGE_KEYS, READY_KEYS, load
from .tables import SPECS, Spec, english, expected_placeholders, flatten, live

ROOT = Path(__file__).resolve().parents[2]
I18N_DIR = ROOT / "app" / "static" / "i18n"

#: Latin words any language may keep (brands, units, abbreviations the sites uses in Latin).
DEFAULT_ALLOW_LATIN = frozenset({
    "WhatsApp", "Divine", "Astro", "Divine Astro", "Google", "UPI", "PDF", "AI", "IST", "AM", "PM",
    "SMS", "OK", "Wi-Fi", "FAQ", "QR", "PNG", "URL", "iPhone", "Android", "Chrome", "Safari",
    "Instagram", "Facebook", "YouTube", "Telegram", "Gmail", "Razorpay", "Cashfree", "Drik",
    "Panchang", "Lahiri", "KP", "Swiss", "Ephemeris", "Vimshottari", "Kundali",
    # compass letters of a coordinate, the example names the naam-milan page types in, and
    # the Latin letters its transliteration table explains
    "N", "E", "S", "W", "Ram", "Sita", "T", "D", "Th", "Dh",
})
_ALWAYS_LATIN = re.compile(r"[A-Z]\d{1,2}")             # D1 .. D60, A1 .. A12 (chart labels)
_NAME_VAR = re.compile(r"\{[tl]_[a-z_]+\}")
_PLACEHOLDER = re.compile(r"\{[A-Za-z_][\w.:\-]*\}")
_TAG = re.compile(r"<(/?)([A-Za-z][A-Za-z0-9]*)[^>]*?(/?)>")
_ENTITY = re.compile(r"&#?\w+;")
_URL = re.compile(r"https?://\S+|/[a-z0-9\-_/{}.:?=&]+")
_LATIN_RUN = re.compile(r"[A-Za-z][A-Za-z0-9'’.\-+/]*")


def placeholders(text: str) -> frozenset[str]:
    return frozenset(_PLACEHOLDER.findall(text or ""))


def tags(text: str) -> list[str]:
    return [f"{close}{name.lower()}{selfclose}" for close, name, selfclose in _TAG.findall(text or "")]


def bare(text: str) -> str:
    """`text` without markup: tags, entities, {placeholders}, URLs."""
    text = _TAG.sub(" ", text or "")
    text = re.sub(r"<[^>]*>", " ", text)
    text = _ENTITY.sub(" ", text)
    text = _PLACEHOLDER.sub(" ", text)
    text = re.sub(r"\{[^{}]*\}", " ", text)
    return _URL.sub(" ", text)


def has_words(text: str, allow=frozenset()) -> bool:
    """Whether `text` has letters beyond markup and the Latin words any language may keep."""
    plain = bare(text)
    for word in sorted(DEFAULT_ALLOW_LATIN | set(allow), key=len, reverse=True):
        plain = re.sub(rf"(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])", " ", plain)
    return any(unicodedata.category(c)[0] == "L" for c in plain)


_VOID = {"br", "hr", "img", "input", "meta", "link", "wbr"}


def unbalanced(text: str) -> str:
    """'' if every non-void tag closes in order, else a short description."""
    stack = []
    for close, name, selfclose in _TAG.findall(text or ""):
        name = name.lower()
        if selfclose or name in _VOID:
            continue
        if not close:
            stack.append(name)
        elif not stack or stack.pop() != name:
            return f"</{name}> without its opening tag"
    return f"<{stack[-1]}> never closed" if stack else ""


def in_blocks(c: str, code: str) -> bool:
    n = ord(c)
    return any(a <= n <= b for a, b in BLOCKS.get(code, ()))


def script_problems(text: str, code: str, allow=frozenset()) -> list[str]:
    """Snippets of `text` in a script other than the language's."""
    out = []
    allowed = DEFAULT_ALLOW_LATIN | set(allow)
    plain = bare(text)
    for phrase in sorted((a for a in allowed if " " in a), key=len, reverse=True):
        plain = plain.replace(phrase, " ")
    for run in _LATIN_RUN.findall(plain):
        word = run.strip(".-+/'’")
        if word and word not in allowed and not _ALWAYS_LATIN.fullmatch(word):
            out.append(word)
    for c in plain:
        if c.isascii():
            continue
        if unicodedata.category(c)[0] in "LM" and not in_blocks(c, code) \
                and not 0xFE00 <= ord(c) <= 0xFE0F:                  # variation selectors (emoji)
            out.append(c + f" (U+{ord(c):04X})")
    return out


def format_error(text: str) -> str:
    try:
        list(string.Formatter().parse(text))
    except ValueError as e:
        return str(e)
    return ""


@dataclass
class Result:
    name: str                           # SEO_TEXT, names TITHI, i18n/pa.json ...
    total: int = 0                      # keys expected
    filled: int = 0                     # keys with a value
    problems: dict = field(default_factory=dict)    # category -> [detail, ...]
    skipped: str = ""                   # why nothing was checked (optional table, empty)

    def add(self, category: str, detail: str) -> None:
        self.problems.setdefault(category, []).append(detail)

    @property
    def ok(self) -> bool:
        return not self.problems


def source_latin(text: str) -> frozenset:
    """Capitalised / upper-case / digit-bearing Latin tokens of an English UI string —
    app and field names the UI shows as they are (PhonePe, UTR, D1-D60, Spam)."""
    return frozenset(t.strip(".-+/'’") for t in _LATIN_RUN.findall(bare(text))
                     if t[0].isupper() or any(c.isdigit() for c in t))


def compare(name: str, en: dict, own: dict, code: str, *, rules: dict | None = None,
            allow=frozenset(), keep=frozenset(), optional=False, extra_keys_ok=False,
            tag_check=True, latin_from_source=False, extra_prefixes=()) -> Result:
    """Check one table: `en` {key: English text}, `own` {key: the language's text}.
    `rules` {key: (core, allowed)} placeholder sets (tables.placeholder_rules)."""
    r = Result(name, total=len(en))
    if optional and not any(isinstance(v, str) and v.strip() for v in own.values()):
        r.skipped = "optional, left empty"
        return r
    for key in en:
        if key not in own:
            r.add("missing", str(key))
        elif not isinstance(own[key], str) or not own[key].strip():
            r.add("empty", str(key))
    for key in own:
        if key not in en and not extra_keys_ok and not str(key).startswith(tuple(extra_prefixes)):
            r.add("extra", str(key))
    for key, value in own.items():
        if key not in en or not isinstance(value, str) or not value.strip():
            continue
        r.filled += 1
        if str(key).endswith("_lang"):                 # lang="" of a line: the language's own code
            if value != code:
                r.add("wrong value", f"{key}: must be {code!r}")
            continue
        core, allowed = (rules or {}).get(key) or (placeholders(en[key]),) * 2
        got = placeholders(value)
        lost = sorted(core - got)
        gained = sorted(p for p in got - allowed if not _NAME_VAR.fullmatch(p))
        if lost or gained:
            r.add("placeholders", f"{key}: missing {' '.join(lost) or '-'}; "
                                  f"unknown {' '.join(gained) or '-'} (allowed: {' '.join(sorted(allowed)) or 'none'})")
        bad = format_error(value)
        if bad:
            r.add("braces", f"{key}: {bad}")
        allow_here = allow | source_latin(en[key]) if latin_from_source else allow
        if en[key].strip() and value.strip() == en[key].strip() and has_words(en[key], allow_here) \
                and key not in keep:
            r.add("same as English", str(key))
        wrong = script_problems(value, code, allow_here)
        if wrong:
            r.add("wrong script", f"{key}: {', '.join(dict.fromkeys(wrong))[:80]}")
        if tag_check:
            broken = unbalanced(value)
            if broken:
                r.add("html", f"{key}: {broken}")
    return r


# --------------------------------------------------------------------------
# Sources: a language module, or (to validate the checker itself) the live tables
# --------------------------------------------------------------------------

def live_data(code: str, spec: Spec):
    """The language's entries read back out of the live shared table, in the shape
    of the constant in a language file."""
    table = live(spec)
    k = spec.kind
    if k == "text":
        skip = spec.skip() if spec.skip else set()
        return {key: v for key, v in table.get(code, {}).items() if key not in skip}
    if k == "bank":
        return {key: v.get(code, "") for key, v in table.items()}
    if k == "pairs":
        return tuple(table.get(code, ()))
    if k == "tuple":
        return tuple(table.get(code, ()))
    if k == "scalar":
        return table.get(code, "")
    if k == "choghadiya":
        return {name: info.get(f"description_{code}", "") for name, info in table.items()}
    if k == "variants":
        return dict(table.get(code, {}))
    raise KeyError(k)


def check_tables(code: str, module, *, source: str = "module", groups=None) -> list[Result]:
    results = []
    allow = frozenset(getattr(module, "ALLOW_LATIN", ()) if module else ())
    keep = frozenset(getattr(module, "KEEP_ENGLISH", ()) if module else ())
    for spec in SPECS.values():
        if groups and spec.group not in groups:
            continue
        data = live_data(code, spec) if source == "live" else getattr(module, spec.id, None)
        en = english(spec)
        if spec.id == "ASTRO_MONTHS":
            results.append(_check_variants(code, spec, data, allow))
            continue
        if spec.id == "RASHIFAL_CLOCK_LANG":
            r = Result(spec.id)
            if data not in (None, "", "en"):
                r.add("extra", f"CLOCK_LANG must be '' or 'en', not {data!r}")
            results.append(r)
            continue
        own = flatten(spec.id, data)
        if spec.shape == "pairs" and spec.fields == ("href", "text"):
            results.append(_check_links(spec, data, en, code, allow))
            continue
        r = compare(spec.id, en, own, code, rules=expected_placeholders(spec), allow=allow,
                    keep=keep, optional=spec.optional)
        results.append(r)
    return results


def _check_links(spec, data, en, code, allow) -> Result:
    """MORE_LINKS: ((href, text), ...). Hrefs must equal English's (first: {twin:en})."""
    r = Result(spec.id, total=len(en) // 2)
    data = tuple(data or ())
    if len(data) != len(en) // 2:
        r.add("missing", f"expected {len(en) // 2} links, found {len(data)}")
    for i, pair in enumerate(data):
        if len(pair) != 2:
            r.add("extra", f"{i}: not a (href, text) pair")
            continue
        href, text = pair
        want = en.get(f"{i}.href")
        if i == 0:
            want = "{twin:en}"
        if want is not None and href != want:
            r.add("placeholders", f"{i}: href {href!r}, expected {want!r}")
        if not str(text).strip():
            r.add("empty", f"{i}.text")
        else:
            r.filled += 1
            if str(text).strip() == en.get(f"{i}.text", "").strip():
                r.add("same as English", f"{i}.text")
            wrong = script_problems(text, code, allow)
            if wrong:
                r.add("wrong script", f"{i}.text: {', '.join(dict.fromkeys(wrong))}")
    return r


def _check_variants(code, spec, data, allow) -> Result:
    r = Result(spec.id)
    if not data:
        r.skipped = "optional, left empty"
        return r
    for month, spellings in data.items():
        if month not in range(1, 13):
            r.add("extra", f"month {month}")
        for s in spellings:
            r.filled += 1
            wrong = script_problems(s, code, allow)
            if wrong:
                r.add("wrong script", f"{month}: {s}")
    return r


# --------------------------------------------------------------------------
# names_<code>.py and static/i18n/<code>.json
# --------------------------------------------------------------------------

def check_names(code: str, *, allow=frozenset()) -> list[Result]:
    from app.astro import names_i18n as N
    results = []
    try:
        module = importlib.import_module(f"app.astro.names_{code}")
    except ModuleNotFoundError:
        r = Result(f"names_{code}.py")
        r.add("missing", "the file does not exist (python -m app.lang_data skeleton %s)" % code)
        return [r]
    en = N._names("en")
    suffix = code.upper()
    for name in N.TABLES:
        base = getattr(en, name)
        own = getattr(module, f"{name}_{suffix}", None)
        if own is None:
            r = Result(f"names {name}", total=len(base))
            r.add("missing", f"{name}_{suffix} is not defined")
            results.append(r)
            continue
        base_flat = dict(enumerate(base)) if isinstance(base, tuple) else dict(base)
        own_flat = dict(enumerate(own)) if isinstance(own, (list, tuple)) else dict(own)
        optional = name in ("SOLAR_MASA", "REGIONAL_NOTE")
        r = compare(f"names {name}", base_flat, own_flat, code, allow=allow, optional=optional,
                    extra_keys_ok=name in ("SOLAR_MASA", "REGIONAL_NOTE", "CLOCK"), tag_check=False)
        if optional and not base_flat and own_flat:
            r.skipped = ""
        results.append(r)
    for name in N.TEXTS:
        own = getattr(module, f"{name}_{suffix}", None)
        results.append(compare(f"names {name}", {0: getattr(en, name)}, {0: own or ""}, code,
                               allow=allow, tag_check=False))
    return results


def _flat_json(value, prefix=""):
    """(path, leaf) pairs; nested keys join with "/" (top-level keys contain dots)."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield from _flat_json(v, f"{prefix}/{k}" if prefix else str(k))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _flat_json(v, f"{prefix}/{i}" if prefix else str(i))
    else:
        yield prefix, value


def check_json(code: str, *, allow=frozenset(), keep=frozenset()) -> Result:
    path = I18N_DIR / f"{code}.json"
    r = Result(f"static/i18n/{code}.json")
    en = {k: v for k, v in _flat_json(json.loads((I18N_DIR / "en.json").read_text(encoding="utf-8")))}
    r.total = len(en)
    if not path.exists():
        r.add("missing", f"{path.name} does not exist")
        return r
    try:
        own = {k: v for k, v in _flat_json(json.loads(path.read_text(encoding="utf-8")))}
    except ValueError as e:
        r.add("braces", f"not valid JSON: {e}")
        return r
    enstr = {k: v for k, v in en.items() if isinstance(v, str)}
    ownstr = {k: v for k, v in own.items() if isinstance(v, str)}
    res = compare(r.name, enstr, ownstr, code, allow=allow, keep=keep, tag_check=False,
                  latin_from_source=True, extra_prefixes=("acct.errors/",))
    for k in en:
        if k not in enstr and k not in own:
            res.add("missing", k)
    return res


# --------------------------------------------------------------------------
# Whole language
# --------------------------------------------------------------------------

def akshar_check(code: str, module) -> Result:
    """Every namakshar syllable must come out in the language's script."""
    from app import i18n
    from app.astro.namakshar import ABHIJIT, NAKSHATRA_LIST
    r = Result("AKSHAR")
    spec = getattr(module, "AKSHAR", None) if module else i18n._AKSHAR.get(code)
    if not spec:
        r.add("missing", "AKSHAR = (Unicode block start, {Devanagari letter: override})")
        return r
    saved = i18n._AKSHAR.get(code)
    i18n._AKSHAR[code] = (spec[0], dict(spec[1]))
    try:
        syllables = [d for n in NAKSHATRA_LIST for d, _ in n.syllables] + [d for d, _ in ABHIJIT]
        r.total = len(syllables)
        for d in syllables:
            out = i18n.akshar(d, code)
            bad = [c for c in out if unicodedata.category(c)[0] in "LM" and not in_blocks(c, code)]
            if bad:
                r.add("wrong script", f"{d} -> {out}")
            else:
                r.filled += 1
    finally:
        if saved is None:
            i18n._AKSHAR.pop(code, None)
        else:
            i18n._AKSHAR[code] = saved
    return r


def check_language(code: str, *, source: str = "module", only=None) -> list[Result]:
    """Every result for `code`. `only`: iterable of group names (+ 'names', 'json', 'akshar')."""
    only = set(only or ())
    module = load(code) if source == "module" else None
    if source == "module" and module is None:
        r = Result(f"app/lang_data/{code}.py")
        r.add("missing", "the file does not exist (python -m app.lang_data skeleton %s)" % code)
        return [r]
    allow = frozenset(getattr(module, "ALLOW_LATIN", ()) if module else ())
    keep = frozenset(getattr(module, "KEEP_ENGLISH", ()) if module else ())
    results: list[Result] = []
    groups = {g for g in READY_KEYS if not only or g in only}
    if groups:
        results += check_tables(code, module, source=source, groups=groups)
    if not only or "akshar" in only:
        results.append(akshar_check(code, module))
    if not only or "names" in only:
        results += check_names(code, allow=allow)
    if not only or "json" in only:
        results.append(check_json(code, allow=allow, keep=keep))
    return results


def group_of(result: Result) -> str:
    if result.name in SPECS:
        return SPECS[result.name].group
    if result.name.startswith("names") or result.name.endswith(".json"):
        return "app"
    return "seo" if result.name == "AKSHAR" else ""


def ready_problems(code: str, results: list[Result] | None = None) -> list[str]:
    """READY keys the language has set although the data behind them is not clean."""
    module = load(code)
    if module is None:
        return []
    results = results or check_language(code)
    declared = set(getattr(module, "READY", ()))
    names_ok = all(r.ok for r in results if r.name.startswith("names"))
    out = []
    for key in sorted(declared, key=READY_KEYS.index):
        bad = [r.name for r in results
               if r.name in SPECS and SPECS[r.name].group == key and not r.ok]
        if key == "nakshatra":
            bad += [r.name for r in results if r.name == "AKSHAR" and not r.ok]
        if key == "app":
            bad += [r.name for r in results if (r.name.startswith("names") or r.name.endswith(".json"))
                    and not r.ok]
        if key in PAGE_KEYS and not names_ok:
            bad.append("names_%s.py" % code)
        if key == "recurring":
            bad += [r.name for r in results if r.name in SPECS and SPECS[r.name].group == "vrat"
                    and not r.ok]
        if bad:
            out.append(f"READY has {key!r} but these are incomplete: {', '.join(dict.fromkeys(bad))}")
    return out


def report(code: str, results: list[Result], *, limit: int = 8, quiet: bool = False,
           out=None) -> int:
    """Print the report; the number of problem entries (0 = complete)."""
    out = out or sys.stdout
    bad = 0
    for r in results:
        if r.skipped:
            print(f"  skip  {r.name:<28} ({r.skipped})", file=out)
            continue
        n = sum(len(v) for v in r.problems.values())
        bad += n
        if not n:
            if not quiet:
                print(f"  ok    {r.name:<28} {r.filled}/{r.total}", file=out)
            continue
        summary = ", ".join(f"{len(v)} {k}" for k, v in r.problems.items())
        print(f"  FAIL  {r.name:<28} {r.filled}/{r.total} filled: {summary}", file=out)
        for cat, details in r.problems.items():
            for d in details[:limit]:
                print(f"          {cat}: {d}", file=out)
            if len(details) > limit:
                print(f"          ... {len(details) - limit} more {cat} (use --all)", file=out)
    return bad
