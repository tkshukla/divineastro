"""End-to-end test of the PDF export.

sign in -> cast a chart -> ask questions -> download both PDFs.
Also asserts the two properties that matter once a file leaves the server:

  * an anonymous caller gets nothing
  * one customer can never pull another customer's answers, even by guessing
    question ids

Start the server first:

    cd C:\\Astro
    $env:ASTRO_SECRET_KEY='dev-secret'; $env:ASTRO_DEV_LOGIN='1'
    C:\\Astro\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8600

then

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_pdf
"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Port 8600 by default, matching the other end-to-end tests. ASTRO_TEST_BASE
# points the run at a server on another port when 8600 is already taken.
BASE = os.environ.get("ASTRO_TEST_BASE", "http://127.0.0.1:8600").rstrip("/")
ALICE = f"alice{random.randint(10000, 99999)}@example.com"
BOB = f"bob{random.randint(10000, 99999)}@example.com"

# A Hindi question, so the export has to shape Devanagari and not print boxes.
HINDI_QUESTION = "\u092e\u0947\u0930\u093e \u0935\u093f\u0935\u093e\u0939 \u0915\u092c \u0939\u094b\u0917\u093e?"

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not condition:
        failures.append(f"{label} {detail}")


def is_pdf(response) -> bool:
    return (response.status_code == 200
            and response.headers.get("content-type", "").startswith("application/pdf")
            and response.content[:5] == b"%PDF-")


def kb(data: bytes) -> str:
    return f"{len(data) / 1024:.0f} KB"


def sign_in(email: str, name: str) -> requests.Session:
    s = requests.Session()
    r = s.post(f"{BASE}/api/auth/dev", json={"email": email, "name": name})
    r.raise_for_status()
    return s


def cast_chart(s: requests.Session) -> str:
    r = s.post(f"{BASE}/api/chart", json={
        "name": "Test Native", "date": "1986-08-19", "time": "11:59",
        "place": "Sultanpur", "latitude": 26.2647, "longitude": 82.0730,
        "timezone": "Asia/Kolkata", "zodiac": "sidereal", "ayanamsa": "lahiri",
        "house_system": "Whole Sign",
    })
    r.raise_for_status()
    return r.json()["session_id"]


def main() -> int:
    print("\n1. Two separate customers sign in")
    alice = sign_in(ALICE, "Alice Sharma")
    bob = sign_in(BOB, "Bob Verma")
    check("both accounts created", True)

    print("\n2. Alice casts a sidereal chart and asks questions")
    sid = cast_chart(alice)
    asked = 0
    for question, language in (("How is my career going to develop?", "en"),
                               ("Will this year be good for money?", "en"),
                               (HINDI_QUESTION, "hi")):
        r = alice.post(f"{BASE}/api/ask", json={
            "session_id": sid, "question": question,
            "language": language, "provider": "off"})
        if r.status_code == 200:
            asked += 1
        else:
            check(f"asking {question[:24]!r}", False, f"HTTP {r.status_code} {r.text[:80]}")
    check("three questions answered and logged", asked == 3, str(asked))

    history = alice.get(f"{BASE}/api/history").json()["questions"]
    alice_ids = [q["id"] for q in history]
    check("history has the three rows", len(alice_ids) == 3, str(len(alice_ids)))
    check("an answer carries markdown", any("**" in q["answer"] or "###" in q["answer"]
                                            for q in history))

    print("\n3. Questions PDF")
    r = alice.get(f"{BASE}/api/pdf/questions")
    check("HTTP 200", r.status_code == 200, r.text[:120] if r.status_code != 200 else "")
    check("content-type is application/pdf",
          r.headers.get("content-type", "").startswith("application/pdf"),
          r.headers.get("content-type", ""))
    check("body starts with %PDF", r.content[:5] == b"%PDF-", repr(r.content[:8]))
    check("offered as a download",
          "attachment" in r.headers.get("content-disposition", ""),
          r.headers.get("content-disposition", ""))
    full = r.content
    check("non-trivial size", len(full) > 8_000, kb(full))
    print(f"     questions PDF: {kb(full)}")

    print("\n4. ?limit= and ?ids= export a subset")
    one = alice.get(f"{BASE}/api/pdf/questions?limit=1")
    check("limit=1 returns a PDF", is_pdf(one), str(one.status_code))
    check("limit=1 is smaller than the full export", len(one.content) < len(full),
          f"{kb(one.content)} vs {kb(full)}")

    subset = alice.get(f"{BASE}/api/pdf/questions?ids={alice_ids[0]},{alice_ids[1]}")
    check("ids= returns a PDF", is_pdf(subset), str(subset.status_code))
    check("ids= subset is smaller than the full export",
          len(subset.content) < len(full), f"{kb(subset.content)} vs {kb(full)}")

    junk = alice.get(f"{BASE}/api/pdf/questions?ids=nonsense")
    check("a malformed ids list is rejected", junk.status_code == 400, str(junk.status_code))

    print("\n5. Chart PDF")
    chart = alice.get(f"{BASE}/api/pdf/chart/{sid}")
    check("HTTP 200", chart.status_code == 200,
          chart.text[:160] if chart.status_code != 200 else "")
    check("content-type is application/pdf",
          chart.headers.get("content-type", "").startswith("application/pdf"),
          chart.headers.get("content-type", ""))
    check("body starts with %PDF", chart.content[:5] == b"%PDF-", repr(chart.content[:8]))
    # The wheel and the two Vedic squares are vector art; a chart report that
    # came out under ~40 KB did not draw them.
    check("chart PDF carries its drawings", len(chart.content) > 40_000, kb(chart.content))
    print(f"     chart PDF: {kb(chart.content)}")

    missing = alice.get(f"{BASE}/api/pdf/chart/does-not-exist")
    check("an unknown chart session 404s", missing.status_code == 404, str(missing.status_code))

    print("\n6. Anonymous callers are blocked")
    for path in ("/api/pdf/questions", f"/api/pdf/chart/{sid}"):
        anon = requests.get(f"{BASE}{path}")
        check(f"anonymous {path} rejected", anon.status_code == 401, str(anon.status_code))

    print("\n7. Bob cannot download Alice's answers")
    bob_sid = cast_chart(bob)
    bob.post(f"{BASE}/api/ask", json={
        "session_id": bob_sid, "question": "What about my health?", "provider": "off"})
    bob_ids = [q["id"] for q in bob.get(f"{BASE}/api/history").json()["questions"]]
    check("Bob has his own single question", len(bob_ids) == 1, str(len(bob_ids)))
    check("the two accounts hold different rows",
          not set(bob_ids) & set(alice_ids), f"{bob_ids} vs {alice_ids}")

    stolen = bob.get(f"{BASE}/api/pdf/questions?ids=" + ",".join(str(i) for i in alice_ids))
    check("asking for only Alice's ids yields nothing, not a PDF",
          stolen.status_code == 404, str(stolen.status_code))

    # Mixing his own id in must not smuggle hers through: the document Bob gets
    # has to be the same one his own id alone produces.
    mixed = bob.get(f"{BASE}/api/pdf/questions?ids="
                    + ",".join(str(i) for i in bob_ids + alice_ids))
    mine = bob.get(f"{BASE}/api/pdf/questions?ids={bob_ids[0]}")
    check("a mixed id list still returns a PDF", is_pdf(mixed), str(mixed.status_code))
    check("Alice's rows are dropped from Bob's export",
          abs(len(mixed.content) - len(mine.content)) < 512,
          f"{kb(mixed.content)} vs {kb(mine.content)}")

    bobs_own = bob.get(f"{BASE}/api/pdf/questions")
    check("Bob's own export is much smaller than Alice's three-question one",
          is_pdf(bobs_own) and len(bobs_own.content) < len(full),
          f"{kb(bobs_own.content)} vs {kb(full)}")

    print("\n8. Devanagari")
    fonts = alice.get(f"{BASE}/api/pdf/fonts")
    check("font diagnostics available", fonts.status_code == 200, str(fonts.status_code))
    info = fonts.json() if fonts.status_code == 200 else {}
    check("a PDF engine is present", info.get("typst_available") is True, str(info))
    print(f"     {info.get('note', '')}")
    check("Devanagari renders (Hindi answers are not boxes)",
          info.get("devanagari_ok") is True,
          "no Devanagari font on this host — Hindi answers would print as tofu")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("pdf export: all green")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.ConnectionError:
        print(f"\nCould not reach {BASE} — start the server first (see the module docstring).")
        raise SystemExit(2) from None
