"""The Starter's emailed answers (DIVASTRO-155).

A signed-in customer with no instant questions left but emailed-answer credits
(the one-time Starter, billing.STARTER_SKU) asks as usual. Instead of answering in
the chat, the server:

1. ENQUEUE (`enqueue`, called by /api/ask and /api/ask/stream): debits ONE
   emailed-answer credit (credit_entries.credit_type = "email"), stores an
   `emailed_answer_jobs` row with everything needed to rebuild the chart later
   (the birth payload: the in-memory chart session expires) and returns at once.
   The app shows "Your detailed answer will be emailed to <email> within 30
   minutes".

2. WORK (`run_next`, one job at a time, from the loop `start_worker` starts in the
   app's lifespan; DB-backed, so a restart resumes): rebuild the chart, run the
   same `analyse()` + Vedic context as an instant answer, then write the reading:

   * normally with the LOCAL model (Ollama, ASTRO_EMAIL_ANSWER_MODEL, default
     qwen2.5:7b), in ENGLISH, with the chat's own narration prompt
     (llm.stream_polish) minus its "keep it short" note, and a larger output cap;
     a non-English answer is then translated by Claude (llm.translate);
   * with CLAUDE (same prompt, written directly in the customer's language) when
     Ollama is unreachable or fails, when its run passes the time budget, or when
     the job's projected finish (its place in the queue x the measured average
     local duration, 4 minutes until measured) would be more than
     ASTRO_EMAIL_ANSWER_SAFE_MIN (25) minutes after it was asked;
   * with the RULE ENGINE's own reading (answer_engine) plus an honest one-line
     note when Claude fails too (no key, credit balance too low, API down).

   Every path emails the answer (app/mail.py) and saves it to the customer's
   `questions` rows (My questions). `model_used` records which path ran.

3. FAILURE: a job that cannot produce or deliver an answer (the chart cannot be
   rebuilt, the email cannot be sent) is marked failed and its credit is refunded
   (an EntryKind.refund row of credit_type "email"); an answer that exists is still
   saved to My questions (then with charged = False).

QUESTIONS ROW SEMANTICS: an emailed answer is a normal `questions` row written
when the job finishes, `charged` = True when the emailed credit stayed spent, False
when it was refunded. It is linked from the job (`question_id`), which is how
/api/history marks it as emailed.

ALERTS (`_alert`): a job delivered later than ASTRO_EMAIL_ANSWER_DEADLINE_MIN (30),
more than ASTRO_EMAIL_ANSWER_FALLBACK_ALERT (3) local-model fallbacks in an hour,
any Claude failure, or a failed job: logged at ERROR and emailed to
ASTRO_ADMIN_EMAILS at most once an hour (per process).

Like push.py's sender this assumes ONE app process (production: one uvicorn
worker). ASTRO_EMAIL_ANSWER_WORKER=0 turns the loop off (the queue then only
fills); tests call `run_next()` directly.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import html
import json
import logging
import os
import re
import statistics
import threading
import time
import urllib.request
from collections import Counter
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import billing, i18n, llm, mail
from .db import (
    CREDIT_EMAIL, EmailedAnswerJob, EntryKind, QuestionLog, User, aware, email_balance,
    grant, session as db_session, utcnow,
)
from .emailed_answers_text import tx

log = logging.getLogger("astro.emailed_answers")

STATIC = Path(__file__).parent / "static"
SITE_URL = os.environ.get("ASTRO_SITE_URL", "https://divineastro.org").rstrip("/")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30), "IST")

# Fallback reasons that count towards the "too many fallbacks in an hour" alert.
FALLBACK_REASONS = ("ollama_down", "ollama_error", "ollama_timeout", "projected_late")
MAX_ATTEMPTS = 3
CLAUDE_EST_S = 60          # what one Claude-written job is assumed to take, for the plan


# --------------------------------------------------------------------------
# Settings (read on every use, so an env change in a test or a restart applies)
# --------------------------------------------------------------------------

def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "").strip() or default)
    except ValueError:
        return default


def deadline_min() -> int:
    return billing.EMAIL_ANSWER_DEADLINE_MIN


def safe_min() -> int:
    """A job whose local run would end later than this many minutes after it was
    asked is written by Claude instead (the rest of the deadline is its reserve)."""
    return min(_int("ASTRO_EMAIL_ANSWER_SAFE_MIN", 25), deadline_min())


def start_avg_s() -> float:
    return 60.0 * _int("ASTRO_EMAIL_ANSWER_AVG_MIN", 4)


def model() -> str:
    return os.environ.get("ASTRO_EMAIL_ANSWER_MODEL", "").strip() or "qwen2.5:7b"


def ollama_url() -> str:
    return (os.environ.get("ASTRO_EMAIL_ANSWER_OLLAMA_URL", "").strip() or llm.OLLAMA_URL).rstrip("/")


def num_predict() -> int:
    # The prompt asks for 300-500 words; ~1.4 tokens a word in English plus headroom.
    return _int("ASTRO_EMAIL_ANSWER_NUM_PREDICT", 1000)


def ollama_max_s() -> int:
    return _int("ASTRO_EMAIL_ANSWER_OLLAMA_MAX_S", 1200)


def writer() -> str:
    """Who writes the emailed answers: "claude" (default; owner decision 11 Oct 2026, after the
    local model measured ~25 min per answer on this 2-core VM) or "ollama" (local model first,
    Claude as the safety net)."""
    w = os.environ.get("ASTRO_EMAIL_ANSWER_WRITER", "claude").strip().lower()
    return "ollama" if w == "ollama" else "claude"


def fallback_alert_per_hour() -> int:
    return _int("ASTRO_EMAIL_ANSWER_FALLBACK_ALERT", 3)


def poll_s() -> float:
    return float(_int("ASTRO_EMAIL_ANSWER_POLL_S", 5))


def worker_enabled() -> bool:
    return os.environ.get("ASTRO_EMAIL_ANSWER_WORKER", "1").strip() != "0"


# --------------------------------------------------------------------------
# Enqueue
# --------------------------------------------------------------------------

_wake = threading.Event()


def eta_minutes(db: Session) -> int:
    """The promise shown to the customer. Always the deadline: the worker's
    routing exists to keep it, so the app never quotes a shorter guess."""
    return deadline_min()


def enqueue(db: Session, user: User, session, question: str, language: str,
            birth_id: int | None, as_of: dt.datetime | None = None,
            visitor: str = "") -> EmailedAnswerJob:
    """Debit one emailed-answer credit and queue the question. Commits.

    `session` is the live chart session (chart_service.ChartSession); its birth
    payload is stored so the worker can rebuild the chart after the session has
    expired. The caller has already checked email_balance(...) > 0."""
    birth = session.birth
    email = billing.deliverable_email(user)
    grant(db, user.id, -1, EntryKind.question, note=question[:200], credit_type=CREDIT_EMAIL)
    job = EmailedAnswerJob(
        user_id=user.id, birth_id=birth_id,
        birth_json=json.dumps(birth.to_dict(), ensure_ascii=False),
        chart_name=(birth.name or "")[:120], question=question,
        language=i18n.normalize(language), email=email,
        as_of=(as_of or dt.datetime.now()).isoformat(timespec="seconds"),
        visitor=visitor[:16],
    )
    db.add(job)
    db.commit()
    _wake.set()
    return job


def queued_payload(db: Session, job: EmailedAnswerJob) -> dict:
    """What the app renders as the "queued" card."""
    return {
        "queued": True, "job_id": job.id, "email": job.email,
        "minutes": eta_minutes(db), "email_credits": email_balance(db, job.user_id),
        "language": job.language, "question": job.question,
    }


# --------------------------------------------------------------------------
# Planning: which jobs Claude must write to keep the promise
# --------------------------------------------------------------------------

def ollama_avg_s(db: Session) -> float:
    """Measured average of the last 5 jobs the local model wrote (start to finish),
    or ASTRO_EMAIL_ANSWER_AVG_MIN until there are any."""
    rows = db.execute(
        select(EmailedAnswerJob.started_at, EmailedAnswerJob.finished_at)
        .where(EmailedAnswerJob.status == "done",
               EmailedAnswerJob.model_used.like("ollama:%"),
               EmailedAnswerJob.started_at.is_not(None),
               EmailedAnswerJob.finished_at.is_not(None))
        .order_by(EmailedAnswerJob.finished_at.desc()).limit(5)).all()
    spans = [(aware(f) - aware(s)).total_seconds() for s, f in rows]
    spans = [x for x in spans if x > 0]
    return statistics.mean(spans) if spans else start_avg_s()


def ollama_ready(url: str | None = None, name: str | None = None) -> bool:
    """The local model answers /api/tags within 3 s and has the model pulled."""
    url, name = url or ollama_url(), name or model()
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=3) as resp:
            data = json.loads(resp.read())
        names = {m.get("name") for m in data.get("models", [])}
        return name in names or f"{name}:latest" in names
    except Exception:
        return False


def plan(jobs: list[EmailedAnswerJob], now: dt.datetime, avg_s: float,
         local_ok: bool) -> dict[int, str]:
    """{job id: route reason} for the pending jobs, oldest first.

    "ollama" = the local model writes it; anything else = Claude, and why:
    "ollama_down", or "projected_late" when the job's projected finish (queue
    position x avg_s, Claude jobs counted at CLAUDE_EST_S) is later than
    created_at + safe_min()."""
    out: dict[int, str] = {}
    t = now
    if writer() == "claude":           # Claude writes every job; not a fallback
        return {job.id: "claude" for job in jobs}
    for job in jobs:
        if not local_ok:
            out[job.id] = "ollama_down"
            t += dt.timedelta(seconds=CLAUDE_EST_S)
            continue
        finish = t + dt.timedelta(seconds=avg_s)
        if finish > aware(job.created_at) + dt.timedelta(minutes=safe_min()):
            out[job.id] = "projected_late"
            t += dt.timedelta(seconds=CLAUDE_EST_S)
        else:
            out[job.id] = "ollama"
            t = finish
    return out


# --------------------------------------------------------------------------
# The worker
# --------------------------------------------------------------------------

_run_lock = threading.Lock()


def recover() -> int:
    """At start-up: a job left "running" by a crash or a restart goes back to the
    queue (or fails, refunded, after MAX_ATTEMPTS). Returns how many were reset."""
    n = 0
    with db_session() as db:
        for job in db.execute(select(EmailedAnswerJob).where(
                EmailedAnswerJob.status == "running")).scalars().all():
            if job.attempts >= MAX_ATTEMPTS:
                _fail(db, job, "gave up after a restart mid-job")
            else:
                job.status = "pending"
                n += 1
        db.commit()
    if n:
        log.warning("emailed answers: %d interrupted job(s) put back in the queue", n)
    return n


def run_next(now: dt.datetime | None = None) -> int | None:
    """Process ONE job (the next one the plan picks). Returns its id, or None when
    the queue is empty. Never raises: a job that blows up is failed and refunded."""
    if not _run_lock.acquire(blocking=False):
        return None
    try:
        now = now or utcnow()
        with db_session() as db:
            jobs = db.execute(
                select(EmailedAnswerJob).where(EmailedAnswerJob.status == "pending")
                .order_by(EmailedAnswerJob.created_at, EmailedAnswerJob.id)).scalars().all()
            if not jobs:
                return None
            local_ok = ollama_ready()
            routes = plan(jobs, now, ollama_avg_s(db), local_ok)
            # A job Claude must write is short work and time-critical: it goes first.
            urgent = [j for j in jobs if routes[j.id] != "ollama"]
            job = urgent[0] if urgent else jobs[0]
            reason = routes[job.id]
            job_id = job.id
            try:
                _process(db, job, reason)
            except Exception as exc:                       # noqa: BLE001
                log.exception("emailed answer job %s failed", job_id)
                db.rollback()
                job = db.get(EmailedAnswerJob, job_id)
                _fail(db, job, f"{type(exc).__name__}: {exc}")
                db.commit()
            return job_id
    finally:
        _run_lock.release()


def _history(db: Session, job: EmailedAnswerJob) -> list[dict]:
    stmt = select(QuestionLog).where(QuestionLog.user_id == job.user_id,
                                     QuestionLog.created_at < job.created_at)
    if job.birth_id:
        stmt = stmt.where(QuestionLog.birth_id == job.birth_id)
    rows = db.execute(stmt.order_by(QuestionLog.created_at.desc()).limit(5)).scalars().all()
    return [{"question": r.question, "answer": r.answer} for r in reversed(rows)]


def _analyse(job: EmailedAnswerJob) -> dict:
    """The chart rebuilt from the stored birth payload, and the same analysis an
    instant answer gets (main.ask_stream): analyse() + the Vedic context."""
    from .chart_service import BirthData, build
    from .interpret import analyse
    from .main import _engine_lang, _vedic_context

    birth = BirthData(**json.loads(job.birth_json))
    session = build(birth)
    try:
        when = dt.datetime.fromisoformat(job.as_of) if job.as_of else dt.datetime.now()
    except ValueError:
        when = dt.datetime.now()
    result = analyse(session, job.question, when, language=_engine_lang(job.language)).to_dict()
    result["vedic"] = _vedic_context(session)
    result["answer_engine"] = result["answer"]
    result["birth_date"] = birth.date
    return result


def _ollama_text(result: dict, job: EmailedAnswerJob, history: list[dict], budget_s: float) -> str:
    meta: dict = {}
    text = "".join(llm.stream_polish(
        result, "en", f"ollama:{model()}", job.question, history=history, meta=meta,
        num_predict=num_predict(), ollama_url=ollama_url(),
        timeout=max(30.0, min(budget_s, 300.0)),
        deadline=time.monotonic() + budget_s, brief=False)).strip()
    if len(text) < 120:
        raise RuntimeError("the local model returned too little text to trust")
    return text


def _claude_text(result: dict, job: EmailedAnswerJob, history: list[dict]) -> str:
    if not llm._anthropic_ready():
        raise RuntimeError("Claude is not configured (no ANTHROPIC_API_KEY)")
    text = "".join(llm.stream_polish(
        result, job.language, "anthropic", job.question, history=history,
        meta={}, local_fallback=False)).strip()
    if len(text) < 120:
        raise RuntimeError("Claude returned too little text to trust")
    return text


def _process(db: Session, job: EmailedAnswerJob, reason: str) -> None:
    start = utcnow()
    job.status, job.started_at = "running", start
    job.attempts = (job.attempts or 0) + 1
    job.route_reason = reason
    db.commit()

    result = _analyse(job)
    history = _history(db, job)
    lang = job.language
    notes: list[str] = []
    text = ""
    translator = ""
    used = ""

    if reason == "ollama":
        budget = min(float(ollama_max_s()),
                     (aware(job.created_at) + dt.timedelta(minutes=safe_min()) - start).total_seconds())
        if budget < 60:
            reason = "projected_late"
        else:
            try:
                text = _ollama_text(result, job, history, budget)
                used = f"ollama:{model()}"
            except TimeoutError as exc:
                reason = "ollama_timeout"
                job.error = f"ollama: {exc}"
            except Exception as exc:                         # noqa: BLE001
                reason = "ollama_error"
                job.error = f"ollama: {type(exc).__name__}: {exc}"
        job.route_reason = reason
        if used and lang != "en":
            try:
                text = llm.translate(text, lang)
                translator = f"anthropic:{llm.TRANSLATE_MODEL}"
            except Exception as exc:                         # noqa: BLE001
                translator = "failed"
                notes.append(tx("note_translate", lang))
                job.error = (job.error + "\n" if job.error else "") + f"translate: {exc}"
                _alert("claude_failed", f"translation of job {job.id} failed: {exc}")

    if not used:
        if reason in FALLBACK_REASONS:
            log.warning("emailed answer job %s: %s, Claude writes it", job.id, reason)
            _check_fallback_rate(db, job)
        try:
            text = _claude_text(result, job, history)
            used = f"anthropic:{llm.CLAUDE_MODEL}"
        except Exception as exc:                             # noqa: BLE001
            job.error = (job.error + "\n" if job.error else "") + f"claude: {type(exc).__name__}: {exc}"
            _alert("claude_failed", f"Claude could not write job {job.id}: {exc}")
            text = result.get("answer_engine", "")
            used = "engine"
            notes.append(tx("note_engine", lang))
            if lang in llm.REGIONAL:
                notes.append(i18n.get(lang).english_answer)

    job.model_used, job.translator = used, translator
    job.answer = text
    # The answer is saved to My questions before it is emailed, so it is never lost.
    row = QuestionLog(
        user_id=job.user_id, birth_id=job.birth_id, question=job.question,
        answer=_with_notes(text, notes), answer_engine=result.get("answer_engine", ""),
        topic=result.get("topic", ""), verdict=result.get("verdict", ""),
        score=float(result.get("score") or 0.0), language=lang, charged=True)
    db.add(row)
    db.flush()
    job.question_id = row.id
    db.commit()

    sent = True
    if job.email:
        subject, body, html_body = render_email(job, result, text, notes)
        sent = any(mail.send([job.email], subject, body, html_body) for _ in range(2))
    job.emailed = bool(job.email) and sent
    job.finished_at = utcnow()
    if not sent:
        row.charged = False
        _fail(db, job, (job.error + "\n" if job.error else "") + "the email could not be sent",
              notify=False)
        db.commit()
        return

    job.status = "done"
    job.birth_json = ""                  # personal data: not kept once it is answered
    db.commit()
    took = (aware(job.finished_at) - aware(job.created_at)).total_seconds() / 60
    log.info("emailed answer job %s done in %.1f min by %s%s", job.id, took, used,
             f" (+{translator})" if translator else "")
    if took > deadline_min():
        _alert("late", f"job {job.id} was delivered after {took:.1f} minutes "
                       f"(promise: {deadline_min()}) by {used}")
    from . import analytics
    analytics.record_server_event("email_answer_delivered", lang, job.visitor)


def _with_notes(text: str, notes: list[str]) -> str:
    return "\n\n".join([*notes, text]) if notes else text


def _fail(db: Session, job: EmailedAnswerJob, error: str, notify: bool = True) -> None:
    """Mark a job failed, refund its credit once, tell the customer and the admin."""
    job.status = "failed"
    job.error = error[:4000]
    job.finished_at = job.finished_at or utcnow()
    job.birth_json = ""
    if not job.refunded:
        grant(db, job.user_id, 1, EntryKind.refund,
              note=f"Emailed answer #{job.id} could not be delivered", credit_type=CREDIT_EMAIL)
        job.refunded = True
    db.flush()
    log.error("emailed answer job %s failed (credit refunded): %s", job.id, error)
    _alert("failed", f"job {job.id} failed and was refunded: {error}")
    if notify and job.email:
        lang = job.language
        q = job.question if len(job.question) <= 200 else job.question[:200] + "…"
        mail.send([job.email], tx("fail_subject", lang),
                  tx("fail_body", lang, question=q) + f"\n\n{_site(lang)}\n\n{tx('sign', lang)}")


# --------------------------------------------------------------------------
# Alerts
# --------------------------------------------------------------------------

ALERT_EVERY_S = 3600
_alert_state = {"last": 0.0, "pending": []}
_alert_lock = threading.Lock()


def _alert(kind: str, detail: str) -> bool:
    """Log at ERROR, and email the admins at most once an hour (the lines held back
    in between go into the next email). Returns whether an email went out."""
    log.error("emailed answers ALERT [%s] %s", kind, detail)
    with _alert_lock:
        _alert_state["pending"].append(f"[{kind}] {detail}")
        now = time.monotonic()
        if _alert_state["last"] and now - _alert_state["last"] < ALERT_EVERY_S:
            return False
        lines, _alert_state["pending"] = _alert_state["pending"], []
        _alert_state["last"] = now
    from . import auth
    to = sorted(auth.admin_emails())
    body = ("Emailed answers (Starter) need a look:\n\n" + "\n".join(lines)
            + "\n\nSee HANDOVER.md, 'Starter: emailed answers', for what to do.")
    return bool(to) and mail.send(to, "Divine Astro: emailed answers alert", body)


def _check_fallback_rate(db: Session, job: EmailedAnswerJob) -> None:
    since = utcnow() - dt.timedelta(hours=1)
    n = db.execute(select(func.count(EmailedAnswerJob.id)).where(
        EmailedAnswerJob.started_at >= since,
        EmailedAnswerJob.route_reason.in_(FALLBACK_REASONS))).scalar_one()
    if n > fallback_alert_per_hour():
        _alert("fallbacks", f"{n} emailed answers in the last hour were not written by the "
                            f"local model (latest: job {job.id}, {job.route_reason})")


# --------------------------------------------------------------------------
# The email
# --------------------------------------------------------------------------

def _site(lang: str) -> str:
    return f"{SITE_URL}/" + (f"?lang={lang}" if lang and lang != "en" else "")


def _history_label(lang: str) -> str:
    for code in (lang, "en"):
        try:
            table = json.loads((STATIC / "i18n" / f"{code}.json").read_text(encoding="utf-8"))
            if table.get("acct.history"):
                return table["acct.history"]
        except (OSError, ValueError):
            continue
    return "My questions"


_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
_ITAL = re.compile(r"(?<![\w*])_(.+?)_(?![\w*])", re.S)


def _plain(text: str) -> str:
    return _ITAL.sub(r"\1", _BOLD.sub(r"\1", text))


def _html_paragraphs(text: str) -> str:
    out = []
    for para in re.split(r"\n\s*\n", text.strip()):
        safe = html.escape(para.strip()).replace("\n", "<br>")
        safe = _BOLD.sub(r"<b>\1</b>", safe)
        out.append(f'<p style="margin:0 0 14px;line-height:1.6">{safe}</p>')
    return "".join(out)


def _born(job: EmailedAnswerJob, result: dict, lang: str) -> str:
    raw = result.get("birth_date") or ""
    try:
        when = i18n.format_date(dt.date.fromisoformat(raw), lang)
    except (ValueError, TypeError):
        when = raw
    born = tx("born", lang, date=when) if when else ""
    return ", ".join(x for x in (job.chart_name, born) if x)


def render_email(job: EmailedAnswerJob, result: dict, text: str,
                 notes: list[str]) -> tuple[str, str, str]:
    """(subject, plain text, HTML) in the customer's language."""
    lang = job.language
    chart = _born(job, result, lang)
    site = _site(lang)
    saved = tx("saved", lang, history=_history_label(lang))
    disclaimer = re.sub(r"\s+", " ", i18n.chrome("disclaimer", lang)).strip()
    note_txt = "".join(f"{n}\n\n" for n in notes)

    body = (f"{tx('hello', lang)}\n\n{tx('intro', lang)}\n\n"
            f"{tx('question', lang)}: {job.question}\n"
            + (f"{tx('chart', lang)}: {chart}\n" if chart else "")
            + f"\n{tx('answer', lang)}:\n\n{note_txt}{_plain(text)}\n\n"
            f"{tx('by', lang)}\n{saved}\n\n{tx('cta', lang)}: {site}\n\n"
            f"{disclaimer}\n\n{tx('sign', lang)}\n")

    e = html.escape
    notes_html = "".join(
        f'<p style="margin:0 0 14px;padding:8px 12px;background:#fff7e6;border-radius:8px;'
        f'color:#7a5300;font-size:14px">{e(n)}</p>' for n in notes)
    html_body = f"""<!doctype html><html lang="{e(lang)}"><body style="margin:0;padding:0;background:#f6f3ee">
<div style="max-width:600px;margin:0 auto;padding:24px 18px;font-family:Arial,'Noto Sans',sans-serif;color:#222;font-size:16px">
<p style="margin:0 0 6px;color:#b5651d;font-weight:bold;font-size:18px">{e(tx('sign', lang))}</p>
<p style="margin:0 0 16px">{e(tx('hello', lang))}<br>{e(tx('intro', lang))}</p>
<div style="background:#fff;border-radius:12px;padding:16px 18px;margin:0 0 16px">
<p style="margin:0 0 4px;color:#777;font-size:13px">{e(tx('question', lang))}</p>
<p style="margin:0 0 10px;font-weight:bold">{e(job.question)}</p>
{f'<p style="margin:0;color:#555;font-size:14px">{e(tx("chart", lang))}: {e(chart)}</p>' if chart else ''}
</div>
<div style="background:#fff;border-radius:12px;padding:16px 18px;margin:0 0 16px">
<p style="margin:0 0 10px;color:#777;font-size:13px">{e(tx('answer', lang))}</p>
{notes_html}{_html_paragraphs(text)}
</div>
<p style="margin:0 0 6px;color:#555;font-size:14px">{e(tx('by', lang))}<br>{e(saved)}</p>
<p style="margin:18px 0"><a href="{e(site)}" style="display:inline-block;background:#b5651d;color:#fff;text-decoration:none;padding:11px 18px;border-radius:8px;font-weight:bold">{e(tx('cta', lang))}</a></p>
<p style="margin:18px 0 0;color:#888;font-size:12px;line-height:1.5">{e(disclaimer)}</p>
</div></body></html>"""
    return tx("subject", lang), body, html_body


# --------------------------------------------------------------------------
# The loop
# --------------------------------------------------------------------------

async def _loop() -> None:
    await asyncio.to_thread(recover)
    while True:
        try:
            done = await asyncio.to_thread(run_next)
        except Exception:                              # pragma: no cover - keep the loop alive
            log.exception("emailed answers pass failed")
            done = None
        if done is None:
            await asyncio.to_thread(_wake.wait, poll_s())
            _wake.clear()


def start_worker() -> asyncio.Task | None:
    """Called from the app's lifespan. One loop per process (see the docstring)."""
    if not worker_enabled():
        return None
    log.info("emailed answers worker started (model %s at %s, deadline %s min)",
             model(), ollama_url(), deadline_min())
    return asyncio.get_running_loop().create_task(_loop())


# --------------------------------------------------------------------------
# The admin Traffic tile
# --------------------------------------------------------------------------

def admin_summary(db: Session, now: dt.datetime | None = None) -> dict:
    """Today's (IST) emailed-answer jobs: count, median minutes to deliver, model
    mix, late and failed, and what is waiting now."""
    now = now or utcnow()
    start = dt.datetime.combine(now.astimezone(IST).date(), dt.time.min, IST).astimezone(dt.timezone.utc)
    rows = db.execute(select(EmailedAnswerJob).where(EmailedAnswerJob.created_at >= start)).scalars().all()
    deadline = dt.timedelta(minutes=deadline_min())
    took = [(aware(j.finished_at) - aware(j.created_at)).total_seconds() / 60
            for j in rows if j.status == "done" and j.finished_at]
    late = sum(1 for j in rows if j.status == "done" and j.finished_at
               and aware(j.finished_at) - aware(j.created_at) > deadline)
    late += sum(1 for j in rows if j.status in ("pending", "running")
                and now - aware(j.created_at) > deadline)
    waiting = db.execute(select(func.count(EmailedAnswerJob.id)).where(
        EmailedAnswerJob.status.in_(("pending", "running")))).scalar_one()
    return {
        "enabled": billing.starter_enabled(),
        "today": len(rows),
        "delivered": sum(1 for j in rows if j.status == "done"),
        "failed": sum(1 for j in rows if j.status == "failed"),
        "late": late,
        "waiting": int(waiting),
        "median_minutes": round(statistics.median(took), 1) if took else None,
        "models": dict(Counter(j.model_used or ("(waiting)" if j.status in ("pending", "running")
                                                 else "(none)") for j in rows)),
        "deadline_min": deadline_min(),
    }
