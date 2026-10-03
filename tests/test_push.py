"""Daily web push (DIVASTRO-112): endpoints, the daily message, the sender.

Pins: the whole feature is OFF without VAPID keys (404s, no opt-in markup); the
key / subscribe / unsubscribe endpoints and their validation (only real push
services, real P-256 keys, a real timezone); the message for a vrat day (Indira
Ekadashi, 6 Oct 2026, with its parana) and an ordinary day (Rahu Kaal), EN and
HI, with UTM tags; the sender sends once per local day at 06:00-11:00 in each
subscriber's own timezone, never twice, deletes on 404/410, counts other
failures; the migration applies (and rolls back) on SQLite; the admin Traffic
summary carries the subscriber count; app.push_keys makes a usable key pair.

No server needed, no network: pywebpush.webpush is replaced by a recorder.
A throwaway SQLite database.

    ~/.venvs/divineastro/bin/python -u -m tests.test_push
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import os
import secrets
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_push_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["ASTRO_ADMIN_EMAILS"] = "owner@divineastro.org"
os.environ["ASTRO_PUSH_SENDER"] = "0"
for _k in ("ASTRO_VAPID_PUBLIC_KEY", "ASTRO_VAPID_PRIVATE_KEY"):
    os.environ.pop(_k, None)

import pywebpush  # noqa: E402
from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import ec  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import inspect, select  # noqa: E402

from app import daily_message, push, push_keys  # noqa: E402
from app.db import PushSubscription, engine, session as db_session  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
UTM = "utm_source=push&utm_medium=notification&utm_campaign=daily"


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def browser_sub(host: str = "fcm.googleapis.com") -> dict:
    """A subscription shaped exactly like a browser's PushSubscription.toJSON()."""
    pub = ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return {"endpoint": f"https://{host}/fcm/send/{secrets.token_urlsafe(24)}",
            "keys": {"p256dh": _b64(pub), "auth": _b64(secrets.token_bytes(16))}}


def body(sub: dict | None = None, **kw) -> dict:
    out = {"subscription": sub or browser_sub(), "lat": 28.6139, "lon": 77.2090,
           "tz": "Asia/Kolkata", "label": "New Delhi, Delhi", "lang": "en"}
    out.update(kw)
    return out


def keys_on() -> None:
    pub, priv = push_keys.generate()
    os.environ["ASTRO_VAPID_PUBLIC_KEY"] = pub
    os.environ["ASTRO_VAPID_PRIVATE_KEY"] = priv
    os.environ["ASTRO_VAPID_SUBJECT"] = "mailto:support@divineastro.org"


def keys_off() -> None:
    os.environ.pop("ASTRO_VAPID_PUBLIC_KEY", None)
    os.environ.pop("ASTRO_VAPID_PRIVATE_KEY", None)


def rows() -> list[PushSubscription]:
    with db_session() as db:
        return list(db.execute(select(PushSubscription).order_by(PushSubscription.id)).scalars())


def clear() -> None:
    with db_session() as db:
        for r in db.execute(select(PushSubscription)).scalars():
            db.delete(r)
        db.commit()


class FakeResp:
    def __init__(self, status: int):
        self.status_code = status
        self.reason = "x"
        self.text = ""
        self.headers = {}


class Recorder:
    """Stands in for pywebpush.webpush. `status` per call: 201, an error
    status (raised as WebPushException, as the real one does), or an exception."""

    def __init__(self, status=201):
        self.status = status
        self.calls: list[dict] = []

    def __call__(self, subscription_info, data=None, vapid_private_key=None,
                 vapid_claims=None, ttl=0, timeout=None, headers=None, **_):
        self.calls.append({"endpoint": subscription_info["endpoint"], "data": json.loads(data),
                           "claims": dict(vapid_claims or {}), "ttl": ttl,
                           "vapid": vapid_private_key})
        if isinstance(self.status, Exception):
            raise self.status
        if self.status > 202:
            raise pywebpush.WebPushException("Push failed", response=FakeResp(self.status))
        return FakeResp(self.status)


def utc(y, m, d, hh, mm) -> dt.datetime:
    return dt.datetime(y, m, d, hh, mm, tzinfo=dt.timezone.utc)


def main() -> int:
    real_webpush = pywebpush.webpush

    print("1. Migration: the table exists on SQLite after alembic upgrade head")
    insp = inspect(engine)
    check("push_subscriptions table created", "push_subscriptions" in insp.get_table_names())
    cols = {c["name"] for c in insp.get_columns("push_subscriptions")}
    want = {"id", "endpoint", "p256dh", "auth", "lat", "lon", "tz", "city", "lang",
            "user_id", "created_at", "last_sent", "failures"}
    check("all columns present", want <= cols, str(sorted(want - cols)))
    uniq = [u["column_names"] for u in insp.get_unique_constraints("push_subscriptions")]
    check("endpoint is unique", ["endpoint"] in uniq, str(uniq))
    from alembic import command
    from alembic.config import Config
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", os.environ["ASTRO_DATABASE_URL"])
    try:
        command.downgrade(cfg, "-1")
        gone = "push_subscriptions" not in inspect(engine).get_table_names()
        command.upgrade(cfg, "head")
        back = "push_subscriptions" in inspect(engine).get_table_names()
        check("downgrade -1 drops it, upgrade head brings it back", gone and back)
    except Exception as exc:
        check("downgrade/upgrade round trip", False, repr(exc))

    print("2. Feature OFF without VAPID keys")
    keys_off()
    check("GET /api/push/key -> 404", client.get("/api/push/key").status_code == 404)
    check("GET /sw.js -> 404", client.get("/sw.js").status_code == 404)
    check("POST /api/push/subscribe -> 404",
          client.post("/api/push/subscribe", json=body()).status_code == 404)
    check("POST /api/push/unsubscribe -> 404",
          client.post("/api/push/unsubscribe", json={"endpoint": "x"}).status_code == 404)
    page = client.get("/vrat-tyohar").text
    check("/vrat-tyohar has no opt-in markup", "push-optin" not in page and "push.js" not in page)
    check("run_due does nothing", push.run_due(utc(2026, 10, 6, 1, 0))["due"] == 0)
    check("sender not started", push.start_sender() is None)
    home = client.get("/").text
    check("home carries the hidden mount + push.js (it asks /api/push/key itself)",
          'id="push-optin"' in home and "/static/push.js" in home)

    print("3. Feature ON")
    keys_on()
    r = client.get("/api/push/key")
    check("GET /api/push/key -> the public key", r.status_code == 200
          and r.json().get("key") == os.environ["ASTRO_VAPID_PUBLIC_KEY"])
    sw = client.get("/sw.js")
    check("GET /sw.js -> JavaScript, no-cache, push + notificationclick handlers",
          sw.status_code == 200 and "javascript" in sw.headers.get("content-type", "")
          and sw.headers.get("cache-control") == "no-cache"
          and "'push'" in sw.text and "'notificationclick'" in sw.text, sw.headers.get("content-type"))
    check("service worker has no fetch handler (no offline caching)", "'fetch'" not in sw.text)
    for path in ("/vrat-tyohar", "/hi/vrat-tyohar", "/ekadashi-2026", "/hi/vrat-tyohar/2026",
                 "/tyohar/diwali-2026"):
        html = client.get(path).text
        check(f"{path}: opt-in mount + /static/push.js",
              'id="push-optin"' in html and '<script src="/static/push.js" defer>' in html)
    check("sender still off with ASTRO_PUSH_SENDER=0", push.start_sender() is None)

    print("4. Subscribe / unsubscribe")
    clear()
    s1 = browser_sub()
    r = client.post("/api/push/subscribe", json=body(s1))
    check("subscribe -> 200 created", r.status_code == 200 and r.json() == {"ok": True, "created": True},
          r.text)
    r = client.post("/api/push/subscribe", json=body(s1, lang="hi", label="Lucknow, Uttar Pradesh",
                                                       lat=26.85, lon=80.95))
    check("same endpoint again -> updated, not duplicated",
          r.status_code == 200 and r.json()["created"] is False and len(rows()) == 1)
    row = rows()[0]
    check("stored city/lang/place/keys", (row.lang, row.city, row.lat, row.tz, row.p256dh, row.auth) ==
          ("hi", "Lucknow, Uttar Pradesh", 26.85, "Asia/Kolkata", s1["keys"]["p256dh"], s1["keys"]["auth"]))
    check("anonymous subscriber has no user_id", row.user_id is None)

    signed = TestClient(app, raise_server_exceptions=False)
    signed.post("/api/auth/dev", json={"email": "owner@divineastro.org"})
    s2 = browser_sub("updates.push.services.mozilla.com")
    r = signed.post("/api/push/subscribe", json=body(s2))
    check("signed-in subscribe (Firefox endpoint) records user_id",
          r.status_code == 200 and rows()[-1].user_id is not None, r.text)
    tr = signed.get("/api/admin/traffic?days=7")
    check("admin Traffic summary carries the subscriber count",
          tr.status_code == 200 and tr.json().get("push") == {"enabled": True, "subscribers": 2},
          str(tr.json().get("push") if tr.status_code == 200 else tr.status_code))

    bad = [
        ("http endpoint", body({**browser_sub(), "endpoint": "http://fcm.googleapis.com/x"})),
        ("unknown host", body({**browser_sub(), "endpoint": "https://evil.example.com/push"})),
        ("lookalike host", body({**browser_sub(), "endpoint": "https://fcm.googleapis.com.evil.io/x"})),
        ("internal host", body({**browser_sub(), "endpoint": "https://127.0.0.1/x"})),
        ("odd port", body({**browser_sub(), "endpoint": "https://fcm.googleapis.com:8443/x"})),
        ("p256dh not a P-256 point", body({**browser_sub(), "keys": {"p256dh": _b64(b"x" * 40),
                                                                     "auth": _b64(b"a" * 16)}})),
        ("auth wrong length", body({**browser_sub(), "keys": {**browser_sub()["keys"],
                                                              "auth": _b64(b"a" * 8)}})),
        ("unknown timezone", body(tz="Mars/Olympus")),
    ]
    for label, payload in bad:
        r = client.post("/api/push/subscribe", json=payload)
        check(f"rejects {label} (400)", r.status_code == 400, f"{r.status_code} {r.text[:80]}")
    r = client.post("/api/push/subscribe", json=body(lat=123))
    check("rejects latitude out of range (422)", r.status_code == 422, str(r.status_code))
    r = client.post("/api/push/subscribe", json={"lat": 1})
    check("rejects a body without a subscription (422)", r.status_code == 422)
    check("nothing stored by the rejected requests", len(rows()) == 2)

    r = client.post("/api/push/unsubscribe", json={"endpoint": s2["endpoint"]})
    check("unsubscribe -> removed", r.status_code == 200 and r.json()["removed"] is True
          and len(rows()) == 1)
    r = client.post("/api/push/unsubscribe", json={"endpoint": s2["endpoint"]})
    check("unsubscribe again -> 200, nothing to remove", r.status_code == 200
          and r.json()["removed"] is False)

    print("5. The daily message")
    d_vrat, d_plain = dt.date(2026, 10, 6), dt.date(2026, 10, 5)
    delhi = (28.6139, 77.2090, "Asia/Kolkata")
    en = daily_message.build(d_vrat, *delhi, "en", city="New Delhi, Delhi")
    hi = daily_message.build(d_vrat, *delhi, "hi", city="New Delhi, Delhi")
    print("     ", en)
    print("     ", hi)
    check("vrat day EN title", en["title"] == "Today: Indira Ekadashi", en["title"])
    check("vrat day EN body: parana next morning, Delhi",
          en["body"] == "Parana (breaking the fast): 7 Oct, 06:17–08:37 · New Delhi", en["body"])
    check("vrat day HI title", hi["title"] == "आज: इंदिरा एकादशी", hi["title"])
    check("vrat day HI body", hi["body"] == "पारण का समय: 7 अक्टूबर, 06:17–08:37 · नई दिल्ली", hi["body"])
    check("vrat day links the vrat-tyohar page with UTM",
          en["path"] == f"/vrat-tyohar?{UTM}" and hi["path"] == f"/hi/vrat-tyohar?{UTM}"
          and en["url"].endswith(en["path"]) and en["url"].startswith("http"))
    en = daily_message.build(d_plain, *delhi, "en", city="New Delhi, Delhi")
    hi = daily_message.build(d_plain, *delhi, "hi", city="New Delhi, Delhi")
    print("     ", en)
    print("     ", hi)
    check("ordinary day EN: Rahu Kaal title", en["title"] == "Today's Rahu Kaal in New Delhi: 07:44–09:12",
          en["title"])
    check("ordinary day HI: Rahu Kaal title", hi["title"] == "आज का राहु काल: 07:44–09:12 · नई दिल्ली",
          hi["title"])
    check("ordinary day links the city's Rahu Kaal page",
          en["path"] == f"/rahu-kaal?{UTM}" and hi["path"] == f"/hi/rahu-kaal?{UTM}")
    lko = daily_message.build(d_plain, 26.85, 80.95, "Asia/Kolkata", "hi", city="Lucknow, Uttar Pradesh")
    check("Lucknow: own page + Hindi city name",
          lko["path"].startswith("/hi/rahu-kaal/lucknow?") and "लखनऊ" in lko["title"], lko["title"])
    ldn = daily_message.build(d_plain, 51.5074, -0.1278, "Europe/London", "en", city="London, England")
    check("a city with no page: London's own Rahu Kaal in London time, links the app's Panchang",
          ldn["title"].startswith("Today's Rahu Kaal in London: 0") and ldn["path"].startswith("/?open=panchang"),
          ldn["title"])
    tag = daily_message.build(d_plain, *delhi, "en", source="telegram", medium="social", campaign="daily")
    check("UTM tags are the caller's (shareable with other channels)",
          "utm_source=telegram&utm_medium=social" in tag["path"])

    print("6. The sender: 06:00 local, once a day, per timezone")
    clear()
    rec = Recorder(201)
    pywebpush.webpush = rec
    try:
        client.post("/api/push/subscribe", json=body(browser_sub(), lang="hi"))       # Delhi, Hindi
        client.post("/api/push/subscribe", json=body(browser_sub(), lat=51.5074, lon=-0.1278,
                                                     tz="Europe/London", label="London, England"))
        st = push.run_due(utc(2026, 10, 6, 0, 15))            # 05:45 IST, 01:15 BST
        check("before 06:00 local: nobody due", st["due"] == 0 and not rec.calls, str(st))
        st = push.run_due(utc(2026, 10, 6, 0, 35))            # 06:05 IST
        check("06:05 IST: the Delhi subscriber only", st == {"due": 1, "sent": 1, "removed": 0, "failed": 0},
              str(st))
        sent = rec.calls[0]["data"] if rec.calls else {}
        check("payload: Hindi Indira Ekadashi, parana, site-relative URL, icon",
              sent.get("title") == "आज: इंदिरा एकादशी" and "पारण" in sent.get("body", "")
              and sent.get("url") == f"/hi/vrat-tyohar?{UTM}" and sent.get("icon") == push.ICON, str(sent))
        check("VAPID claims: our mailto subject, a key object, TTL set",
              rec.calls and rec.calls[0]["claims"].get("sub") == "mailto:support@divineastro.org"
              and rec.calls[0]["vapid"] is not None and rec.calls[0]["ttl"] == push.TTL_S)
        st = push.run_due(utc(2026, 10, 6, 0, 40))
        st2 = push.run_due(utc(2026, 10, 6, 4, 0))            # 09:30 IST, 05:00 BST
        check("same day again: no second send (idempotent)", st["sent"] == 0 and st2["sent"] == 0
              and len(rec.calls) == 1, f"{st} {st2}")
        st = push.run_due(utc(2026, 10, 6, 5, 5))             # 06:05 BST, 10:35 IST
        check("06:05 London: the London subscriber, in London's own day",
              st["sent"] == 1 and len(rec.calls) == 2 and "London" in rec.calls[1]["data"]["body"]
              + rec.calls[1]["data"]["title"], str(st))
        st = push.run_due(utc(2026, 10, 7, 6, 0))             # 11:30 IST, 07:00 BST
        check("after 11:00 local the day is skipped (no stale 'today'); London still due",
              st["sent"] == 1 and rec.calls[-1]["endpoint"] == rows()[1].endpoint, str(st))
        st = push.run_due(utc(2026, 10, 8, 1, 0))             # 06:30 IST next day
        check("next morning: due again", st["sent"] == 1 and rows()[0].last_sent is not None)

        print("7. Failures: 410/404 delete, others count")
        clear()
        client.post("/api/push/subscribe", json=body(browser_sub()))
        rec.status = 410
        st = push.run_due(utc(2026, 10, 9, 1, 0))
        check("410 Gone -> subscription deleted", st["removed"] == 1 and not rows(), str(st))
        client.post("/api/push/subscribe", json=body(browser_sub()))
        rec.status = 404
        st = push.run_due(utc(2026, 10, 9, 1, 0))
        check("404 -> subscription deleted", st["removed"] == 1 and not rows(), str(st))
        client.post("/api/push/subscribe", json=body(browser_sub()))
        rec.status = 500
        st = push.run_due(utc(2026, 10, 9, 1, 0))
        check("500 -> kept, failure counted",
              st["failed"] == 1 and rows()[0].failures == 1, str(st))
        st = push.run_due(utc(2026, 10, 9, 1, 10))
        check("...and no retry storm the same day (one attempt a day)", st["due"] == 0, str(st))
        rec.status = ConnectionError("down")
        push.run_due(utc(2026, 10, 10, 1, 0))
        check("network error -> failure counted", rows()[0].failures == 2)
        rec.status = 201
        push.run_due(utc(2026, 10, 11, 1, 0))
        check("a success resets the failure count", rows()[0].failures == 0 and rows()[0].last_sent)
        rec.status = 503
        for i in range(push.MAX_FAILURES):
            push.run_due(utc(2026, 10, 12 + i, 1, 0))
        check(f"{push.MAX_FAILURES} failed days in a row -> deleted", not rows())
    finally:
        pywebpush.webpush = real_webpush

    print("8. app.push_keys")
    pub, priv = push_keys.generate()
    from py_vapid import Vapid
    v = Vapid.from_string(priv)
    raw_pub = v.public_key.public_bytes(serialization.Encoding.X962,
                                        serialization.PublicFormat.UncompressedPoint)
    check("public key is the uncompressed point of the private key",
          _b64(raw_pub) == pub and len(raw_pub) == 65)
    hdrs = v.sign({"sub": "mailto:support@divineastro.org", "aud": "https://fcm.googleapis.com"})
    check("the private key signs VAPID headers", "Authorization" in hdrs or "authorization" in hdrs,
          str(list(hdrs)))

    print("9. The real pywebpush path (encryption + VAPID), with only the HTTP POST faked")
    keys_on()
    import requests
    posted: list[dict] = []
    real_post = requests.post

    def fake_post(url, data=None, headers=None, timeout=None, **_):
        posted.append({"url": url, "data": data, "headers": dict(headers or {})})
        return FakeResp(201)

    requests.post = fake_post
    try:
        row = PushSubscription(endpoint=browser_sub()["endpoint"], **{
            k: v for k, v in browser_sub()["keys"].items()}, lat=28.6, lon=77.2, tz="Asia/Kolkata",
            city="", lang="en", failures=0)
        status = push.send_one(row, push.payload({"title": "t", "body": "b", "path": "/"}, "en"))
        h = posted[0]["headers"] if posted else {}
        check("send_one -> 201 through the real library", status == 201, str(status))
        check("encrypted aes128gcm body, VAPID Authorization, TTL and Urgency headers",
              posted and posted[0]["url"] == row.endpoint and h.get("content-encoding") == "aes128gcm"
              and str(h.get("authorization", "")).startswith("vapid t=") and h.get("ttl") == str(push.TTL_S)
              and h.get("urgency") == "normal" and b"title" not in (posted[0]["data"] or b""),
              str({k: (str(v)[:24]) for k, v in h.items()}))
    finally:
        requests.post = real_post

    keys_off()
    print()
    if failures:
        print(f"FAILED {len(failures)}: " + "; ".join(failures))
        return 1
    print("All push checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
