"""UPI collection with manual verification.

Why this exists: payment aggregators classify astrology as high-risk and refuse
onboarding. UPI needs nobody's approval — the customer pays your VPA directly
from any UPI app, and you confirm it against your bank statement.

The trade-off is honest and worth stating plainly: **this is manual**. Nothing
here can verify a payment on its own. The customer tells us they paid and gives
a UTR; a human checks the bank statement and approves. That is fine at tens of
orders a day and untenable at hundreds — by which point a real gateway should
have approved.

Two design rules follow from that:

* **A claimed payment grants nothing.** Submitting a UTR only moves the order to
  `awaiting_verification`. Credits appear when a human approves. Otherwise
  anyone could type twelve digits and get free questions.
* **A UTR may be used once, globally.** The unique index on `utr` is what stops
  the same reference being submitted against several orders.
"""

from __future__ import annotations

import base64
import io
import os
import re
import urllib.parse

# The payee. UPI_VPA is the only value that must be set for this to work.
VPA = os.environ.get("ASTRO_UPI_VPA", "")
PAYEE = os.environ.get("ASTRO_UPI_PAYEE", os.environ.get("ASTRO_LEGAL_NAME", "Divine Astro"))

# UTRs (Unique Transaction References) are 12 digits on UPI. Some banks show a
# longer RRN; accept 10-22 alphanumerics and normalise, rather than rejecting a
# customer who pasted exactly what their app showed them.
UTR_RE = re.compile(r"^[A-Za-z0-9]{10,22}$")


def configured() -> bool:
    return bool(VPA)


def normalise_utr(raw: str) -> str:
    return re.sub(r"[\s-]", "", (raw or "")).upper()


def valid_utr(raw: str) -> bool:
    return bool(UTR_RE.match(normalise_utr(raw)))


def reference(order_id: int) -> str:
    """Short human-quotable reference the customer puts in the payment note."""
    return f"DA{order_id:06d}"


def payment_link(order_id: int, amount_paise: int) -> str:
    """A UPI deep link. Opens the customer's UPI app with everything prefilled.

    On a phone this is a tappable link; on a desktop it becomes the QR below.
    """
    params = {
        "pa": VPA,
        "pn": PAYEE,
        "am": f"{amount_paise / 100:.2f}",
        "cu": "INR",
        "tn": f"Divine Astro {reference(order_id)}",
        "tr": reference(order_id),
    }
    return "upi://pay?" + urllib.parse.urlencode(params)


def qr_data_uri(order_id: int, amount_paise: int) -> str:
    """The same link as a QR image, inlined so the page makes no extra request."""
    import qrcode
    from qrcode.constants import ERROR_CORRECT_M

    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M,
                       box_size=8, border=2)
    qr.add_data(payment_link(order_id, amount_paise))
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0d1024", back_color="#ffffff")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def instructions(order_id: int, amount_paise: int) -> dict:
    """Everything the checkout screen needs to show."""
    return {
        "mode": "upi_manual",
        "vpa": VPA,
        "payee": PAYEE,
        "amount": amount_paise,
        "amount_rupees": f"{amount_paise / 100:.2f}".rstrip("0").rstrip("."),
        "reference": reference(order_id),
        "link": payment_link(order_id, amount_paise),
        "qr": qr_data_uri(order_id, amount_paise),
        "steps": [
            f"Pay ₹{amount_paise / 100:.0f} to {VPA} using any UPI app.",
            f"Put the reference {reference(order_id)} in the payment note.",
            "Copy the UTR / transaction reference your app shows after paying.",
            "Enter it below. We verify against our bank statement and add your "
            "questions — usually within a few hours.",
        ],
    }
