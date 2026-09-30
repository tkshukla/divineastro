"""Temporary diagnostic — not part of the suite, deleted after use.

Finds exactly which .topbar child is wrapping in CI (DIVASTRO-72 investigation,
round 2 — the .who-text-truncation fix made zero difference, so the wrap is
somewhere else in the topbar).
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
        const bar = document.querySelector('.topbar');
        const kids = [...bar.children].map(e => {
            const b = e.getBoundingClientRect();
            return {tag: e.tagName, cls: e.className, id: e.id,
                    x: Math.round(b.left), y: Math.round(b.top),
                    w: Math.round(b.width), h: Math.round(b.height)};
        });
        return {bar_w: bar.getBoundingClientRect().width, kids};
    }""")
    print("DIAG_LAYOUT_JSON " + json.dumps(data))
    pg.page.screenshot(path="/tmp/topbar_ci.png")
    browser.close()
