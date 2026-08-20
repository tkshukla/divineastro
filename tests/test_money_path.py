"""End-to-end test of the paid path.

register -> 10 free questions -> paywall at zero -> buy a pack -> ask again.
Also asserts the two properties that protect real money:

  * a failed answer must not consume a credit
  * confirming the same payment twice must not grant credits twice

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_money_path
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
# A fresh identity each run so repeated runs don't collide on the same account.
EMAIL = f"tester{random.randint(10000, 99999)}@example.com"

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not condition:
        failures.append(f"{label} {detail}")


def main() -> int:
    s = requests.Session()

    print("\n1. Sign-in (social)")
    provs = s.get(f"{BASE}/api/auth/providers").json()
    print(f"     OAuth providers configured: {[p['key'] for p in provs['providers']] or 'none yet'}")
    check("dev login available for testing", provs.get("dev_login") is True)

    signed = s.post(f"{BASE}/api/auth/dev", json={"email": EMAIL, "name": "Test User"})
    check("sign-in succeeded", signed.status_code == 200, signed.text[:140])
    user = signed.json()["user"]
    start_credits = user["credits"]
    print(f"     credits after signup: {start_credits}")
    check("signup grants free questions", start_credits == 10, str(start_credits))

    print("\n2. Session persists")
    me = s.get(f"{BASE}/api/me").json()["user"]
    check("cookie authenticates", bool(me) and me["email"] == EMAIL)

    print("\n2b. Signing in again returns the same account")
    again = s.post(f"{BASE}/api/auth/dev", json={"email": EMAIL}).json()
    check("no duplicate account", again["created"] is False)
    check("credits not re-granted", again["user"]["credits"] == start_credits,
          str(again["user"]["credits"]))

    print("\n3. Cast a chart")
    chart = s.post(f"{BASE}/api/chart", json={
        "name": "Test", "date": "1986-08-19", "time": "11:59", "place": "Sultanpur",
        "latitude": 26.2647, "longitude": 82.0730, "timezone": "Asia/Kolkata",
        "zodiac": "sidereal", "ayanamsa": "lahiri", "house_system": "Whole Sign",
    })
    check("chart built", chart.status_code == 200, chart.text[:120])
    sid = chart.json()["session_id"]

    print("\n4. Spend all ten free questions")
    left = None
    for i in range(10):
        r = s.post(f"{BASE}/api/ask", json={
            "session_id": sid, "question": f"How is my career, take {i}?",
            "language": "en", "provider": "off"})
        if r.status_code != 200:
            check(f"question {i+1}", False, f"HTTP {r.status_code} {r.text[:80]}")
            break
        left = r.json().get("credits")
        if i in (0, 9):
            print(f"     after Q{i+1}: {left} credits left")
    check("all ten answered, balance zero", left == 0, str(left))

    print("\n5. Paywall")
    blocked = s.post(f"{BASE}/api/ask", json={
        "session_id": sid, "question": "One more?", "provider": "off"})
    check("11th question blocked with 402", blocked.status_code == 402, str(blocked.status_code))
    detail = blocked.json().get("detail", {})
    check("paywall payload names the reason", detail.get("error") == "no_credits", str(detail))

    print("\n6. Buy a pack (test mode)")
    order = s.post(f"{BASE}/api/orders", json={"sku": "q50"})
    check("order created", order.status_code == 200, order.text[:120])
    oid = order.json()["order"]["id"]

    confirm = s.post(f"{BASE}/api/orders/confirm",
                     json={"order_id": oid, "payload": {}}).json()
    check("payment confirmed", confirm.get("ok") is True, str(confirm)[:120])
    check("50 credits granted", confirm.get("credits") == 50, str(confirm.get("credits")))

    print("\n7. Idempotency — replay the same confirmation")
    replay = s.post(f"{BASE}/api/orders/confirm",
                    json={"order_id": oid, "payload": {}}).json()
    check("replay grants nothing", replay.get("granted") is False, str(replay.get("granted")))
    check("balance unchanged after replay", replay.get("credits") == 50,
          str(replay.get("credits")))

    print("\n8. Asking works again")
    again = s.post(f"{BASE}/api/ask", json={
        "session_id": sid, "question": "And now?", "provider": "off"})
    check("question answered after purchase", again.status_code == 200)
    check("balance decremented to 49", again.json().get("credits") == 49,
          str(again.json().get("credits")))

    print("\n9. A failed answer must not charge")
    before = s.get(f"{BASE}/api/me").json()["user"]["credits"]
    dead = s.post(f"{BASE}/api/ask", json={
        "session_id": "does-not-exist", "question": "hello", "provider": "off"})
    after = s.get(f"{BASE}/api/me").json()["user"]["credits"]
    check("bad session rejected", dead.status_code == 404, str(dead.status_code))
    check("no credit consumed on failure", before == after, f"{before} -> {after}")

    print("\n10. History and ledger")
    hist = s.get(f"{BASE}/api/history").json()["questions"]
    check("questions logged", len(hist) == 11, f"{len(hist)} rows")
    check("answers stored", all(q["answer"] for q in hist))
    ledger = s.get(f"{BASE}/api/ledger").json()
    check("ledger balances", ledger["balance"] == after, f"{ledger['balance']} vs {after}")

    print("\n11. Anonymous users are blocked")
    anon = requests.post(f"{BASE}/api/ask", json={
        "session_id": sid, "question": "free?", "provider": "off"})
    check("unauthenticated ask rejected", anon.status_code == 401, str(anon.status_code))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("money path: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
