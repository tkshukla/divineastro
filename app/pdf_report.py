"""PDF export — the customer's question history and their chart, as files they keep.

Engine: **Typst**, driven directly through the `typst` Python package.

Why Typst and not something new:

* It is already installed — `stellium` renders its own reports with it, so the
  wheel is not being reinvented and no new dependency enters the image.
* It lays out real documents (running headers, page numbers, breakable blocks,
  tables that survive a page boundary) which is exactly what a 30-question
  history needs and what a draw-a-box PDF library (reportlab, fpdf2) makes you
  write by hand.
* It rasterises SVG natively, so stellium's chart wheel and the North/South
  Indian Vedic squares go straight into the page as vectors.

Why not `stellium.ReportBuilder`, which also emits PDF:

* `ReportBuilder.from_chart()` requires a chart. The question-history export has
  no chart at all — it is rows from a database — so half the feature could not
  use it.
* Its section vocabulary is table / key-value / text / svg. A long markdown
  answer with headings, bold runs and bullets is not expressible in it, and the
  answers are the entire point of the export.
* Using it for one route and hand-rolled Typst for the other would give the
  customer two documents that do not look like they came from the same product.

So both routes share one template family and one design.

**Devanagari.** The fonts stellium bundles (EB Garamond, IBM Plex, Spectral,
Cinzel, the Noto symbol faces) contain **no** Devanagari — Hindi answers would
be tofu on the bundled set alone. Typst also searches the host's system fonts,
and every font family named in `_DEVANAGARI` below is checked at import time;
on Windows `Nirmala UI` ships with the OS and renders Hindi correctly, shaping
and all. `pdf_font_report()` says which one was found, and
`ASTRO_PDF_FONT_PATHS` (os.pathsep-separated directories) adds font directories
for deployments — a Linux container needs `fonts-noto-devanagari` or the font
dropped into such a directory.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

try:                                    # typst ships as a stellium dependency
    import typst
except ImportError:                     # pragma: no cover - defensive
    typst = None                        # type: ignore[assignment]

from .chart_service import SIDEREAL_YEAR, VIMSHOTTARI, dms, vimshottari, wheel_svg

# --------------------------------------------------------------------------
# Fonts
# --------------------------------------------------------------------------

# Serif body, in fallback order. Typst falls back per character, so a Hindi
# answer inside an English document picks up the Devanagari face automatically.
_DEVANAGARI = ("Nirmala UI", "Noto Sans Devanagari", "Noto Serif Devanagari",
               "Mangal", "Sanskrit Text", "Aparajita", "Kokila", "Utsaah",
               "Lohit Devanagari", "Samyak Devanagari", "FreeSerif")

BODY_FONTS = ("EB Garamond", "IBM Plex Serif", *_DEVANAGARI,
              "Noto Sans Symbols", "Noto Sans Symbols 2")
DISPLAY_FONTS = ("Cinzel", "EB Garamond", *_DEVANAGARI)
MONO_FONTS = ("IBM Plex Mono", *_DEVANAGARI)


def font_paths() -> list[str]:
    """Font directories handed to Typst: stellium's bundle plus any extras.

    System fonts are searched too (`ignore_system_fonts` stays False), which is
    how Devanagari is found on a machine that has it.
    """
    paths: list[str] = []
    try:
        from stellium.presentation import typst_runtime

        paths.extend(typst_runtime.font_paths())
    except Exception:                   # pragma: no cover - stellium layout change
        pass
    for extra in os.environ.get("ASTRO_PDF_FONT_PATHS", "").split(os.pathsep):
        if extra.strip() and os.path.isdir(extra.strip()):
            paths.append(extra.strip())
    return paths


_FONT_SUFFIXES = (".ttf", ".otf", ".ttc", ".otc")


def _font_file_keys() -> set[str]:
    """Squashed stems of every font file on the usual search paths.

    Typst does its own font discovery and does not expose the result, so this
    walks the same directories Typst does and matches on filename. It answers
    the only question that matters — is there a Devanagari face here at all —
    without dragging in fontTools to read name tables.
    """
    directories = [
        *font_paths(),
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
        os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
        "/usr/share/fonts", "/usr/local/share/fonts", "/Library/Fonts",
        "/System/Library/Fonts", os.path.expanduser("~/Library/Fonts"),
        os.path.expanduser("~/.fonts"), os.path.expanduser("~/.local/share/fonts"),
    ]
    keys: set[str] = set()
    for directory in directories:
        if not os.path.isdir(directory):
            continue
        try:
            for root, _dirs, filenames in os.walk(directory):
                for filename in filenames:
                    if filename.lower().endswith(_FONT_SUFFIXES):
                        keys.add(_squash(Path(filename).stem))
        except OSError:
            continue
    return keys


def _squash(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def devanagari_font() -> str | None:
    """The first Devanagari family that looks present on this machine.

    Matching is two-way containment on squashed names because a family and its
    file rarely agree: `Nirmala UI` ships as `Nirmala.ttc`.
    """
    keys = _font_file_keys()
    for family in _DEVANAGARI:
        wanted = _squash(family)
        for key in keys:
            if len(key) < 5:
                continue
            # a style suffix is noise: NotoSansDevanagari-Regular -> ...devanagari
            trimmed = key.split("regular")[0] or key
            if wanted in trimmed or trimmed in wanted:
                return family
    return None


def pdf_font_report() -> dict:
    """Diagnostics for the export — surfaced by /api/pdf/fonts."""
    found = devanagari_font()
    return {
        "engine": "typst",
        "typst_available": typst is not None,
        "font_paths": font_paths(),
        "devanagari_font": found,
        "devanagari_ok": bool(found),
        "note": (
            f"Hindi answers render with {found}."
            if found else
            "No Devanagari font was found — Hindi answers will render as empty "
            "boxes. Install a Devanagari family (e.g. Noto Sans Devanagari) or "
            "point ASTRO_PDF_FONT_PATHS at a directory containing one."
        ),
    }


# --------------------------------------------------------------------------
# Markdown -> block model
#
# The answers are markdown produced by our own engine and, optionally, rewritten
# by an LLM told to keep that structure: ### headings, **bold**, - bullets.
# Rather than pull in a markdown library and then a second translation layer,
# this parses the subset directly into blocks the Typst template renders.
# Nothing here ever emits Typst syntax — every string travels to the template
# inside data.json and is inserted as a plain string, so no answer text can be
# interpreted as markup or escape the document.
# --------------------------------------------------------------------------

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_NUMBER = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
_RULE = re.compile(r"^\s*(?:-{3,}|_{3,}|\*{3,})\s*$")
_QUOTE = re.compile(r"^\s*>\s?(.*)$")
_FENCE = re.compile(r"^\s*```")

_INLINE = re.compile(
    r"\*\*\*(?P<bi>[^*]+?)\*\*\*"
    r"|\*\*(?P<b>.+?)\*\*"
    r"|__(?P<b2>.+?)__"
    r"|(?<![\w*])\*(?P<i>[^*\n]+?)\*(?!\*)"
    r"|(?<![\w_])_(?P<i2>[^_\n]+?)_(?!\w)"
    r"|`(?P<code>[^`\n]+?)`"
    r"|\[(?P<link>[^\]\n]+?)\]\((?P<url>[^)\s]+)\)",
    re.S,
)


def _span(text: str, bold: bool = False, italic: bool = False,
          code: bool = False) -> dict:
    return {"t": text, "b": bold, "i": italic, "c": code}


def inline_spans(text: str) -> list[dict]:
    """Split one line of markdown into styled runs."""
    spans: list[dict] = []
    cursor = 0
    for match in _INLINE.finditer(text):
        if match.start() > cursor:
            spans.append(_span(text[cursor:match.start()]))
        groups = match.groupdict()
        if groups["bi"] is not None:
            spans.append(_span(groups["bi"], bold=True, italic=True))
        elif groups["b"] is not None:
            spans.append(_span(groups["b"], bold=True))
        elif groups["b2"] is not None:
            spans.append(_span(groups["b2"], bold=True))
        elif groups["i"] is not None:
            spans.append(_span(groups["i"], italic=True))
        elif groups["i2"] is not None:
            spans.append(_span(groups["i2"], italic=True))
        elif groups["code"] is not None:
            spans.append(_span(groups["code"], code=True))
        else:                                   # a link — keep the label
            spans.append(_span(groups["link"], italic=True))
        cursor = match.end()
    if cursor < len(text):
        spans.append(_span(text[cursor:]))
    return [s for s in spans if s["t"]] or [_span("")]


def markdown_blocks(text: str) -> list[dict]:
    """Markdown to a flat list of blocks the Typst template knows how to draw."""
    blocks: list[dict] = []
    paragraph: list[str] = []
    listing: dict | None = None

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append({"kind": "p", "spans": inline_spans(" ".join(paragraph))})
            paragraph = []

    def flush_list() -> None:
        nonlocal listing
        if listing:
            blocks.append(listing)
            listing = None

    def flush() -> None:
        flush_paragraph()
        flush_list()

    lines = (text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]

        if _FENCE.match(line):
            flush()
            index += 1
            body: list[str] = []
            while index < len(lines) and not _FENCE.match(lines[index]):
                body.append(lines[index])
                index += 1
            blocks.append({"kind": "code", "text": "\n".join(body)})
            index += 1
            continue

        if not line.strip():
            flush()
            index += 1
            continue

        if _RULE.match(line):
            flush()
            blocks.append({"kind": "hr"})
            index += 1
            continue

        heading = _HEADING.match(line)
        if heading:
            flush()
            blocks.append({
                "kind": "h",
                "level": min(len(heading.group(1)), 4),
                "spans": inline_spans(heading.group(2).strip()),
            })
            index += 1
            continue

        quote = _QUOTE.match(line)
        if quote:
            flush()
            blocks.append({"kind": "quote", "spans": inline_spans(quote.group(1))})
            index += 1
            continue

        bullet = _BULLET.match(line)
        number = _NUMBER.match(line)
        if bullet or number:
            flush_paragraph()
            indent = len(bullet.group(1) if bullet else number.group(1))
            depth = min(indent // 2, 2)
            if bullet:
                marker, wanted = "\u2022", "ul"
                body_text = bullet.group(2)
            else:
                marker, wanted = f"{number.group(2)}.", "ol"
                body_text = number.group(3)
            if listing is None or listing["kind"] != wanted:
                flush_list()
                listing = {"kind": wanted, "items": []}
            listing["items"].append({
                "marker": marker, "depth": depth,
                "spans": inline_spans(body_text.strip()),
            })
            index += 1
            continue

        flush_list()
        paragraph.append(line.strip())
        index += 1

    flush()
    return blocks


# --------------------------------------------------------------------------
# Typst templates
#
# Every piece of user data arrives via data.json and is inserted as a *string*,
# which Typst renders literally. There is no string interpolation into Typst
# source anywhere in this module.
# --------------------------------------------------------------------------

_PRELUDE = r"""
#let d = json(sys.inputs.data)

#let INK   = rgb("#1d1c26")
#let MUTED = rgb("#6b6879")
#let RULE  = rgb("#d8d3c8")
#let ACC   = rgb("#8a6a2f")
#let WASH  = rgb("#faf7f1")

#let BODY = @@BODY@@
#let DISP = @@DISPLAY@@
#let MONO = @@MONO@@

#set document(title: d.title, author: d.brand)
#set text(font: BODY, size: 10.2pt, fill: INK, lang: d.at("lang", default: "en"))
#set par(leading: 0.74em, spacing: 0.9em)
#set block(spacing: 0.9em)

#let spans(ss) = {
  for s in ss {
    if s.c { raw(s.t) }
    else if s.b and s.i { strong(emph(s.t)) }
    else if s.b { strong(s.t) }
    else if s.i { emph(s.t) }
    else { s.t }
  }
}

#let blocks(bs) = {
  for b in bs {
    if b.kind == "h" {
      // Deliberately the body face, not DISP: the display font is capitals-only,
      // which is right for a cover and unreadable for a run of sub-headings.
      block(above: 1.35em, below: 0.55em,
        text(size: (12.4pt, 11.4pt, 10.8pt, 10.4pt).at(b.level - 1),
             weight: "semibold", fill: ACC, spans(b.spans)))
    } else if b.kind == "p" {
      block(spans(b.spans))
    } else if b.kind == "quote" {
      block(inset: (left: 10pt), stroke: (left: 2pt + RULE),
        text(fill: MUTED, style: "italic", spans(b.spans)))
    } else if b.kind == "code" {
      block(width: 100%, fill: WASH, inset: 7pt, radius: 2pt,
        text(font: MONO, size: 8.6pt, raw(b.text)))
    } else if b.kind == "hr" {
      block(above: 0.9em, below: 0.9em, line(length: 100%, stroke: 0.5pt + RULE))
    } else {
      block(above: 0.45em, below: 0.45em, {
        for it in b.items {
          pad(left: 8pt + it.depth * 12pt,
            grid(columns: (13pt, 1fr), gutter: 0pt,
              text(fill: ACC, it.marker), spans(it.spans)))
        }
      })
    }
  }
}

#let chip(label, value) = box(
  inset: (x: 5pt, y: 2.5pt), radius: 2pt, fill: WASH, stroke: 0.4pt + RULE,
  text(size: 7.6pt, fill: MUTED, label + " " + upper(value)))

#let kvtable(rows) = table(
  columns: (auto, 1fr), stroke: none, align: left,
  inset: (x: 0pt, y: 4.5pt), column-gutter: 18pt,
  ..rows.map(r => (
    text(fill: MUTED, size: if d.lang == "hi" { 11.2pt } else { 9.2pt }, r.at(0)),
    text(size: if d.lang == "hi" { 11.2pt } else { 10pt }, r.at(1))
  )).flatten())

// `cols` is one number per column: 0 means auto, n means n*1fr. Giving at least
// one column a fraction is what makes the table fill the measure instead of
// huddling against the left margin.
#let datatable(t) = table(
  columns: t.cols.map(c => if c == 0 { auto } else { c * 1fr }),
  stroke: (bottom: 0.4pt + RULE),
  inset: (x: 6pt, y: 5.5pt),
  align: left,
  fill: (x, y) => if y == 0 { WASH } else { none },
  table.header(..t.headers.map(h =>
    text(size: if d.lang == "hi" { 10.5pt } else { 8.8pt }, weight: "semibold", fill: MUTED, upper(h)))),
  ..t.rows.flatten().map(c => text(size: if d.lang == "hi" { 10.5pt } else { 9.2pt }, c)))

#let cover(subtitle) = page(margin: (x: 62pt, y: 96pt), header: none, footer: none)[
  #align(center)[
    #text(font: DISP, size: 21pt, weight: "semibold", tracking: 2pt, d.brand)
    #v(4pt)
    #line(length: 34%, stroke: 0.6pt + ACC)
    #v(46pt)
    #text(font: DISP, size: 27pt, d.title)
    #v(10pt)
    #text(size: 13pt, fill: MUTED, subtitle)
    #v(52pt)
    #kvtable(d.cover)
    #v(1fr)
    #text(size: 8.4pt, fill: MUTED, d.footer)
  ]
]

#let running = context {
  if counter(page).get().first() > 0 {
    grid(columns: (1fr, auto),
      text(size: 8pt, fill: MUTED, d.brand + "  \u{00b7}  " + d.title),
      text(size: 8pt, fill: MUTED, counter(page).display()))
    v(-6pt)
    line(length: 100%, stroke: 0.4pt + RULE)
  }
}
"""

_REMEDIES_BODY = """
#cover(d.subject)
#counter(page).update(1)
#set page(paper: "a4", margin: (x: 54pt, top: 64pt, bottom: 58pt), header: running)

#let section(title) = block(above: 16pt, below: 8pt, {
  text(font: DISP, size: 12.5pt, fill: ACC, title)
  v(3pt)
  line(length: 100%, stroke: 0.6pt + RULE)
})

#section("Birth details")
#kvtable(d.birth)

#section("Recommended gemstones")
#datatable(d.gemstones)

#section("Active dasha remedies (" + d.mahadasha + " Mahadasha)")
#block(width: 100%, fill: WASH, inset: 12pt, radius: 4pt, stroke: 0.5pt + RULE)[
  #text(weight: "bold", fill: ACC, "Recommended Mantra:") \
  #text(font: BODY, size: 10.5pt, d.mantra) \
  #v(8pt)
  #text(weight: "bold", fill: ACC, "Charity & Actions:") \
  #text(d.charity)
]

#section("Personalized spiritual guidance")
#blocks(d.guidance)
"""

_QUESTIONS_BODY = """
#cover(d.subject)
#counter(page).update(1)
#set page(paper: "a4", margin: (x: 54pt, top: 64pt, bottom: 58pt), header: running)

#for q in d.items {
  block(breakable: true, width: 100%, above: 0pt, below: 22pt)[
    #grid(columns: (1fr, auto), align: (left + horizon, right + horizon),
      text(font: DISP, size: 9pt, fill: ACC, "QUESTION " + str(q.n)),
      text(size: 8.2pt, fill: MUTED, q.asked_at))
    #v(2pt)
    #line(length: 100%, stroke: 0.7pt + RULE)
    #v(7pt)
    #text(size: 13pt, weight: "medium", q.question)
    #v(6pt)
    #{ for c in q.chips { chip(c.at(0), c.at(1)); h(5pt) } }
    #v(9pt)
    #blocks(q.blocks)
  ]
}

#if d.items.len() == 0 [
  #v(40pt)
  #align(center, text(fill: MUTED, style: "italic",
    "No questions have been asked on this account yet."))
]
"""

_CHART_BODY = """
#cover(d.subject)
#counter(page).update(1)
#set page(paper: "a4", margin: (x: 54pt, top: 64pt, bottom: 58pt), header: running)

#let section(title) = block(above: 16pt, below: 8pt, {
  text(font: DISP, size: 12.5pt, fill: ACC, title)
  v(3pt)
  line(length: 100%, stroke: 0.6pt + RULE)
})

#section(d.texts.birth_details)
#kvtable(d.birth)

#if d.note != "" [
  #v(6pt)
  #block(inset: (left: 10pt), stroke: (left: 2pt + RULE),
    text(size: 8.8pt, fill: MUTED, style: "italic", d.note))
]

#let vedic(path, label) = align(center)[
  #image(path, width: 100%)
  #v(3pt)
  #text(size: 8.2pt, fill: MUTED, label)
]

#if d.d1_north != "" or d.d1_south != "" {
  section(d.texts.d1_title)
  let cells = ()
  if d.d1_north != "" { cells.push(vedic(d.d1_north, d.texts.north_indian)) }
  if d.d1_south != "" { cells.push(vedic(d.d1_south, d.texts.south_indian)) }
  grid(columns: cells.map(c => 1fr), gutter: 14pt, ..cells)
}

#if d.d9_north != "" or d.d9_south != "" {
  section(d.texts.d9_title)
  let cells = ()
  if d.d9_north != "" { cells.push(vedic(d.d9_north, d.texts.north_indian)) }
  if d.d9_south != "" { cells.push(vedic(d.d9_south, d.texts.south_indian)) }
  grid(columns: cells.map(c => 1fr), gutter: 14pt, ..cells)
}

#section(d.texts.vargas_title)
#datatable(d.vargas)

#section(d.texts.yogas_title)
#datatable(d.yogas)

#section(d.texts.planetary_positions)
#datatable(d.positions)

#section(d.texts.houses)
#datatable(d.houses)

#if d.aspects.rows.len() > 0 [
  #section(d.texts.aspects)
  #datatable(d.aspects)
]

#if d.dasha != none [
  #section(d.texts.dasha)
  #kvtable(d.dasha.summary)
  #v(8pt)
  #datatable(d.dasha.table)
  
  #v(8pt)
  #section(d.texts.antardasha_title)
  #datatable(d.dasha.antardasha)
]

#if d.houses_detailed.len() > 0 [
  #section(d.texts.houses_detailed_title)
  #blocks(d.houses_detailed)
]

#if d.planets_detailed.len() > 0 [
  #section(d.texts.planets_detailed_title)
  #blocks(d.planets_detailed)
]

#if d.remedies_detailed.len() > 0 [
  #section(d.texts.remedies_detailed_title)
  #blocks(d.remedies_detailed)
]

#if d.varshphal.len() > 0 [
  #section(d.texts.varshphal_title)
  #grid(
    columns: (auto, 1fr),
    gutter: 12pt,
    ..d.varshphal.map(m => (
      text(weight: "bold", fill: ACC, m.at(0)),
      blocks(m.at(1))
    )).flatten()
  )
]

#if d.upcoming.len() > 0 [
  #section(d.texts.upcoming_title)
  #blocks(d.upcoming)
]

#if d.house_summary.len() > 0 [
  #section(d.texts.house_summary_title)
  #blocks(d.house_summary)
]
"""


def _typst_string_array(values) -> str:
    return "(" + ", ".join(json.dumps(v) for v in values) + ",)"


def _template(body: str) -> str:
    """The prelude with the font stacks substituted in, then the document body.

    Plain `replace` rather than %-formatting or f-strings: the Typst source is
    full of `%` (every `width: 100%`) and `{}` (every code block).
    """
    return (
        _PRELUDE
        .replace("@@BODY@@", _typst_string_array(BODY_FONTS))
        .replace("@@DISPLAY@@", _typst_string_array(DISPLAY_FONTS))
        .replace("@@MONO@@", _typst_string_array(MONO_FONTS))
        + body
    )


def _compile(body: str, data: dict, files: dict[str, str] | None = None) -> bytes:
    """Write a throwaway Typst project and compile it to PDF bytes."""
    if typst is None:                   # pragma: no cover - defensive
        raise RuntimeError("The `typst` package is not installed; PDF export is unavailable.")
    root = tempfile.mkdtemp(prefix="astro_pdf_")
    try:
        for name, content in (files or {}).items():
            with open(os.path.join(root, name), "w", encoding="utf-8") as fh:
                fh.write(content)
        with open(os.path.join(root, "data.json"), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        entry = os.path.join(root, "report.typ")
        with open(entry, "w", encoding="utf-8") as fh:
            fh.write(_template(body))
        return typst.compile(entry, root=root, font_paths=font_paths(),
                             sys_inputs={"data": "data.json"})
    finally:
        shutil.rmtree(root, ignore_errors=True)


# --------------------------------------------------------------------------
# Route 1 — question history
# --------------------------------------------------------------------------

def _local(value: dt.datetime | None) -> str:
    if value is None:
        return ""
    return value.strftime("%d %b %Y, %H:%M")


def questions_pdf(rows, *, brand: str, site: str, user_name: str,
                  user_email: str = "", subtitle: str = "") -> bytes:
    """A PDF of one user's questions and answers.

    `rows` are QuestionLog objects, already filtered to that user by the caller.
    """
    today = dt.datetime.now()
    languages = {(r.language or "en") for r in rows}
    items = []
    for number, row in enumerate(rows, start=1):
        chips = []
        if row.topic:
            chips.append(["Topic", str(row.topic).replace("_", " ")])
        if row.verdict:
            chips.append(["Verdict", str(row.verdict)])
        if (row.language or "en") != "en":
            chips.append(["Language", str(row.language)])
        items.append({
            "n": number,
            "question": (row.question or "").strip() or "(no question recorded)",
            "asked_at": _local(row.created_at),
            "chips": chips,
            "blocks": markdown_blocks(row.answer or row.answer_engine or ""),
        })

    cover = [["Prepared for", user_name or user_email or "Guest"]]
    if user_email and user_email != user_name:
        cover.append(["Account", user_email])
    cover.append(["Questions", str(len(items))])
    cover.append(["Generated", today.strftime("%d %B %Y")])

    data = {
        "brand": brand,
        "title": "Questions & Answers",
        "subject": subtitle or "Your consultation record",
        "lang": "hi" if languages == {"hi"} else "en",
        "cover": cover,
        "footer": f"{brand} \u00b7 {site}",
        "items": items,
    }
    return _compile(_QUESTIONS_BODY, data)


# --------------------------------------------------------------------------
# Route 2 — chart report
# --------------------------------------------------------------------------

_SVG_ENCODINGS = ("utf-8", "cp1252", "latin-1")


def _read_svg(path: str) -> str:
    """Read an SVG stellium wrote.

    `draw_vedic()` opens its output with the platform's default encoding, so on
    a Windows host the degree sign lands as cp1252 byte 0xB0 and Typst — which
    only accepts UTF-8 — refuses the file. Decode defensively and hand Typst
    UTF-8 whatever the source was.
    """
    raw = Path(path).read_bytes()
    for encoding in _SVG_ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


class VargaChartWrapper:
    def __init__(self, original_chart, division: str):
        self.metadata = getattr(original_chart.chart, "metadata", {})
        self.datetime = getattr(original_chart.chart, "datetime", None)
        self.location = getattr(original_chart.chart, "location", None)
        
        # Compute the varga signs
        from .astro.vargas import divisional_chart
        v_data = divisional_chart(original_chart, division)
        lagna_sign = v_data["lagna"]["sign"] if isinstance(v_data["lagna"], dict) else v_data["lagna"]
        
        from .astro.panchang import SIGNS
        lagna_idx = SIGNS.index(lagna_sign)
        
        class HouseMock:
            cusps = [lagna_idx * 30.0] * 12
        self._houses = HouseMock()
        
        self._planets = []
        class PlanetMock:
            def __init__(self, name, longitude, speed_longitude):
                self.name = name
                self.longitude = longitude
                self.speed_longitude = speed_longitude
                
        for pl_name, pl_info in v_data["positions"].items():
            if pl_name == "Lagna":
                continue
            pl_sign = pl_info["sign"]
            pl_idx = SIGNS.index(pl_sign)
            
            orig_pl = original_chart.chart.get_object(pl_name)
            speed = -1.0 if (orig_pl and orig_pl.speed_longitude and orig_pl.speed_longitude < 0) else 1.0
            
            self._planets.append(PlanetMock(pl_name, pl_idx * 30.0 + 15.0, speed))
            
    def get_houses(self):
        return self._houses
        
    def get_planets(self):
        return self._planets
        
    def get_object(self, name):
        for p in self._planets:
            if p.name == name:
                return p
        return None


def _vedic_svgs(session) -> dict[str, str]:
    """Rashi (D1) and Navamsa (D9) squares for North and South Indian, as SVG source."""
    out: dict[str, str] = {}
    scratch = tempfile.mkdtemp(prefix="astro_vedic_")
    try:
        from stellium.visualization.vedic.north_indian import NorthIndianRenderer
        from stellium.visualization.vedic.south_indian import SouthIndianRenderer
        
        # 1. Rashi D1
        for style, name in (("north_indian", "d1_north"), ("south_indian", "d1_south")):
            target = os.path.join(scratch, f"{name}.svg")
            try:
                session.chart.draw_vedic(target, style=style, theme="classic", size=520)
                out[name] = _read_svg(target)
            except Exception:
                pass
                
        # 2. Navamsa D9
        try:
            d9_wrapper = VargaChartWrapper(session, "D9")
            for name, renderer_cls in (("d9_north", NorthIndianRenderer), ("d9_south", SouthIndianRenderer)):
                target = os.path.join(scratch, f"{name}.svg")
                try:
                    renderer = renderer_cls(size=520, theme="classic")
                    renderer.render_to_file(d9_wrapper, target)
                    out[name] = _read_svg(target)
                except Exception:
                    pass
        except Exception:
            pass
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return out


def _dasha_ladder(session, when: dt.datetime) -> list[list[str]]:
    """The full 120-year mahadasha sequence from the sidereal Moon.

    `chart_service.vimshottari()` computes this ladder internally but only
    returns the current period plus the next three, which is not a dasha table.
    The arithmetic below is the same cycle over the same imported constants; if
    `chart_service` ever exposes the ladder, delete this and call it.
    """
    moon = session.chart.get_object("Moon")
    span = 360.0 / 27.0
    index = int(moon.longitude // span) % 27
    fraction = (moon.longitude % span) / span
    start_lord = index % 9

    birth = session.birth.local_datetime
    cursor = birth - dt.timedelta(days=fraction * VIMSHOTTARI[start_lord][1] * SIDEREAL_YEAR)
    if when.tzinfo is None:
        when = when.replace(tzinfo=birth.tzinfo)

    rows: list[list[str]] = []
    for step in range(9):
        lord, years = VIMSHOTTARI[(start_lord + step) % 9]
        end = cursor + dt.timedelta(days=years * SIDEREAL_YEAR)
        if cursor <= when < end:
            state = "current"
        elif end <= when:
            state = "past"
        else:
            state = "ahead"
        rows.append([lord, f"{years}", cursor.strftime("%d %b %Y"),
                     end.strftime("%d %b %Y"), state])
        cursor = end
    return rows


def _antardasha_ladder(session, when: dt.datetime) -> list[list[str]]:
    """Antardashas of the current Mahadasha."""
    mladder = _dasha_ladder(session, when)
    active_m = None
    for m in mladder:
        if m[4] == "current":
            active_m = m
            break
    if not active_m:
        active_m = mladder[0]
        
    m_lord_name = active_m[0]
    m_start_str = active_m[2]
    
    # Parse date
    m_start = dt.datetime.strptime(m_start_str, "%d %b %Y")
    if when.tzinfo:
        m_start = m_start.replace(tzinfo=when.tzinfo)
    else:
        m_start = m_start.replace(tzinfo=None)
        when = when.replace(tzinfo=None)
    
    # Vimshottari order & years
    ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    v_years = {
        "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
        "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
    }
    
    m_idx = ORDER.index(m_lord_name)
    m_years_total = v_years[m_lord_name]
    
    cursor = m_start
    rows: list[list[str]] = []
    
    for step in range(9):
        a_lord = ORDER[(m_idx + step) % 9]
        a_years = v_years[a_lord]
        # (m_years * a_years / 120) * SIDEREAL_YEAR
        days = (m_years_total * a_years / 120.0) * SIDEREAL_YEAR
        end = cursor + dt.timedelta(days=days)
        
        if cursor <= when < end:
            state = "current"
        elif end <= when:
            state = "past"
        else:
            state = "ahead"
            
        rows.append([a_lord, cursor.strftime("%d %b %Y"), end.strftime("%d %b %Y"), state])
        cursor = end
        
    return rows


def _varga_grid(session) -> dict:
    """Returns a table of planet signs across D1, D3, D7, D9, D10, D12."""
    from .astro.vargas import divisional_chart
    divisions = ["D1", "D3", "D7", "D9", "D10", "D12"]
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Lagna"]
    
    v_charts = {}
    for div in divisions:
        if div == "D1":
            v_charts[div] = {
                "Lagna": session.bundle["objects"]["ASC"]["sign"],
                "positions": {p: session.bundle["objects"][p]["sign"] for p in planets if p in session.bundle["objects"]}
            }
        else:
            try:
                v_data = divisional_chart(session, div)
                lag_sign = v_data["lagna"]["sign"] if isinstance(v_data["lagna"], dict) else v_data["lagna"]
                v_charts[div] = {
                    "Lagna": lag_sign,
                    "positions": {p: v_data["positions"][p]["sign"] for p in planets if p in v_data["positions"]}
                }
            except Exception:
                v_charts[div] = {"Lagna": "\u2014", "positions": {}}
                
    rows = []
    for p in planets:
        row = [p]
        for div in divisions:
            if p == "Lagna":
                sign = v_charts[div]["Lagna"]
            else:
                sign = v_charts[div]["positions"].get(p, "\u2014")
            row.append(sign)
        rows.append(row)
        
    return {
        "headers": ["Object", "D1 (Rashi)", "D3", "D7", "D9 (Nav)", "D10 (Das)", "D12 (Dvad)"],
        "cols": [0, 1, 1, 1, 1, 1, 1],
        "rows": rows
    }


def _yogas_pdf_table(session) -> dict:
    """Returns a table of formed yogas."""
    from .astro.vargas import yogas
    try:
        y_data = yogas(session)
        formed = y_data.get("yogas", [])
    except Exception:
        formed = []
        
    rows = []
    for y in formed:
        planets_str = ", ".join(y.get("planets", [])) if y.get("planets") else "\u2014"
        rows.append([y.get("name", ""), y.get("group", ""), planets_str, y.get("note", "")])
        
    if not rows:
        rows = [["No major yogas formed", "\u2014", "\u2014", "Continue daily prayers for planetary strength"]]
        
    return {
        "headers": ["Yoga Name", "Category", "Planets", "Effect / Description"],
        "cols": [1, 1, 1, 2],
        "rows": rows
    }


def _positions_table(bundle: dict) -> dict:
    order = {"planet": 0, "node": 1, "angle": 2, "point": 3, "part": 4}
    objects = sorted(
        bundle["objects"].values(),
        key=lambda o: (order.get(o["kind"], 9), o["longitude"]),
    )
    rows = []
    for obj in objects:
        if obj["kind"] not in ("planet", "node", "angle"):
            continue
        rows.append([
            obj["name"] + (" R" if obj.get("retrograde") else ""),
            obj["sign"],
            obj["dms"],
            str(obj["house"]),
            (obj.get("placement") or "").title(),
            ", ".join(obj.get("dignities") or []) or "\u2014",
        ])
    return {"headers": ["Body", "Sign", "Degree", "House", "Placement", "Dignity"],
            "cols": [0, 0, 0, 0, 0, 1], "rows": rows}


def _houses_table(bundle: dict) -> dict:
    houses = bundle["houses"]
    rows = []
    for number in range(1, 13):
        occupants = [
            o["name"] for o in bundle["objects"].values()
            if o["kind"] == "planet" and o["house"] == number
        ]
        rows.append([
            str(number),
            houses["signs"][number - 1],
            dms(houses["degrees"][number - 1]),
            houses["rulers"][number - 1],
            ", ".join(occupants) or "\u2014",
        ])
    return {"headers": ["House", "Sign on cusp", "Cusp", "Ruler", "Occupants"],
            "cols": [0, 0, 0, 0, 1], "rows": rows}


# Everything the chart carries is in the bundle, but a printed aspect table is
# a reading aid, not a dump: Ptolemaic aspects between bodies a reader has heard
# of. Vertex-to-Mean-Apogee belongs in the JSON, not on paper.
_ASPECT_BODIES = {
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "Chiron", "ASC", "MC",
    "North Node", "South Node", "True Node", "Mean Node",
}
_ASPECT_TYPES = {"conjunction", "opposition", "square", "trine", "sextile"}


def _aspects_table(bundle: dict, limit: int = 26) -> dict:
    rows = []
    for aspect in bundle["aspects"]:
        if aspect["a"] not in _ASPECT_BODIES or aspect["b"] not in _ASPECT_BODIES:
            continue
        if aspect["type"].lower() not in _ASPECT_TYPES:
            continue
        rows.append([aspect["a"], aspect["type"], aspect["b"], dms(aspect["orb"]),
                     "applying" if aspect["applying"] else "separating"])
        if len(rows) >= limit:
            break
    return {"headers": ["Body", "Aspect", "Body", "Orb", "Motion"],
            "cols": [0, 0, 0, 0, 1], "rows": rows}


_PLANETS_HI = {
    "Sun": "सूर्य", "Moon": "चंद्रमा", "Mars": "मंगल", "Mercury": "बुध", "Jupiter": "बृहस्पति", 
    "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु", "Lagna": "लग्न", 
    "ASC": "लग्न", "MC": "दशम भाव", "DSC": "सप्तम भाव", "IC": "चतुर्थ भाव", 
    "True Node": "राहु", "South Node": "केतु", "Mean Node": "राहु",
    "Uranus": "अरुण", "Neptune": "वरुण", "Pluto": "यम", "Chiron": "चिरोन"
}

_SIGNS_HI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क", "Leo": "सिंह", 
    "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक", "Sagittarius": "धनु", 
    "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}

_ZODIAC_HI = {
    "sidereal": "निरयण (Sidereal)", "sidereal".title(): "निरयण (Sidereal)",
    "tropical": "सायन (Tropical)", "tropical".title(): "सायन (Tropical)"
}

_HOUSE_SYSTEM_HI = {
    "Whole Sign": "भाव चलित (Whole Sign)", "Equal House": "सम भाव (Equal House)"
}

_DIGNITIES_HI = {
    "exalted": "उच्च", "debilitated": "नीच", "own": "स्वराशि", "friendly": "मित्र", 
    "neutral": "सम", "inimical": "शत्रु", "moolatrikona": "मूलत्रिकोण",
    "exalted".title(): "उच्च", "debilitated".title(): "नीच", "own".title(): "स्वराशि", 
    "friendly".title(): "मित्र", "neutral".title(): "सम", "inimical".title(): "शत्रु",
    "moolatrikona".title(): "मूलत्रिकोण"
}

_MOTION_HI = {
    "retrograde": "वक्री", "direct": "मार्गी", "combust": "अस्त", 
    "yes": "हाँ", "no": "नहीं", "Yes": "हाँ", "No": "नहीं"
}

_POSITION_HI = {
    "angular": "केंद्र", "succedent": "पणफर", "cadent": "आपोक्लिम",
    "angular".title(): "केंद्र", "succedent".title(): "पणफर", "cadent".title(): "आपोक्लिम"
}

_ASPECTS_HI = {
    "conjunction": "युति", "opposition": "प्रतियुति", "square": "केन्द्र", 
    "trine": "त्रिकोण", "sextile": "षडाष्टक"
}


def _format_date_hi(date_str: str) -> str:
    import re
    months_map = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
        "january": "01", "february": "02", "march": "03", "april": "04", "may": "05", "june": "06",
        "july": "07", "august": "08", "september": "09", "october": "10", "november": "11", "december": "12"
    }
    
    # Try parsing format DD Month YYYY
    m = re.match(r"(\d+)\s+([A-Za-z]+)\s+(\d+)(?:,\s+(\d+:\d+))?", date_str)
    if m:
        day = m.group(1).zfill(2)
        mon_name = m.group(2).lower()
        year = m.group(3)
        time = m.group(4)
        mon = months_map.get(mon_name, "01")
        if time:
            return f"{day}-{mon}-{year}, {time}"
        return f"{day}-{mon}-{year}"
        
    # Check if Month DD, YYYY
    m2 = re.match(r"([A-Za-z]+)\s+(\d+),\s+(\d+)(?:\s+(\d+:\d+\s*[A-Za-z]+))?", date_str)
    if m2:
        mon_name = m2.group(1).lower()
        day = m2.group(2).zfill(2)
        year = m2.group(3)
        time = m2.group(4)
        mon = months_map.get(mon_name, "01")
        if time:
            return f"{day}-{mon}-{year}, {time}"
        return f"{day}-{mon}-{year}"
        
    return date_str


def _translate_val(val: str, language: str) -> str:
    if language != "hi":
        return val
    if not isinstance(val, str):
        return str(val)
    val_stripped = val.strip()
    if not val_stripped:
        return val
        
    for m in [_PLANETS_HI, _SIGNS_HI, _ZODIAC_HI, _HOUSE_SYSTEM_HI, _DIGNITIES_HI, _MOTION_HI, _POSITION_HI, _ASPECTS_HI]:
        if val_stripped in m:
            return m[val_stripped]
            
    # Check suffix " R" for retrograde
    if val_stripped.endswith(" R") and val_stripped[:-2] in _PLANETS_HI:
        return _PLANETS_HI[val_stripped[:-2]] + " (वक्री)"
        
    # Check comma separated list
    if "," in val_stripped:
        parts = [p.strip() for p in val_stripped.split(",")]
        mapped = [_translate_val(p, language) for p in parts]
        return ", ".join(mapped)
        
    # Handle numbers or degrees: e.g. "23°07'" or "10°57'"
    if "°" in val_stripped:
        # Check if it has a trailing sign name like "23°07' Aries"
        # E.g. split and translate the sign name part
        for sign_eng, sign_hi in _SIGNS_HI.items():
            if sign_eng in val_stripped:
                return val_stripped.replace(sign_eng, sign_hi)
        return val_stripped
        
    # Try translating date
    return _format_date_hi(val_stripped)


_LOCALIZED_TEXTS = {
    "en": {
        "title": "Birth Chart & Kundali Report",
        "born": "Born",
        "at": "At",
        "system": "System",
        "generated": "Generated",
        "birth_details": "Birth Details (जन्म विवरण)",
        "d1_title": "Rashi Chart (D1) - लग्न कुंडली",
        "d9_title": "Navamsa Chart (D9) - नवमांश कुंडली",
        "north_indian": "North Indian Style (उत्तर भारतीय पद्धति)",
        "south_indian": "South Indian Style (दक्षिण भारतीय पद्धति)",
        "planetary_positions": "Planetary Positions (ग्रह स्थिति)",
        "houses": "House Placements (भाव विवरण)",
        "aspects": "Major Aspects (प्रमुख दृष्टि)",
        "dasha": "Vimshottari Dasha (विम्शोत्तरी दशा)",
        "varshphal_title": "Yearly Varshphal Forecast (वार्षिक राशिफल)",
        "upcoming_title": "Upcoming Key Periods (आगामी समय)",
        "house_summary_title": "House-wise Summary (भाव विवेचन)",
        "vargas_title": "Divisional Placements Table (वर्ग कुंडली सारणी)",
        "yogas_title": "Formed Yogas Analysis (योग विवेचन)",
        "antardasha_title": "Antardashas of Active Mahadasha (सूक्ष्म अंतर्दशा काल)",
        "houses_detailed_title": "Detailed House Analysis (भाव फल विवेचन)",
        "planets_detailed_title": "Planetary Placement Interpretations (ग्रह फल विवेचन)",
        "remedies_detailed_title": "Spiritual Guidelines & Remedies (उपाय एवं मंत्र)",
    },
    "hi": {
        "title": "जन्म कुंडली विवरण (Kundali Report)",
        "born": "जन्म समय",
        "at": "जन्म स्थान",
        "system": "पद्धति",
        "generated": "दिनांक",
        "birth_details": "जन्म विवरण (Birth Details)",
        "d1_title": "लग्न कुंडली / लग्न चक्र (Rashi D1)",
        "d9_title": "नवमांश कुंडली / नवमांश चक्र (Navamsa D9)",
        "north_indian": "उत्तर भारतीय शैली (North Indian)",
        "south_indian": "दक्षिण भारतीय शैली (South Indian)",
        "planetary_positions": "ग्रह स्थिति (Planetary Positions)",
        "houses": "भाव विवरण (Houses)",
        "aspects": "प्रमुख दृष्टि (Major Aspects)",
        "dasha": "विम्शोत्तरी दशा (Vimshottari Dasha)",
        "varshphal_title": "वार्षिक वर्षफल (Yearly Varshphal)",
        "upcoming_title": "आगामी महत्वपूर्ण समय (Upcoming Key Periods)",
        "house_summary_title": "भाव विवेचन / भाव फल (House-wise Summary)",
        "vargas_title": "वर्ग कुंडली स्थिति विवरण (Divisional Table)",
        "yogas_title": "कुंडली में स्थित महत्वपूर्ण योग (Yogas)",
        "antardasha_title": "सक्रिय महादशा की अंतर्दशाएं (Antardashas)",
        "houses_detailed_title": "द्वादश भाव फल विवेचन (Detailed House Analysis)",
        "planets_detailed_title": "ग्रह फल विवेचन (Detailed Planets Analysis)",
        "remedies_detailed_title": "ज्योतिषीय उपाय एवं वैदिक मंत्र (Remedies & Mantras)",
    }
}


def chart_pdf(session, *, brand: str, site: str, when: dt.datetime | None = None, language: str = "en") -> bytes:
    """A full chart report for an active chart session supporting English and Hindi."""
    from .llm import generate_kundali_narratives
    
    when = when or dt.datetime.now()
    bundle = session.bundle
    birth = session.birth
    meta = bundle["meta"]
    
    texts = _LOCALIZED_TEXTS.get(language, _LOCALIZED_TEXTS["en"])

    files: dict[str, str] = {}
    try:
        files["wheel.svg"] = wheel_svg(session, theme="classic")
    except Exception:                   # a wheel that will not draw is not fatal
        pass
    for name, svg in _vedic_svgs(session).items():
        files[f"{name}.svg"] = svg

    birth_rows = []
    if language == "hi":
        birth_rows = [
            ["नाम", meta["name"]],
            ["जन्म तिथि व समय", meta["local_time"] if birth.time_known else f"{meta['local_time']} (समय अज्ञात)"],
            ["जन्म स्थान", f"{meta['place']}  ({meta['latitude']:.4f}, {meta['longitude']:.4f})"],
            ["समय क्षेत्र", f"{meta['timezone']} (UTC{meta['utc_offset'][:3]}:{meta['utc_offset'][3:]})"],
            ["यूनीवर्सल समय (UT)", str(meta["utc_time"])],
            ["अयन चक्र / अयन", "निरयण (Sidereal) \u00b7 " + (f"{str(meta['ayanamsa']).title()} अयन " f"{meta['ayanamsa_value']}\u00b0" if meta.get("ayanamsa_value") else "")],
            ["भाव पद्धति", meta["house_system"]],
            ["वर्ग", "दिन की कुंडली" if meta["sect"] == "diurnal" else "रात्रि की कुंडली"],
        ]
    else:
        birth_rows = [
            ["Name", meta["name"]],
            ["Date & time", meta["local_time"] if birth.time_known else f"{meta['local_time']} (birth time unknown)"],
            ["Place", f"{meta['place']}  ({meta['latitude']:.4f}, {meta['longitude']:.4f})"],
            ["Time zone", f"{meta['timezone']} (UTC{meta['utc_offset'][:3]}:{meta['utc_offset'][3:]})"],
            ["Universal time", str(meta["utc_time"])],
            ["Zodiac", meta["zodiac"].title() + (f" \u00b7 {str(meta['ayanamsa']).title()} ayanamsa " f"{meta['ayanamsa_value']}\u00b0" if meta.get("ayanamsa_value") else "")],
            ["House system", meta["house_system"]],
            ["Sect", f"{meta['sect']} chart"],
        ]

    dasha = None
    if birth.zodiac == "sidereal":
        try:
            summary = vimshottari(session, when)
            maha, antar = summary.get("mahadasha"), summary.get("antardasha")
            dasha = {
                "summary": [
                    ["Moon", summary["moon_position"]],
                    ["Nakshatra", f"{summary['nakshatra']} (pada {summary['pada']})"],
                    ["Mahadasha", f"{maha['lord']}  {maha['start']} \u2013 {maha['end']}"
                     if maha else "\u2014"],
                    ["Antardasha", f"{antar['lord']}  {antar['start']} \u2013 {antar['end']}"
                     if antar else "\u2014"],
                    ["As of", when.strftime("%d %B %Y")],
                ],
                "table": {
                    "headers": ["Mahadasha", "Years", "From", "To", "Status"],
                    "cols": [0, 0, 0, 0, 1],
                    "rows": _dasha_ladder(session, when),
                },
            }
            if language == "hi":
                dasha["table"]["headers"] = ["महादशा", "वर्ष", "आरंभ तिथि", "समाप्ति तिथि", "स्थिति"]
                status_map = {"past": "गत काल", "current": "सक्रिय", "ahead": "आगामी"}
                for row in dasha["table"]["rows"]:
                    row[4] = status_map.get(row[4], row[4])
                
                sum_map = {
                    "Moon": "चंद्रमा",
                    "Nakshatra": "नक्षत्र",
                    "Mahadasha": "वर्तमान महादशा",
                    "Antardasha": "वर्तमान अंतर्दशा",
                    "As of": "तिथि के अनुसार"
                }
                for row in dasha["summary"]:
                    if row[0] in sum_map:
                        row[0] = sum_map[row[0]]
        except Exception:               # pragma: no cover - defensive
            dasha = None

    vargas_table = _varga_grid(session)
    yogas_table = _yogas_pdf_table(session)
    
    antardasha_table = None
    if dasha:
        antardasha_table = {
            "headers": ["Antardasha", "From", "To", "Status"],
            "cols": [0, 0, 0, 1],
            "rows": _antardasha_ladder(session, when)
        }
        dasha["antardasha"] = antardasha_table

    if language == "hi":
        for row in birth_rows:
            row[1] = _translate_val(row[1], language)

        vargas_table["headers"] = ["ग्रह/लग्न", "D1 (लग्न)", "D3 (द्रेष्काण)", "D7 (सप्तांश)", "D9 (नवमांश)", "D10 (दशांश)", "D12 (द्वादशांश)"]
        for row in vargas_table["rows"]:
            for i in range(len(row)):
                row[i] = _translate_val(row[i], language)
                
        yogas_table["headers"] = ["योग का नाम", "श्रेणी", "संबद्ध ग्रह", "प्रभाव / शास्त्रीय फल"]
        for row in yogas_table["rows"]:
            row[0] = _translate_val(row[0], language)
            row[1] = _translate_val(row[1], language)
            row[2] = _translate_val(row[2], language)
        
        if dasha:
            dasha["table"]["headers"] = ["महादशा", "वर्ष", "आरंभ तिथि", "समाप्ति तिथि", "स्थिति"]
            for row in dasha["table"]["rows"]:
                row[0] = _translate_val(row[0], language)
                row[2] = _translate_val(row[2], language)
                row[3] = _translate_val(row[3], language)
                row[4] = _translate_val(row[4], language)
                
            for row in dasha["summary"]:
                row[1] = _translate_val(row[1], language)

            if antardasha_table:
                antardasha_table["headers"] = ["अंतर्दशा स्वामी", "आरंभ तिथि", "समाप्ति तिथि", "स्थिति"]
                for row in antardasha_table["rows"]:
                    row[0] = _translate_val(row[0], language)
                    row[1] = _translate_val(row[1], language)
                    row[2] = _translate_val(row[2], language)
                    row[3] = _translate_val(row[3], language)

    # Call LLM to generate narrative sections
    analysis_input = {
        "meta": meta,
        "lagna": bundle["objects"]["ASC"]["sign"],
        "dasha": {
            "mahadasha": {"lord": dasha["summary"][2][1].split()[0] if (dasha and len(dasha["summary"]) > 2) else "Rahu"}
        }
    }
    if "Moon" in bundle["objects"]:
        analysis_input["moon_sign"] = bundle["objects"]["Moon"]["sign"]

    narratives = generate_kundali_narratives(analysis_input, language=language)
    from .llm import generate_kundali_interpretations
    interpretations = generate_kundali_interpretations(analysis_input, language=language)

    pos_table = _positions_table(bundle)
    if language == "hi":
        pos_table["headers"] = ["ग्रह", "राशि", "स्थिति", "भाव", "गति", "वक्री"]
        for row in pos_table["rows"]:
            row[0] = _translate_val(row[0], language)
            row[1] = _translate_val(row[1], language)
            row[2] = _translate_val(row[2], language)
            row[3] = _translate_val(row[3], language)
            row[4] = _translate_val(row[4], language)
            row[5] = _translate_val(row[5], language)

    houses_table = _houses_table(bundle)
    if language == "hi":
        houses_table["headers"] = ["भाव", "राशि", "विस्तार", "दूरी", "स्वामी", "स्थित ग्रह"]
        for row in houses_table["rows"]:
            row[1] = _translate_val(row[1], language)
            row[3] = _translate_val(row[3], language)
            if len(row) > 4:
                row[4] = _translate_val(row[4], language)

    aspects_table = _aspects_table(bundle)
    if language == "hi":
        aspects_table["headers"] = ["कारक", "दृष्टि", "लक्ष्य", "अंतर", "सटीक"]
        for row in aspects_table["rows"]:
            row[0] = _translate_val(row[0], language)
            row[1] = _translate_val(row[1], language)
            row[2] = _translate_val(row[2], language)
            row[4] = _translate_val(row[4], language)

    data = {
        "brand": brand,
        "title": texts["title"],
        "subject": meta["name"],
        "lang": language,
        "texts": texts,
        "cover": [
            [texts["born"], _translate_val(meta["local_time"], language)],
            [texts["at"], _translate_val(meta["place"], language)],
            [texts["system"], f"{_translate_val(meta['zodiac'], language)} \u00b7 {_translate_val(meta['house_system'], language)}"],
            [texts["generated"], _translate_val(when.strftime("%d %B %Y"), language)],
        ],
        "footer": f"{brand} \u00b7 {site}",
        "birth": birth_rows,
        "note": bundle.get("house_note") or "",
        "d1_north": "d1_north.svg" if "d1_north.svg" in files else "",
        "d1_south": "d1_south.svg" if "d1_south.svg" in files else "",
        "d9_north": "d9_north.svg" if "d9_north.svg" in files else "",
        "d9_south": "d9_south.svg" if "d9_south.svg" in files else "",
        "vargas": vargas_table,
        "yogas": yogas_table,
        "positions": pos_table,
        "houses": houses_table,
        "aspects": aspects_table,
        "dasha": dasha,
        "varshphal": [[m, markdown_blocks(p)] for m, p in narratives["varshphal"]],
        "upcoming": markdown_blocks(narratives["key_periods"]),
        "house_summary": markdown_blocks(narratives["house_summary"]),
        "houses_detailed": markdown_blocks(interpretations["houses_detailed"]),
        "planets_detailed": markdown_blocks(interpretations["planets_detailed"]),
        "remedies_detailed": markdown_blocks(interpretations["yogas_remedies_detailed"]),
    }
    return _compile(_CHART_BODY, data, files)


def remedies_pdf(session, *, brand: str, site: str, language: str = "en") -> bytes:
    """A full remedies and gemstones PDF report for an active chart session."""
    from .astro.remedies import recommend_remedies
    from .llm import generate_spiritual_guidance

    bundle = session.bundle
    meta = bundle["meta"]
    
    # Calculate remedies and gemstones
    rem = recommend_remedies(session)
    
    # Generate guidance
    analysis = {
        "meta": meta,
        "lagna": bundle["objects"]["ASC"]["sign"],
        "moon_sign": rem["gemstones"]["life_stone"]["planet"],
        "dasha": {
            "mahadasha": {
                "lord": rem["dasha_remedies"]["mahadasha_lord"]
            }
        }
    }
    if "Moon" in bundle["objects"]:
        analysis["moon_sign"] = bundle["objects"]["Moon"]["sign"]
        
    guidance_text = generate_spiritual_guidance(analysis, language=language)
    
    # Format gemstones table
    gems_rows = []
    for gkey in ["life_stone", "lucky_stone", "fortune_stone"]:
        g = rem["gemstones"][gkey]
        gems_rows.append([
            g["role"],
            g["name"],
            g["metal"],
            g["finger"]
        ])
    
    gemstones_table = {
        "headers": ["Role", "Gemstone", "Metal", "Finger"],
        "cols": [1, 1, 1, 1],
        "rows": gems_rows
    }
    
    birth_rows = [
        ["Name", meta["name"]],
        ["Date & time", meta["local_time"]],
        ["Place", meta["place"]],
        ["Lagna (Ascendant)", bundle["objects"]["ASC"]["sign"]],
    ]
    if "Moon" in bundle["objects"]:
        birth_rows.append(["Moon Sign", bundle["objects"]["Moon"]["sign"]])
        
    data = {
        "brand": brand,
        "title": "Remedies & Gemstones Report",
        "subject": meta["name"],
        "lang": language,
        "cover": [
            ["Born", meta["local_time"]],
            ["At", meta["place"]],
            ["Generated", dt.datetime.now().strftime("%d %B %Y")],
        ],
        "footer": f"{brand} \u00b7 {site}",
        "birth": birth_rows,
        "gemstones": gemstones_table,
        "mahadasha": rem["dasha_remedies"]["mahadasha_lord"],
        "mantra": rem["dasha_remedies"]["mantra"],
        "charity": rem["dasha_remedies"]["charity"],
        "guidance": markdown_blocks(guidance_text),
    }
    return _compile(_REMEDIES_BODY, data)


# --------------------------------------------------------------------------
# Filenames
# --------------------------------------------------------------------------

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def safe_filename(*parts: str, suffix: str = ".pdf") -> str:
    """An ASCII filename safe for a Content-Disposition header."""
    stem = "-".join(p for p in (_UNSAFE.sub("-", (p or "").strip()).strip("-")
                                for p in parts) if p)
    return (stem or "report")[:80] + suffix


__all__ = [
    "chart_pdf", "devanagari_font", "font_paths", "inline_spans",
    "markdown_blocks", "pdf_font_report", "questions_pdf", "remedies_pdf", "safe_filename",
]

