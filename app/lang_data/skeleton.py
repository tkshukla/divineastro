"""`python -m app.lang_data skeleton <code>`: write the files a translator fills.

Writes (and, with --force, overwrites):

  app/lang_data/<code>.py        every table of tables.SPECS with every English key, each
                                 value "" and the English text (and the {placeholders} it
                                 must keep) in the comment above it
  app/astro/names_<code>.py      every astrology name table, every English key, values ""
  app/static/i18n/<code>.json    `{}` — only if the file does not exist yet

A "" value is the TODO marker: the site treats it as "not translated" (English shows), and
`check` reports it, so an untranslated value can neither render nor pass. The skeleton
refuses to overwrite a file you have edited unless you pass --force.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from . import BLOCKS, READY_KEYS
from .check import ROOT, placeholders
from .tables import SPECS, Spec, english, expected_placeholders as expected_placeholders_for

LANG_NAMES = {"pa": "Punjabi (ਪੰਜਾਬੀ, Gurmukhi)", "ne": "Nepali (नेपाली, Devanagari)",
              "as": "Assamese (অসমীয়া, Assamese/Bengali script)", "mr": "Marathi (मराठी, Devanagari)",
              "gu": "Gujarati (ગુજરાતી, Gujarati script)"}

#: Script data a translator does not write: block start and the letters that move
#: differently from "same offset in the block". See i18n._AKSHAR.
AKSHAR_DEFAULTS = {
    "pa": (0x0A00, {"ष": "ਸ਼"}),
    "gu": (0x0A80, {}),
    "as": (0x0980, {"र": "ৰ", "व": "ৱ"}),
    "mr": (0x0900, {}),
    "ne": (0x0900, {}),
}

_GROUP_TITLE = {
    "seo": "seo       /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali + shared chrome, cities",
    "rashifal": "rashifal  /rashifal and /rashifal/<sign>",
    "vrat": "vrat      /vrat-tyohar /ekadashi-<year> /tyohar/<slug>-<year>",
    "nakshatra": "nakshatra /nakshatra /rashi /naam-se-kundali-milan",
    "muhurat": "muhurat   /muhurat/<kind>-<year>",
    "recurring": "recurring /purnima-<year> /amavasya-<year> /pradosh-vrat-<year> ... (DIVASTRO-141)",
    "hub": "hub       /sitemap",
    "app": "app       AI-narration vocabulary here; names_<code>.py and static/i18n/<code>.json beside it",
}


def _comment(text: str, prefix: str, indent: str, width: int = 100) -> list[str]:
    out = []
    flat = " ".join(str(text).split()) if str(text).strip() else ""
    if not flat:
        return out
    first = True
    for line in textwrap.wrap(flat, width=max(40, width - len(indent) - len(prefix) - 2)) or [""]:
        out.append(f"{indent}# {prefix if first else ' ' * len(prefix)}{line}")
        first = False
    return out


def _key(k) -> str:
    return json.dumps(k, ensure_ascii=False) if isinstance(k, str) else repr(k)


def render_dict(spec: Spec, en: dict, ph: dict | None, code: str = "") -> list[str]:
    lines = [f"{spec.id} = {{"]
    for key, text in en.items():
        lines += _comment(text, "EN: ", "    ")
        core, allowed = (ph or {}).get(key) or (placeholders(text),) * 2
        if core:
            lines.append(f"    # keep: {' '.join(sorted(core))}")
        if allowed - core:
            lines.append(f"    # may also use: {' '.join(sorted(allowed - core))}")
        if str(key).endswith("_lang"):         # the lang=\"\" of a line: this language's own code
            lines.append(f"    {_key(key)}: {code!r},")
        else:
            lines.append(f"    {_key(key)}: \"\",")
    lines.append("}")
    return lines


def render_pairs(spec: Spec, en: dict, ph: dict | None, code: str = "") -> list[str]:
    lines = [f"{spec.id} = ("]
    n = len(en) // len(spec.fields)
    for i in range(n):
        parts = [en[f"{i}.{f}"] for f in spec.fields]
        for f, text in zip(spec.fields, parts):
            lines += _comment(text, f"EN {f}: ", "    ")
        if spec.fields == ("href", "text"):
            href = "{twin:en}" if i == 0 else parts[0]
            lines.append(f"    ({_key(href)}, \"\"),")
        else:
            lines.append("    (\"\", \"\"),")
    lines.append(")")
    return lines


def render_tuple(spec: Spec, en: dict, ph: dict | None, code: str = "") -> list[str]:
    return [f"{spec.id} = ()   # or 12 month names, January first"]


def render_scalar(spec: Spec, en, ph, code: str = "") -> list[str]:
    return [f"{spec.id} = \"\""]


def render_variants(spec: Spec, en, ph, code: str = "") -> list[str]:
    return [f"{spec.id} = {{}}   # {{month number: (other spellings,)}}, e.g. {{2: (\"...\",)}}"]


_RENDER = {"dict": render_dict, "pairs": render_pairs, "tuple": render_tuple,
           "scalar": render_scalar, "variants": render_variants}


def _akshar_source(code: str) -> str:
    start, fix = AKSHAR_DEFAULTS.get(code, (BLOCKS.get(code, ((0,),))[0][0], {}))
    body = ", ".join(f"{k!r}: {v!r}" for k, v in fix.items())
    return f"(0x{start:04X}, {{{body}}})"


def render_module(code: str, header_note: str = "") -> str:
    name = LANG_NAMES.get(code, code)
    out = [f'''"""{name} — the data a translator fills (DIVASTRO-143).

This file is the ONLY place the {code} text of the shared tables is edited; app/lang_data merges it
into them at import time, as if it were written in app/seo_text.py and friends.

  python -m app.lang_data check {code}      what is left, per table (exit 0 = complete)
  python -m app.lang_data skeleton {code} --force   regenerate (DISCARDS your edits)

Rules: every key below stays; a value "" means "not translated yet" (English shows, the
checker complains). Keep every {{placeholder}} the comment lists under `keep:`; the word order
is yours. HTML values keep their tags (write &amp; for &). Astrology names (tithi, nakshatra,
rashi, graha ...) are not here: they are in app/astro/names_{code}.py. Digits are ASCII, as in
the other languages. Full instructions: docs/lang-agent-brief.md.

Set READY when a whole page module is complete, and only then — an unfinished module in READY
fails `check` and CI. A module that is not READY renders the English body, noindex.
"""

from __future__ import annotations

# Page modules that are complete for this language (the table groups below):
#   "seo" "rashifal" "vrat" "nakshatra" "muhurat" "recurring" "hub" "app"
READY = frozenset()

# Latin-script words the {code} text may keep besides the defaults (WhatsApp, UPI, PDF ...).
ALLOW_LATIN = frozenset()

# static/i18n/{code}.json keys whose value is deliberately the English word (brand names, "OK").
KEEP_ENGLISH = frozenset()

# Namakshar syllables are Devanagari in the engine; this maps a letter to this script:
# (Unicode block start, {{Devanagari letter: this script's letter where the offset is wrong}}).
# Already set — `check` verifies all 108 syllables come out in the {code} script.
AKSHAR = {_akshar_source(code)}
''']
    current = None
    for spec in SPECS.values():
        if spec.group != current:
            current = spec.group
            out.append("\n# " + "-" * 76)
            out.append(f"# {_GROUP_TITLE[current]}")
            out.append("# " + "-" * 76)
        en = english(spec)
        ph = expected_placeholders_for(spec)
        out.append("")
        target = f"{spec.module.replace('.', '/')}.py {spec.attr}"
        count = len(en) if spec.shape != "pairs" else len(en) // len(spec.fields)
        out.append(f"# {target}[\"{code}\"] — {spec.note}" + (f"  [{count}]" if count else ""))
        if spec.optional:
            out.append("# (optional: may stay empty)")
        out += _RENDER[spec.shape](spec, en, ph, code)
    return "\n".join(out) + "\n"


def render_names(code: str) -> str:
    from app.astro import names_i18n as N
    en = N._names("en")
    suffix = code.upper()
    name = LANG_NAMES.get(code, code)
    out = [f'''"""{name} names for the panchang, festivals and matching (DIVASTRO-143).

Same shape as names_kn.py / names_bn.py: one table per name, suffix _{suffix}, keyed by the
ENGLISH name the engines emit; names_i18n.names_for("{code}") exposes them. A key left "" (or a
table left out) falls back to the English name, so the site works while this fills up; `python -m
app.lang_data check {code}` lists what is left. Use the names {name.split(' (')[0]} panchang and jyotish
tradition uses, in this language's script, not a transliteration of the English. Document
choices a native reviewer should confirm in this docstring (see names_bn.py).

Tables: TITHI(16) NAKSHATRAS(27) VARA(7) YOGA(27) KARANA(11) PAKSHA(2) MASA(12 lunar months)
SOLAR_MASA(optional: only if the calendar is solar) RASHI(12) GRAHA(9) CHOGHADIYA(7)
CHOGHADIYA_QUALITY(3) TIMINGS FESTIVAL_TIMINGS FESTIVALS EKADASHI REGIONAL_NOTE(optional)
KOOTA GANA NADI VARNA VASHYA YONI TARA WEEKDAY(7, short) MONTHS(12) CLOCK(4) LIMBS(10) and
the two notes NOTE_POLAR / NOTE_WEDNESDAY.
"""

from __future__ import annotations
''']
    from app.astro.names_i18n import TABLES, TEXTS
    for table in TABLES:
        base = getattr(en, table)
        out.append("")
        if table in ("SOLAR_MASA", "REGIONAL_NOTE"):
            hint = ("lunar months are MASA; fill this only if the calendar is solar (keys \"Aries\"..\"Pisces\")"
                    if table == "SOLAR_MASA" else "optional strong regional framing per festival key")
            out.append(f"# {hint}")
            out.append(f"{table}_{suffix} = {{}}")
            continue
        if isinstance(base, tuple):
            out.append(f"{table}_{suffix} = [")
            for month in base:
                out.append(f"    \"\",   # {month}")
            out.append("]")
            continue
        out.append(f"{table}_{suffix} = {{")
        for key, text in base.items():
            comment = f"   # {text}" if text != key else ""
            out.append(f"    {_key(key)}: \"\",{comment}")
        out.append("}")
    for text in TEXTS:
        out.append("")
        out += _comment(getattr(en, text), "EN: ", "")
        out.append(f"{text}_{suffix} = \"\"")
    out.append(f'''

def add_{code}(p: dict) -> dict:
    """add_hindi's twin for {name.split(' (')[0]}: name_{code} / paksha_{code} / label_{code} / notes_{code}."""
    from .names_i18n import add_names
    return add_names(p, "{code}")''')
    return "\n".join(out) + "\n"


def write(code: str, *, force: bool = False, say=print) -> int:
    """Write the three files; the number refused."""
    refused = 0
    targets = [
        (ROOT / "app" / "lang_data" / f"{code}.py", render_module(code)),
        (ROOT / "app" / "astro" / f"names_{code}.py", render_names(code)),
    ]
    for path, text in targets:
        if path.exists() and not force and path.read_text(encoding="utf-8") != text:
            say(f"  kept     {path.relative_to(ROOT)}  (differs from a fresh skeleton; --force to overwrite)")
            refused += 1
            continue
        path.write_text(text, encoding="utf-8")
        say(f"  wrote    {path.relative_to(ROOT)}")
    js = ROOT / "app" / "static" / "i18n" / f"{code}.json"
    if not js.exists():
        js.write_text("{}\n", encoding="utf-8")
        say(f"  wrote    {js.relative_to(ROOT)}")
    else:
        say(f"  kept     {js.relative_to(ROOT)}")
    return refused
