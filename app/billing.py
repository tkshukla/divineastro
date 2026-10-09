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

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import coupons, gateways
from .db import (
    Coupon, CreditEntry, EntryKind, FulfilStatus, Order, OrderStatus,
    WebhookEvent, grant, utcnow,
)

log = logging.getLogger("astro.billing")

# The free questions a NEW account is given (DIVASTRO-154: 3, was 10). The one value
# every grant (auth, email_auth, phone_auth, the admin's manual customer) and every
# display (/api/me, /api/products, /pricing, the daily posts, the app's strings via
# {n}) reads. Changing it only affects accounts created afterwards: credits already
# granted are ledger rows (credit_entries) and are never touched.
FREE_QUESTIONS = int(os.environ.get("ASTRO_FREE_QUESTIONS", "3"))

# Fulfilment promise shown to the customer at checkout and on the order.
ASTROLOGER = os.environ.get("ASTRO_ASTROLOGER", "Pandit Shukla")
TURNAROUND_DAYS = int(os.environ.get("ASTRO_TURNAROUND_DAYS", "10"))


def live() -> bool:
    return gateways.active().key != "test"


# --------------------------------------------------------------------------
# Catalogue
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# The Diwali offer: a real, time-boxed price
#
# Every product has two prices. `list_paise` is the regular price the site
# charges once the offer is over. `offer_paise` is the limited-offer price.
# The price in force is computed from the clock, never stored:
#
#   offer active  (now < ends_at, and not switched off)  -> offer_paise
#   otherwise                                              -> list_paise
#
# so the price flips by itself at the end instant, with no manual step. The
# struck-through "was" price shown to customers is list_paise and only while
# the offer is active, which is exactly what is charged afterwards.
# See HANDOVER.md "Diwali offer" for the honesty rules.
# --------------------------------------------------------------------------

OFFER_NAME = "Diwali offer"
IST = timezone(timedelta(hours=5, minutes=30), "IST")
# 15 November 2026, 23:59:59 IST: the offer is live strictly before this instant;
# at it and after, list prices apply.
OFFER_END_DEFAULT = datetime(2026, 11, 15, 23, 59, 59, tzinfo=IST)


def _now() -> datetime:
    """The clock. Tests replace this to move time."""
    return datetime.now(timezone.utc)


def offer_ends_at() -> datetime | None:
    """When the offer ends (an aware datetime), or None if it cannot be
    determined. ASTRO_OFFER_ENDS (ISO 8601; a value without an offset is read
    as IST) moves the end without a deploy. An unreadable value is logged and
    the offer is treated as OVER: list prices are the safe failure, since they
    are what the site charges anyway."""
    raw = os.environ.get("ASTRO_OFFER_ENDS", "").strip()
    if not raw:
        return OFFER_END_DEFAULT
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        log.error("ASTRO_OFFER_ENDS=%r is not ISO 8601; the offer is OFF", raw)
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=IST)


def _killed() -> bool:
    return os.environ.get("ASTRO_OFFER_OFF", "").strip().lower() in ("1", "true", "yes", "on")


def offer_active(now: datetime | None = None) -> bool:
    if _killed():                      # the kill switch only ever ENDS the offer
        return False
    ends = offer_ends_at()
    if ends is None:
        return False
    now = now or _now()
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now < ends


def offer_status(now: datetime | None = None) -> dict:
    """{active, name, ends_at_iso, ends_at_label}. ends_at_* are None once the
    offer is not active, so nothing can advertise an end that has passed."""
    if not offer_active(now):
        return {"active": False, "name": OFFER_NAME,
                "ends_at_iso": None, "ends_at_label": None}
    ends = offer_ends_at().astimezone(IST)
    return {"active": True, "name": OFFER_NAME,
            "ends_at_iso": ends.isoformat(),
            "ends_at_label": f"{ends.day} {ends:%B %Y}, {ends:%H:%M} IST"}


def effective_price_paise(sku: str, now: datetime | None = None) -> int:
    """What a customer is charged for `sku` right now."""
    p = PRODUCTS[sku]
    return p.offer_paise if offer_active(now) else p.list_paise


@dataclass(frozen=True)
class Product:
    sku: str
    title: str
    title_hi: str
    offer_paise: int          # the limited-offer price
    credits: int
    kind: str                 # 'questions' | 'kundali'
    blurb: str
    blurb_hi: str
    pages: int = 0
    highlight: bool = False
    list_paise: int = 0       # the regular price, charged once the offer ends

    def price_paise(self, now: datetime | None = None) -> int:
        return self.offer_paise if offer_active(now) else self.list_paise

    @property
    def amount_paise(self) -> int:
        """The price in force right now. Read this (or price_paise(now)) for
        anything a customer is charged or shown; never offer_paise directly."""
        return self.price_paise()

    @property
    def rupees(self) -> int:
        return self.amount_paise // 100

    @property
    def per_question(self) -> float | None:
        return round(self.amount_paise / 100 / self.credits, 2) if self.credits else None

    def to_dict(self, now: datetime | None = None) -> dict:
        now = now or _now()                      # one instant for the whole dict
        active = offer_active(now)
        amount = self.price_paise(now)
        return {
            "sku": self.sku, "title": self.title, "title_hi": self.title_hi,
            "amount_paise": amount,
            "credits": self.credits, "kind": self.kind,
            "blurb": self.blurb, "blurb_hi": self.blurb_hi,
            "pages": self.pages, "highlight": self.highlight,
            "rupees": amount // 100,
            "per_question": round(amount / 100 / self.credits, 2) if self.credits else None,
            # The regular price, only while the offer is live (else null).
            "list_amount_paise": self.list_paise if active else None,
            "list_per_question": (round(self.list_paise / 100 / self.credits, 2)
                                  if active and self.credits else None),
            "offer": {"active": active, "name": OFFER_NAME,
                      "ends_at": offer_status(now)["ends_at_iso"]},
        }


# Regular prices, in paise: what the site charges after the offer. The
# offer_paise given in each Product() below is the Diwali offer price.
LIST_PRICES_PAISE = {
    "q10": 19900, "q50": 59900, "q100": 119900,
    "sq_career": 19900, "sq_marriage_timing": 19900, "sq_wealth_business": 19900,
    "life_book": 89900, "k3": 19900, "k5": 59900, "k3q3": 199900,
}


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
            "Fifty questions on any chart you have saved. Ask across career, marriage, health and timing.",
            "अपनी किसी भी सहेजी हुई कुंडली पर पचास प्रश्न। करियर, विवाह, स्वास्थ्य और समय पर पूछें।",
            highlight=True),
    Product("q100", "100 Questions", "100 प्रश्न", 65100, 100, "questions",
            "The lowest price per question: a hundred questions on any chart you have saved.",
            "सबसे कम प्रति-प्रश्न मूल्य: अपनी किसी भी सहेजी हुई कुंडली पर सौ प्रश्न।"),

    Product("k3", "Hand-written Kundali — 3 pages", "हस्तलिखित कुंडली — 3 पृष्ठ",
            11100, 0, "kundali",
            "Three pages written by hand by our astrologer, delivered as a scanned PDF.",
            "हमारे ज्योतिषी द्वारा हाथ से लिखे तीन पृष्ठ, स्कैन की गई PDF के रूप में।",
            pages=3),
    Product("k5", "Hand-written Kundali — 5 pages", "हस्तलिखित कुंडली — 5 पृष्ठ",
            35100, 0, "kundali",
            "Five hand-written pages covering dashas and remedies, delivered as a scanned PDF.",
            "दशा और उपायों सहित पाँच हस्तलिखित पृष्ठ, स्कैन की गई PDF के रूप में।",
            pages=5),
    Product("k3q3", "Hand-written Kundali + 3 Questions", "हस्तलिखित कुंडली + 3 प्रश्न",
            110000, 3, "kundali",
            "Three hand-written pages, plus 3 questions added to your question balance.",
            "तीन हस्तलिखित पृष्ठ, और आपके प्रश्न-शेष में 3 प्रश्न जुड़ते हैं।",
            pages=3, highlight=True),

    Product("sq_career", "Career & Profession Report", "करियर एवं व्यवसाय मार्गदर्शन रिपोर्ट",
            11100, 0, "single_question",
            "A PDF on your career, from your own chart: the houses and planets that govern it, your running dasha and the sub-periods of the next three years, yogas and remedies.",
            "आपकी अपनी कुंडली से करियर पर PDF: इसे चलाने वाले भाव और ग्रह, चल रही दशा और अगले तीन वर्षों की अंतर्दशाएँ, योग और उपाय।",
            pages=5, highlight=True),
    Product("sq_marriage_timing", "Marriage & Relationship Report", "विवाह समय एवं संबंध मार्गदर्शन रिपोर्ट",
            11100, 0, "single_question",
            "A PDF on marriage and relationships, from your own chart: the houses and planets that govern them, your running dasha and the sub-periods of the next three years, yogas and remedies.",
            "आपकी अपनी कुंडली से विवाह और संबंधों पर PDF: इन्हें चलाने वाले भाव और ग्रह, चल रही दशा और अगले तीन वर्षों की अंतर्दशाएँ, योग और उपाय।",
            pages=5),
    Product("sq_wealth_business", "Wealth, Finance & Growth Report", "धन, वित्त एवं व्यापार वृद्धि रिपोर्ट",
            11100, 0, "single_question",
            "A PDF on wealth and business, from your own chart: the houses and planets that govern them, your running dasha and the sub-periods of the next three years, yogas and remedies.",
            "आपकी अपनी कुंडली से धन और व्यापार पर PDF: इन्हें चलाने वाले भाव और ग्रह, चल रही दशा और अगले तीन वर्षों की अंतर्दशाएँ, योग और उपाय।",
            pages=5),

    Product("life_book", "Comprehensive Vedic Life Book", "सम्पूर्ण वैदिक जीवन कुंडली महाग्रन्थ",
            49900, 0, "kundali_book",
            "A PDF horoscope book from your own chart: the D1 and D9 chart drawings, planet, house and aspect tables, Ashtakavarga, a divisional-chart (varga) table, yogas, the Vimshottari dasha and antardasha tables, house-by-house and planet-by-planet readings, the dasha sub-periods of the next twelve months and remedies.",
            "आपकी अपनी कुंडली से बनी PDF पुस्तक: D1 और D9 कुंडली चित्र, ग्रह, भाव और दृष्टि सारणियाँ, अष्टकवर्ग, वर्ग कुंडली सारणी, योग, विंशोत्तरी महादशा-अंतर्दशा, भाव-भाव और ग्रह-ग्रह फल, अगले बारह महीनों की अंतर्दशाएँ और उपाय।",
            pages=8, highlight=True),
]}


# Attach the regular prices (kept in one table so they are easy to review).
PRODUCTS = {sku: (p if p.list_paise else
                  Product(**{**p.__dict__, "list_paise": LIST_PRICES_PAISE[sku]}))
            for sku, p in PRODUCTS.items()}
assert all(p.list_paise >= p.offer_paise for p in PRODUCTS.values()), \
    "a list price below its offer price would make the 'offer' a surcharge"


def catalogue(kind: str | None = None, now: datetime | None = None) -> list[dict]:
    now = now or _now()
    return [p.to_dict(now) for p in PRODUCTS.values() if kind is None or p.kind == kind]


# --------------------------------------------------------------------------
# Order creation
# --------------------------------------------------------------------------

def create_order(db: Session, user, sku: str, birth_id: int | None = None,
                 coupon_code: str | None = None,
                 report_topic: str | None = None) -> tuple[Order, dict]:
    """Create the local order, then ask the active gateway to open a session.

    A coupon is priced here, once, and the result is frozen onto the order:
    the gateway is asked for exactly `amount_paise`, and `credits` already
    includes any extra_credits bonus. Editing the coupon afterwards therefore
    cannot change what an order in flight charges or pays out.
    """
    product = PRODUCTS.get(sku)
    if product is None:
        raise ValueError(f"Unknown product '{sku}'")

    # One instant decides the price for coupon, order and gateway alike, and
    # it is frozen on the order below (amount_paise): a payment made later is
    # checked against that, never against a recomputed price.
    price = product.price_paise(_now())

    coupon = None
    discount = bonus = 0
    if coupon_code and coupon_code.strip():
        coupon, message, discount, bonus = coupons.validate(
            db, coupon_code, user, product, amount_paise=price)
        if coupon is None:
            raise ValueError(message or "That coupon cannot be used.")

    topic = report_topic or (product.sku if product.kind == "single_question" else None)
    gateway = gateways.active()
    order = Order(
        user_id=user.id,
        sku=product.sku,
        title=product.title,
        amount_paise=price - discount,
        original_amount_paise=price,
        discount_paise=discount,
        coupon_id=coupon.id if coupon else None,
        credits=product.credits + bonus,
        birth_id=birth_id,
        report_topic=topic,
        fulfilment=(FulfilStatus.pending if product.kind == "kundali"
                    else FulfilStatus.not_applicable),
        provider=gateway.key,
    )
    db.add(order)
    db.flush()   # assign order.id so the gateway receipt can reference it

    checkout = gateway.create(order, user)
    db.commit()
    return order, checkout


MANUAL_METHODS = ("upi", "cash", "bank", "other")
MANUAL_MAX_PAISE = 1_000_000_00      # ₹10 lakh — a typo guard, not a business rule
CUSTOM_SKU = "custom"


def create_manual_order(db: Session, user, admin_user, *, sku: str,
                        amount_paise: int, title: str = "", credits: int = 0,
                        method: str = "upi", reference: str = "", note: str = "",
                        birth_id: int | None = None,
                        provider: str = "manual") -> Order:
    """Record a sale that happened outside the site — cash, a UPI transfer to
    the personal handle, a bank deposit — as an ordinary PAID order.

    It deliberately goes through `mark_paid`, the same idempotent path every
    gateway uses, rather than inserting credits directly: the ledger row,
    revenue totals and the kundali work queue then all behave exactly as they
    do for an online order, and the admin has already verified the money
    before typing it in, so there is no claim/verify step to run.

    `sku` is a catalogue SKU or CUSTOM_SKU. A custom order names its own title
    and credit count (bespoke consultations, discounts done by hand); a
    catalogue order takes title and credits from the product, and only the
    amount is the admin's to override.

    `provider` is "manual" for a real off-site sale, or "comp" for something
    given away free (admin "grant"). A comp is still a PAID order at ₹0 — so the
    fulfilment queue, the ledger and the customer's order history all treat it
    like any other — but it is never counted or listed as a sale.
    """
    if amount_paise < 0 or amount_paise > MANUAL_MAX_PAISE:
        raise ValueError("Amount is out of range.")
    if method not in MANUAL_METHODS:
        raise ValueError(f"Payment method must be one of: {', '.join(MANUAL_METHODS)}.")

    if sku == CUSTOM_SKU:
        title = title.strip()
        if not title:
            raise ValueError("A custom order needs a title.")
        if credits < 0 or credits > 10_000:
            raise ValueError("Credits must be between 0 and 10,000.")
        product, kind, list_price = None, "custom", amount_paise
    else:
        product = PRODUCTS.get(sku)
        if product is None:
            raise ValueError(f"Unknown product '{sku}'")
        title, credits, kind, list_price = (
            product.title, product.credits, product.kind, product.amount_paise)

    order = Order(
        user_id=user.id,
        sku=sku,
        title=title[:160],
        amount_paise=amount_paise,
        original_amount_paise=list_price,
        discount_paise=max(0, list_price - amount_paise),
        credits=credits,
        birth_id=birth_id,
        report_topic=sku if kind == "single_question" else None,
        # Only a hand-written kundali has a delivery step to track; everything
        # else is complete the moment it is paid.
        fulfilment=(FulfilStatus.pending if kind == "kundali"
                    else FulfilStatus.not_applicable),
        fulfil_note=note.strip()[:2000],
        provider=provider,
        verified_by=admin_user.id,
        verified_at=utcnow(),
        verify_note=" · ".join(
            p for p in (f"{provider}/{method}", reference.strip(), note.strip()) if p)[:255],
    )
    db.add(order)
    db.flush()                                   # need order.id below
    order.provider_order_id = f"{'MAN' if provider == 'manual' else 'CMP'}{order.id:06d}"
    # Per-order, never the admin's free-text reference: provider_payment_id is
    # UNIQUE with provider, and two cash sales can both say "cash".
    mark_paid(db, order, f"manual:{order.id}")
    return order


def has_paid_report(db: Session, user, sku: str | None = None,
                    birth_id: int | None = None,
                    topic: str | None = None) -> Order | None:
    """Check if the user has a paid order for this single-question report or sku."""
    query = select(Order).where(
        Order.user_id == user.id,
        Order.status == OrderStatus.paid,
    )
    if sku:
        query = query.where(Order.sku == sku)
    if topic:
        query = query.where(Order.report_topic == topic)
    if birth_id is not None:
        query = query.where((Order.birth_id == birth_id) | (Order.birth_id == None))
    query = query.order_by(Order.id.desc())
    return db.execute(query).scalars().first()


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
    if product is None:            # a custom manual order has no pack to exceed
        return 0
    return max(0, int(order.credits or 0) - product.credits)


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
