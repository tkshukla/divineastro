"""Database models.

SQLite in development, Postgres in production — set ASTRO_DATABASE_URL to swap.
SQLAlchemy 2.0 style throughout so the move is a connection-string change.

Design notes that matter for a paid product:

* **Credits are a ledger, not a counter.** Every grant and every spend is an
  immutable row. The balance is the sum. When a customer disputes a charge or a
  webhook fires twice, you can prove exactly what happened — a single mutable
  `questions_left` integer cannot.
* **Payments are idempotent.** Razorpay retries webhooks. `provider_payment_id`
  is unique, so a replayed webhook cannot grant credits twice.
* **Birth data is personal data** under the DPDP Act. It lives in one table,
  linked to a user, and is deletable on request.
"""

from __future__ import annotations

import datetime as dt
import enum
import os
import secrets
from pathlib import Path

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Index, Integer, MetaData, String, Text,
    UniqueConstraint, create_engine, func, select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

DB_URL = os.environ.get(
    "ASTRO_DATABASE_URL",
    f"sqlite:///{Path(__file__).resolve().parent.parent / 'data' / 'astro.db'}",
)

engine = create_engine(
    DB_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
)


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def aware(value: dt.datetime | None) -> dt.datetime | None:
    """Coerce a datetime read back from the database to UTC-aware.

    SQLite has no timezone type, so `DateTime(timezone=True)` round-trips as
    naive; Postgres round-trips as aware. Comparing the two raises. Every
    comparison against `utcnow()` goes through here so the code is correct on
    both backends.
    """
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)


# SQLite cannot ALTER a table in place, so Alembic rebuilds it ("batch mode"),
# and a rebuild can only reproduce constraints that have names. Without a
# convention, SQLAlchemy leaves foreign keys anonymous and every future
# migration touching this table fails with "Constraint must have a name".
# Setting it once here names them all, forever.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# --------------------------------------------------------------------------
# Users and authentication
# --------------------------------------------------------------------------

class User(Base):
    """An account, identified by the social provider that vouched for it.

    Identity is (provider, provider_sub) — a provider's subject id is stable
    even if the person changes their email. `email` is kept for contact and for
    linking a second provider to the same human, and `phone` is optional
    contact detail for hand-written kundali orders, never a login credential.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), default="", index=True)
    name: Mapped[str] = mapped_column(String(120), default="")
    picture: Mapped[str] = mapped_column(String(400), default="")
    provider: Mapped[str] = mapped_column(String(20), default="")
    provider_sub: Mapped[str] = mapped_column(String(128), default="", index=True)
    phone: Mapped[str] = mapped_column(String(20), default="")
    language: Mapped[str] = mapped_column(String(5), default="en")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    entries: Mapped[list["CreditEntry"]] = relationship(back_populates="user")
    births: Mapped[list["BirthProfile"]] = relationship(back_populates="user")

    __table_args__ = (
        UniqueConstraint("provider", "provider_sub", name="uq_provider_identity"),
    )


# --------------------------------------------------------------------------
# Birth data (personal data — deletable)
# --------------------------------------------------------------------------

class BirthProfile(Base):
    __tablename__ = "birth_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    label: Mapped[str] = mapped_column(String(120), default="")
    name: Mapped[str] = mapped_column(String(120), default="")
    date: Mapped[str] = mapped_column(String(10))         # YYYY-MM-DD
    time: Mapped[str] = mapped_column(String(5))          # HH:MM
    time_known: Mapped[bool] = mapped_column(Boolean, default=True)
    # 'female' | 'male' | 'other' | '' (unstated). Several classical Jyotish
    # rules — notably which houses are read for a spouse — are stated in
    # gendered terms, so the reading asks rather than assumes. Empty is a valid
    # answer and must stay valid: nobody is forced to declare one.
    gender: Mapped[str] = mapped_column(String(10), default="")
    place: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()
    timezone: Mapped[str] = mapped_column(String(64))
    zodiac: Mapped[str] = mapped_column(String(12), default="sidereal")
    ayanamsa: Mapped[str] = mapped_column(String(24), default="lahiri")
    house_system: Mapped[str] = mapped_column(String(24), default="Whole Sign")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="births")


# --------------------------------------------------------------------------
# Credits — an append-only ledger
# --------------------------------------------------------------------------

class EntryKind(str, enum.Enum):
    signup_bonus = "signup_bonus"
    purchase = "purchase"
    question = "question"          # negative
    refund = "refund"
    admin_adjust = "admin_adjust"


class CreditEntry(Base):
    __tablename__ = "credit_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    delta: Mapped[int] = mapped_column(Integer)            # +granted / -spent
    kind: Mapped[EntryKind] = mapped_column(Enum(EntryKind))
    note: Mapped[str] = mapped_column(String(255), default="")
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="entries")


# --------------------------------------------------------------------------
# Questions asked (also the source for the PDF export)
# --------------------------------------------------------------------------

class QuestionLog(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    birth_id: Mapped[int | None] = mapped_column(ForeignKey("birth_profiles.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    answer_engine: Mapped[str] = mapped_column(Text, default="")
    topic: Mapped[str] = mapped_column(String(40), default="")
    verdict: Mapped[str] = mapped_column(String(60), default="")
    score: Mapped[float] = mapped_column(default=0.0)
    language: Mapped[str] = mapped_column(String(5), default="en")
    charged: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# --------------------------------------------------------------------------
# Coupons
# --------------------------------------------------------------------------

class CouponKind(str, enum.Enum):
    percent = "percent"                # value = 1..100
    flat = "flat"                      # value = paise off
    extra_credits = "extra_credits"    # value = bonus credits, price unchanged


class Coupon(Base):
    """A discount code.

    Money here follows the same rule as everywhere else: integer paise, never
    floats. `times_redeemed` is a denormalised counter kept in step with the
    `coupon_redemptions` rows — the rows are the truth, the counter is for
    cheap limit checks and admin listings.
    """

    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    kind: Mapped[CouponKind] = mapped_column(Enum(CouponKind), default=CouponKind.percent)
    value: Mapped[int] = mapped_column(Integer, default=0)

    min_amount_paise: Mapped[int] = mapped_column(Integer, default=0)
    # Caps a percent discount. NULL = uncapped.
    max_discount_paise: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    # "all" | "questions" | "kundali" | a specific sku
    applies_to: Mapped[str] = mapped_column(String(40), default="all")

    active: Mapped[bool] = mapped_column(Boolean, default=True)
    starts_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None)
    expires_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None)

    max_redemptions: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None)      # NULL = unlimited
    max_per_user: Mapped[int] = mapped_column(Integer, default=1)
    times_redeemed: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CouponRedemption(Base):
    """One row per order that actually consumed a coupon.

    `order_id` is UNIQUE: a replayed payment webhook cannot record a second
    redemption for the same order, so the counter cannot drift upwards.
    """

    __tablename__ = "coupon_redemptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    discount_paise: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (
        UniqueConstraint("order_id", name="uq_redemption_order"),
        Index("ix_redemption_coupon_user", "coupon_id", "user_id"),
    )


# --------------------------------------------------------------------------
# Orders and payments
# --------------------------------------------------------------------------

class OrderStatus(str, enum.Enum):
    created = "created"
    # The customer says they paid by UPI and gave a reference. Nothing is
    # granted in this state — a human must confirm it against the bank
    # statement first, or anyone could type twelve digits for free credits.
    awaiting_verification = "awaiting_verification"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"
    rejected = "rejected"


class FulfilStatus(str, enum.Enum):
    not_applicable = "not_applicable"
    pending = "pending"
    in_progress = "in_progress"
    delivered = "delivered"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    sku: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(160))
    # What the customer is ACTUALLY charged, after any coupon.
    amount_paise: Mapped[int] = mapped_column(Integer)     # store money as integers
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    # Credits granted on payment: the pack's credits plus any extra_credits
    # bonus, resolved once at order creation so a coupon edited afterwards
    # cannot change what an already-placed order pays out.
    credits: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.created)

    # Coupon trail. `original_amount_paise` is the list price; the difference
    # from `amount_paise` is `discount_paise`.
    coupon_id: Mapped[int | None] = mapped_column(
        ForeignKey("coupons.id"), nullable=True, default=None)
    discount_paise: Mapped[int] = mapped_column(Integer, default=0)
    original_amount_paise: Mapped[int] = mapped_column(Integer, default=0)

    provider: Mapped[str] = mapped_column(String(20), default="razorpay")
    provider_order_id: Mapped[str] = mapped_column(String(64), default="", index=True)
    # NULL until the gateway confirms. Nullable rather than "" because SQL
    # treats NULLs as distinct in a UNIQUE index — many unpaid orders can
    # coexist, while a captured payment id can still only ever be used once.
    provider_payment_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default=None)

    # Hand-written kundali fulfilment (digital scan delivery)
    fulfilment: Mapped[FulfilStatus] = mapped_column(
        Enum(FulfilStatus), default=FulfilStatus.not_applicable)
    fulfil_note: Mapped[str] = mapped_column(Text, default="")
    delivered_path: Mapped[str] = mapped_column(String(255), default="")
    birth_id: Mapped[int | None] = mapped_column(ForeignKey("birth_profiles.id"), nullable=True)
    report_topic: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)

    # --- manual UPI collection -------------------------------------------
    # What the customer claims, and who checked it.
    utr: Mapped[str | None] = mapped_column(String(32), nullable=True)
    utr_submitted_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)
    verify_note: Mapped[str] = mapped_column(String(255), default="")

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    paid_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        # A gateway payment id may only ever be recorded once, so a replayed
        # webhook cannot grant a second batch of credits.
        UniqueConstraint("provider", "provider_payment_id", name="uq_provider_payment"),
        # A UPI reference likewise belongs to exactly one order — this is what
        # stops the same UTR being claimed against several purchases. NULL is
        # distinct in SQL, so unpaid orders do not collide.
        UniqueConstraint("utr", name="uq_order_utr"),
    )


class WebhookEvent(Base):
    """Raw webhook receipts — the audit trail when a payment is disputed."""

    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(20), default="razorpay")
    event_id: Mapped[str] = mapped_column(String(80), unique=True)
    event_type: Mapped[str] = mapped_column(String(60), default="")
    payload: Mapped[str] = mapped_column(Text)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def init_db() -> None:
    """Bring the database up to the latest migration.

    Alembic rather than `create_all()`: once real customers exist, adding a
    column must not mean dropping the database. Running it at startup keeps
    deployment to one step, which is right for a single-instance service — if
    this ever scales to several app servers, move it to a release job so two
    instances cannot migrate concurrently.
    """
    if DB_URL.startswith("sqlite"):
        Path(DB_URL.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)

    from alembic import command
    from alembic.config import Config

    root = Path(__file__).resolve().parent.parent
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "migrations"))
    cfg.set_main_option("sqlalchemy.url", DB_URL)
    command.upgrade(cfg, "head")


def session() -> Session:
    return Session(engine, expire_on_commit=False)


def balance(db: Session, user_id: int) -> int:
    """Current credit balance = sum of the ledger."""
    total = db.execute(
        select(func.coalesce(func.sum(CreditEntry.delta), 0))
        .where(CreditEntry.user_id == user_id)
    ).scalar_one()
    return int(total)


def grant(db: Session, user_id: int, amount: int, kind: EntryKind,
          note: str = "", order_id: int | None = None) -> CreditEntry:
    entry = CreditEntry(user_id=user_id, delta=amount, kind=kind,
                        note=note, order_id=order_id)
    db.add(entry)
    return entry


def new_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)
