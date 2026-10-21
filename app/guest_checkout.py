"""Buying without signing in (DIVASTRO-158).

277 people opened the sign-in sheet in 14 days and 30 signed up: payment must not
wait behind account creation. A signed-out visitor may buy a product listed in
billing.GUEST_CHECKOUT_SKUS (today the Rs 21 Starter) with only an email address,
and optionally a phone number.

THE ORDER BELONGS TO A USER, AS EVERY ORDER DOES (orders.user_id stays NOT NULL, and
every price, amount and signature check in billing / api_account runs unchanged):

* the address already has an account whose email is proof of the mailbox (Google,
  Apple, dev, email-code, an admin-recorded "manual" customer, or an earlier guest
  order): the order is that account's. Nothing is said about it to the buyer;
* otherwise a placeholder account is created: provider="guest",
  provider_sub="guest:<address>", no password, no welcome questions,
  signup_source="guest_checkout" (not counted as a sign-up). It is NEVER signed in
  to: no route issues a session for it. The first sign-in that proves the address
  (an email code, or Google / Apple: `adopt`) turns it into that person's real
  account, with the welcome questions and the sign-up recorded then, so the order
  and its answers are waiting in My orders / My questions. A Microsoft sign-in does
  not adopt it (its email claim is not proof of the mailbox; see email_auth).

SECURITY. A guest checkout never signs anyone in and never shows anything of an
account: the checkout's reply is the same whether the address is new or known, the
gateway is shown only the typed address and phone (never the account's name or
number), and the order page shows only this order. The one unavoidable signal is
the Starter's once-per-account rule: a known address that already has a Starter is
refused with one generic sentence ("cannot be bought for this address"), the same
one a suspended account gets, never "this address has an account" / "already bought".

THE STARTER'S QUESTIONS. The visitor cast their chart signed out, so the checkout
carries that chart's birth details (taken from the server's own chart session, not
from the browser) on the order (`orders.guest_json`). After payment the buyer types
their 3 questions on the order page, which is reached with the order's TOKEN: an
HMAC-signed (itsdangerous, ASTRO_SECRET_KEY, its own salt), 60-day value naming the
order, not guessable from the order id. The browser gets it with the checkout reply
(kept in this tab's storage across the PayU round trip), PayU's verified return adds
it to the redirect, and it is emailed to the buyer as a link once the order is paid
(so a closed tab, or a payment settled later by webhook or by the admin's UPI check,
still reaches the questions). Each question is an ordinary emailed_answer_jobs row
(order_id = this order, email = the order's address), answered and emailed by the
existing worker; the order page shows each question's status, never the answer text
(that goes only to the mailbox), and the answer is written without the account's
other conversations. The birth details are dropped from the order once all its
questions are in (each job drops its own copy when it is answered).

Abuse: checkout creation is rate-limited per IP address (an IPv6 /64 counts as one)
and per email address, in process memory like the sign-in limits (auth.throttled).
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import os
import re
import types

from fastapi import APIRouter, Depends, HTTPException, Request
from itsdangerous import BadSignature, URLSafeTimedSerializer
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import analytics, auth, billing, email_auth, guest, i18n, mail
from .db import (
    CreditEntry, EmailedAnswerJob, EntryKind, Order, OrderStatus, User, aware, email_balance,
    grant, session as db_session, utcnow,
)

log = logging.getLogger("astro.guest_checkout")

router = APIRouter(prefix="/api/guest")

GUEST_PROVIDER = "guest"
SIGNUP_SOURCE = "guest_checkout"
SITE_URL = os.environ.get("ASTRO_SITE_URL", "https://divineastro.org").rstrip("/")

# Accounts whose users.email proves the mailbox, so a guest order for that address
# is credited to them (the same set email_auth links to, plus earlier guest orders).
CREDIT_TO_PROVIDERS = (*email_auth.LINKABLE_PROVIDERS, "email", "manual", GUEST_PROVIDER)

TOKEN_SALT = "guest-order"
TOKEN_MAX_AGE = 60 * 24 * 60 * 60          # 60 days: covers a late UPI check and a slow reader
_signer = URLSafeTimedSerializer(auth.SECRET, salt=TOKEN_SALT)

# Checkout creations: per IP (or IPv6 /64), per address (short and daily windows).
PER_IP = (10, 60 * 60)
PER_EMAIL = (5, 60 * 60)
PER_EMAIL_DAILY = (10, 24 * 60 * 60)
_HITS_IP: dict[str, list[float]] = {}
_HITS_EMAIL: dict[str, list[float]] = {}
_HITS_EMAIL_DAY: dict[str, list[float]] = {}

MAX_QUESTION_LEN = 1000
_PHONE = re.compile(r"^\+?[0-9]{7,15}$")

# Error replies carry a code the app words in the visitor's language (acct.guestErr.*);
# `message` is the English for API clients and logs.
MESSAGES = {
    "signed_in": "You are signed in: buy from the store instead.",
    "unavailable": "This can't be bought without signing in right now.",
    "email": "Please enter a valid email address, e.g. name@gmail.com.",
    "typo": "Did you mean {s}? Please check the address.",
    "phone": "Please enter a valid phone number, or leave it empty.",
    "rate": "Too many attempts. Please wait a few minutes and try again.",
    "refused": ("This offer can't be bought for this email address. If you have bought "
                "it before, sign in with this address to see your answers."),
    "chart": "Make your free kundali first: the answers are read from it.",
    "gateway": "The payment page could not be opened. Please try again.",
    "token": "This link is not valid or has expired.",
    "not_paid": "This order is not paid yet.",
    "no_questions": "Type at least one question.",
    "too_long": "A question can be at most 1000 characters.",
    "used": "All the questions for this order have been asked.",
    "other_order": "That payment belongs to a different order.",
}


def _err(status: int, code: str, **kw) -> HTTPException:
    detail = {"code": code, "message": MESSAGES[code].format(**kw)}
    if kw:
        detail.update(kw)
    return HTTPException(status, detail)


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------------------------------
# Tokens
# --------------------------------------------------------------------------

def token_for(order: Order) -> str:
    return _signer.dumps({"o": int(order.id)})


def order_for_token(db: Session, token: str) -> Order:
    """The guest order a token names, or 404. Only guest orders have tokens."""
    try:
        data = _signer.loads(token or "", max_age=TOKEN_MAX_AGE)
        order_id = int(data["o"])
    except (BadSignature, KeyError, TypeError, ValueError):
        raise _err(404, "token") from None
    order = db.get(Order, order_id)
    if order is None or not order.guest_email:
        raise _err(404, "token")
    return order


# --------------------------------------------------------------------------
# Accounts
# --------------------------------------------------------------------------

def can_adopt(provider: str) -> bool:
    """Whether a sign-in with this provider may take over a guest placeholder."""
    return provider in email_auth.LINKABLE_PROVIDERS or provider == "email"


def adopt(db: Session, user: User, provider: str, sub: str) -> None:
    """A guest placeholder becomes the real account of whoever just proved its address.
    The welcome questions and the sign-up (attribute_signup, called by the sign-in
    route because the caller reports it as created) happen now, once."""
    user.provider, user.provider_sub = provider, sub
    user.signup_source = None
    user.signup_campaign = None
    had_bonus = db.execute(
        select(CreditEntry.id).where(CreditEntry.user_id == user.id,
                                     CreditEntry.kind == EntryKind.signup_bonus)).first()
    if had_bonus is None:
        grant(db, user.id, billing.FREE_QUESTIONS, EntryKind.signup_bonus,
              note="Welcome — free questions")
    user.adopted_guest = True          # not a column: tells the sign-in route this is a sign-up


def account_for(db: Session, addr: str, phone: str = "") -> User:
    """The account a guest order for `addr` is credited to (see the module docstring)."""
    user = db.execute(
        select(User).where(User.email == addr, User.provider.in_(CREDIT_TO_PROVIDERS))
        .order_by(User.id)).scalars().first()
    if user is None:
        user = db.execute(select(User).where(
            User.provider == "manual", User.provider_sub == f"manual:{addr}")
            .order_by(User.id)).scalars().first()
    if user is None:
        user = db.execute(select(User).where(
            User.provider == GUEST_PROVIDER, User.provider_sub == f"guest:{addr}")
        ).scalars().first()
    if user is not None:
        return user
    user = User(email=addr, name="", phone=phone, provider=GUEST_PROVIDER,
                provider_sub=f"guest:{addr}", signup_source=SIGNUP_SOURCE)
    db.add(user)
    db.flush()
    return user


# --------------------------------------------------------------------------
# Validation and limits
# --------------------------------------------------------------------------

def normalise_email(raw: str) -> str:
    try:
        return email_auth.normalise(raw, "en")
    except HTTPException as exc:
        m = re.search(r"Did you mean (\S+)\?", str(exc.detail))
        if m:
            raise _err(400, "typo", s=m.group(1)) from None
        raise _err(400, "email") from None


def normalise_phone(raw: str) -> str:
    phone = re.sub(r"[\s\-().]", "", raw or "")
    if not phone:
        return ""
    if not _PHONE.match(phone):
        raise _err(400, "phone")
    return phone


def _ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _limited(ip: str, addr: str) -> bool:
    ip_key = guest._address_key(ip)
    return (auth.throttled(_HITS_IP, ip_key, *PER_IP)
            or auth.throttled(_HITS_EMAIL, addr, *PER_EMAIL)
            or auth.throttled(_HITS_EMAIL_DAY, addr, *PER_EMAIL_DAILY))


def _note(ip: str, addr: str) -> None:
    auth.note_hit(_HITS_IP, guest._address_key(ip))
    auth.note_hit(_HITS_EMAIL, addr)
    auth.note_hit(_HITS_EMAIL_DAY, addr)


def reset_for_tests() -> None:
    _HITS_IP.clear()
    _HITS_EMAIL.clear()
    _HITS_EMAIL_DAY.clear()


def _guest_birth(session_id: str) -> dict | None:
    """The birth details of a chart THIS signed-out visitor cast (the server's own
    session), or None. A chart that belongs to an account is not theirs to send."""
    from .main import SESSIONS

    entry = SESSIONS.get(session_id or "")
    if entry is None or entry.get("user_id") is not None:
        return None
    return entry["session"].birth.to_dict()


def _payload(order: Order) -> dict:
    try:
        return json.loads(order.guest_json or "{}") or {}
    except ValueError:
        return {}


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

class CheckoutIn(BaseModel):
    sku: str
    email: str
    phone: str = ""
    session_id: str = ""
    lang: str = "en"


@router.post("/checkout")
def checkout(body: CheckoutIn, request: Request, db: Session = Depends(get_db)) -> dict:
    """Open a payment for a guest product. The reply never depends on whether the
    address already has an account."""
    if auth.current_user(request, db) is not None:
        raise _err(409, "signed_in")
    product = billing.PRODUCTS.get(body.sku)
    if product is None or body.sku not in billing.guest_checkout_skus():
        raise _err(400, "unavailable")
    addr = normalise_email(body.email)
    phone = normalise_phone(body.phone)
    lang = i18n.normalize(body.lang)

    ip = _ip(request)
    if _limited(ip, addr):
        raise _err(429, "rate")
    _note(ip, addr)

    birth = None
    if product.kind == billing.EMAIL_ANSWER_KIND:
        birth = _guest_birth(body.session_id)
        if birth is None:
            raise _err(400, "chart")

    user = account_for(db, addr, phone)
    if user.blocked:
        db.rollback()
        raise _err(409, "refused")
    if product.sku == billing.STARTER_SKU:
        st = billing.starter_status(db, user)
        if not st["available"]:
            db.rollback()
            raise _err(409, "unavailable" if st["reason"] == "disabled" else "refused")

    visitor = analytics.event_visitor(request)
    payer = types.SimpleNamespace(id=user.id, email=addr, name="", phone=phone)
    payload = {"lang": lang, "visitor": visitor}
    if birth is not None:
        payload["birth"] = birth
    try:
        order, checkout_ = billing.create_order(
            db, user, product.sku, payer=payer,
            guest={"email": addr, "phone": phone, "json": json.dumps(payload, ensure_ascii=False)})
    except billing.StarterRefused:
        db.rollback()
        raise _err(409, "refused") from None
    except ValueError:
        db.rollback()
        raise _err(400, "unavailable") from None
    except Exception as exc:                                  # noqa: BLE001
        db.rollback()
        log.error("guest checkout: gateway error: %s", exc)
        raise _err(502, "gateway") from None

    analytics.record_server_event("guest_checkout_start", product.sku, visitor)
    return {"order": _order_brief(order), "checkout": checkout_, "token": token_for(order),
            "email": addr}


def _order_brief(order: Order) -> dict:
    return {"id": order.id, "sku": order.sku, "title": order.title,
            "amount_paise": order.amount_paise, "credits": order.credits,
            "status": order.status.value}


class TokenIn(BaseModel):
    token: str


class ConfirmIn(TokenIn):
    payload: dict = Field(default_factory=dict)


@router.post("/confirm")
def confirm(body: ConfirmIn, db: Session = Depends(get_db)) -> dict:
    """The browser return of a JS / hosted gateway, for a guest order: the same checks
    as /api/orders/confirm, with the token in place of the session. PayU never comes
    here: its signed return goes to /api/payu/return, with its amount check."""
    from . import gateways

    order = order_for_token(db, body.token)
    if gateways.active().key == "payu":
        raise _err(400, "unavailable")
    claimed = (body.payload.get("payment_request_id") or body.payload.get("order_id")
               or body.payload.get("razorpay_order_id") or body.payload.get("ORDERID") or "")
    if claimed and order.provider_order_id and claimed != order.provider_order_id:
        raise _err(400, "other_order")
    if order.status != OrderStatus.paid and billing.verify_return(body.payload):
        payment_id = (body.payload.get("razorpay_payment_id")
                      or body.payload.get("TXNID") or body.payload.get("payment_id") or "")
        billing.mark_paid(db, order, payment_id)
    return status(db, order)


class UtrIn(TokenIn):
    utr_last5: str


@router.post("/upi-claim")
def upi_claim(body: UtrIn, db: Session = Depends(get_db)) -> dict:
    """Manual UPI for a guest order: like /api/orders/upi-claim, grants nothing; the
    admin's check against the bank statement does (and then emails the buyer)."""
    from . import upi

    order = order_for_token(db, body.token)
    if order.status == OrderStatus.paid:
        return status(db, order)
    suffix = upi.normalise_utr_suffix(body.utr_last5)
    if not upi.valid_utr_suffix(suffix):
        raise HTTPException(
            400, "That doesn't look like the last 5 characters of a UPI "
                 "reference. Check your payment app's confirmation screen.")
    order.utr_last5 = suffix
    order.utr_submitted_at = utcnow()
    order.status = OrderStatus.awaiting_verification
    db.commit()
    try:
        mail.send(list(auth.admin_emails()), f"UPI claim: order #{order.id}",
                  f"{order.guest_email} (guest checkout) claimed ₹{order.amount_paise / 100:.0f} "
                  f"for {order.title}, UTR ends in {suffix}. Verify at /admin.")
    except Exception:                                        # noqa: BLE001
        pass
    return status(db, order)


@router.post("/order")
def order_status(body: TokenIn, db: Session = Depends(get_db)) -> dict:
    return status(db, order_for_token(db, body.token))


def _jobs(db: Session, order: Order) -> list[EmailedAnswerJob]:
    return list(db.execute(select(EmailedAnswerJob).where(EmailedAnswerJob.order_id == order.id)
                           .order_by(EmailedAnswerJob.id)).scalars().all())


def questions_left(db: Session, order: Order) -> int:
    """How many questions this guest order can still have answered: its own credits
    minus the questions entered with it (a refunded one does not count), and never
    more than the account still holds."""
    if order.status != OrderStatus.paid:
        return 0
    product = billing.PRODUCTS.get(order.sku)
    if product is None or product.kind != billing.EMAIL_ANSWER_KIND:
        return 0
    used = db.execute(select(func.count(EmailedAnswerJob.id)).where(
        EmailedAnswerJob.order_id == order.id,
        EmailedAnswerJob.refunded.is_(False))).scalar_one()
    return max(0, min(int(order.credits or 0) - int(used), email_balance(db, order.user_id)))


def _iso(value) -> str | None:
    value = aware(value)
    return value.isoformat() if value else None


def status(db: Session, order: Order) -> dict:
    """What the order page shows: this order only, nothing else of the account."""
    product = billing.PRODUCTS.get(order.sku)
    p = _payload(order)
    birth = p.get("birth") or {}
    deadline = dt.timedelta(minutes=billing.EMAIL_ANSWER_DEADLINE_MIN)
    return {
        "ok": True,
        "order": _order_brief(order),
        "paid": order.status == OrderStatus.paid,
        "pending": order.status in (OrderStatus.created, OrderStatus.awaiting_verification),
        "kind": product.kind if product else "",
        "email": order.guest_email,
        "minutes": billing.EMAIL_ANSWER_DEADLINE_MIN,
        "chart": ({"name": birth.get("name", ""), "date": birth.get("date", ""),
                   "place": birth.get("place", "")} if birth
                  else {"name": p["chart_name"]} if p.get("chart_name") else None),
        "questions_left": questions_left(db, order),
        "questions": [{
            "question": j.question, "status": j.status, "refunded": j.refunded,
            "asked": _iso(j.created_at), "due": _iso(aware(j.created_at) + deadline),
            "delivered": _iso(j.finished_at) if j.status == "done" else None,
        } for j in _jobs(db, order)],
    }


class QuestionsIn(TokenIn):
    questions: list[str] = Field(default_factory=list)
    lang: str = "en"


@router.post("/questions")
def ask_questions(body: QuestionsIn, request: Request, db: Session = Depends(get_db)) -> dict:
    """Queue the paid order's questions (Starter): each one debits one emailed answer
    of the order's account and is answered and emailed to the order's address by the
    background worker (app/emailed_answers.py)."""
    from . import emailed_answers
    from .chart_service import BirthData

    order = order_for_token(db, body.token)
    texts = [q.strip() for q in body.questions if isinstance(q, str) and q.strip()]
    if not texts:
        raise _err(400, "no_questions")
    if any(len(q) > MAX_QUESTION_LEN for q in texts):
        raise _err(400, "too_long")
    if order.status != OrderStatus.paid:
        raise _err(409, "not_paid")
    # Serialise two submissions of the same order (Postgres; SQLite has one writer).
    order = db.execute(select(Order).where(Order.id == order.id).with_for_update()).scalar_one()
    left = questions_left(db, order)
    if left <= 0:
        raise _err(409, "used")
    p = _payload(order)
    if not p.get("birth"):
        raise _err(409, "used")
    user = db.get(User, order.user_id)
    chart = types.SimpleNamespace(birth=BirthData(**p["birth"]))
    lang = i18n.normalize(body.lang or p.get("lang"))
    visitor = analytics.event_visitor(request) or p.get("visitor", "")
    for q in texts[:left]:
        emailed_answers.enqueue(db, user, chart, q, lang, None, visitor=visitor,
                                email=order.guest_email, order_id=order.id)
        analytics.record_server_event("email_answer_queued", lang, visitor)
    if questions_left(db, order) <= 0:
        # Every question is in: the order no longer needs the birth details (each
        # job keeps its own copy until it is answered).
        p.pop("birth", None)
        p["chart_name"] = (chart.birth.name or "")[:120]
        order.guest_json = json.dumps(p, ensure_ascii=False)
        db.commit()
    return status(db, order)


# --------------------------------------------------------------------------
# After payment
# --------------------------------------------------------------------------

def link_for(order: Order, lang: str) -> str:
    q = f"?gt={token_for(order)}"
    if lang and lang != "en":
        q += f"&lang={lang}"
    return f"{SITE_URL}/{q}"


def on_paid(db: Session, order: Order) -> None:
    """Called once by billing.mark_paid when a guest order becomes paid: email the
    buyer the link to their order page, and count the purchase."""
    from .emailed_answers_text import tx

    p = _payload(order)
    lang = i18n.normalize(p.get("lang"))
    analytics.record_server_event("guest_checkout_paid", order.sku, p.get("visitor", ""))
    product = billing.PRODUCTS.get(order.sku)
    if product is None or product.kind != billing.EMAIL_ANSWER_KIND:
        return            # other guest products deliver in their own way (billing.order_email)
    link = link_for(order, lang)
    values = {"n": order.credits, "minutes": billing.EMAIL_ANSWER_DEADLINE_MIN}
    body = (f"{tx('hello', lang)}\n\n{tx('guest_body', lang, **values)}\n\n"
            f"{tx('guest_cta', lang)}: {link}\n\n{tx('guest_later', lang)}\n\n{tx('sign', lang)}\n")
    from html import escape as e
    html_body = f"""<!doctype html><html lang="{e(lang)}"><body style="margin:0;padding:0;background:#f6f3ee">
<div style="max-width:600px;margin:0 auto;padding:24px 18px;font-family:Arial,'Noto Sans',sans-serif;color:#222;font-size:16px">
<p style="margin:0 0 6px;color:#b5651d;font-weight:bold;font-size:18px">{e(tx('sign', lang))}</p>
<p style="margin:0 0 16px">{e(tx('hello', lang))}<br>{e(tx('guest_body', lang, **values))}</p>
<p style="margin:18px 0"><a href="{e(link)}" style="display:inline-block;background:#b5651d;color:#fff;text-decoration:none;padding:11px 18px;border-radius:8px;font-weight:bold">{e(tx('guest_cta', lang))}</a></p>
<p style="margin:0 0 6px;color:#555;font-size:14px">{e(tx('guest_later', lang))}</p>
</div></body></html>"""
    if not mail.send([order.guest_email], tx("guest_subject", lang), body, html_body):
        log.error("guest order %s: the order link could not be emailed", order.id)
