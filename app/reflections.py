"""Tonight's Reflection: the 10 PM IST WhatsApp Channel post (DIVASTRO-127).

A short thought in the spirit of spiritual psychology: English on top, Hindi
below, an optional source line, good night. No links: the morning panchang and
the evening katha carry those.

The library is app/reflections.json, a list of
    {"id", "theme", "en", "hi", ["source"], ["tags"]}
validated at import (see _parse), so a bad entry fails CI with its id instead
of breaking a post at night. `en` / `hi` are 2-3 lines joined by "\\n";
`source` is set only for a quotation or a faithful paraphrase (marked
"(paraphrased)"); `tags` are festivals.py observance keys and reserve the
reflection for those days.

    python -m app.reflections --daily --dry-run        # what tonight's post would be
    python -m app.reflections --daily                  # post today's pick (once per date)
    python -m app.reflections --id gita-2-47           # post one particular reflection
"""

from __future__ import annotations

import argparse
import datetime as dt
import functools
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from . import daily_state
from .astro import festivals

JOB = "reflection"
LIBRARY_FILE = Path(__file__).resolve().parent / "reflections.json"

THEMES = ("mind", "attachment", "ego", "fear", "anger", "desire", "acceptance", "gratitude",
          "stillness", "karma", "impermanence", "compassion", "self-knowledge", "relationships",
          "discipline", "faith", "time", "silence", "forgiveness", "contentment")

FESTIVAL_GAP_DAYS = 300     # a festival reflection is not repeated within this many days
RECENT_THEMES = 3           # try not to repeat a theme used in the last N nights
SEED = "divastro-127"       # the rotation order; change it to reshuffle

# Dates that must get one particular reflection, whatever the festival or the
# rotation says (the cron's --daily cannot override it; --id still can).
PINNED: dict[str, str] = {
    "2026-10-04": "gita-2-47",     # the first post: Bhagavad Gita 2.47
}

EN_LIMIT = 300
HI_LIMIT = 400

HEADER = "*🌙 आज रात का विचार · Tonight's Reflection*"
FOOTER = "🙏 शुभ रात्रि · Good night"


@dataclass(frozen=True)
class Reflection:
    id: str
    theme: str
    en: str
    hi: str
    source: str = ""
    tags: tuple[str, ...] = ()


class ReflectionError(ValueError):
    """A library entry that does not match the schema. The message names the entry."""


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
# Hindi text: Devanagari plus spaces and ordinary punctuation, nothing else.
_HI_OK = re.compile(r"^[ऀ-ॿ \n,.;:?!'\"‘’“”()—–\-…]+$")
_MARKUP = re.compile(r"[*_~`]|https?://|www\.", re.I)
_REQUIRED = {"id", "theme", "en", "hi"}
_OPTIONAL = {"source", "tags"}


def festival_keys() -> set[str]:
    from .katha import festival_keys as keys    # one list of observance keys for both posts
    return keys()


def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.split("\n")]


def _parse(raw: object, where: str, keys: set[str]) -> Reflection:
    if not isinstance(raw, dict):
        raise ReflectionError(f"{where}: must be an object")
    rid = raw.get("id")
    where = f"{where} ({rid})" if isinstance(rid, str) else where
    missing = sorted(_REQUIRED - set(raw))
    extra = sorted(set(raw) - _REQUIRED - _OPTIONAL)
    if missing:
        raise ReflectionError(f"{where}: missing {', '.join(missing)}")
    if extra:
        raise ReflectionError(f"{where}: unknown field(s) {', '.join(extra)}")
    if not isinstance(rid, str) or not ID_RE.match(rid):
        raise ReflectionError(f"{where}: id must be lowercase-words-with-hyphens")
    if raw["theme"] not in THEMES:
        raise ReflectionError(f"{where}: theme {raw['theme']!r} is not one of {', '.join(THEMES)}")
    out: dict[str, object] = {"id": rid, "theme": raw["theme"]}
    for lang, limit in (("en", EN_LIMIT), ("hi", HI_LIMIT)):
        text = raw[lang]
        if not isinstance(text, str):
            raise ReflectionError(f"{where}: {lang} must be a string")
        lines = _lines(text)
        if not 2 <= len(lines) <= 3 or not all(lines):
            raise ReflectionError(f"{where}: {lang} must be 2-3 non-empty lines")
        text = "\n".join(lines)
        if len(text) > limit:
            raise ReflectionError(f"{where}: {lang} is {len(text)} chars; keep it to {limit}")
        if _MARKUP.search(text):
            raise ReflectionError(f"{where}: {lang} has markup or a link (* _ ~ ` or URL)")
        out[lang] = text
    if _DEVANAGARI.search(str(out["en"])):
        raise ReflectionError(f"{where}: en has Devanagari")
    if not _HI_OK.match(str(out["hi"])):
        bad = sorted({c for c in str(out["hi"]) if not _HI_OK.match(c)})
        raise ReflectionError(f"{where}: hi must be Devanagari only (found {bad})")
    if "source" in raw:
        src = raw["source"]
        if not isinstance(src, str) or not src.strip() or _MARKUP.search(src):
            raise ReflectionError(f"{where}: source must be a non-empty plain string")
        out["source"] = src.strip()
    tags = raw.get("tags", [])
    if (not isinstance(tags, list) or not all(isinstance(t, str) for t in tags)
            or len(set(tags)) != len(tags)):
        raise ReflectionError(f"{where}: tags must be a list of distinct strings")
    unknown = sorted(set(tags) - keys)
    if unknown:
        raise ReflectionError(f"{where}: tags {unknown} are not festival keys from "
                              f"app/astro/festivals.py")
    out["tags"] = tuple(tags)
    return Reflection(**out)  # type: ignore[arg-type]


def load(path: Path | str | None = None) -> dict[str, Reflection]:
    """The library (default $ASTRO_REFLECTIONS_FILE, else app/reflections.json),
    validated, keyed by id, in file order."""
    p = Path(path or os.environ.get("ASTRO_REFLECTIONS_FILE") or LIBRARY_FILE)
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ReflectionError(f"{p.name}: not valid UTF-8 JSON: {exc}") from None
    if not isinstance(raw, list):
        raise ReflectionError(f"{p.name}: must hold a JSON list")
    keys = festival_keys()
    lib: dict[str, Reflection] = {}
    for i, item in enumerate(raw):
        r = _parse(item, f"{p.name}[{i}]", keys)
        if r.id in lib:
            raise ReflectionError(f"{p.name}[{i}]: duplicate id {r.id!r}")
        lib[r.id] = r
    for day, rid in PINNED.items():
        if rid not in lib and p == LIBRARY_FILE:
            raise ReflectionError(f"PINNED {day}: no reflection {rid!r}")
    return lib


LIBRARY: dict[str, Reflection] = load()


# --------------------------------------------------------------------------
# The post
# --------------------------------------------------------------------------

def post_text(r: Reflection) -> str:
    """The WhatsApp post: header, English, Hindi, [source], good night."""
    parts = [HEADER, r.en, r.hi]
    if r.source:
        parts.append(f"_— {r.source}_")
    parts.append(FOOTER)
    return "\n\n".join(parts)


# --------------------------------------------------------------------------
# The nightly pick
# --------------------------------------------------------------------------

def history(lib: dict[str, Reflection] | None = None) -> dict[str, dt.date]:
    """id -> the day it was last posted (daily_state's reflection cache)."""
    out = {}
    for rid in (LIBRARY if lib is None else lib):
        rec = daily_state.recall(JOB, rid)
        if not isinstance(rec, dict):
            continue
        try:
            out[rid] = dt.date.fromisoformat(str(rec.get("day") or rec.get("posted"))[:10])
        except ValueError:
            continue
    return out


def rotation(lib: dict[str, Reflection]) -> list[str]:
    """The evergreen (untagged) reflections in a shuffled-but-fixed order that
    spreads each theme evenly through the cycle: within a theme the order is a
    seeded shuffle, and the k-th of n reflections of a theme sits near k/n."""
    def h(s: str) -> float:
        return int(hashlib.sha256(f"{SEED}:{s}".encode()).hexdigest()[:12], 16) / 16 ** 12

    by_theme: dict[str, list[str]] = {}
    for r in lib.values():
        if not r.tags:
            by_theme.setdefault(r.theme, []).append(r.id)
    keyed = []
    for theme, ids in by_theme.items():
        ids.sort(key=h)
        off = h("theme:" + theme)
        keyed += [((k + off) / len(ids), h(rid), rid) for k, rid in enumerate(ids)]
    return [rid for *_k, rid in sorted(keyed)]


@functools.lru_cache(maxsize=2048)
def _observances(day: dt.date) -> tuple[dict, ...]:
    return tuple(festivals.on(day))


def _festival(day: dt.date, lib: dict[str, Reflection],
              posted: dict[str, dt.date]) -> list[Reflection]:
    """Reflections tagged for `day`'s observances (New Delhi) and not posted in
    the last FESTIVAL_GAP_DAYS: major observances first, then never/least
    recently posted, then file order."""
    order = {rid: i for i, rid in enumerate(lib)}
    best: dict[str, tuple] = {}
    for o in _observances(day):
        for r in lib.values():
            last = posted.get(r.id)
            if o.get("key") not in r.tags or (last and (day - last).days < FESTIVAL_GAP_DAYS):
                continue
            rank = (not o.get("major"), last is not None, last or dt.date.min, order[r.id])
            best[r.id] = min(best.get(r.id, rank), rank)
    return [lib[rid] for rid in sorted(best, key=best.get)]  # type: ignore[arg-type]


def pick(day: dt.date, lib: dict[str, Reflection] | None = None,
         posted: dict[str, dt.date] | None = None) -> str | None:
    """The reflection for `day`'s 10 PM post.

    0. A date in PINNED gets its pinned reflection.
    1. A reflection tagged for one of today's observances, not posted in the
       last FESTIVAL_GAP_DAYS days, whose theme differs from last night's.
    2. Otherwise the next never-posted evergreen (untagged) reflection in
       rotation() order; once all have gone out, the least recently posted.
    Themes: never last night's theme; where possible not one of the last
    RECENT_THEMES nights', nor the theme tomorrow's festival reflection will
    need (so tomorrow can keep it).
    """
    lib = LIBRARY if lib is None else lib
    if not lib:
        return None
    pinned = PINNED.get(day.isoformat())
    if pinned in lib:
        return pinned
    posted = history(lib) if posted is None else posted

    by_day: dict[dt.date, str] = {}
    for rid, d in posted.items():
        if rid in lib and 0 < (day - d).days <= RECENT_THEMES:
            by_day[d] = lib[rid].theme
    prev = by_day.get(day - dt.timedelta(days=1))
    recent = set(by_day.values())
    tomorrow = _festival(day + dt.timedelta(days=1), lib, posted)
    keep = tomorrow[0].theme if tomorrow else None

    for r in _festival(day, lib, posted):
        if r.theme != prev:
            return r.id

    order = rotation(lib)
    if not order:                       # nothing evergreen: fall back to everything
        order = list(lib)
    index = {rid: i for i, rid in enumerate(order)}
    never = [rid for rid in order if rid not in posted]
    seen = sorted((rid for rid in order if rid in posted),
                  key=lambda rid: (posted[rid], index[rid]))
    rules = (lambda t: t not in recent and t != keep,
             lambda t: t != prev and t != keep,
             lambda t: t != prev)
    for pool in (never, seen):
        for ok in rules:
            for rid in pool:
                if ok(lib[rid].theme):
                    return rid
    return (never or seen)[0]


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _post(rid: str, day: dt.date, daily: bool) -> int:
    """Send one reflection to the channel. 0 posted, 1 failed, 2 not configured."""
    from . import whatsapp_channel as W           # lazy: only the CLI needs the connector

    token = os.environ.get("ASTRO_WA_TOKEN", "").strip()
    chan = os.environ.get("ASTRO_WA_CHANNEL_LINK", "").strip()
    if not token or not chan:
        print("reflection: ASTRO_WA_TOKEN and ASTRO_WA_CHANNEL_LINK must both be set "
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
            msg_id = client.post(jid, post_text(LIBRARY[rid]), None, None)
        except W.ConnectorError as exc:
            if exc.status == 409:
                raise W.Unlinked(str(exc)) from None
            raise
        now = dt.datetime.now().isoformat(timespec="seconds")
        try:
            daily_state.remember(JOB, rid, {"posted": now, "id": msg_id, "day": day.isoformat()})
            if daily:
                daily_state.mark(JOB, day, "post", {"reflection": rid, "id": msg_id})
        except OSError as exc:
            print(f"reflection: posted, but could not record it: {exc}", file=sys.stderr)
        print(f"reflection: posted {rid} for {day} (message {msg_id})")
        return 0
    except W.Unlinked as exc:
        print(f"reflection: NOT POSTED {rid} for {day}: {exc}", file=sys.stderr)
        W.alert_owner(str(exc), day)
        return 1
    except W.ConnectorError as exc:
        print(f"reflection: FAILED {rid} for {day}: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:                            # e.g. the state dir is not writable
        print(f"reflection: FAILED {rid} for {day}: "
              f"{client._redact(f'{type(exc).__name__}: {exc}')}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.reflections",
                                 description=__doc__.split("\n\n")[0])
    which = ap.add_mutually_exclusive_group(required=True)
    which.add_argument("--daily", action="store_true", help="post today's pick, once per date")
    which.add_argument("--id", dest="rid", metavar="ID", help="post this reflection")
    ap.add_argument("--date", help="with --daily: YYYY-MM-DD (default: today in IST)")
    ap.add_argument("--dry-run", action="store_true", help="print the post, send nothing")
    ap.add_argument("--force", action="store_true", help="post even if already posted")
    args = ap.parse_args(argv)

    try:
        day = dt.date.fromisoformat(args.date) if args.date else daily_state.today_ist()
    except ValueError as exc:
        print(f"reflection: {exc}", file=sys.stderr)
        return 2

    if args.rid:
        if args.rid not in LIBRARY:
            print(f"reflection: no reflection with id {args.rid!r}", file=sys.stderr)
            return 2
        rid = args.rid
        done = daily_state.recall(JOB, rid)
    else:
        rec = daily_state.sent(JOB, day).get("post")
        done = rec if isinstance(rec, dict) and rec.get("reflection") in LIBRARY else None
        # Already posted for this date: that one, so a dry run or --force shows
        # / re-sends what went out rather than the next pick.
        rid = done["reflection"] if done else pick(day)
        if rid is None:
            print("reflection: the library is empty", file=sys.stderr)
            return 1

    if args.dry_run:
        text = post_text(LIBRARY[rid])
        print(f"----- reflection {rid} ({LIBRARY[rid].theme}) for {day} ({len(text)} chars)"
              + (" [already posted]" if done else "") + " -----")
        print(text)
        return 0
    if done and not args.force:
        what = f"{rid} already posted" if args.rid else f"already posted for {day} ({rid})"
        print(f"reflection: {what}; nothing to do (--force to post again)")
        return 0
    return _post(rid, day, daily=args.daily)


if __name__ == "__main__":
    raise SystemExit(main())
