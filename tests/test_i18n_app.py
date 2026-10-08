"""The app's (SPA's) UI strings: one JSON file per language (DIVASTRO-121).

app.js and account.js used to carry their English and Hindi strings inline, and
tools.js / push.js / share.js a few dozen more as `hi ? '…' : '…'`. They now
live in app/static/i18n/<code>.json, English being the per-key fallback, so a
translation agent adds a language by filling one file. This checks:

* every file exists for every registry language and is a flat JSON object
  (string values, except the few structured acct.* entries);
* en.json has every key the JS asks for (t("…"), tr('…'), at("…"), push.js);
* hi.json still has every Hindi string the old inline tables had, unchanged,
  and is as complete as en.json (no Hindi regression);
* the new languages' files only use keys English has (a typo'd key would
  silently never show);
* the page at / inlines the registry and the English + Hindi tables, and its
  header carries the language picker with all eight languages.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_i18n_app
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

STATIC = ROOT / "app" / "static"
I18N_DIR = STATIC / "i18n"
BASELINE = Path(__file__).resolve().parent / "i18n_hi_baseline.json"
# Entries whose value is a list or a map rather than one string (a translation
# keeps the same shape): the suggested questions, and three account ones.
STRUCTURED = {"starters", "acct.upiHelpApps", "acct.errors", "acct.status"}

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def load(code: str) -> dict:
    return json.loads((I18N_DIR / f"{code}.json").read_text(encoding="utf-8"))


def keys_used_by_js() -> set[str]:
    """Literal keys the browser code looks up."""
    keys: set[str] = set()
    for name in ("app.js", "tools.js", "share.js"):
        src = (STATIC / name).read_text(encoding="utf-8")
        keys |= set(re.findall(r"""\bt\(\s*["']([A-Za-z0-9_.]+)["']\s*\)""", src))
        keys |= set(re.findall(r"""\btr\(\s*["']([A-Za-z0-9_.]+)["']\s*,""", src))
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    if "t(`feat${i}`)" in app:
        keys |= {f"feat{i}" for i in range(1, 7)}
    acct = (STATIC / "account.js").read_text(encoding="utf-8")
    keys |= {f"acct.{k}" for k in re.findall(r"""\bat\(\s*["']([A-Za-z0-9_]+)["']\s*\)""", acct)}
    push = (STATIC / "push.js").read_text(encoding="utf-8")
    keys |= {f"push.{k}" for k in re.findall(r"""\btr\(\s*'([A-Za-z0-9_]+)'\s*\)""", push)}
    return keys


def file_checks(codes: list[str]) -> dict[str, dict]:
    print("\n1. One valid JSON file per language")
    tables = {}
    for code in codes:
        path = I18N_DIR / f"{code}.json"
        try:
            table = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            check(f"{code}.json loads", False, str(e))
            continue
        bad = [k for k, v in table.items() if not isinstance(k, str)
               or not (isinstance(v, str) or (k in STRUCTURED and isinstance(v, (list, dict))))]
        check(f"{code}.json is a flat object of strings", isinstance(table, dict) and not bad, str(bad[:5]))
        tables[code] = table
    extra = sorted(p.stem for p in I18N_DIR.glob("*.json") if p.stem not in codes)
    check("no JSON file for a language the registry does not know", not extra, str(extra))
    return tables


def coverage_checks(tables: dict[str, dict]) -> None:
    print("\n2. English has every key the JS uses; Hindi has every key English has")
    en, hi = tables["en"], tables["hi"]
    used = keys_used_by_js()
    check("the key scan is not vacuous", len(used) > 250, f"{len(used)} keys")
    missing = sorted(used - set(en))
    check("en.json has every key app/account/tools/share/push.js look up", not missing, str(missing[:20]))
    gaps = sorted(k for k in en if k not in hi)
    check("hi.json has every key en.json has", not gaps, str(gaps[:20]))
    empty = sorted(k for k, v in en.items() if v == "" )
    check("no empty English strings", not empty, str(empty[:10]))

    print("\n3. Hindi: no regression against the old inline tables")
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    lost = [k for k, v in base["app"].items() if hi.get(k) != v]
    check(f"all {len(base['app'])} old I18N.hi strings unchanged in hi.json", not lost, str(lost[:10]))
    lost = [k for k, v in base["acct"].items() if hi.get(f"acct.{k}") != v]
    check(f"all {len(base['acct'])} old A_I18N.hi strings unchanged as acct.*", not lost, str(lost[:10]))

    print("\n4. New languages only use keys English has")
    for code, table in tables.items():
        if code in ("en", "hi"):
            continue
        stray = sorted(set(table) - set(en))
        check(f"{code}.json: every key exists in en.json", not stray, str(stray[:10]))


def js_checks(codes: list[str]) -> None:
    print("\n5. The JS knows every language and has no EN/हिं leftovers")
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    m = re.search(r"\[((?:\"[a-z]{2}\",?\s*){8,})\]\.map\(\(code\)", app)
    fallback = re.findall(r"\"([a-z]{2})\"", m.group(1)) if m else []
    check("app.js's fallback language list is the registry's", fallback == codes, str(fallback))
    check("state.lang is chosen from all registry codes (pickLang), not an en/hi map",
          "pickLang(new URLSearchParams(location.search).get(\"lang\"), storedLang())" in app
          and '({ hi: "hi", en: "en" })' not in app)
    check("the old EN/हिं button handlers are gone", '$$(".lang")' not in app)
    check("window.daSetLang / daGetLang are exposed for langpick.js",
          "window.daSetLang" in app and "window.daGetLang" in app)
    check("other languages are fetched from /static/i18n/<code>.json",
          "/static/i18n/${code}.json" in app)
    for name in ("tools.js", "account.js", "share.js"):
        src = (STATIC / name).read_text(encoding="utf-8")
        inline = re.findall(r"""(?:isHi|\bhi)\s*\?\s*['"`][^'"`]*['"`]\s*:""", src)
        check(f"{name}: no inline `hi ? '…' : '…'` UI strings left", not inline, str(inline[:3]))
    index = (STATIC / "index.html").read_text(encoding="utf-8")
    check("index.html: the picker and data placeholders are there, the old buttons are not",
          "<!--LANG_PICKER-->" in index and "<!--LANG_DATA-->" in index
          and 'class="lang active"' not in index and "/static/langpick.js" in index)


def page_checks(codes: list[str]) -> None:
    from app import lang_data
    print("\n6. GET / inlines the registry + en/hi strings and renders the picker")
    tmp = tempfile.mkdtemp(prefix="astro_i18n_")
    os.environ.setdefault("ASTRO_DATABASE_URL", f"sqlite:///{Path(tmp).as_posix()}/t.db")
    from fastapi.testclient import TestClient
    from app.main import app
    html = TestClient(app).get("/").text
    m = re.search(r"window\.DA_LANGS=(\[.*?\]);window\.DA_I18N=", html)
    langs = json.loads(m.group(1)) if m else []
    listed = [c for c in codes if lang_data.listed(c)]       # DIVASTRO-143: new ones appear once READY
    check("DA_LANGS lists the listed languages in order", [l["code"] for l in langs] == listed,
          str([l.get("code") for l in langs]))
    m = re.search(r"window\.DA_I18N=(\{.*?\});window\.DA_I18N_V=", html)
    inline = json.loads(m.group(1)) if m else {}
    check("DA_I18N carries English and Hindi only (others load on demand)",
          sorted(inline) == ["en", "hi"] and inline["hi"] == load("hi"), str(sorted(inline)))
    check("the inline script cannot be closed early by a string", "</script" not in (m.group(1) if m else ""))
    header = html.split("<header", 1)[1].split("</header>", 1)[0] if "<header" in html else ""
    links = re.findall(r'<a href="([^"]*)" hreflang="[^"]*" lang="[^"]*" data-lang="([a-z]{2})"', header)
    check("the header has the language picker with every listed language",
          'class="lang-picker"' in header and [c for _, c in links] == listed, str(links))
    check("each picker link opens the app in that language (works without JS)",
          all(h == f"/?lang={c}" for h, c in links), str(links))
    check("no placeholder is left in the page", "<!--LANG_" not in html)


def main() -> int:
    from app import i18n
    codes = list(i18n.CODES)
    tables = file_checks(codes)
    if {"en", "hi"} <= set(tables):
        coverage_checks(tables)
    js_checks(codes)
    page_checks(codes)
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("i18n app: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
