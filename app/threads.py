"""Conversations: a signed-in customer's past questions, grouped into threads
(DIVASTRO-170).

There is no conversation id in the schema. A question (`questions` row) or a
Starter emailed answer still being written (`emailed_answer_jobs` row with no
`questions` row yet) belongs to a conversation by its CHART:

* asked on a SAVED chart (`birth_id` set, the profile still this user's): one
  conversation per chart, key ``c<birth_id>``, however far apart the questions
  are. That is how the chat already works: the follow-up context /api/ask uses is
  "this chart's last questions" (main.py), with no time limit, so the thread
  shown is the thread the model sees, and the customer continues it by opening
  the chart again.
* asked on a chart that was NOT saved (`birth_id` NULL: a chart over the saved
  limit, a question from a guest order page, or one asked before DIVASTRO-170 made
  the app send the saved chart's id) or on a chart since deleted: nothing says
  which chart it was, so consecutive such questions form one conversation, split
  where more than SPLIT apart (12 h: an unsaved chart lives in memory for 12 h,
  main.SESSION_TTL, so a longer gap is certainly another sitting and possibly
  another chart). Key ``u<epoch seconds of its first question>``. These are
  shown READ-ONLY: the chart is gone, so there is nothing to continue on.

Items, oldest first, each one question and its answer:

* ``q<id>``: a questions row (an instant answer, or a delivered emailed one); an
  emailed one carries ``emailed`` (status done, or failed when the email could not
  be sent — the answer was kept, the credit refunded).
* ``j<id>``: an emailed job with no answer row yet: pending / running, or failed
  before an answer existed (refunded).

An emailed answer is placed at the time it was ASKED (the job's created_at), not
when its row was written, so it sits in order among the instant answers.

Everything is read with ``user_id == <the caller>``: there is no way to name
another account's rows (a key only selects among the caller's own threads).
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import billing
from .db import BirthProfile, EmailedAnswerJob, QuestionLog, aware

SPLIT = dt.timedelta(hours=12)
MAX_QUESTIONS = 500      # newest rows considered; a customer pays per question
MAX_JOBS = 200
PAGE = 50                # items per page of a thread (the newest first)


def _iso(value) -> str | None:
    value = aware(value)
    return value.isoformat() if value else None


def _items(db: Session, user_id: int) -> list[dict]:
    rows = db.execute(
        select(QuestionLog).where(QuestionLog.user_id == user_id)
        .order_by(QuestionLog.created_at.desc()).limit(MAX_QUESTIONS)
    ).scalars().all()
    jobs = db.execute(
        select(EmailedAnswerJob).where(EmailedAnswerJob.user_id == user_id)
        .order_by(EmailedAnswerJob.created_at.desc()).limit(MAX_JOBS)
    ).scalars().all()
    by_row = {j.question_id: j for j in jobs if j.question_id}
    out: list[dict] = []
    for q in rows:
        j = by_row.get(q.id)
        at = aware(j.created_at if j is not None else q.created_at)
        out.append({
            "key": f"q{q.id}", "id": q.id, "job_id": j.id if j is not None else None,
            "birth_id": q.birth_id, "question": q.question, "answer": q.answer,
            "topic": q.topic, "verdict": q.verdict, "language": q.language,
            "at": at, "emailed": None if j is None else {
                "status": j.status, "asked": _iso(j.created_at),
                "delivered": _iso(j.finished_at) if j.status == "done" else None,
                "sent": j.emailed, "refunded": j.refunded},
            "_name": j.chart_name if j is not None else "",
        })
    for j in jobs:
        if j.question_id or j.status == "done":
            continue                     # answered: it is the questions row above
        out.append({
            "key": f"j{j.id}", "id": None, "job_id": j.id, "birth_id": j.birth_id,
            "question": j.question, "answer": "", "topic": "", "verdict": "",
            "language": j.language, "at": aware(j.created_at),
            "emailed": {"status": j.status, "asked": _iso(j.created_at),
                        "due": _iso(aware(j.created_at) + dt.timedelta(
                            minutes=billing.EMAIL_ANSWER_DEADLINE_MIN)),
                        "delivered": None, "sent": False, "refunded": j.refunded},
            "_name": j.chart_name,
        })
    out.sort(key=lambda i: (i["at"], i["key"]))
    return out


def _pending(item: dict) -> bool:
    e = item["emailed"]
    return bool(e) and e["status"] in ("pending", "running")


def build(db: Session, user_id: int) -> list[dict]:
    """The caller's conversations, the most recently active first. Each has its
    items oldest first (see the module docstring)."""
    profiles = {b.id: b for b in db.execute(
        select(BirthProfile).where(BirthProfile.user_id == user_id)).scalars()}
    threads: dict[str, dict] = {}
    last_unsaved: dict | None = None
    for item in _items(db, user_id):
        profile = profiles.get(item["birth_id"]) if item["birth_id"] else None
        if profile is not None:
            key = f"c{profile.id}"
            th = threads.get(key)
            if th is None:
                th = threads[key] = {
                    "key": key, "birth_id": profile.id, "available": True,
                    "label": profile.label or profile.name or profile.place, "items": []}
        else:
            th = last_unsaved
            if th is None or item["at"] - th["items"][-1]["at"] > SPLIT:
                key = f"u{int(item['at'].timestamp())}"
                th = last_unsaved = threads[key] = {
                    "key": key, "birth_id": None, "available": False, "label": "", "items": []}
            if not th["label"] and item["_name"]:
                th["label"] = item["_name"]
        th["items"].append(item)
    out = list(threads.values())
    for th in out:
        th["count"] = len(th["items"])
        th["first_at"] = th["items"][0]["at"]
        th["last_at"] = th["items"][-1]["at"]
        th["pending"] = sum(1 for i in th["items"] if _pending(i))
    out.sort(key=lambda th: th["last_at"], reverse=True)
    return out


def item_dict(item: dict) -> dict:
    out = {k: v for k, v in item.items() if not k.startswith("_")}
    out["at"] = _iso(item["at"])
    return out


def summary(th: dict) -> dict:
    last = th["items"][-1]
    return {"key": th["key"], "birth_id": th["birth_id"], "available": th["available"],
            "label": th["label"], "count": th["count"], "pending": th["pending"],
            "first_at": _iso(th["first_at"]), "last_at": _iso(th["last_at"]),
            "last_question": last["question"][:200]}


def page(th: dict, before: str | None = None, limit: int = PAGE) -> dict:
    """One page of a thread: the newest `limit` items (oldest first), or the
    newest ones asked before `before` (an item's ``at``, for "earlier")."""
    items = th["items"]
    if before:
        try:
            cut = aware(dt.datetime.fromisoformat(before))
            items = [i for i in items if i["at"] < cut]
        except (TypeError, ValueError):
            pass
    limit = max(1, min(int(limit or PAGE), 100))
    shown = items[-limit:]
    return {**summary(th), "more": len(items) > len(shown),
            "items": [item_dict(i) for i in shown]}


def empty(profile: BirthProfile) -> dict:
    """The conversation of a saved chart nothing has been asked on yet."""
    return {"key": f"c{profile.id}", "birth_id": profile.id, "available": True,
            "label": profile.label or profile.name or profile.place, "count": 0, "pending": 0,
            "first_at": None, "last_at": None, "last_question": "", "more": False, "items": []}


def key_of(threads: list[dict]) -> dict[str, str]:
    """item key -> the key of the conversation it is in."""
    return {i["key"]: th["key"] for th in threads for i in th["items"]}
