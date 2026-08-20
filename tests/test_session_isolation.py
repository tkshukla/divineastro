"""Chart sessions must not be readable across accounts.

Birth details are personal data under the DPDP Act, and session ids travel in
URLs and browser history. Possession of an id must never be proof of
entitlement. This pins that down.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_session_isolation
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def sign_in() -> requests.Session:
    s = requests.Session()
    email = f"iso{random.randint(10000, 99999)}@example.com"
    s.post(f"{BASE}/api/auth/dev", json={"email": email}, timeout=30).raise_for_status()
    return s


def cast(s: requests.Session) -> str:
    r = s.post(f"{BASE}/api/chart", json={
        "name": "Test", "date": "1986-08-19", "time": "11:59", "place": "Sultanpur",
        "latitude": 26.2647, "longitude": 82.0730, "timezone": "Asia/Kolkata",
        "zodiac": "sidereal", "ayanamsa": "lahiri", "house_system": "Whole Sign",
    }, timeout=60)
    r.raise_for_status()
    return r.json()["session_id"]


def main() -> int:
    print("\n1. Two separate accounts")
    alice, bob = sign_in(), sign_in()
    alice_sid = cast(alice)
    check("Alice cast a chart", bool(alice_sid))
    check("session id is full entropy (32 hex chars)", len(alice_sid) == 32,
          f"{len(alice_sid)} chars")

    print("\n2. Alice can use her own session")
    for path in (f"/api/transits/{alice_sid}", f"/api/report/{alice_sid}",
                 f"/api/pdf/chart/{alice_sid}"):
        r = alice.get(f"{BASE}{path}", timeout=90)
        check(f"Alice {path.split('/')[2]}", r.status_code == 200, str(r.status_code))

    print("\n3. Bob holds Alice's session id and must get nothing")
    for path in (f"/api/transits/{alice_sid}", f"/api/solar-return/{alice_sid}",
                 f"/api/report/{alice_sid}", f"/api/pdf/chart/{alice_sid}"):
        r = bob.get(f"{BASE}{path}", timeout=90)
        check(f"Bob blocked from {path.split('/')[2]}", r.status_code == 404,
              str(r.status_code))

    r = bob.post(f"{BASE}/api/ask", json={
        "session_id": alice_sid, "question": "What does her chart say?",
        "provider": "off"}, timeout=90)
    check("Bob cannot ask against Alice's chart", r.status_code == 404, str(r.status_code))

    r = bob.delete(f"{BASE}/api/session/{alice_sid}", timeout=30)
    check("Bob cannot delete Alice's session", r.status_code == 404, str(r.status_code))

    print("\n4. Anonymous callers get nothing either")
    for path in (f"/api/transits/{alice_sid}", f"/api/report/{alice_sid}"):
        r = requests.get(f"{BASE}{path}", timeout=30)
        check(f"anonymous blocked from {path.split('/')[2]}",
              r.status_code in (401, 404), str(r.status_code))

    print("\n5. Alice still owns her session after the attempts")
    r = alice.get(f"{BASE}/api/transits/{alice_sid}", timeout=60)
    check("Alice unaffected", r.status_code == 200, str(r.status_code))

    print("\n6. A chart cast before signing in is claimed by the first user")
    anon = requests.Session()
    anon_sid = cast(anon)
    r = anon.post(f"{BASE}/api/auth/dev",
                  json={"email": f"claim{random.randint(10000,99999)}@example.com"},
                  timeout=30)
    check("anonymous visitor signed in", r.status_code == 200)
    r = anon.post(f"{BASE}/api/ask", json={
        "session_id": anon_sid, "question": "How is my career?", "provider": "off"},
        timeout=90)
    check("their pre-login chart still works", r.status_code == 200, str(r.status_code))
    r = bob.get(f"{BASE}/api/transits/{anon_sid}", timeout=60)
    check("but nobody else can reach it now", r.status_code == 404, str(r.status_code))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("session isolation: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
