"""Bhakti: aartis, chalisas, stotras, mantras, puja vidhi and havan vidhi.

    /bhakti                 the index, grouped by kind
    /bhakti/<slug>          one text

The texts are traditional (Tulsidas, Adi Shankaracharya, the Puranas, the
common aarti books) and so in the public domain; each page names its source.
The verse itself is printed in the original (Sanskrit, Awadhi, Hindi); the
instructions around it are Hindi. Hindi is the only language for now
(TRANSLATED), so the other languages' picker links lead to the Hindi page.

One text = one JSON file in app/bhakti_texts/<slug>.json, validated at import
by `_parse` (a malformed file fails CI with its name). The index, the sitemap
and the public-page list follow automatically.

Schema:
  slug, category (CATEGORIES), deity (DEITIES), title (Devanagari),
  title_en (Latin, for search and the English meta line), source, summary,
  intro: [paragraph, ...],
  sections: [{"heading": str (may be ""), "blocks": [{"v": verse} | {"p": paragraph}]}],
  note (optional str), related (optional [slug, ...], each must exist).
A verse keeps its line breaks; paragraphs allow *bold* only.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import i18n, seo_pages
from .seo_pages import HI, SITE_URL, _e, _render

router = APIRouter()
TEXT_DIR = Path(__file__).resolve().parent / "bhakti_texts"

# category -> (heading, one-line intro), in index order.
CATEGORIES: dict[str, tuple[str, str]] = {
    "puja-vidhi": ("पूजा विधि", "घर पर पूजा करने की पूरी विधि, सामग्री और मंत्रों सहित।"),
    "havan-vidhi": ("हवन विधि", "हवन की तैयारी, आहुति के मंत्र और पूर्णाहुति।"),
    "aarti": ("आरती संग्रह", "पूजा के अंत में गाई जाने वाली प्रसिद्ध आरतियाँ।"),
    "chalisa": ("चालीसा संग्रह", "चालीस चौपाइयों वाली स्तुतियाँ, दोहों सहित।"),
    "stotra": ("स्तोत्र संग्रह", "संस्कृत के प्रसिद्ध स्तोत्र और अष्टक।"),
    "mantra": ("मंत्र संग्रह", "रोज़ जाप के लिए प्रमुख वैदिक और पौराणिक मंत्र।"),
}

DEITIES: dict[str, str] = {
    "ganesh": "श्री गणेश", "shiva": "भगवान शिव", "vishnu": "भगवान विष्णु",
    "krishna": "श्रीकृष्ण", "ram": "श्रीराम", "hanuman": "श्री हनुमान",
    "durga": "माँ दुर्गा", "lakshmi": "माँ लक्ष्मी", "saraswati": "माँ सरस्वती",
    "surya": "सूर्य देव", "navagraha": "नवग्रह", "shani": "शनि देव",
    "satyanarayan": "श्री सत्यनारायण", "general": "सामान्य",
}

TRANSLATED = frozenset({HI})


# --------------------------------------------------------------------------
# Texts and their schema
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Section:
    heading: str
    blocks: tuple[tuple[str, str], ...]     # ("v", verse) or ("p", paragraph)


@dataclass(frozen=True)
class Text:
    slug: str
    category: str
    deity: str
    title: str
    title_en: str
    source: str
    summary: str
    intro: tuple[str, ...]
    sections: tuple[Section, ...]
    note: str = ""
    related: tuple[str, ...] = ()


class TextError(ValueError):
    """A text file that does not match the schema. The message starts with the file name."""


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_REQUIRED = {"slug", "category", "deity", "title", "title_en", "source", "summary", "intro",
             "sections"}
_OPTIONAL = {"note", "related"}


def _markup_problem(text: str) -> str | None:
    """Paragraph markup is `*bold*` only: balanced single asterisks, no HTML."""
    if "**" in text:
        return "'**' (use single *bold*)"
    if text.count("*") % 2:
        return "an unbalanced '*'"
    if re.search(r"</?[A-Za-z]", text):
        return "HTML (only *bold* markup is allowed)"
    return None


def _parse(raw: object, where: str, stem: str) -> Text:
    def fail(msg: str) -> TextError:
        return TextError(f"{where}: {msg}")

    if not isinstance(raw, dict):
        raise fail("the file must hold one JSON object")
    missing = sorted(_REQUIRED - set(raw))
    extra = sorted(set(raw) - _REQUIRED - _OPTIONAL)
    if missing:
        raise fail(f"missing {', '.join(missing)}")
    if extra:
        raise fail(f"unknown field(s) {', '.join(extra)}")
    slug = raw["slug"]
    if not isinstance(slug, str) or not SLUG_RE.match(slug) or slug != stem:
        raise fail(f"slug must be lowercase-hyphenated and equal the file name ({stem!r})")
    if raw["category"] not in CATEGORIES:
        raise fail(f"category must be one of {', '.join(CATEGORIES)}")
    if raw["deity"] not in DEITIES:
        raise fail(f"deity must be one of {', '.join(DEITIES)}")
    for key in ("title", "title_en", "source", "summary"):
        if not isinstance(raw[key], str) or not raw[key].strip():
            raise fail(f"{key} must be a non-empty string")
        if (p := _markup_problem(raw[key])):
            raise fail(f"{key} has {p}")
    if not _DEVANAGARI.search(raw["title"]):
        raise fail("title must be in Devanagari")
    if _DEVANAGARI.search(raw["title_en"]):
        raise fail("title_en must be in Latin script")
    intro = raw["intro"]
    if not isinstance(intro, list) or not all(isinstance(p, str) and p.strip() for p in intro):
        raise fail("intro must be a list of non-empty paragraphs")
    for i, p in enumerate(intro):
        if (m := _markup_problem(p)):
            raise fail(f"intro[{i}] has {m}")
    secs = raw["sections"]
    if not isinstance(secs, list) or not secs:
        raise fail("sections must be a non-empty list")
    sections = []
    for i, s in enumerate(secs):
        if not isinstance(s, dict) or set(s) != {"heading", "blocks"}:
            raise fail(f"sections[{i}] must have exactly heading and blocks")
        if not isinstance(s["heading"], str):
            raise fail(f"sections[{i}].heading must be a string")
        blocks = s["blocks"]
        if not isinstance(blocks, list) or not blocks:
            raise fail(f"sections[{i}].blocks must be a non-empty list")
        out = []
        for j, b in enumerate(blocks):
            if not isinstance(b, dict) or len(b) != 1 or next(iter(b)) not in ("v", "p"):
                raise fail(f"sections[{i}].blocks[{j}] must be {{\"v\": verse}} or {{\"p\": text}}")
            kind, value = next(iter(b.items()))
            if not isinstance(value, str) or not value.strip():
                raise fail(f"sections[{i}].blocks[{j}] is empty")
            if kind == "p" and (m := _markup_problem(value)):
                raise fail(f"sections[{i}].blocks[{j}] has {m}")
            if kind == "v" and re.search(r"</?[A-Za-z]", value):
                raise fail(f"sections[{i}].blocks[{j}] has HTML")
            out.append((kind, value.strip()))
        sections.append(Section(s["heading"].strip(), tuple(out)))
    note = raw.get("note", "")
    if not isinstance(note, str) or ((m := _markup_problem(note)) and note):
        raise fail("note must be a string with *bold* markup only")
    related = raw.get("related", [])
    if not isinstance(related, list) or not all(isinstance(r, str) and SLUG_RE.match(r)
                                                for r in related):
        raise fail("related must be a list of slugs")
    if slug in related or len(set(related)) != len(related):
        raise fail("related must not repeat a slug or name the text itself")
    return Text(slug=slug, category=raw["category"], deity=raw["deity"],
                title=raw["title"].strip(), title_en=raw["title_en"].strip(),
                source=raw["source"].strip(), summary=raw["summary"].strip(),
                intro=tuple(p.strip() for p in intro), sections=tuple(sections),
                note=note.strip(), related=tuple(related))


def load(directory: Path | str | None = None) -> dict[str, Text]:
    """Every <slug>.json in `directory` (default $ASTRO_BHAKTI_DIR, else
    app/bhakti_texts), validated, keyed by slug, in slug order. Raises
    TextError naming the file on the first bad one, or on a `related` slug
    that has no file."""
    d = Path(directory or os.environ.get("ASTRO_BHAKTI_DIR") or TEXT_DIR)
    texts: dict[str, Text] = {}
    for f in sorted(d.glob("*.json")):
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise TextError(f"{f.name}: not valid UTF-8 JSON: {exc}") from None
        t = _parse(raw, f.name, f.stem)
        texts[t.slug] = t
    for t in texts.values():
        for r in t.related:
            if r not in texts:
                raise TextError(f"{t.slug}.json: related slug {r!r} has no file")
    return texts


TEXTS = load()


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

_BOLD = re.compile(r"\*(.+?)\*")


def _html(text: str) -> str:
    """Paragraph markup: *bold*, everything else escaped."""
    return _BOLD.sub(r"<strong>\1</strong>", _e(text))


def _verse(text: str) -> str:
    """A verse keeps its lines; a blank line separates stanzas."""
    stanzas = [s for s in re.split(r"\n\s*\n", text) if s.strip()]
    return "".join(f'<p class="verse">{"<br>".join(_e(ln.strip()) for ln in s.splitlines())}</p>'
                   for s in stanzas)


def page_path(slug: str | None = None) -> str:
    return f"/bhakti/{slug}" if slug else "/bhakti"


def _lang_paths(slug: str | None) -> dict[str, str]:
    return {code: page_path(slug) for code in i18n.CODES}


def sitemap_paths() -> list[str]:
    return [page_path(None)] + [page_path(s) for s in TEXTS]


def is_public_path(path: str) -> bool:
    return path in sitemap_paths()


_UI = {
    "index": "आरती, चालीसा, स्तोत्र और पूजा विधि",
    "crumb": "भक्ति",
    "intro": "देवी-देवताओं की आरतियाँ, चालीसा, संस्कृत स्तोत्र, मंत्र, और घर पर पूजा व हवन "
             "करने की पूरी विधि, एक ही जगह। हर पाठ के साथ उसका स्रोत दिया गया है।",
    "index_desc": "हनुमान चालीसा, शिव चालीसा, ॐ जय जगदीश हरे, शिव तांडव स्तोत्र, लक्ष्मी पूजा "
                  "विधि, हवन विधि और अन्य आरती, चालीसा, स्तोत्र, मंत्र हिंदी में।",
    "source": "स्रोत", "deity": "देवता", "nf": "पाठ नहीं मिला", "nf_desc": "यह पाठ उपलब्ध नहीं है।",
    "all": "सभी आरती, चालीसा और स्तोत्र", "related": "यह भी पढ़ें",
    "jump": "सीधे जाएँ",
    "fix": "पाठ में कोई अशुद्धि दिखे तो हमें बताएँ, हम तुरंत सुधारेंगे:",
    "fix_link": "सुधार भेजें",
    "cta_h": "पूजा के साथ अपनी कुंडली भी देखें",
    "cta_p": "जन्म तिथि, समय और स्थान से मुफ़्त कुंडली, दशा और ग्रह स्थिति। AI ज्योतिषी से पहले "
             "{free} सवाल फ्री, कोई कार्ड नहीं चाहिए।",
    "cta_kundali": "मुफ़्त कुंडली बनाएँ", "cta_panchang": "आज का पंचांग और शुभ मुहूर्त",
}


def _free_line(text: str) -> str:
    from . import billing                     # lazy: billing pulls in the DB layer
    return text.replace("{free}", str(billing.FREE_QUESTIONS))


def _index() -> HTMLResponse:
    nav = " · ".join(f'<a href="#{c}">{_e(h)}</a>' for c, (h, _) in CATEGORIES.items()
                     if any(t.category == c for t in TEXTS.values()))
    sections = []
    for cat, (heading, blurb) in CATEGORIES.items():
        group = sorted((t for t in TEXTS.values() if t.category == cat),
                       key=lambda t: (list(DEITIES).index(t.deity), t.title))
        if not group:
            continue
        items = "".join(
            f'<li><a href="{_e(page_path(t.slug))}"><strong>{_e(t.title)}</strong></a>'
            f' <small>({_e(DEITIES[t.deity])})</small> — {_e(t.summary)}</li>' for t in group)
        sections.append(f'<h2 id="{cat}">{_e(heading)}</h2><p>{_e(blurb)}</p>'
                        f'<ul class="katha-list">{items}</ul>')
    body = (f"<h1>{_e(_UI['index'])}</h1><p>{_e(_UI['intro'])}</p>"
            f'<p class="date">{_e(_UI["jump"])}: {nav}</p>' + "".join(sections))
    return _render(title=f"{_UI['index']} | Divine Astro", description=_UI["index_desc"],
                   path=page_path(None), alt=None, crumbs=[(_UI["crumb"], page_path(None))],
                   body=body, lang=HI, x_default=HI, translated=TRANSLATED,
                   lang_paths=_lang_paths(None))


def _page(slug: str) -> HTMLResponse:
    t = TEXTS.get(slug)
    if t is None:
        return _render(title=f"{_UI['nf']} | Divine Astro", description=_UI["nf_desc"],
                       path=page_path(slug), crumbs=[(_UI["crumb"], page_path(None))],
                       translated=TRANSLATED, lang_paths=_lang_paths(slug),
                       body=f'<h1>{_e(_UI["nf"])}</h1><p><a href="{page_path(None)}">'
                            f'{_e(_UI["all"])}</a></p>',
                       lang=HI, status=404, cache=False)
    title = f"{t.title} | {t.title_en} | Divine Astro"
    parts = [f"<p>{_html(p)}</p>" for p in t.intro]
    parts.insert(1, seo_pages._top_bar(lang=HI, path=page_path(slug), title=title))
    for s in t.sections:
        if s.heading:
            parts.append(f"<h2>{_e(s.heading)}</h2>")
        for kind, value in s.blocks:
            parts.append(_verse(value) if kind == "v" else f"<p>{_html(value)}</p>")
    if t.note:
        parts.append(f'<div class="box"><p>{_html(t.note)}</p></div>')
    related = "".join(f'<li><a href="{_e(page_path(r))}">{_e(TEXTS[r].title)}</a></li>'
                      for r in t.related)
    body = (f"<h1>{_e(t.title)}</h1>"
            f'<p class="date">{_e(_UI["source"])}: {_e(t.source)} · {_e(_UI["deity"])}: '
            f'{_e(DEITIES[t.deity])}</p>'
            + "".join(parts)
            + f'<p><small>{_e(_UI["fix"])} <a href="/feedback">{_e(_UI["fix_link"])}</a>'
              f'</small></p>'
            + f"<h2>{_e(_UI['cta_h'])}</h2><p>{_e(_free_line(_UI['cta_p']))}</p>"
            + seo_pages._cta("free-kundali", _UI["cta_kundali"], HI, big=True)
            + f'<p><a href="/hi/panchang">{_e(_UI["cta_panchang"])}</a></p>'
            + f'<h2>{_e(_UI["related"])}</h2><ul class="links">{related}'
              f'<li><a href="{page_path(None)}">{_e(_UI["all"])}</a></li></ul>')
    work = {"@type": "CreativeWork", "name": t.title, "alternateName": t.title_en,
            "inLanguage": "hi-IN", "description": t.summary, "author": t.source,
            "genre": CATEGORIES[t.category][0], "url": SITE_URL + page_path(slug),
            "publisher": {"@type": "Organization", "name": seo_pages.BRAND,
                          "url": SITE_URL + "/"}}
    return _render(title=title, description=f"{t.title} ({t.title_en}): {t.summary}",
                   path=page_path(slug), alt=None,
                   crumbs=[(_UI["crumb"], page_path(None)), (t.title, page_path(slug))],
                   body=body, lang=HI, extra_ld=(work,), x_default=HI,
                   translated=TRANSLATED, lang_paths=_lang_paths(slug))


@router.get("/bhakti", response_class=HTMLResponse)
def bhakti_index() -> HTMLResponse:
    return _index()


@router.get("/bhakti/{slug}", response_class=HTMLResponse)
def bhakti_page(slug: str) -> HTMLResponse:
    return _page(slug)
