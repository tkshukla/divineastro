"""The language registry (DIVASTRO-121): every language the site speaks, in one place.

English and Hindi have been first-class since DIVASTRO-106. This adds Kannada,
Telugu, Tamil, Malayalam, Bengali and Odia the same way: a URL prefix per
language (/kn/panchang, ...), a `lang` code the app keeps in `state.lang`, and
English as the fallback for anything not yet translated.

How a page decides what it is
-----------------------------
Every server-rendered module (seo_pages, rashifal_pages, vrat_pages, ...)
declares which languages it has actually been translated into:

    TRANSLATED = frozenset({"en", "hi"})        # in that module

A page in a language that is NOT in its module's TRANSLATED set still renders
(the link from the language picker must never 404) — but its body is the
English text, so it must not compete with the real English page in search:

* `<meta name="robots" content="noindex, follow">`
* no hreflang alternates on it, and it is not listed in anyone else's
* it is left out of sitemap.xml
* a one-line "translation coming soon" notice in that language's own script

Translating a module into, say, Kannada is then: write the Kannada strings,
make the page builder use them for lang == "kn", and add "kn" to the module's
TRANSLATED. Nothing else: hreflang, sitemap, noindex and the notice all follow
from that one set. See `docs/i18n.md` for the step-by-step.

The app (SPA) reads its strings from app/static/i18n/<code>.json, English
being the fallback per key; `client_registry()` is what it is told about the
languages themselves (main.py inlines it into index.html).
"""

from __future__ import annotations

import functools
import html
import re
from dataclasses import dataclass, field
from typing import Iterable, Mapping

DEFAULT = "en"


@dataclass(frozen=True)
class Language:
    code: str            # what state.lang, ?lang= and the API `language` params carry
    native: str          # the picker shows this, in its own script
    english: str         # small text under the native name
    script: str          # ISO 15924
    hreflang: str        # <link rel=alternate hreflang=...>
    bcp47: str           # schema.org inLanguage
    html_lang: str       # <html lang=...>
    og_locale: str
    prefix: str          # URL prefix of this language's copy of a page; "" for English
    status: str          # "full" | "beta" (the app's UI is not translated yet)
    font: str | None     # Google Fonts family that renders the script well (None: system fonts)
    # Short strings, in the language's OWN script. Read by the picker, the
    # first-visit hint and the untranslated-page notice — which must be readable
    # by someone who does not read English, so they are written here by hand.
    choose: str = ""     # "Choose language" (the picker's heading / aria-label)
    hint: str = ""       # "View this site in <language>?" (the first-visit banner)
    yes: str = ""        # "View in <language>" (its button)
    not_now: str = ""    # "Not now"
    notice: str = ""     # "Translation coming soon — this page is in English for now."
    extra: Mapping[str, str] = field(default_factory=dict)


LANGUAGES: tuple[Language, ...] = (
    Language("en", "English", "English", "Latn", "en", "en-IN", "en-IN", "en_IN", "", "full", None,
             choose="Choose language", hint="View this site in English?", yes="View in English",
             not_now="Not now", notice="Translation coming soon — this page is shown in English for now."),
    Language("hi", "हिन्दी", "Hindi", "Deva", "hi", "hi-IN", "hi", "hi_IN", "/hi", "full", None,
             choose="भाषा चुनें", hint="क्या आप यह साइट हिन्दी में देखना चाहेंगे?",
             yes="हिन्दी में देखें", not_now="अभी नहीं",
             notice="अनुवाद जल्द आ रहा है — यह पेज अभी अंग्रेज़ी में दिखाया जा रहा है।"),
    Language("kn", "ಕನ್ನಡ", "Kannada", "Knda", "kn", "kn-IN", "kn", "kn_IN", "/kn", "beta",
             "Noto Sans Kannada",
             choose="ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ", hint="ಈ ಸೈಟ್ ಅನ್ನು ಕನ್ನಡದಲ್ಲಿ ನೋಡಬೇಕೆ?",
             yes="ಕನ್ನಡದಲ್ಲಿ ನೋಡಿ", not_now="ಈಗ ಬೇಡ",
             notice="ಅನುವಾದ ಶೀಘ್ರದಲ್ಲೇ ಬರಲಿದೆ — ಸದ್ಯಕ್ಕೆ ಈ ಪುಟವನ್ನು ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ತೋರಿಸಲಾಗಿದೆ."),
    Language("te", "తెలుగు", "Telugu", "Telu", "te", "te-IN", "te", "te_IN", "/te", "beta",
             "Noto Sans Telugu",
             choose="భాషను ఎంచుకోండి", hint="ఈ సైట్‌ను తెలుగులో చూడాలనుకుంటున్నారా?",
             yes="తెలుగులో చూడండి", not_now="ఇప్పుడు కాదు",
             notice="అనువాదం త్వరలో వస్తుంది — ప్రస్తుతానికి ఈ పేజీ ఆంగ్లంలో చూపబడుతోంది."),
    Language("ta", "தமிழ்", "Tamil", "Taml", "ta", "ta-IN", "ta", "ta_IN", "/ta", "beta",
             "Noto Sans Tamil",
             choose="மொழியைத் தேர்ந்தெடுக்கவும்", hint="இந்தத் தளத்தைத் தமிழில் பார்க்க விரும்புகிறீர்களா?",
             yes="தமிழில் பார்க்க", not_now="இப்போது வேண்டாம்",
             notice="மொழிபெயர்ப்பு விரைவில் வரும் — தற்போது இந்தப் பக்கம் ஆங்கிலத்தில் காட்டப்படுகிறது."),
    Language("ml", "മലയാളം", "Malayalam", "Mlym", "ml", "ml-IN", "ml", "ml_IN", "/ml", "beta",
             "Noto Sans Malayalam",
             choose="ഭാഷ തിരഞ്ഞെടുക്കുക", hint="ഈ സൈറ്റ് മലയാളത്തിൽ കാണണോ?",
             yes="മലയാളത്തിൽ കാണുക", not_now="ഇപ്പോൾ വേണ്ട",
             notice="വിവർത്തനം ഉടൻ വരുന്നു — ഇപ്പോൾ ഈ പേജ് ഇംഗ്ലീഷിലാണ് കാണിക്കുന്നത്."),
    Language("bn", "বাংলা", "Bengali", "Beng", "bn", "bn-IN", "bn", "bn_IN", "/bn", "beta",
             "Noto Sans Bengali",
             choose="ভাষা বেছে নিন", hint="এই সাইটটি বাংলায় দেখতে চান?",
             yes="বাংলায় দেখুন", not_now="এখন নয়",
             notice="অনুবাদ শীঘ্রই আসছে — আপাতত এই পৃষ্ঠাটি ইংরেজিতে দেখানো হচ্ছে।"),
    Language("or", "ଓଡ଼ିଆ", "Odia", "Orya", "or", "or-IN", "or", "or_IN", "/or", "beta",
             "Noto Sans Oriya",
             choose="ଭାଷା ବାଛନ୍ତୁ", hint="ଏହି ସାଇଟ୍‌ଟି ଓଡ଼ିଆରେ ଦେଖିବେ କି?",
             yes="ଓଡ଼ିଆରେ ଦେଖନ୍ତୁ", not_now="ଏବେ ନୁହେଁ",
             notice="ଅନୁବାଦ ଶୀଘ୍ର ଆସୁଛି — ଆପାତତଃ ଏହି ପୃଷ୍ଠାଟି ଇଂରାଜୀରେ ଦେଖାଯାଉଛି।"),
)

BY_CODE: dict[str, Language] = {lang.code: lang for lang in LANGUAGES}
CODES: tuple[str, ...] = tuple(BY_CODE)
# The languages whose pages live under a URL prefix served by the generic
# /{lang:xlang}/... routes — every one except English (no prefix) and Hindi
# (whose /hi/ routes predate this and are registered explicitly).
EXTRA_CODES: tuple[str, ...] = tuple(c for c in CODES if c not in ("en", "hi"))
# What every module translates today. A module's own TRANSLATED starts as this.
BASE_TRANSLATED = frozenset({"en", "hi"})


def get(lang: str | None) -> Language:
    """The registry entry, English for anything unknown (never raises)."""
    return BY_CODE.get((lang or "").strip().lower(), BY_CODE[DEFAULT])


def normalize(lang: str | None) -> str:
    """A known code, or "en". Used by every API `language`/`lang` parameter so
    an unsupported value degrades to English instead of a 422."""
    return get(lang).code


def is_supported(lang: str | None) -> bool:
    return (lang or "") in BY_CODE


def ordered(codes: Iterable[str]) -> list[str]:
    """`codes` in registry order (dedupe, unknown dropped) — sets have no order."""
    wanted = set(codes)
    return [c for c in CODES if c in wanted]


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

def prefix(lang: str) -> str:
    return get(lang).prefix


def localized_path(path: str, lang: str) -> str:
    """The English path `path` in `lang`: '/panchang' -> '/kn/panchang', '/' -> '/kn/'.
    Already-prefixed paths are first stripped, so this is idempotent."""
    _, bare = strip_prefix(path)
    p = prefix(lang)
    if not p:
        return bare
    return p + ("/" if bare == "/" else bare)


_PREFIX_RE = re.compile(r"^/(" + "|".join(c for c in CODES if c != "en") + r")(?=/|$)")


def strip_prefix(path: str) -> tuple[str, str]:
    """'/kn/panchang/pune' -> ('kn', '/panchang/pune'); '/panchang' -> ('en', '/panchang').
    Only registry prefixes count; /en/katha (katha's own scheme) is left alone."""
    m = _PREFIX_RE.match(path or "/")
    if not m:
        return DEFAULT, path or "/"
    rest = path[m.end():] or "/"
    return m.group(1), rest


def alternates(en_path: str, translated: Iterable[str], x_default: str = DEFAULT,
               site: str = "", paths: Mapping[str, str] | None = None,
               region: bool = False) -> str:
    """Reciprocal hreflang <link>s for every TRANSLATED language (in registry
    order) plus x-default. `paths` overrides a language's URL (katha's Hindi copy
    is the unprefixed one); otherwise it is localized_path(en_path, lang).
    `region` writes "en-IN"/"hi-IN" instead of "en"/"hi" (the rashifal, nakshatra
    and muhurat pages always have; kept so their en/hi tags don't change).
    Every copy of a page must emit the identical set — a one-way hreflang is ignored."""
    paths = dict(paths or {})
    langs = ordered(translated)
    out = []
    for code in langs:
        href = paths.get(code, localized_path(en_path, code))
        tag = get(code).bcp47 if region else get(code).hreflang
        out.append(f'<link rel="alternate" hreflang="{tag}" '
                   f'href="{html.escape(site + href)}"/>\n')
    default = x_default if x_default in langs else DEFAULT
    href = paths.get(default, localized_path(en_path, default))
    out.append(f'<link rel="alternate" hreflang="x-default" href="{html.escape(site + href)}"/>\n')
    return "".join(out)


def app_link(lang: str, query: str = "") -> str:
    """A link into the app that opens it in `lang`: app_link('kn', 'open=panchang')."""
    parts = [query] if query else []
    if lang != DEFAULT:
        parts.append(f"lang={lang}")
    return "/" + ("?" + "&".join(parts) if parts else "")


# --------------------------------------------------------------------------
# Strings
# --------------------------------------------------------------------------

# A string table may carry a NATIVE layer beside its languages: templates a
# language uses for a key it has not translated yet, before falling back to
# English. It holds only the keys whose English text is mostly an astrology
# name ("{tithi}", a timing label), so an untranslated Kannada page still prints
# its tithi/nakshatra names from app/astro/names_kn.py instead of English words.
NATIVE = "_native"


def t(key: str, lang: str, table: Mapping[str, Mapping[str, str]]) -> str:
    """table[lang][key], falling back to table['_native'][key] (any language but
    English), then table['en'][key], then to the key itself. The shape of every
    per-module string table: {"en": {...}, "hi": {...}, "kn": {...}}."""
    for code in ((lang, NATIVE, DEFAULT) if lang != DEFAULT else (DEFAULT,)):
        value = table.get(code, {}).get(key)
        if value:
            return value
    return key


def fmt(key: str, lang: str, table: Mapping[str, Mapping[str, str]], **values) -> str:
    """t() then str.format(**values): templates keep their `{placeholders}` (the
    word order is the translator's). Values are inserted as given — HTML-escape
    them first where the template is HTML. Every template may also use the
    astrology labels of `lang` (name_vars): {t_rahu_kaal}, {l_tithi}, ..."""
    return t(key, lang, table).format(**{**name_vars(lang), **values})


@functools.lru_cache(maxsize=None)
def _name_vars(lang: str) -> dict:
    n = names(lang)
    out = {f"t_{k}": v for k, v in n.TIMINGS.items()}
    out.update({f"l_{k}": v for k, v in n.LIMBS.items()})
    return out


def name_vars(lang: str) -> dict:
    """{t_<timing>: ..., l_<limb>: ...} from names_<code>.TIMINGS / LIMBS, so a
    template can say "{t_rahu_kaal}" and get ರಾಹು ಕಾಲ on a Kannada page."""
    return _name_vars(lang if lang in BY_CODE else DEFAULT)


def has(key: str, lang: str, table: Mapping[str, Mapping[str, str]]) -> bool:
    """Whether `lang` has its own text for `key` (not a fallback)."""
    return bool(table.get(lang, {}).get(key))


# --------------------------------------------------------------------------
# Astrology names, dates and clock times in any language
# --------------------------------------------------------------------------

def names(lang: str | None):
    """The name tables for `lang` (app.astro.names_i18n.Names): TITHI, NAKSHATRAS,
    VARA, MONTHS, CLOCK, TIMINGS, FESTIVALS ... English for an unknown code."""
    from .astro.names_i18n import names_for
    return names_for(lang)


def format_date(day, lang: str, *, short: bool = False, months=None) -> str:
    """'8 November 2026' / '8 Nov' in English; '8 नवंबर 2026' / '8 नवंबर' in
    Hindi, and the same shape with names_<code>.MONTHS in every other language
    (English abbreviates a short month; the Indian languages do not). `months`
    overrides the month names for one module that spells them its own way."""
    if lang not in BY_CODE or lang == DEFAULT:
        text = f"{day.day} {day.strftime('%b' if short else '%B')}"
    else:
        text = f"{day.day} {(months or names(lang).MONTHS)[day.month - 1]}"
    return text if short else f"{text} {day.year}"


def month_name(month: int, lang: str, months=None) -> str:
    """'November' / 'नवंबर' / 'ನವೆಂಬರ್' for a month number 1-12."""
    if lang not in BY_CODE or lang == DEFAULT:
        import calendar
        return calendar.month_name[month]
    return (months or names(lang).MONTHS)[month - 1]


def format_time(moment, lang: str) -> str:
    """'6:29 AM' in English; '<part of day> 6:29' (सुबह 6:29) in every Indian
    language — how almanacs print times (names_i18n.Names.clock)."""
    return names(lang if lang in BY_CODE else DEFAULT).clock(moment)


def weekday(day, lang: str) -> str:
    """'Sunday' / 'रविवार' / the names_<code>.VARA word, for a date."""
    english = day.strftime("%A")
    return names(lang).VARA.get(english, english)


# Strings for the chrome every server-rendered page shares (crumbs, footer,
# share button). The translation agents fill the new languages' columns; until
# then each key falls back to English.
CHROME: dict[str, dict[str, str]] = {
    "en": {
        "home": "Home", "breadcrumb": "Breadcrumb", "share": "Share on WhatsApp",
        "f_katha": "Kathas", "f_terms": "Terms &amp; Conditions", "f_privacy": "Privacy Policy",
        "f_refund": "Refund &amp; Cancellation", "f_contact": "Contact Us", "f_feedback": "Feedback",
        "disclaimer": ("Astrological readings are provided for guidance and\n    entertainment. "
                       "They are not medical, legal or financial advice."),
    },
    "hi": {
        "home": "होम", "breadcrumb": "ब्रेडक्रंब", "share": "WhatsApp पर भेजें",
        "f_katha": "कथाएँ", "f_terms": "नियम और शर्तें", "f_privacy": "गोपनीयता नीति",
        "f_refund": "रिफ़ंड और रद्दीकरण", "f_contact": "संपर्क करें", "f_feedback": "सुझाव",
        "disclaimer": ("ज्योतिषीय जानकारी मार्गदर्शन और मनोरंजन के लिए है। यह चिकित्सा, "
                       "कानूनी या वित्तीय सलाह नहीं है।"),
    },
}


def pick(by_lang: Mapping[str, object], lang: str):
    """by_lang[lang] if present (and non-empty), else by_lang['en'] — for the many
    module tables shaped {"en": ..., "hi": ...}. Adding a "kn" entry is how a
    translation agent fills one in; until then Kannada pages show the English."""
    value = by_lang.get(lang)
    return value if value else by_lang[DEFAULT]


def chrome(key: str, lang: str) -> str:
    return t(key, lang, CHROME)


# --------------------------------------------------------------------------
# Server-rendered page pieces: the language picker, the notice, fonts, robots
# --------------------------------------------------------------------------

GLOBE = ('<svg class="lp-globe" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" '
         'focusable="false"><path fill="none" stroke="currentColor" stroke-width="1.8" '
         'd="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zm-8.5 9h17M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9'
         'c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>')


def font_link(lang: str) -> str:
    """The Google Fonts stylesheet for `lang`'s script — only for the active
    language, never all eight. `display=swap`: text shows at once in a system
    font and swaps when the web font arrives. Google's CSS splits each family by
    unicode-range, so only the script's own glyphs are downloaded."""
    family = get(lang).font
    if not family:
        return ""
    fam = family.replace(" ", "+")
    return ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>\n'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={fam}:wght@400;600'
            '&amp;display=swap"/>\n')


def font_url(lang: str) -> str:
    family = get(lang).font
    if not family:
        return ""
    return f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@400;600&display=swap"


def robots_meta(lang: str, translated: Iterable[str]) -> str:
    """noindex for a page whose body is still the English fallback."""
    if lang in set(translated):
        return ""
    return '<meta name="robots" content="noindex, follow"/>\n'


def notice(lang: str, translated: Iterable[str]) -> str:
    """'Translation coming soon' in the page language's own script, or ''."""
    if lang in set(translated):
        return ""
    L = get(lang)
    return (f'<p class="lp-notice" role="note" lang="{L.html_lang}">{html.escape(L.notice)}</p>')


def picker(lang: str, links: Mapping[str, str], *, label: str | None = None) -> str:
    """The language picker for a server-rendered page: a pill button with a globe
    and the current language's native name, opening a list of all eight.

    Built on <details>/<summary>, so it works with no script at all (keyboard:
    Tab to it, Enter/Space opens; the links are ordinary links). langpick.js adds
    Escape-to-close, close-on-outside-click, remembers the choice for the app,
    and shows the first-visit hint. `links` maps every registry code to the URL of
    this page in that language."""
    cur = get(lang)
    label = label or cur.choose
    items = []
    for L in LANGUAGES:
        href = links.get(L.code) or app_link(L.code)
        current = ' aria-current="true"' if L.code == cur.code else ""
        items.append(
            f'<li><a href="{html.escape(href)}" hreflang="{L.hreflang}" lang="{L.html_lang}" '
            f'data-lang="{L.code}" data-hint="{html.escape(L.hint)}" data-yes="{html.escape(L.yes)}" '
            f'data-notnow="{html.escape(L.not_now)}"{current}>'
            f'<span class="lp-native">{html.escape(L.native)}</span>'
            # The small English name, except where it would just repeat the native one.
            + (f'<span class="lp-en" lang="en">{html.escape(L.english)}</span>'
               if L.english != L.native else "")
            + '</a></li>')
    return (f'<details class="lang-picker" data-current="{cur.code}">'
            f'<summary class="lp-btn" aria-label="{html.escape(label)}: {html.escape(cur.native)}">'
            f'{GLOBE}<span class="lp-cur" lang="{cur.html_lang}">{html.escape(cur.native)}</span>'
            f'<span class="lp-caret" aria-hidden="true">▾</span></summary>'
            f'<div class="lp-menu" role="group" aria-label="{html.escape(label)}">'
            f'<p class="lp-title">{html.escape(label)}</p>'
            f'<ul>{"".join(items)}</ul></div></details>')


def picker_links(en_path: str, overrides: Mapping[str, str] | None = None) -> dict[str, str]:
    """Every language's copy of the page whose English path is `en_path`.
    Untranslated copies are still real pages (English body, noindex), so every
    link resolves."""
    out = {code: localized_path(en_path, code) for code in CODES}
    out.update(overrides or {})
    return out


# The picker's CSS lives in static/styles.css ("Language picker"), shared with the app header.


# Font stacks per script: the Latin families first (so English words in a
# Kannada page keep the site's look), then the script's web font, then the
# system fonts that carry it on Windows/Android, then the generic family.
_SCRIPT_FALLBACK = {
    "kn": '"Noto Sans Kannada", "Tunga", "Nirmala UI"',
    "te": '"Noto Sans Telugu", "Gautami", "Nirmala UI"',
    "ta": '"Noto Sans Tamil", "Latha", "Nirmala UI"',
    "ml": '"Noto Sans Malayalam", "Kartika", "Nirmala UI"',
    "bn": '"Noto Sans Bengali", "Vrinda", "Nirmala UI"',
    "or": '"Noto Sans Oriya", "Kalinga", "Nirmala UI"',
}


def font_css() -> str:
    """html[lang=xx] overrides of --sans/--serif, used by styles.css's twin and
    the server pages. Generated so the list can't drift from the registry."""
    out = []
    for code, fams in _SCRIPT_FALLBACK.items():
        out.append(
            f'html[lang="{code}"] {{ --sans: "Segoe UI", Inter, system-ui, -apple-system, '
            f'"Helvetica Neue", Arial, {fams}, sans-serif; '
            f'--serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, {fams}, serif; }}')
    return "\n".join(out) + "\n"


LANGPICK_SCRIPT = '<script src="/static/langpick.js" defer></script>\n'


def head_extras(lang: str, translated: Iterable[str]) -> str:
    """Everything a page's <head> needs for its language beyond the shell:
    the robots meta for an untranslated copy, the script's web font, and the
    picker's script (Escape/outside-click/remember-choice/first-visit hint)."""
    return robots_meta(lang, translated) + font_link(lang) + LANGPICK_SCRIPT


# --------------------------------------------------------------------------
# Links inside an untranslated page
# --------------------------------------------------------------------------

# First path segments that have a copy in every language (the generic
# /{lang:xlang}/... routes). Modules add their own on import.
LOCALIZABLE_ROOTS: set[str] = set()
_HREF = re.compile(r'href="(/[^"]*)"')


def localize_links(fragment: str, lang: str) -> str:
    """Keep a reader inside their language: in a page served under /kn/, rewrite
    links to other localizable pages ('/panchang/pune' -> '/kn/panchang/pune')
    and into the app ('/?open=x' -> '/?open=x&lang=kn'). Links that already carry
    a language prefix, and everything else (legal pages, /static, /api), are
    left alone. A no-op for English and Hindi, whose pages write their links
    themselves."""
    if lang in ("en", "hi") or lang not in BY_CODE:
        return fragment

    def fix(m: re.Match) -> str:
        url = m.group(1)
        path, sep, query = url.partition("?")
        if path == "/":
            q = html.unescape(query)
            if "lang=" in q:
                return m.group(0)
            q = (q + "&" if q else "") + f"lang={lang}"
            return f'href="/?{html.escape(q)}"'
        code, _ = strip_prefix(path)
        if code != DEFAULT:
            return m.group(0)
        root = path.split("/")[1] if path.count("/") >= 1 else ""
        key = root if root in LOCALIZABLE_ROOTS else root.split("-")[0] + "-"
        if root not in LOCALIZABLE_ROOTS and key not in LOCALIZABLE_ROOTS:
            return m.group(0)
        return f'href="{localized_path(path, lang)}{sep}{query}"'

    return _HREF.sub(fix, fragment)


# --------------------------------------------------------------------------
# Routing: /{lang:xlang}/... matches exactly the extra languages
# --------------------------------------------------------------------------

def _register_convertor() -> None:
    from starlette.convertors import Convertor, register_url_convertor

    class LangConvertor(Convertor):
        regex = "|".join(EXTRA_CODES)

        def convert(self, value: str) -> str:
            return value

        def to_string(self, value: str) -> str:
            return value

    register_url_convertor("xlang", LangConvertor())


_register_convertor()


# --------------------------------------------------------------------------
# The app (SPA)
# --------------------------------------------------------------------------

def client_registry() -> list[dict]:
    """What the app is told about the languages (inlined into index.html by main.py)."""
    return [{"code": L.code, "native": L.native, "english": L.english, "script": L.script,
             "htmlLang": L.html_lang, "prefix": L.prefix, "status": L.status,
             "font": font_url(L.code), "choose": L.choose, "hint": L.hint, "yes": L.yes,
             "notNow": L.not_now, "notice": L.notice} for L in LANGUAGES]
