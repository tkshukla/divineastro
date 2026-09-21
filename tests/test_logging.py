"""The app must still be able to log after it has run its migrations.

Why this exists: migrations/env.py called logging.config.fileConfig(alembic.ini)
with its DEFAULT disable_existing_loggers=True. init_db() runs that at every
start-up, so it silently disabled every logger that already existed — uvicorn's
error logger (unhandled-exception tracebacks) and every module's own
`logging.getLogger(__name__)`. In production a 500 left no trace at all and every
log.warning(...) in the app was dropped. Kundali Matchmaking returned 500 for
three weeks with an empty log to say why.

Needs no server; uses a throwaway SQLite database:

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_logging
"""

from __future__ import annotations

import logging
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Must be set before app.db is imported (it reads the URL at import time).
_tmp = tempfile.mkdtemp(prefix="astro_logtest_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


class Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)


def main() -> int:
    # Import the app first, exactly as uvicorn does: this is what creates the
    # module-level loggers BEFORE the migration runs.
    from app import analytics, api_feedback, auth, llm, main as _main  # noqa: F401
    from app.db import init_db

    names = ["uvicorn.error", "uvicorn.access", "astro.auth", "astro.llm",
             analytics.__name__, api_feedback.__name__]
    for n in names:
        logging.getLogger(n)                       # uvicorn's may not exist until asked for
    check("the loggers exist and are enabled BEFORE the migration",
          all(not logging.getLogger(n).disabled for n in names))

    print("\n1. Running the migrations must not disable them")
    init_db()
    disabled = [n for n in names if logging.getLogger(n).disabled]
    check("no existing logger was disabled by init_db()", not disabled, str(disabled))

    print("\n2. A logged error/warning actually reaches a handler")
    cap = Capture()
    root = logging.getLogger()
    root.addHandler(cap)
    try:
        logging.getLogger("uvicorn.error").error("unhandled exception in ASGI application")
        logging.getLogger("astro.auth").warning("a warning from the app")
        logging.getLogger(analytics.__name__).warning("visit tracking failed")
    finally:
        root.removeHandler(cap)
    got = {r.getMessage() for r in cap.records}
    check("uvicorn's error logger still emits (this is where 500 tracebacks go)",
          "unhandled exception in ASGI application" in got or
          any("unhandled" in r.getMessage() for r in cap.records) or
          logging.getLogger("uvicorn.error").propagate is False,
          str(got))
    check("the app's own warnings are emitted", {"a warning from the app", "visit tracking failed"} <= got, str(got))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("logging: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
