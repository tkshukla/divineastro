"""Every API call the browser code makes must hit a route that really exists.

The admin panel's Approve / Reject buttons POSTed to /api/admin/upi/approve and
/reject. Neither route exists — the API has one /api/admin/upi/verify that takes
approve=true|false — so every click 404'd and a real payment could not be
approved. The backend tests all called /verify directly, so nothing noticed.

This reads the fetch()/api() calls out of app/static/*.js and checks each path
(and, where the call names one, its HTTP method) against the app's OpenAPI
schema. It needs no server and no database.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_frontend_routes
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# api('/api/x') / fetch(`/api/x/${id}`) — the path, up to a query string.
_CALL = re.compile(r"""(?:api|fetch)\(\s*([`'"])(/api/[^`'"?]*)""")
_METHOD = re.compile(r"""method:\s*['"](\w+)['"]""")


def route_table(app) -> list[tuple[re.Pattern, set[str], str]]:
    """(matcher, methods, template) for every /api path in the OpenAPI schema.

    OpenAPI rather than app.routes: current FastAPI nests included routers in an
    opaque wrapper, so iterating app.routes silently misses the account routes.
    """
    out = []
    for path, item in app.openapi()["paths"].items():
        if path.startswith("/api"):
            rx = re.compile("^" + re.sub(r"\{[^}]+\}", r"[^/]+", path) + "$")
            out.append((rx, {m.upper() for m in item}, path))
    return out


def problems(source: str, table, where: str = "") -> tuple[int, list[str]]:
    """Return (calls checked, problems) for one file's source text."""
    bad, n = [], 0
    for m in _CALL.finditer(source):
        n += 1
        raw = m.group(2)
        path = re.sub(r"\$\{[^}]*\}", "X", raw)            # a template hole is one segment
        method = (lambda mm: mm.group(1).upper() if mm else "GET")(
            _METHOD.search(source[m.end():m.end() + 260]))
        line = source.count("\n", 0, m.start()) + 1
        hits = [(methods, tpl) for rx, methods, tpl in table if rx.match(path)]
        if not hits:
            bad.append(f"{where}:{line} {method} {raw} — no such route")
        elif not any(method in methods for methods, _ in hits):
            bad.append(f"{where}:{line} {method} {raw} — route exists, but not for {method}")
    return n, bad


HOME_IDS = ("today-strip", "today-open", "today-city", "today-place", "today-results",
            "today-tithi", "today-nak", "today-rahu", "sample-qa", "sample-q", "sample-a",
            "sample-ask", "sample-ask-label", "home-cta", "free-badge")
HOME_KEYS = ("homeCta", "todayTitle", "todayTithi", "todayNak", "todayRahu", "todayNow",
             "todayChange", "todayCityPh", "todayOpen", "sampleTag", "sampleQ", "sampleA",
             "sampleNote", "sampleAsk")


def i18n_keys(app_js: str, lang: str) -> set[str]:
    """Keys of one language block of app.js's I18N table (`en: {` … `hi: {` / `};`)."""
    start = app_js.index(f"\n  {lang}: {{")
    nxt = re.search(r"\n  [a-z]{2}: \{|\n\};", app_js[start + 5:])
    block = app_js[start:start + 5 + nxt.start()] if nxt else app_js[start:]
    return set(re.findall(r"(?:^|[\s,{])([A-Za-z_]\w*):\s", block))


def home_value_checks() -> None:
    """DIVASTRO-101: the home screen's Today strip, sample answer and clearer main
    button are wired up, in both languages, and in the agreed order."""
    print("\n3. Home screen shows value before the first tap (DIVASTRO-101)")
    static = ROOT / "app" / "static"
    html = (static / "index.html").read_text(encoding="utf-8")
    app_js = (static / "app.js").read_text(encoding="utf-8")
    tools_js = (static / "tools.js").read_text(encoding="utf-8")

    missing = [i for i in HOME_IDS if f'id="{i}"' not in html]
    check("every new home element is in index.html", not missing, str(missing))

    home = html[html.index('id="stage-home"'):html.index('id="home-footer"')]
    order = ["home-tagline", "home-cta", "today-strip", "open-milan", "sample-qa", "feat-grid"]
    pos = [home.find(f'id="{i}"') for i in order]
    check("order: tagline > main button > Today strip > tools > sample Q&A > features",
          all(p >= 0 for p in pos) and pos == sorted(pos), str(dict(zip(order, pos))))

    en, hi = i18n_keys(app_js, "en"), i18n_keys(app_js, "hi")
    check("the language parser finds the real tables", len(en) > 100 and len(hi) > 100, f"{len(en)}/{len(hi)}")
    check("every new string exists in English", not [k for k in HOME_KEYS if k not in en],
          str([k for k in HOME_KEYS if k not in en]))
    check("every new string exists in Hindi", not [k for k in HOME_KEYS if k not in hi],
          str([k for k in HOME_KEYS if k not in hi]))

    cta = re.search(r'\n    homeCta: "([^"]+)"', app_js)
    check("the main button says the kundali is free and needs no sign-in",
          bool(cta) and "free" in cta.group(1).lower() and "sign-in" in cta.group(1).lower(),
          cta.group(1) if cta else "no homeCta")

    # The strip must reuse the Panchang tool's API (no second computation) and
    # remember the city defensively (localStorage throws in some private modes).
    check("the Today strip calls the existing /api/panchang", "fetch(`/api/panchang?${params}`)" in tools_js)
    check("the chosen city is remembered, inside try/catch",
          re.search(r"try \{ localStorage\.setItem\(TODAY_KEY", tools_js) is not None)
    check("a failed load hides the strip", "todayStrip.hidden = true" in tools_js)
    # Hindi Panchang: the Hindi names come from /api/panchang (app/astro/names_hi.py),
    # not from a JavaScript copy of the tables, and EN / हिं reaches an open result.
    check("tools.js keeps no copy of the tithi / nakshatra tables",
          not re.search(r"\b(TITHI_HI|NAK_HI|PAKSHA_HI)\b", tools_js))
    check("the strip and the Panchang tool read the API's Hindi names",
          "ti.label_hi" in tools_js and "nk.name_hi" in tools_js and "r.label_hi || r.name_hi" in tools_js)
    check("applyLanguage reaches the tools (window.applyToolsLanguage)",
          "window.applyToolsLanguage()" in app_js and "window.applyToolsLanguage = applyToolsLanguage" in tools_js)
    tool_keys = ("panchangTitle", "panchangSub", "lblDate", "lblPlace", "rahuKaalL", "yamagandaL",
                 "gulikaL", "abhijitL", "abhijitShort", "paErr", "muErr", "choErr", "muNeedDates",
                 "muNone", "muColDate", "muColVerdict", "muColLimbs", "muColAbhijit", "muColReasons",
                 "evMarriage", "evGrihaPravesh", "evMundan", "evNamkaran", "evGeneral")
    check("every Panchang-tool string exists in both languages",
          not [k for k in tool_keys if k not in en or k not in hi],
          str([k for k in tool_keys if k not in en or k not in hi]))

    # DIVASTRO-111: "Today: <vrat>" line, from its own tiny endpoint, failing silently.
    check("the strip has a hidden vrat line linking to /vrat-tyohar",
          re.search(r'<a class="today-vrat" id="today-vrat" href="/vrat-tyohar" hidden>', home)
          is not None)
    check("tools.js fetches /api/vrat/today", "fetch(`/api/vrat/today?${params}`)" in tools_js)
    _p, body = js_function(tools_js, "loadVrat")
    check("the vrat lookup swallows every failure", "catch" in body and "hidden = true" not in body
          and "throw" not in body)
    _p, line = js_function(tools_js, "renderVratLine")
    check("the vrat line says 'आज:' / 'Today:' and links to the Hindi page in Hindi",
          "'आज'" in line and "'Today'" in line and "/hi/vrat-tyohar" in line)
    check("an ordinary day shows no line", "!items.length" in line and "el.hidden = true" in line)


# ---- DIVASTRO-107: WhatsApp share buttons ---------------------------------
SHARE_KEYS = ("shareWa", "shareShort", "shareMilanText", "shareTodayText", "sharePanchangText")
# Anything that could identify one of the two people in a Kundali Milan.
PERSONAL = re.compile(r"\b(name|date|time|place|birth|dob|groom|bride|payload|readSide|label|"
                      r"latitude|longitude)\b", re.I)


def js_function(source: str, name: str) -> tuple[str, str]:
    """(parameter list, body) of `function name(...) { ... }`, by brace matching."""
    m = re.search(rf"function {name}\(([^)]*)\)\s*\{{", source)
    if not m:
        return "", ""
    depth, i = 1, m.end()
    while depth and i < len(source):
        depth += {"{": 1, "}": -1}.get(source[i], 0)
        i += 1
    return m.group(1), source[m.end():i - 1]


def share_checks() -> None:
    """DIVASTRO-107: share buttons are wired, bilingual, UTM-tagged, and the
    Kundali Milan share text cannot carry either person's details."""
    print("\n4. WhatsApp share buttons (DIVASTRO-107)")
    static = ROOT / "app" / "static"
    html = (static / "index.html").read_text(encoding="utf-8")
    app_js = (static / "app.js").read_text(encoding="utf-8")
    tools_js = (static / "tools.js").read_text(encoding="utf-8")
    share_js = (static / "share.js").read_text(encoding="utf-8")

    check("the Today strip has a share button", 'id="today-share"' in html and 'id="today-share-l"' in html)
    check("share.js loads before tools.js",
          0 <= html.find('/static/share.js"') < html.find('/static/tools.js"'))
    for slot in ("milan-share", "panchang-share"):
        check(f"tools.js renders #{slot}", f"shareSlot('{slot}')" in tools_js)
    for fn in ("shareMilan(ak)", "sharePanchang(p)", "shareToday(tithi, rahu)"):
        check(f"tools.js calls {fn}", fn in tools_js)

    en, hi = i18n_keys(app_js, "en"), i18n_keys(app_js, "hi")
    check("every share string exists in English", not [k for k in SHARE_KEYS if k not in en],
          str([k for k in SHARE_KEYS if k not in en]))
    check("every share string exists in Hindi", not [k for k in SHARE_KEYS if k not in hi],
          str([k for k in SHARE_KEYS if k not in hi]))
    milan_tpl = re.findall(r'shareMilanText: "([^"]+)"', app_js)
    holes = {h for tpl in milan_tpl for h in re.findall(r"\{(\w+)\}", tpl)}
    check("the Milan share text has only {score} and {max} holes, in both languages",
          len(milan_tpl) == 2 and holes == {"score", "max"}, str(holes))

    # The builder takes two numbers and nothing else; the caller passes the score.
    params, body = js_function(share_js, "milanText")
    check("milanText(score, maximum) takes only the score", params.replace(" ", "") == "score,maximum", params)
    hit = PERSONAL.search(body) if body else None
    check("milanText uses no personal field", bool(body) and not hit, hit.group(0) if hit else "")
    params, body = js_function(tools_js, "shareMilan")
    hit = PERSONAL.search(body)
    other = re.search(r"ak\.(?!total\b|maximum\b)\w+", body)
    check("shareMilan passes only ak.total / ak.maximum",
          "ak.total" in body and "ak.maximum" in body and not hit and not other,
          (hit or other).group(0) if (hit or other) else "")

    check("links are tagged utm_source=whatsapp & utm_medium=share",
          "utm_source: 'whatsapp', utm_medium: 'share'" in share_js)
    for campaign in ("'milan'", "'panchang'", "'rahukaal'"):
        check(f"campaign {campaign} is used", f", {campaign})" in tools_js)
    check("the wa.me text is URL-encoded", "wa.me/?text=${encodeURIComponent(" in share_js)
    check("phones use navigator.share; anything else falls back to the wa.me link",
          "navigator.share(" in share_js and "AbortError" in share_js and "target = '_blank'" in share_js)
    check("the city list comes from /api/share/cities", "fetch('/api/share/cities')" in share_js)


def main() -> int:
    from app.main import app

    table = route_table(app)
    print("\n1. The checker itself")
    check("it sees the account/admin routes, not just app.py's own",
          any(tpl == "/api/admin/upi/verify" for *_, tpl in table)
          and any(tpl == "/api/admin/orders/manual" for *_, tpl in table), f"{len(table)} routes")

    # It has to be able to fail, or a green run proves nothing: the exact call
    # that shipped broken, and a right path with the wrong method.
    n, bad = problems("await api(`/api/admin/upi/${act}`, { method: 'POST' });", table, "old")
    check("it flags the original bug (POST /api/admin/upi/approve|reject)", len(bad) == 1, str(bad))
    n, bad = problems("await api('/api/admin/upi/verify', { method: 'DELETE' });", table, "wrongverb")
    check("it flags a real path called with the wrong HTTP method", len(bad) == 1, str(bad))
    n, bad = problems("await api('/api/admin/upi/verify', { method: 'POST' });", table, "ok")
    check("it accepts a correct call", n == 1 and not bad, str(bad))
    n, bad = problems("await api(`/api/admin/coupons/${id}/restore`, { method: 'POST' });", table, "hole")
    check("it resolves ${...} template holes to a path segment", n == 1 and not bad, str(bad))

    print("\n2. Every call in the real frontend")
    total, all_bad = 0, []
    for js in sorted((ROOT / "app" / "static").glob("*.js")):
        n, bad = problems(js.read_text(encoding="utf-8"), table, js.name)
        total += n
        all_bad += bad
    check("every fetch()/api() call names a route (and method) that exists",
          not all_bad, "; ".join(all_bad))
    check("the scan is not vacuous", total > 40, f"{total} calls read")

    home_value_checks()
    share_checks()

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("frontend routes: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
