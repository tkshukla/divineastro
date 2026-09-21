"""Kundali Matchmaking, end to end through the real HTTP endpoint.

Why this exists: /api/match returned 500 for EVERY request from 29 Aug (a table
reshaped in a "Hindi localization" commit broke the Yoni lookup) and nothing
noticed — the unit suite exercises matching.py directly, and it crashed on its
own table access before reaching any scoring check, so it never got as far as
proving the endpoint worked. This calls the endpoint the way the browser does.

No server needed (FastAPI's in-process client):

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_match_api
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

failures: list[str] = []
client = TestClient(app, raise_server_exceptions=False)   # a 500 must come back as a 500, not raise

BLR = {"place": "Bengaluru, Karnataka, India", "latitude": 12.97194, "longitude": 77.59369,
       "timezone": "Asia/Kolkata"}
DEL = {"place": "Delhi, India", "latitude": 28.6519, "longitude": 77.2315, "timezone": "Asia/Kolkata"}
DEVANAGARI = re.compile(r"[\u0900-\u097F]")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def person(date: str, time: str = "12:00", known: bool = True, **place) -> dict:
    return {"name": "T", "date": date, "time": time, "time_known": known, **(place or BLR)}


def post(groom: dict, bride: dict, lang: str = "en"):
    return client.post("/api/match", json={"groom": groom, "bride": bride, "lang": lang})


def main() -> int:
    print("\n1. An ordinary request works (this returned 500 for every user)")
    r = post(person("1975-09-19", "06:43"), person("1980-03-12", "14:20", **DEL))
    check("HTTP 200", r.status_code == 200, f"{r.status_code} {r.text[:80]}")
    d = r.json() if r.status_code == 200 else {}
    ak = d.get("ashtakoot", {})
    check("a total inside 0..36", 0 <= ak.get("total", -1) <= 36, str(ak.get("total")))
    check("all eight kootas present", len(ak.get("kootas", [])) == 8, str(len(ak.get("kootas", []))))
    check("each koota has a label and a score within its maximum",
          all(k["label"] and 0 <= k["score"] <= k["max"] for k in ak.get("kootas", [])))
    yoni = next((k for k in ak.get("kootas", []) if "yoni" in k["label"].lower()), None)
    check("Yoni — the koota that crashed — is present and scored", yoni is not None and 0 <= yoni["score"] <= 4,
          str(yoni and (yoni["label"], yoni["score"])))
    check("the Mangal Dosha section is present", "mangal" in d or "mangal_dosha" in d, str([k for k in d][:8]))

    print("\n2. Hindi")
    h = post(person("1975-09-19", "06:43"), person("1980-03-12", "14:20", **DEL), lang="hi")
    check("HTTP 200 in Hindi", h.status_code == 200, f"{h.status_code} {h.text[:80]}")
    hd = h.json() if h.status_code == 200 else {}
    check("the score is the same as in English (language must not change the maths)",
          hd.get("ashtakoot", {}).get("total") == ak.get("total"))
    check("koota names come back in Devanagari",
          bool(hd) and all(DEVANAGARI.search(k["label"]) for k in hd["ashtakoot"]["kootas"]))

    print("\n3. Awkward but valid inputs")
    r = post(person("1990-01-01", known=False), person("1992-06-30", known=False))
    check("unknown birth times still work, with the caveat", r.status_code == 200 and bool(r.json().get("caveat")),
          f"{r.status_code}")
    a, b = person("1975-09-19", "06:43"), person("1980-03-12", "14:20", **DEL)
    check("groom and bride can be swapped", post(b, a).status_code == 200)
    check("the same person on both sides", post(a, a).status_code == 200)

    print("\n4. Bad input is a clean 400 with a readable message, never a 500")
    r = post(person("not-a-date"), b)
    check("an invalid date -> 400", r.status_code == 400, f"{r.status_code} {r.text[:80]}")
    check("the 400 body is JSON with a 'detail'", r.headers.get("content-type", "").startswith("application/json")
          and "detail" in r.json())
    check("a missing side -> 422 validation, not 500",
          client.post("/api/match", json={"groom": a}).status_code == 422)

    print("\n5. No pair of charts may 500 (150 random couples, all 12 signs and 27 nakshatras get exercised)")
    rng = random.Random(20260920)
    bad = []
    for i in range(150):
        def rp():
            y, mo, dd = rng.randint(1940, 2015), rng.randint(1, 12), rng.randint(1, 28)
            return person(f"{y:04d}-{mo:02d}-{dd:02d}", f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}",
                          **rng.choice([BLR, DEL]))
        g, br = rp(), rp()
        resp = post(g, br, lang=rng.choice(["en", "hi"]))
        if resp.status_code != 200:
            bad.append(f"{g['date']} x {br['date']} -> {resp.status_code}")
    check("every one returns 200", not bad, "; ".join(bad[:4]))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("match api: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
