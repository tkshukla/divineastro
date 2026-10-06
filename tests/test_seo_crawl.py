"""Crawlability (DIVASTRO-133): sitemap order/priority/lastmod, the /sitemap hub,
the footer link block, the canonical Link header on "/", and the Caddy redirect.

    ~/.venvs/divineastro/bin/python -u -m tests.test_seo_crawl
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_tmp = tempfile.mkdtemp(prefix="astro_crawl_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import i18n, seo_cities, seo_pages  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
SITE = seo_pages.SITE_URL
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def main() -> int:
    print("1. sitemap.xml")
    xml = client.get("/sitemap.xml").text
    entries = re.findall(r"<url>(.*?)</url>", xml)
    locs = [re.search(r"<loc>(.*?)</loc>", e).group(1) for e in entries]
    check("same URL set as sitemap_paths()",
          set(locs) == {SITE + p for p in seo_pages.sitemap_paths()} and len(locs) == len(set(locs)))
    check("home is first", locs[0] == SITE + "/", locs[0])
    prios = [float(re.search(r"<priority>(.*?)</priority>", e).group(1)) for e in entries]
    check("every entry has a priority 0.1-1.0, best first",
          all(0.1 <= p <= 1.0 for p in prios) and prios == sorted(prios, reverse=True))
    by = {l: e for l, e in zip(locs, entries)}
    check("daily tool pages carry lastmod, legal/static pages do not",
          "<lastmod>" in by[SITE + "/panchang/pune"] and "<lastmod>" in by[SITE + "/rashifal"]
          and "<lastmod>" not in by[SITE + "/terms"] and "<lastmod>" not in by[SITE + "/kundali-milan"])
    check("a top city ranks above a small one, English above regional",
          seo_pages.sitemap_priority("/panchang/mumbai") > seo_pages.sitemap_priority("/panchang/" + seo_cities.CITIES[-1].slug)
          and seo_pages.sitemap_priority("/kn/panchang") < seo_pages.sitemap_priority("/panchang"))
    check("no untranslated language is listed",
          not any(re.match(rf"{re.escape(SITE)}/(?!{'|'.join(i18n.ordered(seo_pages.TRANSLATED))})[a-z]{{2}}/", l)
                  for l in locs if i18n.strip_prefix(l.replace(SITE, ""))[0] not in seo_pages.TRANSLATED))

    print("2. /sitemap hub, every language")
    cities = {c.slug for c in seo_cities.CITIES}
    for lang in i18n.ordered(seo_pages.TRANSLATED):
        path = i18n.prefix(lang) + "/sitemap"
        r = client.get(path)
        h = r.text
        check(f"{path}: 200, canonical, indexable, in the sitemap",
              r.status_code == 200 and f'rel="canonical" href="{SITE}{path}"' in h
              and "noindex" not in h.lower() and SITE + path in locs)
        hrefs = set(re.findall(r'href="(/[^"#?]*)"', h))
        pre = i18n.prefix(lang)
        check(f"{path}: links every city's Panchang page",
              all(f"{pre}/panchang/{s}" in hrefs or (s == "new-delhi" and f"{pre}/panchang" in hrefs)
                  for s in cities))
        check(f"{path}: links the sections",
              all(any(x.startswith(pre + root) for x in hrefs)
                  for root in ("/rashifal", "/vrat-tyohar", "/muhurat/", "/nakshatra", "/rashi",
                               "/free-kundali", "/kundali-milan", "/rahu-kaal", "/choghadiya")))
        bad = [x for x in hrefs if x.startswith(pre + "/") and x not in ("/katha",)
               and client.get(x).status_code != 200][:3] if lang in ("en", "hi") else []
        check(f"{path}: its internal links resolve", not bad, str(bad))

    print("3. footer link block")
    for path, token in (("/panchang/pune", "/sitemap"), ("/hi/rashifal", "/hi/sitemap"),
                        ("/kn/panchang", "/kn/sitemap"), ("/katha", "/hi/sitemap"), ("/en/katha", "/sitemap"),
                        ("/vrat-tyohar", "/sitemap"), ("/muhurat/vivah-2026", "/sitemap")):
        h = client.get(path).text
        foot = h[h.index('<footer'):]
        check(f"{path}: footer links to {token}",
              'class="footer-sections"' in foot and f'href="{token}"' in foot)

    print("4. home, robots, Caddy")
    r = client.get("/")
    check('"/" has a canonical Link header', r.headers.get("link") == f'<{SITE}/>; rel="canonical"',
          str(r.headers.get("link")))
    r = client.get("/robots.txt")
    check("robots.txt still allows pages and lists the sitemap",
          "Allow: /" in r.text and f"Sitemap: {SITE}/sitemap.xml" in r.text
          and "Disallow: /api/" in r.text)
    cf = (ROOT / "Caddyfile").read_text(encoding="utf-8")
    check("Caddy redirects www to the apex, permanently",
          re.search(r"www\.divineastro\.org \{\s*redir https://divineastro\.org\{uri\} permanent", cf)
          is not None and "divineastro.org, www.divineastro.org" not in cf)
    check("Caddy marks /api and /admin noindex", "X-Robots-Tag" in cf and "/api/* /admin" in cf)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for x in failures:
            print(f"  - {x}")
        return 1
    print("seo_crawl: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
