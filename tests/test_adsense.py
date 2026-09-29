"""AdSense is four pieces in four files, and each one fails silently on its own.

  * index.html loads the ad script and carries the verification meta tag;
  * /ads.txt must name the same publisher, or Google limits ad serving;
  * the Caddyfile CSP must allow Google's ad domains, or the browser drops the
    script with nothing but a console warning (see the PayU note there);
  * the privacy policy must disclose advertising cookies — it used to promise
    there were none.

This checks they agree with each other. No server and no database needed.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_adsense
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


def main() -> int:
    from app import legal, main as app_main

    pub = app_main.ADSENSE_PUBLISHER                      # "pub-…"
    index = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    print("index.html")
    check("verification meta names our publisher",
          f'name="google-adsense-account" content="ca-{pub}"' in index)
    check("ad script names our publisher",
          f"adsbygoogle.js?client=ca-{pub}" in index)
    for other in ("admin.html", "feedback.html"):
        page = (ROOT / "app" / "static" / other).read_text(encoding="utf-8")
        check(f"{other} carries no ads", "adsbygoogle" not in page)

    print("/ads.txt")
    body = app_main.ads_txt().body.decode()
    check("names Google, our publisher, DIRECT",
          body.strip() == f"google.com, {pub}, DIRECT, f08c47fec0942fa0", repr(body))

    print("Caddyfile CSP")
    caddy = (ROOT / "Caddyfile").read_text(encoding="utf-8")
    m = re.search(r'Content-Security-Policy\s+"([^"]+)"', caddy)
    csp = {d.split()[0]: d.split()[1:] for d in m.group(1).split(";") if d.strip()} if m else {}
    for directive in ("script-src", "frame-src", "connect-src"):
        for host in ("https://*.googlesyndication.com", "https://*.doubleclick.net",
                     "https://*.google.com", "https://*.adtrafficquality.google"):
            check(f"{directive} allows {host}", host in csp.get(directive, []))
    check("Google sign-in still reachable (form-action)",
          "https://accounts.google.com" in csp.get("form-action", []))
    check("PayU checkout still reachable (form-action)",
          "https://*.payu.in" in csp.get("form-action", []))

    print("privacy policy")
    policy = legal.privacy().body.decode()
    check("discloses Google AdSense", "Google AdSense" in policy)
    check("links to Google's ad settings", "adssettings.google.com" in policy)
    check("no longer claims there are no ad cookies",
          "do not use advertising or third-party tracking cookies" not in policy)

    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
