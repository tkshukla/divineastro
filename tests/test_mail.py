"""Admin mail: the SMTP wrapper itself, and its one call site.

Two things need checking, and they need different setups:

1. `app.mail.send()` is a pure function — mock `smtplib.SMTP` and check what
   it would have sent, no network needed.
2. `submit_utr()`'s wiring is in-process against a real (SQLite) DB session,
   the same way `test_remedies_doshas.py` builds fixtures directly rather
   than through HTTP — `test_upi.py`'s HTTP-level suite drives a *separate*
   server process, so monkeypatching `app.mail.send` from a test script
   cannot reach it; only an in-process call can.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_mail
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# The notification body includes a rupee sign; Windows consoles default to a
# cp1252 stdout that can't encode it, and the assertion below never gets to
# run its own PASS/FAIL check before that crashes the whole script.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app import mail

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def test_mail_module() -> None:
    print("\n1. app.mail.send() — pure unit tests")

    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("ASTRO_SMTP_HOST", None)
        check("unconfigured: returns False, does not raise",
              mail.send(["ops@example.com"], "subject", "body") is False)
        check("empty recipient list: returns False, does not raise",
              mail.send([], "subject", "body") is False)

    with patch.dict(os.environ, {
        "ASTRO_SMTP_HOST": "smtp.example.com", "ASTRO_SMTP_PORT": "587",
        "ASTRO_SMTP_USER": "bot@example.com", "ASTRO_SMTP_PASS": "secret",
        "ASTRO_MAIL_FROM": "Divine Astro <support@divineastro.org>",
    }):
        fake_smtp = MagicMock()
        fake_smtp.__enter__ = MagicMock(return_value=fake_smtp)
        fake_smtp.__exit__ = MagicMock(return_value=False)
        with patch("smtplib.SMTP", return_value=fake_smtp) as ctor:
            ok = mail.send(["ops@example.com", "owner@example.com"], "Test subject", "Test body")
            check("configured + mocked SMTP: returns True", ok is True)
            check("connects to the configured host/port",
                  ctor.call_args[0] == ("smtp.example.com", 587), str(ctor.call_args))
            check("logs in with the configured credentials",
                  fake_smtp.login.call_args[0] == ("bot@example.com", "secret"))
            sent = fake_smtp.send_message.call_args[0][0]
            check("subject carried through", sent["Subject"] == "Test subject", sent["Subject"])
            check("both recipients addressed", "ops@example.com" in sent["To"] and
                  "owner@example.com" in sent["To"], sent["To"])

        # A broken transport must not raise out of send() — the customer-
        # facing caller (submit_utr) depends on this never becoming a 500.
        with patch("smtplib.SMTP", side_effect=OSError("connection refused")):
            try:
                ok = mail.send(["ops@example.com"], "subject", "body")
                check("transport failure: returns False, does not raise", ok is False)
            except Exception as exc:
                check("transport failure: returns False, does not raise", False,
                      f"{type(exc).__name__}: {exc}")


def test_submit_utr_wiring() -> None:
    print("\n2. submit_utr() calls mail.send() exactly once per claim")

    import random

    from app import api_account
    from app.db import Order, OrderStatus, User, session as db_session

    email = f"mailtest{random.randint(10000, 99999)}@example.com"
    with db_session() as db:
        user = User(email=email, name="Mail Test", provider="dev", provider_sub=email)
        db.add(user)
        db.flush()

        order = Order(
            user_id=user.id, sku="q10", title="10 Questions", amount_paise=11100,
            credits=10, status=OrderStatus.created, provider="upi_manual",
        )
        db.add(order)
        db.commit()
        db.refresh(user)
        db.refresh(order)

        calls = []
        with patch.object(api_account.mail, "send",
                          side_effect=lambda *a, **k: calls.append((a, k)) or True):
            with patch.dict(os.environ, {"ASTRO_ADMIN_EMAILS": "owner@divineastro.org"}):
                body = api_account.UtrIn(order_id=order.id, utr=str(random.randint(10**11, 10**12 - 1)))
                result = api_account.submit_utr(body, user=user, db=db)

        check("claim succeeded", result.get("ok") is True, str(result))
        check("mail.send called exactly once", len(calls) == 1, f"called {len(calls)} times")
        if calls:
            args, _ = calls[0]
            to, subject, msg_body = args
            check("admin recipient list used", to == ["owner@divineastro.org"], str(to))
            check("subject names the order", str(order.id) in subject, subject)
            check("body carries the buyer's email and the UTR",
                  email in msg_body and body.utr in msg_body, msg_body)

        # A second claim on an already-verified order (the early-return
        # branch) must not fire a second notification.
        db.refresh(order)
        order.status = OrderStatus.paid
        db.commit()
        calls.clear()
        with patch.object(api_account.mail, "send",
                          side_effect=lambda *a, **k: calls.append((a, k)) or True):
            api_account.submit_utr(
                api_account.UtrIn(order_id=order.id, utr=body.utr), user=user, db=db)
        check("no second notification once already paid", len(calls) == 0, f"called {len(calls)} times")


def main() -> int:
    print("Admin mail (app.mail + submit_utr wiring)")
    test_mail_module()
    test_submit_utr_wiring()

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("admin mail — all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
