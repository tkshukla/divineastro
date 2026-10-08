"""Per-language data modules (DIVASTRO-143): one file per language, the ONLY place
a translator edits.

Punjabi (pa), Nepali (ne), Assamese (as), Marathi (mr) and Gujarati (gu) were added
without writing a word of their text into the shared files. Every table that for
the older languages lives inline in app/seo_text.py, app/vrat_text.py ... has a
twin in `app/lang_data/<code>.py`, under a constant named in `tables.SPECS`
(`SEO_TEXT`, `VRAT_ABOUT`, `RASHIFAL_MOON_HOUSE` ...). Each shared module calls

    lang_data.merge("SEO_TEXT", TEXT)

once, next to its tables; that overlays the per-language data into the live table
at import time, so `TEXT["pa"]` exists exactly as if it were written inline (an
empty value is skipped: it counts as "not translated", the English fallback shows).

Which pages are *really* translated is a separate, explicit switch in the same
file:

    READY = frozenset({"seo", "hub"})        # page modules complete for this language

and each page module computes its TRANSLATED set as

    i18n.BASE_TRANSLATED | {legacy languages} | lang_data.ready("seo")

so a translator flips a module by editing only their own file. Until a module is
READY its pages for the language render the English body, noindex, with no hreflang,
out of the sitemap, with the "translation coming soon" notice (docs/i18n.md).

    python -m app.lang_data skeleton pa     # write app/lang_data/pa.py (every key, TODO values)
    python -m app.lang_data check pa        # completeness / placeholders / script report

This package imports nothing from app.*, so i18n.py can use it first thing.
`as` is a Python keyword, so the modules are loaded by name with importlib; the file
is `app/lang_data/as.py` like the others and the language code stays "as".
"""

from __future__ import annotations

import functools
import importlib.util
import os
import sys
import types
from pathlib import Path
from typing import Iterable

#: The languages that have a per-language module, in registry order.
NEW_CODES: tuple[str, ...] = ("pa", "ne", "as", "mr", "gu")
#: The six languages written inline in the shared files before DIVASTRO-143.
LEGACY_CODES: tuple[str, ...] = ("kn", "te", "ta", "ml", "bn", "or")

#: The page modules a language can be READY for. "nakshatra" covers nakshatra_pages
#: and naam_milan; "app" is the SPA json plus the astrology name tables.
PAGE_KEYS: tuple[str, ...] = ("seo", "rashifal", "vrat", "nakshatra", "muhurat", "recurring", "hub")
READY_KEYS: tuple[str, ...] = PAGE_KEYS + ("app",)

#: Unicode blocks each script may use (the checker's "wrong script" rule).
#: Assamese is written in the Bengali block (ৰ U+09F0 and ৱ U+09F1 are in it);
#: Marathi and Nepali are Devanagari.
BLOCKS: dict[str, tuple[tuple[int, int], ...]] = {
    "hi": ((0x0900, 0x097F),), "mr": ((0x0900, 0x097F),), "ne": ((0x0900, 0x097F),),
    "pa": ((0x0A00, 0x0A7F),), "gu": ((0x0A80, 0x0AFF),), "as": ((0x0980, 0x09FF),),
    "bn": ((0x0980, 0x09FF),), "or": ((0x0B00, 0x0B7F),), "ta": ((0x0B80, 0x0BFF),),
    "te": ((0x0C00, 0x0C7F),), "kn": ((0x0C80, 0x0CFF),), "ml": ((0x0D00, 0x0D7F),),
}

_DIR = Path(__file__).resolve().parent
#: Where `load` looks for <code>.py (tests point this at a temporary directory).
SEARCH_DIRS: list[Path] = [_DIR]


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def _load_file(code: str) -> types.ModuleType | None:
    for directory in SEARCH_DIRS:
        path = directory / f"{code}.py"
        if path.is_file():
            # A synthetic name: `as` cannot be spelled in an import statement.
            name = f"app.lang_data._{code}" if directory == _DIR else f"_lang_data_{code}"
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            try:
                spec.loader.exec_module(module)
            except Exception:
                sys.modules.pop(name, None)
                raise
            return module
    return None


@functools.lru_cache(maxsize=None)
def load(code: str) -> types.ModuleType | None:
    """The module for `code`, or None when it has none. Validates READY."""
    module = _load_file(code)
    if module is None:
        return None
    ready = getattr(module, "READY", frozenset())
    unknown = set(ready) - set(READY_KEYS)
    if unknown:
        raise ValueError(f"app/lang_data/{code}.py: READY names unknown module(s) {sorted(unknown)};"
                         f" known: {READY_KEYS}")
    return module


def reload() -> None:
    """Forget loaded modules (tests that switch SEARCH_DIRS / NEW_CODES)."""
    load.cache_clear()


def modules() -> list[tuple[str, types.ModuleType]]:
    """[(code, module)] for every code in NEW_CODES that has a file."""
    out = []
    for code in NEW_CODES:
        module = load(code)
        if module is not None:
            out.append((code, module))
    return out


def ready(key: str) -> frozenset[str]:
    """The new languages whose READY includes `key` ('seo', 'rashifal', ...)."""
    if key not in READY_KEYS:
        raise KeyError(f"unknown READY key {key!r}; known: {READY_KEYS}")
    return frozenset(code for code, m in modules() if key in getattr(m, "READY", ()))


def listed(code: str) -> bool:
    """Whether the language shows in the language picker and the app's registry.

    The older languages always do. A new language (pa ne as mr gu) does once it has
    something READY — until then it is reachable by URL (/pa/panchang, English body,
    noindex) but not offered, so that adding it to the registry changes nothing on any
    English or Hindi page (tests/test_seo_snapshots.py stays byte-identical).
    ASTRO_LIST_ALL_LANGS=1 lists them all (staging, screenshots, the e2e picker test)."""
    if code not in NEW_CODES:
        return True
    if os.environ.get("ASTRO_LIST_ALL_LANGS", "") not in ("", "0"):
        return True
    module = load(code)
    return bool(module is not None and getattr(module, "READY", ()))


def translated(key: str, base: Iterable[str], legacy: Iterable[str] = ()) -> frozenset[str]:
    """A page module's TRANSLATED set: `base` (en, hi) + the legacy languages it was
    written in before DIVASTRO-143 + every new language READY for `key`."""
    return frozenset(base) | frozenset(legacy) | ready(key)


# --------------------------------------------------------------------------
# Merging
# --------------------------------------------------------------------------

def merge(table_id: str, table) -> None:
    """Overlay every language's `table_id` constant into the live `table`, in place,
    as if it were written inline. Empty values are skipped (not translated)."""
    from .tables import SPECS
    kind = SPECS[table_id].kind
    for code, module in modules():
        data = getattr(module, table_id, None)
        if data:
            MERGERS[kind](code, data, table)


def merge_akshar(target: dict) -> None:
    """i18n._AKSHAR[code] = (block start, {Devanagari letter: override})."""
    for code, module in modules():
        spec = getattr(module, "AKSHAR", None)
        if spec:
            target[code] = (spec[0], dict(spec[1]))


def filled(code: str, table_id: str) -> bool:
    """Whether the language's module has any non-empty value for `table_id`."""
    from .tables import flatten
    module = load(code)
    data = getattr(module, table_id, None) if module else None
    return any(v for v in flatten(table_id, data).values()) if data else False


def _m_text(code, data, table):                 # table[code] = {key: str}
    values = {k: v for k, v in data.items() if v}
    if values:
        table.setdefault(code, {}).update(values)


def _m_bank(code, data, table):                 # table[key][code] = str
    for key, value in data.items():
        if value and key in table:
            table[key][code] = value


def _m_pairs(code, data, table):                # table[code] = ((a, b), ...), all or nothing
    if all(all(part for part in pair) for pair in data):
        table[code] = tuple(tuple(pair) for pair in data)


def _m_tuple(code, data, table):                # table[code] = (12 names)
    if len(data) == 12 and all(data):
        table[code] = tuple(data)


def _m_scalar(code, data, table):               # table[code] = str
    if data:
        table[code] = data


def _m_choghadiya(code, data, table):           # table[name]["description_<code>"]
    for name, text in data.items():
        if text and name in table:
            table[name][f"description_{code}"] = text


def _m_variants(code, data, table):             # table[code] = {1..12: (spellings,)}
    values = {k: tuple(v) for k, v in data.items() if v}
    if values:
        table[code] = values


MERGERS = {"text": _m_text, "bank": _m_bank, "pairs": _m_pairs, "tuple": _m_tuple,
           "scalar": _m_scalar, "choghadiya": _m_choghadiya, "variants": _m_variants}
