"""Katha: retold mythological stories, the evening WhatsApp Channel post.

Each story lives twice: a teaser on the channel that stops at the turning
point, and the whole story on the site, so the "read more" click lands on our
own page (and the page itself can rank for "<story> ki katha" searches). The
pages exist in Hindi (canonical, /katha/<slug>) and English (/en/katha/<slug>),
with reciprocal hreflang.

The stories are retellings of episodes from the Itihasa, the Puranas and the
vrat kathas. Each names the text it comes from; nothing is invented that is
not in the source episode.

One story = one JSON file in app/katha_stories/<slug>.json (DIVASTRO-120; the
schema is checked by `_parse` below and described in deploy/daily_channels.md).
Every file is loaded and validated at import, so a malformed story fails CI
with its file name instead of breaking a page at night. The page, the index,
the sitemap and the channel rotation follow automatically.

    python -m app.katha --daily --dry-run              # what tonight's post would be
    python -m app.katha --daily                        # post today's pick (once per date)
    python -m app.katha --slug savitri-satyavan        # post one particular story
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import daily_state, i18n, seo_pages
from .astro import festivals
from .seo_pages import EN, HI, SITE_URL, _e, _render

router = APIRouter()
JOB = "katha"
STORY_DIR = Path(__file__).resolve().parent / "katha_stories"

# category -> (Hindi heading, English heading), in index order.
CATEGORIES: dict[str, tuple[str, str]] = {
    "vrat-katha": ("व्रत कथाएँ", "Vrat kathas"),
    "devi": ("देवी की कथाएँ", "Stories of the Devi"),
    "shiva": ("भगवान शिव की कथाएँ", "Stories of Shiva"),
    "vishnu": ("भगवान विष्णु की कथाएँ", "Stories of Vishnu"),
    "krishna": ("श्रीकृष्ण की कथाएँ", "Stories of Krishna"),
    "ram": ("श्रीराम की कथाएँ", "Stories of Rama"),
    "ganesh": ("श्री गणेश की कथाएँ", "Stories of Ganesha"),
    "mahabharata": ("महाभारत की कथाएँ", "Stories from the Mahabharata"),
    "rishi": ("ऋषि-मुनियों की कथाएँ", "Stories of the rishis"),
    "other": ("अन्य कथाएँ", "More stories"),
}

# Picking (see pick()).
FESTIVAL_GAP_DAYS = 300     # a festival story is not repeated within this many days
EVERGREEN_GAP_DAYS = 60     # off-season festival stories only once every evergreen is this fresh
WA_LIMIT = 4000             # a channel post must stay well inside WhatsApp's text limit


# --------------------------------------------------------------------------
# Stories and their schema
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Text:
    """One language's version of a story."""
    title: str
    source: str                # the text the episode comes from
    summary: str               # one line, for the index and meta description
    teaser: tuple[str, ...]    # channel paragraphs, ending on the turning point
    hook: str                  # the question that sends readers to the page
    rest: tuple[str, ...]      # the remainder, on the page after the teaser
    message: str               # what the story teaches
    note: str = ""             # e.g. the vrat it is read on


@dataclass(frozen=True)
class Story:
    slug: str
    category: str
    tags: tuple[str, ...]          # festivals.py observance keys it belongs to
    match_names: tuple[str, ...]   # exact festivals name_en values (a specific Ekadashi)
    hi: Text
    en: Text
    links: tuple[tuple[str, str, str, str], ...] = ()   # (hi label, hi path, en label, en path)

    @property
    def evergreen(self) -> bool:
        return not self.tags and not self.match_names

    def text(self, lang: str) -> Text:
        return self.hi if lang == HI else self.en


class StoryError(ValueError):
    """A story file that does not match the schema. The message starts with the file name."""


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_TEXT_KEYS = ("title", "source", "summary", "teaser", "hook", "rest", "message", "note")
_TOP_REQUIRED = {"slug", "category", "tags", "hi", "en"}
_TOP_OPTIONAL = {"match_names", "links"}


def festival_keys() -> set[str]:
    """Every observance key festivals.on() can return (switched-off ones excluded)."""
    keys = {s.key for s in festivals.RECURRING + festivals.FESTIVALS}
    keys |= {"ekadashi", "holi", "makar_sankranti", "lohri"}       # built outside the Spec lists
    return keys - set(festivals.OMITTED)


def festival_names() -> set[str]:
    """Every name_en festivals.on() can return."""
    names = {s.name_en for s in festivals.RECURRING + festivals.FESTIVALS
             if s.key not in festivals.OMITTED}
    names |= {en for en, _hi in festivals.EKADASHI_NAMES.values()}
    names |= {en for en, _hi in festivals.ADHIKA_EKADASHI_NAMES.values()}
    names |= {"Makar Sankranti", "Lohri"}
    if "holi" not in festivals.OMITTED:
        names.add("Holi")
    return names


def _markup_problem(text: str) -> str | None:
    """Paragraph markup is `*bold*` only: balanced single asterisks, no HTML."""
    if "**" in text:
        return "'**' (use single *bold*)"
    if text.count("*") % 2:
        return "an unbalanced '*'"
    if re.search(r"</?[A-Za-z]", text):
        return "HTML (only *bold* markup is allowed)"
    for bad in ("](", "__", "~~", "```"):
        if bad in text:
            return f"unsupported markup {bad!r} (only *bold*)"
    return None


def _parse_text(raw: object, where: str, lang: str) -> Text:
    def fail(msg: str) -> StoryError:
        return StoryError(f"{where}: {lang}: {msg}")

    if not isinstance(raw, dict):
        raise fail("must be an object")
    missing = [k for k in _TEXT_KEYS if k not in raw]
    extra = sorted(set(raw) - set(_TEXT_KEYS))
    if missing:
        raise fail(f"missing {', '.join(missing)}")
    if extra:
        raise fail(f"unknown field(s) {', '.join(extra)}")
    out: dict[str, object] = {}
    for key in _TEXT_KEYS:
        value = raw[key]
        if key in ("teaser", "rest"):
            if not isinstance(value, list) or not value:
                raise fail(f"{key} must be a non-empty list of paragraphs")
            for i, para in enumerate(value):
                if not isinstance(para, str) or not para.strip():
                    raise fail(f"{key}[{i}] must be a non-empty string")
                if (p := _markup_problem(para)):
                    raise fail(f"{key}[{i}] has {p}")
            out[key] = tuple(p.strip() for p in value)
        else:
            if not isinstance(value, str):
                raise fail(f"{key} must be a string")
            if key != "note" and not value.strip():
                raise fail(f"{key} must not be empty")
            if (p := _markup_problem(value)):
                raise fail(f"{key} has {p}")
            out[key] = value.strip()
    has_dev = bool(_DEVANAGARI.search(str(out["title"])))
    if lang == HI and not has_dev:
        raise fail("title is not in Hindi (Devanagari)")
    if lang == EN and has_dev:
        raise fail("title is in Devanagari; the en version must be English")
    return Text(**out)  # type: ignore[arg-type]


def _str_list(raw: object, where: str, field: str) -> tuple[str, ...]:
    if not isinstance(raw, list) or not all(isinstance(x, str) and x.strip() for x in raw):
        raise StoryError(f"{where}: {field} must be a list of non-empty strings")
    if len(set(raw)) != len(raw):
        raise StoryError(f"{where}: {field} has duplicates")
    return tuple(raw)


def _parse(raw: object, where: str, stem: str) -> Story:
    if not isinstance(raw, dict):
        raise StoryError(f"{where}: the file must hold one JSON object")
    missing = sorted(_TOP_REQUIRED - set(raw))
    extra = sorted(set(raw) - _TOP_REQUIRED - _TOP_OPTIONAL)
    if missing:
        raise StoryError(f"{where}: missing {', '.join(missing)}")
    if extra:
        raise StoryError(f"{where}: unknown field(s) {', '.join(extra)}")
    slug = raw["slug"]
    if not isinstance(slug, str) or not SLUG_RE.match(slug):
        raise StoryError(f"{where}: slug {slug!r} must be lowercase-words-with-hyphens")
    if slug != stem:
        raise StoryError(f"{where}: slug {slug!r} must match the file name ({stem}.json)")
    if raw["category"] not in CATEGORIES:
        raise StoryError(f"{where}: category {raw['category']!r} is not one of "
                         f"{', '.join(CATEGORIES)}")
    tags = _str_list(raw["tags"], where, "tags")
    unknown = sorted(set(tags) - festival_keys())
    if unknown:
        raise StoryError(f"{where}: tags {unknown} are not festival keys from "
                         f"app/astro/festivals.py")
    names = _str_list(raw.get("match_names", []), where, "match_names")
    unknown = sorted(set(names) - festival_names())
    if unknown:
        raise StoryError(f"{where}: match_names {unknown} are not festival name_en values from "
                         f"app/astro/festivals.py")
    links_raw = raw.get("links", [])
    if not isinstance(links_raw, list):
        raise StoryError(f"{where}: links must be a list")
    links = []
    for i, ln in enumerate(links_raw):
        if (not isinstance(ln, list) or len(ln) != 4
                or not all(isinstance(x, str) and x.strip() for x in ln)):
            raise StoryError(f"{where}: links[{i}] must be "
                             f"[hindi label, /hi/path, english label, /path]")
        if not (ln[1].startswith("/") and ln[3].startswith("/")) or "//" in ln[1] + ln[3]:
            raise StoryError(f"{where}: links[{i}] paths must be site paths starting with /")
        links.append(tuple(ln))
    story = Story(slug=slug, category=raw["category"], tags=tags, match_names=names,
                  hi=_parse_text(raw["hi"], where, HI), en=_parse_text(raw["en"], where, EN),
                  links=tuple(links))  # type: ignore[arg-type]
    for lang in (HI, EN):
        n = len(_teaser_text(story, lang))
        if n >= WA_LIMIT:
            raise StoryError(f"{where}: {lang} teaser post is {n} chars; keep it under {WA_LIMIT}")
    return story


def load(directory: Path | str | None = None) -> dict[str, Story]:
    """Every <slug>.json in `directory` (default $ASTRO_KATHA_DIR, else
    app/katha_stories), validated, keyed by slug, in slug order (the rotation
    order). Raises StoryError naming the file on the first bad one."""
    d = Path(directory or os.environ.get("ASTRO_KATHA_DIR") or STORY_DIR)
    stories: dict[str, Story] = {}
    for f in sorted(d.glob("*.json")):
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise StoryError(f"{f.name}: not valid UTF-8 JSON: {exc}") from None
        story = _parse(raw, f.name, f.stem)
        stories[story.slug] = story
    return stories



# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

_BOLD = re.compile(r"\*(.+?)\*")


def _html(text: str) -> str:
    """Our paragraph markup: *bold*, everything else escaped."""
    return _BOLD.sub(r"<strong>\1</strong>", _e(text))


def page_path(slug: str | None = None, lang: str = HI) -> str:
    base = "/katha" if lang == HI else "/en/katha"
    return f"{base}/{slug}" if slug else base


# DIVASTRO-121: katha is the one module whose canonical language is Hindi
# (/katha) with English at /en/katha. The other registry languages get NO katha
# routes until their stories are written: the picker sends them to the English
# copy. To add, say, Kannada: write the stories' Kannada text, add "/kn/katha"
# routes and a page_path() branch, put "kn" in TRANSLATED and in _lang_paths().
TRANSLATED = frozenset({HI, EN})


def _lang_paths(slug: str | None) -> dict[str, str]:
    """Each registry language's copy of a katha page, for hreflang and the picker."""
    out = {code: page_path(slug, EN) for code in i18n.CODES}
    out[HI] = page_path(slug, HI)
    return out


def sitemap_paths() -> list[str]:
    langs = [lang for lang in (HI, EN) if lang in TRANSLATED]
    return [page_path(None, lang) for lang in langs] + [
        page_path(s, lang) for s in STORIES for lang in langs]


def is_public_path(path: str) -> bool:
    return path in sitemap_paths()


_UI = {
    HI: {"index": "पौराणिक कथाएँ", "crumb": "कथाएँ", "source": "स्रोत",
         "lesson": "इस कथा का संदेश", "next": "आगे", "more": "और कथाएँ पढ़ें",
         "intro": "रामायण, महाभारत, पुराणों और व्रत कथाओं की प्रसिद्ध कथाएँ, सरल हिंदी में। हर "
                  "कथा के साथ उसका मूल स्रोत दिया गया है।",
         "index_desc": "रामायण, महाभारत, पुराण और व्रत कथाएँ सरल हिंदी में, मूल स्रोत सहित।",
         "title_suffix": " की कथा", "nf": "कथा नहीं मिली", "nf_desc": "यह कथा उपलब्ध नहीं है।",
         "all": "सभी कथाएँ देखें",
         "cta_h": "कथा पढ़ ली — अब अपनी कुंडली देखें",
         "cta_p": "जन्म तिथि, समय और स्थान से मुफ़्त कुंडली, दशा और ग्रह स्थिति। AI ज्योतिषी से पहले 10 सवाल फ्री — कोई कार्ड नहीं चाहिए।",
         "cta_kundali": "मुफ़्त कुंडली बनाएँ", "cta_panchang": "आज का पंचांग देखें"},
    EN: {"index": "Stories from the Puranas", "crumb": "Kathas", "source": "Source",
         "lesson": "What this story teaches", "next": "Read next", "more": "More stories",
         "intro": "Famous stories from the Ramayana, the Mahabharata, the Puranas and the vrat "
                  "kathas, retold in plain English. Each names the text it comes from.",
         "index_desc": "Stories from the Ramayana, Mahabharata, Puranas and vrat kathas in plain "
                       "English, with their sources.",
         "title_suffix": ": the story", "nf": "Story not found",
         "nf_desc": "This story is not available.", "all": "See all stories",
         "cta_h": "You have read the story — now see your own chart",
         "cta_p": "A free kundali with your dashas and planetary positions from your birth date, time and place. "
                  "Your first 10 questions to the AI astrologer are free — no card needed.",
         "cta_kundali": "Make my free kundali", "cta_panchang": "See today's Panchang"},
}


def _index(lang: str) -> HTMLResponse:
    ui = _UI[lang]
    sections = []
    for cat, names in CATEGORIES.items():
        group = [s for s in STORIES.values() if s.category == cat]
        if not group:
            continue
        items = "".join(
            f'<li><a href="{_e(page_path(s.slug, lang))}"><strong>{_e(s.text(lang).title)}'
            f'</strong></a> — {_e(s.text(lang).summary)} <small>({_e(s.text(lang).source)})</small>'
            f'</li>' for s in group)
        heading = names[0] if lang == HI else names[1]
        sections.append(f'<h2 id="{cat}">{_e(heading)}</h2><ul class="katha-list">{items}</ul>')
    body = f"<h1>{_e(ui['index'])}</h1><p>{_e(ui['intro'])}</p>" + "".join(sections)
    return _render(title=f"{ui['index']} | Divine Astro", description=ui["index_desc"],
                   path=page_path(None, lang), alt=page_path(None, EN if lang == HI else HI),
                   crumbs=[(ui["crumb"], page_path(None, lang))], body=body, lang=lang,
                   x_default=HI, translated=TRANSLATED, lang_paths=_lang_paths(None))


def _story(slug: str, lang: str) -> HTMLResponse:
    ui = _UI[lang]
    s = STORIES.get(slug)
    if s is None:
        return _render(title=f"{ui['nf']} | Divine Astro", description=ui["nf_desc"],
                       path=page_path(slug, lang), crumbs=[(ui["crumb"], page_path(None, lang))],
                       translated=TRANSLATED, lang_paths=_lang_paths(slug),
                       body=f'<h1>{_e(ui["nf"])}</h1><p><a href="{page_path(None, lang)}">'
                            f'{_e(ui["all"])}</a></p>',
                       lang=lang, status=404, cache=False)
    t = s.text(lang)
    paras = "".join(f"<p>{_html(p)}</p>" for p in (*t.teaser, *t.rest))
    links = "".join(f'<li><a href="{_e(ln[1] if lang == HI else ln[3])}">'
                    f'{_e(ln[0] if lang == HI else ln[2])}</a></li>' for ln in s.links)
    body = (f"<h1>{_e(t.title)}</h1>"
            f'<p class="date">{_e(ui["source"])}: {_e(t.source)}</p>'
            f"{paras}"
            f"<h2>{_e(ui['lesson'])}</h2><p>{_html(t.message)}</p>"
            + (f"<p>{_html(t.note)}</p>" if t.note else "")
            + f"<h2>{_e(ui['cta_h'])}</h2><p>{_e(ui['cta_p'])}</p>"
            + seo_pages._cta("free-kundali", ui["cta_kundali"], lang, big=True)
            + f'<p><a href="{_e(i18n.prefix(lang))}/panchang">{_e(ui["cta_panchang"])}</a></p>'
            + (f'<h2>{_e(ui["next"])}</h2><ul class="links">{links}'
               f'<li><a href="{page_path(None, lang)}">{_e(ui["more"])}</a></li></ul>'))
    article = {"@type": "Article", "headline": t.title,
               "inLanguage": "hi-IN" if lang == HI else "en-IN",
               "description": t.summary, "isBasedOn": t.source,
               "articleSection": CATEGORIES[s.category][0 if lang == HI else 1],
               "url": SITE_URL + page_path(slug, lang),
               "publisher": {"@type": "Organization", "name": seo_pages.BRAND,
                             "url": SITE_URL + "/"}}
    return _render(title=f"{t.title}{ui['title_suffix']} | Divine Astro",
                   description=f"{t.title}: {t.summary} {ui['source']}: {t.source}.",
                   path=page_path(slug, lang), alt=page_path(slug, EN if lang == HI else HI),
                   crumbs=[(ui["crumb"], page_path(None, lang)), (t.title, page_path(slug, lang))],
                   body=body, lang=lang, extra_ld=(article,), x_default=HI,
                   translated=TRANSLATED, lang_paths=_lang_paths(slug))


@router.get("/katha", response_class=HTMLResponse)
def katha_index() -> HTMLResponse:
    return _index(HI)


@router.get("/en/katha", response_class=HTMLResponse)
def katha_index_en() -> HTMLResponse:
    return _index(EN)


@router.get("/katha/{slug}", response_class=HTMLResponse)
def katha_page(slug: str) -> HTMLResponse:
    return _story(slug, HI)


@router.get("/en/katha/{slug}", response_class=HTMLResponse)
def katha_page_en(slug: str) -> HTMLResponse:
    return _story(slug, EN)


def share_text(path: str) -> str | None:
    """The WhatsApp share message for a katha page (share.seo_share_text)."""
    lang = EN if path.startswith("/en/") else HI
    parts = [p for p in path.removeprefix("/en").split("/") if p]
    if parts == ["katha"]:
        return ("Stories from the Ramayana, Mahabharata & Puranas · "
                "रामायण, महाभारत और पुराणों की कथाएँ:")
    if len(parts) == 2 and parts[0] == "katha" and parts[1] in STORIES:
        s = STORIES[parts[1]]
        return (f"Read the story of {s.en.title} · {s.hi.title} की कथा पढ़ें:" if lang == EN
                else f"{s.hi.title} की कथा पढ़ें · The story of {s.en.title}:")
    return None


# --------------------------------------------------------------------------
# The channel post
# --------------------------------------------------------------------------

def link(slug: str, campaign: str = "katha", lang: str = HI) -> str:
    q = urlencode({"utm_source": "whatsapp", "utm_medium": "channel", "utm_campaign": campaign})
    return f"{SITE_URL}{page_path(slug, lang)}?{q}"


def _teaser_text(s: Story, lang: str = HI) -> str:
    t = s.text(lang)
    head, more, src = (("📖 आज की कथा", "पूरी कथा पढ़ें", "स्रोत") if lang == HI
                       else ("📖 Today's story", "Read the whole story", "Source"))
    return "\n\n".join([
        f"*{head}: {t.title}*",
        *t.teaser,
        f"🙏 {t.hook}",
        f"👉 *{more}:*\n{link(s.slug, lang=lang)}",
        f"_{src}: {t.source}_",
    ])


def teaser(slug: str, lang: str = HI) -> str:
    """The WhatsApp post: title, the story up to its turning point, the hook,
    the link to the rest, the source. WhatsApp *bold* markup."""
    return _teaser_text(STORIES[slug], lang)


# Loaded last: validation renders each teaser to check its length.
STORIES: dict[str, Story] = load()


# --------------------------------------------------------------------------
# The daily pick
# --------------------------------------------------------------------------

def history(stories: dict[str, Story] | None = None) -> dict[str, dt.date]:
    """slug -> the day it was last posted, from daily_state's katha cache
    ({slug: {"posted": ISO datetime, "id": ..., ["day": ISO date]}})."""
    out = {}
    for slug in (STORIES if stories is None else stories):
        rec = daily_state.recall(JOB, slug)
        if not isinstance(rec, dict):
            continue
        raw = rec.get("day") or rec.get("posted")
        try:
            out[slug] = dt.date.fromisoformat(str(raw)[:10])
        except ValueError:
            continue
    return out


# The nine forms of Navadurga, one per night of Navratri, in order.
NAVDURGA = ("shailputri", "brahmacharini", "chandraghanta", "kushmanda", "skandamata",
            "katyayani", "kalaratri", "mahagauri", "siddhidatri")
NAVRATRI_KEYS = ("navratri", "chaitra_navratri")


def pick(day: dt.date, stories: dict[str, Story] | None = None,
         posted: dict[str, dt.date] | None = None) -> str | None:
    """The story for `day`'s evening post.

    1. A story belonging to one of today's observances (festivals.on(day), New
       Delhi): its `match_names` hold the observance's name_en, or its `tags`
       the observance key; not posted in the last FESTIVAL_GAP_DAYS days.
       A name match beats a tag match, a major festival beats a minor one,
       then the longest-unposted, then rotation order.
    2. Otherwise an evergreen story (no tags, no match_names): the first never
       posted in rotation order, else the least recently posted.
    3. A festival story is used on a day that is not its own only when every
       evergreen story has been posted within EVERGREEN_GAP_DAYS (or there are
       none): then the never-posted first, else the least recently posted of all.
    """
    stories = STORIES if stories is None else stories
    if not stories:
        return None
    posted = history(stories) if posted is None else posted
    order = {slug: i for i, slug in enumerate(stories)}

    def fresh(slug: str, gap: int) -> bool:
        last = posted.get(slug)
        return last is not None and (day - last).days < gap

    def staleness(slug: str) -> tuple:
        last = posted.get(slug)
        return (last is not None, last or dt.date.min, order[slug])

    # Navratri: the nine nights each have their own form of the Devi, in a
    # fixed order (Shailputri on the first day … Siddhidatri on the ninth), so
    # those days get their story by position, not by tag. festivals.on() marks
    # only the first day, so find the start within the last eight days.
    for start_key in NAVRATRI_KEYS:
        for o in festivals.observances(day - dt.timedelta(days=8), day):
            if o.get("key") != start_key:
                continue
            n = (day - dt.date.fromisoformat(o["date"])).days
            if 0 <= n < len(NAVDURGA) and NAVDURGA[n] in stories \
                    and not fresh(NAVDURGA[n], FESTIVAL_GAP_DAYS):
                return NAVDURGA[n]

    best: tuple | None = None
    for o in festivals.on(day):
        for slug, s in stories.items():
            by_name = o.get("name_en") in s.match_names
            if not (by_name or o.get("key") in s.tags) or fresh(slug, FESTIVAL_GAP_DAYS):
                continue
            rank = (not by_name, not o.get("major"), *staleness(slug))
            if best is None or rank < best:
                best = rank
    if best is not None:
        return list(stories)[best[-1]]

    evergreen = [slug for slug, s in stories.items() if s.evergreen]
    if evergreen:
        choice = min(evergreen, key=staleness)
        if not fresh(choice, EVERGREEN_GAP_DAYS):
            return choice
    return min(stories, key=staleness)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _post(slug: str, day: dt.date, daily: bool) -> int:
    """Send one story to the channel. 0 posted, 1 failed, 2 not configured."""
    from . import whatsapp_channel as W           # lazy: only the CLI needs the connector

    token = os.environ.get("ASTRO_WA_TOKEN", "").strip()
    chan = os.environ.get("ASTRO_WA_CHANNEL_LINK", "").strip()
    if not token or not chan:
        print("katha: ASTRO_WA_TOKEN and ASTRO_WA_CHANNEL_LINK must both be set "
              "(see deploy/daily_channels.md section 5)", file=sys.stderr)
        return 2
    try:
        wait_s = float(os.environ.get("ASTRO_WA_WAIT") or 60)
    except ValueError:
        wait_s = 60.0
    client = W.Client(os.environ.get("ASTRO_WA_URL", "").strip() or W.DEFAULT_URL, token)
    try:
        W.wait_connected(client, wait_s)
        jid = W.channel_jid(client, chan)
        try:
            msg_id = client.post(jid, teaser(slug), None, None)
        except W.ConnectorError as exc:
            if exc.status == 409:
                raise W.Unlinked(str(exc)) from None
            raise
        now = dt.datetime.now().isoformat(timespec="seconds")
        try:
            daily_state.remember(JOB, slug, {"posted": now, "id": msg_id, "day": day.isoformat()})
            if daily:
                daily_state.mark(JOB, day, "story", {"slug": slug, "id": msg_id})
        except OSError as exc:
            print(f"katha: posted, but could not record it: {exc}", file=sys.stderr)
        print(f"katha: posted {slug} for {day} (message {msg_id})")
        return 0
    except W.Unlinked as exc:
        print(f"katha: NOT POSTED {slug} for {day}: {exc}", file=sys.stderr)
        W.alert_owner(str(exc), day)
        return 1
    except W.ConnectorError as exc:
        print(f"katha: FAILED {slug} for {day}: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:                            # e.g. the state dir is not writable
        print(f"katha: FAILED {slug} for {day}: "
              f"{client._redact(f'{type(exc).__name__}: {exc}')}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.katha", description=__doc__.split("\n\n")[0])
    which = ap.add_mutually_exclusive_group(required=True)
    which.add_argument("--daily", action="store_true", help="post today's pick, once per date")
    which.add_argument("--slug", choices=sorted(STORIES), help="post this story")
    ap.add_argument("--date", help="with --daily: YYYY-MM-DD (default: today in IST)")
    ap.add_argument("--dry-run", action="store_true", help="print the post, send nothing")
    ap.add_argument("--force", action="store_true", help="post even if already posted")
    args = ap.parse_args(argv)

    try:
        day = dt.date.fromisoformat(args.date) if args.date else daily_state.today_ist()
    except ValueError as exc:
        print(f"katha: {exc}", file=sys.stderr)
        return 2

    if args.slug:
        slug = args.slug
        done = daily_state.recall(JOB, slug)
    else:
        rec = daily_state.sent(JOB, day).get("story")
        done = rec if isinstance(rec, dict) and rec.get("slug") in STORIES else None
        # Already posted for this date: that story, so a dry run or --force
        # shows / re-sends what went out rather than the next pick.
        slug = done["slug"] if done else pick(day)
        if slug is None:
            print("katha: no stories to pick from", file=sys.stderr)
            return 1

    if args.dry_run:
        text = teaser(slug)
        print(f"----- katha {slug} for {day} ({len(text)} chars, WhatsApp *bold*)"
              + (" [already posted]" if done else "") + " -----")
        print(text)
        return 0
    if done and not args.force:
        what = f"{slug} already posted" if args.slug else f"already posted for {day} ({slug})"
        print(f"katha: {what}; nothing to do (--force to post again)")
        return 0
    return _post(slug, day, daily=args.daily)


if __name__ == "__main__":
    raise SystemExit(main())
