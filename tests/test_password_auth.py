"""Username/password sign-in — a second account path alongside OAuth,
specifically for someone who does not want to reveal any identity (no email,
no real name). See app/auth.py's module docstring for why this is a
separate pair of functions rather than a branch inside upsert_user().

No server needed (FastAPI's in-process TestClient).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_password_auth
"""

from __future__ import annotations

import os
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="astro_pwauth_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["ASTRO_GATEWAY"] = "test"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def rand_username(prefix: str = "u") -> str:
    return f"{prefix}{random.randint(100000, 999999)}"


def main() -> int:
    print("\n1. Registering a new username/password account")
    client = TestClient(app)
    username = rand_username()
    r = client.post("/api/auth/register", json={"username": username, "password": "correcthorse123"})
    check("HTTP 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")
    data = r.json()
    check("no email is attached to the account", data["user"]["email"] == "", str(data["user"]))
    check("the account displays by its chosen username, not a generic placeholder",
          data["user"]["name"] == username, data["user"]["name"])
    check("the signup bonus was granted", data["user"]["credits"] == 10, str(data["user"]["credits"]))
    check("a session cookie was actually issued", "gd_session" in client.cookies, str(client.cookies))

    print("\n2. The same username cannot be registered twice")
    r2 = client.post("/api/auth/register", json={"username": username, "password": "anotherpassword1"})
    check("409, not a silent overwrite", r2.status_code == 409, f"{r2.status_code} {r2.text[:200]}")

    print("\n3. Validation: short username, short password")
    r3 = client.post("/api/auth/register", json={"username": "ab", "password": "longenoughpassword"})
    check("a too-short username is rejected", r3.status_code == 400, str(r3.status_code))
    r4 = client.post("/api/auth/register", json={"username": rand_username(), "password": "short"})
    check("a too-short password is rejected", r4.status_code == 400, str(r4.status_code))

    print("\n4. Logging in with the right credentials, from a fresh client (no stale cookie)")
    fresh = TestClient(app)
    r5 = fresh.post("/api/auth/login", json={"username": username, "password": "correcthorse123"})
    check("login succeeds", r5.status_code == 200, f"{r5.status_code} {r5.text[:200]}")
    me = fresh.get("/api/me").json()
    check("the session actually resolves to this account",
          me["user"]["name"] == username, str(me))

    print("\n5. Wrong password and unknown username give the SAME generic error "
          "(no account enumeration)")
    wrong_pw = TestClient(app).post("/api/auth/login", json={"username": username, "password": "nope"})
    unknown_user = TestClient(app).post("/api/auth/login",
                                        json={"username": rand_username("ghost"), "password": "nope12345"})
    check("wrong password -> 401", wrong_pw.status_code == 401, str(wrong_pw.status_code))
    check("unknown username -> 401 (not 404 — would leak which usernames exist)",
          unknown_user.status_code == 401, str(unknown_user.status_code))
    check("both show the same generic message",
          wrong_pw.json()["detail"] == unknown_user.json()["detail"],
          f"{wrong_pw.json()['detail']!r} vs {unknown_user.json()['detail']!r}")

    print("\n6. A blocked password-account user is refused, same as any other blocked user")
    blocked_username = rand_username("blocked")
    client2 = TestClient(app)
    client2.post("/api/auth/register", json={"username": blocked_username, "password": "correcthorse123"})
    me2 = client2.get("/api/me").json()
    uid = me2["user"]["id"]
    os.environ["ASTRO_ADMIN_EMAILS"] = "owner@divineastro.org"
    admin_client = TestClient(app)
    admin_client.post("/api/auth/dev", json={"email": "owner@divineastro.org"})
    block = admin_client.post(f"/api/admin/users/{uid}/block", json={"blocked": True, "reason": "test"})
    check("admin can block a password-account user", block.status_code == 200,
          f"{block.status_code} {block.text[:200]}")
    blocked_login = TestClient(app).post(
        "/api/auth/login", json={"username": blocked_username, "password": "correcthorse123"})
    check("the blocked account is refused at login", blocked_login.status_code == 403,
          f"{blocked_login.status_code} {blocked_login.text[:200]}")

    print("\n7. Repeated failed logins against one username are rate-limited")
    rl_username = rand_username("rl")
    rl_client = TestClient(app)
    statuses = []
    for _ in range(6):
        r = rl_client.post("/api/auth/login", json={"username": rl_username, "password": "wrong"})
        statuses.append(r.status_code)
    check("the first several failures are ordinary 401s",
          statuses[:5] == [401] * 5, str(statuses))
    check("a later attempt is throttled with 429, not silently allowed to keep guessing",
          429 in statuses, str(statuses))

    print("\n8. Logging in again does not grant a second signup bonus")
    second_login = TestClient(app).post(
        "/api/auth/login", json={"username": username, "password": "correcthorse123"})
    check("credits are unchanged by a second login",
          second_login.json()["user"]["credits"] == 10, str(second_login.json()["user"]))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("password auth: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
