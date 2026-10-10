"""One Starter emailed-answer job, end to end, against a REAL Ollama (DIVASTRO-155).

Not a CI test: it needs a running Ollama with the model pulled. It runs the worker's
exact path (app/emailed_answers.run_next: rebuild the chart, analyse(), the chat's
narration prompt, Ollama, Claude translation/fallback when configured, the email)
in-process, on a throwaway SQLite database, with the console mail transport, so
NOTHING is emailed and the production database is never touched. It prints how long
the job took, which model wrote it, and the email it would have sent.

    # on the VM, with the ollama container up (port bound to the host's loopback):
    docker compose exec app python tools/emailed_answer_smoke.py --ollama-url http://ollama:11434
    # or from a checkout on the host:
    python tools/emailed_answer_smoke.py --ollama-url http://127.0.0.1:11434 --lang hi

    --model qwen2.5:7b        the Ollama model (default: ASTRO_EMAIL_ANSWER_MODEL or qwen2.5:7b)
    --lang en|hi|...          the customer's language (non-English needs Claude to translate)
    --question "..."          the question
    --no-claude               ignore ANTHROPIC_API_KEY: no translation, no Claude fallback
    --num-predict N           ASTRO_EMAIL_ANSWER_NUM_PREDICT for this run (default 1000)

Exit status 0 when the job was delivered by the local model, 1 otherwise (it still
prints what happened).
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BIRTH = {"name": "Smoke Test", "date": "1985-06-15", "time": "10:30", "latitude": 28.6519,
         "longitude": 77.2315, "timezone": "Asia/Kolkata", "place": "Delhi, India"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ollama-url", required=True)
    ap.add_argument("--model", default=os.environ.get("ASTRO_EMAIL_ANSWER_MODEL", "qwen2.5:7b"))
    ap.add_argument("--lang", default="en")
    ap.add_argument("--question", default="How will my career develop over the next two years?")
    ap.add_argument("--no-claude", action="store_true")
    ap.add_argument("--num-predict", default=os.environ.get("ASTRO_EMAIL_ANSWER_NUM_PREDICT", "1000"))
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="emailed_smoke_")
    # Everything below is set BEFORE the app is imported: a scratch database, mail that
    # is only printed, no background worker, and the Ollama under test.
    os.environ.update({
        "ASTRO_DATABASE_URL": f"sqlite:///{tmp}/smoke.db",
        "ASTRO_SMTP_HOST": "console", "ASTRO_COOKIE_SECURE": "0",
        "ASTRO_EMAIL_ANSWER_WORKER": "0", "ASTRO_ADMIN_EMAILS": "",
        "ASTRO_EMAIL_ANSWER_OLLAMA_URL": args.ollama_url.rstrip("/"),
        "ASTRO_EMAIL_ANSWER_MODEL": args.model,
        "ASTRO_EMAIL_ANSWER_NUM_PREDICT": str(args.num_predict),
        "ASTRO_SECRET_KEY": os.environ.get("ASTRO_SECRET_KEY") or "smoke-not-a-secret",
    })
    if args.no_claude:
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

    import logging
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("app.mail").setLevel(logging.ERROR)     # the body is printed below instead

    from app import emailed_answers as ea, llm, mail
    from app.chart_service import BirthData, build
    from app.db import CREDIT_EMAIL, EntryKind, User, grant, init_db, session as db_session

    init_db()
    print(f"Ollama {args.ollama_url}  model {args.model}  reachable+pulled: "
          f"{ea.ollama_ready(args.ollama_url.rstrip('/'), args.model)}")
    print(f"Claude configured: {llm._anthropic_ready()}  ({llm.CLAUDE_MODEL})")
    with db_session() as db:
        user = User(email="smoke@example.invalid", name="Smoke", provider="dev", provider_sub="smoke")
        db.add(user)
        db.flush()
        grant(db, user.id, 1, EntryKind.purchase, note="smoke", credit_type=CREDIT_EMAIL)
        db.commit()
        session = build(BirthData(**BIRTH))
        job = ea.enqueue(db, user, session, args.question, args.lang, None)
        job_id = job.id

    t0 = time.monotonic()
    ea.run_next()
    took = time.monotonic() - t0
    with db_session() as db:
        from app.db import EmailedAnswerJob
        job = db.get(EmailedAnswerJob, job_id)

    print("=" * 72)
    print(f"status       {job.status}")
    print(f"duration     {took:.1f} s ({took / 60:.1f} min)")
    print(f"model_used   {job.model_used}")
    print(f"route        {job.route_reason}")
    print(f"translator   {job.translator or '-'}")
    print(f"words        {len(job.answer.split())}")
    if job.error:
        print(f"errors       {job.error}")
    sent = [m for m in mail.OUTBOX if "smoke@example.invalid" in m[0]]
    if sent:
        to, subject, body, _html = sent[-1]
        print("=" * 72)
        print(f"(NOT sent) To: {', '.join(to)}\nSubject: {subject}\n\n{body}")
    return 0 if job.status == "done" and job.model_used.startswith("ollama:") else 1


if __name__ == "__main__":
    sys.exit(main())
