"""User feedback: the /feedback page's API, and the admin inbox behind it.

Kept out of api_account.py, which is already the money path and long enough.
Feedback is deliberately for signed-in users only: it is a small, low-traffic
form with no CAPTCHA, and requiring an account is what keeps it from becoming
a spam sink. Someone who cannot sign in can still write to the support address
shown on the page.
"""

from __future__ import annotations

import datetime as dt
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import auth, mail
from .api_account import admin, get_db, me
from .db import FEEDBACK_CATEGORIES, FEEDBACK_STATUSES, Feedback, User, utcnow

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

MAX_PER_HOUR = 5             # per user — a real person rarely sends more than one
MIN_LEN, MAX_LEN = 10, 2000


class FeedbackIn(BaseModel):
    category: str = "general"
    rating: int | None = None          # 1-5, optional
    message: str
    page: str = ""                     # where they came from, e.g. "/" or "/admin"
    allow_contact: bool = True


class FeedbackPatch(BaseModel):
    status: str | None = None
    admin_note: str | None = None


def _when(d: dt.datetime | None) -> str:
    return d.strftime("%d %b %Y, %H:%M") if d else ""


@router.post("/feedback")
def submit_feedback(body: FeedbackIn, user: User = Depends(me),
                    db: Session = Depends(get_db)) -> dict:
    category = body.category.strip().lower()
    if category not in FEEDBACK_CATEGORIES:
        raise HTTPException(400, f"category must be one of {list(FEEDBACK_CATEGORIES)}")
    if body.rating is not None and not 1 <= body.rating <= 5:
        raise HTTPException(400, "The rating must be between 1 and 5.")
    message = body.message.strip()
    if len(message) < MIN_LEN:
        raise HTTPException(400, f"Please write a little more (at least {MIN_LEN} characters).")
    if len(message) > MAX_LEN:
        raise HTTPException(400, f"Please keep it under {MAX_LEN} characters.")

    recent = db.execute(
        select(Feedback).where(
            Feedback.user_id == user.id,
            Feedback.created_at >= utcnow() - dt.timedelta(hours=1),
        ).order_by(Feedback.id.desc())
    ).scalars().all()
    # A double-click, or a resubmit after a slow response, must not file it twice.
    for f in recent:
        if f.message == message and f.category == category:
            return {"ok": True, "id": f.id, "duplicate": True}
    if len(recent) >= MAX_PER_HOUR:
        raise HTTPException(
            429, "You have sent several messages in the last hour. "
                 "Please try again a little later.")

    row = Feedback(
        user_id=user.id, category=category, rating=body.rating, message=message,
        page=body.page.strip()[:120], allow_contact=bool(body.allow_contact))
    db.add(row)
    db.commit()

    # Best-effort: SMTP may be unconfigured, and the admin inbox is the source
    # of truth either way. A mail failure must never fail the submission.
    try:
        mail.send(
            list(auth.admin_emails()),
            f"Feedback ({category}) from {user.email or 'a user'}",
            f"{'★' * (body.rating or 0)}{'  ' if body.rating else ''}{category}\n"
            f"From: {user.name or ''} <{user.email}>"
            f"{'' if body.allow_contact else '  (asked not to be contacted)'}\n\n"
            f"{message}\n\nRead and handle it at /admin → Feedback.",
        )
    except Exception:
        log.warning("feedback notification failed", exc_info=True)
    return {"ok": True, "id": row.id, "duplicate": False}


@router.get("/feedback/mine")
def my_feedback(user: User = Depends(me), db: Session = Depends(get_db)) -> dict:
    """The user's own recent submissions and whether we have dealt with them.

    Internal notes are never included — those are for the operator.
    """
    rows = db.execute(
        select(Feedback).where(Feedback.user_id == user.id)
        .order_by(Feedback.id.desc()).limit(10)
    ).scalars().all()
    return {"feedback": [{
        "id": f.id, "category": f.category, "rating": f.rating,
        "message": f.message[:160], "status": f.status, "at": _when(f.created_at),
    } for f in rows]}


# --------------------------------------------------------------------------
# Admin inbox
# --------------------------------------------------------------------------

def _item(f: Feedback, u: User | None) -> dict:
    return {
        "id": f.id, "category": f.category, "rating": f.rating, "message": f.message,
        "page": f.page, "allow_contact": f.allow_contact, "status": f.status,
        "admin_note": f.admin_note, "at": _when(f.created_at),
        "handled_at": _when(f.handled_at),
        "user_id": f.user_id,
        "email": u.email if u else "", "name": u.name if u else "",
    }


@router.get("/admin/feedback")
def admin_list_feedback(status: str = "all", q: str = "", limit: int = 100,
                        _: User = Depends(admin), db: Session = Depends(get_db)) -> dict:
    stmt = select(Feedback, User).outerjoin(User, User.id == Feedback.user_id)
    if status in FEEDBACK_STATUSES:
        stmt = stmt.where(Feedback.status == status)
    if q.strip():
        like = f"%{q.strip().lower()}%"
        stmt = stmt.where(func.lower(Feedback.message).like(like)
                          | func.lower(User.email).like(like)
                          | func.lower(User.name).like(like))
    rows = db.execute(stmt.order_by(Feedback.id.desc()).limit(max(1, min(limit, 200)))).all()

    counts = {s: 0 for s in FEEDBACK_STATUSES}
    for s, n in db.execute(select(Feedback.status, func.count(Feedback.id))
                           .group_by(Feedback.status)).all():
        counts[s] = n
    counts["all"] = sum(counts.values())
    return {"items": [_item(f, u) for f, u in rows], "counts": counts}


@router.patch("/admin/feedback/{feedback_id}")
def admin_update_feedback(feedback_id: int, body: FeedbackPatch,
                          admin_user: User = Depends(admin),
                          db: Session = Depends(get_db)) -> dict:
    f = db.get(Feedback, feedback_id)
    if f is None:
        raise HTTPException(404, "Feedback not found.")
    fields = body.model_dump(exclude_unset=True)
    if fields.get("status") is not None:
        if fields["status"] not in FEEDBACK_STATUSES:
            raise HTTPException(400, f"status must be one of {list(FEEDBACK_STATUSES)}")
        f.status = fields["status"]
        f.handled_by = admin_user.id
        f.handled_at = utcnow() if f.status != "new" else None
    if fields.get("admin_note") is not None:
        f.admin_note = fields["admin_note"].strip()[:2000]
    db.commit()
    return {"ok": True, "item": _item(f, db.get(User, f.user_id))}
