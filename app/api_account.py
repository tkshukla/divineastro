"""Account, credit and payment routes.

Mounted by main.py. Kept separate from the astrology endpoints so the
money path can be read and audited on its own.
"""

from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import auth, billing, coupons
from .db import (
    BirthProfile, Coupon, CouponKind, CouponRedemption, CreditEntry, EntryKind,
    FulfilStatus, Order, OrderStatus, QuestionLog, User, balance, grant,
    session as db_session, utcnow,
)

router = APIRouter(prefix="/api")


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


def me(request: Request, db: Session = Depends(get_db)) -> User:
    return auth.require_user(request, db)


def admin(user: User = Depends(me)) -> User:
    """Admin gate. 403 rather than 404: the caller is authenticated already."""
    if not user.is_admin:
        raise HTTPException(403, "Administrator access required.")
    return user


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------

class ProfileIn(BaseModel):
    name: str = ""
    phone: str = ""
    language: str = "en"


class OrderIn(BaseModel):
    sku: str
    birth_id: int | None = None
    coupon_code: str | None = None
    report_topic: str | None = None


class CouponPreviewIn(BaseModel):
    code: str = ""
    sku: str


class CouponIn(BaseModel):
    """Admin coupon create. Datetimes are ISO-8601 strings or null."""

    code: str
    description: str = ""
    kind: str = "percent"
    value: int = 0
    min_amount_paise: int = 0
    max_discount_paise: int | None = None
    applies_to: str = "all"
    active: bool = True
    starts_at: str | None = None
    expires_at: str | None = None
    max_redemptions: int | None = None
    max_per_user: int = 1


class CouponPatch(BaseModel):
    """Admin coupon update. Every field optional — only what is sent changes."""

    description: str | None = None
    kind: str | None = None
    value: int | None = None
    min_amount_paise: int | None = None
    max_discount_paise: int | None = None
    applies_to: str | None = None
    active: bool | None = None
    starts_at: str | None = None
    expires_at: str | None = None
    max_redemptions: int | None = None
    max_per_user: int | None = None


class ConfirmIn(BaseModel):
    """Browser-side return. Fields vary by gateway, so this stays permissive."""

    order_id: int | None = None
    payload: dict = Field(default_factory=dict)


class BirthIn(BaseModel):
    label: str = ""
    name: str = ""
    date: str
    time: str = "12:00"
    time_known: bool = True
    gender: str = ""              # 'female' | 'male' | 'other' | '' (unstated)
    place: str
    latitude: float
    longitude: float
    timezone: str = ""
    zodiac: str = "sidereal"
    ayanamsa: str = "lahiri"
    house_system: str = Field(default="Whole Sign")


class BirthPatch(BaseModel):
    """Rename only. Birth data itself is never edited — it is recast instead."""

    label: str


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------

DEV_LOGIN = os.environ.get("ASTRO_DEV_LOGIN", "0") == "1"


@router.get("/auth/providers")
def auth_providers() -> dict:
    return {"providers": auth.providers(), "dev_login": DEV_LOGIN}


@router.post("/auth/dev")
def dev_login(body: dict, response: Response, db: Session = Depends(get_db)) -> dict:
    """Sign in without a real provider. Only for local development and tests.

    Gated behind ASTRO_DEV_LOGIN=1 and refuses to run when cookies are marked
    secure, so it cannot be left on by accident in production.
    """
    if not DEV_LOGIN or os.environ.get("ASTRO_COOKIE_SECURE", "0") == "1":
        raise HTTPException(404, "Not found.")
    email = (body.get("email") or "dev@example.com").strip().lower()
    user, created = auth.upsert_user(db, "dev", {
        "sub": f"dev:{email}", "email": email, "email_verified": True,
        "name": body.get("name") or email.split("@")[0],
    })
    auth.issue_session(response, user)
    return {"user": _user_dict(db, user), "created": created}


@router.get("/auth/{provider}/start")
async def oauth_start(provider: str, request: Request, next: str = "/"):
    client = auth.client(provider)
    redirect_uri = str(request.url_for("oauth_callback", provider=provider))
    request.session["post_login"] = next
    return await client.authorize_redirect(request, redirect_uri)


@router.api_route("/auth/{provider}/callback", methods=["GET", "POST"],
                  name="oauth_callback")
async def oauth_callback(provider: str, request: Request,
                         db: Session = Depends(get_db)):
    client = auth.client(provider)
    try:
        token = await client.authorize_access_token(request)
    except auth.OAuthError as exc:
        raise HTTPException(400, f"Sign-in was cancelled or failed: {exc.error}") from exc

    claims = token.get("userinfo") or {}
    if not claims:                       # Apple returns claims only in the id_token
        claims = await client.parse_id_token(request, token)

    user, created = auth.upsert_user(db, provider, dict(claims))
    target = request.session.pop("post_login", "/") or "/"
    response = RedirectResponse(url=f"{target}{'&' if '?' in target else '?'}welcome="
                                    f"{'1' if created else '0'}", status_code=303)
    auth.issue_session(response, user)
    return response


@router.post("/auth/logout")
def logout(response: Response) -> dict:
    auth.clear_session(response)
    return {"ok": True}


@router.get("/me")
def whoami(request: Request, db: Session = Depends(get_db)) -> dict:
    user = auth.current_user(request, db)
    if user is None:
        return {"user": None, "free_questions": billing.FREE_QUESTIONS}
    return {"user": _user_dict(db, user)}


@router.post("/me")
def update_me(body: ProfileIn, user: User = Depends(me),
              db: Session = Depends(get_db)) -> dict:
    if body.name.strip():
        user.name = body.name.strip()[:120]
    if body.phone.strip():
        user.phone = body.phone.strip()[:20]
    if body.language in ("en", "hi"):
        user.language = body.language
    db.commit()
    return {"user": _user_dict(db, user)}


def _user_dict(db: Session, user: User) -> dict:
    asked = db.execute(
        select(CreditEntry).where(
            CreditEntry.user_id == user.id, CreditEntry.kind == EntryKind.question)
    ).scalars().all()
    return {
        "id": user.id, "email": user.email, "name": user.name,
        "picture": user.picture, "provider": user.provider, "phone": user.phone,
        "language": user.language, "is_admin": user.is_admin,
        "credits": balance(db, user.id),
        "questions_asked": len(asked),
        "member_since": user.created_at.strftime("%b %Y"),
    }


# --------------------------------------------------------------------------
# Saved birth profiles
# --------------------------------------------------------------------------

# A chart is a person, not a document: five covers a family and keeps the
# picker glanceable. Enforced here because the browser is not to be trusted.
MAX_BIRTHS = 5


def _my_births(db: Session, user: User) -> list[BirthProfile]:
    return list(db.execute(
        select(BirthProfile).where(BirthProfile.user_id == user.id)
        .order_by(BirthProfile.created_at.desc())
    ).scalars().all())


GENDERS = ("female", "male", "other")


def _gender(raw: str) -> str:
    """Anything unrecognised becomes '' — unstated is always an allowed answer,
    so a bad value is never worth rejecting a saved chart over."""
    value = (raw or "").strip().lower()
    return value if value in GENDERS else ""


def _same_birth(row: BirthProfile, body: BirthIn) -> bool:
    """Same moment, same place — the same chart, whatever it was labelled.

    Coordinates are compared with a tolerance: the geocoder can hand back
    marginally different decimals for one city between lookups, and a few
    metres never moves a planet.
    """
    return (row.date == body.date and row.time == body.time
            and row.place == body.place
            and abs(row.latitude - body.latitude) < 1e-4
            and abs(row.longitude - body.longitude) < 1e-4)


@router.get("/births")
def list_births(user: User = Depends(me), db: Session = Depends(get_db)) -> dict:
    rows = _my_births(db, user)
    return {"births": [_birth_dict(b) for b in rows], "max": MAX_BIRTHS}


@router.post("/births")
def add_birth(body: BirthIn, user: User = Depends(me),
              db: Session = Depends(get_db)) -> dict:
    """Save a chart. Called on every cast, so it must be idempotent.

    Recasting a chart the user already has returns the existing row untouched —
    including its label, which they may have renamed since.
    """
    from . import geo

    rows = _my_births(db, user)
    for row in rows:
        if _same_birth(row, body):
            return {"birth": _birth_dict(row), "created": False}

    if len(rows) >= MAX_BIRTHS:
        raise HTTPException(
            409, f"You can keep {MAX_BIRTHS} saved charts. Delete one to save another.")

    tz = body.timezone or geo.timezone_for(body.latitude, body.longitude)
    profile = BirthProfile(
        user_id=user.id, label=(body.label or body.name or body.place)[:120],
        name=body.name, date=body.date, time=body.time, time_known=body.time_known,
        gender=_gender(body.gender),
        place=body.place, latitude=body.latitude, longitude=body.longitude,
        # Stored sidereal regardless of what the client sent — see the note in
        # main.py. A saved profile is replayed on every later reading, so a
        # tropical one would keep producing dasha-less charts indefinitely.
        timezone=tz, zodiac="sidereal", ayanamsa="lahiri",
        house_system="Whole Sign",
    )
    db.add(profile)
    db.commit()
    return {"birth": _birth_dict(profile), "created": True}


@router.patch("/births/{birth_id}")
def rename_birth(birth_id: int, body: BirthPatch, user: User = Depends(me),
                 db: Session = Depends(get_db)) -> dict:
    profile = db.get(BirthProfile, birth_id)
    if profile is None or profile.user_id != user.id:
        raise HTTPException(404, "Not found.")
    label = body.label.strip()
    if not label:
        raise HTTPException(400, "A name is required.")
    profile.label = label[:120]
    db.commit()
    return {"birth": _birth_dict(profile)}


@router.delete("/births/{birth_id}")
def delete_birth(birth_id: int, user: User = Depends(me),
                 db: Session = Depends(get_db)) -> dict:
    profile = db.get(BirthProfile, birth_id)
    if profile is None or profile.user_id != user.id:
        raise HTTPException(404, "Not found.")
    db.delete(profile)
    db.commit()
    return {"ok": True}


def _birth_dict(b: BirthProfile) -> dict:
    return {
        "id": b.id, "label": b.label, "name": b.name, "date": b.date, "time": b.time,
        "time_known": b.time_known, "gender": b.gender, "place": b.place, "latitude": b.latitude,
        "longitude": b.longitude, "timezone": b.timezone, "zodiac": b.zodiac,
        "ayanamsa": b.ayanamsa, "house_system": b.house_system,
    }


# --------------------------------------------------------------------------
# Catalogue and orders
# --------------------------------------------------------------------------

@router.get("/products")
def products(kind: str | None = None) -> dict:
    from . import gateways

    return {
        "products": billing.catalogue(kind),
        "free_questions": billing.FREE_QUESTIONS,
        "astrologer": billing.ASTROLOGER,
        "turnaround_days": billing.TURNAROUND_DAYS,
        "payment": gateways.status(),
    }


@router.post("/orders")
def create_order(body: OrderIn, user: User = Depends(me),
                 db: Session = Depends(get_db)) -> dict:
    try:
        order, checkout = billing.create_order(
            db, user, body.sku, body.birth_id, body.coupon_code, body.report_topic)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"Payment gateway error: {exc}") from exc
    return {"order": _order_dict(order), "checkout": checkout}


@router.post("/orders/confirm")
def confirm_order(body: ConfirmIn, user: User = Depends(me),
                  db: Session = Depends(get_db)) -> dict:
    """Browser return. Only grants when the gateway's return is verifiable.

    Gateways whose browser return carries no signature (Cashfree) always fall
    through to 'pending' here — the webhook grants instead. That is deliberate:
    an unsigned client-side callback must never move money.
    """
    order = db.get(Order, body.order_id) if body.order_id else None
    if order is None:
        provider_order = body.payload.get("order_id") \
            or body.payload.get("payment_request_id") \
            or body.payload.get("razorpay_order_id") or body.payload.get("ORDERID")
        if provider_order:
            order = db.execute(
                select(Order).where(Order.provider_order_id == provider_order)
            ).scalar_one_or_none()

    if order is None or order.user_id != user.id:
        raise HTTPException(404, "Order not found.")

    # The receipt must belong to THIS order. Without this a customer could buy
    # the ₹111 pack, then present that same payment against a ₹751 order they
    # created separately — verify_return only asks "was this payment real".
    claimed = (body.payload.get("payment_request_id") or body.payload.get("order_id")
               or body.payload.get("razorpay_order_id") or body.payload.get("ORDERID") or "")
    if claimed and order.provider_order_id and claimed != order.provider_order_id:
        raise HTTPException(400, "That payment belongs to a different order.")

    if not billing.verify_return(body.payload):
        return {
            "ok": True, "granted": False, "pending": True,
            "message": "Payment is being confirmed. Credits appear within a minute.",
            "credits": balance(db, user.id), "order": _order_dict(order),
        }

    payment_id = (body.payload.get("razorpay_payment_id")
                  or body.payload.get("TXNID") or body.payload.get("payment_id") or "")
    granted, message = billing.mark_paid(db, order, payment_id)
    return {
        "ok": True, "granted": granted, "message": message,
        "credits": balance(db, user.id), "order": _order_dict(order),
    }


class UtrIn(BaseModel):
    order_id: int
    utr: str


@router.post("/orders/upi-claim")
def submit_utr(body: UtrIn, user: User = Depends(me),
               db: Session = Depends(get_db)) -> dict:
    """Customer says they paid by UPI. Grants nothing — queues it for a human.

    The UTR is stored under a UNIQUE constraint, so the same reference cannot be
    claimed against two orders. Everything else waits on verification.
    """
    from . import upi

    order = db.get(Order, body.order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(404, "Order not found.")
    if order.status == OrderStatus.paid:
        return {"ok": True, "status": order.status.value,
                "message": "This order is already paid."}

    utr = upi.normalise_utr(body.utr)
    if not upi.valid_utr(utr):
        raise HTTPException(
            400, "That does not look like a UPI reference. It is usually 12 "
                 "digits, shown as UTR or Transaction ID in your UPI app.")

    clash = db.execute(
        select(Order).where(Order.utr == utr, Order.id != order.id)
    ).scalar_one_or_none()
    if clash is not None:
        raise HTTPException(
            409, "That reference has already been submitted for another order. "
                 "Please check the UTR, or contact us if this looks wrong.")

    order.utr = utr
    order.utr_submitted_at = utcnow()
    order.status = OrderStatus.awaiting_verification
    db.commit()
    return {
        "ok": True, "status": order.status.value,
        "message": "Thank you. We are checking this against our bank statement "
                   "and will add your questions shortly — usually within a few "
                   "hours. You will not need to pay again.",
        "order": _order_dict(order),
    }


@router.get("/admin/upi/pending")
def upi_pending(user: User = Depends(admin), db: Session = Depends(get_db)) -> dict:
    """Everything waiting on a human to check the bank statement."""
    rows = db.execute(
        select(Order).where(Order.status == OrderStatus.awaiting_verification)
        .order_by(Order.utr_submitted_at)
    ).scalars().all()
    out = []
    for o in rows:
        buyer = db.get(User, o.user_id)
        d = _order_dict(o)
        d.update({
            "utr": o.utr,
            "submitted_at": o.utr_submitted_at.strftime("%d %b %Y, %H:%M")
                            if o.utr_submitted_at else None,
            "buyer_email": buyer.email if buyer else "",
            "buyer_name": buyer.name if buyer else "",
            "expected_amount": o.amount_paise // 100,
            "reference": o.provider_order_id,
        })
        out.append(d)
    return {"pending": out}


class VerifyIn(BaseModel):
    order_id: int
    approve: bool
    note: str = ""


@router.post("/admin/upi/verify")
def upi_verify(body: VerifyIn, user: User = Depends(admin),
               db: Session = Depends(get_db)) -> dict:
    """Approve or reject a claimed UPI payment. Approval is what grants credits."""
    order = db.get(Order, body.order_id)
    if order is None:
        raise HTTPException(404, "Order not found.")

    order.verified_by = user.id
    order.verified_at = utcnow()
    order.verify_note = body.note[:255]

    if not body.approve:
        order.status = OrderStatus.rejected
        db.commit()
        return {"ok": True, "granted": False, "order": _order_dict(order)}

    granted, message = billing.mark_paid(db, order, order.utr or "")
    return {
        "ok": True, "granted": granted, "message": message,
        "order": _order_dict(order),
        "buyer_credits": balance(db, order.user_id),
    }


# --------------------------------------------------------------------------
# Hand-written kundali fulfilment
# --------------------------------------------------------------------------

@router.get("/admin/kundalis")
def admin_kundalis(state: str = "open", _: User = Depends(admin),
                   db: Session = Depends(get_db)) -> dict:
    """The astrologer's work queue: paid kundali orders and their birth data.

    `state=open` hides delivered work; `state=all` shows everything. Only paid
    orders appear — an unpaid order is not yet a commitment to write anything.
    """
    q = select(Order).where(
        Order.fulfilment != FulfilStatus.not_applicable,
        Order.status == OrderStatus.paid,
    )
    if state != "all":
        q = q.where(Order.fulfilment != FulfilStatus.delivered)

    out = []
    for o in db.execute(q.order_by(Order.created_at)).scalars().all():
        buyer = db.get(User, o.user_id)
        birth = db.get(BirthProfile, o.birth_id) if o.birth_id else None
        d = _order_dict(o)
        d.update({
            "buyer_email": buyer.email if buyer else "",
            "buyer_name": buyer.name if buyer else "",
            "buyer_phone": buyer.phone if buyer else "",
            "fulfil_note": o.fulfil_note,
            "birth": _birth_dict(birth) if birth else None,
        })
        out.append(d)
    return {"kundalis": out}


class FulfilIn(BaseModel):
    order_id: int
    status: str
    note: str = ""


@router.post("/admin/kundalis/fulfil")
def admin_fulfil(body: FulfilIn, _: User = Depends(admin),
                 db: Session = Depends(get_db)) -> dict:
    order = db.get(Order, body.order_id)
    if order is None:
        raise HTTPException(404, "Order not found.")
    try:
        status = FulfilStatus(body.status)
    except ValueError:
        raise HTTPException(400, f"Unknown fulfilment status '{body.status}'.") from None
    if status is FulfilStatus.not_applicable:
        raise HTTPException(400, "A kundali order cannot become not_applicable.")

    order.fulfilment = status
    if body.note:
        order.fulfil_note = body.note[:2000]
    db.commit()
    return {"ok": True, "order": _order_dict(order)}


@router.post("/webhooks/payment")
async def payment_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    """Single webhook endpoint; the active gateway parses its own format."""
    body = await request.body()
    result = billing.handle_webhook(db, body, request.headers)
    if not result.get("ok") and "signature" in str(result.get("reason", "")):
        raise HTTPException(400, "Invalid signature.")
    return result


@router.get("/orders")
def my_orders(user: User = Depends(me), db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())
    ).scalars().all()
    return {"orders": [_order_dict(o) for o in rows]}


def _order_dict(o: Order) -> dict:
    return {
        "id": o.id, "sku": o.sku, "title": o.title,
        "amount": o.amount_paise // 100, "credits": o.credits,
        "status": o.status.value, "fulfilment": o.fulfilment.value,
        "created_at": o.created_at.strftime("%d %b %Y"),
        "paid_at": o.paid_at.strftime("%d %b %Y") if o.paid_at else None,
        "delivered": bool(o.delivered_path),
        "report_topic": o.report_topic,
        # Coupon trail — paise, so the client can render exact rupees.
        "amount_paise": o.amount_paise,
        "original_amount_paise": o.original_amount_paise or o.amount_paise,
        "discount_paise": o.discount_paise or 0,
        "coupon_id": o.coupon_id,
    }


# --------------------------------------------------------------------------
# Coupons — customer-facing preview
# --------------------------------------------------------------------------

@router.post("/coupons/preview")
def preview_coupon(body: CouponPreviewIn, user: User = Depends(me),
                   db: Session = Depends(get_db)) -> dict:
    """Price a coupon without consuming it.

    Called live from the store as the customer types, so it must never write.
    Money is returned in paise; `*_rupees` mirrors are for display only.
    """
    product = billing.PRODUCTS.get(body.sku)
    if product is None:
        raise HTTPException(400, f"Unknown product '{body.sku}'")

    coupon, message, discount, bonus = coupons.validate(db, body.code, user, product)
    original = product.amount_paise
    if coupon is None:
        discount, bonus = 0, 0
    final = original - discount
    return {
        "valid": coupon is not None,
        "code": coupons.normalise(body.code),
        "sku": product.sku,
        "message": message or "",
        "kind": coupon.kind.value if coupon else None,
        "original": original,
        "discount": discount,
        "final": final,
        "bonus_credits": bonus,
        "original_rupees": original / 100,
        "discount_rupees": discount / 100,
        "final_rupees": final / 100,
    }


# --------------------------------------------------------------------------
# Coupons — admin
# --------------------------------------------------------------------------

def _coupon_kind(value: str) -> CouponKind:
    try:
        return CouponKind(str(value).strip().lower())
    except ValueError as exc:
        raise HTTPException(
            400, f"kind must be one of {[k.value for k in CouponKind]}") from exc


def _check_value(kind: CouponKind, value: int) -> None:
    if kind == CouponKind.percent and not 1 <= int(value) <= 100:
        raise HTTPException(400, "A percent coupon's value must be 1–100.")
    if kind != CouponKind.percent and int(value) < 1:
        raise HTTPException(400, "value must be at least 1.")


@router.get("/admin/coupons")
def admin_list_coupons(_: User = Depends(admin),
                       db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(Coupon).order_by(Coupon.created_at.desc())
    ).scalars().all()
    return {"coupons": [coupons.to_dict(db, c) for c in rows]}


@router.post("/admin/coupons")
def admin_create_coupon(body: CouponIn, _: User = Depends(admin),
                        db: Session = Depends(get_db)) -> dict:
    code = coupons.normalise(body.code)
    if not code:
        raise HTTPException(400, "A code is required.")
    if coupons.find(db, code) is not None:
        raise HTTPException(409, f"Coupon '{code}' already exists.")

    kind = _coupon_kind(body.kind)
    _check_value(kind, body.value)
    try:
        starts_at = coupons.parse_dt(body.starts_at)
        expires_at = coupons.parse_dt(body.expires_at)
    except ValueError as exc:
        raise HTTPException(400, f"Bad date: {exc}") from exc

    coupon = Coupon(
        code=code, description=body.description[:255], kind=kind, value=int(body.value),
        min_amount_paise=max(0, int(body.min_amount_paise)),
        max_discount_paise=body.max_discount_paise,
        applies_to=(body.applies_to or "all").strip().lower()[:40],
        active=body.active, starts_at=starts_at, expires_at=expires_at,
        max_redemptions=body.max_redemptions,
        max_per_user=max(0, int(body.max_per_user)),
    )
    db.add(coupon)
    db.commit()
    return {"coupon": coupons.to_dict(db, coupon)}


@router.patch("/admin/coupons/{coupon_id}")
def admin_update_coupon(coupon_id: int, body: CouponPatch,
                        _: User = Depends(admin),
                        db: Session = Depends(get_db)) -> dict:
    coupon = db.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(404, "Coupon not found.")

    fields = body.model_dump(exclude_unset=True)
    if "kind" in fields and fields["kind"] is not None:
        coupon.kind = _coupon_kind(fields["kind"])
    if "value" in fields and fields["value"] is not None:
        _check_value(coupon.kind, fields["value"])
        coupon.value = int(fields["value"])
    for name in ("starts_at", "expires_at"):
        if name in fields:
            try:
                setattr(coupon, name, coupons.parse_dt(fields[name]))
            except ValueError as exc:
                raise HTTPException(400, f"Bad {name}: {exc}") from exc
    if "description" in fields and fields["description"] is not None:
        coupon.description = fields["description"][:255]
    if "applies_to" in fields and fields["applies_to"] is not None:
        coupon.applies_to = fields["applies_to"].strip().lower()[:40]
    if "active" in fields and fields["active"] is not None:
        coupon.active = bool(fields["active"])
    if "min_amount_paise" in fields and fields["min_amount_paise"] is not None:
        coupon.min_amount_paise = max(0, int(fields["min_amount_paise"]))
    if "max_per_user" in fields and fields["max_per_user"] is not None:
        coupon.max_per_user = max(0, int(fields["max_per_user"]))
    # These two are meaningfully nullable — null means "uncapped"/"unlimited".
    if "max_discount_paise" in fields:
        coupon.max_discount_paise = fields["max_discount_paise"]
    if "max_redemptions" in fields:
        coupon.max_redemptions = fields["max_redemptions"]

    db.commit()
    return {"coupon": coupons.to_dict(db, coupon)}


@router.delete("/admin/coupons/{coupon_id}")
def admin_delete_coupon(coupon_id: int, _: User = Depends(admin),
                        db: Session = Depends(get_db)) -> dict:
    """Soft-delete once it has been used — the redemption trail must survive."""
    coupon = db.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(404, "Coupon not found.")

    used = db.execute(
        select(CouponRedemption.id).where(CouponRedemption.coupon_id == coupon.id)
    ).first() is not None
    if used:
        coupon.active = False
        db.commit()
        return {"ok": True, "deleted": False, "deactivated": True,
                "coupon": coupons.to_dict(db, coupon)}

    db.delete(coupon)
    db.commit()
    return {"ok": True, "deleted": True, "deactivated": False}


@router.get("/admin/coupons/{coupon_id}/redemptions")
def admin_coupon_redemptions(coupon_id: int, _: User = Depends(admin),
                             db: Session = Depends(get_db)) -> dict:
    coupon = db.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(404, "Coupon not found.")

    rows = db.execute(
        select(CouponRedemption, User, Order)
        .join(User, User.id == CouponRedemption.user_id)
        .join(Order, Order.id == CouponRedemption.order_id)
        .where(CouponRedemption.coupon_id == coupon_id)
        .order_by(CouponRedemption.created_at.desc())
    ).all()
    return {
        "coupon": coupons.to_dict(db, coupon),
        "redemptions": [{
            "id": r.id, "user_id": r.user_id, "email": u.email,
            "order_id": r.order_id, "sku": o.sku, "order_status": o.status.value,
            "discount_paise": r.discount_paise,
            "at": r.created_at.strftime("%d %b %Y, %H:%M"),
        } for r, u, o in rows],
    }


# --------------------------------------------------------------------------
# History
# --------------------------------------------------------------------------

@router.get("/history")
def history(limit: int = 100, user: User = Depends(me),
            db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(QuestionLog).where(QuestionLog.user_id == user.id)
        .order_by(QuestionLog.created_at.desc()).limit(min(limit, 500))
    ).scalars().all()
    return {"questions": [{
        "id": q.id, "question": q.question, "answer": q.answer,
        "topic": q.topic, "verdict": q.verdict, "language": q.language,
        "asked_at": q.created_at.strftime("%d %b %Y, %H:%M"),
    } for q in rows]}


@router.get("/ledger")
def ledger(user: User = Depends(me), db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(CreditEntry).where(CreditEntry.user_id == user.id)
        .order_by(CreditEntry.created_at.desc()).limit(200)
    ).scalars().all()
    return {
        "balance": balance(db, user.id),
        "entries": [{
            "delta": e.delta, "kind": e.kind.value, "note": e.note,
            "at": e.created_at.strftime("%d %b %Y, %H:%M"),
        } for e in rows],
    }
