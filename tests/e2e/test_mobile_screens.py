"""Every screen, on phones, in both themes: no sideways scroll, thumb-sized
controls, readable text, legible contrast, and no browser-side errors.

This is the screen-by-screen half of DIVASTRO-74 (mobile-first UI). The chat
screen has its own, stricter test (test_chat_layout).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_mobile_screens [--shots] [profile ...]

--shots writes a full-page PNG of every screen to tests/e2e/shots/ for a person to look at.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, PHONES, Checker, Page, server  # noqa: E402

check = Checker()
SHOTS = Path(__file__).resolve().parent / "shots"

MIN_TARGET = 44
MIN_TEXT = 12            # px — nothing a person is meant to read is smaller
SEVERE_CONTRAST = 4.5    # WCAG AA for body text (DIVASTRO-70); gradients/images are skipped, see CONTRAST_JS
AA = 4.5

# Contrast: walk up to the first opaque background, blend back down, compare with
# the text colour. Elements over gradients or images are skipped (unknowable here).
CONTRAST_JS = """
() => {
  const parse = (c) => { const m = c.match(/rgba?\\(([^)]+)\\)/); if (!m) return null;
    const p = m[1].split(',').map(parseFloat); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const over = (top, bot) => { const a = top.a + bot.a * (1 - top.a); if (a === 0) return {r:0,g:0,b:0,a:0};
    return {r: (top.r*top.a + bot.r*bot.a*(1-top.a))/a, g: (top.g*top.a + bot.g*bot.a*(1-top.a))/a,
            b: (top.b*top.a + bot.b*bot.a*(1-top.a))/a, a}; };
  const lum = ({r,g,b}) => { const f = (v) => { v/=255; return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); };
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b); };
  const ratio = (a, b) => { const l1 = lum(a), l2 = lum(b); return (Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05); };
  const effectiveBg = (el) => {
    const layers = []; let e = el;
    while (e) { const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      const c = parse(cs.backgroundColor); if (c && c.a > 0) layers.push(c);
      if (c && c.a === 1) break; e = e.parentElement; }
    let acc = layers.length && layers[layers.length-1].a === 1 ? layers.pop() : parse(getComputedStyle(document.body).backgroundColor);
    if (!acc || acc.a < 1) acc = {r:255,g:255,b:255,a:1};
    while (layers.length) acc = over(layers.pop(), acc);
    return acc; };
  const out = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    if (r.width < 4 || r.height < 4 || cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) < 0.3) continue;
    if (![...el.childNodes].some(n => n.nodeType === 3 && /[\p{L}\p{N}]/u.test(n.textContent))) continue;   // emoji-only spans ignore CSS colour
    if (el.closest('canvas, svg, [hidden], .glow')) continue;
    const fg = parse(cs.color); const bg = effectiveBg(el); if (!fg || !bg) continue;
    const solid = over({...fg, a: fg.a}, bg);
    const cr = ratio(solid, bg);
    if (cr < 4.5) out.push({sel: (el.id ? '#'+el.id : el.tagName.toLowerCase()) + (el.className && typeof el.className === 'string' ? '.'+el.className.trim().split(/\\s+/).join('.') : ''),
                            text: el.textContent.trim().slice(0, 28), cr: Math.round(cr*100)/100, fs: parseFloat(cs.fontSize)});
  }
  return out;
}
"""

SMALL_TEXT_JS = f"""
() => {{
  const out = [];
  for (const el of document.querySelectorAll('body *')) {{
    const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    if (r.width < 4 || r.height < 4 || cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (!([...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()))) continue;
    if (el.closest('svg, canvas, [hidden], script, style')) continue;
    const fs = parseFloat(cs.fontSize);
    if (fs < {MIN_TEXT}) out.push({{sel: el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\\s+/)[0] : ''),
                                    text: el.textContent.trim().slice(0, 24), fs}});
  }}
  return out;
}}
"""

TARGETS_JS = f"""
() => {{
  const out = [];
  for (const el of document.querySelectorAll('button, select, input:not([type=hidden]):not([type=checkbox]):not([type=radio]), [role=button], summary')) {{
    const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    if (r.width === 0 || r.height === 0 || cs.visibility === 'hidden' || el.closest('[hidden], .site-footer')) continue;
    if (r.bottom < 0 || r.top > 20000) continue;
    if (Math.min(r.width, r.height) < {MIN_TARGET} - 0.5)
      out.push({{sel: el.tagName.toLowerCase() + (el.id ? '#' + el.id : (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\\s+/)[0] : '')),
                 w: Math.round(r.width), h: Math.round(r.height)}});
  }}
  return out;
}}
"""


OVERFLOW_JS = """
() => {
  const vw = window.innerWidth, out = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if (r.width === 0 || r.height === 0 || cs.visibility === 'hidden' || cs.position === 'fixed' ||
        el.closest('[hidden], canvas, svg, .glow, [aria-hidden="true"]')) continue;   // decoration is allowed to bleed off-screen
    if (r.right <= vw + 1) continue;
    let scroller = false;
    for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
      const o = getComputedStyle(a).overflowX; if (o === 'auto' || o === 'scroll') { scroller = true; break; } }
    if (!scroller) out.push({sel: el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/)[0] : ''),
                            right: Math.round(r.right)});
  }
  return out;
}
"""


def pick_first_place(pg: Page, input_sel: str, list_sel: str, term: str = "Delhi") -> None:
    pg.page.fill(input_sel, term)
    pg.page.wait_for_selector(f"{list_sel} li", timeout=10000)
    pg.page.click(f"{list_sel} li >> nth=0")


def go_home(pg: Page) -> None:
    pg.open_home()


def go_birth(pg: Page) -> None:
    pg.open_home()
    pg.page.evaluate("showStage('stage-birth')")


def go_dashboard(pg: Page) -> None:
    pg.open_home()
    pg.page.evaluate("async (b) => { await castChart(b); }", BIRTH)
    pg.page.wait_for_function("document.querySelector('#dash-name')?.textContent.trim().length > 1")
    pg.page.wait_for_timeout(1500)      # cards fill in asynchronously


def go_chat(pg: Page) -> None:
    pg.open_chat()


def go_milan(pg: Page) -> None:
    pg.open_home()
    pg.page.click("#open-milan")
    for side, date in (("groom", "1990-01-01"), ("bride", "1992-06-30")):
        f = f'.milan-card[data-side="{side}"]'
        pg.page.fill(f'{f} [data-f="date"]', date)
        pick_first_place(pg, f'{f} [data-f="place"]', f'{f} [data-f="results"]')
    pg.page.click("#milan-go")
    pg.page.wait_for_selector("#stage-milan .koota-table, #stage-milan [class*='ms-']", timeout=20000)
    pg.page.wait_for_timeout(600)


def go_panchang(pg: Page) -> None:
    pg.open_home()
    pg.page.click("#open-panchang")
    pg.page.wait_for_function("document.querySelector('#panchang-result')?.innerHTML.length > 50", timeout=20000)
    pg.page.wait_for_timeout(400)


def go_muhurat(pg: Page) -> None:
    pg.open_home()
    pg.page.click("#open-muhurat")
    pick_first_place(pg, "#mu-place", "#mu-results")
    pg.page.click("#muhurat-go")
    pg.page.wait_for_function("!document.querySelector('#muhurat-result').hidden", timeout=30000)
    pg.page.wait_for_timeout(400)


def go_choghadiya(pg: Page) -> None:
    pg.open_home()
    pg.page.click("#open-choghadiya")
    pick_first_place(pg, "#cho-place", "#cho-results")
    pg.page.click("#choghadiya-go")
    pg.page.wait_for_function(
        "document.querySelector('#choghadiya-result') && document.querySelector('#choghadiya-result').innerHTML.length > 50",
        timeout=30000)
    pg.page.wait_for_timeout(400)


def go_store(pg: Page) -> None:
    pg.open_home()
    # openStore() opens the sign-in dialog instead if the account has not loaded yet.
    pg.page.wait_for_function("typeof acct !== 'undefined' && acct.user && acct.products && acct.products.length")
    pg.page.evaluate("openStore()")
    pg.page.wait_for_selector(".modal .pack")
    pg.page.wait_for_timeout(400)


SCREENS = [
    ("home", go_home, True), ("birth", go_birth, True), ("dashboard", go_dashboard, True),
    ("chat", go_chat, False), ("milan", go_milan, True), ("panchang", go_panchang, True),
    ("muhurat", go_muhurat, True), ("choghadiya", go_choghadiya, True), ("store", go_store, False),
]


def audit(profile: str, theme: str, ctx_args: dict, base: str, browser, shots: bool) -> None:
    ctx = browser.new_context(**ctx_args, color_scheme=theme)
    pg = Page(ctx.new_page(), base)
    pg.page.add_init_script(f"localStorage.setItem('astro.theme', '{theme}')")
    pg.sign_in()
    vw = ctx_args.get("viewport", {}).get("width") or 412
    for name, go, scrolls in SCREENS:
        label = f"{profile}/{theme}/{name}"
        try:
            go(pg)
        except Exception as ex:                          # a screen that cannot even be reached
            check(f"{label}: screen can be reached", False, str(ex).splitlines()[0][:120])
            continue
        if shots:
            SHOTS.mkdir(exist_ok=True)
            pg.page.screenshot(path=str(SHOTS / f"{profile}_{theme}_{name}.png"), full_page=scrolls)
        if scrolls:
            over = pg.page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            check(f"{label}: no sideways scroll", over <= 1, f"{over}px too wide")
        pg.page.wait_for_timeout(350)     # let colour transitions finish before measuring contrast
        screen_w = pg.page.viewport_size["width"]
        page_w = pg.page.evaluate("window.innerWidth")
        check(f"{label}: page is exactly as wide as the screen (not zoomed out)", abs(page_w - screen_w) <= 1,
              f"page {page_w}px on a {screen_w}px screen")
        blank = pg.page.evaluate(
            "[...document.querySelectorAll('.lang')].filter(b => b.getBoundingClientRect().width > 0 "
            "&& b.innerText.trim().length === 0).length")
        check(f"{label}: language buttons show their label", blank == 0, f"{blank} blank")
        pushed = pg.page.evaluate(OVERFLOW_JS)
        check(f"{label}: nothing is pushed off the right edge", not pushed,
              "; ".join(f"{o['sel']} to x={o['right']}" for o in pushed[:3]) + (f" (+{len(pushed) - 3})" if len(pushed) > 3 else ""))
        small_t = pg.page.evaluate(TARGETS_JS)
        check(f"{label}: controls are >= {MIN_TARGET}px to tap", not small_t,
              "; ".join(f"{t['sel']} {t['w']}x{t['h']}" for t in small_t[:4]) + (f" (+{len(small_t) - 4})" if len(small_t) > 4 else ""))
        small_x = pg.page.evaluate(SMALL_TEXT_JS)
        check(f"{label}: text is >= {MIN_TEXT}px", not small_x,
              "; ".join(f"{t['sel']} '{t['text']}' {t['fs']:.1f}px" for t in small_x[:3]) + (f" (+{len(small_x) - 3})" if len(small_x) > 3 else ""))
        weak = pg.page.evaluate(CONTRAST_JS)
        severe = [w for w in weak if w["cr"] < SEVERE_CONTRAST]
        check(f"{label}: text contrast is readable (>= {SEVERE_CONTRAST}:1)", not severe,
              "; ".join(f"{w['sel'][:36]} '{w['text']}' {w['cr']}:1" for w in severe[:3]) + (f" (+{len(severe) - 3})" if len(severe) > 3 else ""))
    check(f"{profile}/{theme}: no console errors", not pg.console_errors, "; ".join(pg.console_errors[:2]))
    check(f"{profile}/{theme}: no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    shots = "--shots" in sys.argv
    profiles = {k: v for k, v in PHONES.items() if not args or k in args}
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for name, spec in profiles.items():
                ctx_args = dict(p.devices[spec["device"]]) if "device" in spec else dict(spec)
                for theme in ("dark", "light"):
                    print(f"\n[{name} · {theme}]")
                    audit(name, theme, ctx_args, base, browser, shots)
        finally:
            browser.close()
    return check.finish("mobile screens")


if __name__ == "__main__":
    raise SystemExit(main())
