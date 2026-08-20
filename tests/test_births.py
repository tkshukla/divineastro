"""Saved birth charts.

Two properties matter. **The cap is the server's**, not the browser's — a
customer with curl must be held to the same five as everyone else. And a saved
chart is birth data: it belongs to exactly one account and nobody else may
read, rename or delete it.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_births
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
MAX = 5
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def sign_in() -> requests.Session:
    s = requests.Session()
    email = f"birth{random.randint(10000, 99999)}@example.com"
    s.post(f"{BASE}/api/auth/dev", json={"email": email}, timeout=30).raise_for_status()
    return s


def birth(n: int) -> dict:
    """A distinct chart per n — same city, a birth year apart."""
    return {
        "name": f"Chart {n}", "date": f"199{n}-03-11", "time": "07:45",
        "place": "Sultanpur", "latitude": 26.2647, "longitude": 82.0730,
        "timezone": "Asia/Kolkata", "zodiac": "sidereal", "ayanamsa": "lahiri",
        "house_system": "Whole Sign", "time_known": True,
    }


def saved(s: requests.Session) -> list[dict]:
    return s.get(f"{BASE}/api/births", timeout=20).json()["births"]


def main() -> int:
    print("\n1. A signed-out caller gets nothing")
    anon = requests.Session()
    r = anon.get(f"{BASE}/api/births", timeout=20)
    check("anonymous cannot list", r.status_code == 401, str(r.status_code))
    r = anon.post(f"{BASE}/api/births", json=birth(0), timeout=20)
    check("anonymous cannot save", r.status_code == 401, str(r.status_code))
    r = anon.delete(f"{BASE}/api/births/1", timeout=20)
    check("anonymous cannot delete", r.status_code == 401, str(r.status_code))

    print("\n2. Five charts save; the sixth is refused")
    alice = sign_in()
    check("a new account starts empty", saved(alice) == [], str(len(saved(alice))))
    ids = []
    for n in range(MAX):
        r = alice.post(f"{BASE}/api/births", json=birth(n), timeout=20)
        check(f"chart {n + 1} saved", r.status_code == 200, r.text[:120])
        if r.status_code == 200:
            ids.append(r.json()["birth"]["id"])
    listing = alice.get(f"{BASE}/api/births", timeout=20).json()
    check(f"{MAX} charts listed", len(listing["births"]) == MAX, str(len(listing["births"])))
    check("the cap is advertised", listing.get("max") == MAX, str(listing.get("max")))

    sixth = alice.post(f"{BASE}/api/births", json=birth(MAX), timeout=20)
    check("the sixth is refused with 409", sixth.status_code == 409, str(sixth.status_code))
    check("the refusal says what to do", "delete" in sixth.text.lower(), sixth.text[:120])
    check("nothing was written", len(saved(alice)) == MAX, str(len(saved(alice))))

    print("\n3. Casting the same chart twice does not duplicate it")
    cast = alice.post(f"{BASE}/api/chart", json=birth(0), timeout=60)
    check("the chart still casts", cast.status_code == 200, str(cast.status_code))
    again = alice.post(f"{BASE}/api/births", json=birth(0), timeout=20)
    check("re-saving succeeds even at the cap", again.status_code == 200, again.text[:120])
    check("it is the same row", again.json()["birth"]["id"] == ids[0],
          f"{again.json()['birth']['id']} vs {ids[0]}")
    check("no second row appeared", len(saved(alice)) == MAX, str(len(saved(alice))))

    print("\n4. Renaming keeps the chart, changes the label")
    named = alice.patch(f"{BASE}/api/births/{ids[0]}",
                        json={"label": "Papa's kundali"}, timeout=20)
    check("rename accepted", named.status_code == 200, named.text[:120])
    check("the new label sticks",
          any(b["id"] == ids[0] and b["label"] == "Papa's kundali" for b in saved(alice)))
    blank = alice.patch(f"{BASE}/api/births/{ids[0]}", json={"label": "  "}, timeout=20)
    check("a blank label is refused", blank.status_code == 400, str(blank.status_code))

    print("\n5. Deleting one frees a slot")
    doomed = ids[-1]
    gone = alice.delete(f"{BASE}/api/births/{doomed}", timeout=20)
    check("delete accepted", gone.status_code == 200, str(gone.status_code))
    check(f"{MAX - 1} charts left", len(saved(alice)) == MAX - 1, str(len(saved(alice))))
    # Checked before the next save: SQLite hands the freed rowid straight back.
    check("deleting the same row twice is a 404",
          alice.delete(f"{BASE}/api/births/{doomed}", timeout=20).status_code == 404)
    fresh = alice.post(f"{BASE}/api/births", json=birth(MAX), timeout=20)
    check("a new chart now saves", fresh.status_code == 200, fresh.text[:120])
    check("back at the cap", len(saved(alice)) == MAX, str(len(saved(alice))))

    print("\n6. Charts belong to one account only")
    hers = {b["id"] for b in saved(alice)}
    victim = min(hers)
    bob = sign_in()
    check("Bob's shelf is his own", saved(bob) == [], str(len(saved(bob))))
    bob.post(f"{BASE}/api/births", json=birth(9), timeout=20)
    check("Bob sees only his chart", len(saved(bob)) == 1, str(len(saved(bob))))
    check("Alice's ids are not in Bob's list", not {b["id"] for b in saved(bob)} & hers)
    check("Bob cannot delete Alice's chart",
          bob.delete(f"{BASE}/api/births/{victim}", timeout=20).status_code == 404)
    check("Bob cannot rename Alice's chart",
          bob.patch(f"{BASE}/api/births/{victim}",
                    json={"label": "mine now"}, timeout=20).status_code == 404)
    check("Alice's charts survived", len(saved(alice)) == MAX, str(len(saved(alice))))
    check("Alice's label is untouched",
          any(b["id"] == victim and b["label"] != "mine now" for b in saved(alice)))
    check("Bob's own cap is separate", len(saved(bob)) == 1, str(len(saved(bob))))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("saved birth charts: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
