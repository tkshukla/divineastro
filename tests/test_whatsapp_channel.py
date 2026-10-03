"""The automatic WhatsApp Channel poster (DIVASTRO-116), connector mocked.

  * app.whatsapp_channel talks to the `wa` service over HTTP; here an
    httpx.MockTransport plays that service (a tiny state machine: connected or
    not, the channel lookup, posts received).
  * Covered: not configured -> exit 2; --dry-run prints and needs nothing;
    one post a day; --force; the channel JID resolved once and cached; image
    card + Hindi caption + JPEG thumbnail; text-only fallback when the image
    upload fails; logged out / unreachable -> exit 1 and ONE owner email that
    day (console mail transport); a non-owner number refused; the token never
    printed; the email pack builder shared with app/whatsapp_pack.

Nothing is sent anywhere. A throwaway SQLite database and state directory.

    ~/.venvs/divineastro/bin/python -u -m tests.test_whatsapp_channel
"""

from __future__ import annotations

import base64
import contextlib
import datetime as dt
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_wa_channel_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DAILY_STATE_DIR"] = str(Path(_tmp) / "state")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx  # noqa: E402
from PIL import Image  # noqa: E402

from app import daily_state, mail, whatsapp_channel as W, whatsapp_pack  # noqa: E402

failures: list[str] = []

TOKEN = "wa-secret-token-NEVER-PRINTED-0123456789"
LINK = "https://whatsapp.com/channel/0029VaTestChannel01"
JID = "120363012345678901@newsletter"
JITIYA = dt.date(2026, 10, 3)


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(label)


class Stub:
    """The wa service, as far as the sender can tell."""

    def __init__(self) -> None:
        self.connected = True
        self.reason: str | None = None
        self.role = "OWNER"
        self.fail_image = False
        self.down = False
        self.statuses: list[dict] = []     # scripted /status answers, consumed first
        self.calls: list[tuple[str, dict]] = []
        self.posts: list[dict] = []

    def __call__(self, req: httpx.Request) -> httpx.Response:
        if self.down:
            raise httpx.ConnectError("connection refused")
        body = json.loads(req.content) if req.content else {}
        self.calls.append((req.url.path, body))
        if req.headers.get("x-wa-token") != TOKEN:
            return httpx.Response(401, json={"error": "unauthorized"})
        if req.url.path == "/status":
            if self.statuses:
                return httpx.Response(200, json=self.statuses.pop(0))
            st = {"connected": self.connected, "me": "+91••••••••10", "linked_at": "2026-10-01"}
            if not self.connected:
                st["reason"] = self.reason
            return httpx.Response(200, json=st)
        if not self.connected:
            return httpx.Response(409, json={"error": f"not connected ({self.reason})"})
        if req.url.path == "/channel/resolve":
            return httpx.Response(200, json={"jid": JID, "name": "Divine Astro", "role": self.role})
        if req.url.path == "/channel/post":
            if self.fail_image and "image_base64" in body:
                return httpx.Response(502, json={"error": "whatsapp: upload failed"})
            self.posts.append(body)
            return httpx.Response(200, json={"id": f"3EB0{len(self.posts)}"})
        return httpx.Response(404, json={"error": "not found"})

    def paths(self, path: str) -> int:
        return sum(1 for p, _ in self.calls if p == path)


def _run(argv: list[str]) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = W.main(argv)
    return code, out.getvalue() + err.getvalue()


ENV = {"ASTRO_WA_TOKEN": TOKEN, "ASTRO_WA_CHANNEL_LINK": LINK, "ASTRO_WA_URL": "http://wa:3000",
       "ASTRO_WA_WAIT": "60", "ASTRO_SMTP_HOST": "console", "ASTRO_COOKIE_SECURE": "0",
       "ASTRO_DAILY_PACK_TO": "owner@example.com"}


def main() -> int:
    print("WhatsApp Channel poster (DIVASTRO-116)")
    stub = Stub()
    sleeps: list[float] = []
    all_out: list[str] = []

    def run(argv: list[str]) -> tuple[int, str]:
        code, out = _run(argv)
        all_out.append(out)
        return code, out

    with patch.object(W, "_transport", httpx.MockTransport(stub)), \
            patch.object(W, "_sleep", sleeps.append):

        print("\n1. Configuration and dry run")
        with patch.dict(os.environ, {**ENV, "ASTRO_WA_TOKEN": "", "ASTRO_WA_CHANNEL_LINK": ""}):
            code, out = run(["--date", "2026-10-03", "--dry-run"])
            check("dry-run: exit 0 with nothing configured, prints the Hindi post",
                  code == 0 and "जीवित्पुत्रिका" in out and "*कालाष्टमी*" in out
                  and "utm_source=whatsapp" in out, out[:300])
            check("dry-run: no connector call", not stub.calls, str(stub.calls))
            code, out = run(["--date", "2026-10-03"])
            check("not configured: exit 2, names the variables",
                  code == 2 and "ASTRO_WA_TOKEN" in out and "ASTRO_WA_CHANNEL_LINK" in out, out)
        with patch.dict(os.environ, {**ENV, "ASTRO_WA_CHANNEL_LINK": ""}):
            code, out = run(["--date", "2026-10-03"])
            check("token without channel link: exit 2", code == 2, out)
        code, out = run(["--date", "2026-13-01", "--dry-run"])
        check("bad --date: exit 2", code == 2, out)

        print("\n2. Posting once a day")
        with patch.dict(os.environ, ENV):
            code, out = run(["--date", "2026-10-03"])
            check("posts: exit 0", code == 0 and "posted hi for 2026-10-03" in out, out)
            check("posts: exactly one post", len(stub.posts) == 1, str(len(stub.posts)))
            p = stub.posts[0] if stub.posts else {}
            text, png = whatsapp_pack.post(JITIYA, "hi")
            check("posts: to the resolved channel JID", p.get("jid") == JID, str(p.get("jid")))
            check("posts: Hindi whatsapp text (same builder as the email pack) as the caption",
                  p.get("text") == text and "*🪔 आज का पंचांग*" in p.get("text", ""))
            img = base64.b64decode(p.get("image_base64", "")) if p else b""
            check("posts: the image card PNG", img == png and img[:8] == b"\x89PNG\r\n\x1a\n")
            thumb = base64.b64decode(p.get("thumbnail_base64", "")) if p else b""
            ok = False
            if thumb:
                t = Image.open(io.BytesIO(thumb))
                ok = t.format == "JPEG" and max(t.size) <= 96
            check("posts: a small JPEG thumbnail", ok)
            check("state recorded with the message id",
                  daily_state.sent(W.JOB, JITIYA).get("hi") == "3EB01", str(daily_state.load(W.JOB)))
            check("channel JID cached", (daily_state.recall(W.JOB, "channel") or {}).get("jid") == JID)

            code, out = run(["--date", "2026-10-03"])
            check("idempotent: second run exit 0, no new post",
                  code == 0 and len(stub.posts) == 1 and "already posted" in out, out)
            code, out = run(["--date", "2026-10-03", "--force"])
            check("--force posts again", code == 0 and len(stub.posts) == 2, out)
            code, out = run(["--date", "2026-10-04"])
            check("next day posts", code == 0 and len(stub.posts) == 3, out)
            check("JID resolved only once across all runs", stub.paths("/channel/resolve") == 1,
                  str(stub.paths("/channel/resolve")))

            with patch.dict(os.environ, {"ASTRO_WA_CHANNEL_LINK": LINK + "X"}):
                code, out = run(["--date", "2026-10-05"])
                check("a changed channel link is resolved afresh",
                      code == 0 and stub.paths("/channel/resolve") == 2, out)

            code, out = run(["--date", "2026-10-06", "--no-card"])
            check("--no-card: text only", code == 0 and "image_base64" not in stub.posts[-1], out)

            stub.fail_image = True
            code, out = run(["--date", "2026-10-07"])
            stub.fail_image = False
            check("image upload fails: falls back to ONE text-only post",
                  code == 0 and "image_base64" not in stub.posts[-1]
                  and stub.posts[-1]["text"].startswith("*🪔") and "text only" in out, out)

        print("\n3. Not linked: owner email once a day, exit 1")
        with patch.dict(os.environ, ENV):
            mail.OUTBOX.clear()
            n = len(stub.posts)
            stub.connected, stub.reason = False, "logged_out"
            code, out = run(["--date", "2026-10-08"])
            check("logged out: exit 1, nothing posted", code == 1 and len(stub.posts) == n, out)
            check("logged out: reason shown", "logged_out" in out, out)
            check("logged out: no waiting (not a transient state)", not sleeps, str(sleeps))
            check("logged out: one email to the owner", len(mail.OUTBOX) == 1, str(len(mail.OUTBOX)))
            if mail.OUTBOX:
                to, subject, body, _ = mail.OUTBOX[-1]
                check("email: to the pack recipient, says it is unlinked, has the steps",
                      to == ["owner@example.com"] and "unlinked" in subject
                      and "re-link with these steps" in body and "restart wa" in body
                      and "logs -f wa" in body and "cli.js pair" in body, body[:400])
                check("email: token not in it", TOKEN not in body)
            code, out = run(["--date", "2026-10-08"])
            check("second failure same day: exit 1, no second email",
                  code == 1 and len(mail.OUTBOX) == 1 and "already alerted" in out, out)
            code, out = run(["--date", "2026-10-09"])
            check("next day: alerted again", code == 1 and len(mail.OUTBOX) == 2, out)
            check("not marked as posted", not daily_state.sent(W.JOB, dt.date(2026, 10, 8)))

            # Connected at /status but dropped by the time of the post -> 409.
            stub.connected = True
            stub.statuses = [{"connected": True}]
            orig = stub.__call__

            def drop_after_status(req: httpx.Request) -> httpx.Response:
                if req.url.path == "/channel/post":
                    stub.connected, stub.reason = False, "reconnecting"
                return orig(req)
            with patch.object(W, "_transport", httpx.MockTransport(drop_after_status)):
                code, out = run(["--date", "2026-10-10"])
            check("409 on post: treated as unlinked, exit 1, emailed",
                  code == 1 and len(mail.OUTBOX) == 3, out)

            # Transient reconnect: waits, then posts.
            stub.connected, stub.reason = True, None
            stub.statuses = [{"connected": False, "reason": "reconnecting"},
                             {"connected": False, "reason": "reconnecting"}]
            n = len(stub.posts)
            code, out = run(["--date", "2026-10-11"])
            check("reconnecting: waits, then posts", code == 0 and len(stub.posts) == n + 1
                  and len(sleeps) == 2, f"{out} sleeps={sleeps}")
            with patch.dict(os.environ, {"ASTRO_WA_WAIT": "0"}):
                stub.statuses = [{"connected": False, "reason": "reconnecting"}]
                code, out = run(["--date", "2026-10-12"])
                check("reconnecting past the wait: exit 1 + email",
                      code == 1 and len(mail.OUTBOX) == 4, out)

            stub.down = True
            code, out = run(["--date", "2026-10-13"])
            stub.down = False
            check("connector unreachable: exit 1 + email",
                  code == 1 and "unreachable" in out and len(mail.OUTBOX) == 5, out)

        print("\n4. Misconfiguration")
        with patch.dict(os.environ, {**ENV, "ASTRO_WA_TOKEN": "wrong-token"}):
            n = len(mail.OUTBOX)
            code, out = run(["--date", "2026-10-14"])
            check("wrong token: exit 1, explains, no 'unlinked' email",
                  code == 1 and "ASTRO_WA_TOKEN" in out and len(mail.OUTBOX) == n, out)
        with patch.dict(os.environ, {**ENV, "ASTRO_WA_CHANNEL_LINK": LINK + "Y"}):
            stub.role = "SUBSCRIBER"
            code, out = run(["--date", "2026-10-15"])
            stub.role = "OWNER"
            check("number is not the channel owner: exit 1, not cached",
                  code == 1 and "owner/admin" in out
                  and (daily_state.recall(W.JOB, "channel") or {}).get("link") != LINK + "Y", out)

    print("\n5. Secrets")
    joined = "\n".join(all_out)
    check("token never printed in any run", TOKEN not in joined)
    check("token never in the email outbox", all(TOKEN not in m[2] for m in mail.OUTBOX))
    state_files = "".join(p.read_text(encoding="utf-8")
                          for p in Path(os.environ["ASTRO_DAILY_STATE_DIR"]).glob("*.json"))
    check("token never in the state files", TOKEN not in state_files)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("whatsapp channel — all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
