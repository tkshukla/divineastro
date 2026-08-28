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

What is deliberately not attempted, matching this module's neighbours:

  * The book-length, per-Lagna version of :data:`PLANET_HOUSE_TEXT` (roughly
    1300 short entries, one per Lagna x planet x house, found in the Bhrigu
    Samhita compilation above) is not encoded here. It is a known, large asset
    for future work — see ``docs/sources/bhrigu_samhita_notes.md`` — not
    reproduced from noisy OCR of a source that likely needs a licence to quote.
    :data:`PLANET_HOUSE_TEXT` below is the Lagna-independent version from the
    public-domain Brihat Jataka instead.
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

    Follows the source's own cross-references: Mercury and Mars each have a
    handful of houses of their own and fall back to the Sun's table for the
    rest; Venus has three houses of its own and falls back to Jupiter's table
    (the source's own instruction, not this module's choice); Saturn's 1st
    house depends on the Lagna sign and is the one place this function needs
    it. Moon and Jupiter are complete tables of their own; the Sun's table is
    the base every other planet but the Moon and Jupiter shares by default.
    """
    if not 1 <= house <= 12:
        raise ValueError(f"house must be 1..12, got {house}")

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
