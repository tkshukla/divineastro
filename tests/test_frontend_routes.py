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
