"""Question routing.

A question is mapped to a *topic* (which houses, rulers and natural
significators to read) and an *intent* (whether the person is asking what is
true, when it happens, or what to do). Everything downstream is driven by these
two, so the mapping is kept explicit and inspectable rather than fuzzy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Topic:
    key: str
    label: str
    primary_houses: tuple[int, ...]
    support_houses: tuple[int, ...]
    significators: tuple[str, ...]
    keywords: tuple[str, ...]
    strong_keywords: tuple[str, ...] = ()
    timing_movers: tuple[str, ...] = ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
    blurb: str = ""


TOPICS: tuple[Topic, ...] = (
    Topic(
        key="career",
        label="career and vocation",
        primary_houses=(10, 6),
        support_houses=(2, 1, 11),
        significators=("Sun", "Saturn", "Mars", "Mercury", "Jupiter"),
        # "promoted"/"promote" are spelled out rather than left to "promotion"
        # alone — the same gap as the dasha fix below (_stem only strips one
        # trailing e/y, which can't bridge "promotion" to "promoted"). That
        # gap sent "will I get promoted" to the generic timing topic instead
        # of career, with none of the 10th/6th-house evidence to answer from.
        strong_keywords=("career", "job", "profession", "vocation", "promotion", "promoted",
                         "promote", "workplace",
                         "boss", "employer", "resign", "quit my job", "appraisal", "layoff",
                         "business", "startup", "entrepreneur", "self employed", "freelance"),
        keywords=("work", "office", "company", "role", "position", "salary hike", "interview",
                  "government job", "corporate", "manager", "success", "ambition", "reputation"),
        blurb="the 10th house of standing and the 6th of daily work",
    ),
    Topic(
        key="money",
        label="money and material security",
        primary_houses=(2, 11),
        support_houses=(8, 10, 5),
        significators=("Jupiter", "Venus", "Saturn", "Mercury"),
        strong_keywords=("money", "wealth", "salary", "income", "rich", "finance", "financial",
                         "savings", "debt", "loan", "investment", "invest", "profit", "loss",
                         "afford", "earnings", "bankrupt"),
        keywords=("earn", "pay", "cash", "fund", "budget", "expense", "property value",
                  "returns", "stocks", "crypto", "gold"),
        blurb="the 2nd house of earned resources and the 11th of gains",
    ),
    Topic(
        key="love",
        label="love and relationships",
        primary_houses=(7, 5),
        support_houses=(11, 8, 1),
        significators=("Venus", "Mars", "Moon", "Jupiter"),
        strong_keywords=("love", "marriage", "marry", "spouse", "husband", "wife", "partner",
                         "relationship", "girlfriend", "boyfriend", "dating", "romance",
                         "divorce", "separation", "breakup", "engagement", "soulmate",
                         "arranged marriage", "love marriage"),
        keywords=("date", "crush", "affair", "commitment", "compatible", "compatibility",
                  "single", "attract", "intimacy"),
        timing_movers=("Jupiter", "Saturn", "Uranus", "Pluto"),
        blurb="the 7th house of partnership and the 5th of romance",
    ),
    Topic(
        key="family",
        label="home and family",
        primary_houses=(4,),
        support_houses=(3, 10, 12),
        significators=("Moon", "Saturn", "Sun", "Venus"),
        strong_keywords=("family", "home", "mother", "father", "parents", "house purchase",
                         "property", "real estate", "relocate", "moving house", "ancestral",
                         "sibling", "brother", "sister", "buy a house", "buying a house",
                         "own a house", "own home", "new home", "own place"),
        keywords=("roots", "land", "flat", "apartment", "domestic", "household", "hometown"),
        blurb="the 4th house of home and roots",
    ),
    Topic(
        key="children",
        label="children and creativity",
        primary_houses=(5,),
        support_houses=(4, 9, 11),
        significators=("Jupiter", "Venus", "Moon", "Sun"),
        strong_keywords=("children", "child", "kids", "baby", "pregnancy", "pregnant",
                         "conceive", "fertility", "son", "daughter", "parenthood"),
        # "art" (not "artistic") also matches "article" via the \w{0,4} tail
        # _hits allows for inflections — any message merely mentioning an
        # article gets pulled toward this topic. "artistic" keeps the signal
        # without that collision.
        keywords=("creative", "creativity", "artistic", "hobby", "play", "romance", "speculation"),
        blurb="the 5th house of children and creative output",
    ),
    Topic(
        key="health",
        label="health and vitality",
        primary_houses=(6, 1),
        support_houses=(8, 12),
        significators=("Mars", "Saturn", "Moon", "Sun"),
        strong_keywords=("health", "illness", "disease", "sick", "surgery", "hospital",
                         "diagnosis", "recovery", "chronic", "injury", "medical", "fitness",
                         "mental health", "anxiety", "depression", "stress"),
        keywords=("body", "energy", "sleep", "diet", "exercise", "wellbeing", "pain", "immunity"),
        blurb="the 6th house of illness and the 1st of the body",
    ),
    Topic(
        key="education",
        label="education and study",
        primary_houses=(9, 5),
        support_houses=(3, 4, 10),
        significators=("Mercury", "Jupiter", "Sun", "Moon"),
        strong_keywords=("study", "studies", "education", "exam", "exams", "college",
                         "university", "degree", "phd", "masters", "mba", "scholarship",
                         "student", "course", "research", "admission"),
        keywords=("learn", "learning", "school", "academic", "knowledge", "certification"),
        blurb="the 9th house of higher learning and the 3rd of early study",
    ),
    Topic(
        key="travel",
        label="travel and going abroad",
        primary_houses=(9, 12),
        support_houses=(3, 4, 7),
        significators=("Jupiter", "Mercury", "Moon", "Rahu"),
        strong_keywords=("travel", "abroad", "foreign", "immigration", "visa", "migrate",
                         "relocation", "overseas", "settle abroad", "nri", "expat", "trip"),
        keywords=("journey", "flight", "country", "move country", "residence"),
        blurb="the 9th house of long journeys and the 12th of foreign residence",
    ),
    Topic(
        key="spirituality",
        label="spirituality and inner life",
        primary_houses=(12, 9),
        support_houses=(8, 4),
        significators=("Jupiter", "Neptune", "Saturn", "Moon"),
        strong_keywords=("spiritual", "spirituality", "meditation", "god", "faith", "religion",
                         "dharma", "karma", "purpose in life", "moksha", "enlightenment",
                         "past life", "soul"),
        keywords=("meaning", "belief", "practice", "retreat", "solitude", "mystical"),
        blurb="the 12th house of the inner life and the 9th of belief",
    ),
    Topic(
        key="friends",
        label="friends and networks",
        primary_houses=(11,),
        support_houses=(3, 7, 5),
        significators=("Jupiter", "Venus", "Mercury", "Saturn"),
        strong_keywords=("friends", "friendship", "network", "community", "social circle",
                         "mentor", "patron", "colleagues"),
        keywords=("social", "group", "team", "connections", "supporters"),
        blurb="the 11th house of friends, allies and gains",
    ),
    Topic(
        key="obstacles",
        label="obstacles, enemies and setbacks",
        primary_houses=(6, 12),
        support_houses=(8, 1, 7),
        significators=("Saturn", "Mars", "Pluto"),
        strong_keywords=("enemy", "enemies", "obstacle", "obstacles", "problem", "struggle",
                         "conflict", "litigation", "court case", "lawsuit", "betrayal",
                         "why is life hard", "bad luck", "blocked", "stuck"),
        keywords=("rival", "opposition", "difficulty", "setback", "failure", "delay"),
        blurb="the 6th house of adversaries and the 12th of hidden undoing",
    ),
    Topic(
        key="self",
        label="personality and character",
        primary_houses=(1,),
        support_houses=(10, 4, 7),
        significators=("Sun", "Moon", "Mercury"),
        strong_keywords=("personality", "who am i", "my character", "my nature", "describe me",
                         "strengths", "weaknesses", "my chart", "about me", "temperament",
                         "how am i", "what am i like", "self"),
        keywords=("myself", "identity", "traits", "behaviour", "psychology"),
        blurb="the ascendant, its ruler, and the two lights",
    ),
    Topic(
        key="timing",
        label="current period and timing",
        primary_houses=(1, 10),
        support_houses=(4, 7),
        significators=("Sun", "Moon", "Saturn", "Jupiter"),
        # The dasha vocabulary is spelled out rather than left to "dasha" alone.
        # _hits anchors on a word boundary, so "dasha" matches "dasha" and
        # "dashas" but never "mahadasha" or "antardasha" — there is no boundary
        # inside a compound. That gap sent "list of mahadasha and its time" to
        # the default topic, and the reading answered about personality.
        strong_keywords=("right now", "currently", "this year", "next year", "coming months",
                         "current period", "phase of life", "transits", "what is happening",
                         "good time", "auspicious",
                         "dasha", "dasa", "mahadasha", "mahadasa", "maha dasha",
                         "antardasha", "antardasa", "antar dasha", "bhukti",
                         "vimshottari", "pratyantar", "time lord", "time-lord"),
        keywords=("now", "period", "phase", "season", "ahead", "future"),
        blurb="the active time-lords and transits",
    ),
)

TOPIC_BY_KEY = {t.key: t for t in TOPICS}
DEFAULT_TOPIC = TOPIC_BY_KEY["self"]

# --------------------------------------------------------------------------
# Intent
# --------------------------------------------------------------------------

_WHEN = re.compile(
    r"\b(when|what time|how long until|by when|which year|how soon|timeline|"
    r"date for|in which month|kab)\b", re.I)
_WILL = re.compile(r"\b(will|shall|am i going to|are we going to|is it going to|chances of|"
                   r"likelihood|probability|possible that)\b", re.I)
_ADVICE = re.compile(r"\b(should i|should we|is it wise|advice|advise|recommend|better to|"
                     r"do you think i|worth it|good idea|what do i do|how do i|how can i|"
                     r"how should)\b", re.I)
_COMPARE = re.compile(r"\b(or|versus|vs\.?|better)\b", re.I)
_DESCRIBE = re.compile(r"\b(what|who|why|how|describe|tell me|explain|show)\b", re.I)


# Past-tense or explicitly-dated questions ("I got married in 2012", "what was
# happening in 2015", "when I was 25") ask the engine to look backwards.
_PAST = re.compile(
    r"\b(happened|was happening|did happen|used to|back then|"
    r"i (?:got|had|lost|left|joined|started|moved|met|married|quit|failed|passed)|"
    r"we (?:got|had|met|married|moved)|"
    r"my (?:marriage|wedding|divorce|accident|surgery|promotion) (?:was|happened)|"
    r"in the past|last year|previously|earlier)\b", re.I)


# "Which year was that?" — the engine has to search for the date rather than be
# handed one. Distinct from `review`, which analyses a date the user names.
_SEARCH = re.compile(
    r"\b(what|which)\s+(year|month|age|time)\b|"
    r"\bwhen\s+(did|was|were)\b|"
    r"\b(few|some|couple of|several)\s+years?\s+(ago|back)\b|"
    r"\ba while (?:ago|back)\b|\bpinpoint\b|\bidentify the (?:year|period)\b", re.I)


def detect_intent(question: str) -> str:
    """One of: search, review, timing, forecast, advice, describe."""
    q = question.strip()
    if _SEARCH.search(q):
        return "search"
    if _PAST.search(q):
        return "review"
    if _WHEN.search(q):
        return "timing"
    if _ADVICE.search(q):
        return "advice"
    if _WILL.search(q):
        return "forecast"
    if _DESCRIBE.search(q):
        return "describe"
    return "describe"


# --------------------------------------------------------------------------
# Topic matching
# --------------------------------------------------------------------------

@dataclass
class Routing:
    topic: Topic
    intent: str
    score: float
    matched: list[str] = field(default_factory=list)
    secondary: Topic | None = None


def _stem(term: str) -> str:
    """Crude suffix strip so one keyword covers its inflections.

    'marry' -> 'marr', which then matches married / marriage / marries. Only
    applied to longer words, so 'date' does not degrade into matching 'data'.
    """
    t = term.lower()
    if len(t) > 4 and t[-1] in "ye":
        t = t[:-1]
    return t


def _hits(text: str, terms: tuple[str, ...]) -> list[str]:
    found = []
    for term in terms:
        pattern = r"\b" + re.escape(_stem(term)).replace(r"\ ", r"\s+") + r"\w{0,4}\b"
        if re.search(pattern, text, re.I):
            found.append(term)
    return found


def classify(question: str) -> Routing:
    text = question.lower()
    intent = detect_intent(question)

    scored: list[tuple[float, Topic, list[str]]] = []
    for topic in TOPICS:
        strong = _hits(text, topic.strong_keywords)
        weak = _hits(text, topic.keywords)
        score = 3.0 * len(strong) + 1.0 * len(weak)
        if score:
            scored.append((score, topic, strong + weak))

    if not scored:
        # No subject word at all — a bare "when?" or "what's coming?" is a
        # timing question; anything else is a general read of the person.
        topic = TOPIC_BY_KEY["timing"] if intent in ("timing", "forecast") else DEFAULT_TOPIC
        return Routing(topic=topic, intent=intent, score=0.0, matched=[])

    scored.sort(key=lambda s: -s[0])
    best = scored[0]
    second = scored[1][1] if len(scored) > 1 and scored[1][0] >= best[0] * 0.6 else None
    return Routing(topic=best[1], intent=intent, score=best[0], matched=best[2], secondary=second)
