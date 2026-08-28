"""Classical delineation text: what a placement *means*, in the tradition's own terms.

``vargas.py`` answers "what yoga forms" and "what varga is a planet in"; this
module answers the plainer, more constant question a reading actually leans
on — what does Mars in the 10th house say, what does an exalted Venus mean,
what does a Sun–Jupiter conjunction say, what should a Mercury Mahadasha
bring. None of it is astronomy and none of it is scoring; it is reference text,
looked up by placement, the same way ``interpret/knowledge.py`` supplies prose
ingredients for the Western engine.

Sources, and how each is handled:

  * **Brihat Jataka** (Varaha Mihira, tr. N. Chidambaram Iyer, Madras 1885) —
    public domain (Harvard Widener Library / Google Books scan). Chapters 8
    (dasha effects), 10 (avocation), 14 (double-planet yogas), 18 and 20
    (planets by sign and by house) are the source for
    :data:`MAHADASHA_EFFECTS`, :data:`CAREER_BY_PLANET`,
    :data:`CONJUNCTION_DELINEATION` and :data:`PLANET_HOUSE_TEXT`. Content is
    condensed and put in this module's own words rather than quoted at length,
    but the source is out of copyright and a short direct phrase is not a
    concern here the way it is for the second source.
  * **A modern (1975) Hindi compilation**, "Bhrigu Samhita Phalit-Prakash"
    (Dehati Pustak Bhandar, Delhi), presented under Sage Bhrigu's name but
    authored by a 20th-century compiler — **likely still under copyright**.
    Nothing from it is quoted or translated; its per-dignity delineations
    (own/exalted/moolatrikona/friendly/enemy/debilitated, for each graha) only
    inform :data:`DIGNITY_DELINEATION` as independently-phrased facts, cited
    generically below as "the Bhrigu-school dignity tradition" rather than by
    naming the edition. See ``docs/sources/`` for the full reading notes and
    the reasoning behind that line.
  * **A modern compilation presented as "Ravana Samhita"** — likely still
    under copyright, same handling as the Bhrigu source above. Its
    "kalapurusha"/graha-basics chapter states the classical Baladi Avastha
    rule (:func:`baladi_avastha`) plainly enough, and in terms standard
    enough across the tradition, that it is reproduced here as a rule rather
    than as this compilation's own words. Its Vimshottari Antardasha-phala
    chapter also gives :data:`ANTARDASHA_EFFECTS`, condensed and
    independently phrased the same way :data:`MAHADASHA_EFFECTS` is. Its
    Yogini Dasha chapter gives the arithmetic now in
    ``chart_service.yogini_dasha()`` and the result texts in
    :data:`YOGINI_EFFECTS` below. See ``docs/sources/ravana_samhita_notes.md``.

The book-length, per-Lagna version of :data:`PLANET_HOUSE_TEXT` (roughly
1300 short entries, one per Lagna x planet x house, found in the Bhrigu
Samhita compilation) is a known, large asset — see
``docs/sources/bhrigu_samhita_notes.md`` — being brought in incrementally,
one Lagna at a time, as :data:`BHRIGU_LAGNA_HOUSE_TEXT`. :func:`planet_house_text`
prefers it when the caller's Lagna has been transcribed, and falls back to
the Lagna-independent Brihat Jataka text below otherwise; a Lagna not yet
done is simply absent from the table, not guessed at.

What is deliberately not attempted, matching this module's neighbours:

  * Balarishta (infant-death yogas), Ayurdaya (lifespan calculation) and the
    manner/place-of-death chapters of the Brihat Jataka are a deliberate
    product decision, not encoded in this pass. They are real classical
    content and the decision was to include them faithfully when built —
    tracked, not implemented here.
  * Chastity/fidelity/widowhood judgements from both books' women's-horoscopy
    chapters, and the several dozen ultra-specific named Raja Yoga
    combinations in both books, are excluded — the former reads as regressive
    by modern standards and is a different kind of risk than plain
    delineation; the latter are too narrow to generalise and the kendra/
    trikona-lord Raja Yoga logic already in ``vargas.py`` is the better model.
"""

from __future__ import annotations

from .matching import NAISARGIKA_ENEMIES, NAISARGIKA_FRIENDS
from .vargas import (
    DEBILITATION, EXALTATION, GRAHAS, MOOLATRIKONA, OWN_SIGNS, chart_view,
)
from ..chart_service import DOMICILE, SIGNS

# --------------------------------------------------------------------------
# Career and wealth-source, by planet — Brihat Jataka ch. 10 ("On Avocation")
# --------------------------------------------------------------------------
#
# The classical method reads this from whichever planet occupies the 10th
# house from the Lagna or from the Moon; failing an occupant, from the lord of
# the Navamsa held by the lord of the 10th. This module applies a simplified
# version of that chain — see career_significators() — rather than the full
# recursive Navamsa step, which is noted rather than silently reproduced.

CAREER_BY_PLANET: dict[str, str] = {
    "Sun": "leadership or public office, and trade in gold, perfumes, or medicine",
    "Moon": "agriculture, trade in water-linked goods, or work that depends "
            "on the custom of women",
    "Mars": "metals, weapons, engineering, or work that calls for physical "
            "courage and boldness",
    "Mercury": "writing, accounting, teaching, or skilled handicraft",
    "Jupiter": "teaching, the priesthood, law, or work connected with mining "
               "and precious materials",
    "Venus": "gems and luxury goods, the arts, or the keeping of cattle and horses",
    "Saturn": "manual labour or service — a position earned through endurance "
              "rather than given",
}


def career_significators(view: dict) -> list[dict]:
    """Which grahas carry the 10th house's career signal, and their theme.

    Simplified from the source's own chain (10th-house occupant; failing
    that, the 10th lord; the full method also reads the Navamsa lord of that
    lord, which is not reproduced here). Both the Lagna's and the Moon's 10th
    house are read, since the source explicitly allows either.
    """
    out: list[dict] = []
    seen: set[str] = set()
    lagna_index = SIGNS.index(view["lagna_sign"])
    moon_index = SIGNS.index(view["signs"]["Moon"])
    for ref, start_index in (("Lagna", lagna_index), ("Moon", moon_index)):
        tenth_sign = SIGNS[(start_index + 9) % 12]
        occupants = [g for g in GRAHAS if view["signs"][g] == tenth_sign]
        source_planets = occupants or [DOMICILE[tenth_sign]]
        for planet in source_planets:
            if planet in seen:
                continue
            seen.add(planet)
            out.append({
                "planet": planet,
                "from": ref,
                "role": "occupant of the 10th" if planet in occupants else "lord of the 10th",
                "theme": CAREER_BY_PLANET[planet],
            })
    return out


# --------------------------------------------------------------------------
# Mahadasha effects, by planet — Brihat Jataka ch. 8, stanzas 12-18
# --------------------------------------------------------------------------
#
# The source frames every dasha as classifiable "benefic" or "malefic" for the
# native (by the condition of its lord — exalted/own sign reads benefic,
# debilitated/enemy sign reads malefic) and gives a different result text for
# each reading. Rahu and Ketu are not covered by this chapter of the source
# and are left out rather than guessed at.

MAHADASHA_EFFECTS: dict[str, dict[str, str]] = {
    "Sun": {
        "benefic": "wealth through gold, perfumes, or royal and official "
                   "favour; renewed courage and public standing",
        "malefic": "friction through spouse, children, money or authority; "
                   "health strain around the chest",
    },
    "Moon": {
        "benefic": "gains through domestic goods, family, or the public; "
                   "growing wisdom and reputation",
        "malefic": "a drift into idleness, loss of standing, friction with elders",
    },
    "Mars": {
        "benefic": "victory over rivals, and gains through siblings, land, "
                   "or courageous action",
        "malefic": "strife with family and friends, health trouble tied to "
                   "blood or fever, a harder temper",
    },
    "Mercury": {
        "benefic": "income through communication, learning, or trade; a "
                   "growing reputation among the learned",
        "malefic": "sharper speech, financial or legal entanglement, nervous strain",
    },
    "Jupiter": {
        "benefic": "wealth through wisdom, teaching, or ceremony; the "
                   "friendship of the powerful",
        "malefic": "effortful learning, minor physical strain — notably the "
                   "feet or ears — and friction with difficult people",
    },
    "Venus": {
        "benefic": "pleasure, comfort, and gain through relationships, art, "
                   "or trade",
        "malefic": "conflict with others, particularly over indulgence or rivalry",
    },
    "Saturn": {
        "benefic": "steady gains through service, land, or a long-held "
                   "position of responsibility",
        "malefic": "health strain — notably joints and nerves — domestic "
                   "friction, and a sense of being controlled by dependents",
    },
}


def mahadasha_reading(planet: str, favourable: bool) -> str | None:
    """The classical dasha-effect text for one graha, benefic or malefic reading.

    `favourable` should come from the planet's own condition (dignity, house,
    aspect) — this module supplies the text, not the judgement of which
    reading applies. Returns None for Rahu/Ketu: ch. 8 of the source does not
    cover them, and this is not a place to invent a result for them.
    """
    entry = MAHADASHA_EFFECTS.get(planet)
    if entry is None:
        return None
    return entry["benefic" if favourable else "malefic"]


# --------------------------------------------------------------------------
# Antardasha (sub-period) effects, by planet — a modern compilation
# presented as "Ravana Samhita" (see docs/sources/ravana_samhita_notes.md).
# Unlike MAHADASHA_EFFECTS above, the source gives one fixed result per
# planet rather than a benefic/malefic split, and it covers all nine grahas
# including Rahu/Ketu — that asymmetry with the Mahadasha table is the
# source's own, not something this module is smoothing over.
# --------------------------------------------------------------------------

ANTARDASHA_EFFECTS: dict[str, str] = {
    "Sun": "separation from family or a spell away from home, mental strain "
           "and worry, health trouble, and a risk of loss through theft or "
           "squandering of savings",
    "Moon": "material gains and comfort — fine possessions, victory over "
            "rivals, growing strength, and a generally comfortable, "
            "well-provided life",
    "Mars": "conflict with authority or the threat of theft, fire-related "
            "harm, illness, and a run of worry and hardship",
    "Mercury": "comfort and enjoyment, gains in wealth and valuables, and — "
               "alongside the material ease — a turn toward spiritual reflection",
    "Jupiter": "advancement to authority or a position of standing, a "
               "virtuous and settled mind, good health, and steady growth "
               "in wealth and provisions",
    "Venus": "gains in property or land, good health and vigour, marks of "
             "honour and status, growing wealth and family, and increased longevity",
    "Saturn": "false blame or reputational trouble, a harsher temperament, "
              "financial loss, friction with friends and family, and "
              "setbacks in one's work",
    "Rahu": "confusion and poor judgement, anxiety, physical discomfort, "
            "restriction or entanglement, and hardship tied to want",
    "Ketu": "exhaustion tied to separation from a partner, financial loss, "
            "illness, friction with family, and travel or dislocation",
}


def antardasha_reading(planet: str) -> str | None:
    """The classical antardasha-effect text for one graha, unconditional on
    its dignity (the source gives a single fixed reading per planet, not a
    benefic/malefic split — see the module note above `ANTARDASHA_EFFECTS`).
    """
    return ANTARDASHA_EFFECTS.get(planet)


# --------------------------------------------------------------------------
# Yogini Dasha effects, by Yogini name — the same modern compilation
# presented as "Ravana Samhita" that supplies vargas.YOGINI_DASHA in
# chart_service.py. The source gives one result text per Yogini and reuses
# it at both the mahadasha and antardasha timescale (its own "Mangaladi
# dasha phal, again" heading for the antardasha-level reading repeats the
# same eight themes rather than giving a second table) — this module follows
# that, rather than inventing a distinct antardasha-level text the source
# doesn't have.
# --------------------------------------------------------------------------

YOGINI_EFFECTS: dict[str, str] = {
    "Mangala": "the neutralising of a rival's or an opponent's trouble, "
               "gains in property, vehicles, gold or fine possessions, and "
               "family good fortune — a generally auspicious start",
    "Pingala": "a comfortable opening that tends to give way to growing "
               "physical strain, mental agitation, and friction within the "
               "family as the period goes on",
    "Dhanya": "growth in wealth and resources, recognition or favour from "
              "those in authority, victory in disputes, patience and "
              "resolve, and comfort from spouse and children",
    "Bhramari": "displacement or travel away from home, setbacks in "
                "conflict, strain on a partner, mounting debt and illness, "
                "and friction with relatives",
    "Bhadrika": "financial gain, rising happiness, recognition of one's own "
                "abilities, honour from those in authority, and a "
                "generally auspicious, comfortable stretch",
    "Ulka": "travel, illness and distress, loss of wealth or separation "
            "from one's homeland, and friction with friends and family",
    "Siddha": "a real sense of accomplishment and standing, comfort from "
              "friends and family, growing reputation, and success in "
              "one's undertakings",
    "Sankata": "conflict and friction with others, health affliction, "
               "strain on close relationships, loss of resources or "
               "livestock, restlessness, and difficulty with those in "
               "authority",
}


def yogini_dasha_reading(name: str) -> str | None:
    """The classical result text for one Yogini Dasha name (Mangala,
    Pingala, ... Sankata) — used for both the mahadasha and antardasha
    timescale; see the module note above `YOGINI_EFFECTS`.
    """
    return YOGINI_EFFECTS.get(name)


# --------------------------------------------------------------------------
# Conjunction meanings — Brihat Jataka ch. 14 ("Double Planetary Yogas"),
# cross-read against the Bhrigu-school tradition's own equivalent list
# (independently phrased; see the module docstring on why).
# --------------------------------------------------------------------------

CONJUNCTION_DELINEATION: dict[frozenset, str] = {
    frozenset({"Sun", "Moon"}): "public visibility mixed with private feeling — "
        "cleverness and a magnetic presence, alongside some tension between "
        "duty and instinct",
    frozenset({"Sun", "Mars"}): "forceful, assertive energy — courage and "
        "initiative, with a temper that needs a legitimate outlet",
    frozenset({"Sun", "Mercury"}): "articulate confidence — learned, "
        "well-spoken, and capable of real standing (this is Budha-Aditya "
        "Yoga; see vargas.budha_aditya for the formation test)",
    frozenset({"Sun", "Jupiter"}): "moral weight and generosity — respected, "
        "well-connected, and drawn to service",
    frozenset({"Sun", "Venus"}): "charm and creative flair — sociable, though "
        "comfort can compete with duty",
    frozenset({"Sun", "Saturn"}): "authority earned through discipline — "
        "durable achievement, usually after real hardship",
    frozenset({"Moon", "Mars"}): "drive fused with feeling — earning power "
        "and enterprise, with a temper that runs hot (this is Chandra-Mangala "
        "Yoga; see vargas.chandra_mangala)",
    frozenset({"Moon", "Mercury"}): "quick, expressive, warm-hearted "
        "communication",
    frozenset({"Moon", "Jupiter"}): "generous, protective, and well-regarded — "
        "warmth that draws real goodwill",
    frozenset({"Moon", "Venus"}): "an affectionate, comfort-seeking nature, "
        "drawn to beauty and ease",
    frozenset({"Moon", "Saturn"}): "emotional restraint — a heavier, more "
        "cautious inner life, self-reliant rather than openly needy",
    frozenset({"Mars", "Mercury"}): "sharp, incisive thinking, put to "
        "practical or competitive use",
    frozenset({"Mars", "Jupiter"}): "principled assertiveness — courage in "
        "service of a cause, and real leadership potential",
    frozenset({"Mars", "Venus"}): "a strong pull between desire and "
        "discipline — passionate, sometimes turbulent, relationships",
    frozenset({"Mars", "Saturn"}): "grinding effort — real endurance under "
        "real pressure, at the cost of ease",
    frozenset({"Mercury", "Jupiter"}): "articulate wisdom — a natural "
        "teacher or communicator",
    frozenset({"Mercury", "Venus"}): "refined taste and diplomatic skill — a "
        "gift for the arts or for negotiation",
    frozenset({"Mercury", "Saturn"}): "methodical, careful thinking, "
        "sometimes at the price of spontaneity",
    frozenset({"Jupiter", "Venus"}): "abundance and goodwill — a fortunate, "
        "well-liked combination",
    frozenset({"Jupiter", "Saturn"}): "the long view — real achievement "
        "built slowly, through structure rather than luck",
    frozenset({"Venus", "Saturn"}): "loyalty and endurance in relationships, "
        "sometimes with a note of self-denial or delay",
}


def conjunctions_present(view: dict) -> list[dict]:
    """Every pair of the seven classical grahas sharing a sign in this chart."""
    out = []
    for i, a in enumerate(GRAHAS):
        for b in GRAHAS[i + 1:]:
            if view["signs"][a] == view["signs"][b]:
                text = CONJUNCTION_DELINEATION.get(frozenset({a, b}))
                if text:
                    out.append({
                        "planets": [a, b], "sign": view["signs"][a], "note": text,
                    })
    return out


# --------------------------------------------------------------------------
# Dignity delineation — richer per-planet text than vargas.DIGNITY_TEXT's
# generic phrasing, informed by (but not quoting) the Bhrigu-school tradition.
# --------------------------------------------------------------------------

DIGNITY_DELINEATION: dict[str, dict[str, str]] = {
    "Sun": {
        "exaltation": "operating at full power — confident, purposeful, and "
                      "given more authority than it strictly asked for",
        "moolatrikona": "steady and self-assured, working from real inner conviction",
        "own_sign": "comfortable in its own authority, direct and effective",
        "friendly_sign": "supported and able to act, though the confidence "
                         "is partly borrowed",
        "neutral_sign": "workable but impersonal — capable, without much "
                        "warmth behind it",
        "enemy_sign": "working against the grain — effort is real but "
                     "recognition is grudging",
        "debilitation": "undercut — the usual confidence gives way to "
                       "self-doubt or a struggle to be seen",
    },
    "Moon": {
        "exaltation": "emotionally at its best — nourishing, intuitive, and "
                     "unusually resilient",
        "moolatrikona": "settled and nurturing, a genuine source of comfort to others",
        "own_sign": "at home — emotional needs are easy to read and easy to meet",
        "friendly_sign": "reasonably at ease, drawing support from its surroundings",
        "neutral_sign": "even-keeled — neither especially settled nor "
                        "especially strained",
        "enemy_sign": "unsettled — moods run changeable and hard to soothe",
        "debilitation": "insecure — prone to anxiety, and to seeking comfort "
                       "in the wrong places",
    },
    "Mars": {
        "exaltation": "at its most capable — decisive, disciplined, and "
                     "physically formidable",
        "moolatrikona": "confident and direct, acting from real conviction "
                        "rather than impulse",
        "own_sign": "assertive and effective, comfortable taking the lead",
        "friendly_sign": "able to act with support, even if the drive is "
                         "not fully its own",
        "neutral_sign": "functional — gets things done, without particular "
                        "flair either way",
        "enemy_sign": "frustrated — the energy is real but keeps meeting resistance",
        "debilitation": "blunted — courage curdles into recklessness, or "
                       "just as often, timidity",
    },
    "Mercury": {
        "exaltation": "unusually sharp — quick, precise, and articulate "
                     "beyond its years",
        "moolatrikona": "clear-headed and well-organised in its thinking",
        "own_sign": "comfortable with ideas and language, a natural communicator",
        "friendly_sign": "capable, though the cleverness leans on outside support",
        "neutral_sign": "adequate — communicates well enough, without real spark",
        "enemy_sign": "scattered — thinking that struggles to settle or convince",
        "debilitation": "confused — a mind that doubts itself and "
                       "second-guesses its own judgement",
    },
    "Jupiter": {
        "exaltation": "expansive and trusted — wisdom and good fortune arrive together",
        "moolatrikona": "genuinely wise, generous from a position of real strength",
        "own_sign": "comfortable granting and receiving trust, a natural teacher",
        "friendly_sign": "well-meaning and supported, if not fully self-sufficient",
        "neutral_sign": "moderate — neither notably fortunate nor notably strained",
        "enemy_sign": "overreaching — good intentions outrun good judgement",
        "debilitation": "diminished — the usual optimism curdles into "
                       "complacency or excess",
    },
    "Venus": {
        "exaltation": "at its most refined — magnetic, tasteful, and "
                     "genuinely well-loved",
        "moolatrikona": "comfortable and gracious, at ease with pleasure and beauty",
        "own_sign": "at home in relationship and creativity, naturally likable",
        "friendly_sign": "pleasant and supported, though the charm leans on others",
        "neutral_sign": "pleasant enough, without the pull of real attraction",
        "enemy_sign": "uneasy in love or comfort — indulgence stands in for "
                     "real connection",
        "debilitation": "undervalued — affection and taste go unrecognised, "
                       "or are used against its own interest",
    },
    "Saturn": {
        "exaltation": "at its most disciplined — real authority, earned the "
                     "hard way and genuinely deserved",
        "moolatrikona": "steady and dutiful, comfortable carrying real responsibility",
        "own_sign": "capable of sustained, structured effort, and trusted with it",
        "friendly_sign": "diligent and supported, though the discipline is "
                         "not fully self-generated",
        "neutral_sign": "ordinary discipline — duty performed without "
                        "particular struggle or particular reward",
        "enemy_sign": "burdened — duty feels heavier than it should, and "
                     "recognition is slow",
        "debilitation": "fearful — restriction without the compensating "
                       "maturity, delay without the reward",
    },
}


def dignity_state(planet: str, sign: str, degree: float | None = None) -> str:
    """Which of the seven dignity states a graha's placement falls into.

    Ordered exaltation > moolatrikona > own sign > friendly > neutral >
    enemy > debilitation, matching vargas._dignity's own ranking for the
    states it shares. Friendly/enemy/neutral are read off the sign's lord's
    naisargika relationship to the planet (matching.NAISARGIKA_FRIENDS /
    NAISARGIKA_ENEMIES, BPHS ch. 3) — the same table vargas.py and
    matching.py already cite for it, so this is not a fourth copy of the
    friendship data, only a fourth reader of it.
    """
    if EXALTATION.get(planet) == sign:
        return "exaltation"
    if planet in MOOLATRIKONA:
        mt_sign, low, high = MOOLATRIKONA[planet]
        if sign == mt_sign and degree is not None and low <= degree < high:
            return "moolatrikona"
    if sign in OWN_SIGNS.get(planet, ()):
        return "own_sign"
    if DEBILITATION.get(planet) == sign:
        return "debilitation"
    lord = DOMICILE[sign]
    if lord == planet:
        return "own_sign"
    if lord in NAISARGIKA_FRIENDS.get(planet, set()):
        return "friendly_sign"
    if lord in NAISARGIKA_ENEMIES.get(planet, set()):
        return "enemy_sign"
    return "neutral_sign"


def dignity_delineation(planet: str, sign: str, degree: float | None = None) -> dict:
    """The full dignity read for a graha: which state, and the text for it."""
    state = dignity_state(planet, sign, degree)
    return {
        "planet": planet, "sign": sign, "state": state,
        "note": DIGNITY_DELINEATION.get(planet, {}).get(state, ""),
    }


# --------------------------------------------------------------------------
# Baladi Avastha — a planet's five-fold "life stage" within its sign's 30°,
# by 6° step, read in reverse for even signs. Source: a modern compilation
# presented as "Ravana Samhita" (see docs/sources/ravana_samhita_notes.md);
# the rule itself is standard across the tradition, not this compilation's
# own wording.
# --------------------------------------------------------------------------

_AVASTHA_ORDER = ("Bala", "Kumara", "Yuva", "Vriddha", "Mrita")

_AVASTHA_TEXT: dict[str, str] = {
    "Bala": "an infant state — its significations are slow to mature and "
            "easily overshadowed by other factors in the chart",
    "Kumara": "a growing, adolescent state — results build gradually rather "
              "than arriving in full",
    "Yuva": "a youthful, mature state — the planet is at its most capable "
            "and gives its significations in full",
    "Vriddha": "an aged state — past its peak; results are real but past "
               "their prime, or slower to renew",
    "Mrita": "a 'dead' (Mrita) state — significations are weak or dormant "
             "until a stronger dasha or transit revives them",
}


def baladi_avastha(sign: str, degree: float) -> dict:
    """Which of the five Baladi Avastha life-stages a placement falls in.

    Each sign's 30° is read in five 6° steps, Bala > Kumara > Yuva > Vriddha
    > Mrita in odd signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius),
    reversed in even signs. `degree` is the planet's degree within its own
    sign (0-30), the same value vargas.chart_view supplies as
    ``view["degrees"][planet]``.
    """
    if not 0 <= degree < 30:
        raise ValueError(f"degree must be 0..30 within the sign, got {degree}")
    step = min(int(degree // 6), 4)
    odd_sign = SIGNS.index(sign) % 2 == 0
    order = _AVASTHA_ORDER if odd_sign else tuple(reversed(_AVASTHA_ORDER))
    state = order[step]
    return {"state": state, "note": _AVASTHA_TEXT[state]}


# --------------------------------------------------------------------------
# Per-Lagna planet-in-house text — the Bhrigu Samhita compilation's own
# Lagna-specific version of the Brihat Jataka table below (see the module
# docstring). Each entry condenses the source's own placement + dignity +
# aspect walk-through into the same one/two-sentence register the rest of
# this module uses; the full aspect-by-aspect detail the source gives is not
# reproduced, matching how the Brihat Jataka table below is handled too.
#
# ARIES (Mesha) LAGNA — the first Lagna transcribed, complete except three
# entries: printed page 107 of the scanned source is missing outright (a
# jump from printed page 106 to 108 across every planet's section on that
# spread, confirmed against the page images, not an OCR segmentation
# failure), which is exactly where Jupiter's 8th/9th/10th-house entries for
# this Lagna would sit. Left absent rather than guessed at; see
# docs/sources/bhrigu_samhita_notes.md.
# --------------------------------------------------------------------------

BHRIGU_LAGNA_HOUSE_TEXT: dict[str, dict[str, dict[int, str]]] = {
    "Aries": {
        "Sun": {
            1: "Exalted and vitalised — confident, learned, courageous and "
               "ambitious, with abundant children — but its aspect on a "
               "debilitated 7th house brings friction in marriage and partnership",
            2: "Financial strain and setbacks in education or with children "
               "(Sun rules the 5th here); family and property disputes "
               "recur — but its aspect on the 8th brings long life and "
               "occasional windfalls",
            3: "Sharpens intellect and courage, and its aspect on the 9th "
               "brings good fortune, generosity and a devout nature; "
               "siblings are supportive and the native speaks with real presence",
            4: "Brings comfort through home, land and vehicles, and success "
               "through learning — but its aspect on the 10th (an enemy's "
               "sign) strains ties with the father and brings setbacks in "
               "official life, softened by some lasting respect",
            5: "In its own sign here, gives real learning, fame and the "
               "blessing of children — but its aspect on the 12th brings "
               "obstacles to charitable works, and the native's sharp "
               "tongue and pride draw private criticism",
            6: "Gives steady victory over rivals and deep learning despite "
               "some difficulty in early education (Sun rules the 5th "
               "here); its aspect on the 12th brings recognition and gain "
               "abroad, at the cost of higher spending and some worry over children",
            7: "In an enemy's sign here, brings recurring strain in "
               "marriage and partnership — but its aspect back on the "
               "Lagna gives a commanding, resourceful presence, even as "
               "the same placement (Sun rules the 5th) weakens the "
               "children/legacy side of life",
            8: "Friend's sign brings longevity and gains through "
               "inheritance or hidden wealth, but the 8th house's nature "
               "weakens spouse and children, and its aspect on the 2nd "
               "brings ongoing dissatisfaction over money and family",
            9: "One of its best placements — real learning, righteousness, "
               "fame and continuous good fortune, with charitable and "
               "devout instincts; its aspect on the 3rd sharpens courage "
               "and strengthens ties with siblings",
            10: "In an enemy's sign here, brings some setbacks with the "
                "father and in career or public standing, though a real "
                "gift for foreign languages or official communication; its "
                "aspect on the 4th brings strong comfort from mother, home and land",
            11: "Enemy's sign here still gives substantial gains (malefics "
                "are held to be strong in the 11th) after real effort, and "
                "its aspect on the 5th adds gains through education and "
                "children — though the native's sharp tongue serves mostly self-interest",
            12: "Friend's sign here brings good standing with distant "
                "places at the cost of heavy expenses, and some worry over "
                "children's education — offset by its aspect on the 6th, "
                "which brings victory over rivals",
        },
        "Moon": {
            1: "Friend's sign brings mental and domestic peace; its aspect "
               "on the 7th supports a happy marriage, steady livelihood and good health",
            2: "Exalted here — brings great wealth, prosperity and family "
               "comfort, tempered by some deficiency on the mother's side "
               "and mild worry over health and inheritance from its aspect on the 8th",
            3: "Friend's sign strengthens courage and sibling ties, and — "
               "ruling the 4th from here — brings home and property "
               "comfort; its aspect on the 9th makes for a generous, "
               "learned and fortunate life",
            4: "In its own sign here, gives full comfort through mother, "
               "home and property — but its aspect on the 10th brings "
               "friction with the father and setbacks to reputation that "
               "keep this otherwise prosperous placement from bringing due recognition",
            5: "Friend's sign gives real learning and the blessing of "
               "children; its aspect on the 11th brings some difficulty "
               "with income, borne with patience — the native is "
               "otherwise calm, capable and content, close to the mother, "
               "though career gains come with effort",
            6: "Friend's sign brings the wisdom and valour to make peace "
               "with rivals, though domestic harmony stays uneven; its "
               "aspect on the 12th adds gain from distant places and "
               "spending on worthy causes",
            7: "Brings comfort through a partner and material pleasure, "
               "good looks and property; its aspect on the Lagna adds "
               "physical vitality, honour and general success",
            8: "Friend's sign here still brings loss around mother, "
               "property or real estate and an unsettled home life — "
               "offset by its aspect on the 2nd, which keeps opening "
               "opportunities for wealth",
            9: "Friend's sign draws the native toward religion, charity "
               "and pilgrimage, and brings comfort from mother and "
               "property; its aspect on the 3rd strengthens courage and "
               "sibling ties, rounding out a fortunate, righteous nature",
            10: "Enemy's sign here brings some friction with the father, "
                "yet recognition and success in career through sheer "
                "diligence; its aspect on the 4th gives strong comfort "
                "from mother and home, often built through the native's own effort",
            11: "Enemy's sign here still grows income steadily through "
                "emotional intelligence, and its aspect on the 5th brings "
                "learning and the blessing of children, despite some "
                "difficulty along the way",
            12: "Friend's sign brings spending toward good causes and "
                "ties to distant places; its aspect on the 6th brings "
                "victory over rivals through wisdom and a knack for "
                "resolving disputes",
        },
        "Mars": {
            1: "In its own sign here, gives a strong body, self-reliance "
               "and courage, with a long life despite occasional illness "
               "(Mars rules the 8th here) — its aspect on the 7th brings "
               "some loss through partnership or business",
            2: "Enemy's sign here brings setbacks in accumulating wealth "
               "and some physical discomfort, and its far-reaching "
               "aspects touch nearly every house — difficulty with "
               "children, support for longevity, and obstacles to fortune "
               "all appear in turn",
            3: "Friend's sign brings courage and daring, though as 8th "
               "lord here it weakens comfort from siblings; its aspects "
               "bring victory over rivals, growing fortune, and some "
               "difficulty with the father or career in turn",
            4: "Debilitated here despite sitting in a friend's sign — "
               "comfort through mother, home and property runs short, and "
               "spousal comfort is likewise strained, though gains do "
               "come through the father or government, and income "
               "arrives only with real effort",
            5: "Friend's sign brings some difficulty around education and "
               "children, softened by support for longevity from its own "
               "aspect on the 8th, and income arriving from distant "
               "places, at the cost of higher expenses",
            6: "Brings victory over rivals, courage and fearlessness; its "
               "aspects obstruct smooth career progress even as they "
               "bring gain from distant places, and keep the native "
               "healthy, self-assured and forceful",
            7: "Enemy's sign here brings difficulty around a partner or "
               "business — offset by exaltation-strength aspects that "
               "advance career and reputation, and keep the body healthy, "
               "even as wealth and family gains come only through hard, "
               "under-rewarded effort",
            8: "In its own sign here, gives long life and gains through "
               "inheritance, though as Lagna lord it costs some physical "
               "grace; its aspects bring income only with difficulty, "
               "ongoing worry over money and family, and a boost to "
               "courage that comes at the cost of sibling harmony",
            9: "Friend's sign lifts fortune despite some difficulty (Mars "
               "rules the 8th here), and its aspects raise both spending "
               "and courage while leaving comfort in travel, property and "
               "home somewhat diminished",
            10: "Exalted here (though in an enemy's sign) — brings "
                "hostility toward the father alongside real advancement "
                "in career and public life; its aspects strengthen the "
                "body and bring real success through education and "
                "children, even as home comfort suffers",
            11: "Exalted here — grows income steadily despite some "
                "difficulty (Mars rules the 8th here), and its aspects "
                "bring dissatisfaction over money alongside success in "
                "education and real courage against rivals",
            12: "Friend's sign brings frequent travel and heavy spending, "
                "with some cost to appearance; its aspects sharpen "
                "courage even as they strain both sibling and spousal "
                "comfort along the way",
        },
        "Mercury": {
            1: "Friend's sign gives an industrious nature, though as 6th "
               "lord here it brings some tendency to illness and reduced "
               "sibling comfort; success in career comes through hard "
               "work, tempered by some difficulty with a spouse",
            2: "Friend's sign lifts wealth and drive, but as both 3rd and "
               "8th lord here it brings some loss and difficulty in "
               "earning and some reduction in sibling comfort — offset by "
               "an aspect on the 8th that lengthens life and brings gains "
               "through inheritance",
            3: "In its own sign here, gives real courage and boldness — "
               "as 6th lord it wins out over rivals though sibling "
               "comfort suffers, and its aspect on the 9th brings fortune "
               "earned through the native's own valour",
            4: "Enemy's sign here brings some deficiency in comfort "
               "through mother, home or property — offset by its aspect "
               "on the 10th, which brings honour and success through "
               "father or career",
            5: "Friend's sign gives success through hard work in learning "
               "and with children, and its aspect on the 11th brings "
               "growing fortune and an edge over rivals through sheer wit",
            6: "Exalted in its own sign here — capable of real dominance "
               "over rivals and great undertakings through sheer effort, "
               "though sibling relations carry some friction and expenses "
               "abroad bring some loss",
            7: "Friend's sign brings success in business through effort, "
               "though as 6th lord it strains marriage — supportive "
               "siblings and sound judgement balance some minor physical vulnerability",
            8: "Friend's sign still brings some difficulty around "
               "courage, longevity and inheritance, and some risk from "
               "rivals (Mercury rules the 3rd and 6th here) — wealth "
               "comes only through real effort, via its aspect on the 2nd",
            9: "Friend's sign brings some difficulty to fortune (Mercury "
               "rules the 6th here), balanced by real gains that arrive "
               "through rivalry itself, and by an aspect on the 3rd that "
               "strengthens courage and self-reliance",
            10: "Friend's sign brings real advancement through courage "
                "and effort, with respect from authority and success "
                "among rivals — though as 6th lord it strains ties with "
                "the father, and its aspect on the 4th brings some "
                "deficiency in home comfort",
            11: "Friend's sign brings real success in income through hard "
                "work and wit, and gains through siblings, with some "
                "difficulty (Mercury rules the 6th here); its aspect on "
                "the 5th brings success in education, tempered by some "
                "difficulty with children",
            12: "Friend's sign brings some difficulty with expenses and "
                "foreign dealings (Mercury rules the 6th here), balanced "
                "by its own aspect on the 6th, which supports victory "
                "over rivals through wit and discretion",
        },
        "Jupiter": {
            1: "Friend's sign brings real fame, advancement and respect "
               "from distant places, and its aspects touch nearly every "
               "corner of life — deepening learning and the blessing of "
               "children, some difficulty around a partner, and rising "
               "fortune and righteousness",
            2: "Enemy's sign brings both gain and setback through distant "
               "connections, with wisdom-driven success over rivals, "
               "gains through longevity or inheritance, and some "
               "difficulty with father or career in turn",
            3: "Friend's sign brings courage and sibling comfort; its "
               "aspects raise fortune and righteousness even as they "
               "bring some difficulty around a partner and some "
               "difficulty with income",
            4: "Friend's sign brings full comfort through mother, home "
               "and property; its aspects bring gains through longevity, "
               "some deficiency with father or career, and good standing "
               "abroad despite heavy expense",
            5: "Friend's sign brings learning, wisdom and the blessing of "
               "children, deepened further by its own aspect on the 9th; "
               "income comes with some difficulty but eventual success, "
               "and the body stays healthy and attractive throughout",
            6: "Own sign here brings success over rivals and advancing "
               "fortune despite obstacles along the way — its aspects "
               "bring some deficiency with father or career, heavy "
               "expense offset by gain from distant places, and some "
               "discord over money and family",
            7: "Enemy's sign brings difficulty around a partner or "
               "business and some obstacle to income, balanced by an "
               "aspect on the Lagna that gives an attractive body and "
               "commanding presence, and one on the 3rd that keeps "
               "sibling ties and courage strong",
            # 8, 9, 10: missing — printed page 107 of the source is absent
            # from the scan; see the section note above.
            11: "Enemy's sign brings some deficiency to fortune's "
                "advance, and its aspects give somewhat flawed success "
                "with siblings, real support for education and children, "
                "and eventual success with a partner despite initial difficulty",
            12: "In its own sign here, brings heavy expense alongside "
                "gain from distant places; its aspects bring comfort "
                "through mother and home, success over rivals through "
                "good judgement, and further gains tied to longevity and inheritance",
        },
        "Venus": {
            1: "Enemy's sign still gives an attractive body, respect, "
               "strength and cleverness; its own-sign aspect on the 7th "
               "brings success in partnership, tempered by some "
               "difficulty in business and family (Venus rules the 7th here)",
            2: "In its own sign here, brings wealth, family blessing and "
               "good fortune, tempered by some difficulty around a "
               "partner or business (Venus rules both the 2nd and 7th "
               "here); gains through longevity or inheritance still "
               "arrive through the native's own merit",
            3: "Friend's sign brings courage, cleverness and growing "
               "sibling ties, with some difficulty around a partner "
               "(Venus rules the 7th here); its aspect on the 9th brings "
               "fortune and a righteous character",
            4: "Enemy's sign brings some deficiency in home comfort, "
               "offset by wealth and family comfort from its kendra "
               "placement as 2nd lord; its aspect on the 10th brings "
               "success through father or career",
            5: "Enemy's sign, though placed in a trikona here, brings "
               "some difficulty before success arrives in education or "
               "with children; its aspect on the 11th supports steady income",
            6: "Debilitated despite a friend's sign — the native relies "
               "on quiet cleverness against rivals but still meets "
               "difficulty; its aspect on the 12th raises expenses even "
               "as it brings success through distant connections",
            7: "In its own sign and a kendra here — brings real success "
               "in partnership and business, and its aspect on the Lagna "
               "adds good looks, competence and physical vigour",
            8: "Enemy's sign brings real difficulty around wealth, "
               "family, and a partner (Venus rules both the 2nd and 7th "
               "here), though longevity gains some strength — wealth "
               "still grows through hard effort and cleverness, via its "
               "aspect on the 2nd",
            9: "Enemy's sign, softened by a trikona placement here — "
               "brings good fortune, cleverness and comfort from spouse "
               "and family, and its aspect on the 3rd strengthens courage "
               "and sibling ties",
            10: "Friend's sign brings comfort through father and career, "
                "and its aspect on the 4th adds comfort through mother and home",
            11: "Friend's sign brings real gain through cleverness and "
                "wealth (Venus rules the 2nd and 7th here), extending to "
                "success through a partner too; its aspect on the 5th "
                "brings similarly clever success in education and with children",
            12: "Exalted here — gains wealth and fame through cleverness "
                "in distant dealings, though spending runs high; its "
                "aspect on the 6th brings gain from rivals through "
                "cunning, at some cost in return",
        },
        "Saturn": {
            1: "Enemy's sign brings some deficiency in appearance and "
               "reputation and difficulty in career or government, "
               "balanced by aspects that strengthen courage, bring "
               "success with a partner, and raise standing through career "
               "and friendship",
            2: "Friend's sign brings wealth and family comfort, with some "
               "deficiency in home comfort, some unease alongside gains "
               "from longevity, and — through its aspect on the 11th — an "
               "added boost to lifespan",
            3: "Friend's sign brings growing courage and support from "
               "career and father (Saturn rules the 10th and 11th here), "
               "with some difficulty around children, in matters of "
               "fortune, and in foreign dealings and expenses",
            4: "Enemy's sign brings some deficiency in home comfort even "
               "as overall comfort grows, with gain and influence over "
               "rivals, real support for career and reputation, and some "
               "cost to appearance and peace of mind",
            5: "Enemy's sign, softened by a trikona here — brings success "
               "in education despite some difference with children, and "
               "its several aspects bring success in partnership, strong "
               "income, and real gains in wealth and family",
            6: "Friend's sign brings friction with the father but real "
               "success in career through difficulty, good income and "
               "victory over rivals — its aspects add success with "
               "longevity, higher expenses abroad, and stronger courage "
               "and sibling comfort",
            7: "Friend's sign brings real success in business and strong "
               "gains through father or career (Saturn rules the 10th "
               "and 11th here), balanced by some difficulty to fortune, "
               "some deficiency in appearance, and reduced home comfort",
            8: "Enemy's sign still brings gains through longevity despite "
               "reduced income; its aspects bring modest gains through "
               "father or career, wealth through hard effort, and some "
               "flaw around education or children",
            9: "Enemy's sign brings a slow start to fortune that improves "
               "with time, with support from father or career; its "
               "aspects bring good income, growing courage and sibling "
               "comfort, and real influence over rivals",
            10: "In its own sign here, brings real peace and comfort "
                "through father and career, and — through its aspect on "
                "the 7th — full success in business and partnership, "
                "despite raised expenses and some strain at home",
            11: "In its own sign here, brings strong income and real "
                "support through father or career, with some cost to "
                "appearance, some flaw in education and children, and "
                "growth in longevity though only modest gains through inheritance",
            12: "Enemy's sign brings heavy expense and loss through "
                "father, career or distant dealings, with wealth growing "
                "only through real effort, some influence gained over "
                "rivals, and real difficulty to fortune's advance",
        },
        "Rahu": {
            1: "Brings some deficiency in appearance and health and a "
               "persistent undercurrent of worry, with a temperament "
               "inclined toward deception and secretive method, despite real courage",
            2: "Brings worry over money, repeated setbacks and family "
               "distress, though the native eventually recovers "
               "financially through sheer resourcefulness and gains "
               "standing as a person of means",
            3: "Brings real growth in courage and sibling comfort — bold "
               "and resourceful, if given to revealing his own "
               "weaknesses, and successful because of exactly these traits",
            4: "Brings deficiency in home comfort, a lack of domestic "
               "peace and ongoing mental unrest, with only limited "
               "success from secretive methods",
            5: "Brings real difficulty in education despite some "
               "eventual success, and distress over children, with "
               "secretive methods bringing only ordinary results",
            6: "Brings courage and secretive method used well against "
               "rivals, holding ground under pressure; trouble recurs "
               "but is repeatedly overcome through courage and patience",
            7: "Brings worry and hardship around a partner or business, "
               "eased partly through secretive method, though domestic "
               "life stays difficult and is sustained only through real effort",
            8: "Brings repeated severe suffering through life and losses "
               "tied to inheritance; secretive method wins occasional "
               "victories, but worry never fully lifts",
            9: "Debilitated here — brings real difficulty to fortune's "
               "advance, recurring disgrace and disappointment, and few "
               "successes despite considerable suffering",
            10: "Brings difficulty with father or career and repeated "
                "crises in work and reputation, with only very limited "
                "success and much suffering along the way",
            11: "Brings very good income through hard effort (malefics "
                "are held to be strong in the 11th), though occasional "
                "loss appears where gain was expected; the native tends "
                "to be thrifty, hard-working and somewhat self-interested",
            12: "Brings heavy expense through distant dealings and real "
                "difficulty from the same connections, alternating "
                "between hardship overcome and periods of comfort, "
                "without ever quite escaping debt",
        },
        "Ketu": {
            1: "Brings physical suffering and mental worry, some injury "
               "and diminished good looks — courageous and resourceful "
               "despite frequent setbacks, and inclined toward secretive method",
            2: "Brings physical and financial strain, family trouble and "
               "disputes — some improvement comes through secretive "
               "method, though inner worry and hardship persist behind an "
               "outwardly prosperous appearance",
            3: "Debilitated here — weakens courage and sibling comfort "
               "and brings a timid disposition; secretive, self-interested "
               "method brings only rare success despite great effort",
            4: "Brings deficiency in home comfort and domestic unease, "
               "though the pressure makes the native resourceful — "
               "sometimes resourceful enough to seek relief abroad",
            5: "Brings real difficulty in education and a weak memory "
               "that limits learning, along with distress over children "
               "and a stubborn, harsh-spoken temperament; considerable "
               "effort brings only limited success",
            6: "Brings victory over rivals and a bold, discerning nature, "
               "tempered by some inner weakness and some loss on the "
               "maternal side",
            7: "Brings difficulty in business and with a partner, worked "
               "through with many secretive strategies as domestic "
               "disputes recur",
            8: "Brings repeated severe suffering and loss tied to "
               "inheritance; secretive method wins some victories, but "
               "hardship and some lasting illness remain",
            9: "Exalted here — brings good fortune, righteousness and "
               "wealth, though life still brings many changes and "
               "difficulties even at this strength; the overall character "
               "remains happy and righteous",
            10: "Brings real struggle with father, career or business, "
                "often forcing a change of course — respect and success "
                "still arrive eventually through secretive method and hard effort",
            11: "Brings very good income through secretive method, though "
                "it takes ongoing change and real effort to keep it flowing",
            12: "Brings some suffering and heavy expense tied to distant "
                "dealings, softened by Ketu's naturally benefic character "
                "— occasional small gains appear, and spending tends "
                "toward worthy causes",
        },
    },
    # TAURUS (Vrishabha) LAGNA — complete except one entry: Jupiter's 3rd
    # house. The source's own text for that entry names Sun rather than
    # Jupiter and describes a sign inconsistent with the 3rd house from
    # Taurus — an internal contradiction across a heading and its own body
    # text, not a simple misprint, and different in kind from the Aries
    # scan-page gap above. Left absent rather than guessed at.
    "Taurus": {
        "Sun": {
            1: "Friend's sign brings some deficiency in home comfort and "
               "physical beauty (Sun rules the 4th here); its aspect on "
               "the 7th brings success and harmony in partnership and "
               "business — the native carries an impressive, forceful presence",
            2: "Friend's sign brings wealth and family comfort, with some "
               "shortfall on the mother's side and underused property "
               "(Sun rules the 4th here); its aspect on the 8th brings "
               "long life and gains through inheritance",
            3: "Friend's sign brings comfort through property, home and "
               "mother, and strengthens courage and sibling ties; its "
               "aspect on the 9th brings advancement in fortune through "
               "real effort, with some laxity in religious practice",
            4: "In its own sign here, brings full comfort through mother, "
               "home and family and a real sense of style, tempered by "
               "some inner unease; its aspect on the 10th brings "
               "dissatisfaction with father or career, and standing "
               "comes only through real struggle",
            5: "Friend's sign brings comfort through mother and home, "
               "strong prospects in education and family fortune, and a "
               "deep, thoughtful character; its aspect on the 11th adds "
               "further gains through income",
            6: "Debilitated in an enemy's sign here — brings real "
               "hardship from rivals before influence is finally "
               "asserted, and some deficiency in home comfort along the way",
            7: "Friend's sign brings success through partnership and "
               "business, and gains through mother or home too; its "
               "aspect on the Lagna adds good looks, respectability and fame",
            8: "Friend's sign brings gains through longevity and "
               "inheritance, with some deficiency in courage or sibling "
               "comfort; its aspect on the 2nd grows wealth and family, "
               "though only through real effort",
            9: "Enemy's sign brings some difficulty to fortune's advance "
               "and religious practice, tempered by real respect and "
               "support through father or career; its aspect on the 3rd "
               "grows courage and sibling comfort",
            10: "Enemy's sign brings some setbacks with father, career or "
                "business, alongside a real command of foreign languages "
                "or official communication; its aspect on the 4th brings "
                "full comfort through mother and home",
            11: "Friend's sign steadily grows income and brings full "
                "comfort through mother, family and home; its aspect on "
                "the 5th adds gains through education and family fortune",
            12: "Exalted here — brings good standing with distant places "
                "at the cost of heavy expenses and some deficiency in "
                "home comfort; its aspect on the 6th wins influence over "
                "rivals only after real difficulty",
        },
        "Moon": {
            1: "Exalted here — brings strong morale, comfort through "
               "siblings and growing courage that lead to real success "
               "and recognition; its aspect on the 7th brings some "
               "dissatisfaction over partnership and some difficulty "
               "running a household",
            2: "Friend's sign brings wealth earned through personal "
               "drive and family comfort, with some deficiency in "
               "sibling comfort; its aspect on the 8th brings longevity "
               "and gains through inheritance",
            3: "In its own sign here, brings real growth in courage — "
               "bold, industrious and cheerful, drawing fame and respect; "
               "its aspect on the 9th brings little natural interest in "
               "religious practice, and fortune grows only through real effort",
            4: "Friend's sign brings comfort through mother, home and "
               "family, and grows sibling comfort and courage too; its "
               "aspect on the 10th brings success with father or career "
               "only after real effort",
            5: "Friend's sign brings real success in education and with "
               "children, and warm relations with younger siblings; its "
               "aspect on the 11th grows income and prosperity through "
               "the native's own wit",
            6: "Holds real influence over rivals and wins disputes "
               "despite some inner worry beneath an outwardly bold "
               "manner; its aspect on the 12th brings gain from distant "
               "connections at the cost of higher expense",
            7: "Debilitated here — brings loss, worry and difficulty "
               "around business and a partner, offset partly by its "
               "aspect on the Lagna, which gives good looks, respect, "
               "fame and a resilient heart despite a generally difficult life",
            8: "Friend's sign brings gains through longevity and "
               "inheritance, with some deficiency in courage and sibling "
               "comfort; its aspect on the 2nd grows wealth and family "
               "through real effort",
            9: "Enemy's sign still brings a righteous, fortunate nature "
               "and real support from siblings; its aspect on the 3rd "
               "grows courage further, giving a bold, energetic and "
               "cheerful temperament",
            10: "Enemy's sign brings some difference with the father, "
                "though real success in career through effort, and "
                "growing sibling comfort; its aspect on the 4th brings "
                "full comfort through mother, home and family",
            11: "Friend's sign brings real success in income and growing "
                "sibling comfort; its aspect on the 5th adds gains "
                "through education and children, rounding out a learned, "
                "prosperous and sweet-spoken nature",
            12: "Friend's sign brings gain through distant connections "
                "at some cost in expenses and sibling comfort; its "
                "aspect on the 6th brings success over rivals through cleverness",
        },
        "Mars": {
            1: "Friend's sign brings some tendency to blood disorders and "
               "physical frailty alongside real physical strength (Mars "
               "rules the 7th and 12th here); good standing with distant "
               "places comes with some deficiency in home comfort, "
               "success in partnership, and some worry over longevity in turn",
            2: "Friend's sign brings worry over money and family offset "
               "by gain through distant connections, some weakening of "
               "education and children, and — through its aspects — "
               "worry over longevity alongside real growth in fortune "
               "and religious standing",
            3: "Friend's sign brings loss around siblings, personal "
               "drive and business alike, though its aspects bring an "
               "end to rivals and growth in fortune and religious "
               "standing, at some cost to career and reputation",
            4: "Friend's sign brings loss through home, property and "
               "mother (Mars rules the 12th here), offset by success in "
               "partnership through its aspect on the 7th and gain from "
               "distant places, at the cost of higher expense and some "
               "loss through father or career",
            5: "Friend's sign brings worry and loss around education, "
               "children, and a partner or business alike, with some "
               "cost to longevity and higher expense offset by gain from "
               "distant connections",
            6: "Enemy's sign still brings victory over rivals, at some "
               "cost around a partner or business; its aspects advance "
               "religion and fortune, bring gain from distant places at "
               "higher expense, and leave the body somewhat weakened, "
               "prone to blood-related disorders",
            7: "In its own sign here (Mars rules both the 7th and "
               "12th), brings real strain around a partner or business "
               "despite genuine underlying strength; its aspects bring "
               "gain from distant places, some difficulty with father or "
               "career, physical weakness, and worry over money and "
               "family in turn",
            8: "Friend's sign brings difficulty around a partner, "
               "business or longevity, often forcing life abroad, though "
               "wealth still arrives from foreign connections; worry "
               "over money and family and some diminished sibling "
               "comfort follow in turn",
            9: "Enemy's sign still brings gains through a partner and "
               "career advancement through fortune, alongside genuine "
               "devotion; its aspects bring heavy expense offset by "
               "distant gains, some diminished courage, and reduced home comfort",
            10: "Enemy's sign brings trouble with father or career "
                "alongside gain from distant connections; its aspects "
                "bring some physical weakness, reduced home comfort, and "
                "friction around children, softened by modest gain "
                "through friendship",
            11: "Friend's sign brings growing income and gain through a "
                "partner and distant connections, with some difficulty "
                "in education and some loss through friendship, "
                "alongside growing influence over rivals — clever but "
                "somewhat self-interested",
            12: "In its own sign here, brings heavy expense offset by "
                "strength from distant connections; ordinary success "
                "around a partner or business (Mars rules the 7th here) "
                "comes alongside some loss to courage and sibling "
                "comfort, and wins over rivals despite uneven fortunes "
                "in partnership",
        },
        "Mercury": {
            1: "Friend's sign brings an attractive, respected and famous "
               "nature, with wealth and family strength (Mercury rules "
               "the 2nd and 5th here), and real success in education and "
               "with children; its aspect on the 7th brings success and "
               "cooperation in partnership and business",
            2: "In its own sign here, brings real growth in wealth and "
               "family, with some trouble around children and some "
               "difficulty in education; its aspect on the 8th brings "
               "longevity and gains through inheritance",
            3: "Friend's sign brings growing courage and sibling "
               "comfort, and wealth earned through the native's own "
               "drive; its aspect on the 9th rounds out a devout, "
               "learned and gracious character",
            4: "Friend's sign brings comfort through mother, home and "
               "family and a grave, discerning, intelligent character; "
               "its aspect on the 10th brings ample support from father "
               "and career, and success in professional life",
            5: "Exalted in its own sign here — blessed with children, "
               "intelligent and learned, earning wealth through wit and "
               "full family comfort; its aspect on the 11th brings some "
               "difficulty in income, offset by gains through friendship "
               "and children",
            6: "Friend's sign brings some unrest from rivals eased "
               "through wit, and some difference around children and "
               "family; its aspect on the 12th raises expenses, though "
               "brings honour and wealth through distant connections",
            7: "Friend's sign brings an intelligent spouse and real "
               "success in business, and comfort and wealth through "
               "education, family and children; its aspect on the Lagna "
               "adds good looks, fame, respect and wisdom",
            8: "Friend's sign brings gains through longevity and "
               "inheritance and growing wealth, with some trouble around "
               "family, education and children; its aspect on the 2nd "
               "brings wealth through real effort and a life of real comfort",
            9: "Friend's sign grows fortune and wealth through wit, with "
               "real comfort through religion, education, children and "
               "family; its aspect on the 3rd brings sibling comfort and "
               "growing courage",
            10: "Friend's sign brings real gains and respect through "
                "father and career, and genuine financial success "
                "through wit in business, with comfort through children "
                "too; its aspect on the 4th brings full comfort through "
                "mother, home and family",
            11: "Friend's sign brings some difficulty with friendship "
                "and saving, with modest gains through family and "
                "children, and some mental strain from worry; its "
                "aspect on the 5th brings real learning and strong "
                "standing with children",
            12: "Friend's sign brings gain through distant connections "
                "at higher expense, some dissatisfaction over education, "
                "family and wealth, and some loss around children; its "
                "aspect on the 6th brings success over rivals through wit",
        },
        "Jupiter": {
            1: "Enemy's sign still brings gains through physical effort "
               "and growing longevity; its aspects bring gains in "
               "education, partial success around partnership, and some "
               "deficiency in fortune and religious practice — "
               "advancement here comes through effort, not ease",
            2: "Friend's sign brings some difficulty in wealth and "
               "family comfort (Jupiter rules the 8th here); its aspects "
               "bring longevity and gains through inheritance, victory "
               "over rivals, and ordinary success in career alongside "
               "some friction with the father",
            # 3: skipped — the source's own text for this entry is
            # internally inconsistent (names Sun, not Jupiter, and a sign
            # that doesn't fit the 3rd house from Taurus); see the section
            # note above.
            4: "Friend's sign brings some deficiency in comfort through "
               "the mother (Jupiter rules the 8th here), alongside "
               "growing longevity and gains through inheritance; its "
               "aspect on the 10th brings some deficiency with father "
               "and reputation, offset by gain through connections, "
               "though expenses run high",
            5: "Friend's sign brings real gains in education, "
               "intelligence and children, and growing longevity; its "
               "aspects bring some deficiency in fortune and religious "
               "devotion, and good income through wit",
            6: "Friend's sign brings wisdom-driven victory over rivals, "
               "though with some deficiency in longevity gains (Jupiter "
               "rules the 8th here); its aspects raise expenses even as "
               "they bring connections abroad, and demand real physical "
               "effort for a livelihood",
            7: "Friend's sign brings difficulty around a partner or "
               "business (Jupiter rules the 8th here), offset by "
               "growing longevity and inheritance; its aspects bring "
               "good income, some physical frailty, and growing sibling "
               "comfort and courage",
            8: "In its own sign here (Jupiter rules the 8th), brings "
               "growing longevity despite some difficulty with income; "
               "its aspects bring gain through distant connections at "
               "higher expense, growth in wealth through real effort, "
               "and some dissatisfaction over home comfort",
            9: "Enemy's sign brings some weakness in fortune and "
               "religious practice, and some deficiency in appearance, "
               "demanding real effort for advancement; its aspects bring "
               "growing sibling comfort, courage and success over rivals",
            10: "Enemy's sign brings some loss through father, career or "
                "business (Jupiter rules the 8th here), with limited "
                "success in income, offset by growing wealth with family "
                "support and gains through longevity, despite ongoing "
                "trouble from rivals",
            11: "In its own sign here (Jupiter rules both the 8th and "
                "11th), brings good income despite real effort required, "
                "and growing longevity; its aspects bring sibling "
                "comfort, success in education and children, and good "
                "gain through business alongside some difficulty around "
                "a partner",
            12: "Friend's sign brings gain through distant connections "
                "at higher expense; its aspects bring some difficulty "
                "though real comfort with the mother, influence over "
                "rivals through wisdom, and some deficiency in longevity "
                "with expenses running ahead of income",
        },
        "Venus": {
            1: "In its own sign and as Lagna-lord here, brings real "
               "growth in physical beauty and inner strength, and "
               "victory over rivals, though occasional illness; its "
               "aspect on the 7th brings success through wit in "
               "partnership and business, rounding out a generally "
               "comfortable life",
            2: "Friend's sign grows wealth and family through physical "
               "effort, with some difficulty in personal comfort; its "
               "aspect on the 8th brings some deficiency in longevity, "
               "offset by gain from rivals through wit",
            3: "Enemy's sign still grows courage despite some friction "
               "with siblings; its aspect on the 9th brings a devout, "
               "fortunate nature — bold, clever and hard-working, "
               "gaining wealth, fame and respect through these very qualities",
            4: "Enemy's sign brings some deficiency in comfort through "
               "mother and home, though comfort still arrives despite "
               "the shortfall, aided by peace and cleverness that win "
               "out over rivals; its aspect on the 10th brings success "
               "with father and career, and real gains in wealth and fame",
            5: "Debilitated here — weakens education and children, "
               "though success over rivals still comes through wit; its "
               "aspect on the 11th brings income through hard work and "
               "mental sharpness, at the cost of some worry and a dip in "
               "physical beauty",
            6: "In its own sign here, brings victory over rivals "
               "through physical strength and cleverness, though as "
               "Lagna-lord placed in the 6th it costs some physical "
               "beauty; gain through the mother comes with some "
               "dependency, and its aspect on the 12th brings gain from "
               "distant connections at higher expense — a commanding "
               "figure, if caught in recurring disputes",
            7: "Friend's sign brings some friction around a partner and "
               "real success in business through hard physical effort; "
               "its aspect on the Lagna brings deep worldly engagement, "
               "tempered by a tendency toward illness",
            8: "Enemy's sign brings some deficiency in physical beauty "
               "and a tendency toward illness, though longevity and "
               "gains through inheritance arrive via quiet cleverness; "
               "its aspect on the 2nd grows wealth through hard effort, "
               "alongside some weakness on the maternal side and "
               "digestive trouble",
            9: "Friend's sign advances fortune through physical effort "
               "and brings success over rivals; a handsome build comes "
               "with a tendency toward illness, and its aspect on the "
               "3rd brings sibling comfort through some difficulty and "
               "growing courage",
            10: "Friend's sign brings some ordinary friction with the "
                "father, though real success in career and business "
                "through effort, and continued influence over rivals; "
                "its aspect on the 4th brings success through mother, "
                "home and property, achieved with some difficulty",
            11: "In its own sign here, grows income through hard effort "
                "despite a tendency toward illness; its aspect on the "
                "5th brings some deficiency in education and children, "
                "alongside some gain won even from rivals",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections; a frail build accompanies "
                "real diligence, and its aspect on the 6th brings some "
                "loss through rivals despite a real cleverness at "
                "earning money",
        },
        "Saturn": {
            1: "Friend's sign brings a handsome, fortunate nature; its "
               "aspects bring some deficiency in sibling comfort "
               "alongside growing courage, success in partnership "
               "through some difficulty, and — through its own-sign "
               "aspect on the 10th — gain and respect through father and career",
            2: "Friend's sign grows wealth and family with some "
               "deficiency in overall comfort; its aspects bring some "
               "deficiency through the mother, growth in longevity, and "
               "good income and respect through career",
            3: "Enemy's sign brings some friction with siblings "
               "alongside growing courage; its aspects bring success in "
               "education and with children, real growth in fortune, "
               "and reduced expenses alongside some carelessness in "
               "foreign dealings",
            4: "Enemy's sign brings friction with the mother and some "
               "deficiency in home comfort; its aspects bring influence "
               "over rivals, gain through the maternal line, real "
               "success with father and career, and some difficulty "
               "around children",
            5: "Friend's sign brings real success in education, "
               "children and family; its aspects bring some "
               "dissatisfaction around a partner and over income, offset "
               "by real wealth and family strength",
            6: "Exalted here — brings commanding influence over rivals "
               "and success in career and business; its aspects bring "
               "anxious gains around longevity, unsatisfying foreign "
               "connections with higher expense, and growing courage at "
               "some cost to sibling harmony",
            7: "Friend's sign brings real success through a partner and "
               "strong support through father or career, though some "
               "difficulty running a household; its aspects grow "
               "religious devotion and fortune, add good looks and "
               "influence, and bring some deficiency in home comfort",
            8: "Enemy's sign still brings a long life through some "
               "difficulty; its aspects bring some deficiency with "
               "father or career, real struggle before fortune advances, "
               "wealth through careful effort, and success in education "
               "and children",
            9: "In its own sign here, brings a devout, fortunate nature "
               "and real gains through father and career; its aspects "
               "bring income through some questionable means, growing "
               "courage at some cost to sibling harmony, and strong "
               "influence over rivals",
            10: "In its own sign here, brings real gains and respect "
                "through father, career and business; its aspects bring "
                "some expense trouble and carelessness abroad, some "
                "deficiency in home comfort, and real fortune despite "
                "ongoing worry in daily life",
            11: "Friend's sign brings success in income after some "
                "difficulty and real strength of fortune; its aspects "
                "bring physical strength and longevity, success in "
                "education and children, and some difficulty around "
                "longevity-related matters",
            12: "Debilitated here — brings trouble with expenses and "
                "foreign dealings, and some difficulty with father, "
                "career, fortune and religious practice; its aspects "
                "bring ordinary help with wealth and family, influence "
                "over rivals, and modest growth in fortune despite "
                "reduced respect",
        },
        "Rahu": {
            1: "Brings some loss to physical beauty and health, though "
               "real success through quiet cleverness and inner resolve "
               "serving self-interest; bold and courageous, gaining "
               "influence and stature through many strategies, though "
               "occasionally the target of illness or injury",
            2: "Brings growth in wealth and family through many "
               "strategies and cleverness, offset by occasional hardship "
               "and struggle",
            3: "Brings some hardship around siblings and personal "
               "drive, borne outwardly with confidence while inner "
               "weakness and worry are carefully concealed",
            4: "Brings hardship and distress around mother, land and "
               "home, often forcing life abroad, with only ordinary "
               "wealth and comfort arriving through hard effort and "
               "secretive method",
            5: "Brings comfort with children through some difficulty "
               "and mental strain around learning; the native tends to "
               "talk a great deal, relies on secretive method, and can "
               "lean toward excess",
            6: "Brings real influence over rivals and skill at handling "
               "difficulties, alongside some deficiency in maternal "
               "comfort; the native excels at secretive method and "
               "hidden knowledge",
            7: "Brings distress through a partner and difficulty in "
               "business, resolved only partially through secretive "
               "method; some tendency toward disorders of the "
               "reproductive organs",
            8: "Debilitated here — brings many difficulties and losses "
               "around longevity, though the native remains courteous "
               "and composed; troubled by hidden worries, relies on "
               "secretive method, and sustains life through distant connections",
            9: "Brings difficulty in fortune and religious practice, "
               "with some success only through secretive method and "
               "hard effort; life alternates continually between "
               "comfort and hardship, wealth and want",
            10: "Brings difficulty with father, career and business, "
                "with success arriving only through secretive method, "
                "effort and restraint — though outwardly the native "
                "appears prosperous and respected",
            11: "Brings success in income despite some obstacles, "
                "through secretive method and hard effort; the native "
                "does not lose heart under pressure and eventually "
                "succeeds, though tends toward self-interest",
            12: "Brings difficulty managing expenses, requiring "
                "cleverness and secretive method; outwardly appears "
                "prosperous and influential, and real success does "
                "arrive through hard effort",
        },
        "Ketu": {
            1: "Brings some deficiency in physical beauty and "
               "persistent worry; the native influences others through "
               "physical effort and real competence, and often carries "
               "a scar or mark on the body",
            2: "Brings many worries and difficulties around wealth and "
               "family, resolved only in small part through hard effort "
               "and secretive method aimed at self-interest",
            3: "Brings some deficiency in courage, and loss or hardship "
               "connected to siblings, though the native conceals this "
               "inner weakness and finds modest success through "
               "secretive method and hard effort",
            4: "Brings difficulty around mother, home and family life, "
               "sustained through secretive method and hard effort, "
               "often forcing life abroad",
            5: "Brings difficulty in education and with children, met "
               "with modest success through courage and secretive "
               "method; the native is bold, patient, and keeps their "
               "intentions private",
            6: "Brings real influence over rivals through patience, "
               "hard effort, secretive method and courage, with some "
               "loss on the maternal side",
            7: "Brings real distress and loss through a partner, along "
               "with disorders of the reproductive organs; setbacks "
               "appear in business and domestic life too, though hard "
               "effort brings some strength",
            8: "Brings no special gain around longevity or inheritance; "
               "the native sustains life through hard effort, remaining "
               "bold, patient and skilled in secretive method, and "
               "living in comfort despite this",
            9: "Brings advancement in fortune through hard effort; "
               "devout without being showy about it — bold, "
               "hard-working, and inclined toward secretive method",
            10: "Brings some loss with father and career, with only "
                "ordinary success gained through great effort; the "
                "native appears prosperous, content and respected "
                "outwardly, though inner weakness persists",
            11: "Brings real difficulty in income, alternating between "
                "good gains and real setbacks; the native remains bold "
                "and hard-working throughout",
            12: "Brings real difficulty managing expenses and trouble "
                "through distant connections; the native remains "
                "hard-working, industrious, patient and bold",
        },
    },
}


def bhrigu_house_text(lagna_sign: str, planet: str, house: int) -> str | None:
    """The Bhrigu-school Lagna-specific reading for one graha in one house,
    if this Lagna has been transcribed (see :data:`BHRIGU_LAGNA_HOUSE_TEXT`).

    Returns None — never a guess — when the Lagna, planet or house isn't
    covered yet; callers fall back to the Lagna-independent
    :func:`planet_house_text` for the seven classical grahas, or simply omit
    Rahu/Ketu house-text, which has no other source in this module.
    """
    return BHRIGU_LAGNA_HOUSE_TEXT.get(lagna_sign, {}).get(planet, {}).get(house)


# --------------------------------------------------------------------------
# Planets in the 12 houses — Brihat Jataka ch. 20 ("On the Planets in the Bhavas")
# --------------------------------------------------------------------------
#
# The source itself is economical here: Mars, Mercury, Venus and Saturn are
# each given their OWN text for a handful of houses and told to "produce the
# same effects as the Sun" in the rest. That structure is kept rather than
# flattened, both because it is faithful to the source and because it is the
# same "base table plus named overrides" shape the rest of this codebase
# favours over one flat table per planet. Jupiter alone gets its own complete
# 12-house table (stanza 7 states all twelve directly), and Venus is told to
# follow Jupiter's table outside its own four named houses.

_BASE_HOUSE_TEXT: dict[int, str] = {   # the Sun's table, ch. 20 stanzas 1-3
    1: "a restless, combative disposition — quick to act, with vitality that "
       "can run hot",
    2: "real earning power, though income can sit at the mercy of people in authority",
    3: "intelligence and personal drive",
    4: "grief or mental strain connected with home and parents",
    5: "difficulty around children, and a thinner purse",
    6: "strength enough to see off open opposition",
    7: "friction or disgrace through partnership",
    8: "few children, and some risk to the eyes",
    9: "sons, wealth and comfort — though classical commentators disagree "
       "on this house, and a minority reading gives the opposite",
    10: "comfort, standing and real power",
    11: "considerable wealth",
    12: "a turning away from convention — the source's own word is close to 'apostasy'",
}

_MOON_HOUSE_TEXT: dict[int, str] = {   # ch. 20 stanzas 4-5, fully its own table
    1: "a strong, sometimes turbulent emotional presence; wellbeing tracks mood closely",
    2: "a large, close-knit family circle",
    3: "restless, easily provoked energy",
    4: "happiness, learning, and a strong bond to home",
    5: "sharp intelligence and real affection for children",
    6: "a softer constitution, a light appetite, and slower action under pressure",
    7: "susceptibility to envy of others' success, and strong romantic longing",
    8: "changeable moods and some vulnerability to illness",
    9: "being well liked, with good kin and material comfort",
    10: "success wherever they go, with virtue and real accomplishment",
    11: "a strong reputation and material gain",
    12: "an undermining, self-sabotaging streak beneath the surface",
}

_MERCURY_OVERRIDES: dict[int, str] = {   # ch. 20 stanza 6, houses 1-8 its own
    1: "learned and articulate from an early age",
    2: "wealth built through skill with words or numbers",
    3: "a mischievous, quick-witted streak",
    4: "genuine, solid education",
    5: "an aptitude for advising power — the source's own phrase is 'a "
       "king's minister'",
    6: "largely free of open rivals",
    7: "an aptitude for law or formal argument",
    8: "a reputation for integrity that outlasts them",
}

_MARS_OVERRIDES: dict[int, str] = {   # ch. 20 stanza 6, houses 1, 2, 9 its own
    1: "a body that carries old wounds or scars, met with self-reliance and courage",
    2: "modest means, or wealth spent on plain necessities rather than comfort",
    9: "a tendency to act first and justify it later — the source's own "
       "reading is blunt: prone to wrongdoing",
}

_JUPITER_HOUSE_TEXT: dict[int, str] = {   # ch. 20 stanza 7, fully its own table
    1: "genuine learning",
    2: "persuasive, well-regarded speech",
    3: "frugality — careful with resources",
    4: "comfort and ease at home",
    5: "intelligence, and real delight in children",
    6: "freedom from real enemies",
    7: "qualities that outshine their own father's",
    8: "a pull toward actions beneath their apparent station",
    9: "genuine devotion",
    10: "wealth and good regard",
    11: "gains that arrive easily and often",
    12: "capacity for startling, even fearsome, undertakings",
}

_VENUS_OVERRIDES: dict[int, str] = {   # ch. 20 stanza 8, houses 1, 5, 7 its own
    1: "an aptitude for love and comfort — sociable and at ease",
    5: "comfort and pleasure, often arriving through creativity or romance",
    7: "a partnership marked by both strong attraction and real friction",
}

_SATURN_LAGNA_ROYAL_SIGNS = {"Libra", "Sagittarius", "Capricorn", "Aquarius", "Pisces"}
_SATURN_HOUSE1_ORDINARY = (
    "a harder start in life — material lack, health strain in youth, and a "
    "certain roughness of manner"
)
_SATURN_HOUSE1_ROYAL = (
    "authority earned the hard way — the source likens it to governing a "
    "town or village, learned and well turned-out"
)


def planet_house_text(planet: str, house: int, lagna_sign: str | None = None) -> str:
    """The classical reading for one graha in one house from the Lagna.

    Checks the Lagna-specific Bhrigu table first (see
    :data:`BHRIGU_LAGNA_HOUSE_TEXT`) when `lagna_sign` names a Lagna that has
    been transcribed — this is the only path that can return a reading for
    Rahu/Ketu, since the tables below this point cover the seven classical
    grahas only. Failing that, falls back to the source's own
    cross-references for the Lagna-independent Brihat Jataka table: Mercury
    and Mars each have a handful of houses of their own and fall back to the
    Sun's table for the rest; Venus has three houses of its own and falls
    back to Jupiter's table (the source's own instruction, not this module's
    choice); Saturn's 1st house depends on the Lagna sign and is the one
    place this fallback path needs it. Moon and Jupiter are complete tables
    of their own; the Sun's table is the base every other planet but the
    Moon and Jupiter shares by default.
    """
    if not 1 <= house <= 12:
        raise ValueError(f"house must be 1..12, got {house}")

    if lagna_sign is not None:
        bhrigu = bhrigu_house_text(lagna_sign, planet, house)
        if bhrigu is not None:
            return bhrigu

    if planet == "Moon":
        return _MOON_HOUSE_TEXT[house]
    if planet == "Jupiter":
        return _JUPITER_HOUSE_TEXT[house]
    if planet == "Mercury":
        return _MERCURY_OVERRIDES.get(house, _BASE_HOUSE_TEXT[house])
    if planet == "Mars":
        return _MARS_OVERRIDES.get(house, _BASE_HOUSE_TEXT[house])
    if planet == "Venus":
        return _VENUS_OVERRIDES.get(house, _JUPITER_HOUSE_TEXT[house])
    if planet == "Saturn":
        if house == 1:
            if lagna_sign in _SATURN_LAGNA_ROYAL_SIGNS:
                return _SATURN_HOUSE1_ROYAL
            return _SATURN_HOUSE1_ORDINARY
        return _BASE_HOUSE_TEXT[house]
    if planet == "Sun":
        return _BASE_HOUSE_TEXT[house]
    raise KeyError(f"planet_house_text has no table for {planet!r}")


# --------------------------------------------------------------------------
# One entry point: everything above, read off a real chart at once
# --------------------------------------------------------------------------

def delineate(chart: object) -> dict:
    """The classical delineation layer for one chart: dignity, house, career,
    and conjunction text for all seven classical grahas.

    `chart` is a `chart_service` chart session or the bundle dict it carries,
    built with `zodiac='sidereal'` — the same requirement `vargas.analyse`
    makes, since this module reads its chart the same way.
    """
    view = chart_view(chart)
    lagna_sign = view["lagna_sign"]

    planets: dict[str, dict] = {}
    for planet in GRAHAS:
        sign = view["signs"][planet]
        degree = view["degrees"][planet]
        house = view["houses"][planet]
        planets[planet] = {
            "sign": sign,
            "house": house,
            "dignity": dignity_delineation(planet, sign, degree),
            "house_text": planet_house_text(planet, house, lagna_sign),
            "avastha": baladi_avastha(sign, degree),
        }

    return {
        "lagna": lagna_sign,
        "planets": planets,
        "career": career_significators(view),
        "conjunctions": conjunctions_present(view),
        "source_note": (
            "Dignity, house and conjunction text follow the Brihat Jataka "
            "(Varaha Mihira, public domain) and a traditional Bhrigu-school "
            "dignity reading, condensed and independently phrased. See "
            "docs/sources/ for the full reading notes."
        ),
    }
