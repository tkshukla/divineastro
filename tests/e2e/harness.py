"""Shared plumbing for the browser (end-to-end) tests.

Why this exists: the API tests cannot see what a customer's browser sees. Bugs
that only a real browser reveals have already reached production — the CSP
`form-action` gap that silently blocked PayU checkout ("nothing happens when I
click Buy") and a phone layout that left the answer area 34px tall with the
question box below the screen. See DIVASTRO-72.

    pip install -r requirements-dev.txt
    python -m playwright install chromium
    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_chat_layout

Each run starts its own server on a free port with a throwaway SQLite database,
the dev sign-in, the test payment gateway and no LLM, so it is free, offline
and deterministic.
"""

from __future__ import annotations

import contextlib
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# A chart every test can reuse. Fixed inputs -> identical chart every run.
BIRTH = {
    "name": "E2E Tester", "date": "1985-06-15", "time": "10:30",
    "place": "Delhi, India", "latitude": 28.6519, "longitude": 77.2315,
    "timezone": "Asia/Kolkata", "zodiac": "sidereal", "ayanamsa": "lahiri",
    "house_system": "Whole Sign", "time_known": True, "gender": "male",
}

# Phones people actually use. Playwright's own device descriptors set the user
# agent, touch and pixel ratio; the two small ones are hand-made because the
# most common budget Android screens are 360px wide.
PHONES = {
    "pixel7_412x915": {"device": "Pixel 7"},
    "android_360x640": {"viewport": {"width": 360, "height": 640}, "is_mobile": True,
                        "has_touch": True, "device_scale_factor": 3},
    "iphone_375x812": {"viewport": {"width": 375, "height": 812}, "is_mobile": True,
                       "has_touch": True, "device_scale_factor": 3},
    "iphone_se_375x667": {"viewport": {"width": 375, "height": 667}, "is_mobile": True,
                          "has_touch": True, "device_scale_factor": 2},
    # The narrowest screens still in use; anything that fits here fits everywhere.
    "small_320x568": {"viewport": {"width": 320, "height": 568}, "is_mobile": True,
                      "has_touch": True, "device_scale_factor": 2},
}
DESKTOPS = {
    "laptop_1366x768": {"viewport": {"width": 1366, "height": 768}},
    "desktop_1440x800": {"viewport": {"width": 1440, "height": 800}},
}


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def server(extra_env: dict | None = None):
    """Run the app for the duration of the block; yields its base URL."""
    port = _free_port()
    tmp = tempfile.mkdtemp(prefix="astro_e2e_")
    env = dict(os.environ)
    env.update({
        "ASTRO_DATABASE_URL": f"sqlite:///{Path(tmp).as_posix()}/e2e.db",
        "ASTRO_DEV_LOGIN": "1", "ASTRO_COOKIE_SECURE": "0",
        "ASTRO_GATEWAY": "test", "ASTRO_SECRET_KEY": "e2e-secret",
        "ASTRO_ADMIN_EMAILS": "admin@e2e.test",
        "PYTHONIOENCODING": "utf-8",
    })
    env.update(extra_env or {})
    log = open(Path(tmp) / "server.log", "w", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
         "--port", str(port)],
        cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(120):
            try:
                urllib.request.urlopen(f"{base}/api/health", timeout=1)
                break
            except Exception:
                if proc.poll() is not None:
                    raise RuntimeError(f"server exited early, see {tmp}/server.log")
                time.sleep(0.5)
        else:
            raise RuntimeError(f"server did not come up, see {tmp}/server.log")
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


# Recorded inside every page so a test can assert on them afterwards. A CSP
# violation never throws, so nothing else would ever surface it.
_WATCH = """
window.__csp = [];
document.addEventListener('securitypolicyviolation', (e) => {
  window.__csp.push({directive: e.violatedDirective, blocked: e.blockedURI});
});
"""


class Page:
    """A Playwright page plus the things every test wants to assert on."""

    def __init__(self, page, base: str):
        self.page = page
        self.base = base
        self.console_errors: list[str] = []
        self.failed_requests: list[str] = []
        page.add_init_script(_WATCH)
        page.on("console", lambda m: self.console_errors.append(m.text)
                if m.type == "error" else None)
        page.on("pageerror", lambda e: self.console_errors.append(f"pageerror: {e}"))
        page.on("response", lambda r: self.failed_requests.append(f"{r.status} {r.url}")
                if r.status >= 500 and r.url.startswith(base) else None)

    def csp_violations(self) -> list[dict]:
        return self.page.evaluate("window.__csp || []")

    def sign_in(self, email: str = "e2e@example.com", name: str = "E2E Tester") -> None:
        r = self.page.context.request.post(
            f"{self.base}/api/auth/dev", data={"email": email, "name": name})
        assert r.ok, f"dev sign-in failed: {r.status}"

    def open_home(self) -> None:
        self.page.goto(self.base + "/", wait_until="domcontentloaded")
        self.page.wait_for_function("typeof showStage === 'function'")

    def open_chat(self) -> None:
        """Signed in, chart cast, on the chat screen with the opening reading."""
        self.sign_in()
        self.open_home()
        self.page.evaluate("async (b) => { await castChart(b); showStage('stage-chat'); }", BIRTH)
        self.page.wait_for_selector("#thread .msg.bot", timeout=30000)
        # No LLM in tests: the rule engine's own answer is used.
        self.page.evaluate("state.provider = 'off'")
        self.page.wait_for_timeout(400)      # let entry animations settle

    def rect(self, selector: str) -> dict | None:
        return self.page.evaluate(
            """(s) => { const e = document.querySelector(s); if (!e) return null;
                        const r = e.getBoundingClientRect();
                        return {top: r.top, bottom: r.bottom, height: r.height,
                                left: r.left, right: r.right, width: r.width}; }""",
            selector)


class Checker:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def __call__(self, label: str, ok: bool, detail: str = "") -> None:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
        if not ok:
            self.failures.append(label)

    def finish(self, name: str) -> int:
        print("\n" + "=" * 60)
        if self.failures:
            print(f"{len(self.failures)} FAILURES")
            for f in self.failures:
                print("  -", f)
            return 1
        print(f"{name}: all green")
        return 0
