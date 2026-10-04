"""Traffic analytics: what counts as a visit, how it is classified, what is (and
is not) stored, first-touch sign-up attribution, the funnel, and the admin endpoint.

Since DIVASTRO-99 a visit is recorded by the page's own beacon (POST /api/visit,
sent by static/visit.js), never by the HTML request, so these checks send the
beacon the way a browser would after loading the page.

Part 1 is pure functions — no server. Part 2 needs the app running:

    ASTRO_GATEWAY=test ASTRO_DEV_LOGIN=1 uvicorn app.main:app --port 8600
    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_traffic

The server must see the client as 127.0.0.1 and honour X-Forwarded-For from it
(uvicorn's default), and it rate-limits /api/visit per address, so run this
against a server that has not just taken a burst of beacons from 127.0.0.1.
"""

from __future__ import annotations

import datetime as dt
import os
import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import analytics as an  # noqa: E402

BASE = os.environ.get("ASTRO_TEST_BASE", "http://127.0.0.1:8600")
RUN = random.randint(100000, 999999)
failures: list[str] = []

CHROME = (f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          f"(KHTML, like Gecko) Chrome/120.0 Safari/537.36 run{RUN}")
# Beacons come "from" an address unique to this run (via X-Forwarded-For, which the
# server honours from 127.0.0.1), so the per-address rate limit on /api/visit is
# never shared with an earlier run against the same server. 198.18.0.0/15 is a
# reserved benchmarking range: not a cloud network, never a real visitor.
RUN_IP = f"198.18.{RUN % 250}.{RUN // 250 % 250 + 1}"
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

    print("\n2b. Fake browsers seen on the live server (2026-09-27)")
    fake_iphone = ("Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 "
                   "(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1")
    for label, ua in (("the fixed iOS 13.2.3 iPhone (~100 cloud IPs)", fake_iphone),
                      ("any other iPhone OS <= 13", fake_iphone.replace("13_2_3", "12_4_1")),
                      ("a bare 'Google Chrome' UA", "Google Chrome"),
                      ("a two-letter UA", "XY"),
                      ("the typo'd '(HTML, like Gecko' UA",
                       "Mozilla/5.0 (Linux; Android 7.0;) AppleWebKit/537.36 (HTML, like Gecko) Mobile Safari/537.36"),
                      ("a scraper that avoids the word bot", "Mozilla/5.0 (compatible; CBZeroScraper/1.0)")):
        check(f"counted as a bot: {label}", an.is_bot(ua))
    for label, ua in (("iPhone on iOS 14", fake_iphone.replace("13_2_3", "14_8")),
                      ("iPhone on iOS 15", fake_iphone.replace("13_2_3", "15_7")),
                      ("iPhone on iOS 17", IPHONE),
                      ("Android Chrome", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                                         "(KHTML, like Gecko) Chrome/153.0.0.0 Mobile Safari/537.36"),
                      ("Windows Chrome", CHROME)):
        check(f"still counted as a person: {label}", not an.is_bot(ua))

    print("\n2c. Cloud networks nobody browses from")
    for label, ip in (("Tencent Cloud 43.157.x", "43.157.38.228"), ("Tencent Cloud 49.51.x", "49.51.166.228"),
                      ("Tencent Cloud 162.62.x", "162.62.213.10"), ("Huawei Cloud 114.119.129.x", "114.119.129.25"),
                      ("Google Cloud 34.96.x", "34.96.40.48")):
        check(f"cloud address is filtered: {label}", an.is_cloud_ip(ip))
    for label, ip in (("Jio residential 49.37.x (49.51 must not bleed into 49.37)", "49.37.248.16"),
                      ("Airtel-style 223.233.x", "223.233.65.10"), ("a documentation address", "203.0.113.9"),
                      ("IPv6 residential", "2401:4900:1c00::1"), ("empty", ""), ("garbage", "not-an-ip")):
        check(f"person's address is kept: {label}", not an.is_cloud_ip(ip))
    import os as _os
    _os.environ["ASTRO_BOT_NETS"] = "203.0.113.0/24, bad-entry"
    try:
        an._CLOUD_NETS = an._cloud_networks()
        check("ASTRO_BOT_NETS adds ranges without a code change", an.is_cloud_ip("203.0.113.9"))
        check("a bad ASTRO_BOT_NETS entry is ignored, not fatal", an.is_cloud_ip("43.157.38.228"))
    finally:
        _os.environ.pop("ASTRO_BOT_NETS", None)
        an._CLOUD_NETS = an._cloud_networks()
    check("the override is gone again afterwards", not an.is_cloud_ip("203.0.113.9"))

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
        # the funnel: visitors -> sign-ups -> saved a chart -> asked
        from app.db import BirthProfile, QuestionLog
        f0 = an.summary(db, 30)["funnel"]
        check("the funnel carries every step",
              {"visitors", "new_users", "chart_users", "charts", "question_users", "questions"} <= set(f0), str(f0))
        check("with no charts or questions yet, those steps are 0",
              (f0["charts"], f0["questions"]) == (0, 0) and f0["visitors"] == 3, str(f0))
        users = db.query(User).order_by(User.id).all()
        boss = User(email="boss@example.com", provider="google", provider_sub="gb", is_admin=True,
                    created_at=now_ - dt.timedelta(days=40))
        db.add(boss)
        db.flush()
        birth = dict(date="1990-01-01", time="10:00", place="Delhi", latitude=28.6, longitude=77.2,
                     timezone="Asia/Kolkata")
        for u in users[:2]:                                    # two people, three charts
            db.add(BirthProfile(user_id=u.id, created_at=now_, **birth))
        db.add(BirthProfile(user_id=users[0].id, created_at=now_, **birth))
        db.add(BirthProfile(user_id=users[2].id, created_at=now_ - dt.timedelta(days=60), **birth))
        db.add(BirthProfile(user_id=boss.id, created_at=now_, **birth))
        for _ in range(4):
            db.add(QuestionLog(user_id=users[0].id, question="q", answer="a", created_at=now_))
        db.add(QuestionLog(user_id=boss.id, question="q", answer="a", created_at=now_))
        db.commit()
        f1 = an.summary(db, 30)["funnel"]
        check("charts saved in the window, and by how many people",
              (f1["charts"], f1["chart_users"]) == (3, 2), str(f1))
        check("questions asked in the window, and by how many people",
              (f1["questions"], f1["question_users"]) == (4, 1), str(f1))
        check("the funnel's sign-ups and visitors match the totals",
              f1["new_users"] == 47 and f1["visitors"] == 3, str(f1))
        check("the 7-day funnel is computed over 7 days",
              an.summary(db, 7)["funnel"]["charts"] == 3)
    eng.dispose()

    print("\n3d. The beacon body is checked before anything is counted")
    pb = an.parse_beacon
    check("a normal beacon is accepted, query reduced to the keys that matter",
          pb({"path": "/", "ref": "https://www.google.com/", "q": "?utm_source=x&junk=1&fbclid=abc"})
          == ("/", "https://www.google.com/", {"utm_source": "x"}))
    check("every public page is accepted, trailing slash or not",
          all(pb({"path": p_ + "/", "ref": "", "q": ""}) is not None
              for p_ in ("/feedback", "/terms", "/privacy", "/refund", "/contact")))
    for label, body in (("an API path", {"path": "/api/health"}), ("the admin page", {"path": "/admin"}),
                        ("a made-up page", {"path": "/wp-login.php"}), ("no path", {"ref": ""}),
                        ("a non-string path", {"path": ["/"]}), ("a list, not an object", ["/"]),
                        ("null", None), ("an over-long referrer", {"path": "/", "ref": "x" * 5000})):
        check(f"rejected: {label}", pb(body) is None)
    check("?welcome survives parsing so the visit can be skipped",
          "welcome" in pb({"path": "/", "q": "?welcome=1"})[2])

    print("\n3e. The beacon is rate-limited per address, in memory")
    an._rate.clear()
    t = 1000.0
    allowed = sum(an.rate_ok("198.51.100.7", t) for _ in range(an.RATE_MAX + 15))
    check(f"at most {an.RATE_MAX} a minute from one address", allowed == an.RATE_MAX, str(allowed))
    check("another address is unaffected", an.rate_ok("198.51.100.8", t))
    check("the window resets after a minute", an.rate_ok("198.51.100.7", t + an.RATE_WINDOW_S + 1))
    an._rate.clear()
    allowed6 = sum(an.rate_ok(f"2401:4900:1c00:7::{i:x}", t) for i in range(an.RATE_MAX + 15))
    check("rotating IPv6 addresses inside one /64 share a limit", allowed6 == an.RATE_MAX, str(allowed6))
    check("garbage in place of an address does not crash it", an.rate_ok("not-an-ip", t))
    an._rate.clear()


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


def beacon(path: str = "/", ua: str = CHROME, referrer: str = "", q: str = "",
           headers: dict | None = None, session_: requests.Session | None = None, raw=None):
    """What static/visit.js sends after the page has loaded and run its script.
    Like sendBeacon, the body is a plain-text JSON string."""
    import json
    s = session_ or requests.Session()
    data = raw if raw is not None else json.dumps({"path": path, "ref": referrer, "q": q})
    return s.post(f"{BASE}/api/visit", data=data, timeout=30,
                  headers={"User-Agent": ua, "Content-Type": "text/plain;charset=UTF-8",
                           "Referer": f"{BASE}{path}", "X-Forwarded-For": RUN_IP, **(headers or {})})


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
    for path in ("/", "/feedback", "/terms", "/privacy", "/refund", "/contact"):
        r = get(path, headers={"Referer": "https://www.google.com/search?q=kundali"})
        check(f"{path} loads", r.status_code == 200, str(r.status_code))
        check(f"loading {path} sets no cookie", "astro_src" not in r.headers.get("set-cookie", ""))
    check("loading the HTML alone records NOTHING (scanners never run the beacon)",
          count_visits() == before, f"{before} -> {count_visits()}")
    home = get("/").text
    check("every public page loads the beacon script",
          "/static/visit.js" in home and "/static/visit.js" in get("/feedback").text
          and all("/static/visit.js" in get(p_).text for p_ in ("/terms", "/privacy", "/refund", "/contact")))
    check("the beacon script itself is served", get("/static/visit.js").status_code == 200)

    r = beacon("/", referrer="https://www.google.com/search?q=kundali")
    check("the beacon answers 204", r.status_code == 204, str(r.status_code))
    rows = visits_now()
    check("one beacon records one visit", len(rows) == before + 1, f"{before} -> {len(rows)}")
    v = rows[-1]
    check("classified by the PAGE's referrer, not the beacon's own (our-site) Referer",
          (v.path, v.source, v.device) == ("/", "google", "desktop"), str((v.path, v.source, v.device)))
    check("and an anonymous visitor hash", len(v.visitor) == 16)
    stored = " ".join(str(x) for x in (v.path, v.source, v.medium, v.campaign, v.device, v.visitor))
    check("NO IP address and NO browser string reached the database",
          RUN_IP not in stored and "127.0.0.1" not in stored and "Mozilla" not in stored and f"run{RUN}" not in stored, stored)

    n = count_visits()
    for label, kwargs in [
        ("a bot", dict(ua="Googlebot/2.1 (+http://www.google.com/bot.html)")),
        ("headless Chrome", dict(ua="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "HeadlessChrome/120.0 Safari/537.36")),
        ("a WhatsApp link-preview fetch", dict(ua="WhatsApp/2.23.20.0 A")),
        ("Do-Not-Track", dict(headers={"DNT": "1"})),
        ("Global-Privacy-Control", dict(headers={"Sec-GPC": "1"})),
        ("a prerender", dict(headers={"Sec-Purpose": "prefetch;prerender"})),
        ("no user-agent at all", dict(ua="")),
        ("the fake iOS 13.2.3 iPhone", dict(ua="Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) "
                                              "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1")),
        ("a real-looking browser arriving from a Tencent Cloud address", dict(headers={"X-Forwarded-For": "43.157.38.228"})),
        ("a real-looking browser arriving from a Google Cloud address", dict(headers={"X-Forwarded-For": "34.96.40.48"})),
        ("the landing after signing in (?welcome)", dict(q="?welcome=1")),
    ]:
        r = beacon("/", **kwargs)
        check(f"{label} is not counted (and still gets a quiet 204)",
              count_visits() == n and r.status_code == 204, f"{n} -> {count_visits()}, {r.status_code}")
    beacon("/", ua=CHROME + " home", headers={"X-Forwarded-For": "49.37.248.16"})
    check("a real person on a home connection IS still counted", count_visits() == n + 1, f"{n} -> {count_visits()}")

    print("\n4b. The beacon ignores garbage")
    n = count_visits()
    for path in ("/api/health", "/static/app.js", "/admin", "/wp-login.php", "/docs"):
        r = beacon(path)
        check(f"a beacon claiming {path} is ignored", count_visits() == n and r.status_code == 204,
              f"{n} -> {count_visits()}, {r.status_code}")
    check("a body that is not JSON -> 400", beacon(raw="hello").status_code == 400)
    check("deeply nested JSON -> 400, not a crash", beacon(raw="[" * 2000).status_code == 400)
    check("an oversized body -> 413", beacon(raw='{"path": "/", "ref": "' + "x" * 5000 + '"}').status_code == 413)
    check("a GET to the beacon is not allowed", requests.get(f"{BASE}/api/visit", timeout=10).status_code == 405)
    check("none of that was counted", count_visits() == n, f"{n} -> {count_visits()}")
    flood_ip = f"198.19.{RUN % 250}.{RUN // 250 % 250 + 1}"
    codes = {beacon("/", ua=CHROME + " flood", headers={"X-Forwarded-For": flood_ip}).status_code
             for _ in range(an.RATE_MAX + 5)}
    check(f"one address flooding the beacon records at most {an.RATE_MAX} a minute",
          count_visits() == n + an.RATE_MAX, f"{n} -> {count_visits()}")
    check("and the excess still gets a quiet 204", codes == {204}, str(codes))

    print("\n5. Public pages, paths, UTM tags")
    beacon("/feedback")
    beacon("/privacy/", referrer="https://divineastro.org/")
    paths = [x.path for x in visits_now()[-2:]]
    check("other public pages are counted with their own path (trailing slash normalised)",
          paths == ["/feedback", "/privacy"], str(paths))
    beacon("/", ua=IPHONE, q=f"?utm_source=WhatsApp&utm_medium=Social&utm_campaign=diwali{RUN}")
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
    beacon("/", session_=a)
    check("a signed-in admin loading the site adds nothing", count_visits() == n, f"{n} -> {count_visits()}")
    beacon("/", ua=CHROME + " other")
    check("but an ordinary visitor still does", count_visits() == n + 1)

    print("\n7. The first-touch cookie")
    s = requests.Session()
    r = get("/?utm_source=instagram&utm_campaign=reel1", ua=CHROME + " insta", session_=s)
    check("loading the page does not set it — only a browser that runs the beacon gets one",
          "astro_src" not in r.headers.get("set-cookie", "") and "astro_src" not in s.cookies)
    r = beacon("/", ua=CHROME + " insta", q="?utm_source=instagram&utm_campaign=reel1", session_=s)
    set_cookie = r.headers.get("set-cookie", "")
    check("the first beacon sets the source cookie (source|campaign)",
          "astro_src=instagram|reel1" in set_cookie.replace('"', ''), set_cookie[:120])
    check("it is HttpOnly, SameSite=Lax and site-wide",
          all(x in set_cookie.lower() for x in ("httponly", "samesite=lax", "path=/")), set_cookie)
    r = beacon("/", ua=CHROME + " insta", q="?utm_source=facebook", session_=s)
    check("a later visit does NOT overwrite it (first touch wins)", "astro_src" not in r.headers.get("set-cookie", ""))
    r2 = beacon("/", session_=requests.Session(), referrer="https://divineastro.org/x")
    check("an internal referrer never seeds the cookie", "astro_src" not in r2.headers.get("set-cookie", ""))
    r3 = beacon("/", session_=requests.Session(), ua="Googlebot/2.1 (+http://www.google.com/bot.html)",
                q="?utm_source=spam")
    check("a bot's beacon never gets the cookie", "astro_src" not in r3.headers.get("set-cookie", ""))

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
    s3 = requests.Session()
    beacon("/terms", ua=CHROME + " legal", referrer="https://t.co/abc", session_=s3)
    email3 = f"legal{RUN}@example.com"
    sign_in(email3, s3)
    check("first touch on a legal page attributes too", user_row(email3).signup_source == "x",
          str(user_row(email3).signup_source))

    print("\n9. The admin endpoint")
    plain = sign_in(f"tplain{RUN}@example.com")
    check("anonymous -> 401", requests.get(f"{BASE}/api/admin/traffic", timeout=20).status_code == 401)
    check("a normal user -> 403", plain.get(f"{BASE}/api/admin/traffic", timeout=20).status_code == 403)
    t0 = a.get(f"{BASE}/api/admin/traffic?days=30", timeout=30).json()
    keys = {"range", "windows", "totals", "funnel", "live_now", "daily", "sources", "signup_sources",
            "providers", "devices", "pages", "campaigns", "tracking_since", "users_total"}
    check("the response carries every section", keys <= set(t0), str(keys - set(t0)))
    check("30 days -> 30 daily points, oldest first", len(t0["daily"]) == 30
          and t0["daily"][0]["date"] < t0["daily"][-1]["date"])
    check("days=0 is clamped to 1, days=999 to 180",
          len(a.get(f"{BASE}/api/admin/traffic?days=0", timeout=30).json()["daily"]) == 1
          and len(a.get(f"{BASE}/api/admin/traffic?days=999", timeout=30).json()["daily"]) == 180)
    today = t0["daily"][-1]
    check("today's page views include what this test just generated", today["pageviews"] >= 8, str(today))
    fun = t0["funnel"]
    check("the funnel carries every step",
          {"visitors", "new_users", "chart_users", "charts", "question_users", "questions"} <= set(fun), str(fun))
    check("its visitors and sign-ups are the range totals",
          (fun["visitors"], fun["new_users"]) == (t0["totals"]["visitors"], t0["totals"]["new_users"]), str(fun))
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


def events_now() -> list:
    from sqlalchemy import select

    from app.db import Event, session

    with session() as db:
        return db.execute(select(Event).order_by(Event.id)).scalars().all()


def part3() -> None:
    """DIVASTRO-128: in-app events."""
    import json

    print("\n6. In-app events")
    ev_ip = f"198.19.{(RUN + 7) % 250}.{(RUN // 250 + 9) % 250 + 1}"

    def post_event(name: str = "chart_cast", detail: str = "", ua: str = CHROME, headers=None, raw=None):
        data = raw if raw is not None else json.dumps({"name": name, "detail": detail})
        return requests.post(f"{BASE}/api/event", data=data, timeout=30,
                             headers={"User-Agent": ua, "Content-Type": "text/plain;charset=UTF-8",
                                      "Referer": f"{BASE}/", "X-Forwarded-For": ev_ip, **(headers or {})})

    n = len(events_now())
    r = post_event("screen", "birth")
    check("an event answers 204", r.status_code == 204, str(r.status_code))
    rows = events_now()
    check("one event is one row", len(rows) == n + 1, f"{n} -> {len(rows)}")
    e = rows[-1]
    check("with its name, label and an anonymous visitor hash",
          (e.name, e.detail) == ("screen", "birth") and len(e.visitor) == 16, str((e.name, e.detail, e.visitor)))
    stored = " ".join(str(x) for x in (e.name, e.detail, e.visitor, e.source, e.campaign))
    check("NO IP address and NO browser string in the row",
          ev_ip not in stored and "Mozilla" not in stored and f"run{RUN}" not in stored, stored)
    check("the label is cleaned to a short safe string",
          (post_event("checkout_start", "<script>BAD sku!</script>").status_code == 204
           and events_now()[-1].detail == "scriptbadskuscript"), events_now()[-1].detail)

    n = len(events_now())
    for label, kwargs in [
        ("a bot", dict(ua="Googlebot/2.1 (+http://www.google.com/bot.html)")),
        ("Do-Not-Track", dict(headers={"DNT": "1"})),
        ("Global-Privacy-Control", dict(headers={"Sec-GPC": "1"})),
        ("a prerender", dict(headers={"Sec-Purpose": "prefetch;prerender"})),
        ("a Tencent Cloud address", dict(headers={"X-Forwarded-For": "43.157.38.228"})),
        ("an unknown event name", dict(name="drop_table")),
    ]:
        r = post_event(**kwargs)
        check(f"{label} is not recorded (and still gets a quiet 204)",
              len(events_now()) == n and r.status_code == 204, f"{n} -> {len(events_now())}, {r.status_code}")
    check("a body that is not JSON -> 400", post_event(raw="hello").status_code == 400)
    check("an oversized body -> 413", post_event(raw='{"name": "screen", "detail": "' + "x" * 2000 + '"}').status_code == 413)
    check("a GET to /api/event is not allowed", requests.get(f"{BASE}/api/event", timeout=10).status_code == 405)
    check("none of that was recorded", len(events_now()) == n, f"{n} -> {len(events_now())}")

    print("\n6b. The admin summary shows the in-app funnel and journeys")
    jv = f"198.19.{(RUN + 11) % 250}.{(RUN // 250 + 13) % 250 + 1}"
    jua = CHROME + " journey"
    hdr = {"X-Forwarded-For": jv}
    beacon("/panchang/bengaluru", ua=jua, q="?utm_source=whatsapp&utm_campaign=blr-test", headers=hdr)
    for name, detail in [("screen", "birth"), ("chart_cast", ""), ("ask_sent", "")]:
        requests.post(f"{BASE}/api/event", data=json.dumps({"name": name, "detail": detail}), timeout=30,
                      headers={"User-Agent": jua, "Content-Type": "text/plain;charset=UTF-8",
                               "X-Forwarded-For": jv})
    admin = sign_in(f"admin{RUN}@example.com")
    make_admin(f"admin{RUN}@example.com")
    d = admin.get(f"{BASE}/api/admin/traffic?days=7", timeout=30).json()
    steps = {x["label"]: x["count"] for x in d.get("app_funnel", [])}
    check("the funnel counts people who cast a chart",
          steps.get("Cast a chart", 0) >= 1 and steps.get("Asked the AI a question", 0) >= 1, str(steps))
    mine = [j for j in d.get("journeys", []) if j["steps"] and j["steps"][0]["label"] == "/panchang/bengaluru"]
    check("the journey lists the page, then each action in order",
          bool(mine) and [x["label"] for x in mine[0]["steps"]] ==
          ["/panchang/bengaluru", "screen: birth", "chart_cast", "ask_sent"],
          str(mine[:1]))
    check("the journey carries the visitor's source", bool(mine) and mine[0]["source"] == "whatsapp", str(mine[:1]))

    print("\n6c. Events are purged with visits")
    from app.db import Event, session
    with session() as db:
        db.add_all([Event(ts=an.utcnow() - dt.timedelta(days=an.RETENTION_DAYS + 30), name="screen", detail="old-ev"),
                    Event(ts=an.utcnow(), name="screen", detail="fresh-ev")])
        db.commit()
        an.purge_old(db)
        left = {x.detail for x in db.query(Event).filter(Event.detail.in_(["old-ev", "fresh-ev"]))}
    check("old events are deleted, recent ones kept", left == {"fresh-ev"}, str(left))


def main() -> int:
    part1()
    try:
        requests.get(f"{BASE}/api/health", timeout=5).raise_for_status()
    except Exception:
        print("\n(server not reachable — part 2 skipped; start it to run the integration checks)")
        return 1 if failures else 0
    part2()
    part3()
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
