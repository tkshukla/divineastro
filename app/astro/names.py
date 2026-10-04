"""Panchang names in any registry language (DIVASTRO-121).

names_hi.py is the model: per-language tables keyed by the engine's English
names. A language gets the same treatment by adding `app/astro/names_<code>.py`
with the same shape, the table names suffixed by the code in upper case:

    TITHI_KN, NAKSHATRAS_KN, VARA_KN, YOGA_KN, KARANA_KN, PAKSHA_KN,
    NOTE_POLAR_KN, NOTE_WEDNESDAY_KN

(unsuffixed TITHI, NAKSHATRAS, ... are accepted too). Nothing else needs to
change: `names_for(lang)` finds the module, `add_names(p, lang)` adds
`name_<code>` etc. to an /api/panchang response exactly as `add_hindi` adds
`name_hi`, and the app's `loc(row, 'name')` picks them up. A missing module, a
missing table or a missing entry falls back to the English name — never an
error.
"""

from __future__ import annotations

import functools
import importlib
from types import ModuleType

TABLES = ("TITHI", "NAKSHATRAS", "VARA", "YOGA", "KARANA", "PAKSHA")
NOTES = ("NOTE_POLAR", "NOTE_WEDNESDAY")


@functools.lru_cache(maxsize=None)
def names_for(lang: str) -> ModuleType | None:
    """The app.astro.names_<lang> module, or None (English, or not written yet)."""
    if not lang or lang == "en" or not lang.isalpha():
        return None
    try:
        return importlib.import_module(f"app.astro.names_{lang}")
    except ModuleNotFoundError:
        return None


def table(lang: str, name: str) -> dict[str, str]:
    """One table (e.g. "TITHI") for `lang`; {} when there is none — callers do
    `table(...).get(english, english)`, so an empty table means English."""
    mod = names_for(lang)
    if mod is None:
        return {}
    value = getattr(mod, f"{name}_{lang.upper()}", None)
    if value is None:
        value = getattr(mod, name, None)
    return value if isinstance(value, dict) else {}


def note(lang: str, name: str) -> str | None:
    mod = names_for(lang)
    if mod is None:
        return None
    return getattr(mod, f"{name}_{lang.upper()}", None) or getattr(mod, name, None)


def available() -> list[str]:
    """Registry languages (beyond en/hi) that have a names module today."""
    from .. import i18n
    return [code for code in i18n.EXTRA_CODES if names_for(code) is not None]


def add_names(p: dict, lang: str) -> dict:
    """Add `<field>_<lang>` beside the English fields of a daily_panchang dict —
    the same fields add_hindi adds for Hindi. English where a name is missing."""
    if lang in ("en", "hi") or names_for(lang) is None:
        return p
    sfx = f"_{lang}"
    tithi, paksha = table(lang, "TITHI"), table(lang, "PAKSHA")
    for row in p.get("tithi") or []:
        name, pk = row.get("name"), row.get("paksha")
        row["name" + sfx] = tithi.get(name, name)
        row["paksha" + sfx] = paksha.get(pk, pk)
        row["label" + sfx] = f"{row['paksha' + sfx] or ''} {row['name' + sfx]}".strip()
    for key, tname in (("nakshatra", "NAKSHATRAS"), ("yoga", "YOGA"), ("karana", "KARANA")):
        t = table(lang, tname)
        for row in p.get(key) or []:
            row["name" + sfx] = t.get(row.get("name"), row.get("name"))
    vara = p.get("vara")
    if vara:
        vara["name" + sfx] = table(lang, "VARA").get(vara.get("weekday"), vara.get("name"))
    notes = []
    if p.get("reckoned_from") == "midnight":
        notes.append(note(lang, "NOTE_POLAR"))
    elif (p.get("muhurta") or {}).get("abhijit") is None and p.get("reckoned_from") == "sunrise":
        notes.append(note(lang, "NOTE_WEDNESDAY"))
    # A note not yet translated falls back to the English one from the engine.
    p["notes" + sfx] = [n for n in notes if n] or (list(p.get("notes") or []) if notes else [])
    return p


def add_all(p: dict) -> dict:
    """Hindi (always, as before) plus every language that has a names module, so
    the app can switch language without asking the server again."""
    from .names_hi import add_hindi
    add_hindi(p)
    for code in available():
        add_names(p, code)
    return p
