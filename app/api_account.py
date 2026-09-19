"""Account, credit and payment routes.

Mounted by main.py. Kept separate from the astrology endpoints so the
money path can be read and audited on its own.
"""

from __future__ import annotations

import datetime as dt
import os
import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import analytics, auth, billing, coupons, mail
from .db import (
    BirthProfile, Coupon, CouponKind, CouponRedemption, CreditEntry, EntryKind,
    Feedback, FulfilStatus, Order, OrderStatus, QuestionLog, User, balance, grant,
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
def dev_login(body: dict, request: Request, response: Response,
              db: Session = Depends(get_db)) -> dict:
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
    if created:
        analytics.attribute_signup(db, user, request)
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
    if created:
        analytics.attribute_signup(db, user, request)
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
    utr_last5: str


@router.post("/orders/upi-claim")
def submit_utr(body: UtrIn, user: User = Depends(me),
               db: Session = Depends(get_db)) -> dict:
    """Customer says they paid by UPI. Grants nothing — queues it for a human.

    Only the last 5 characters of the UTR are asked for (less to type on a
    phone), so unlike the old full-UTR flow this carries no uniqueness
    guarantee — two honest customers can land on the same 5 characters at
    realistic order volumes, and this is never treated as proof of payment on
    its own. It exists purely as a search hint for whoever matches the claim
    against the real bank statement in /admin; upi_pending() below flags when
    two pending orders share a suffix so the admin knows to look closer, but
    neither claim is blocked here.
    """
    from . import upi

    order = db.get(Order, body.order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(404, "Order not found.")
    if order.status == OrderStatus.paid:
        return {"ok": True, "status": order.status.value,
                "message": "This order is already paid."}

    suffix = upi.normalise_utr_suffix(body.utr_last5)
    if not upi.valid_utr_suffix(suffix):
        raise HTTPException(
            400, "That doesn't look like the last 5 characters of a UPI "
                 "reference. Check your payment app's confirmation screen.")

    order.utr_last5 = suffix
    order.utr_submitted_at = utcnow()
    order.status = OrderStatus.awaiting_verification
    db.commit()

    # Best-effort — a mail outage must never fail a claim that already
    # succeeded. Previously nothing pinged anyone at all; an admin had to
    # remember to check /admin/upi/pending.
    try:
        mail.send(
            list(auth.admin_emails()),
            f"UPI claim: order #{order.id}",
            f"{user.email} claimed ₹{order.amount_paise / 100:.0f} for "
            f"{order.title}, UTR ends in {suffix}. Verify at /admin.",
        )
    except Exception:
        pass

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

    # utr_last5 carries no uniqueness guarantee (see submit_utr's docstring),
    # so two pending claims can legitimately share one. Flagging that here —
    # rather than blocking the customer at claim time — is what actually
    # protects against mismatching a claim to the wrong bank-statement line:
    # the admin sees the ambiguity and can tell them apart by amount and
    # buyer instead of approving on a 5-character match alone.
    suffix_counts: dict[str, int] = {}
    for o in rows:
        if o.utr_last5:
            suffix_counts[o.utr_last5] = suffix_counts.get(o.utr_last5, 0) + 1

    out = []
    for o in rows:
        buyer = db.get(User, o.user_id)
        d = _order_dict(o)
        d.update({
            "utr_last5": o.utr_last5,
            "utr_ambiguous": bool(o.utr_last5) and suffix_counts.get(o.utr_last5, 0) > 1,
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

    # order_id-derived, not the raw customer input — provider_payment_id sits
    # under UniqueConstraint("provider", "provider_payment_id"), and two
    # different orders CAN share a utr_last5 by design (see upi_pending's
    # docstring above). Writing that raw suffix straight into a globally-
    # unique column would let the second of two colliding approvals crash
    # with an IntegrityError instead of granting credits. The suffix is still
    # folded in as a human-readable tag for later lookup.
    from . import upi
    payment_id = f"{upi.reference(order.id)}:{order.utr_last5 or ''}"
    granted, message = billing.mark_paid(db, order, payment_id)
    return {
        "ok": True, "granted": granted, "message": message,
        "order": _order_dict(order),
        "buyer_credits": balance(db, order.user_id),
    }


# --------------------------------------------------------------------------
# Manual orders — a sale that happened outside the site
# --------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_MANUAL_DUP_WINDOW = dt.timedelta(minutes=2)


class ManualOrderIn(BaseModel):
    email: str = ""
    name: str = ""
    phone: str = ""
    sku: str                          # a catalogue SKU, or "custom"
    title: str = ""                   # custom orders only
    amount_paise: int | None = None   # None -> the catalogue list price
    credits: int = 0                  # custom orders only
    method: str = "upi"               # upi | cash | bank | other
    reference: str = ""               # UTR tail, receipt no., ...
    note: str = ""
    birth: BirthIn | None = None
    force: bool = False               # record even if it looks like a repeat


def _manual_customer(db: Session, email: str, name: str, phone: str) -> tuple[User, bool]:
    """Find the customer by email, or create an account for them.

    A created account is `provider="manual"`; when its owner later signs in
    with Google/etc. on the same verified address, auth.upsert_user adopts it,
    so they land on the purchase that was recorded for them. A phone-only
    customer (no email) has nothing to be adopted by — the admin can still
    fulfil the order, it just stays under that record.
    """
    email = email.strip().lower()
    phone = re.sub(r"[\s\-()]", "", phone or "")[:20]
    if not email and not phone:
        raise HTTPException(400, "Enter the customer's email or phone number.")
    if email and not _EMAIL_RE.match(email):
        raise HTTPException(400, "That email address does not look right.")

    if email:
        user = db.execute(select(User).where(func.lower(User.email) == email)
                          ).scalars().first()
    else:
        user = db.execute(select(User).where(
            User.provider == "manual", User.provider_sub == f"manual:{phone}")
        ).scalars().first()

    if user is not None:
        if user.blocked:
            raise HTTPException(409, "This customer's account is suspended.")
        if name.strip() and not user.name:
            user.name = name.strip()[:120]
        if phone and not user.phone:
            user.phone = phone
        return user, False

    user = User(email=email, name=name.strip()[:120], phone=phone,
                provider="manual", provider_sub=f"manual:{email or phone}",
                signup_source="manual")      # recorded by an admin, not a site sign-up
    db.add(user)
    db.flush()
    if email:     # same welcome gift upsert_user gives a first sign-in
        grant(db, user.id, billing.FREE_QUESTIONS, EntryKind.signup_bonus,
              note="Welcome — free questions")
    return user, True


def _manual_birth(db: Session, user: User, b: BirthIn) -> BirthProfile:
    """Attach the customer's birth data, reusing an identical chart they have.

    Unlike the self-service /births route this ignores the MAX_BIRTHS cap: it
    is the admin recording something a customer already paid for, and refusing
    would strand a paid kundali with no birth data.
    """
    from . import geo

    try:
        dt.date.fromisoformat(b.date)
        dt.datetime.strptime(b.time, "%H:%M")
    except ValueError:
        raise HTTPException(400, "Birth date must be YYYY-MM-DD and time HH:MM.")
    if not b.place.strip():
        raise HTTPException(400, "Choose the birth place from the list.")

    for row in _my_births(db, user):
        if _same_birth(row, b):
            return row
    profile = BirthProfile(
        user_id=user.id, label=(b.label or b.name or b.place)[:120],
        name=b.name, date=b.date, time=b.time, time_known=b.time_known,
        gender=_gender(b.gender), place=b.place,
        latitude=b.latitude, longitude=b.longitude,
        timezone=b.timezone or geo.timezone_for(b.latitude, b.longitude),
        zodiac="sidereal", ayanamsa="lahiri", house_system="Whole Sign",
    )
    db.add(profile)
    db.flush()
    return profile


def _manual_order_dict(o: Order, u: User | None, admin_email: str = "") -> dict:
    return {
        **_order_dict(o),
        "customer_email": u.email if u else "",
        "customer_name": u.name if u else "",
        "customer_phone": u.phone if u else "",
        "note": o.verify_note,
        "recorded_by": admin_email,
    }


@router.post("/admin/orders/manual")
def create_manual_order(body: ManualOrderIn, user: User = Depends(admin),
                        db: Session = Depends(get_db)) -> dict:
    """Record an off-site sale as a paid order and deliver what it includes."""
    is_custom = body.sku == billing.CUSTOM_SKU
    product = billing.PRODUCTS.get(body.sku)
    if not is_custom and product is None:
        raise HTTPException(400, f"Unknown product '{body.sku}'.")
    amount = body.amount_paise if body.amount_paise is not None else (
        None if is_custom else product.amount_paise)
    if amount is None:
        raise HTTPException(400, "Enter the amount received.")

    try:
        customer, created = _manual_customer(db, body.email, body.name, body.phone)

        if not body.force:
            recent = db.execute(select(Order).where(
                Order.user_id == customer.id, Order.provider == "manual",
                Order.sku == body.sku, Order.amount_paise == amount,
                Order.created_at >= utcnow() - _MANUAL_DUP_WINDOW,
            ).order_by(Order.id.desc())).scalars().first()
            if recent is not None:
                raise HTTPException(
                    409, f"An identical manual order (#{recent.id}) was recorded "
                         "under two minutes ago. Tick “record anyway” "
                         "if this is a second sale.")

        birth = _manual_birth(db, customer, body.birth) if body.birth else None
        order = billing.create_manual_order(
            db, customer, user, sku=body.sku, amount_paise=amount,
            title=body.title, credits=body.credits, method=body.method.strip().lower(),
            reference=body.reference, note=body.note,
            birth_id=birth.id if birth else None)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(400, str(exc))
    except HTTPException:
        db.rollback()          # do not leave a half-made customer behind
        raise

    warnings = []
    if product is not None and product.kind == "kundali" and birth is None:
        warnings.append("No birth details were entered — the astrologer will "
                        "have nothing to work from until they are added.")
    return {
        "ok": True,
        "order": _manual_order_dict(order, customer, user.email),
        "customer": {"id": customer.id, "email": customer.email,
                     "name": customer.name, "created": created,
                     "credits": balance(db, customer.id)},
        "birth": _birth_dict(birth) if birth else None,
        "warnings": warnings,
    }


@router.get("/admin/orders/manual")
def list_manual_orders(limit: int = 30, _: User = Depends(admin),
                       db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(Order, User).outerjoin(User, User.id == Order.user_id)
        .where(Order.provider == "manual").order_by(Order.id.desc())
        .limit(max(1, min(limit, 100)))
    ).all()
    admin_ids = {o.verified_by for o, _u in rows if o.verified_by}
    admins = ({a.id: a.email for a in db.execute(
        select(User).where(User.id.in_(admin_ids))).scalars()} if admin_ids else {})
    return {"orders": [_manual_order_dict(o, u, admins.get(o.verified_by, ""))
                       for o, u in rows]}


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
    existing = coupons.find(db, code)
    if existing is not None:
        if existing.deleted_at is not None:
            raise HTTPException(
                409, f"Coupon '{code}' was deleted earlier. Restore it from the "
                     "Deleted list, or choose a different code.")
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
    if coupon.deleted_at is not None:
        raise HTTPException(409, "This coupon is deleted. Restore it before editing.")

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
    """Delete = hide and disable, never destroy.

    The row stays so the admin can still list it (the Deleted filter) and
    restore it, its code stays reserved, and any redemption trail survives.
    Idempotent: deleting an already-deleted coupon changes nothing.
    """
    coupon = db.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(404, "Coupon not found.")

    if coupon.deleted_at is None:
        coupon.deleted_at = utcnow()
        coupon.active = False
        db.commit()
    return {"ok": True, "deleted": True, "coupon": coupons.to_dict(db, coupon)}


@router.post("/admin/coupons/{coupon_id}/restore")
def admin_restore_coupon(coupon_id: int, _: User = Depends(admin),
                         db: Session = Depends(get_db)) -> dict:
    """Bring a deleted coupon back — as PAUSED, not live.

    A coupon someone chose to delete should not start discounting orders again
    the instant it is restored; the admin resumes it deliberately.
    """
    coupon = db.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(404, "Coupon not found.")
    if coupon.deleted_at is not None:
        coupon.deleted_at = None
        coupon.active = False
        db.commit()
    return {"ok": True, "coupon": coupons.to_dict(db, coupon)}


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


# --------------------------------------------------------------------------
# Admin — Metrics, Users, Questions & Health
# --------------------------------------------------------------------------

class CreditAdjustIn(BaseModel):
    delta: int
    note: str = ""


class UserBlockIn(BaseModel):
    blocked: bool
    reason: str = ""             # required when blocking; ignored when unblocking


class GrantIn(BaseModel):
    """Give a user something without a payment: question credits, or a whole
    product (recorded as a ₹0 "comp" order). A note is always required."""

    kind: str                    # "credits" | "product"
    credits: int = 0
    sku: str = ""
    note: str


@router.get("/admin/metrics")
def admin_metrics(_: User = Depends(admin), db: Session = Depends(get_db)) -> dict:
    """Revenue, order volumes, user statistics, and recent activity."""
    now = dt.datetime.now(dt.timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 1. Revenue
    # Complimentary grants ("comp") are paid ₹0 orders; they are not sales, so
    # they must not inflate order counts or the product breakdown.
    paid_stmt = select(Order).where(Order.status == OrderStatus.paid,
                                    Order.provider != "comp")
    all_paid = db.execute(paid_stmt).scalars().all()

    rev_all_paise = sum(o.amount_paise for o in all_paid)
    def _paid_since(o: Order, since: dt.datetime) -> bool:
        # SQLite hands timestamps back naive (Postgres returns them aware);
        # everything is stored UTC, so a naive value is UTC.
        at = o.paid_at
        if at is None:
            return False
        if at.tzinfo is None:
            at = at.replace(tzinfo=dt.timezone.utc)
        return at >= since

    rev_today_paise = sum(o.amount_paise for o in all_paid if _paid_since(o, today_start))
    rev_month_paise = sum(o.amount_paise for o in all_paid if _paid_since(o, month_start))

    # 2. Total counts
    total_users = db.execute(select(func.count(User.id))).scalar_one() or 0
    total_questions = db.execute(select(func.count(QuestionLog.id))).scalar_one() or 0
    total_paid_orders = len(all_paid)

    # 3. Product breakdown
    sku_counts: dict[str, dict] = {}
    for o in all_paid:
        sku = o.sku or "other"
        if sku not in sku_counts:
            sku_counts[sku] = {"sku": sku, "title": o.title or sku, "count": 0, "revenue_paise": 0}
        sku_counts[sku]["count"] += 1
        sku_counts[sku]["revenue_paise"] += o.amount_paise

    # 4. Recent orders
    recent_orders_rows = db.execute(
        select(Order, User)
        .outerjoin(User, User.id == Order.user_id)
        .order_by(Order.created_at.desc())
        .limit(15)
    ).all()

    recent_orders = []
    for o, u in recent_orders_rows:
        recent_orders.append({
            "id": o.id,
            "sku": o.sku,
            "title": o.title,
            "amount_paise": o.amount_paise,
            "status": o.status.value,
            "buyer_email": u.email if u else "anonymous",
            "buyer_name": u.name if u else "",
            "provider": o.provider,
            "created_at": o.created_at.strftime("%d %b %Y, %H:%M") if o.created_at else "—",
            "paid_at": o.paid_at.strftime("%d %b %Y, %H:%M") if o.paid_at else None,
        })

    return {
        "revenue_all_rupees": rev_all_paise / 100,
        "revenue_today_rupees": rev_today_paise / 100,
        "revenue_month_rupees": rev_month_paise / 100,
        "total_users": total_users,
        "total_questions": total_questions,
        "total_paid_orders": total_paid_orders,
        "products": list(sku_counts.values()),
        "recent_orders": recent_orders,
    }


@router.get("/admin/users")
def admin_users(q: str = "", limit: int = 50, _: User = Depends(admin),
                db: Session = Depends(get_db)) -> dict:
    """Search and manage registered users."""
    stmt = select(User)
    if q.strip():
        search = f"%{q.strip().lower()}%"
        stmt = stmt.where((func.lower(User.email).like(search)) | (func.lower(User.name).like(search)))
    
    users = db.execute(stmt.order_by(User.created_at.desc()).limit(min(limit, 100))).scalars().all()

    results = []
    for u in users:
        # Questions asked count
        q_count = db.execute(
            select(func.count(QuestionLog.id)).where(QuestionLog.user_id == u.id)
        ).scalar_one() or 0

        # Paid orders count & spend
        paid_orders = db.execute(
            select(Order).where(Order.user_id == u.id, Order.status == OrderStatus.paid,
                                Order.provider != "comp")
        ).scalars().all()
        spent_rupees = sum(o.amount_paise for o in paid_orders) / 100

        results.append({
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "phone": u.phone,
            "provider": u.provider,
            "is_admin": u.is_admin,
            "blocked": u.blocked,
            "blocked_reason": u.blocked_reason or "",
            "balance": balance(db, u.id),
            "questions_count": q_count,
            "orders_count": len(paid_orders),
            "spent_rupees": spent_rupees,
            "created_at": u.created_at.strftime("%d %b %Y, %H:%M") if u.created_at else "—",
            "last_seen_at": u.last_seen_at.strftime("%d %b %Y, %H:%M") if u.last_seen_at else "—",
        })

    return {"users": results, "count": len(results)}


@router.post("/admin/users/{user_id}/credits")
def admin_adjust_credits(user_id: int, body: CreditAdjustIn, admin_user: User = Depends(admin),
                         db: Session = Depends(get_db)) -> dict:
    """Manual credit addition or subtraction with audit note."""
    target_user = db.get(User, user_id)
    if target_user is None:
        raise HTTPException(404, "User not found.")
    if body.delta == 0:
        raise HTTPException(400, "The adjustment must not be zero.")
    if abs(body.delta) > 10_000:
        raise HTTPException(400, "That adjustment is unreasonably large.")
    # A deduction that would leave a negative balance is almost always a typo
    # (an extra digit), and a negative balance is meaningless to the customer.
    if body.delta < 0 and balance(db, user_id) + body.delta < 0:
        raise HTTPException(
            400, f"That would take the balance below zero (it is "
                 f"{balance(db, user_id)}).")

    note = f"Admin ({admin_user.email}): {body.note.strip()}" if body.note.strip() else f"Admin adjustment by {admin_user.email}"
    grant(db, user_id, body.delta, EntryKind.admin_adjust, note=note[:255])
    db.commit()

    return {"ok": True, "user_id": user_id, "new_balance": balance(db, user_id)}


@router.post("/admin/users/{user_id}/grant")
def admin_grant(user_id: int, body: GrantIn, admin_user: User = Depends(admin),
                db: Session = Depends(get_db)) -> dict:
    """Give a user something for free, with the reason on the record.

    credits  — appended to the ledger as an admin adjustment.
    product  — a complimentary order: PAID at ₹0 with provider "comp", so a
               kundali enters the astrologer's queue and a report/book unlocks,
               exactly as if bought, but it is never counted as a sale.
    """
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(404, "User not found.")
    note = body.note.strip()
    if len(note) < 3:
        raise HTTPException(400, "Say why you are granting this (a short note is required).")

    if body.kind == "credits":
        if not 1 <= body.credits <= 1000:
            raise HTTPException(400, "Grant between 1 and 1,000 question credits at a time.")
        grant(db, target.id, body.credits, EntryKind.admin_adjust,
              note=f"Grant by {admin_user.email}: {note}"[:255])
        db.commit()
        return {"ok": True, "kind": "credits", "new_balance": balance(db, target.id)}

    if body.kind == "product":
        if body.sku not in billing.PRODUCTS:
            raise HTTPException(400, f"Unknown product '{body.sku}'.")
        try:
            order = billing.create_manual_order(
                db, target, admin_user, sku=body.sku, amount_paise=0, method="other",
                note=note, provider="comp")
        except ValueError as exc:
            db.rollback()
            raise HTTPException(400, str(exc))
        return {"ok": True, "kind": "product", "order": _order_dict(order),
                "new_balance": balance(db, target.id)}

    raise HTTPException(400, "kind must be 'credits' or 'product'.")


@router.get("/admin/users/{user_id}")
def admin_user_detail(user_id: int, _: User = Depends(admin),
                      db: Session = Depends(get_db)) -> dict:
    """Everything the admin wants in front of them before acting on an account."""
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(404, "User not found.")

    def when(d):
        return d.strftime("%d %b %Y, %H:%M") if d else ""

    ledger = db.execute(
        select(CreditEntry).where(CreditEntry.user_id == u.id)
        .order_by(CreditEntry.id.desc()).limit(30)).scalars().all()
    orders = db.execute(
        select(Order).where(Order.user_id == u.id)
        .order_by(Order.id.desc()).limit(20)).scalars().all()
    feedback = db.execute(
        select(Feedback).where(Feedback.user_id == u.id)
        .order_by(Feedback.id.desc()).limit(5)).scalars().all()
    blocker = db.get(User, u.blocked_by) if u.blocked_by else None

    return {
        "user": {
            "id": u.id, "email": u.email, "name": u.name, "phone": u.phone,
            "provider": u.provider, "is_admin": u.is_admin,
            "created_at": when(u.created_at), "last_seen_at": when(u.last_seen_at),
            "blocked": u.blocked, "blocked_reason": u.blocked_reason or "",
            "blocked_at": when(u.blocked_at),
            "blocked_by": blocker.email if blocker else "",
        },
        "balance": balance(db, u.id),
        "questions_count": db.execute(
            select(func.count(QuestionLog.id)).where(QuestionLog.user_id == u.id)
        ).scalar_one() or 0,
        "births_count": db.execute(
            select(func.count(BirthProfile.id)).where(BirthProfile.user_id == u.id)
        ).scalar_one() or 0,
        "ledger": [{"id": e.id, "delta": e.delta, "kind": e.kind.value,
                    "note": e.note, "at": when(e.created_at)} for e in ledger],
        "orders": [{"id": o.id, "sku": o.sku, "title": o.title,
                    "amount": o.amount_paise // 100, "status": o.status.value,
                    "provider": o.provider, "fulfilment": o.fulfilment.value,
                    "at": when(o.paid_at or o.created_at)} for o in orders],
        "feedback": [{"id": f.id, "category": f.category, "rating": f.rating,
                      "message": f.message[:200], "status": f.status,
                      "at": when(f.created_at)} for f in feedback],
    }


@router.post("/admin/users/{user_id}/block")
def admin_block_user(user_id: int, body: UserBlockIn, admin_user: User = Depends(admin),
                     db: Session = Depends(get_db)) -> dict:
    """Block or unblock a user account."""
    target_user = db.get(User, user_id)
    if target_user is None:
        raise HTTPException(404, "User not found.")
    if target_user.id == admin_user.id:
        raise HTTPException(400, "You cannot block yourself.")
    if target_user.is_admin:
        raise HTTPException(
            400, "Administrators cannot be blocked. Remove their admin access first.")

    if body.blocked:
        reason = body.reason.strip()
        if len(reason) < 3:
            raise HTTPException(400, "Give a reason for the block (it is kept on the account).")
        target_user.blocked = True
        target_user.blocked_reason = reason[:255]
        target_user.blocked_at = utcnow()
        target_user.blocked_by = admin_user.id
    else:
        target_user.blocked = False
        target_user.blocked_reason = None
        target_user.blocked_at = None
        target_user.blocked_by = None
    db.commit()
    return {"ok": True, "user_id": user_id, "blocked": target_user.blocked,
            "blocked_reason": target_user.blocked_reason or ""}


@router.get("/admin/questions")
def admin_questions(q: str = "", limit: int = 50, _: User = Depends(admin),
                    db: Session = Depends(get_db)) -> dict:
    """Feed of recent user questions and consultations."""
    stmt = select(QuestionLog, User).outerjoin(User, User.id == QuestionLog.user_id)
    if q.strip():
        search = f"%{q.strip().lower()}%"
        stmt = stmt.where((func.lower(QuestionLog.question).like(search)) | (func.lower(User.email).like(search)))

    rows = db.execute(stmt.order_by(QuestionLog.created_at.desc()).limit(min(limit, 100))).all()
    questions = []
    for q_log, u in rows:
        questions.append({
            "id": q_log.id,
            "user_id": q_log.user_id,
            "user_email": u.email if u else "anonymous",
            "question": q_log.question,
            "answer_preview": (q_log.answer[:140] + "...") if q_log.answer and len(q_log.answer) > 140 else (q_log.answer or ""),
            "topic": q_log.topic,
            "verdict": q_log.verdict,
            "language": q_log.language,
            "asked_at": q_log.created_at.strftime("%d %b %Y, %H:%M") if q_log.created_at else "—",
        })
    return {"questions": questions}


@router.get("/admin/system-health")
def admin_system_health(_: User = Depends(admin), db: Session = Depends(get_db)) -> dict:
    """Live diagnostic health check of the platform."""
    from . import gateways
    from .astro import panchang

    # Check ephemeris
    swe_active = panchang.swe is not None

    # Check LLM key
    llm_configured = bool(os.getenv("ANTHROPIC_API_KEY"))

    # Check DB
    db_ok = True
    try:
        db.execute(select(func.count(User.id))).scalar_one()
    except Exception:
        db_ok = False

    return {
        "status": "healthy" if (db_ok and swe_active and llm_configured) else "degraded",
        "database": {"ok": db_ok, "driver": db.bind.dialect.name if db.bind else "unknown"},
        "ephemeris": {"ok": swe_active, "engine": "Swiss Ephemeris / pyswisseph" if swe_active else "offline"},
        "llm": {"ok": llm_configured, "provider": "Anthropic Claude"},
        "gateways": gateways.status(),
    }
