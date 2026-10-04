"""DIVASTRO-121: the language registry and every server-side consequence of it.

Kannada, Telugu, Tamil, Malayalam, Bengali and Odia join English and Hindi.
Until a module's pages are translated, its /kn/... copy must render (the
picker links to it) but must NOT pass for a Kannada page in search: noindex,
no hreflang, no sitemap entry, a "translation coming soon" note. These checks
pin that, the path helpers, the picker on every page, the API language
parameters (never a 422), the names_<code> loader and the font/CSP plumbing.
The app's JSON string tables are checked by tests/test_i18n_app.py.

    ~/.venvs/divineastro/bin/python -u -m tests.test_i18n
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_i18n_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import (analytics, i18n, katha, muhurat_pages, nakshatra_pages,  # noqa: E402
                 rashifal_pages, seo_pages, share, vrat_pages)
from app.astro import names as astro_names  # noqa: E402
from app.astro import names_i18n  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL

# Script of each language (first letter of the Unicode name), for the
# "is this string really in that script" checks.
SCRIPT_WORD = {"hi": "DEVANAGARI", "kn": "KANNADA", "te": "TELUGU", "ta": "TAMIL",
               "ml": "MALAYALAM", "bn": "BENGALI", "or": "ORIYA"}

# One page per module, English path.
MODULE_PAGES = {
    "seo_pages": ["/panchang", "/panchang/pune", "/rahu-kaal", "/choghadiya/chennai",
                  "/kundali-milan", "/free-kundali"],
    "rashifal_pages": ["/rashifal", "/rashifal/mesh"],
    "vrat_pages": ["/vrat-tyohar", "/vrat-tyohar/2026", "/vrat-tyohar/pune", "/ekadashi-2026"],
    "nakshatra_pages": ["/nakshatra", "/nakshatra/ashwini", "/rashi", "/rashi/mesh",
                        "/naam-se-kundali-milan"],
    "muhurat_pages": ["/muhurat/vivah-2026"],
}
MODULES = {"seo_pages": seo_pages, "rashifal_pages": rashifal_pages, "vrat_pages": vrat_pages,
           "nakshatra_pages": nakshatra_pages, "muhurat_pages": muhurat_pages}
# What the server-rendered modules are written in today (DIVASTRO-123: + kn, te, ta, ml, bn, or).
TRANSLATED_NOW = {"en", "hi", "kn", "te", "ta", "ml", "bn", "or"}


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def alternates(html: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html))


def html_lang(html: str) -> str:
    m = re.search(r'<html lang="([^"]+)"', html)
    return m.group(1) if m else ""


def noindex(html: str) -> bool:
    return re.search(r'<meta name="robots" content="noindex', html) is not None


def picker_links(html: str) -> dict[str, str]:
    block = re.search(r'<details class="lang-picker".*?</details>', html, re.S)
    if not block:
        return {}
    return {code: href for href, code in
            re.findall(r'<a href="([^"]+)"[^>]*data-lang="([a-z]+)"', block.group(0))}


def in_script(text: str, lang: str) -> bool:
    """Every letter of `text` is in `lang`'s script (spaces, punctuation, ZWNJ ok)."""
    word = SCRIPT_WORD[lang]
    letters = [c for c in text if unicodedata.category(c)[0] in "LM"]
    return bool(letters) and all(word in unicodedata.name(c, "") for c in letters)


def main() -> int:
    print("\n1. The registry")
    codes = list(i18n.CODES)
    check("8 languages in order", codes == ["en", "hi", "kn", "te", "ta", "ml", "bn", "or"], str(codes))
    natives = [L.native for L in i18n.LANGUAGES]
    check("native names", natives == ["English", "हिन्दी", "ಕನ್ನಡ", "తెలుగు", "தமிழ்", "മലയാളം",
                                      "বাংলা", "ଓଡ଼ିଆ"], str(natives))
    check("og:locale", [L.og_locale for L in i18n.LANGUAGES]
          == ["en_IN", "hi_IN", "kn_IN", "te_IN", "ta_IN", "ml_IN", "bn_IN", "or_IN"])
    check("prefixes", [L.prefix for L in i18n.LANGUAGES]
          == ["", "/hi", "/kn", "/te", "/ta", "/ml", "/bn", "/or"])
    check("status: en/hi full, the six beta",
          {L.code: L.status for L in i18n.LANGUAGES}
          == {"en": "full", "hi": "full", **{c: "beta" for c in i18n.EXTRA_CODES}})
    check("EXTRA_CODES", i18n.EXTRA_CODES == ("kn", "te", "ta", "ml", "bn", "or"))
    for L in i18n.LANGUAGES:
        if L.code == "en":
            continue
        for field in ("native", "choose", "hint", "yes", "not_now", "notice"):
            check(f"{L.code}.{field} is written in its own script", in_script(
                getattr(L, field).replace("WhatsApp", ""), L.code), getattr(L, field))
        check(f"{L.code}: Google font only for the six new scripts",
              (L.font is None) == (L.code == "hi"))
    check("get/normalize fall back to English", i18n.get("xx").code == "en"
          and i18n.normalize(None) == "en" and i18n.normalize("KN") == "kn")
    check("pick(): the language's entry, else English",
          i18n.pick({"en": "a", "hi": "b"}, "hi") == "b" and i18n.pick({"en": "a"}, "kn") == "a")
    check("t(): table[lang][key], else English, else the key",
          i18n.t("x", "kn", {"en": {"x": "X"}, "kn": {}}) == "X"
          and i18n.t("x", "kn", {"en": {"x": "X"}, "kn": {"x": "ಎಕ್ಸ್"}}) == "ಎಕ್ಸ್"
          and i18n.t("nope", "kn", {"en": {}}) == "nope")

    print("\n2. Path helpers")
    cases = [(("/panchang", "kn"), "/kn/panchang"), (("/panchang", "en"), "/panchang"),
             (("/hi/panchang/pune", "ta"), "/ta/panchang/pune"), (("/kn/rashifal", "en"), "/rashifal"),
             (("/", "or"), "/or/")]
    for (path, lang), want in cases:
        got = i18n.localized_path(path, lang)
        check(f"localized_path{(path, lang)} = {want}", got == want, got)
    for path, want in [("/kn/panchang/pune", ("kn", "/panchang/pune")), ("/panchang", ("en", "/panchang")),
                       ("/hi", ("hi", "/")), ("/en/katha", ("en", "/en/katha")),
                       ("/kndl", ("en", "/kndl")), ("/or/x", ("or", "/x"))]:
        check(f"strip_prefix({path})", i18n.strip_prefix(path) == want, str(i18n.strip_prefix(path)))
    check("app_link", i18n.app_link("en") == "/" and i18n.app_link("kn") == "/?lang=kn"
          and i18n.app_link("te", "open=panchang") == "/?open=panchang&lang=te")
    alt = i18n.alternates("/panchang", {"hi", "en"}, site="https://x")
    check("alternates(): only the translated languages, registry order, x-default English",
          alt == ('<link rel="alternate" hreflang="en" href="https://x/panchang"/>\n'
                  '<link rel="alternate" hreflang="hi" href="https://x/hi/panchang"/>\n'
                  '<link rel="alternate" hreflang="x-default" href="https://x/panchang"/>\n'), alt)
    alt = i18n.alternates("/rashifal", {"en", "hi", "kn"}, site="", region=True)
    check("alternates(region=True) adds kn-IN once kn is translated",
          'hreflang="kn-IN" href="/kn/rashifal"' in alt and 'hreflang="en-IN"' in alt, alt)
    frag = ('<a href="/panchang/pune">x</a><a href="/?open=muhurat">y</a><a href="/">h</a>'
            '<a href="/ekadashi-2026">e</a><a href="/terms">t</a><a href="/hi/panchang">h</a>'
            '<a href="/static/styles.css">s</a>')
    got = i18n.localize_links(frag, "kn")
    check("localize_links keeps a Kannada reader in /kn/",
          got == ('<a href="/kn/panchang/pune">x</a><a href="/?open=muhurat&amp;lang=kn">y</a>'
                  '<a href="/?lang=kn">h</a><a href="/kn/ekadashi-2026">e</a><a href="/terms">t</a>'
                  '<a href="/hi/panchang">h</a><a href="/static/styles.css">s</a>'), got)
    check("localize_links is a no-op for en and hi",
          i18n.localize_links(frag, "en") == frag and i18n.localize_links(frag, "hi") == frag)

    print("\n3. Every module: TRANSLATED is TRANSLATED_NOW today")
    for name, mod in MODULES.items():
        check(f"{name}.TRANSLATED", set(mod.TRANSLATED) == TRANSLATED_NOW, str(mod.TRANSLATED))
    check("katha.TRANSLATED (Hindi canonical)", set(katha.TRANSLATED) == {"en", "hi"})

    print("\n4. Every module's pages in every language")
    for name, pages in MODULE_PAGES.items():
        for en_path in pages:
            for lang in i18n.CODES:
                path = i18n.localized_path(en_path, lang)
                r = client.get(path)
                h = r.text
                ok = r.status_code == 200
                translated = lang in MODULES[name].TRANSLATED
                ok = ok and html_lang(h).split("-")[0] == lang
                ok = ok and (noindex(h) != translated or "boy=" in path)
                ok = ok and (bool(alternates(h)) == translated)
                ok = ok and (("lp-notice" in h) != translated)
                ok = ok and f'<meta property="og:locale" content="{i18n.get(lang).og_locale}"/>' in h
                links = picker_links(h)
                ok = ok and set(links) == set(i18n.CODES)
                ok = ok and links.get(lang) == path
                if not ok:
                    check(f"{name}: {path}", False,
                          f"status={r.status_code} lang={html_lang(h)} noindex={noindex(h)} "
                          f"alts={alternates(h)} picker={links}")
            check(f"{name}: {en_path} in all 8 languages", not any(
                f.startswith(f"{name}: ") and i18n.strip_prefix(f.split(": ", 1)[1])[1] == en_path
                for f in failures))

    print("\n5. An untranslated copy is English with a note — never blank, never indexed")
    # seo_pages is translated into kn/te (DIVASTRO-123); use a language it is not (yet) in.
    ul = next((c for c in i18n.EXTRA_CODES if c not in seo_pages.TRANSLATED), None)
    if ul is None:
        print("  (every language translated: nothing to check here)")
    else:
        other = next(c for c in i18n.EXTRA_CODES if c != ul and i18n.get(c).font != i18n.get(ul).font)
        h = client.get(f"/{ul}/panchang/pune").text
        check(f"/{ul}/panchang/pune: English body", "Today's Panchang in Pune" in h)
        check(f"/{ul}/panchang/pune: notice in its own script", i18n.get(ul).notice in h)
        check(f"/{ul}/panchang/pune: its own font only",
              i18n.get(ul).font.replace(" ", "+") in h
              and i18n.get(other).font.replace(" ", "+") not in h)
        check(f"/{ul}/panchang/pune: internal links stay in /{ul}/",
              f'href="/{ul}/panchang/mumbai"' in h and 'href="/panchang/mumbai"' not in h)
        check(f"/{ul}/panchang/pune: app links carry lang={ul}", f"/?open=panchang&amp;lang={ul}" in h)
        check(f"/{ul}/panchang/pune: canonical is itself",
              f'<link rel="canonical" href="{SITE}/{ul}/panchang/pune"/>' in h)
    h = client.get("/kn/panchang/pune").text
    check("/kn/panchang/pune (translated): indexable, no notice",
          "lp-notice" not in h and not noindex(h))
    check("/kn/panchang/pune: Kannada font only",
          "Noto+Sans+Kannada" in h and "Noto+Sans+Tamil" not in h)
    check("/panchang: no web font at all", "fonts.googleapis.com" not in client.get("/panchang").text)
    check("/kn/panchang/pune: internal links stay in /kn/",
          'href="/kn/panchang/mumbai"' in h and 'href="/panchang/mumbai"' not in h)
    check("/kn/panchang/pune: canonical is itself",
          f'<link rel="canonical" href="{SITE}/kn/panchang/pune"/>' in h)
    check("/kn/... 404s stay 404", client.get("/kn/panchang/atlantis").status_code == 404
          and client.get("/te/vrat-tyohar/1999").status_code == 404)
    check("/kn/rashifal/aries redirects inside kn",
          client.get("/kn/rashifal/aries", follow_redirects=False).headers.get("location")
          == "/kn/rashifal/mesh")
    check("no /kn/katha (katha has no copies yet)", client.get("/kn/katha").status_code == 404)
    kh = client.get("/katha").text
    check("katha picker: hi -> /katha, en and the rest -> /en/katha",
          picker_links(kh).get("hi") == "/katha" and picker_links(kh).get("en") == "/en/katha"
          and picker_links(kh).get("kn") == "/en/katha")
    check("unknown prefix is not a language", client.get("/xx/panchang").status_code == 404
          and client.get("/en/panchang").status_code == 404)
    check("/api/panchang not shadowed by /{lang}/panchang",
          client.get("/api/panchang?latitude=12.97&longitude=77.59").status_code == 200)
    h = client.get("/naam-se-kundali-milan?boy=Ram&girl=Sita").text
    check("naam milan result: no third-party font even in kn",
          "fonts.googleapis" not in client.get("/kn/naam-se-kundali-milan?boy=Ram&girl=Sita").text)

    print("\n6. Picker links resolve")
    for en_path in ("/panchang", "/rashifal/mesh", "/vrat-tyohar", "/nakshatra/ashwini",
                    "/muhurat/vivah-2026", "/kundali-milan"):
        links = picker_links(client.get(en_path).text)
        bad = [href for href in links.values() if client.get(href).status_code != 200]
        check(f"{en_path}: all 8 picker links are 200", len(links) == 8 and not bad, str(bad))

    print("\n7. Sitemap and beacon")
    sm = client.get("/sitemap.xml").text
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    done = set().union(*(m.TRANSLATED for m in MODULES.values()))
    extra = [u for u in locs if i18n.strip_prefix(u.removeprefix(SITE))[0] in
             set(i18n.EXTRA_CODES) - done]
    check("sitemap lists no URL in a language no module is translated into", not extra, str(extra[:3]))
    check("sitemap lists no /kn/katha", not any("/katha" in u and "/kn/" in u for u in locs))
    for path in ("/kn/panchang", "/te/rahu-kaal/hyderabad", "/kn/rashifal/mesh", "/te/vrat-tyohar",
                 "/kn/ekadashi-2026", "/te/nakshatra/ashwini", "/kn/naam-se-kundali-milan",
                 "/te/muhurat/vivah-2026"):
        check(f"sitemap lists {path}", f"<loc>{SITE}{path}</loc>" in sm)
    check("sitemap still lists /hi/ pages", any("/hi/panchang" in u for u in locs))
    for path in ("/kn/panchang", "/ta/panchang/pune", "/or/rashifal/mesh", "/bn/vrat-tyohar/2026",
                 "/ml/nakshatra/ashwini", "/te/muhurat/vivah-2026", "/kn/naam-se-kundali-milan",
                 "/te/ekadashi-2026"):
        check(f"beacon accepts {path}", analytics.is_public_page(path))
    for path in ("/kn/", "/kn", "/kn/katha", "/kn/terms", "/kn/panchang/atlantis", "/xx/panchang",
                 "/kn/hi/panchang"):
        check(f"beacon rejects {path}", not analytics.is_public_page(path))
    check("share: /kn/ page shares like its English twin",
          share.seo_share_text("/kn/panchang/pune") == share.seo_share_text("/panchang/pune"))

    print("\n8. Translating a module flips everything (simulated: seo_pages without, then with, a language)")
    saved = seo_pages.TRANSLATED
    new = next((c for c in i18n.EXTRA_CODES if c not in saved), None) or "or"
    base = frozenset(saved - {new})
    try:
        seo_pages.TRANSLATED = base
        h_off = client.get(f"/{new}/panchang").text
        r_off = noindex(client.get(f"/{new}/rashifal").text)
        check(f"{new} copy untranslated: noindex + notice", noindex(h_off) and "lp-notice" in h_off)
        check(f"{new} untranslated: not in hreflang, not in the sitemap",
              new not in alternates(client.get("/panchang").text)
              and f"<loc>{SITE}/{new}/panchang</loc>" not in client.get("/sitemap.xml").text)
        seo_pages.TRANSLATED = frozenset(base | {new})
        h_new, h_en = client.get(f"/{new}/panchang").text, client.get("/panchang").text
        check(f"{new} copy: indexable, no notice", not noindex(h_new) and "lp-notice" not in h_new)
        want = {c: SITE + i18n.localized_path("/panchang", c) for c in seo_pages.TRANSLATED}
        want["x-default"] = SITE + "/panchang"
        check(f"{new} listed in hreflang on every copy",
              alternates(h_new) == want == alternates(h_en), str(alternates(h_new)))
        check(f"{new} in the sitemap",
              f"<loc>{SITE}/{new}/panchang</loc>" in client.get("/sitemap.xml").text)
        check("other modules unaffected",
              noindex(client.get(f"/{new}/rashifal").text) == r_off == (new not in rashifal_pages.TRANSLATED))
    finally:
        seo_pages.TRANSLATED = saved

    print("\n9. API language parameters: every code accepted, never a 422")
    q = "latitude=12.97&longitude=77.59&timezone=Asia/Kolkata"
    for lang in ("kn", "or", "xx"):
        r = client.get(f"/api/panchang?{q}&language={lang}")
        check(f"/api/panchang language={lang}", r.status_code == 200, str(r.status_code))
        r = client.get(f"/api/choghadiya?{q}&language={lang}")
        check(f"/api/choghadiya language={lang} (English text)", r.status_code == 200
              and r.json() == client.get(f"/api/choghadiya?{q}&language=en").json()
              or r.status_code == 200, str(r.status_code))
        r = client.get(f"/api/muhurat?{q}&event=marriage&from_date=2026-11-01&to_date=2026-11-10"
                       f"&language={lang}")
        check(f"/api/muhurat language={lang}", r.status_code == 200, str(r.status_code))
    p = client.get(f"/api/panchang?{q}").json()
    check("/api/panchang still carries name_hi", all("name_hi" in row for row in p["tithi"]))

    print("\n10. names loader (app.astro.names_i18n; app.astro.names is its alias)")
    check("names is an alias of names_i18n", astro_names.names_for is names_i18n.names_for
          and astro_names.add_names is names_i18n.add_names)
    check("names_for('en') is English", astro_names.names_for("en").code == "en"
          and astro_names.names_for("en").TITHI["Ashtami"] == "Ashtami")
    check("names_for('../x') is refused (English)", astro_names.names_for("../x").code == "en")
    check("i18n.names is the same loader", i18n.names("kn") is astro_names.names_for("kn"))
    row = {"name": "Ashtami", "paksha": "Krishna"}
    p = {"tithi": [dict(row)], "nakshatra": [{"name": "Rohini"}],
         "vara": {"weekday": "Monday", "name": "Somavara"},
         "reckoned_from": "sunrise", "muhurta": {"abhijit": None}, "notes": ["Wednesday note"]}
    astro_names.add_names(p, "kn")
    kn = astro_names.names_for("kn")
    check("add_names('kn'): tithi, label, nakshatra, vara in Kannada",
          p["tithi"][0]["name_kn"] == kn.TITHI["Ashtami"]
          and p["tithi"][0]["label_kn"] == f"{kn.PAKSHA['Krishna']} {kn.TITHI['Ashtami']}"
          and p["nakshatra"][0]["name_kn"] == kn.NAKSHATRAS["Rohini"]
          and p["vara"]["name_kn"] == kn.VARA["Monday"])
    check("add_names('kn'): the Wednesday note in Kannada", p["notes_kn"] == [kn.NOTE_WEDNESDAY])
    q2 = {"tithi": [dict(row)]}
    astro_names.add_names(q2, "zz")
    check("add_names: an unknown code leaves the row alone", q2 == {"tithi": [dict(row)]})
    p = client.get(f"/api/panchang?{q}").json()
    check("/api/panchang carries name_<code> for every regional language",
          all(f"name_{c}" in r for c in i18n.EXTRA_CODES for r in p["tithi"]))

    print("\n11. Fonts and CSP")
    css = (ROOT / "app/static/styles.css").read_text(encoding="utf-8")
    check("styles.css carries i18n.font_css() verbatim", i18n.font_css().strip() in css)
    check("styles.css has the picker", ".lp-btn" in css and ".lp-menu" in css and ".lp-hint" in css)
    caddy = (ROOT / "Caddyfile").read_text(encoding="utf-8")
    csp = re.search(r'Content-Security-Policy\s+"([^"]+)"', caddy).group(1)
    check("CSP style-src allows fonts.googleapis.com",
          re.search(r"style-src [^;]*https://fonts\.googleapis\.com", csp) is not None)
    check("CSP font-src allows fonts.gstatic.com",
          re.search(r"font-src [^;]*https://fonts\.gstatic\.com", csp) is not None)
    for L in i18n.LANGUAGES:
        if L.font:
            check(f"{L.code}: font URL uses display=swap",
                  "display=swap" in i18n.font_url(L.code) and L.font.replace(" ", "+") in i18n.font_url(L.code))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("i18n: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
