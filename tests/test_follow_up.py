"""DIVASTRO-169: a new question is answered on its own topic.

Feedback from the first paying user (30 Oct): "I asked different follow-up
questions, but each answer kept going back to the first one, which was about
career." Every prompt carried the last five questions and answers and ended
"treat this question as a continuation of the dialogue". This pins:
  - topics.is_follow_up, the deterministic follow-up / new-topic rule, over a
    table of question pairs (the user's own thread among them);
  - a statement such as "I just got an offer today" is news, not a question
    about today's date (it used to route to the date-window topic);
  - the built prompt carries no history for a new topic, and only the one
    previous turn for a follow-up;
  - the engine reads a subject-less follow-up on the previous turn's topic and
    leaves a question with its own subject alone.
"""
import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("ASTRO_SECRET_KEY", "ci")
from app import llm  # noqa: E402
from app.interpret.topics import classify, follow_up_topic, is_follow_up  # noqa: E402

failures: list[str] = []
NOW = dt.date(2026, 10, 30)


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS" if ok else "FAIL"), "", name, ("" if ok else f"-- {detail}"))
    if not ok:
        failures.append(name)


JOB = ("When will I get a better job?", "career")
# (previous question, its topic, new question, follow-up?)
TABLE = [
    # The user's thread, in order.
    (*JOB, "I just got an offer today", True),
    ("I just got an offer today", "career", "What happens if I stay in the same company", True),
    ("What happens if I stay in the same company", "career", "When will I get married?", False),
    ("When will I get married?", "love", "Will my money situation improve this year?", False),
    ("Will my money situation improve this year?", "money",
     "When is a good time for me to start something new?", False),
    # Continuations with no subject of their own.
    (*JOB, "and when exactly?", True),
    (*JOB, "what about after that?", True),
    (*JOB, "When?", True),
    (*JOB, "Will it happen?", True),
    (*JOB, "Is that good?", True),
    (*JOB, "so should I take it?", True),
    (*JOB, "tell me more", True),
    (*JOB, "aur kab?", True),
    (*JOB, "तो फिर कब?", True),
    (*JOB, "and next month?", True),
    (*JOB, "I got a promotion yesterday", True),
    # Same subject again: the same thread.
    (*JOB, "Should I quit my job?", True),
    # A subject of its own, different from the last: new, whatever it opens with.
    (*JOB, "what about my marriage?", False),
    (*JOB, "and my health?", False),
    (*JOB, "मेरी शादी कब होगी?", False),
    (*JOB, "Describe my personality", False),
    # A date window of its own, or a long subject-less question: new.
    (*JOB, "how is my day today?", False),
    (*JOB, "aaj kaisa rahega", False),
    (*JOB, "What is the overall outlook for my life in the coming years?", False),
    # No previous turn: never a follow-up.
    ("", "", "and when exactly?", False),
]

print("Follow-up or new topic\n")
for prev_q, prev_t, q, want in TABLE:
    got = is_follow_up(q, prev_q or None, prev_t or None, now=NOW)
    check(f"{prev_q[:28]!r} -> {q!r}: {'follow-up' if want else 'new topic'}", got == want,
          f"got {'follow-up' if got else 'new topic'}")

# Unknown previous topic (an old QuestionLog row): re-derived from its question.
check("previous topic re-derived when missing",
      is_follow_up("When will I get married?", "When will I get a better job?", None) is False
      and is_follow_up("Should I quit my job?", "When will I get a better job?", None) is True)

print("\nA statement is news, not a date window\n")
r = classify("I just got an offer today", now=NOW)
check("'I just got an offer today' is a career statement, not today's window",
      r.topic.key == "career" and r.period is None and r.intent != "period",
      f"{r.topic.key}/{r.intent}/{r.period}")
for q in ("how is my day today?", "aaj kaisa rahega", "I have an interview tomorrow",
          "How is today for my career?"):
    r = classify(q, now=NOW)
    check(f"{q!r} keeps its window", r.period is not None and r.intent == "period",
          f"{r.topic.key}/{r.intent}/{r.period}")

print("\nInherited topic\n")
prev = {"question": JOB[0], "topic": "career"}
for q in ("and when exactly?", "I just got an offer today", "and next month?"):
    t = follow_up_topic(q, prev, now=NOW) or classify(q, now=NOW).topic
    check(f"{q!r} after a job question is read as career", t.key == "career", t.key)
for q in ("When will I get married?", "Will my money situation improve this year?",
          "how is my day today?"):
    check(f"{q!r} keeps its own routing", follow_up_topic(q, prev, now=NOW) is None)
check("no inheritance from a personality or date-window turn",
      follow_up_topic("and when?", {"question": "Describe me", "topic": "self"}) is None
      and follow_up_topic("and when?", {"question": "how is my week", "topic": "period"}) is None)

print("\nThe prompt's history\n")
ANALYSIS = {"topic": "money", "topic_label": "money and material security",
            "verdict": "favourable", "score": 0.3,
            "evidence": [{"factor": "2nd ruler", "detail": "Jupiter Pisces 10°00′ H2",
                          "score": 0.8}]}
HISTORY = [
    {"question": "When will I get a better job?", "topic": "career",
     "answer": "CAREER-ANSWER-1 Your work improves from **Mar 2027**."},
    {"question": "I just got an offer today", "topic": "career",
     "answer": "CAREER-ANSWER-2 The offer looks good."},
    {"question": "When will I get married?", "topic": "love",
     "answer": "LOVE-ANSWER Marriage looks likely from **Jan 2028**."},
]
p = llm._build_prompt(ANALYSIS, "en", "Will my money situation improve this year?", HISTORY)
check("a new topic gets no history at all",
      "-ANSWER" not in p and "Previous question" not in p and "HISTORY" not in p, p[:300])
check("an earlier answer's dates are not offered for a new topic",
      "Jan 2028" not in p and "Mar 2027" not in p)

love = dict(ANALYSIS, topic="love", topic_label="marriage")
p = llm._build_prompt(love, "en", "and when exactly?", HISTORY)
check("a follow-up gets the one previous turn",
      "LOVE-ANSWER" in p and "Previous question: “When will I get married?”" in p
      and "CAREER-ANSWER" not in p, p[:400])
check("the previous turn comes before the question and is marked as context only",
      p.index("Previous answer") < p.index("THE QUESTION TO ANSWER")
      and "only to understand what they mean now" in p)
long = [{"question": "When will I get married?", "topic": "love", "answer": "word " * 2000}]
p = llm._build_prompt(love, "en", "and when exactly?", long)
check("a long previous answer is cut", p.count("word ") < 400)
check("no history, no history block",
      "Previous question" not in llm._build_prompt(love, "en", "and when?", [])
      and "Previous question" not in llm._build_prompt(love, "en", "and when?", None))

print("\nThe engine\n")
from app.chart_service import BirthData, build  # noqa: E402
from app.interpret import analyse  # noqa: E402

session = build(BirthData(name="T", date="1998-03-12", time="08:40", latitude=26.8467,
                          longitude=80.9462, timezone="Asia/Kolkata", place="Lucknow"))
when = dt.datetime(2026, 10, 30, 12, 0)
a = analyse(session, "and when exactly?", when, previous=prev)
check("analyse reads a subject-less follow-up on the previous topic", a.topic == "career", a.topic)
a = analyse(session, "I just got an offer today", when, previous=prev)
check("the offer statement is a career reading, not a date window",
      a.topic == "career" and a.intent != "period", f"{a.topic}/{a.intent}")
a = analyse(session, "Will my money situation improve this year?", when, previous=prev)
check("a question with its own subject is unchanged by `previous`",
      a.topic == analyse(session, "Will my money situation improve this year?", when).topic
      == "money", a.topic)
check("no previous turn: routing as before",
      analyse(session, "and when exactly?", when).topic != "career")

print("\n" + "=" * 60)
if failures:
    print(f"{len(failures)} FAILURES")
    for f in failures:
        print("  -", f)
    raise SystemExit(1)
print("follow-up rule: all green")
