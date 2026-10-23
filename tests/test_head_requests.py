"""HEAD is answered like GET without a body for public pages and crawler files.

Before this, FastAPI replied 405 to HEAD on every GET route, including /ads.txt,
/robots.txt and /sitemap.xml, while AdSense kept reporting ads.txt as "Not found".

    python -m tests.test_head_requests
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def main() -> int:
    c = TestClient(app)
    for path in ("/", "/ads.txt", "/robots.txt", "/sitemap.xml", "/panchang", "/pricing"):
        g = c.get(path)
        h = c.head(path)
        check(f"HEAD {path} -> same status as GET", h.status_code == g.status_code == 200,
              f"GET {g.status_code}, HEAD {h.status_code}")
        check(f"HEAD {path} has no body", h.content == b"", f"{len(h.content)} bytes")
        check(f"HEAD {path} keeps the content type",
              h.headers.get("content-type") == g.headers.get("content-type"),
              f"{h.headers.get('content-type')} vs {g.headers.get('content-type')}")
    ads = c.get("/ads.txt").text
    check("ads.txt still lists the publisher line", "google.com, pub-" in ads and "DIRECT" in ads, ads)
    check("an unknown page still 404s on HEAD", c.head("/no-such-page-xyz").status_code == 404)
    check("API routes are not served to HEAD", c.head("/api/health").status_code == 405)
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        return 1
    print("head requests: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
