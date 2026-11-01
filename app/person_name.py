"""The person's name as a report may print it (DIVASTRO-168).

The birth form's name is optional, and a blank one reaches the chart as the
server's placeholder "Native" (chart_service). That placeholder stays — the
engine and older callers rely on a non-empty name — but nothing a customer
reads may print it: no "Name: Native" row, no "Native" on a cover or in a file
name. Every renderer asks `display_name` instead of reading meta["name"].

`scrub_placeholder` is the guard for model-written report text: a prompt for an
unnamed chart says "the person", but a model can still write "Native" as if it
were a name. Only the capitalised word is touched (lowercase "the native" is
ordinary jyotish usage and stays), and only for a chart that has no name.
"""
from __future__ import annotations

import re

PLACEHOLDER = "Native"

# Values that mean "no name was given": the server's fallback, its Hindi
# transliteration, and the dash the Milan report casts an unnamed side with.
_NO_NAME = {"native", "नेटिव", "—", "-", "–"}

# The cover line of a report for an unnamed chart, in each report language.
YOUR_KUNDALI = {
    "en": "Your kundali",
    "hi": "आपकी कुंडली",
    "kn": "ನಿಮ್ಮ ಜಾತಕ",
    "te": "మీ జాతకం",
    "ta": "உங்கள் ஜாதகம்",
    "ml": "നിങ്ങളുടെ ജാതകം",
    "bn": "আপনার কুণ্ডলী",
    "or": "ଆପଣଙ୍କ କୁଣ୍ଡଳୀ",
}


def display_name(meta_or_name) -> str | None:
    """The name the person typed, or None when they gave none.

    Takes a chart's meta dict (or anything with a "name" key) or the bare name.
    """
    if isinstance(meta_or_name, dict):
        meta_or_name = meta_or_name.get("name")
    name = " ".join(str(meta_or_name or "").split())
    if not name or name.casefold() in _NO_NAME:
        return None
    return name


def cover_subject(meta, language: str = "en") -> str:
    """The cover's subtitle: the name, else the neutral "Your kundali"."""
    return display_name(meta) or YOUR_KUNDALI.get(language, YOUR_KUNDALI["en"])


def prompt_person(meta) -> str:
    """Who a report prompt is about: "a native named Asha", or "the person"."""
    name = display_name(meta)
    return f"a native named {name}" if name else "the person"


def prompt_name_rule(meta) -> str:
    """For an unnamed chart, the instruction that keeps a name out of the text."""
    if display_name(meta):
        return ""
    return ("The person did not give a name. Never call them by a name, and never "
            "write the word \"Native\" as if it were one; address them as \"you\".\n\n")


# "Native" used as a name. Capitalised only, never "Native American"; an
# optional "the"/"The" in front is folded into the replacement.
_DEAR = re.compile(r"\b([Dd]ear) Native\b(?! American)")
_NAMED = re.compile(r"[ \t]*\bnamed Native\b(?! American)")
_NATIVE = re.compile(r"(?<![\w-])(?:([Tt])he )?Native\b(?! American)")
_SENTENCE_START = re.compile(r"(?:^|[.!?:\n*#>]\s*|^\s*[-*]\s+)$")
_LOCAL_WORD = {"hi": "जातक"}


def scrub_placeholder(text: str, language: str = "en") -> str:
    """Model text for an unnamed chart with "Native"-as-a-name taken out."""
    if not text or (PLACEHOLDER not in text and "नेटिव" not in text):
        return text
    text = text.replace("नेटिव", "जातक")
    text = _DEAR.sub(lambda m: f"{m.group(1)} reader", text)
    text = _NAMED.sub("", text)
    local = _LOCAL_WORD.get(language)

    def repl(m: re.Match) -> str:
        if language != "en":
            # A Hindi or regional report: the English word is a stray either
            # way. Hindi has its own word for it; elsewhere it is dropped.
            return local or ""
        start = bool(_SENTENCE_START.search(text[:m.start()])) or m.group(1) == "T"
        return "The native" if start else "the native"

    text = _NATIVE.sub(repl, text)
    return re.sub(r"[ \t]{2,}", " ", text)


def scrub_fields(result: dict, keys, meta, language: str = "en") -> dict:
    """`scrub_placeholder` over the text fields of a report section, in place,
    when the chart has no name; a named chart's text is left exactly as written."""
    if display_name(meta):
        return result
    for k in keys:
        v = result.get(k)
        if isinstance(v, str):
            result[k] = scrub_placeholder(v, language)
        elif isinstance(v, list):
            result[k] = [[row[0], scrub_placeholder(row[1], language)]
                         if isinstance(row, list) and len(row) > 1 and isinstance(row[1], str)
                         else row for row in v]
    return result
