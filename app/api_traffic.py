"""Traffic endpoints: the page-load beacon that records a visit, and the admin
summary behind the Traffic tab. The logic itself lives in analytics.py so it can
be tested without HTTP."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from . import analytics
from .api_account import admin, get_db
from .db import User

router = APIRouter(prefix="/api")


async def _read_capped(request: Request, limit: int) -> bytes | None:
    """The request body, or None once it passes `limit` bytes. Stops reading at
    the cap, so an oversized upload costs us at most `limit` bytes of memory."""
    declared = request.headers.get("content-length", "")
    if declared.isdigit() and int(declared) > limit:
        return None
    buf = bytearray()
    async for chunk in request.stream():
        buf += chunk
        if len(buf) > limit:
            return None
    return bytes(buf)


@router.post("/visit", status_code=204)
async def visit(request: Request) -> Response:
    """One page load, reported by static/visit.js (see analytics.py for why the
    visit is counted here and not on the HTML request).

    Unauthenticated, so it is guarded cheaply: a per-address rate limit, a small
    body cap, and only our own public pages are accepted. Anything ignored —
    rate-limited, a bot, Do-Not-Track, an unknown page — still gets a quiet 204,
    so the page never logs an error and a prober learns nothing. Only bodies our
    own script could never send get an error status.

    The body is read as JSON whatever its content type: sendBeacon() sends a
    plain string as text/plain, which also keeps it a "simple" request.
    """
    ok = Response(status_code=204)
    ip = request.client.host if request.client else ""
    if not analytics.rate_ok(ip):
        return ok
    raw = await _read_capped(request, analytics.MAX_BEACON_BYTES)
    if raw is None:
        return Response(status_code=413)
    try:
        beacon = analytics.parse_beacon(json.loads(raw or b"null"))
    except (ValueError, RecursionError):   # not JSON / not UTF-8 / 2 KB of nested [[[
        return Response(status_code=400)
    if beacon is None:
        return ok
    # The visit write is a blocking DB call; keep it off the event loop.
    cookie = await run_in_threadpool(analytics.record_visit, request, *beacon)
    if cookie:
        ok.headers.append("set-cookie", cookie)
    return ok


@router.post("/event", status_code=204)
async def event(request: Request) -> Response:
    """One in-app action, reported by static/visit.js's daTrack() (DIVASTRO-128).
    Guarded exactly like /api/visit: rate limit, tiny body cap, a fixed list of
    event names, and a quiet 204 for anything ignored."""
    ok = Response(status_code=204)
    ip = request.client.host if request.client else ""
    if not analytics.rate_ok(ip):
        return ok
    raw = await _read_capped(request, analytics.MAX_EVENT_BYTES)
    if raw is None:
        return Response(status_code=413)
    try:
        ev = analytics.parse_event(json.loads(raw or b"null"))
    except (ValueError, RecursionError):
        return Response(status_code=400)
    if ev is not None:
        await run_in_threadpool(analytics.record_event, request, *ev)
    return ok


@router.get("/admin/traffic")
def admin_traffic(days: int = 30, _: User = Depends(admin),
                  db: Session = Depends(get_db)) -> dict:
    """Visitors, page views, new users, the sign-up funnel and where they came
    from, for the last `days` days (1-180, IST calendar days)."""
    out = analytics.summary(db, days)
    from . import push                     # DIVASTRO-112: daily web-push subscribers
    out["push"] = push.admin_summary(db)
    return out
