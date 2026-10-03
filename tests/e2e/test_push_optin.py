"""The opt-in daily push button (DIVASTRO-112), in a real browser.

Pins: the button is NOT there when the server has no VAPID keys, when the
browser has no PushManager, or when notifications are blocked; nothing ever
prompts by itself; with keys set it appears under the home Today strip and on
the /vrat-tyohar pages (EN and HI); a tap registers /sw.js, subscribes with the
server's VAPID key and POSTs the subscription with the Today strip's city and
the UI language; the subscribed state offers "Unsubscribe", which POSTs
/api/push/unsubscribe.

Headless Chromium has no real push service (FCM), so PushManager.subscribe /
getSubscription are stubbed with a browser-shaped subscription, and (since
headless reports notifications as always 'denied') so is the permission
state; everything else — the service worker registration, the fetches, the
server — is real.

    ~/.venvs/divineastro/bin/python -u -m tests.e2e.test_push_optin
"""

from __future__ import annotations

import base64
import json
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import ec  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from app import push_keys  # noqa: E402
from tests.e2e.harness import Checker, Page, server  # noqa: E402

check = Checker()


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


P256DH = _b64(ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(
    serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint))
AUTH = _b64(secrets.token_bytes(16))

# Counts permission prompts, and replaces the push service with a stub.
STUB = """
(() => {
  // Headless Chromium reports notifications as 'denied' whatever is granted, so
  // the permission is simulated: 'default' until the page asks, 'granted' after.
  window.__prompts = 0;
  if (window.Notification) {
    let perm = 'default';
    Object.defineProperty(Notification, 'permission', { get: () => perm, configurable: true });
    Notification.requestPermission = async () => { window.__prompts++; perm = 'granted'; return perm; };
  }
  if (!window.PushManager) return;
  let cur = null;
  const mk = () => ({
    endpoint: 'https://fcm.googleapis.com/fcm/send/e2e-' + Math.random().toString(36).slice(2),
    toJSON() { return { endpoint: this.endpoint, expirationTime: null, keys: { p256dh: '%P%', auth: '%A%' } }; },
    unsubscribe: async () => { cur = null; window.__pushUnsubscribed = true; return true; },
  });
  PushManager.prototype.subscribe = async function (opts) {
    window.__pushKeyBytes = opts && opts.applicationServerKey ? opts.applicationServerKey.byteLength : 0;
    window.__pushVisible = !!(opts && opts.userVisibleOnly);
    cur = mk(); return cur;
  };
  PushManager.prototype.getSubscription = async function () { return cur; };
})();
""".replace("%P%", P256DH).replace("%A%", AUTH)

NO_PUSH = "delete window.PushManager;"
DENIED = "Object.defineProperty(Notification, 'permission', { get: () => 'denied', configurable: true });"
LUCKNOW = ("localStorage.setItem('astro.todayCity', JSON.stringify({latitude: 26.8467, "
           "longitude: 80.9462, timezone: 'Asia/Kolkata', label: 'Lucknow, Uttar Pradesh'}));")

PHONE = {"viewport": {"width": 360, "height": 640}, "is_mobile": True, "has_touch": True}


def _new(browser, base: str, scripts: list[str], grant: bool = True, args: dict | None = None):
    ctx = browser.new_context(**(args or PHONE))
    if grant:
        ctx.grant_permissions(["notifications"], origin=base)
    page = ctx.new_page()
    for s in scripts:
        page.add_init_script(s)
    pg = Page(page, base)
    posts: list[dict] = []

    def on_request(req):
        if req.method == "POST" and "/api/push/" in req.url:
            posts.append({"url": req.url, "body": json.loads(req.post_data or "null")})

    page.on("request", on_request)
    return ctx, pg, posts


def _hidden_stays(pg: Page, label: str) -> None:
    pg.page.wait_for_timeout(1500)
    check(label, pg.page.locator("#push-optin").count() == 0 or pg.page.is_hidden("#push-optin"))


def keys_off(browser) -> None:
    print("\n[server without VAPID keys]")
    with server({"ASTRO_VAPID_PUBLIC_KEY": "", "ASTRO_VAPID_PRIVATE_KEY": ""}) as base:
        ctx, pg, _ = _new(browser, base, [STUB])
        pg.open_home()
        pg.page.wait_for_selector("#today-strip:not(.loading)", timeout=15000)
        _hidden_stays(pg, "home: no button when push is off")
        check("no permission prompt", pg.page.evaluate("window.__prompts") == 0)
        r = pg.page.context.request.get(base + "/api/push/key")
        check("/api/push/key is a 404", r.status == 404, str(r.status))
        pg.page.goto(base + "/vrat-tyohar")
        check("/vrat-tyohar: no opt-in markup at all", pg.page.locator("#push-optin").count() == 0)
        ctx.close()


def keys_on(browser) -> None:
    pub, priv = push_keys.generate()
    env = {"ASTRO_VAPID_PUBLIC_KEY": pub, "ASTRO_VAPID_PRIVATE_KEY": priv,
           "ASTRO_PUSH_SENDER": "0"}
    with server(env) as base:
        print("\n[keys set, browser without PushManager]")
        ctx, pg, _ = _new(browser, base, [NO_PUSH])
        pg.open_home()
        _hidden_stays(pg, "home: no button without PushManager")
        ctx.close()

        print("\n[keys set, notifications blocked]")
        ctx, pg, _ = _new(browser, base, [STUB, DENIED], grant=False)
        pg.open_home()
        _hidden_stays(pg, "home: no button when notifications are denied")
        ctx.close()

        print("\n[keys set, supported browser: home, English]")
        ctx, pg, posts = _new(browser, base, [STUB, LUCKNOW])
        pg.open_home()
        pg.page.wait_for_selector("#push-subscribe", timeout=10000)
        text = pg.page.inner_text("#push-subscribe")
        check("button text (EN)", "Daily vrat & Rahu Kaal alerts" in text and "🔔" in text, repr(text))
        check("never prompts by itself", pg.page.evaluate("window.__prompts") == 0)
        strip, opt = pg.rect("#today-strip"), pg.rect("#push-optin")
        check("sits under the Today strip", opt and strip and opt["top"] >= strip["bottom"] - 1,
              f"{strip and strip['bottom']} / {opt and opt['top']}")
        check("fits a 360px screen", opt and opt["right"] <= 360 and opt["left"] >= 0, str(opt))
        pg.page.click("#push-subscribe")
        pg.page.wait_for_selector("#push-unsubscribe", timeout=10000)
        check("one prompt, after the tap", pg.page.evaluate("window.__prompts") == 1)
        check("subscribed with the server's 65-byte VAPID key, userVisibleOnly",
              pg.page.evaluate("window.__pushKeyBytes") == 65 and pg.page.evaluate("window.__pushVisible"))
        sub = [p for p in posts if p["url"].endswith("/api/push/subscribe")]
        b = sub[0]["body"] if sub else {}
        check("POST /api/push/subscribe with the Today city and language",
              b.get("label") == "Lucknow, Uttar Pradesh" and b.get("tz") == "Asia/Kolkata"
              and abs(b.get("lat", 0) - 26.8467) < 1e-6 and b.get("lang") == "en"
              and b.get("subscription", {}).get("keys", {}).get("p256dh") == P256DH, str(b)[:200])
        on = pg.page.inner_text("#push-optin")
        check("subscribed state names the city and offers Unsubscribe",
              "Lucknow" in on and "Unsubscribe" in on, repr(on))
        sw = pg.page.evaluate(
            "navigator.serviceWorker.getRegistration('/').then(r => r && (r.active || r.installing || r.waiting)"
            " ? (r.active || r.installing || r.waiting).scriptURL : null)")
        check("service worker /sw.js registered with scope /", bool(sw) and sw.endswith("/sw.js"), str(sw))
        # Language switch while subscribed: the label follows, the server copy is updated.
        pg.page.click('.lang[data-lang="hi"]')
        pg.page.wait_for_timeout(900)
        check("Hindi subscribed text", "बंद करें" in pg.page.inner_text("#push-optin"))
        resync = [p for p in posts if p["url"].endswith("/api/push/subscribe")]
        check("language switch re-sends the subscription with lang=hi",
              len(resync) >= 2 and resync[-1]["body"].get("lang") == "hi")
        pg.page.click("#push-unsubscribe")
        pg.page.wait_for_selector("#push-subscribe", timeout=5000)
        # The button swaps back first (render() runs before the awaits in
        # unsubscribe()), so wait for the browser unsubscribe to finish too.
        pg.page.wait_for_function("window.__pushUnsubscribed === true", timeout=5000)
        # The request event that fills `posts` can land a beat after the DOM swap.
        for _ in range(50):
            un = [p for p in posts if p["url"].endswith("/api/push/unsubscribe")]
            if un:
                break
            pg.page.wait_for_timeout(100)
        check("Unsubscribe POSTs the endpoint and drops the browser subscription",
              un and un[0]["body"].get("endpoint") == b.get("subscription", {}).get("endpoint")
              and pg.page.evaluate("window.__pushUnsubscribed === true"),
              f"posts={len(un)} body={un[0]['body'] if un else None} "
              f"unsub={pg.page.evaluate('window.__pushUnsubscribed')}")
        check("Hindi button text", "रोज़ व्रत और राहु काल की सूचना" in pg.page.inner_text("#push-subscribe"))
        check("no console errors", not pg.console_errors, str(pg.console_errors[:3]))
        check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()))
        ctx.close()

        print("\n[keys set: /vrat-tyohar pages]")
        for path, want, lang in (("/vrat-tyohar", "Daily vrat & Rahu Kaal alerts", "en"),
                                 ("/hi/vrat-tyohar", "रोज़ व्रत और राहु काल की सूचना", "hi"),
                                 ("/ekadashi-2026", "Daily vrat & Rahu Kaal alerts", "en")):
            ctx, pg, posts = _new(browser, base, [STUB])
            pg.page.goto(base + path, wait_until="domcontentloaded")
            pg.page.wait_for_selector("#push-subscribe", timeout=10000)
            check(f"{path}: button ({lang})", want in pg.page.inner_text("#push-subscribe"))
            check(f"{path}: no prompt before a tap", pg.page.evaluate("window.__prompts") == 0)
            pg.page.click("#push-subscribe")
            pg.page.wait_for_selector("#push-unsubscribe", timeout=10000)
            sub = [p for p in posts if p["url"].endswith("/api/push/subscribe")]
            check(f"{path}: subscribe POST, default city Delhi, lang {lang}",
                  sub and sub[0]["body"].get("lang") == lang
                  and sub[0]["body"].get("label", "").startswith("New Delhi"))
            check(f"{path}: no console errors", not pg.console_errors, str(pg.console_errors[:3]))
            ctx.close()


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            keys_off(browser)
            keys_on(browser)
        finally:
            browser.close()
    return check.finish("push opt-in")


if __name__ == "__main__":
    raise SystemExit(main())
