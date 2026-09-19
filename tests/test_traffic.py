"""Traffic analytics: what counts as a visit, how it is classified, what is (and
is not) stored, first-touch sign-up attribution, and the admin endpoint.

Part 1 is pure functions — no server. Part 2 needs the app running:

    ASTRO_GATEWAY=test ASTRO_DEV_LOGIN=1 uvicorn app.main:app --port 8600
    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_traffic
"""

from __future__ import annotations

import datetime as dt
import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import analytics as an  # noqa: E402

BASE = "http://127.0.0.1:8600"
RUN = random.randint(100000, 999999)
failures: list[str] = []

CHROME = (f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          f"(KHTML, like Gecko) Chrome/120.0 Safari/537.36 run{RUN}")
IPHONE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
          f"(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1 run{RUN}")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# --------------------------------------------------------------------------
# Part 1 — pure functions
# --------------------------------------------------------------------------

def part1() -> None:
    print("\n1. Source classification")
    c = an.classify_source
    check("Google (any country domain)", c("https://www.google.co.in/", {}, "divineastro.org")[0] == "google")
    check("Facebook via its link shim", c("https://l.facebook.com/l.php?u=x", {}, "divineastro.org")[0] == "facebook")
    check("t.co is X", c("https://t.co/abc", {}, "divineastro.org")[0] == "x")
    check("Instagram", c("https://l.instagram.com/?u=x", {}, "divineastro.org")[0] == "instagram")
    check("an Android WhatsApp referrer", c("android-app://com.whatsapp/", {}, "divineastro.org")[0] == "whatsapp")
    check("Google's Android search app", c("android-app://com.google.android.googlequicksearchbox", {}, "divineastro.org")[0] == "google")
    check("an unknown site is reported by its host", c("https://blog.example.org/post", {}, "divineastro.org")[0] == "blog.example.org")
    check("no referrer is direct", c("", {}, "divineastro.org")[0] == "direct")
    check("our own site is internal, not a source", c("https://divineastro.org/feedback", {}, "divineastro.org")[0] == "internal")
    check("www. of our own site is internal too", c("https://www.divineastro.org/", {}, "divineastro.org")[0] == "internal")
    check("the Google sign-in round trip is internal, not 'google'",
          c("https://accounts.google.com/o/oauth2/auth", {}, "divineastro.org")[0] == "internal")
    src, med, camp = c("https://www.google.com/", {"utm_source": "Newsletter", "utm_medium": "Email",
                                                  "utm_campaign": "Diwali 25"}, "divineastro.org")
    check("an explicit utm_source beats the referrer, and labels are cleaned",
          (src, med, camp) == ("newsletter", "email", "diwali25"), str((src, med, camp)))
    check("?ref= is accepted as a source tag", c("", {"ref": "poster"}, "x.org")[0] == "poster")
    check("hostile input is reduced to safe characters",
          an.clean("<script>alert(1)</script>") == "scriptalert1script" and "<" not in an.clean("<b>"))
    check("a label is length-capped", len(an.clean("a" * 500)) == 60)

    print("\n2. Devices and bots")
    check("iPhone -> mobile", an.device_class(IPHONE) == "mobile")
    check("iPad -> tablet", an.device_class("Mozilla/5.0 (iPad; CPU OS 17_0)") == "tablet")
    check("Android phone -> mobile", an.device_class("Mozilla/5.0 (Linux; Android 13; Pixel 7) Mobile Safari") == "mobile")
    check("Android without 'Mobile' -> tablet", an.device_class("Mozilla/5.0 (Linux; Android 13; SM-X700) Safari") == "tablet")
    check("Windows Chrome -> desktop", an.device_class(CHROME) == "desktop")
    for ua in ("Googlebot/2.1", "curl/8.4.0", "python-requests/2.31", "WhatsApp/2.23.20 A",
               "facebookexternalhit/1.1", "Mozilla/5.0 HeadlessChrome/120", "Slackbot-LinkExpanding", ""):
        check(f"a bot / preview fetcher is recognised: {ua[:34] or '(empty UA)'!r}", an.is_bot(ua))
    check("a real desktop browser is not a bot", not an.is_bot(CHROME))
    check("a real phone browser is not a bot", not an.is_bot(IPHONE))

    print("\n3. The visitor hash is anonymous and day-scoped")
    now = dt.datetime(2026, 9, 20, 12, 0, tzinfo=dt.timezone.utc)
    h = an.visitor_hash("203.0.113.9", CHROME, now)
    check("16 hex characters", len(h) == 16 and all(ch in "0123456789abcdef" for ch in h), h)
    check("the same person on the same day is recognised", h == an.visitor_hash("203.0.113.9", CHROME, now))
    check("a different browser is a different visitor", h != an.visitor_hash("203.0.113.9", IPHONE, now))
    check("a different address is a different visitor", h != an.visitor_hash("203.0.113.10", CHROME, now))
    check("the SAME person on the NEXT day is unlinkable",
          h != an.visitor_hash("203.0.113.9", CHROME, now + dt.timedelta(days=1)))
    check("the hash contains neither the IP nor the user-agent", "203" not in h and "run" not in h)
    late = dt.datetime(2026, 9, 20, 18, 45, tzinfo=dt.timezone.utc)      # 00:15 IST on the 21st
    check("the day rolls over at IST midnight, not UTC",
          an.visitor_hash("1.1.1.1", CHROME, late) != an.visitor_hash("1.1.1.1", CHROME, now))


    print("\n3b. The sign-up rate only compares days that tracking covered")
    days = [{"date": f"2026-09-{d:02d}", "visitors": 0, "pageviews": 0, "new_users": 5} for d in range(1, 7)]
    days += [{"date": f"2026-09-{d:02d}", "visitors": 10, "pageviews": 15, "new_users": 1} for d in range(7, 11)]
    check("new users from before tracking are left out (4 ÷ 40, not 34 ÷ 40)",
          an.signup_rate(days, "2026-09-07") == 0.1, str(an.signup_rate(days, "2026-09-07")))
    check("the ratio that would have been shown without the fix is wildly wrong (0.85 = 85%)",
          round(sum(d["new_users"] for d in days) / sum(d["visitors"] for d in days), 2) == 0.85)
    check("no tracking yet -> no rate", an.signup_rate(days, None) is None)
    check("tracked days but no visitors -> no rate, not a divide-by-zero",
          an.signup_rate([{"date": "2026-09-10", "visitors": 0, "pageviews": 0, "new_users": 2}], "2026-09-10") is None)
    check("full coverage behaves as a plain ratio", an.signup_rate(days, "2026-09-01") == round(34 / 40, 4))


    print("\n3c. The production case: many older users, tracking started today")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.db import Base, User, Visit
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    now_ = an.utcnow()
    with Session(eng) as db:
        for i in range(46):                                    # signed up over the past 25 days
            db.add(User(email=f"old{i}@example.com", provider="google", provider_sub=f"g{i}",
                        created_at=now_ - dt.timedelta(days=1 + i % 25)))
        for i in range(3):                                     # tracking began today
            db.add(Visit(ts=now_, path="/", source="google", device="mobile", visitor=f"v{i:015d}"))
        db.commit()
        s0 = an.summary(db, 30)
        check("the 46 older sign-ups are still counted as new users in the window",
              s0["windows"]["d30"]["new_users"] == 46, str(s0["windows"]["d30"]["new_users"]))
        check("but the sign-up rate is NOT 46 ÷ 3 = 1533% — no tracked-day sign-ups, so 0%",
              s0["windows"]["d30"]["signup_rate"] == 0 and s0["totals"]["signup_rate"] == 0,
              str((s0["windows"]["d30"]["signup_rate"], s0["totals"]["signup_rate"])))
        db.add(User(email="today@example.com", provider="google", provider_sub="gt", created_at=now_))
        db.commit()
        s1 = an.summary(db, 30)
        check("one sign-up on a tracked day out of 3 visitors -> 33.3%",
              abs(s1["windows"]["d30"]["signup_rate"] - 1 / 3) < 1e-3, str(s1["windows"]["d30"]["signup_rate"]))
        check("and the rate can never exceed 100% just because history is longer",
              all((w["signup_rate"] or 0) <= 1 for w in s1["windows"].values()))
    eng.dispose()


# --------------------------------------------------------------------------
# Part 2 — the running app
# --------------------------------------------------------------------------

def visits_now() -> list:
    from sqlalchemy import select

    from app.db import Visit, session

    with session() as db:
        return db.execute(select(Visit).order_by(Visit.id)).scalars().all()


def count_visits() -> int:
    return len(visits_now())


def get(path: str, ua: str = CHROME, headers: dict | None = None,
        session_: requests.Session | None = None):
    s = session_ or requests.Session()
    return s.get(f"{BASE}{path}", headers={"User-Agent": ua, **(headers or {})},
                 timeout=30, allow_redirects=False)


def sign_in(email: str, session_: requests.Session | None = None) -> requests.Session:
    s = session_ or requests.Session()
    s.post(f"{BASE}/api/auth/dev", json={"email": email, "name": email.split("@")[0]},
           timeout=30).raise_for_status()
    return s


def make_admin(email: str) -> None:
    from sqlalchemy import select

    from app.db import User, session

    with session() as db:
        u = db.execute(select(User).where(User.email == email)).scalar_one()
        u.is_admin = True
        db.commit()


def user_row(email: str):
    from sqlalchemy import select

    from app.db import User, session

    with session() as db:
        return db.execute(select(User).where(User.email == email)).scalar_one()


def part2() -> None:
    print("\n4. What counts as a visit")
    before = count_visits()
    r = get("/", headers={"Referer": "https://www.google.com/search?q=kundali"})
    check("the home page loads", r.status_code == 200, str(r.status_code))
    rows = visits_now()
    check("one visit was recorded", len(rows) == before + 1, f"{before} -> {len(rows)}")
    v = rows[-1]
    check("with the page, classified source and device",
          (v.path, v.source, v.device) == ("/", "google", "desktop"), str((v.path, v.source, v.device)))
    check("and an anonymous visitor hash", len(v.visitor) == 16)
    stored = " ".join(str(x) for x in (v.path, v.source, v.medium, v.campaign, v.device, v.visitor))
    check("NO IP address and NO browser string reached the database",
          "127.0.0.1" not in stored and "Mozilla" not in stored and f"run{RUN}" not in stored, stored)

    n = count_visits()
    for label, kwargs in [
        ("a bot", dict(ua="Googlebot/2.1 (+http://www.google.com/bot.html)")),
        ("a WhatsApp link-preview fetch", dict(ua="WhatsApp/2.23.20.0 A")),
        ("Do-Not-Track", dict(headers={"DNT": "1"})),
        ("Global-Privacy-Control", dict(headers={"Sec-GPC": "1"})),
        ("a browser prefetch", dict(headers={"Sec-Purpose": "prefetch"})),
        ("no user-agent at all", dict(ua="")),
    ]:
        get("/", **kwargs)
        check(f"{label} is not counted", count_visits() == n, f"{n} -> {count_visits()}")
    for path in ("/api/health", "/static/app.js", "/admin", "/?welcome=1"):
        get(path)
        check(f"{path} is not counted", count_visits() == n, f"{n} -> {count_visits()}")

    print("\n5. Public pages, paths, UTM tags")
    get("/feedback")
    get("/privacy", headers={"Referer": "https://divineastro.org/"})
    paths = [x.path for x in visits_now()[-2:]]
    check("other public pages are counted with their own path",
          paths == ["/feedback", "/privacy"], str(paths))
    check("(a trailing-slash URL is redirected by the router, so it is not a page load)",
          get("/privacy/").status_code in (301, 307, 308))
    get(f"/?utm_source=WhatsApp&utm_medium=Social&utm_campaign=diwali{RUN}", ua=IPHONE)
    v = visits_now()[-1]
    check("utm_source / medium / campaign are recorded, cleaned, and win",
          (v.source, v.medium, v.campaign, v.device) == ("whatsapp", "social", f"diwali{RUN}", "mobile"),
          str((v.source, v.medium, v.campaign, v.device)))
    internal = [x for x in visits_now() if x.path == "/privacy"][-1]
    check("a page-to-page move is recorded as internal, not as a source", internal.source == "internal", internal.source)

    print("\n6. The administrator's own visits do not count")
    admin_email = f"tadmin{RUN}@example.com"
    a = sign_in(admin_email)
    make_admin(admin_email)
    a = sign_in(admin_email)
    n = count_visits()
    get("/", session_=a)
    check("a signed-in admin loading the site adds nothing", count_visits() == n, f"{n} -> {count_visits()}")
    get("/", ua=CHROME + " other")
    check("but an ordinary visitor still does", count_visits() == n + 1)

    print("\n7. The first-touch cookie")
    s = requests.Session()
    r = get("/?utm_source=instagram&utm_campaign=reel1", ua=CHROME + " insta", session_=s)
    set_cookie = r.headers.get("set-cookie", "")
    check("the first visit sets the source cookie (source|campaign)",
          "astro_src=instagram|reel1" in set_cookie.replace('"', ''), set_cookie[:120])
    check("it is HttpOnly and SameSite=Lax", "httponly" in set_cookie.lower() and "samesite=lax" in set_cookie.lower())
    r = get("/?utm_source=facebook", ua=CHROME + " insta", session_=s)
    check("a later visit does NOT overwrite it (first touch wins)", "astro_src" not in r.headers.get("set-cookie", ""))
    r2 = get("/", session_=requests.Session(), headers={"Referer": "https://divineastro.org/x"})
    check("an internal referrer never seeds the cookie", "astro_src" not in r2.headers.get("set-cookie", ""))

    print("\n8. Sign-up attribution")
    email = f"attr{RUN}@example.com"
    sign_in(email, s)                                      # same jar => carries the cookie
    u = user_row(email)
    check("a new user is stamped with the visitor's first source and campaign",
          (u.signup_source, u.signup_campaign) == ("instagram", "reel1"), str((u.signup_source, u.signup_campaign)))
    email2 = f"nocookie{RUN}@example.com"
    sign_in(email2)
    check("a sign-up with no cookie is 'unknown', not guessed", user_row(email2).signup_source == "unknown")
    sign_in(email, s)
    check("signing in again does not restamp the source", user_row(email).signup_source == "instagram")

    print("\n9. The admin endpoint")
    plain = sign_in(f"tplain{RUN}@example.com")
    check("anonymous -> 401", requests.get(f"{BASE}/api/admin/traffic", timeout=20).status_code == 401)
    check("a normal user -> 403", plain.get(f"{BASE}/api/admin/traffic", timeout=20).status_code == 403)
    t0 = a.get(f"{BASE}/api/admin/traffic?days=30", timeout=30).json()
    keys = {"range", "windows", "totals", "live_now", "daily", "sources", "signup_sources",
            "providers", "devices", "pages", "campaigns", "tracking_since", "users_total"}
    check("the response carries every section", keys <= set(t0), str(keys - set(t0)))
    check("30 days -> 30 daily points, oldest first", len(t0["daily"]) == 30
          and t0["daily"][0]["date"] < t0["daily"][-1]["date"])
    check("days=0 is clamped to 1, days=999 to 180",
          len(a.get(f"{BASE}/api/admin/traffic?days=0", timeout=30).json()["daily"]) == 1
          and len(a.get(f"{BASE}/api/admin/traffic?days=999", timeout=30).json()["daily"]) == 180)
    today = t0["daily"][-1]
    check("today's page views include what this test just generated", today["pageviews"] >= 8, str(today))
    check("visitors are unique people, not page views", today["visitors"] < today["pageviews"], str(today))

    from app.analytics import summary
    from app.db import session
    with session() as db:
        srcs = {x["label"]: x["count"] for x in summary(db, 30)["sources"]}
    check("the sources table shows where visitors came from",
          srcs.get("google", 0) >= 1 and srcs.get("whatsapp", 0) >= 1 and srcs.get("instagram", 0) >= 1, str(srcs))
    check("'internal' page-to-page moves are not a source", "internal" not in srcs)
    check("new users by source include the attributed sign-up",
          any(x["label"] == "instagram" and x["count"] >= 1 for x in t0["signup_sources"]), str(t0["signup_sources"]))
    check("a page-level table is present, with the home page on top or near it",
          any(p["label"] == "/" for p in t0["pages"]), str(t0["pages"][:3]))
    check("the sign-up rate is new users / visitors",
          t0["windows"]["d30"]["signup_rate"] is None
          or abs(t0["windows"]["d30"]["signup_rate"]
                 - t0["windows"]["d30"]["new_users"] / t0["windows"]["d30"]["visitors"]) < 1e-3)

    print("\n10. Manual customers are not counted as site sign-ups")
    with session() as db:
        before_new = summary(db, 30)["windows"]["today"]["new_users"]
    r = a.post(f"{BASE}/api/admin/orders/manual",
               json={"email": f"walkin{RUN}@example.com", "sku": "q10", "method": "cash"}, timeout=30)
    check("an admin records a walk-in customer", r.status_code == 200, r.text[:100])
    check("stamped 'manual'", user_row(f"walkin{RUN}@example.com").signup_source == "manual")
    with session() as db:
        after_new = summary(db, 30)["windows"]["today"]["new_users"]
    check("and it does NOT raise 'new users'", after_new == before_new, f"{before_new} -> {after_new}")

    print("\n11. Retention")
    from app.db import Visit
    with session() as db:
        old = Visit(ts=an.utcnow() - dt.timedelta(days=an.RETENTION_DAYS + 30), path="/old", source="direct")
        fresh = Visit(ts=an.utcnow(), path="/fresh-keep", source="direct")
        db.add_all([old, fresh])
        db.commit()
        gone = an.purge_old(db)
        left = {v.path for v in db.query(Visit).filter(Visit.path.in_(["/old", "/fresh-keep"]))}
    check("visits past the retention window are deleted, recent ones kept",
          gone >= 1 and "/old" not in left and "/fresh-keep" in left, f"deleted {gone}, left {left}")


def main() -> int:
    part1()
    try:
        requests.get(f"{BASE}/api/health", timeout=5).raise_for_status()
    except Exception:
        print("\n(server not reachable — part 2 skipped; start it to run the integration checks)")
        return 1 if failures else 0
    part2()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("traffic: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
