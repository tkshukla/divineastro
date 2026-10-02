"""WhatsApp share links (DIVASTRO-107).

Pins the parts of the viral loop that fail silently: a share link whose UTM tags
analytics does not read as "whatsapp", a wa.me text that is not URL-encoded, an
SEO page without the button, and the city list the in-app buttons link with.

No server needed (FastAPI's in-process client). A throwaway SQLite database is
used — never a real one.

    ~/.venvs/divineastro/bin/python -u -m tests.test_share
"""

from __future__ import annotations

import html
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_share_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, seo_cities, share  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


_LINK = re.compile(r'<a class="share-wa" href="([^"]+)"')


def shared_link(page_html: str) -> tuple[str, str] | None:
    """(decoded message text, the divineastro.org URL inside it) from a page's button."""
    m = _LINK.search(page_html)
    if not m:
        return None
    href = html.unescape(m.group(1))
    if not href.startswith("https://wa.me/?text="):
        return None
    raw = href[len("https://wa.me/?text="):]
    if re.search(r"[\s#&?]", raw):              # anything unencoded would break the wa.me link
        return None
    text = unquote(raw)
    url = text.rsplit(" ", 1)[-1]
    return text, url


def analytics_checks() -> None:
    print("\n1. A WhatsApp share landing is attributed to WhatsApp")
    for campaign in ("milan", "panchang", "rahukaal", "choghadiya", "seo-rahu-kaal"):
        url = share.share_url("/rahu-kaal/mumbai", campaign)
        q = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        src = analytics.classify_source("", q, "divineastro.org")
        check(f"utm_campaign={campaign} -> ('whatsapp', 'share', '{campaign}')",
              src == ("whatsapp", "share", campaign), str(src))
    # As the beacon sends it: the raw query string, opened from inside WhatsApp
    # (Android app referrer) — the explicit tag still wins.
    q = dict(p.split("=", 1) for p in "utm_source=whatsapp&utm_medium=share".split("&"))
    src = analytics.classify_source("android-app://com.whatsapp/", q, "divineastro.org")
    check("?utm_source=whatsapp&utm_medium=share is source 'whatsapp'", src[0] == "whatsapp", str(src))
    check("the share path is a page the beacon may count",
          analytics.is_public_page("/rahu-kaal/mumbai") and analytics.is_public_page("/kundali-milan"))

    # End to end through the beacon, exactly as visit.js sends it on landing.
    import json

    from sqlalchemy import select

    from app.db import Visit, session
    chrome = ("Mozilla/5.0 (Linux; Android 13; SM-A145F) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36")
    q = "?utm_source=whatsapp&utm_medium=share&utm_campaign=rahukaal"
    res = client.post("/api/visit", content=json.dumps({"path": "/rahu-kaal/mumbai", "ref": "", "q": q}),
                      headers={"User-Agent": chrome, "Content-Type": "text/plain;charset=UTF-8",
                               "X-Forwarded-For": "49.37.248.77"})
    with session() as db:
        rows = db.execute(select(Visit).where(Visit.path == "/rahu-kaal/mumbai")).scalars().all()
    got = [(v.source, v.medium, v.campaign) for v in rows]
    check("a beacon from a shared link stores source 'whatsapp', medium 'share'",
          res.status_code < 300 and got == [("whatsapp", "share", "rahukaal")], f"{res.status_code} {got}")
    check("and seeds the first-touch cookie with whatsapp|rahukaal (for sign-up attribution)",
          "whatsapp|rahukaal" in res.headers.get("set-cookie", ""), res.headers.get("set-cookie", ""))


def seo_checks() -> None:
    print("\n2. SEO pages carry a plain wa.me share link")
    cases = {
        "/panchang": ("seo-panchang", "New Delhi"),
        "/panchang/mumbai": ("seo-panchang", "Mumbai"),
        "/rahu-kaal/lucknow": ("seo-rahu-kaal", "Lucknow"),
        "/choghadiya/pune": ("seo-choghadiya", "Pune"),
        "/kundali-milan": ("seo-kundali-milan", "Kundali Milan"),
    }
    for path, (campaign, needle) in cases.items():
        res = client.get(path)
        got = shared_link(res.text) if res.status_code == 200 else None
        check(f"{path}: has a fully URL-encoded wa.me share link", got is not None,
              f"status {res.status_code}")
        if not got:
            continue
        text, url = got
        parts = urlsplit(url)
        q = parse_qs(parts.query)
        check(f"{path}: links back to itself on divineastro.org",
              parts.scheme == "https" and parts.netloc == "divineastro.org" and parts.path == path, url)
        check(f"{path}: utm_source=whatsapp, utm_medium=share, utm_campaign={campaign}",
              q == {"utm_source": ["whatsapp"], "utm_medium": ["share"], "utm_campaign": [campaign]}, str(q))
        check(f"{path}: the message names the page", needle in text, text)
        check(f"{path}: opens in a new tab", 'target="_blank" rel="noopener"' in res.text)

    res = client.get("/panchang/atlantis")
    check("a 404 city page has no share button", res.status_code == 404 and "share-wa" not in res.text)
    check("the button is styled from the shared stylesheet",
          ".share-wa {" in (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8"))


def city_list_checks() -> None:
    print("\n3. The city list the in-app buttons link with")
    res = client.get("/api/share/cities")
    data = res.json() if res.status_code == 200 else {}
    slugs = [c.get("slug") for c in data.get("cities", [])]
    check("GET /api/share/cities lists every SEO city",
          slugs == [c.slug for c in seo_cities.CITIES], f"{len(slugs)} cities")
    check("it names the default (bare-URL) city", data.get("default") == seo_cities.DEFAULT.slug)
    check("it is cacheable", "max-age" in res.headers.get("cache-control", ""))
    check("each city has Hindi name and centre",
          all({"name", "name_hi", "lat", "lon"} <= set(c) for c in data.get("cities", [])))


def main() -> int:
    analytics_checks()
    seo_checks()
    city_list_checks()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("share: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
