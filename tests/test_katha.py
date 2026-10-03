"""Katha pages and the evening channel teaser.

    ~/.venvs/divineastro/bin/python -u -m tests.test_katha
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_tmp = tempfile.mkdtemp(prefix="astro_katha_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DAILY_STATE_DIR"] = _tmp

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, katha, seo_pages  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def main() -> int:
    r = client.get("/katha")
    check("/katha: 200 and lists every story", r.status_code == 200
          and all(s.title in r.text for s in katha.STORIES.values()))
    for slug, s in katha.STORIES.items():
        r = client.get(f"/katha/{slug}")
        body = r.text
        check(f"/katha/{slug}: 200", r.status_code == 200, str(r.status_code))
        check(f"{slug}: whole story on the page (teaser + rest)",
              all(katha._html(p) in body for p in (*s.teaser, *s.rest)))
        check(f"{slug}: names its source", s.source in body)
        check(f"{slug}: Article JSON-LD", '"@type": "Article"' in body or '"@type":"Article"' in body)
        check(f"{slug}: counts with the visit beacon", analytics.is_public_page(f"/katha/{slug}"))
        t = katha.teaser(slug)
        check(f"{slug}: teaser stops before the rest", not any(p in t for p in s.rest))
        check(f"{slug}: teaser links to the page with UTM",
              f"/katha/{slug}?utm_source=whatsapp&utm_medium=channel&utm_campaign=katha" in t)
        check(f"{slug}: teaser fits a WhatsApp message", len(t) < 4000, str(len(t)))
    check("unknown story: 404", client.get("/katha/no-such-story").status_code == 404)
    check("sitemap lists the katha pages",
          all(p in seo_pages.sitemap_paths() for p in katha.sitemap_paths()))
    check("dry run prints the teaser", katha.main(["--slug", "savitri-satyavan", "--dry-run"]) == 0)
    os.environ.pop("ASTRO_WA_TOKEN", None)
    check("not configured: exit 2", katha.main(["--slug", "savitri-satyavan"]) == 2)
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        return 1
    print("katha: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
