"""Once-a-day bookkeeping for the daily channel jobs (DIVASTRO-113).

`python -m app.telegram_daily` and `python -m app.whatsapp_pack` run from host
cron at 06:00 IST. A cron retry, a manual re-run or a double-fired job must
not post the same day twice, so each job records what it sent in a small JSON
file:

    $ASTRO_DAILY_STATE_DIR/<job>.json      default dir: /srv/data/daily_channels
    {"2026-10-03": {"hi": 123, "en": 124}, ...}

/srv/data is the app container's `appdata` volume, so the file survives image
rebuilds and container restarts. Deleting it (or passing --force) allows a
re-send. Entries older than KEEP_DAYS are pruned on every write.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

DEFAULT_DIR = "/srv/data/daily_channels"
KEEP_DAYS = 60


def path(job: str) -> Path:
    return Path(os.environ.get("ASTRO_DAILY_STATE_DIR") or DEFAULT_DIR) / f"{job}.json"


def load(job: str) -> dict:
    try:
        data = json.loads(path(job).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def sent(job: str, day: dt.date) -> dict:
    """What `job` already sent for `day`: {part: id-or-True}."""
    entry = load(job).get(day.isoformat())
    return entry if isinstance(entry, dict) else {}


def mark(job: str, day: dt.date, part: str, value: object = True) -> None:
    """Record one part (e.g. "hi") as sent for `day`. Atomic replace."""
    data = load(job)
    data.setdefault(day.isoformat(), {})[part] = value
    cutoff = (day - dt.timedelta(days=KEEP_DAYS)).isoformat()
    data = {k: v for k, v in data.items() if k >= cutoff}
    p = path(job)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")
    tmp.replace(p)


def today_ist() -> dt.date:
    from zoneinfo import ZoneInfo
    return dt.datetime.now(ZoneInfo("Asia/Kolkata")).date()
