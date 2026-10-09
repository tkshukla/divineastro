"""Public sample reports (DIVASTRO-151): see what a paid report holds before paying.

    GET /samples/<sku>.pdf?lang=en|hi        sku: sq_career sq_marriage_timing sq_wealth_business life_book

Each sample is the REAL paid builder (pdf_report.single_question_pdf / life_book_pdf)
run on ONE fixed, fictional chart ("Sample Customer"), with the narration model forced
off (llm.FORCE_OFF) so it is deterministic, costs nothing and reads exactly like
production's rule-engine text. The only difference from a paid report is `sample=True`:
a diagonal watermark and a footer line on every page. The content is complete, the same
length as the real one.

Built on the first request, then served from process memory and from disk (so a restart
does not rebuild), with a lock so concurrent first requests build once. The files live
under the app's data volume, never in the git tree. A copy older than a week is rebuilt:
the "next three years" windows are measured from the build date.
"""

from __future__ import annotations

import logging
import os
import tempfile
import threading
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response

from . import analytics, chart_service, llm, pdf_report

log = logging.getLogger(__name__)
router = APIRouter()

# sku -> the words in the download's file name
SKUS = {
    "sq_career": "career-report",
    "sq_marriage_timing": "marriage-timing-report",
    "sq_wealth_business": "wealth-business-report",
    "life_book": "life-book",
}

# A fictional customer, a date and place that belong to nobody in particular.
DEMO_BIRTH = dict(
    name="Sample Customer", date="1990-08-15", time="10:30",
    latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata",
    place="New Delhi, India", zodiac="sidereal", ayanamsa="lahiri", house_system="Whole Sign")

MAX_AGE_S = 7 * 24 * 3600
RATE_WINDOW_S = 60.0
RATE_MAX = 20                      # downloads a minute per address; a build happens once per sku/lang
CACHE_SECONDS = 86400

_memory: dict[tuple[str, str], tuple[float, bytes]] = {}
_build_lock = threading.Lock()
_rate: dict[str, tuple[float, int]] = {}
_rate_lock = threading.Lock()
builds = 0                         # how many real builds this process has done (tests read it)


def cache_dir() -> Path:
    """$ASTRO_SAMPLES_DIR, else samples-cache/ beside the database (the app's data volume)."""
    env = os.environ.get("ASTRO_SAMPLES_DIR")
    if env:
        return Path(env)
    from .db import _default_db_path
    return _default_db_path.parent / "samples-cache"


def _path(sku: str, lang: str) -> Path:
    return cache_dir() / f"{sku}.{lang}.pdf"


def _rate_ok(ip: str, now: float | None = None) -> bool:
    now = time.monotonic() if now is None else now
    key = analytics._rate_key(ip)
    with _rate_lock:
        start, n = _rate.get(key, (now, 0))
        if now - start >= RATE_WINDOW_S:
            start, n = now, 0
        if n >= RATE_MAX:
            return False
        _rate[key] = (start, n + 1)
        if len(_rate) > 10_000:
            for k in [k for k, (t, _) in _rate.items() if now - t >= RATE_WINDOW_S]:
                del _rate[k]
        return True


def build(sku: str, lang: str) -> bytes:
    """Run the real builder on the demo chart, model off, sample mode on."""
    session = chart_service.build(chart_service.BirthData(**DEMO_BIRTH))
    token = llm.FORCE_OFF.set(True)
    try:
        if sku == "life_book":
            return pdf_report.life_book_pdf(session, brand="Divine Astro", site="divineastro.org",
                                            language=lang, sample=True)
        return pdf_report.single_question_pdf(session, topic=sku, brand="Divine Astro",
                                              language=lang, sample=True)
    finally:
        llm.FORCE_OFF.reset(token)


def get_pdf(sku: str, lang: str) -> bytes:
    """The sample, from memory, then disk, then built (once, under a lock)."""
    global builds
    key = (sku, lang)
    now = time.time()
    hit = _memory.get(key)
    if hit and now - hit[0] < MAX_AGE_S:
        return hit[1]
    with _build_lock:
        hit = _memory.get(key)                       # another request built it while we waited
        if hit and now - hit[0] < MAX_AGE_S:
            return hit[1]
        path = _path(sku, lang)
        try:
            if path.is_file() and now - path.stat().st_mtime < MAX_AGE_S:
                data = path.read_bytes()
                if data.startswith(b"%PDF-"):
                    _memory[key] = (path.stat().st_mtime, data)
                    return data
        except OSError:
            pass
        data = build(sku, lang)
        builds += 1
        _memory[key] = (now, data)
        try:                                         # best effort: a read-only volume only costs a rebuild later
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
            os.replace(tmp, path)
        except OSError as exc:
            log.warning("could not store sample %s/%s: %s", sku, lang, exc)
        return data


@router.get("/samples/{name}.pdf")
def sample_pdf(name: str, request: Request, lang: str = "en") -> Response:
    if name not in SKUS:
        raise HTTPException(404, "There is no sample for that.")
    ip = request.client.host if request.client else ""
    if not _rate_ok(ip):
        raise HTTPException(429, "Too many requests. Please try again in a minute.",
                            headers={"Retry-After": "60"})
    lang = "hi" if lang == "hi" else "en"
    try:
        data = get_pdf(name, lang)
    except Exception as exc:
        log.exception("sample %s/%s failed", name, lang)
        raise HTTPException(500, "Could not build the sample.") from exc
    suffix = "-hindi" if lang == "hi" else ""
    return Response(
        content=data, media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="Divine-Astro-sample-{SKUS[name]}{suffix}.pdf"',
                 "Cache-Control": f"public, max-age={CACHE_SECONDS}"})
