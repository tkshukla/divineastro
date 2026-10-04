"""Deprecated alias of app.astro.names_i18n — the one loader for astrology names.

DIVASTRO-121 added this module's `names_for(lang)` (returning the raw
names_<code> module); DIVASTRO-123 consolidated it into names_i18n, whose
`names_for(lang)` returns a uniform `Names` object for all eight languages
(English and Hindi included). Import from app.astro.names_i18n; this module
only re-exports it so old imports keep working.
"""

from .names_i18n import (  # noqa: F401
    LANGS, REGIONAL_LANGS, TABLES, TEXTS, Names, add_all, add_names, available, names_for,
)
