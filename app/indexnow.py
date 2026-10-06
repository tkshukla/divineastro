"""IndexNow (Bing, Yandex, Naver, Seznam): tell search engines which URLs changed
instead of waiting for them to crawl (DIVASTRO-133).

Off unless ASTRO_INDEXNOW_KEY is set (8-128 characters of A-Z a-z 0-9 and -).
When it is, the app serves the key at /<key>.txt (the proof of ownership
IndexNow asks for) and the CLI can submit URLs:

    python -m app.indexnow --daily              # today's changed/new URLs, once per date
    python -m app.indexnow --daily --dry-run    # print what would be sent
    python -m app.indexnow --all                # the whole sitemap, once (--force to repeat)

"Today's changed URLs" are the pages whose content is rebuilt every day: the
Panchang / Rahu Kaal / Choghadiya pages of the default city and the 20 biggest
cities, the Rashifal pages and the Vrat hub, in every translated language, plus
the katha index, tonight's katha pick and any katha story not submitted before.
The other city pages change daily too but are left to the sitemap: a few hundred
changed URLs a day is the honest signal, three thousand is noise.

Bookkeeping is app/daily_state.py (job "indexnow"): the daily batch is recorded
per date, the one-off --all and the already-submitted stories in the job's
cache file. submit() never raises and nothing here ever logs the key.
Exit codes: 0 sent (or already sent), 1 a send failed, 2 not configured.
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import os
import re
import sys
from typing import Callable, Iterable
from urllib.parse import urlsplit

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from . import daily_state

log = logging.getLogger("divineastro.indexnow")

ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH = 10_000                  # the protocol's per-request maximum
JOB = "indexnow"
TOP_CITIES = 20                 # the cities whose daily pages go in --daily
_KEY_RE = re.compile(r"^[A-Za-z0-9-]{8,128}$")

# transport(endpoint, payload) -> HTTP status code. Tests pass a fake.
Transport = Callable[[str, dict], int]


def key() -> str | None:
    """The configured key, or None (feature off) when unset or malformed."""
    value = (os.environ.get("ASTRO_INDEXNOW_KEY") or "").strip()
    return value if _KEY_RE.match(value) else None


def _site_url() -> str:
    from .seo_pages import SITE_URL
    return SITE_URL


def make_router() -> APIRouter:
    """The key file route, only if a key is configured now. A fixed path per
    key (not /{name}.txt) so it cannot shadow /ads.txt or /robots.txt."""
    router = APIRouter()
    k = key()
    if k:
        @router.get(f"/{k}.txt", include_in_schema=False)
        def key_file() -> PlainTextResponse:
            return PlainTextResponse(k, headers={"Cache-Control": "public, max-age=86400"})
    return router


def _http_post(endpoint: str, payload: dict) -> int:
    import httpx
    return httpx.post(endpoint, json=payload, timeout=20.0,
                      headers={"Content-Type": "application/json; charset=utf-8"}).status_code


def submit(urls: Iterable[str], *, transport: Transport | None = None,
           site: str | None = None) -> dict:
    """POST `urls` to IndexNow in batches of at most BATCH. Never raises.

    Only absolute https URLs on this site's host are sent (IndexNow rejects the
    whole batch for a foreign host); duplicates are dropped, order is kept.
    Returns {"ok": bool, "sent": n, "batches": [status or None, ...], "reason": str}.
    200 and 202 count as accepted.
    """
    result = {"ok": False, "sent": 0, "batches": [], "reason": ""}
    try:
        k = key()
        if not k:
            result["reason"] = "not configured"
            return result
        base = (site or _site_url()).rstrip("/")
        host = urlsplit(base).netloc
        seen, todo = set(), []
        for u in urls:
            if u not in seen and urlsplit(u).scheme == "https" and urlsplit(u).netloc == host:
                seen.add(u)
                todo.append(u)
        if not todo:
            result.update(ok=True, reason="nothing to send")
            return result
        send = transport or _http_post
        ok = True
        for i in range(0, len(todo), BATCH):
            chunk = todo[i:i + BATCH]
            payload = {"host": host, "key": k, "keyLocation": f"{base}/{k}.txt",
                       "urlList": chunk}
            try:
                status = send(ENDPOINT, payload)
            except Exception as exc:                     # network, TLS, timeout ...
                status = None
                log.warning("indexnow: batch of %d failed: %s", len(chunk), type(exc).__name__)
            result["batches"].append(status)
            if status in (200, 202):
                result["sent"] += len(chunk)
            else:
                ok = False
                if status is not None:
                    log.warning("indexnow: batch of %d answered HTTP %s", len(chunk), status)
        result["ok"] = ok
        if not ok:
            result["reason"] = "a batch was not accepted"
    except Exception as exc:                             # submit() must never raise
        result["reason"] = type(exc).__name__
    return result


# --------------------------------------------------------------------------
# Which URLs
# --------------------------------------------------------------------------

def _abs(paths: Iterable[str]) -> list[str]:
    base = _site_url()
    return [base + p for p in paths]


def all_urls() -> list[str]:
    """Every URL in sitemap.xml, best first."""
    from .seo_pages import sitemap_ordered
    return _abs(sitemap_ordered())


def new_stories() -> list[str]:
    """Katha slugs not yet submitted (recorded by --daily)."""
    from .katha import STORIES
    seen = daily_state.recall(JOB, "stories")
    seen = set(seen) if isinstance(seen, list) else set()
    return [s for s in STORIES if s not in seen]


def daily_paths(day: dt.date) -> list[str]:
    """The paths whose content is rebuilt for `day` (see the module docstring)."""
    from . import katha, rashifal_pages, seo_cities, vrat_pages
    from .seo_pages import TOOLS, TRANSLATED, _path

    cities = [seo_cities.DEFAULT] + [c for c in seo_cities.CITIES[:TOP_CITIES]
                                     if c != seo_cities.DEFAULT]
    out = []
    from . import i18n
    for lang in i18n.ordered(TRANSLATED):
        out += [_path(tool, c, lang) for tool in TOOLS for c in cities]
        out += [rashifal_pages.path(r, lang) for r in (None, *rashifal_pages.RASHIS)]
        out.append(vrat_pages.hub_path(lang))
    slugs = list(new_stories())
    try:
        tonight = katha.pick(day)
    except Exception:                                    # a data problem must not stop the rest
        tonight = None
    if tonight and tonight not in slugs:
        slugs.append(tonight)
    for lang in (katha.HI, katha.EN):
        out.append(katha.page_path(None, lang))
        out += [katha.page_path(s, lang) for s in slugs]
    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None, *, transport: Transport | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.indexnow", description=__doc__.split("\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--daily", action="store_true", help="today's changed and new URLs")
    mode.add_argument("--all", action="store_true", help="the whole sitemap (once)")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today in India)")
    ap.add_argument("--force", action="store_true", help="send again even if already done")
    ap.add_argument("--dry-run", action="store_true", help="print the URLs, send nothing")
    args = ap.parse_args(argv)

    try:
        day = dt.date.fromisoformat(args.date) if args.date else daily_state.today_ist()
    except ValueError as exc:
        print(f"indexnow: {exc}", file=sys.stderr)
        return 2

    part = "all" if args.all else "daily"
    urls = all_urls() if args.all else _abs(daily_paths(day))
    if args.dry_run:
        print(f"indexnow: would submit {len(urls)} URLs ({part})")
        for u in urls[:20]:
            print("  ", u)
        return 0
    if not key():
        print("indexnow: ASTRO_INDEXNOW_KEY is not set (or is not 8-128 letters, digits, '-'); "
              "nothing to do", file=sys.stderr)
        return 2

    if not args.force:
        if args.all and daily_state.recall(JOB, "all_done"):
            print("indexnow: the full sitemap was already submitted (use --force to repeat)")
            return 0
        if args.daily and part in daily_state.sent(JOB, day):
            print(f"indexnow: already submitted for {day}; nothing to do")
            return 0

    res = submit(urls, transport=transport)
    if not res["ok"]:
        print(f"indexnow: FAILED ({res['reason']}; batch statuses {res['batches']})",
              file=sys.stderr)
        return 1
    print(f"indexnow: submitted {res['sent']} URLs ({part}, {len(res['batches'])} batch(es))")
    try:
        if args.all:
            daily_state.remember(JOB, "all_done", day.isoformat())
        else:
            from .katha import STORIES
            daily_state.remember(JOB, "stories", sorted(STORIES))
            daily_state.mark(JOB, day, part, res["sent"])
    except Exception as exc:                             # e.g. the state dir is not writable
        print(f"indexnow: sent, but could not record it: {type(exc).__name__}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
