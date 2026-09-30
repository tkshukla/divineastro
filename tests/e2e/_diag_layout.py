"""Temporary diagnostic — not part of the suite, deleted after use.

Prints the exact pixel breakdown of header/topbar/starters/composer/thread at
1366x768 to find why the CI Linux runner measures a shorter #thread than a
local Windows run for the same viewport (DIVASTRO-72 CI investigation).
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tests.e2e.harness import server, Page, DESKTOPS  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

with server() as base, sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(**DESKTOPS["laptop_1366x768"])
    pg = Page(ctx.new_page(), base)
    pg.open_chat()
    data = pg.page.evaluate("""() => {
        const r = s => { const e = document.querySelector(s); if (!e) return null;
            const b = e.getBoundingClientRect(); return {h: Math.round(b.height), top: Math.round(b.top), bottom: Math.round(b.bottom)}; };
        return {
            thread: r('#thread'), composer: r('#ask-form'), header: r('.site-header'),
            topbar: r('.topbar'), starters: r('#starters'), vh: window.innerHeight,
        };
    }""")
    print("DIAG_LAYOUT_JSON " + json.dumps(data))
    browser.close()
