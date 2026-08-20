"""Coupons — validation, pricing and redemption.

Three rules govern everything here:

* **Validation never mutates.** `validate()` is called on every keystroke-ish
  preview in the store. It reads, it prices, it returns a message. Nothing is
  consumed until a payment is actually confirmed.
* **Money is integer paise, and the gateway floor is real.** A discount can
  never exceed the price, and the amount finally charged must stay at or above
  ₹1 — gateways reject zero-value orders. A coupon generous enough to breach
  that is clamped, and the customer is told.
* **Redemption is idempotent per order.** Razorpay and Cashfree both retry
  webhooks; `coupon_redemptions.order_id` is UNIQUE so a replay cannot record a
  second redemption or inflate `times_redeemed`.

`validate()` deliberately takes the *product* rather than a sku, so this module
never imports `billing` and the dependency arrow points one way only.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import Coupon, CouponKind, CouponRedemption, aware, utcnow

# Gateways refuse orders below ₹1, so that is the floor a discount may reach.
MIN_CHARGE_PAISE = 100


def normalise(code: str) -> str:
    return (code or "").strip().upper()


def _user_id(user) -> int:
    return int(getattr(user, "id", user))


def find(db: Session, code: str) -> Coupon | None:
    code = normalise(code)
    if not code:
        return None
    return db.execute(
        select(Coupon).where(Coupon.code == code)
    ).scalar_one_or_none()


def _applies(coupon: Coupon, product) -> bool:
    """`applies_to` is 'all', a product kind ('questions'/'kundali'), or a sku."""
    target = (coupon.applies_to or "all").strip().lower()
    if target in ("", "all", "*"):
        return True
    return target == product.kind or target == product.sku


def _user_redemptions(db: Session, coupon: Coupon, user_id: int) -> int:
    return int(db.execute(
        select(func.count(CouponRedemption.id)).where(
            CouponRedemption.coupon_id == coupon.id,
            CouponRedemption.user_id == user_id,
        )
    ).scalar_one())


def _global_redemptions(db: Session, coupon: Coupon) -> int:
    """The rows are the truth; the counter is only a cache of them."""
    return int(db.execute(
        select(func.count(CouponRedemption.id))
        .where(CouponRedemption.coupon_id == coupon.id)
    ).scalar_one())


def _rupees(paise: int) -> str:
    return f"₹{paise / 100:.2f}".replace(".00", "")


# --------------------------------------------------------------------------
# Pricing
# --------------------------------------------------------------------------

def price(coupon: Coupon, amount_paise: int) -> tuple[int, int, bool]:
    """Price a coupon against a list price.

    Returns (discount_paise, bonus_credits, clamped). `clamped` is True when the
    discount had to be trimmed to keep the charge at or above ₹1.
    """
    discount = 0
    bonus = 0

    if coupon.kind == CouponKind.percent:
        discount = amount_paise * max(0, int(coupon.value)) // 100
        if coupon.max_discount_paise is not None:
            discount = min(discount, int(coupon.max_discount_paise))
    elif coupon.kind == CouponKind.flat:
        discount = max(0, int(coupon.value))
    elif coupon.kind == CouponKind.extra_credits:
        bonus = max(0, int(coupon.value))

    wanted = discount
    discount = min(discount, amount_paise)                   # never below zero
    ceiling = max(0, amount_paise - MIN_CHARGE_PAISE)        # never below ₹1
    discount = min(discount, ceiling)
    return discount, bonus, discount < wanted


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate(db: Session, code: str, user, product
             ) -> tuple[Coupon | None, str | None, int, int]:
    """Check a code against a user and a product.

    Returns (coupon, message, discount_paise, bonus_credits).

    When `coupon` is None the coupon cannot be used and `message` is the
    user-facing reason. When `coupon` is set the code is good and `message` is
    a short confirmation (which also carries the notice when a discount had to
    be clamped to keep the charge at ₹1).
    """
    code = normalise(code)
    if not code:
        return None, "Enter a coupon code.", 0, 0

    coupon = find(db, code)
    if coupon is None:
        return None, f"Coupon '{code}' was not found.", 0, 0
    if not coupon.active:
        return None, "This coupon is no longer active.", 0, 0

    now = utcnow()
    starts_at = aware(coupon.starts_at)
    expires_at = aware(coupon.expires_at)
    if starts_at is not None and now < starts_at:
        return None, (f"This coupon is not valid until "
                      f"{starts_at.strftime('%d %b %Y')}."), 0, 0
    if expires_at is not None and now > expires_at:
        return None, "This coupon has expired.", 0, 0

    if coupon.max_redemptions is not None:
        used = max(int(coupon.times_redeemed or 0),
                   _global_redemptions(db, coupon))
        if used >= int(coupon.max_redemptions):
            return None, "This coupon has reached its usage limit.", 0, 0

    if user is not None and int(coupon.max_per_user or 0) > 0:
        mine = _user_redemptions(db, coupon, _user_id(user))
        if mine >= int(coupon.max_per_user):
            return None, "You have already used this coupon.", 0, 0

    amount = int(product.amount_paise)
    if coupon.min_amount_paise and amount < int(coupon.min_amount_paise):
        return None, (f"This coupon needs an order of "
                      f"{_rupees(int(coupon.min_amount_paise))} or more."), 0, 0

    if not _applies(coupon, product):
        return None, "This coupon does not apply to this item.", 0, 0

    discount, bonus, clamped = price(coupon, amount)

    if coupon.kind == CouponKind.extra_credits:
        if bonus <= 0:
            return None, "This coupon grants nothing.", 0, 0
        message = f"Coupon applied — {bonus} bonus questions added."
    else:
        if discount <= 0:
            return None, "This coupon gives no discount on this item.", 0, 0
        message = f"Coupon applied — {_rupees(discount)} off."
        if clamped:
            message += (f" Reduced so the order stays at "
                        f"{_rupees(MIN_CHARGE_PAISE)}, the payment minimum.")

    return coupon, message, discount, bonus


# --------------------------------------------------------------------------
# Redemption — idempotent per order
# --------------------------------------------------------------------------

def redeem(db: Session, coupon: Coupon, user, order,
           discount_paise: int) -> CouponRedemption:
    """Record that `order` consumed `coupon`, at most once.

    Safe to call from both the browser confirmation and a replayed webhook: the
    second call finds the existing row, leaves `times_redeemed` alone and
    returns the row it found.
    """
    existing = db.execute(
        select(CouponRedemption).where(CouponRedemption.order_id == order.id)
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    row = CouponRedemption(
        coupon_id=coupon.id,
        user_id=_user_id(user),
        order_id=order.id,
        discount_paise=int(discount_paise or 0),
    )
    # Flush the caller's pending work (the credit grant) into the outer
    # transaction FIRST, so the savepoint below contains only this insert.
    db.flush()
    # A SAVEPOINT, not the outer transaction: if two confirmations race, losing
    # the insert must not undo the credit grant that the caller has already
    # staged in the same session.
    savepoint = db.begin_nested()
    db.add(row)
    try:
        savepoint.commit()
    except IntegrityError:
        savepoint.rollback()
        try:
            db.expunge(row)          # usually already detached by the rollback
        except Exception:
            pass
        return db.execute(
            select(CouponRedemption).where(CouponRedemption.order_id == order.id)
        ).scalar_one()

    coupon.times_redeemed = int(coupon.times_redeemed or 0) + 1
    db.flush()
    return row


# --------------------------------------------------------------------------
# Serialisation for the API
# --------------------------------------------------------------------------

def _iso(value: dt.datetime | None) -> str | None:
    value = aware(value)
    return value.isoformat() if value else None


def to_dict(db: Session, coupon: Coupon) -> dict:
    used = _global_redemptions(db, coupon)
    saved = int(db.execute(
        select(func.coalesce(func.sum(CouponRedemption.discount_paise), 0))
        .where(CouponRedemption.coupon_id == coupon.id)
    ).scalar_one())
    return {
        "id": coupon.id,
        "code": coupon.code,
        "description": coupon.description,
        "kind": coupon.kind.value,
        "value": coupon.value,
        "min_amount_paise": coupon.min_amount_paise,
        "max_discount_paise": coupon.max_discount_paise,
        "applies_to": coupon.applies_to,
        "active": coupon.active,
        "starts_at": _iso(coupon.starts_at),
        "expires_at": _iso(coupon.expires_at),
        "max_redemptions": coupon.max_redemptions,
        "max_per_user": coupon.max_per_user,
        "times_redeemed": coupon.times_redeemed,
        "redemptions": used,
        "total_discount_paise": saved,
        "created_at": _iso(coupon.created_at),
    }


def parse_dt(value) -> dt.datetime | None:
    """Accept an ISO-8601 string (or None) from the admin panel."""
    if value in (None, ""):
        return None
    if isinstance(value, dt.datetime):
        return aware(value)
    text = str(value).strip().replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(text)
    return aware(parsed)
