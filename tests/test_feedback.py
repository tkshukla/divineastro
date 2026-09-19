"""User feedback: the submit API and the admin inbox.

The properties that matter: only a signed-in user can send it, junk is refused,
a double-click cannot file it twice, one user cannot flood the inbox, the
operator's private note never reaches the user, and only an admin can read or
triage the inbox.

    ASTRO_GATEWAY=test ASTRO_DEV_LOGIN=1 uvicorn app.main:app --port 8600
    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_feedback
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
RUN = random.randint(100000, 999999)
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def sign_in(email: str) -> requests.Session:
    s = requests.Session()
    s.post(f"{BASE}/api/auth/dev", json={"email": email, "name": email.split("@")[0]},
           timeout=30).raise_for_status()
    return s


def make_admin(email: str) -> None:
    from sqlalchemy import select

    from app.db import User, session as db_session

    with db_session() as db:
        u = db.execute(select(User).where(User.email == email)).scalar_one()
        u.is_admin = True
        db.commit()


def send(s: requests.Session, **kw) -> requests.Response:
    body = {"category": "bug", "rating": 4,
            "message": f"The chat froze after my second question ({RUN})", **kw}
    return s.post(f"{BASE}/api/feedback", json=body, timeout=20)


def main() -> int:
    admin_email = f"fbadmin{RUN}@example.com"
    make_admin_first = sign_in(admin_email)
    make_admin(admin_email)
    admin = sign_in(admin_email)                       # refresh the admin flag
    user_email = f"fbuser{RUN}@example.com"
    user = sign_in(user_email)

    print("\n1. Only a signed-in user can send or read feedback")
    anon = requests.Session()
    check("anonymous POST /feedback -> 401",
          anon.post(f"{BASE}/api/feedback", json={"message": "x" * 20}, timeout=20)
          .status_code == 401)
    check("anonymous GET /feedback/mine -> 401",
          anon.get(f"{BASE}/api/feedback/mine", timeout=20).status_code == 401)
    check("the /feedback page itself is public (it prompts for sign-in)",
          anon.get(f"{BASE}/feedback", timeout=20).status_code == 200)

    print("\n2. Junk is refused")
    check("too short -> 400", send(user, message="short").status_code == 400)
    check("unknown category -> 400", send(user, category="spam").status_code == 400)
    check("rating 0 -> 400", send(user, rating=0).status_code == 400)
    check("rating 6 -> 400", send(user, rating=6).status_code == 400)
    check("over-long message -> 400", send(user, message="x" * 2001).status_code == 400)
    check("nothing was stored by the refused attempts",
          user.get(f"{BASE}/api/feedback/mine", timeout=20).json()["feedback"] == [])

    print("\n3. A good submission, and a double-click")
    r = send(user)
    check("accepted", r.status_code == 200 and r.json()["ok"] is True, r.text[:100])
    fid = r.json()["id"]
    again = send(user)
    check("the identical message again is recognised, not filed twice",
          again.status_code == 200 and again.json().get("duplicate") is True
          and again.json()["id"] == fid, again.text[:100])
    mine = user.get(f"{BASE}/api/feedback/mine", timeout=20).json()["feedback"]
    check("exactly one is on record", len(mine) == 1, str(len(mine)))
    check("optional rating and contact choice are accepted",
          send(user, category="idea", rating=None, allow_contact=False,
               message=f"Please add a dark mode for the chart ({RUN})").status_code == 200)

    print("\n4. One user cannot flood the inbox")
    flood = sign_in(f"fbflood{RUN}@example.com")
    codes = [send(flood, message=f"Distinct message number {i} for the rate limit {RUN}").status_code
             for i in range(7)]
    check("five go through, the rest are refused with 429",
          codes[:5] == [200] * 5 and codes[5:] == [429, 429], str(codes))

    print("\n5. The admin inbox")
    check("a non-admin cannot list it (403)",
          user.get(f"{BASE}/api/admin/feedback", timeout=20).status_code == 403)
    check("a non-admin cannot triage it (403)",
          user.patch(f"{BASE}/api/admin/feedback/{fid}", json={"status": "read"},
                     timeout=20).status_code == 403)
    inbox = admin.get(f"{BASE}/api/admin/feedback", timeout=20).json()
    item = next((i for i in inbox["items"] if i["id"] == fid), None)
    check("the feedback is in the inbox with who sent it",
          item is not None and item["email"] == user_email and item["category"] == "bug"
          and item["rating"] == 4 and item["status"] == "new", str(item)[:160])
    check("counts are reported per status",
          inbox["counts"]["new"] >= 1 and inbox["counts"]["all"] >= inbox["counts"]["new"],
          str(inbox["counts"]))
    only_new = admin.get(f"{BASE}/api/admin/feedback?status=new", timeout=20).json()
    check("status filter returns only that status",
          all(i["status"] == "new" for i in only_new["items"]) and len(only_new["items"]) >= 1)
    found = admin.get(f"{BASE}/api/admin/feedback?q={user_email}", timeout=20).json()["items"]
    check("search by the sender's email finds it",
          any(i["id"] == fid for i in found) and all(i["email"] == user_email for i in found))

    print("\n6. Triage, and the private note stays private")
    r = admin.patch(f"{BASE}/api/admin/feedback/{fid}",
                    json={"status": "read", "admin_note": "Reproduced; fixing."}, timeout=20)
    check("mark read + note", r.status_code == 200 and r.json()["item"]["status"] == "read"
          and r.json()["item"]["admin_note"] == "Reproduced; fixing.", r.text[:140])
    r = admin.patch(f"{BASE}/api/admin/feedback/{fid}", json={"status": "resolved"}, timeout=20)
    check("resolve stamps the handling time", r.json()["item"]["handled_at"] != "", r.text[:140])
    r = admin.patch(f"{BASE}/api/admin/feedback/{fid}", json={"status": "new"}, timeout=20)
    check("reopening clears the handling time", r.json()["item"]["handled_at"] == "")
    admin.patch(f"{BASE}/api/admin/feedback/{fid}", json={"status": "resolved"}, timeout=20)
    check("an invalid status -> 400",
          admin.patch(f"{BASE}/api/admin/feedback/{fid}", json={"status": "banana"},
                      timeout=20).status_code == 400)
    check("an unknown id -> 404",
          admin.patch(f"{BASE}/api/admin/feedback/99999999", json={"status": "read"},
                      timeout=20).status_code == 404)
    mine = user.get(f"{BASE}/api/feedback/mine", timeout=20).json()["feedback"]
    seen = next(f for f in mine if f["id"] == fid)
    check("the user sees the status", seen["status"] == "resolved", str(seen))
    check("the user NEVER sees the operator's private note",
          "admin_note" not in seen and "Reproduced" not in str(mine))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("feedback: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
