"""English and Hindi SEO pages stay byte-identical (DIVASTRO-123).

The server-rendered modules (seo_pages, rashifal_pages, vrat_pages,
muhurat_pages, nakshatra_pages, naam_milan, katha) read their text from
per-language tables so translators can add a language by filling data files.
That refactor — and every translation after it — must not change a single
byte of the English or Hindi output. This renders a fixed set of pages on a
pinned date and compares each body's SHA-256 with tests/seo_snapshots.json:

  every page type x en/hi x 3 cities (new-delhi, mumbai, bengaluru), every
  rashifal sign, muhurat kind, vrat/tyohar page, nakshatra and rashi page,
  naam-milan with a query, a 404, sitemap.xml, robots.txt; plus the text
  formatters other modules reuse (daily_message, push_message, share).

    ~/.venvs/divineastro/bin/python -u -m tests.test_seo_snapshots            # check
    ~/.venvs/divineastro/bin/python -u -m tests.test_seo_snapshots --update   # re-record
    ~/.venvs/divineastro/bin/python -u -m tests.test_seo_snapshots --dump DIR # write each body to DIR

Re-record ONLY for an intended English/Hindi change, and say so in the commit.
A translator adding Kannada never needs to: kn pages are not snapshotted.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if "ASTRO_DATABASE_URL" not in os.environ:
    _tmp = tempfile.mkdtemp(prefix="astro_snap_")
    os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import daily_message, push_message, seo_cities, seo_pages, share  # noqa: E402
from app.main import app  # noqa: E402

DAY = dt.date(2026, 11, 8)          # Diwali: the festival blocks render too
CITIES = ("new-delhi", "mumbai", "bengaluru")
LANGS = ("en", "hi")
SNAPSHOT = ROOT / "tests" / "seo_snapshots.json"


def pin(day: dt.date = DAY) -> None:
    """Every module's `_today` (they import seo_pages._today by name) -> `day`."""
    for name, mod in list(sys.modules.items()):
        if name.startswith("app.") and callable(getattr(mod, "_today", None)):
            setattr(mod, "_today", lambda d=day: d)


def _keep(path: str) -> bool:
    """Drop city copies other than CITIES (the sitemap has ~110 of each)."""
    slugs = {c.slug for c in seo_cities.CITIES}
    last = path.rstrip("/").rsplit("/", 1)[-1]
    return last not in slugs or last in CITIES


def paths() -> list[str]:
    from app import i18n
    # English and Hindi only: the sitemap also lists the translated regional
    # copies (/kn/..., /te/... - DIVASTRO-123), which are not snapshotted.
    out = [p for p in seo_pages.sitemap_paths() if _keep(p)
           and i18n.strip_prefix(p.split("?")[0])[0] in LANGS]
    for pre in ("", "/hi"):
        out += [
            f"{pre}/naam-se-kundali-milan?boy=Rahul&girl=Priya",
            f"{pre}/naam-se-kundali-milan?boy=Arjun&girl=Sita&boy_pada=2&girl_pada=3",
            f"{pre}/panchang/nowhere",
            f"{pre}/rashifal/nowhere",
            f"{pre}/nakshatra/nowhere",
        ]
    out += ["/sitemap.xml", "/robots.txt"]
    if os.environ.get("SNAP_KN"):     # for diffing a regional copy by hand; never recorded
        out = [i18n.localized_path(p, "kn") if not p.startswith("/hi") else p for p in out
               if not p.startswith(("/sitemap", "/robots"))]
        out = [p for p in out if p.startswith("/kn")]
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def texts() -> dict[str, str]:
    """The formatters other modules borrow from the SEO modules."""
    out: dict[str, str] = {}
    for lang in LANGS:
        for channel in ("plain", "telegram", "whatsapp"):
            out[f"daily_message.channel_message:{lang}:{channel}"] = \
                daily_message.channel_message(DAY, lang=lang, channel=channel)
        out[f"daily_message.build:{lang}"] = json.dumps(daily_message.build(DAY, lang=lang),
                                                        ensure_ascii=False, sort_keys=True)
        for slug in CITIES:
            c = seo_cities.BY_SLUG[slug] if hasattr(seo_cities, "BY_SLUG") else \
                next(x for x in seo_cities.CITIES if x.slug == slug)
            out[f"push_message.build:{lang}:{slug}"] = json.dumps(
                push_message.build(DAY, c.latitude, c.longitude, c.timezone, lang, city=c.name),
                ensure_ascii=False, sort_keys=True)
    out["daily_message.card_text"] = json.dumps(daily_message.card_text(DAY), ensure_ascii=False)
    for p in paths():
        if p.endswith(".xml") or p.endswith(".txt") or "?" in p:
            continue
        txt = share.seo_share_text(p)
        if txt is not None:
            out[f"share.seo_share_text:{p}"] = txt
    return out


def render() -> dict[str, bytes]:
    pin()
    client = TestClient(app, raise_server_exceptions=True)
    out: dict[str, bytes] = {}
    for p in paths():
        r = client.get(p)
        out[p] = f"{r.status_code}\n".encode() + r.content
    for k, v in texts().items():
        out["text:" + k] = v.encode()
    return out


_CACHE_BUST = re.compile(rb"\?v=\d+")


def _digest(b: bytes) -> str:
    # Static asset URLs carry a ?v=<mtime> cache-buster that changes with every
    # checkout; it is not page content, so it is left out of the comparison.
    return hashlib.sha256(_CACHE_BUST.sub(b"?v=0", b)).hexdigest()


def main(argv: list[str]) -> int:
    pages = render()
    if "--dump" in argv:
        d = Path(argv[argv.index("--dump") + 1])
        d.mkdir(parents=True, exist_ok=True)
        for k, v in pages.items():
            name = k.strip("/").replace("/", "__").replace("?", "_Q_").replace("&", "_") or "root"
            (d / (name.replace(":", "_") + ".out")).write_bytes(v)
        print(f"dumped {len(pages)} bodies to {d}")
    digests = {k: _digest(v) for k, v in pages.items()}
    if "--update" in argv:
        SNAPSHOT.write_text(json.dumps({"day": DAY.isoformat(), "pages": digests}, indent=1,
                                       ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        print(f"recorded {len(digests)} snapshots in {SNAPSHOT}")
        return 0
    want = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["pages"]
    failures = []
    for k in sorted(set(want) | set(digests)):
        if want.get(k) != digests.get(k):
            failures.append(k)
            print(f"  FAIL  {k}" + ("" if k in want else " (new)") + ("" if k in digests else " (gone)"))
    print(f"\n{len(digests) - len(failures)}/{len(set(want) | set(digests))} identical")
    if failures:
        print("Re-run with --dump DIR before and after to diff the bodies.")
    failures += regional_names()
    return 1 if failures else 0


def regional_names() -> list[str]:
    """A regional copy prints astrology names in its own script: /kn/panchang/bengaluru
    shows the day's tithi and nakshatra from names_kn. It is noindex exactly when
    seo_pages is not (yet) translated into that language (kn is since DIVASTRO-123)."""
    from app import i18n
    pin()
    client = TestClient(app, raise_server_exceptions=True)
    p = seo_pages._panchang("bengaluru", DAY)
    failures = []
    for lang in ("kn", "ta"):
        html = client.get(f"/{lang}/panchang/bengaluru").text
        n = i18n.names(lang)
        want = [n.TITHI[p["tithi"][0]["name"]], n.NAKSHATRAS[p["nakshatra"][0]["name"]],
                n.TIMINGS["rahu_kaal"], n.VARA[p["vara"]["weekday"]], n.MONTHS[DAY.month - 1]]
        missing = [w for w in want if w not in html]
        untranslated = lang not in seo_pages.TRANSLATED
        ok = not missing and ('content="noindex, follow"' in html) == untranslated
        print(f"  {'PASS' if ok else 'FAIL'}  /{lang}/panchang/bengaluru: native tithi, nakshatra, "
              f"Rahu Kaal, weekday, month; " + ("noindex" if untranslated else "indexable")
              + (f" — missing {missing}" if missing else ""))
        if not ok:
            failures.append(lang)
    return failures


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
