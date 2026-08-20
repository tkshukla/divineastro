"""Payment gateway adapters.

The gateway is a swappable component, chosen with ASTRO_GATEWAY. That matters
here because gateway choice in India is driven by *onboarding*, not features —
and onboarding rules change. Nothing above this file knows which one is active.

    test        no gateway; orders confirm locally. Default until keys exist.
    instamojo   Instamojo (hosted redirect; accepts categories others decline)
    paytm       Paytm Payment Gateway (checksum-signed, JS Checkout)
    cashfree    Cashfree (clean API, but restricts astrology)
    razorpay    Razorpay
    upi_manual  direct UPI, settled by a human against the bank statement

Every adapter implements three things:

    create(order, user)      -> dict handed to the browser to open checkout
    verify_return(payload)   -> bool, is this browser callback authentic
    parse_webhook(body, hdr) -> (ok, provider_order_id, provider_payment_id)

Notes for whoever picks:
* **Paytm** requires an MID and a merchant key; individual/proprietor onboarding
  is possible but its KYC is the heaviest of the three.
* **Cashfree** is usually the least painful for a sole individual with PAN and a
  savings account, and its API is the simplest here.
* **Razorpay** also onboards individuals and has the best documentation.
All three support UPI, cards, netbanking and wallets, so the customer-facing
payment options are effectively identical.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from typing import Protocol

# Cashfree is the default: of the three it has the lightest onboarding for a
# sole individual with PAN and a savings account, and its API needs no
# server-side token-minting leg before checkout can open.
GATEWAY = os.environ.get("ASTRO_GATEWAY", "cashfree").lower()


class Gateway(Protocol):
    key: str
    label: str

    def configured(self) -> bool: ...
    def create(self, order, user) -> dict: ...
    def verify_return(self, payload: dict) -> bool: ...
    def parse_webhook(self, body: bytes, headers) -> tuple[bool, str, str]: ...


# --------------------------------------------------------------------------
# Test gateway — no credentials, confirms locally
# --------------------------------------------------------------------------

class TestGateway:
    key, label = "test", "Test mode"

    def configured(self) -> bool:
        return True

    def create(self, order, user) -> dict:
        order.provider_order_id = f"test_order_{order.id}"
        return {"mode": "test", "order_id": order.provider_order_id,
                "amount": order.amount_paise}

    def verify_return(self, payload: dict) -> bool:
        return True

    def parse_webhook(self, body: bytes, headers) -> tuple[bool, str, str]:
        data = json.loads(body or b"{}")
        return True, data.get("order_id", ""), data.get("payment_id", "")


# --------------------------------------------------------------------------
# Paytm
# --------------------------------------------------------------------------

class UpiManualGateway:
    """Direct UPI collection, confirmed by a human against the bank statement.

    There is no automated confirmation path at all, which is the point: it needs
    no aggregator approval. `verify_return` therefore always returns False, so
    the ordinary browser-callback route can never grant credits — the dedicated
    admin verification endpoint is the only way an order becomes paid.
    """

    key, label = "upi_manual", "UPI (manual verification)"

    def configured(self) -> bool:
        from . import upi

        return upi.configured()

    def create(self, order, user) -> dict:
        from . import upi

        order.provider_order_id = upi.reference(order.id)
        return upi.instructions(order.id, order.amount_paise)

    def verify_return(self, payload: dict) -> bool:
        return False        # nothing the browser says can settle a UPI payment

    def parse_webhook(self, body: bytes, headers) -> tuple[bool, str, str]:
        return False, "", ""    # no webhooks exist for this method


class PaytmGateway:
    key, label = "paytm", "Paytm"

    def __init__(self) -> None:
        self.mid = os.environ.get("PAYTM_MID", "")
        self.secret = os.environ.get("PAYTM_MERCHANT_KEY", "")
        self.website = os.environ.get("PAYTM_WEBSITE", "DEFAULT")
        self.host = os.environ.get(
            "PAYTM_HOST",
            "https://securegw-stage.paytm.in" if os.environ.get("PAYTM_STAGING", "1") == "1"
            else "https://securegw.paytm.in",
        )
        self.callback = os.environ.get("PAYTM_CALLBACK_URL", "")

    def configured(self) -> bool:
        return bool(self.mid and self.secret)

    # Paytm signs with AES-128-CBC over a salted SHA-256 hash. The algorithm is
    # theirs; it is implemented here rather than pulled in as a dependency
    # because their SDK is a thin wrapper over exactly this.
    def _checksum(self, payload: str) -> str:
        from Crypto.Cipher import AES          # pycryptodome

        salt = base64.b64encode(os.urandom(4)).decode()[:4]
        digest = hashlib.sha256(f"{payload}|{salt}".encode()).hexdigest()
        plain = digest + salt
        pad = 16 - len(plain) % 16
        plain += chr(pad) * pad
        cipher = AES.new(self.secret.encode()[:16], AES.MODE_CBC, b"@@@@&&&&####$$$$")
        return base64.b64encode(cipher.encrypt(plain.encode())).decode()

    def _verify_checksum(self, payload: str, checksum: str) -> bool:
        from Crypto.Cipher import AES

        try:
            cipher = AES.new(self.secret.encode()[:16], AES.MODE_CBC, b"@@@@&&&&####$$$$")
            decoded = cipher.decrypt(base64.b64decode(checksum)).decode(errors="ignore")
            decoded = decoded[: -ord(decoded[-1])] if decoded else ""
            salt = decoded[-4:]
            expected = hashlib.sha256(f"{payload}|{salt}".encode()).hexdigest() + salt
            return hmac.compare_digest(expected, decoded)
        except Exception:
            return False

    @staticmethod
    def _canonical(params: dict) -> str:
        return "|".join(str(params[k]) for k in sorted(params) if params[k] not in (None, ""))

    def create(self, order, user) -> dict:
        order.provider_order_id = f"GD{order.id:08d}"
        body = {
            "requestType": "Payment",
            "mid": self.mid,
            "websiteName": self.website,
            "orderId": order.provider_order_id,
            "callbackUrl": self.callback,
            "txnAmount": {"value": f"{order.amount_paise / 100:.2f}", "currency": "INR"},
            "userInfo": {"custId": f"user{user.id}", "email": user.email or "",
                         "firstName": user.name or ""},
        }
        signature = self._checksum(json.dumps(body, separators=(",", ":")))
        return {
            "mode": "paytm", "mid": self.mid, "host": self.host,
            "order_id": order.provider_order_id, "amount": order.amount_paise,
            "body": body, "signature": signature,
            "note": "Exchange this for a txnToken server-side via /theia/api/v1/initiateTransaction.",
        }

    def verify_return(self, payload: dict) -> bool:
        checksum = payload.get("CHECKSUMHASH") or payload.get("signature") or ""
        data = {k: v for k, v in payload.items() if k not in ("CHECKSUMHASH", "signature")}
        return self._verify_checksum(self._canonical(data), checksum)

    def parse_webhook(self, body: bytes, headers) -> tuple[bool, str, str]:
        data = json.loads(body or b"{}")
        checksum = data.pop("CHECKSUMHASH", "") or headers.get("X-Paytm-Signature", "")
        ok = self._verify_checksum(self._canonical(data), checksum)
        paid = str(data.get("STATUS", "")).upper() in ("TXN_SUCCESS", "SUCCESS")
        return (ok and paid), data.get("ORDERID", ""), data.get("TXNID", "")


# --------------------------------------------------------------------------
# Cashfree
# --------------------------------------------------------------------------

class CashfreeGateway:
    key, label = "cashfree", "Cashfree"

    def __init__(self) -> None:
        self.app_id = os.environ.get("CASHFREE_APP_ID", "")
        self.secret = os.environ.get("CASHFREE_SECRET_KEY", "")
        self.host = os.environ.get(
            "CASHFREE_HOST",
            "https://sandbox.cashfree.com/pg" if os.environ.get("CASHFREE_SANDBOX", "1") == "1"
            else "https://api.cashfree.com/pg",
        )
        self.return_url = os.environ.get("CASHFREE_RETURN_URL", "")

    def configured(self) -> bool:
        return bool(self.app_id and self.secret)

    def create(self, order, user) -> dict:
        import httpx

        order.provider_order_id = f"GD{order.id:08d}"
        resp = httpx.post(
            f"{self.host}/orders",
            headers={
                "x-client-id": self.app_id,
                "x-client-secret": self.secret,
                "x-api-version": "2023-08-01",
                "Content-Type": "application/json",
            },
            json={
                "order_id": order.provider_order_id,
                "order_amount": round(order.amount_paise / 100, 2),
                "order_currency": "INR",
                "customer_details": {
                    "customer_id": f"user{user.id}",
                    "customer_email": user.email or "noreply@example.com",
                    "customer_phone": user.phone or "9999999999",
                    "customer_name": user.name or "Customer",
                },
                "order_meta": {"return_url": self.return_url},
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "mode": "cashfree", "order_id": order.provider_order_id,
            "payment_session_id": data.get("payment_session_id"),
            "amount": order.amount_paise, "sandbox": "sandbox" in self.host,
        }

    def verify_return(self, payload: dict) -> bool:
        # Cashfree's browser return carries no signature — the order status must
        # be fetched server-side, so a return alone never grants credit.
        return False

    def parse_webhook(self, body: bytes, headers) -> tuple[bool, str, str]:
        signature = headers.get("x-webhook-signature", "")
        timestamp = headers.get("x-webhook-timestamp", "")
        expected = base64.b64encode(
            hmac.new(self.secret.encode(), (timestamp + body.decode()).encode(),
                     hashlib.sha256).digest()
        ).decode()
        ok = hmac.compare_digest(expected, signature)
        data = json.loads(body or b"{}").get("data", {})
        order_id = (data.get("order") or {}).get("order_id", "")
        payment = data.get("payment") or {}
        paid = str(payment.get("payment_status", "")).upper() == "SUCCESS"
        return (ok and paid), order_id, str(payment.get("cf_payment_id", ""))


# --------------------------------------------------------------------------
# Instamojo
# --------------------------------------------------------------------------

class InstamojoGateway:
    """Instamojo Payment Requests (API v1.1).

    Chosen because its onboarding accepts categories the larger aggregators
    decline. The flow is a plain redirect to a hosted page, so there is no JS
    SDK to load and nothing to break in the browser.

    Unlike Cashfree, `verify_return` here is *authoritative*: the browser return
    is unsigned, so this adapter ignores what the browser claims and asks
    Instamojo's API directly whether that payment is in Credit. The webhook
    remains as a backup for customers who close the tab before returning.
    """

    key, label = "instamojo", "Instamojo"

    def __init__(self) -> None:
        self.api_key = os.environ.get("INSTAMOJO_API_KEY", "")
        self.auth_token = os.environ.get("INSTAMOJO_AUTH_TOKEN", "")
        self.salt = os.environ.get("INSTAMOJO_SALT", "")
        self.host = os.environ.get(
            "INSTAMOJO_HOST",
            "https://test.instamojo.com/api/1.1"
            if os.environ.get("INSTAMOJO_SANDBOX", "0") == "1"
            else "https://www.instamojo.com/api/1.1",
        )
        self.redirect_url = os.environ.get("INSTAMOJO_REDIRECT_URL", "")
        self.webhook_url = os.environ.get("INSTAMOJO_WEBHOOK_URL", "")

    def configured(self) -> bool:
        return bool(self.api_key and self.auth_token)

    def _headers(self) -> dict:
        return {"X-Api-Key": self.api_key, "X-Auth-Token": self.auth_token}

    def create(self, order, user) -> dict:
        import httpx

        # Instamojo rejects requests under ₹9 and truncates `purpose` at 30
        # characters, so both are clamped here rather than failing at their end.
        resp = httpx.post(
            f"{self.host}/payment-requests/",
            headers=self._headers(),
            data={
                "purpose": (order.title or "Divine Astro")[:30],
                "amount": f"{max(order.amount_paise, 900) / 100:.2f}",
                "buyer_name": user.name or "Customer",
                "email": user.email or "",
                "phone": user.phone or "",
                "redirect_url": self.redirect_url,
                "webhook": self.webhook_url,
                "send_email": "false",
                "send_sms": "false",
                "allow_repeated_payments": "false",
            },
            timeout=25,
        )
        # raise_for_status() discards the body, and with Instamojo the body is
        # the only part that says *why*. A 403 here means the account is not
        # permitted to create payment requests — activation or plan, not us.
        if resp.status_code >= 400:
            try:
                said = resp.json().get("message") or resp.text
            except Exception:
                said = resp.text
            if resp.status_code in (401, 403):
                raise RuntimeError(
                    f"Instamojo rejected the request ({resp.status_code}): {said} "
                    "The API credentials authenticate, but the account is not "
                    "permitted to create payment requests — check that the "
                    "Instamojo account is fully activated for collecting payments."
                )
            raise RuntimeError(f"Instamojo error {resp.status_code}: {said}")

        data = resp.json()
        if not data.get("success"):
            raise RuntimeError(f"Instamojo refused the request: {data}")

        pr = data["payment_request"]
        order.provider_order_id = pr["id"]
        return {
            "mode": "instamojo", "order_id": pr["id"], "url": pr["longurl"],
            "amount": order.amount_paise, "sandbox": "test.instamojo" in self.host,
        }

    def verify_return(self, payload: dict) -> bool:
        """Ask Instamojo directly. Nothing the browser asserts is trusted."""
        import httpx

        request_id = payload.get("payment_request_id", "")
        payment_id = payload.get("payment_id", "")
        if not (request_id and payment_id and self.configured()):
            return False
        try:
            resp = httpx.get(
                f"{self.host}/payment-requests/{request_id}/{payment_id}/",
                headers=self._headers(), timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return False        # unreachable API → fall through to 'pending'

        if not data.get("success"):
            return False
        payment = ((data.get("payment_request") or {}).get("payment") or {})
        return str(payment.get("status", "")) == "Credit"

    def parse_webhook(self, body: bytes, headers) -> tuple[bool, str, str]:
        """Instamojo posts form-encoded fields with an HMAC-SHA1 `mac`.

        The MAC is taken over every other field's value, ordered by field name
        and joined with '|'. Without the Private Salt configured this returns
        False rather than trusting an unsigned post.
        """
        from urllib.parse import parse_qsl

        if not self.salt:
            return False, "", ""

        data = dict(parse_qsl(body.decode(errors="ignore")))
        mac = data.pop("mac", "")
        message = "|".join(data[k] for k in sorted(data, key=lambda s: s.lower()))
        expected = hmac.new(self.salt.encode(), message.encode(), hashlib.sha1).hexdigest()

        ok = hmac.compare_digest(expected, mac.lower())
        paid = str(data.get("status", "")) == "Credit"
        return (ok and paid), data.get("payment_request_id", ""), data.get("payment_id", "")


# --------------------------------------------------------------------------
# Razorpay
# --------------------------------------------------------------------------

class RazorpayGateway:
    key, label = "razorpay", "Razorpay"

    def __init__(self) -> None:
        self.key_id = os.environ.get("RAZORPAY_KEY_ID", "")
        self.secret = os.environ.get("RAZORPAY_KEY_SECRET", "")
        self.webhook_secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")

    def configured(self) -> bool:
        return bool(self.key_id and self.secret)

    def create(self, order, user) -> dict:
        import razorpay

        rp = razorpay.Client(auth=(self.key_id, self.secret)).order.create({
            "amount": order.amount_paise, "currency": "INR",
            "receipt": f"gd-{order.id}",
            "notes": {"sku": order.sku, "user_id": str(order.user_id)},
        })
        order.provider_order_id = rp["id"]
        return {
            "mode": "razorpay", "key_id": self.key_id, "order_id": rp["id"],
            "amount": order.amount_paise, "currency": "INR",
            "prefill": {"email": user.email, "name": user.name, "contact": user.phone},
        }

    def verify_return(self, payload: dict) -> bool:
        expected = hmac.new(
            self.secret.encode(),
            f"{payload.get('razorpay_order_id','')}|{payload.get('razorpay_payment_id','')}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, payload.get("razorpay_signature", ""))

    def parse_webhook(self, body: bytes, headers) -> tuple[bool, str, str]:
        signature = headers.get("X-Razorpay-Signature", "")
        ok = bool(self.webhook_secret) and hmac.compare_digest(
            hmac.new(self.webhook_secret.encode(), body, hashlib.sha256).hexdigest(),
            signature,
        )
        payload = json.loads(body or b"{}")
        entity = (((payload.get("payload") or {}).get("payment") or {}).get("entity") or {})
        paid = payload.get("event") in ("payment.captured", "order.paid")
        return (ok and paid), entity.get("order_id", ""), entity.get("id", "")


# --------------------------------------------------------------------------
# Selection
# --------------------------------------------------------------------------

# Order matters for the auto-pick fallback below: a real aggregator is
# preferred over manual UPI, because manual costs you human time per order.
_ALL = {g.key: g for g in (
    InstamojoGateway(), PaytmGateway(), CashfreeGateway(), RazorpayGateway(),
    UpiManualGateway(),
)}
_TEST = TestGateway()


def active() -> Gateway:
    """The configured gateway, or the test one when nothing is set up yet."""
    if GATEWAY in _ALL and _ALL[GATEWAY].configured():
        return _ALL[GATEWAY]
    if GATEWAY in _ALL:                      # named but missing credentials
        return _TEST
    for gateway in _ALL.values():            # otherwise take whatever is ready
        if gateway.configured():
            return gateway
    return _TEST


def status() -> dict:
    current = active()
    return {
        "gateway": current.key,
        "label": current.label,
        "live": current.key != "test",
        "available": [
            {"key": g.key, "label": g.label, "configured": g.configured()}
            for g in _ALL.values()
        ],
    }
