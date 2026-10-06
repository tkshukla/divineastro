"""IndexNow (DIVASTRO-133): the key file, submit() and the CLI.

    ~/.venvs/divineastro/bin/python -u -m tests.test_indexnow

No network: every transport is a fake function.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import io
import logging
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_tmp = tempfile.mkdtemp(prefix="astro_indexnow_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DAILY_STATE_DIR"] = _tmp
os.environ.pop("ASTRO_INDEXNOW_KEY", None)

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import daily_state, indexnow, seo_pages  # noqa: E402

SITE = seo_pages.SITE_URL
KEY = "abcd1234efgh5678"
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


class Fake:
    def __init__(self, status=200):
        self.status, self.calls = status, []

    def __call__(self, endpoint, payload):
        self.calls.append((endpoint, payload))
        if isinstance(self.status, Exception):
            raise self.status
        return self.status


def run_cli(argv, transport=None):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = indexnow.main(argv, transport=transport)
    return code, out.getvalue(), err.getvalue()


def main() -> int:
    print("1. off without a key")
    check("key() is None when unset", indexnow.key() is None)
    check("no key route registered", not indexnow.make_router().routes)
    f = Fake()
    r = indexnow.submit([f"{SITE}/panchang"], transport=f)
    check("submit does nothing and does not raise", not r["ok"] and not f.calls, str(r))
    code, _, err = run_cli(["--daily"], f)
    check("CLI exits 2, sends nothing", code == 2 and not f.calls, err)

    os.environ["ASTRO_INDEXNOW_KEY"] = "short"
    check("a malformed key counts as unset", indexnow.key() is None)

    print("2. key file")
    os.environ["ASTRO_INDEXNOW_KEY"] = KEY
    app = FastAPI()
    app.include_router(indexnow.make_router())
    c = TestClient(app)
    r = c.get(f"/{KEY}.txt")
    check("/<key>.txt serves the key", r.status_code == 200 and r.text == KEY, r.text)
    check("another .txt is not served", c.get("/other.txt").status_code == 404)

    print("3. submit")
    f = Fake()
    urls = [f"{SITE}/panchang", f"{SITE}/panchang", "https://evil.example/x",
            "http://divineastro.org/insecure", f"{SITE}/hi/panchang"]
    r = indexnow.submit(urls, transport=f)
    check("one batch, deduped, own host only", r["ok"] and r["sent"] == 2 and len(f.calls) == 1, str(r))
    endpoint, payload = f.calls[0]
    check("endpoint and payload shape", endpoint == "https://api.indexnow.org/indexnow"
          and payload["key"] == KEY and payload["keyLocation"] == f"{SITE}/{KEY}.txt"
          and payload["host"] == SITE.split("//")[1]
          and payload["urlList"] == [f"{SITE}/panchang", f"{SITE}/hi/panchang"], str(payload))
    big = [f"{SITE}/p/{i}" for i in range(25_000)]
    f = Fake(202)
    r = indexnow.submit(big, transport=f)
    check("25,000 URLs go out in 3 batches of <= 10,000",
          [len(p["urlList"]) for _, p in f.calls] == [10_000, 10_000, 5_000] and r["ok"],
          str([len(p["urlList"]) for _, p in f.calls]))
    f = Fake(429)
    r = indexnow.submit([f"{SITE}/a"], transport=f)
    check("HTTP 429 -> not ok, no raise", not r["ok"] and r["sent"] == 0)
    f = Fake(RuntimeError(f"boom {KEY}"))
    logs = io.StringIO()
    h = logging.StreamHandler(logs)
    indexnow.log.addHandler(h)
    r = indexnow.submit([f"{SITE}/a"], transport=f)
    indexnow.log.removeHandler(h)
    check("a transport exception is swallowed", not r["ok"])
    check("the key is never logged", KEY not in logs.getvalue() and KEY not in str(r),
          logs.getvalue())
    check("empty input is ok", indexnow.submit([], transport=Fake())["ok"])

    print("4. daily URLs")
    day = dt.date(2026, 10, 7)
    paths = indexnow.daily_paths(day)
    check("no duplicates, all absolute-able", len(paths) == len(set(paths)) and all(p.startswith("/") for p in paths))
    check("covers panchang/rashifal/vrat/katha in en, hi and kn",
          all(p in paths for p in ("/panchang", "/hi/panchang", "/kn/rahu-kaal", "/rashifal",
                                   "/hi/vrat-tyohar", "/ta/choghadiya", "/katha", "/en/katha")))
    check("a sensible size (not the whole sitemap)", 100 < len(paths) < 2000, str(len(paths)))
    in_sitemap = set(seo_pages.sitemap_paths())
    check("every daily URL is in the sitemap", all(p in in_sitemap for p in paths),
          str([p for p in paths if p not in in_sitemap][:3]))

    print("5. CLI --daily is idempotent per date")
    f = Fake()
    code, out, err = run_cli(["--daily", "--date", "2026-10-07"], f)
    check("first run sends", code == 0 and len(f.calls) == 1, out + err)
    check("state recorded for the date", "daily" in daily_state.sent("indexnow", day))
    code, out, _ = run_cli(["--daily", "--date", "2026-10-07"], f)
    check("second run is a no-op", code == 0 and len(f.calls) == 1 and "already" in out, out)
    code, out, _ = run_cli(["--daily", "--date", "2026-10-07", "--force"], f)
    check("--force sends again", code == 0 and len(f.calls) == 2)
    f2 = Fake()
    run_cli(["--daily", "--date", "2026-10-08"], f2)
    sent = set(f2.calls[0][1]["urlList"])
    from app import katha
    tonight = katha.pick(dt.date(2026, 10, 8))
    others = [x for x in katha.STORIES if x != tonight]
    check("a later day sends only tonight's story page, not every story again",
          f"{SITE}/katha/{tonight}" in sent
          and not any(f"{SITE}/katha/{x}" in sent for x in others), str(len(sent)))
    code, _, _ = run_cli(["--daily", "--date", "2026-10-09"], Fake(500))
    check("a failed send exits 1 and is not recorded",
          code == 1 and "daily" not in daily_state.sent("indexnow", dt.date(2026, 10, 9)))

    print("6. CLI --all and --dry-run")
    f = Fake()
    code, out, _ = run_cli(["--all", "--dry-run"], f)
    check("dry run sends nothing", code == 0 and not f.calls and "would submit" in out, out[:80])
    code, out, err = run_cli(["--all"], f)
    total = sum(len(p["urlList"]) for _, p in f.calls)
    check("--all sends the whole sitemap", code == 0 and total == len(seo_pages.sitemap_paths()),
          f"{total} vs {len(seo_pages.sitemap_paths())}")
    code, out, _ = run_cli(["--all"], f)
    check("--all runs once", code == 0 and "already" in out and sum(
        len(p["urlList"]) for _, p in f.calls) == total)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for x in failures:
            print(f"  - {x}")
        return 1
    print("indexnow: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
