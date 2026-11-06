"""Bhakti: the text files, the schema checks and the pages.

    ~/.venvs/divineastro/bin/python -u -m tests.test_bhakti

The page checks loop over whatever files are in app/bhakti_texts; the schema
checks use fixture files written to temp dirs.
"""

from __future__ import annotations

import copy
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_tmp = tempfile.mkdtemp(prefix="astro_bhakti_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DAILY_STATE_DIR"] = _tmp
os.environ.pop("ASTRO_BHAKTI_DIR", None)

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, bhakti, seo_pages  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
CHALISA = json.loads((bhakti.TEXT_DIR / "hanuman-chalisa.json").read_text(encoding="utf-8"))


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def load_dir(docs: dict[str, dict]) -> dict | str:
    """Write `docs` (file stem -> JSON object) to a temp dir and load it."""
    d = Path(tempfile.mkdtemp(prefix="bhakti_fx_", dir=_tmp))
    for stem, doc in docs.items():
        (d / f"{stem}.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    try:
        return bhakti.load(d)
    except bhakti.TextError as exc:
        return str(exc)


def fixture(slug: str = "fx", **changes) -> dict:
    doc = copy.deepcopy(CHALISA)
    doc.update(slug=slug, related=[])
    doc.update(changes)
    return doc


print("The catalogue")
check("there are texts", len(bhakti.TEXTS) >= 30, str(len(bhakti.TEXTS)))
cats = {t.category for t in bhakti.TEXTS.values()}
check("every category has a text", cats == set(bhakti.CATEGORIES), str(set(bhakti.CATEGORIES) - cats))
check("every related slug exists",
      all(r in bhakti.TEXTS for t in bhakti.TEXTS.values() for r in t.related))
hc = bhakti.TEXTS["hanuman-chalisa"]
chaupai = next(s for s in hc.sections if s.heading == "चौपाई")
lines = sum(len(v.splitlines()) for k, v in chaupai.blocks if k == "v")
check("Hanuman Chalisa has 40 chaupais (80 half-lines)", lines == 80, str(lines))

print("Schema checks")
ok = load_dir({"fx": fixture()})
check("a valid file loads", isinstance(ok, dict) and "fx" in ok, str(ok)[:200])
for label, doc, want in [
    ("slug must match the file name", fixture(slug="other"), "file name"),
    ("unknown category", fixture(category="bhajan"), "category"),
    ("unknown deity", fixture(deity="zeus"), "deity"),
    ("Hindi title required", fixture(title="Hanuman Chalisa"), "Devanagari"),
    ("title_en must be Latin", fixture(title_en="हनुमान"), "Latin"),
    ("no HTML in a paragraph", fixture(intro=["<b>x</b>"]), "HTML"),
    ("unbalanced bold", fixture(intro=["*x"]), "unbalanced"),
    ("block must be v or p", fixture(sections=[{"heading": "", "blocks": [{"x": "y"}]}]), "blocks[0]"),
    ("empty sections", fixture(sections=[]), "sections"),
    ("unknown field", fixture(extra=1), "unknown field"),
]:
    got = load_dir({"fx": doc})
    check(label, isinstance(got, str) and want in got and got.startswith("fx.json"), str(got)[:200])
got = load_dir({"fx": fixture(related=["missing"])})
check("a related slug with no file fails", isinstance(got, str) and "missing" in got, str(got)[:200])

print("Pages")
r = client.get("/bhakti")
check("/bhakti is 200", r.status_code == 200, str(r.status_code))
check("the index links every text",
      all(f'href="/bhakti/{s}"' in r.text for s in bhakti.TEXTS))
check("the index is Hindi", 'lang="hi' in r.text)
for slug, t in bhakti.TEXTS.items():
    r = client.get(f"/bhakti/{slug}")
    if r.status_code != 200 or t.title not in r.text or 'class="verse"' not in r.text:
        check(f"/bhakti/{slug} renders", False, str(r.status_code))
check("every text page renders with its title and verses", not [f for f in failures if "renders" in f])
r = client.get("/bhakti/hanuman-chalisa")
check("canonical is the bhakti URL",
      f'<link rel="canonical" href="{SITE}/bhakti/hanuman-chalisa"' in r.text)
check("not noindex", "noindex" not in r.text)
check("verse lines keep their breaks", "जय हनुमान ज्ञान गुन सागर।<br>" in r.text)
check("CreativeWork JSON-LD", '"@type": "CreativeWork"' in r.text or '"@type":"CreativeWork"' in r.text)
check("a correction link", 'href="/feedback"' in r.text)
r = client.get("/bhakti/no-such-text")
check("unknown slug is 404", r.status_code == 404, str(r.status_code))

print("Wiring")
sm = client.get("/sitemap.xml").text
check("sitemap.xml lists the index and the texts",
      f"{SITE}/bhakti</loc>" in sm and f"{SITE}/bhakti/diwali-lakshmi-puja-vidhi</loc>" in sm)
check("the /sitemap hub links /bhakti", 'href="/bhakti"' in client.get("/sitemap").text)
check("the footer links /bhakti", 'href="/bhakti"' in client.get("/katha").text)
check("analytics counts the pages as public",
      analytics._is_public_page("/bhakti") and analytics._is_public_page("/bhakti/hanuman-chalisa")
      and not analytics._is_public_page("/bhakti/no-such-text"))
check("titles are unique", len({t.title for t in bhakti.TEXTS.values()}) == len(bhakti.TEXTS))
check("no stray Latin full stop ending a Hindi paragraph",
      not [t.slug for t in bhakti.TEXTS.values() for s in t.sections for k, v in s.blocks
           if k == "p" and re.search(r"[ऀ-ॿ]\.$", v)])

print()
if failures:
    print(f"{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("all passed")
