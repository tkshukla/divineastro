"""Products, credit grants and Razorpay integration.

Money is handled with two rules:

* **Amounts are integers in paise.** Never floats. ₹111 is 11100.
* **Granting credits is idempotent.** Both the browser callback and the webhook
  can confirm the same payment; whichever arrives first grants, the second is a
  no-op. Razorpay retries webhooks, so this is not optional.

Razorpay keys come from RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET, and the webhook
secret from RAZORPAY_WEBHOOK_SECRET. With no keys set the module runs in **test
mode**: orders are created locally and can be confirmed without a real payment,
so the whole flow is developable before KYC completes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import coupons, gateways
from .db import (
    Coupon, CreditEntry, EntryKind, FulfilStatus, Order, OrderStatus,
    WebhookEvent, grant, utcnow,
)

FREE_QUESTIONS = int(os.environ.get("ASTRO_FREE_QUESTIONS", "10"))

# Fulfilment promise shown to the customer at checkout and on the order.
ASTROLOGER = os.environ.get("ASTRO_ASTROLOGER", "Pandit Shukla")
TURNAROUND_DAYS = int(os.environ.get("ASTRO_TURNAROUND_DAYS", "10"))


def live() -> bool:
    return gateways.active().key != "test"


# --------------------------------------------------------------------------
# Catalogue
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Product:
    sku: str
    title: str
    title_hi: str
    amount_paise: int
    credits: int
    kind: str                 # 'questions' | 'kundali'
    blurb: str
    blurb_hi: str
    pages: int = 0
    highlight: bool = False

    @property
    def rupees(self) -> int:
        return self.amount_paise // 100

    @property
    def per_question(self) -> float | None:
        return round(self.amount_paise / 100 / self.credits, 2) if self.credits else None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["rupees"] = self.rupees
        d["per_question"] = self.per_question
        return d


# PRICING LADDER: each larger pack must cost less per question than the one
# below it, or a customer who does the arithmetic buys two small packs instead.
#   10  → ₹111  = ₹11.10 each
#   50  → ₹351  = ₹7.02 each
#   100 → ₹651  = ₹6.51 each   (₹751 would have been ₹7.51 — dearer than the 50)
PRODUCTS: dict[str, Product] = {p.sku: p for p in [
    Product("q10", "10 Questions", "10 प्रश्न", 11100, 10, "questions",
            "Ten questions on any chart you have saved.",
            "अपनी किसी भी सहेजी हुई कुंडली पर दस प्रश्न।"),
    Product("q50", "50 Questions", "50 प्रश्न", 35100, 50, "questions",
            "Best value per question. Ask across career, marriage, health and timing.",
            "प्रति प्रश्न सर्वोत्तम मूल्य। करियर, विवाह, स्वास्थ्य और समय पर पूछें।",
            highlight=True),
    Product("q100", "100 Questions", "100 प्रश्न", 65100, 100, "questions",
            "For a full year of consultation.",
            "पूरे वर्ष के परामर्श के लिए।"),

    Product("k3", "Hand-written Kundali — 3 pages", "हस्तलिखित कुंडली — 3 पृष्ठ",
            11100, 0, "kundali",
            "Three pages written by hand by our astrologer, delivered as a scanned PDF.",
            "हमारे ज्योतिषी द्वारा हाथ से लिखे तीन पृष्ठ, स्कैन की गई PDF के रूप में।",
            pages=3),
    Product("k5", "Hand-written Kundali — 5 pages", "हस्तलिखित कुंडली — 5 पृष्ठ",
            35100, 0, "kundali",
            "Five pages, covering dashas and remedies in depth. Scanned PDF.",
            "पाँच पृष्ठ, दशा और उपायों सहित विस्तृत। स्कैन की गई PDF।",
            pages=5),
    Product("k3q3", "Hand-written Kundali + 3 Questions", "हस्तलिखित कुंडली + 3 प्रश्न",
            110000, 3, "kundali",
            "Three hand-written pages plus three questions answered personally.",
            "तीन हस्तलिखित पृष्ठ और तीन प्रश्नों के व्यक्तिगत उत्तर।",
            pages=3, highlight=True),
]}


def catalogue(kind: str | None = None) -> list[dict]:
    return [p.to_dict() for p in PRODUCTS.values() if kind is None or p.kind == kind]


# --------------------------------------------------------------------------
# Order creation
# --------------------------------------------------------------------------

def create_order(db: Session, user, sku: str, birth_id: int | None = None,
                 coupon_code: str | None = None) -> tuple[Order, dict]:
    """Create the local order, then ask the active gateway to open a session.

    A coupon is priced here, once, and the result is frozen onto the order:
    the gateway is asked for exactly `amount_paise`, and `credits` already
    includes any extra_credits bonus. Editing the coupon afterwards therefore
    cannot change what an order in flight charges or pays out.
    """
    product = PRODUCTS.get(sku)
    if product is None:
        raise ValueError(f"Unknown product '{sku}'")

    coupon = None
    discount = bonus = 0
    if coupon_code and coupon_code.strip():
        coupon, message, discount, bonus = coupons.validate(
            db, coupon_code, user, product)
        if coupon is None:
            raise ValueError(message or "That coupon cannot be used.")

    gateway = gateways.active()
    order = Order(
        user_id=user.id,
        sku=product.sku,
        title=product.title,
        amount_paise=product.amount_paise - discount,
        original_amount_paise=product.amount_paise,
        discount_paise=discount,
        coupon_id=coupon.id if coupon else None,
        credits=product.credits + bonus,
        birth_id=birth_id,
        fulfilment=(FulfilStatus.pending if product.kind == "kundali"
                    else FulfilStatus.not_applicable),
        provider=gateway.key,
    )
    db.add(order)
    db.flush()   # assign order.id so the gateway receipt can reference it

    checkout = gateway.create(order, user)
    db.commit()
    return order, checkout


# --------------------------------------------------------------------------
# Confirmation — idempotent
# --------------------------------------------------------------------------

def _already_granted(db: Session, order: Order) -> bool:
    return db.execute(
        select(CreditEntry.id).where(CreditEntry.order_id == order.id)
    ).first() is not None


def _bonus_credits(order: Order) -> int:
    """Credits on the order beyond the pack's own — an extra_credits coupon."""
    product = PRODUCTS.get(order.sku)
    base = product.credits if product else 0
    return max(0, int(order.credits or 0) - base)


def mark_paid(db: Session, order: Order, payment_id: str) -> tuple[bool, str]:
    """Mark an order paid and grant its credits, at most once.

    Returns (granted_now, message). Calling it twice for the same order is safe
    — the second call reports that it was already applied and grants nothing.
    """
    if order.status == OrderStatus.paid and _already_granted(db, order):
        return False, "Payment already recorded."

    order.status = OrderStatus.paid
    # Keep NULL rather than "" when a gateway gives us no payment id, so the
    # (provider, payment_id) uniqueness stays meaningful.
    order.provider_payment_id = payment_id or order.provider_payment_id or None
    order.paid_at = utcnow()

    # order.credits is already pack + any extra_credits bonus (frozen at order
    # creation), so this stays a SINGLE ledger row — which is exactly what
    # _already_granted keys off. Splitting it in two would break that.
    if order.credits and not _already_granted(db, order):
        bonus = _bonus_credits(order)
        note = f"{order.title} ({order.sku})"
        if bonus:
            note += f" +{bonus} bonus"
        grant(db, order.user_id, order.credits, EntryKind.purchase,
              note=note[:255], order_id=order.id)

    # Independently idempotent (UNIQUE on coupon_redemptions.order_id), which
    # matters for kundali orders: they grant no credits, so _already_granted is
    # never true for them and this path can legitimately run more than once.
    if order.coupon_id:
        coupon = db.get(Coupon, order.coupon_id)
        if coupon is not None:
            coupons.redeem(db, coupon, order.user_id, order, order.discount_paise)

    db.commit()
    return True, "Payment recorded."


def verify_return(payload: dict) -> bool:
    """Verify a browser-side return from the active gateway."""
    return gateways.active().verify_return(payload)


def handle_webhook(db: Session, body: bytes, headers) -> dict:
    """Process a gateway webhook: record it, verify it, then grant once.

    The webhook is authoritative. The browser callback only improves the
    user's experience — for Cashfree it carries no signature at all and is
    deliberately never trusted on its own.
    """
    gateway = gateways.active()
    ok, provider_order_id, payment_id = gateway.parse_webhook(body, headers)

    event_id = payment_id or provider_order_id
    if event_id and not db.execute(
        select(WebhookEvent.id).where(WebhookEvent.event_id == event_id)
    ).first():
        db.add(WebhookEvent(
            provider=gateway.key, event_id=event_id, event_type="payment",
            payload=body.decode("utf-8", "replace"), verified=ok))
        db.commit()

    if not ok:
        return {"ok": False, "reason": "bad signature or unpaid"}

    order = db.execute(
        select(Order).where(Order.provider_order_id == provider_order_id)
    ).scalar_one_or_none()
    if order is None:
        return {"ok": False, "reason": "unknown order"}

    granted, message = mark_paid(db, order, payment_id)
    return {"ok": True, "granted": granted, "message": message, "order_id": order.id}
