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
    # GEMINI (Mithuna) LAGNA — complete, all 108 entries (the first Lagna
    # after Aries with no documented gap).
    "Gemini": {
        "Sun": {
            1: "Friend's sign brings commanding energy, boldness and a "
               "strong physique, along with good sibling comfort; its "
               "aspect on the 7th brings success in business and a warm, "
               "affectionate domestic life",
            2: "Friend's sign grows wealth and family through personal "
               "drive, with some shortfall in sibling comfort; its "
               "aspect on the 8th brings some loss around inheritance "
               "and daily unease",
            3: "In its own sign here (Sun rules the 3rd), gives real "
               "strength for siblings and courage; its aspect on the 9th "
               "brings some deficiency in fortune and religious "
               "practice, rounding out a courageous, influential and "
               "content nature",
            4: "Friend's sign brings sibling comfort and growing "
               "courage, and comfort through mother, home and property; "
               "its aspect on the 10th brings success with father, "
               "career and business",
            5: "Debilitated here — weakens the intellect and brings "
               "distress through children and some weakness in courage; "
               "its aspect on the 11th brings income, though through "
               "secretive method and untruth",
            6: "Friend's sign brings victory over rivals and growing "
               "courage despite some friction with siblings; its aspect "
               "on the 12th raises expenses without much gain from "
               "distant connections",
            7: "Friend's sign brings comfort and influence through a "
               "partner, and real gain in business through effort; its "
               "aspect on the Lagna adds good looks and personal strength",
            8: "Enemy's sign brings some deficiency in longevity and "
               "inheritance, and reduced sibling comfort; its aspect on "
               "the 2nd brings gain through effort and ordinary family comfort",
            9: "Enemy's sign advances fortune through hard effort, with "
               "some indifference to religious practice and mixed "
               "sibling relations; its aspect on the 3rd grows courage "
               "further, with some help from a brother",
            10: "Friend's sign brings real strength through the father, "
                "and gain and respect through career and business; its "
                "aspect on the 4th grows courage and brings success "
                "through land, home and family",
            11: "Exalted here — grows courage and brings ample gains; "
                "its aspect on the 5th brings some setback in education "
                "and children, tempered by an otherwise disciplined, "
                "hard-working nature",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections; its aspect on the 6th "
                "establishes influence over rivals despite an "
                "underlying inner strain the native keeps hidden",
        },
        "Moon": {
            1: "Friend's sign brings wealth earned through physical "
               "strength and morale, and ample family comfort; its "
               "aspect on the 7th brings ample success through "
               "partnership and business",
            2: "In its own sign here (Moon rules the 2nd), brings ample "
               "wealth and family comfort; its aspect on the 8th brings "
               "some daily hardship and loss around inheritance, though "
               "the native remains prosperous and well-regarded despite "
               "the mental strain",
            3: "Friend's sign brings growing courage and sibling "
               "comfort; its aspect on the 9th brings obstacles to "
               "fortune and a weaker religious inclination, though "
               "wealth, respect and fame still follow",
            4: "Friend's sign brings some deficiency in mother's "
               "comfort, though ample comfort through property, home "
               "and family; its aspect on the 10th brings good standing "
               "through father and career",
            5: "Brings some obstacle around children, though real "
               "success in education and intellect; its aspect on the "
               "11th brings good income and a clever, well-regarded nature",
            6: "Friend's sign brings wealth earned through hard effort "
               "with some risk from rivals; its aspect on the 12th "
               "raises expenses offset by gain through distant "
               "connections, though the native isn't naturally skilled "
               "at earning",
            7: "Friend's sign brings some obstacles around a partner "
               "that ease with time, bringing growing prosperity after "
               "marriage and real comfort in business and pleasure; its "
               "aspect on the Lagna adds a handsome build and respect",
            8: "Enemy's sign brings trouble around longevity and "
               "inheritance, and disruption to wealth and family "
               "comfort, with ongoing daily unease; its aspect on the "
               "2nd still brings continued gain through wealth and "
               "family, achieved through real effort",
            9: "Enemy's sign grows wealth through religious observance, "
               "with some dissatisfaction in fortune; its aspect on the "
               "3rd brings sibling comfort and growing courage",
            10: "Friend's sign brings real cooperation, comfort, wealth "
                "and respect through father and career, and advancement "
                "in business; its aspect on the 4th brings comfort "
                "through mother, home and property, tempered by some "
                "slowness in growing wealth",
            11: "Friend's sign brings good gain through wealth and "
                "family comfort; its aspect on the 5th brings success "
                "in education and gain through children, rounding out a "
                "learned, prosperous and well-regarded nature",
            12: "Exalted here — brings heavy expense offset by gain "
                "through distant connections, though some diminishment "
                "in family strength; its aspect on the 6th brings "
                "influence over rivals only after yielding ground, with "
                "some inner unrest from illness or dispute",
        },
        "Mars": {
            1: "Friend's sign brings real gain through physical effort "
               "and victory over rivals; its aspects bring ordinary "
               "comfort through mother and home, some distress for a "
               "spouse eased through effort, and growing longevity and inheritance",
            2: "Debilitated here — brings loss around wealth and family, "
               "and harm from rivals including losses at gambling; its "
               "aspects bring some deficiency around children (offset "
               "partly through secretive method), growing longevity and "
               "inheritance, and little natural interest in religious practice",
            3: "Friend's sign brings some difficulty around siblings "
               "alongside growing courage; its aspects bring victory "
               "over rivals, and growing fortune and respect through "
               "father and career",
            4: "Friend's sign brings some strain around the mother, "
               "home and family comfort; its aspects bring some "
               "ordinary trouble around a partner and business, and "
               "good income through effort",
            5: "Brings some tension around honour and respect though "
               "gain still arrives, and its aspects bring education "
               "through effort, growing longevity, and good income "
               "through secretive method and effort",
            6: "In its own sign here (Mars rules the 6th), brings real "
               "victory over rivals despite some difficulty around a "
               "partner; its aspects grow religion and fortune, "
               "alongside heavy expense with modest gain from distant "
               "connections",
            7: "Friend's sign brings mixed difficulty and success "
               "around business and a partner; its aspects bring some "
               "benefit through father and career, physical strength, "
               "and a tendency toward blood-related disorders",
            8: "Friend's sign brings gain through longevity and "
               "inheritance, often forcing life abroad, though wealth "
               "still arrives from foreign connections; its aspects "
               "bring worry over money and family, and diminished "
               "sibling comfort",
            9: "Friend's sign brings gain through a partner and "
               "advancement in career through fortune, alongside "
               "genuine devotion; its aspects bring heavy expense offset "
               "by distant gains, and some diminished courage and home comfort",
            10: "Friend's sign brings some trouble with father or "
                "career alongside gain from distant connections; its "
                "aspects bring some physical weakness, reduced home "
                "comfort, and friction around children softened by "
                "modest gain through friendship",
            11: "In its own sign here (Mars rules the 11th), brings "
                "real growth in income; its aspects bring some obstacle "
                "to saving despite steady effort, mixed success in "
                "education and children, and growing influence over rivals",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections; its aspects bring growing "
                "courage at some cost to sibling comfort, mixed loss "
                "and gain with rivals, and some trouble for a spouse",
        },
        "Mercury": {
            1: "In its own sign and as Lagna-lord here, brings real "
               "physical beauty and health, and ample comfort through "
               "mother, home and property; its aspect on the 7th brings "
               "particular comfort and success in business",
            2: "Enemy's sign still brings wealth and family comfort "
               "with some deficiency in personal or maternal comfort, "
               "and ample comfort through property and home; its aspect "
               "on the 8th grows longevity and gains through inheritance",
            3: "Friend's sign brings sibling comfort and growing "
               "courage, and comfort through mother and home; its "
               "aspect on the 9th brings advancement in fortune and "
               "religion through the native's own effort, and a "
               "naturally gracious character",
            4: "In its own sign here (Mercury rules the 4th), brings "
               "ample comfort through mother, home and property, and "
               "good looks and leisure; its aspect on the 10th brings "
               "some carelessness around father, career and business",
            5: "Friend's sign brings real gains in education and with "
               "children, and a grave, clever, self-assured nature; its "
               "aspect on the 11th brings good income through wit, and "
               "a peace-loving disposition",
            6: "Friend's sign brings success over rivals through "
               "discernment and diligence, with some deficiency in home "
               "comfort and appearance; its aspect on the 12th raises "
               "expense offset by comfort through distant connections, "
               "alongside some trouble from disputes",
            7: "Friend's sign brings success through a partner, in "
               "daily life and in business, with some deficiency around "
               "the mother offset by ample comfort through property and "
               "home; its aspect on the Lagna brings physical beauty, "
               "cleverness and honour",
            8: "Friend's sign brings gains through longevity and "
               "inheritance, though at some cost to home comfort, "
               "physical beauty and health, often forcing life abroad; "
               "its aspect on the 2nd still grows wealth and family through effort",
            9: "Friend's sign advances fortune and career through "
               "physical effort and discernment, and brings comfort "
               "through mother, home and property; its aspect on the "
               "3rd grows courage and sibling comfort, with some "
               "deficiency in education",
            10: "Debilitated here — brings real hardship, forcing hard "
                "physical effort for advancement, with limited comfort "
                "through father and limited success in career; its "
                "aspect on the Lagna improves health and comfort, "
                "though the native alternates between respect and disgrace",
            11: "Friend's sign brings real gains through discernment "
                "and physical effort, and comfort through mother, home "
                "and property; its aspect on the 5th brings success in "
                "education and gain through children",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, with some deficiency in "
                "home comfort; its aspect on the 6th brings influence "
                "over rivals through cleverness, though some inner "
                "unease persists",
        },
        "Jupiter": {
            1: "Friend's sign brings comfort, physical beauty, "
               "self-respect and morale; gain also arrives through "
               "father and career, though the native meets some "
               "obstacle around children despite success in education, "
               "some difference with a partner, and some deficiency in "
               "fortune and religious practice",
            2: "Exalted here — brings real growth in wealth and family; "
               "its aspects bring influence over rivals, some "
               "deficiency in longevity gains, and — through its "
               "own-sign aspect on the 10th — real cooperation and "
               "success through father and career",
            3: "Friend's sign brings growing courage and sibling "
               "comfort; its aspects bring comfort and success through "
               "business and career, and some dissatisfaction to "
               "fortune offset by growing income",
            4: "Friend's sign brings ample comfort through mother, home "
               "and family; its aspects bring some unrest around "
               "longevity, real cooperation and fame through father and "
               "career, and gain from distant connections at higher expense",
            5: "Enemy's sign brings real success in education despite "
               "some weakness in courage; its aspects bring some "
               "difficulty to fortune, good income, and — through its "
               "aspect on the Lagna — good looks, self-respect and "
               "personal strength",
            6: "Friend's sign brings success over rivals despite some "
               "difference with a partner; its aspects grow fortune and "
               "career, and bring gain from distant connections at "
               "higher expense",
            7: "In its own sign here (Jupiter rules the 7th), brings "
               "ample success through business and partnership, and "
               "cooperation and respect through father and career; its "
               "aspects bring very good income, good looks, and growing "
               "courage and sibling comfort",
            8: "Enemy's sign brings difficulty around longevity and "
               "inheritance, and some difficulty through father, "
               "career, business and a partner; its aspects bring some "
               "deceptive foreign dealings, modest gain through effort, "
               "and ordinary comfort through mother and home",
            9: "Enemy's sign advances fortune and religion despite some "
               "difficulty and some dissatisfaction with father, career "
               "and a partner; its aspects bring good looks, growing "
               "courage and sibling comfort, and success in education "
               "despite some difference over children",
            10: "In its own sign here (Jupiter rules both the 7th and "
                "10th), brings real cooperation, comfort and respect "
                "through father and career, and success in business; "
                "its aspects bring good growth in savings, ample home "
                "comfort, and influence over rivals — a life of real "
                "comfort all round",
            11: "Friend's sign brings real gain through father, career "
                "and business; its aspects grow courage and sibling "
                "comfort, and bring success in education alongside "
                "ample gain and comfort through a partner and business",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, alongside some loss "
                "through a partner and business; its aspects bring "
                "comfort through mother and home, success over rivals, "
                "and some difficulty around longevity",
        },
        "Venus": {
            1: "Friend's sign brings a modest build though real skill "
               "in education and cleverness, and free spending offset "
               "by gain through distant connections; its aspect on the "
               "7th brings some friction with a spouse alongside real "
               "success in daily affairs and business through cleverness",
            2: "Enemy's sign still gains wealth and standing through "
               "wit, though savings run thin; its aspect on the 8th "
               "brings gain through longevity and inheritance, "
               "alongside good relations with distant places and real "
               "success in education, despite some deficiency around children",
            3: "Enemy's sign brings some deficiency in courage, sibling "
               "comfort, education and children, offset by real "
               "strength through wit; its aspect on the 9th brings "
               "dedicated effort toward fortune and religion, and skill "
               "in managing expenses",
            4: "Debilitated here — brings some deficiency in comfort "
               "through mother, home and children; its aspect on the "
               "10th brings comfort, respect and cooperation through "
               "father and career, and standing gained through quiet cleverness",
            5: "In its own sign here (Venus rules both the 5th and "
               "12th), brings some flawed but real success in education "
               "and with children, and gain through distant connections "
               "via cleverness; its aspect on the 11th brings good gain "
               "through wit, though expenses tend to run ahead of income",
            6: "Success over rivals here comes through secretive "
               "cleverness and spending power, though some difficulty "
               "in education continues; its aspect on the 12th brings "
               "expenses running ahead of income, and heavy entanglement "
               "in disputes and litigation",
            7: "Brings an intelligent, clever spouse alongside real "
               "distress and worry through a partner, and daily "
               "expenses that demand real wit to manage; its aspect on "
               "the Lagna brings a frail build though growing respect, "
               "and real success in education, children and distant connections",
            8: "Friend's sign brings growing strength through longevity "
               "and inheritance and a diplomat's temperament forged "
               "through hard effort, despite some difficulty around "
               "education and children; its aspect on the 2nd raises "
               "the need for real effort to grow wealth (Venus rules "
               "the 12th here)",
            9: "Friend's sign advances fortune and religion despite "
               "some difficulty, and brings comfort through education "
               "and children; its aspect on the 3rd brings some "
               "estrangement from siblings alongside some loss to courage",
            10: "Exalted here — brings real loss through father and "
                "career (Venus rules the 12th here) despite gain "
                "through distant connections, alongside real standing "
                "and comfort through father, career, education and "
                "children; its aspect on the 4th brings some deficiency "
                "in home comfort",
            11: "Friend's sign brings good gain through cleverness "
                "(Venus rules the 5th here), extending to gain through "
                "a partner too; its own-sign aspect on the 5th brings "
                "similarly clever success in education and with children",
            12: "In its own sign here (Venus rules the 12th), brings "
                "heavy expense offset by standing gained through "
                "distant connections, at some cost to health and some "
                "difficulty around a partner and career; its aspect on "
                "the 6th brings some loss through rivals despite a real "
                "cleverness at earning",
        },
        "Saturn": {
            1: "Friend's sign brings some deficiency in physical beauty "
               "alongside growing longevity and inheritance; its "
               "aspects bring friction with siblings, some difficulty "
               "around a partner and business, and some friction with "
               "father and career",
            2: "Enemy's sign brings loss in savings and family comfort, "
               "and some difficulty through mother and home; its "
               "aspects bring growing longevity alongside some obstacle "
               "to income — regarded by others as fortunate, though "
               "also self-interested",
            3: "Enemy's sign brings some difficulty around siblings "
               "alongside growing longevity; its aspects bring success "
               "in education and children, and advancement in fortune "
               "despite some difficulty and higher expense abroad",
            4: "Friend's sign brings ordinary comfort through mother "
               "alongside real strength through longevity and religious "
               "observance; its aspects bring influence and gain "
               "through rivals, and some friction with father and career",
            5: "Brings success in education and children despite some "
               "difficulty; its aspects bring some difficulty around a "
               "partner and business, some loss in income, and some "
               "obstacle to wealth and family comfort",
            6: "Friend's sign brings success and victory over rivals "
               "and in disputes; its aspects bring growing longevity, "
               "gain through distant connections at higher expense, and "
               "some difficulty around siblings",
            7: "Friend's sign brings mixed comfort and distress through "
               "a partner and business; its aspects bring growing "
               "longevity, advancement in fortune, some deficiency in "
               "physical strength, and comfort through mother and home",
            8: "In its own sign here (Saturn rules the 8th), brings "
               "growing longevity, though some difficulty to fortune "
               "and respect; its aspects bring some difficulty through "
               "father and career, some loss in savings, and success in "
               "education despite some difficulty",
            9: "In its own sign here (Saturn rules the 9th), advances "
               "fortune despite some shortfall, and brings growing "
               "longevity and respect; its aspects bring some "
               "difficulty around income and siblings, alongside "
               "victory over the troubles rivals bring",
            10: "Friend's sign brings some deficiency in comfort "
                "through father alongside real success in career and "
                "business; its aspects bring gain through distant "
                "connections at higher expense, comfort through mother "
                "and home, and some difficulty around a partner and business",
            11: "Enemy's sign brings some obstacle to income and "
                "shortfall in fortune, tempting the native toward some "
                "improper means of earning; its aspects bring some "
                "physical discomfort though the native is considered "
                "fortunate, success in education and children, and "
                "growing longevity",
            12: "Friend's sign brings gain through distant connections "
                "at higher expense; its aspects bring some obstacle to "
                "wealth and family comfort, hard-won victory over "
                "rivals, and advancement in fortune and religious "
                "observance — a life carrying both fame and disrepute, "
                "joy and sorrow, though ultimately regarded as fortunate",
        },
        "Rahu": {
            1: "Exalted here — brings an impressive stature, "
               "discernment and self-interest, and real skill in "
               "secretive method and real courage; the native advances "
               "through arduous undertakings and secretive method, "
               "gaining wealth and respect",
            2: "Brings real loss to wealth and family comfort; "
               "secretive method and hard effort bring only ordinary "
               "success in earning, with real comfort in money arriving "
               "only much later",
            3: "Brings growing courage despite some deficiency in "
               "sibling comfort; the native pursues advancement with "
               "great courage and effort, remaining patient, bold and "
               "skilled in secretive method, though occasionally "
               "meeting serious crises",
            4: "Brings deficiency and dissatisfaction through mother, "
               "home and family comfort; the native seeks comfort "
               "through secretive method",
            5: "Brings success in education and intellect only after "
               "considerable difficulty, with children remaining a "
               "source of distress; the native is knowledgeable in "
               "secretive method, clever, untruthful, impressive, and "
               "beset by many worries",
            6: "Brings real dominance and influence over rivals; the "
               "native conceals weaknesses and is bold, patient, clever "
               "and skilled in secretive method",
            7: "Brings real distress to a spouse and real difficulty in "
               "business, along with some disorder of the reproductive "
               "organs; the native pursues self-interest through "
               "secretive method and untruth without hesitation",
            8: "Brings many crises around longevity and inheritance and "
               "some disorder in the lower abdomen; the native strives "
               "for success through hard effort and secretive method, "
               "keeping difficulties private",
            9: "Brings real difficulty to fortune's advance; the native "
               "grows fortune through effort and secretive method, "
               "though never achieves full comfort and respect, with "
               "only late and partial success in religious observance",
            10: "Brings difficulty with father, career and business, "
                "with only modest success after considerable hard "
                "effort and repeated crises",
            11: "Brings growing income through secretive method and "
                "hard effort, despite occasional severe crises, with "
                "eventual real success; the native, though content with "
                "modest gains, keeps devising new plans for more",
            12: "Brings heavy expense, occasionally leading to real "
                "difficulty, offset by gain through distant connections; "
                "the native manages expenses through secretive method, "
                "effort and cleverness, and appears impressive to others",
        },
        "Ketu": {
            1: "Brings some deficiency in physical beauty; the native "
               "is beset by hidden worries, illness and injury, and "
               "pursues self-interest through secretive method and "
               "physical effort, remaining discerning though not "
               "especially self-assured",
            2: "Brings persistent worry over wealth and family; the "
               "native sometimes suffers greatly from an inability to "
               "save, and faces mental distress over family matters, "
               "gaining only partial relief through patience, courage "
               "and secretive method",
            3: "Brings real growth in courage alongside diminished "
               "sibling comfort, with the native's own courage becoming "
               "a source of trouble; bold, arrogant, boastful and daring",
            4: "Brings success in securing domestic comfort through "
               "real cleverness, with some deficiency in property "
               "comfort; eventual comfort arrives through hidden "
               "courage and patience",
            5: "Brings difficulty in education, and only ordinary "
               "success with children after difficulty; the native "
               "succeeds in learning and other fields through hidden "
               "patience, cleverness and courage",
            6: "Brings the ability to subdue rivals through secretive "
               "method, and success in disputes and litigation; the "
               "native is skilled at concealing inner weakness and "
               "impresses others through sheer boldness",
            7: "Brings real success after some difficulty around a "
               "partner and business, along with a life of real sensory "
               "indulgence; the native achieves considerable "
               "advancement through hard effort and secretive method",
            8: "Brings loss around inheritance and repeated crises "
               "concerning longevity; the native does not abandon "
               "their principles even in crisis, through boldness and "
               "courage, and may suffer some digestive ailment",
            9: "Brings some obstacles to fortune's advance, offset by "
               "modest success through effort; the native cannot fully "
               "keep to religious observance, but gains modest success "
               "in every field through secretive method and hard effort",
            10: "Brings many difficulties through father, career and "
                "business, with real damage to standing and respect at "
                "times; only ordinary success follows secretive method "
                "and hard effort",
            11: "Brings hard effort in the pursuit of income, with "
                "occasional severe crises; the native eventually wins "
                "through patience, courage and effort, achieving modest "
                "success in earning",
            12: "Brings heavy expense, sometimes leading to real "
                "difficulty, alongside some trouble through distant "
                "connections; the native manages expenses through "
                "boldness, secretive method, effort and cleverness",
        },
    },
    # CANCER (Karka) LAGNA — complete, all 108 entries, no documented gap.
    "Cancer": {
        "Sun": {
            1: "Friend's sign brings growing physical beauty, vigour and "
               "influence, plus wealth and family strength; its aspect "
               "on the 7th brings some difficulty in business and partnership",
            2: "In its own sign here (Sun rules the 2nd), brings growing "
               "wealth, family standing and fame; its aspect on the 8th "
               "reduces longevity and brings some daily hardship around "
               "inheritance",
            3: "Friend's sign brings growing courage and some flawed "
               "but real sibling comfort, and wealth growing through "
               "personal drive; its aspect on the 9th brings "
               "advancement in fortune and religious observance, and "
               "growing standing and respect",
            4: "Debilitated here — brings some deficiency in home "
               "comfort and wealth; its aspect on the 10th (exalted) "
               "brings real success, fame and gain through father, "
               "career and business",
            5: "Friend's sign brings some obstacle around children, "
               "though one child proves especially capable; real "
               "success in education and intellect, and growing wealth; "
               "its aspect on the 11th brings good income, though the "
               "native is blunt and hot-tempered",
            6: "Friend's sign brings real influence over rivals, though "
               "some deficiency in wealth and family comfort; its "
               "aspect on the 12th brings gain from distant connections "
               "at higher expense, with the native placing reputation "
               "above money",
            7: "Enemy's sign brings real distress through a spouse and "
               "business, some reproductive-organ complaint and family "
               "difficulty; its aspect on the Lagna brings "
               "respectability alongside a persistent physical strain",
            8: "Enemy's sign brings occasional crises around longevity, "
               "with some loss in inheritance gains; its aspect on the "
               "2nd (own sign) brings some deficiency in wealth and "
               "family comfort, and possible leg trouble — a wealthy "
               "lifestyle nonetheless",
            9: "Friend's sign brings strong fortune, devotion and "
               "standing; its aspect on the 3rd grows courage and "
               "sibling comfort",
            10: "Exalted here — brings real cooperation, standing and "
                "gain through father, career and business; its aspect "
                "on the 4th brings some deficiency in home comfort",
            11: "Enemy's sign brings real gain in wealth, though some "
                "deficiency in family comfort; its aspect on the 5th "
                "brings success in education and gain through children",
            12: "Friend's sign brings good gain through distant "
                "connections at higher expense, and an indulgent "
                "lifestyle, with some deficiency in wealth and family "
                "comfort; its aspect on the 6th brings victory over rivals",
        },
        "Moon": {
            1: "In its own sign and as Lagna-lord here, brings real "
               "beauty, health, strength, fame and standing, and a "
               "genuinely thoughtful, fortunate character; its aspect "
               "on the 7th brings some dissatisfaction around a partner "
               "despite real success in business",
            2: "Friend's sign brings good wealth and family comfort "
               "through some difficulty; its aspect on the 8th brings "
               "some crisis around longevity and reduced gains through "
               "inheritance — a life of real standing and fortune nonetheless",
            3: "Friend's sign brings real growth in courage and sibling "
               "comfort; its aspect on the 9th brings ample advancement "
               "in fortune and religion, rounding out a righteous, "
               "generous, devout and enthusiastic nature",
            4: "Brings ample comfort through mother, home and property, "
               "a handsome build and gentle mind; its aspect on the "
               "10th brings success, cooperation and fame through "
               "father, career and business",
            5: "Debilitated here — success in education and children "
               "comes only with difficulty, and some weakness of body "
               "and mind follows; its aspect on the 11th brings good "
               "income through hidden mental and physical resources, "
               "though some unease persists",
            6: "Friend's sign brings some weakness against rivals, "
               "though real success through humility; its aspect on "
               "the 12th brings honour, respect and wealth through "
               "distant connections at higher expense — a dignified, "
               "self-possessed nature",
            7: "Enemy's sign brings some dissatisfaction around a "
               "spouse though real success follows, alongside "
               "difficulty in business and a strong taste for sensory "
               "pleasure; its aspect on the Lagna brings real inner strength",
            8: "Enemy's sign brings some deficiency in physical beauty "
               "and unsatisfying gains through inheritance, though "
               "growing longevity; its aspect on the 2nd brings gain "
               "through the native's own effort",
            9: "Friend's sign brings real strength of mind and body "
               "that advances fortune, and genuine religious devotion; "
               "its aspect on the 3rd grows courage and sibling comfort, "
               "rounding out a fortunate, righteous and gracious nature",
            10: "Friend's sign brings real standing, fame and gain "
                "through father, career and business, often rising to "
                "high office; its aspect on the 4th brings comfort "
                "through land and home too",
            11: "Exalted here — brings real growth in physical and "
                "mental strength and beauty, and good income; its "
                "aspect on the 5th brings some deficiency in education "
                "and children, and a tendency toward sharp words for "
                "personal gain",
            12: "Friend's sign brings gain through distant connections "
                "at higher expense; its aspect on the 6th brings "
                "influence over rivals through a calm temperament, "
                "though some inner unease and a frail build persist",
        },
        "Mars": {
            1: "Friend's sign brings some deficiency in physical beauty "
               "and health, and weakness through father, career, "
               "children and education; its aspects bring comfort "
               "through mother and home, some dissatisfaction around a "
               "partner despite real success in business, and some "
               "deficiency in longevity and daily life",
            2: "Friend's sign brings good wealth and family comfort, "
               "and gain through father and career too; its aspects "
               "bring some difficulty around education and children "
               "(Mars rules the 5th here), some deficiency in "
               "longevity, and growing fortune and religious standing",
            3: "Friend's sign brings growing courage and sibling "
               "comfort, and gain through education and children too; "
               "its aspects bring good fortune through wit and growing "
               "religious standing, and advancement through career and business",
            4: "Brings comfort through mother, home and property; "
               "success through education and children, and its aspect "
               "on the 7th brings good gain through a partner and business",
            5: "In its own sign here (Mars rules the 5th), brings real "
               "success through education and children; its aspects "
               "bring some dissatisfaction around longevity and "
               "inheritance, and good gain through father, career and business",
            6: "Friend's sign brings victory over rivals and real "
               "success in education and children; its aspects grow "
               "fortune and religious standing, and bring real success "
               "through father and career (Mars rules the 10th here) too",
            7: "Exalted here — brings gain through many attractive "
               "partners despite some difference with them, real "
               "success in business, and good outcomes with education "
               "and children; its aspects bring comfort, gain and "
               "honour through father and career, some deficiency in "
               "health and beauty, and good growth in wealth with an "
               "influential voice",
            8: "Brings gain through longevity, though some loss "
               "through education, children, father and career; its "
               "aspects grow income through effort, wealth and family, "
               "and courage and sibling comfort",
            9: "Friend's sign brings real advancement in fortune, with "
               "full comfort through education, children, father, "
               "career and business; its aspects bring gain through "
               "distant connections at higher expense, growing courage "
               "and sibling comfort, and some difficulty through "
               "mother, home and property",
            10: "In its own sign here (Mars rules the 10th), brings "
                "real standing, fame and gain through father, career "
                "and business; its aspects bring some deficiency in "
                "physical beauty and home comfort, and real gain "
                "through education and children, sometimes reaching a high office",
            11: "Brings gain through father, career and business "
                "through real effort; its aspects bring gain through "
                "wealth and family, mixed success in education and "
                "children, and growing influence and victory over rivals",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections; its aspects grow courage "
                "and sibling comfort, bring victory over rivals, and "
                "some difficulty around a partner and business",
        },
        "Mercury": {
            1: "Enemy's sign brings a frail build, though growing "
               "courage and influence; gain through distant connections "
               "at higher expense; its aspect on the 7th brings some "
               "ordinary success in a partner and business",
            2: "Friend's sign brings real effort needed to grow "
               "savings (Mercury rules the 12th here), and some "
               "deficiency in sibling comfort; its aspect on the 8th "
               "brings good comfort around longevity though limited "
               "inheritance gains — a genuinely comfortable, "
               "influential daily life",
            3: "In its own sign here (Mercury rules the 3rd), brings "
               "real growth in courage, with some deficiency in sibling "
               "comfort; its aspect on the 9th brings some weakness in "
               "fortune and little natural interest in religion, and "
               "some cost to reputation",
            4: "Friend's sign brings some flawed but real success in "
               "home comfort, gain through siblings, and gain through "
               "distant connections; its aspect on the 10th brings "
               "ordinary success through father, career and business",
            5: "Friend's sign brings some flawed but real success in "
               "education and children, and a bold, intelligent "
               "nature; its aspect on the 11th brings gain through wit "
               "and distant connections",
            6: "Friend's sign brings success over rivals through "
               "humility, with some deficiency in sibling comfort and "
               "courage; its aspect on the 12th (own sign) brings heavy "
               "expense and ordinary standing with distant connections",
            7: "Friend's sign brings comfort through a partner and "
               "real success in business; its aspect on the Lagna "
               "brings a mix of strength and frailty in the body, and "
               "heavy spending offset by advancement through effort",
            8: "Friend's sign brings some flawed but real gain around "
               "longevity, with some deficiency in sibling comfort and "
               "courage; its aspect on the 2nd brings wealth gained "
               "through effort, though as 12th lord here expenses run high",
            9: "Friend's sign brings some flawed but real advancement "
               "in fortune and religion, and gain through distant "
               "connections too; its own-sign aspect on the 3rd grows "
               "personal drive despite some setback to fortune's advance",
            10: "Friend's sign brings some flawed but real success in "
                "career, family gain and sibling comfort too; its "
                "aspect on the 4th brings ordinary comfort through "
                "mother, home and property, gained through effort",
            11: "Friend's sign brings good income through effort; its "
                "aspect on the 5th brings mixed loss and gain in "
                "education and children, and good wit-driven income "
                "through voice and discernment",
            12: "In its own sign here (Mercury rules the 12th), brings "
                "heavy expense offset by gain through distant "
                "connections, with some deficiency in sibling comfort "
                "and courage; its aspect on the 6th brings ordinary "
                "success over rivals through hard-earned discretion",
        },
        "Jupiter": {
            1: "Exalted here — brings real physical beauty and "
               "personal presence; its aspects bring full comfort "
               "through education and children, some difficulty around "
               "a partner and daily expense, and — through its own-sign "
               "aspect on the 9th — a strong advance in fortune and "
               "religious standing",
            2: "Friend's sign brings real wealth and family comfort; "
               "its aspects bring victory over rivals through wealth "
               "(Jupiter rules the 6th here), good gain through "
               "longevity, and standing, wealth and success through "
               "father, career and business",
            3: "Friend's sign brings growing courage and sibling "
               "comfort; its aspects bring loss and distress around a "
               "partner and business, and — through its own-sign aspect "
               "on the 9th — advancement in fortune and religion, "
               "despite some initial difficulty",
            4: "Enemy's sign brings some flawed but real comfort "
               "through education and children, and some difficulty in "
               "home comfort though with ordinary success; its aspects "
               "bring some difference in longevity gains, real "
               "cooperation and success through father and career, and "
               "gain from distant connections at higher expense",
            5: "Friend's sign brings real success in education and "
               "children; its own-sign aspect on the 9th grows fortune, "
               "though income comes with some difficulty; its aspect on "
               "the Lagna brings good looks and personal strength",
            6: "In its own sign here (Jupiter rules the 6th), brings "
               "real influence over rivals despite some difficulty in "
               "fortune's advance; its aspects bring success through "
               "father and career, gain from distant connections at "
               "higher expense, and growth in wealth and family",
            7: "Debilitated here — brings some difficulty and hardship "
               "through a partner and business, though real success "
               "eventually follows; its aspects bring gain through "
               "effort, good looks and personal strength, and growing "
               "courage and sibling comfort",
            8: "Enemy's sign brings some difficulty around longevity "
               "and inheritance, and some difficulty through father, "
               "career, business and a partner too; its aspects bring "
               "some deceptive foreign dealings at higher expense, "
               "modest gain through effort, and ordinary comfort "
               "through mother and home",
            9: "In its own sign here (Jupiter rules both the 6th and "
               "9th), brings real advancement in fortune and religion "
               "despite some difficulty; its aspects bring good looks "
               "and personal strength, growing courage and sibling "
               "comfort, and success in education despite some "
               "difference over children",
            10: "Friend's sign brings real cooperation, standing and "
                "success through father, career and business; its "
                "aspects bring good growth in savings, ample comfort "
                "through mother, home and property, and — through its "
                "own-sign aspect on the 6th — influence over rivals",
            11: "Brings real gain through father, career and business; "
                "its aspects grow courage and sibling comfort, bring "
                "success in education alongside some difference over "
                "children, and ample gain and comfort through a partner "
                "and business",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, alongside some loss "
                "through a partner and business (Jupiter rules the 6th "
                "here); its aspects bring comfort through mother and "
                "home, success over rivals, and some difficulty around longevity",
        },
        "Venus": {
            1: "Enemy's sign still brings real comfort, beauty and "
               "cleverness, and comfort through mother and property "
               "too; its aspect on the 7th brings gain and comfort "
               "through a partner and business, with a strongly "
               "indulgent temperament",
            2: "Enemy's sign brings some ordinary dissatisfaction "
               "alongside wealth and family comfort, and comfort "
               "through property and home, with some deficiency around "
               "the mother; its aspect on the 8th brings growing "
               "longevity and gains through inheritance",
            3: "Friend's sign brings some deficiency in sibling comfort "
               "and courage, and some deficiency around the mother; its "
               "aspect on the 9th brings real advancement in fortune "
               "and religious observance, with the native concealing "
               "inner weakness behind an outwardly bold manner",
            4: "In its own sign here (Venus rules the 4th), brings "
               "ample comfort through mother, home and property, and "
               "growing wealth through intelligence; its aspect on the "
               "10th brings standing, comfort, gain and fame through "
               "father, career and business",
            5: "Brings good comfort through education and children; "
               "its own-sign aspect on the 11th brings good income and "
               "wealth, and comfort through mother and home too",
            6: "Enemy's sign brings victory over rivals, though some "
               "deficiency and unease through mother, home and "
               "property, and some dependency in gains; its aspect on "
               "the 12th brings comfort and gain through distant "
               "connections at higher expense",
            7: "Friend's sign brings real success through business and "
               "daily income; its aspect on the Lagna brings good "
               "looks, personal presence, cleverness and comfort",
            8: "Friend's sign brings gain and growth through longevity, "
               "often through advancement abroad, with some deficiency "
               "in home comfort; its aspect on the 2nd grows wealth "
               "only through real effort",
            9: "Exalted here — brings real advancement in fortune and "
               "religion, and ample comfort through mother and home; "
               "its aspect on the 3rd brings some estrangement from "
               "siblings alongside some loss to courage",
            10: "Brings real standing and comfort through father and "
                "career, and gain through distant connections; its "
                "aspect on the 4th (own sign) brings ample comfort "
                "through mother and home",
            11: "In its own sign here (Venus rules the 11th), brings "
                "real gain through wealth and effort, extending to gain "
                "through a partner too; its aspect on the 5th brings "
                "clever success in education and with children",
            12: "Friend's sign brings heavy expense offset by standing "
                "and gain through distant connections, with some "
                "deficiency in home comfort; its aspect on the 6th "
                "brings some loss through rivals despite real "
                "cleverness at earning",
        },
        "Saturn": {
            1: "Enemy's sign brings some deficiency in physical beauty "
               "and a tendency toward illness; its aspects bring "
               "imperfect but real sibling comfort, real success in "
               "business despite some difficulty with a spouse, and "
               "ordinary success and respect through father and career",
            2: "Enemy's sign brings loss around wealth and family; its "
               "aspects bring comfort through mother, home and "
               "property, growing longevity and inheritance gains, and "
               "income growth through effort — a wealthy though "
               "ordinary daily life",
            3: "Friend's sign brings growing courage despite some "
               "friction with siblings; its aspects bring some "
               "difficulty around children and education, some "
               "obstacle to fortune and religious devotion, and gain "
               "through distant connections at higher expense — a "
               "somewhat short-tempered nature",
            4: "Friend's sign brings some deficiency in comfort through "
               "the mother, offset by real comfort through property and "
               "home; its aspects bring some influence over rivals, "
               "some difficulty with father and career, and some cost "
               "to physical health at home",
            5: "Enemy's sign brings difficulty around education, "
               "intellect and children; its aspects bring an "
               "intelligent though sometimes troublesome spouse, real "
               "success in business through discernment, good income, "
               "and some loss in savings and family comfort",
            6: "Enemy's sign still brings real influence over rivals, "
               "though only after some difficulty with a partner and "
               "business; its aspects bring growing longevity, gain "
               "through distant connections at higher expense, and "
               "some difficulty around siblings",
            7: "In its own sign here (Saturn rules the 7th), brings "
               "real success through business, daily income and "
               "sensory comfort; its aspects bring some difficulty to "
               "fortune's advance, some deficiency in physical beauty "
               "and health, and ample comfort through mother and home",
            8: "In its own sign here (Saturn rules the 8th), brings "
               "growing longevity despite ongoing difficulty in "
               "business; its aspects bring some difficulty through "
               "father and career, some loss in savings and family "
               "comfort, and some difficulty in education and with children",
            9: "Enemy's sign brings some difficulty to religious "
               "observance and fortune's advance, though growing "
               "longevity and modest gains through inheritance; its "
               "aspects bring growing income, some difference with "
               "siblings alongside growing courage, and eventual "
               "influence over rivals",
            10: "Debilitated here — brings difficulty through father, "
                "career and business, and some loss in longevity and "
                "inheritance gains; its aspects bring higher expense "
                "offset by gain abroad, comfort through mother and "
                "home, and success through a partner and daily business",
            11: "Friend's sign brings good income and success through "
                "a partner and business; its aspects bring some "
                "deficiency in physical beauty, some difficulty in "
                "education and with children, and real growth in longevity",
            12: "Friend's sign brings gain through distant connections "
                "at higher expense, alongside some loss to comfort "
                "through a partner, business, longevity and "
                "inheritance; its aspects bring some worry over wealth "
                "and family, hard-won influence over rivals, and some "
                "difficulty to religious observance and fortune's "
                "advance — a life of real comfort despite these difficulties",
        },
        "Rahu": {
            1: "Brings some deficiency in physical beauty and an "
               "anxious heart, with occasional severe suffering; "
               "secretive method preserves the native's honour amid "
               "hard effort toward advancement",
            2: "Brings loss in wealth and family comfort; secretive "
               "method and hard effort drive wealth growth, with "
               "occasional sudden gains and constant worry over "
               "protecting reputation — bold and hard-working throughout",
            3: "Brings real growth in courage despite some difficulty "
               "with siblings; the native pursues self-interest through "
               "hard effort, secretive method and sheer manliness, "
               "outwardly bold despite inner weakness",
            4: "Brings some deficiency in mother's comfort and limited "
               "comfort through land and home, often forcing life "
               "abroad, with occasional setbacks",
            5: "Brings difficulty in education and distress through "
               "children, though their happiness arrives eventually; "
               "the native impresses even the learned despite limited "
               "formal education, and is stubborn and versed in law",
            6: "Brings difficulties from rivals overcome through "
               "statecraft and diplomacy; clever, self-interested, and "
               "indifferent to right and wrong",
            7: "Brings difficulty and hardship around a partner and "
               "business, along with a reproductive-organ complaint and "
               "occasional domestic hardship, resolved eventually into "
               "real success",
            8: "Brings occasional anxiety over longevity and loss in "
               "inheritance-related matters, along with a digestive "
               "complaint; the native relies on many secretive "
               "strategies for a livelihood",
            9: "Brings difficulty to fortune's advance and imperfect "
               "religious observance, with occasional severe crises; "
               "some success arrives through secretive method and effort",
            10: "Brings difficulty through father, career and business; "
                "after considerable suffering and repeated "
                "disappointment, some advancement and standing are "
                "preserved through effort, patience and boldness",
            11: "Brings good wealth gained through great cleverness, "
                "alongside occasional ordinary hardship and crises, and "
                "occasional sudden windfalls",
            12: "Brings gain through distant connections via secretive "
                "method, at higher expense; the native achieves "
                "particular respect and fame abroad, concealing "
                "weaknesses and advancing through cleverness and intelligence",
        },
        "Ketu": {
            1: "Brings a deep scar or mark on the body, some deficiency "
               "in beauty and health, and possibly smallpox, with "
               "occasional severe suffering",
            2: "Brings real loss to wealth and major crises from the "
               "same, along with family distress; the native sustains "
               "life through debt, protecting standing through effort "
               "and secretive method",
            3: "Brings growing courage achieved through secretive "
               "method, discernment and hard effort, alongside a "
               "reckless, hot-tempered nature and some diminished "
               "sibling comfort",
            4: "Brings some deficiency in mother's comfort, often "
               "forcing life abroad with repeated relocation and "
               "occasional severe crises, before eventual ordinary comfort",
            5: "Brings distress through children and difficulty in "
               "education; the native is clever, glib and impressive "
               "despite this, concealing his own limitations to "
               "influence others, though not especially content or "
               "well-mannered",
            6: "Brings real success against rivals and the courage to "
               "hold ground even in difficulty; healthy, bold and "
               "hard-working, though lacking in compassion and gentleness",
            7: "Brings difficulty and loss around a partner and "
               "business, a reproductive-organ complaint, and a strong "
               "sensory appetite; stubborn, willful and hard-working",
            8: "Brings repeated severe crises around longevity and loss "
               "in inheritance-related matters, along with a stomach "
               "ailment and hidden financial anxiety; the native "
               "strives continuously for advancement and comfort",
            9: "Brings a need for hard effort toward fortune's advance, "
               "with occasional severe setbacks; the native advances "
               "quietly, though fortune improves only very slowly",
            10: "Brings difficulty through career, father and business, "
                "with some damage to reputation and standing; the "
                "native strives to regain standing through secretive "
                "method and effort",
            11: "Brings hard effort for financial gain, with growing "
                "gains through effort, cleverness and secretive method "
                "despite repeated crises; the native never loses heart "
                "nor avoids effort",
            12: "Brings real difficulty managing expenses, and trouble "
                "through foreign connections too; the native relies on "
                "secretive method and hard work, suffering inwardly "
                "despite an outwardly steady front",
        },
    },
    # LEO (Simha) LAGNA — complete, all 108 entries, no documented gap.
    "Leo": {
        "Sun": {
            1: "In its own sign and as Lagna-lord here, brings real "
               "physical strength, confidence and beauty, a bold and "
               "tall bearing; its aspect on the 7th brings some "
               "difficulty and dissatisfaction in business and with a partner",
            2: "Friend's sign brings growing wealth and family comfort, "
               "though with some loss of independence; its aspect on "
               "the 8th brings longevity and inheritance gains, and "
               "real standing in society",
            3: "Debilitated here — brings friction with siblings and "
               "some diminished drive, though the native remains bold; "
               "its aspect on the 9th brings advancement in fortune and "
               "real religious devotion",
            4: "Friend's sign brings comfort through mother, home and "
               "property, and general physical wellbeing; its aspect "
               "on the 10th brings friction with the father, and "
               "success in career and business only through real effort",
            5: "Friend's sign brings real success in education, "
               "intellect and children, and a sharp, self-aware mind; "
               "its aspect on the 11th brings good income through wit, "
               "alongside a somewhat egotistic nature",
            6: "Enemy's sign brings victory over rivals, undaunted by "
               "hardship, though some deficiency in physical beauty and "
               "some illness and loss of independence; its aspect on "
               "the 12th brings heavy expense offset by gain through "
               "distant connections",
            7: "Enemy's sign brings friction with a spouse, and real "
               "success in business only after difficulty; its aspect "
               "on the Lagna brings growing physical strength, "
               "self-respect and spreading fame",
            8: "Friend's sign brings some difficulty though real gains "
               "in longevity and inheritance, and strength through "
               "distant connections; its aspect on the 2nd brings "
               "wealth and family comfort through hard effort, and a "
               "short-tempered nature",
            9: "Exalted here — strengthens fortune and deepens "
               "religious inclination; its aspect on the 3rd brings "
               "dissatisfaction with siblings and carelessness about "
               "personal drive, in an otherwise heavyset, fortunate and "
               "devout nature",
            10: "Enemy's sign brings friction with the father, though "
                "real advancement, honour and standing in career and "
                "business; its aspect on the 4th brings ample comfort "
                "through mother, home and property",
            11: "Friend's sign brings good income and growing physical "
                "vigour; its aspect on the 5th brings real comfort "
                "through education and children, and a somewhat "
                "sharp-tongued, self-interested nature",
            12: "Friend's sign brings a frail build, though gain "
                "through distant connections and a love of travel; its "
                "aspect on the 6th brings real influence over rivals "
                "and victory over difficulties despite some hardship",
        },
        "Moon": {
            1: "Friend's sign brings a frail build, a love of travel "
               "and a somewhat anxious disposition; its aspect on the "
               "7th brings some difficulty and loss in business and "
               "with a partner",
            2: "Friend's sign brings modest loss in wealth despite a "
               "lavish lifestyle, and some dissatisfaction with family, "
               "though gain from distant connections; its aspect on "
               "the 8th brings growing longevity and some inheritance gains",
            3: "Brings some deficiency in sibling comfort and personal "
               "drive, though gain from distant connections; its "
               "aspect on the 9th brings advancement in fortune and "
               "religion and comfortable finances — regarded by others "
               "as prosperous and content",
            4: "Friend's sign brings some hardship in comfort through "
               "mother, home and property, and domestic financial "
               "strain; its aspect on the 10th (exalted) brings real "
               "cooperation, comfort and success through father, "
               "career and business",
            5: "Friend's sign brings obstacles in education and with "
               "children, and mental strain over expenses; its aspect "
               "on the 11th brings good income through wit, alongside "
               "some dissatisfaction",
            6: "Enemy's sign brings heavy expense from disputes with "
               "rivals and illness, weighing on the mind; its own-sign "
               "aspect on the 12th brings gain through distant "
               "connections at higher expense — victory over rivals "
               "achieved through spending",
            7: "Enemy's sign brings loss around a partner and business, "
               "and difficulty managing household expenses, offset by "
               "gain from distant connections; its aspect on the Lagna "
               "brings a frail build",
            8: "Friend's sign brings loss and worry around longevity "
               "and inheritance, and a stomach ailment, though gain "
               "from distant connections; its aspect on the 2nd brings "
               "some loss in wealth and modest family comfort",
            9: "Friend's sign brings advancement in fortune, though "
               "some laxity in religious practice; its aspect on the "
               "3rd brings some diminished sibling comfort and mental frailty",
            10: "Exalted here — brings heavy spending on ancestral "
                "property, though some flawed but real success in "
                "career and business; its aspect on the 4th brings some "
                "deficiency in home comfort, with expense-driven unrest",
            11: "Friend's sign brings gain from distant connections "
                "offset by heavy expense; its aspect on the 5th brings "
                "some deficiency in education and children, though the "
                "native is outwardly regarded as prosperous",
            12: "In its own sign here (Moon rules the 12th), brings "
                "heavy expense offset by fame and comfort through "
                "distant connections; its aspect on the 6th brings "
                "influence and victory over rivals through willpower "
                "and spending, though disputes and litigation prove costly",
        },
        "Mars": {
            1: "Friend's sign brings an impressive, magnetic "
               "personality, fortunate and devout; its aspects bring "
               "comfort through mother and home, some difficulty "
               "around a partner and business, and gain through "
               "longevity and inheritance",
            2: "Friend's sign brings good wealth and family comfort, "
               "though some deficiency through mother, home and "
               "property; its aspects bring success in education and "
               "children, growing longevity, and advancement in "
               "fortune and religion",
            3: "Enemy's sign brings real gain through siblings and "
               "personal drive; its aspects bring victory over rivals, "
               "advancement in fortune and religion, and cooperation, "
               "success and comfort through father, career and business",
            4: "In its own sign here (Mars rules the 4th), brings real "
               "comfort through mother, home and property; its aspects "
               "bring some difficulty around a partner and business "
               "despite effort, cooperation and honour through father "
               "and career, and good growth in income",
            5: "Friend's sign brings real gain through education and "
               "children; its aspects bring growing longevity and "
               "inheritance, good income, and weak, unreliable "
               "connections abroad at high expense",
            6: "Exalted here — brings real success over rivals and "
               "comfort through good fortune; its aspects bring "
               "advancement in fortune and religion, high expense "
               "abroad, and growing physical vigour, beauty and comfort",
            7: "Enemy's sign brings some flawed but real success "
               "around a partner and business; its aspects bring "
               "cooperation and success through father and career, and "
               "good growth in income",
            8: "Friend's sign brings some difficulty though real gains "
               "around longevity and inheritance; its aspects bring "
               "good growth in income, wealth and family comfort, and "
               "growing courage and sibling comfort",
            9: "In its own sign here (Mars rules the 9th), brings real "
               "advancement in fortune and religion; its aspects bring "
               "hardship from expense and unreliable foreign "
               "connections, some dissatisfaction around siblings "
               "despite growing personal drive, and real comfort "
               "through mother, home and property",
            10: "Friend's sign brings cooperation, success and standing "
                "through father, career and business; its aspects bring "
                "growing physical vigour and good fortune, comfort "
                "through mother and home, and success in education and children",
            11: "Friend's sign brings real growth in wealth and family "
                "comfort; its aspects bring success in education and "
                "children, victory over rivals and diseases alike "
                "(Mars is exalted in its aspect here), and a contented, "
                "comfortable life",
            12: "Debilitated here — brings real difficulty over "
                "expenses and unreliable foreign connections, with loss "
                "to home comfort too; its aspects bring growing sibling "
                "comfort and personal drive, victory over rivals, and "
                "comfort through a partner and business",
        },
        "Mercury": {
            1: "Friend's sign brings growing physical beauty and "
               "influence, and a discerning, generous, indulgent and "
               "wealthy nature; its aspect on the 7th brings "
               "advancement, success and comfort through business and "
               "a partner",
            2: "Exalted in its own sign here (Mercury rules the 2nd), "
               "brings real growth in wealth and family comfort, and "
               "ample sibling comfort; its aspect on the 8th brings "
               "many crises and worry around longevity, a stomach "
               "ailment, and dissatisfaction in daily life",
            3: "Friend's sign brings growing personal drive and "
               "sibling comfort; its aspect on the 9th brings "
               "advancement in fortune and genuine religious devotion "
               "— wealthy, righteous, courageous, famous and content",
            4: "Friend's sign brings ample comfort through mother, "
               "home and property, and growth in wealth; its aspect on "
               "the 10th brings comfort, honour and gain through "
               "father, career and business",
            5: "Friend's sign brings real success in education, "
               "intellect and children, alongside growing wealth; its "
               "own-sign aspect on the 11th brings very good income",
            6: "Friend's sign brings success over rivals through "
               "humility and financial strength; its aspect on the "
               "12th brings heavy expense offset by gain through "
               "distant connections, with limited family comfort",
            7: "Friend's sign brings an attractive spouse and real "
               "gain in business, wealth and family comfort too; its "
               "aspect on the Lagna brings growing physical beauty, "
               "self-respect, discernment and fame",
            8: "Friend's sign brings some difficulty around longevity "
               "and inheritance, with hardship approaching; its "
               "aspects bring real growth in longevity through effort "
               "though gains stay modest, growing personal drive and "
               "sibling comfort, and some flawed but real comfort "
               "through mother, home and property",
            9: "Friend's sign brings real advancement in fortune and "
               "success in learning; its aspects bring some "
               "dissatisfaction with siblings alongside growing "
               "personal drive, and good gain through education and children",
            10: "Friend's sign brings some loss through father, though "
                "real honour and comfort through career, and success "
                "in learning, children and longevity too; its aspects "
                "bring wealth and family comfort, ordinary comfort "
                "through mother and home, and friction with rivals "
                "despite ongoing worry",
            11: "In its own sign here (Mercury rules the 11th), brings "
                "growing income and growth in longevity, though with "
                "real effort; its aspects bring growing personal drive "
                "despite some difference with siblings, real gain in "
                "learning and family comfort, and some difficulty "
                "around a partner and daily business",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, and some difference with "
                "father and siblings; its own-sign aspect on the 6th "
                "brings real influence over rivals through discernment "
                "and hard-won victory in disputes",
        },
        "Jupiter": {
            1: "Friend's sign brings real physical beauty, personal "
               "presence and longevity; its aspects bring success in "
               "education and children, some dissatisfaction around a "
               "partner and business, and advancement in fortune, "
               "religion and gains around longevity",
            2: "Friend's sign brings real growth in wealth and family "
               "comfort, though some difficulty with children; its "
               "aspects bring loss through rivals and the maternal "
               "line, growing longevity, and some difference with "
               "father, career and business",
            3: "Friend's sign brings some difference with siblings, "
               "though growing personal drive and gain from education "
               "and children too; its aspects bring some difficulty "
               "around a partner and business, advancement in fortune "
               "and religion through wit, and good income",
            4: "Friend's sign brings some deficiency in home comfort, "
               "though gains through education and children too; its "
               "aspects bring growing longevity, and friction with "
               "father alongside dissatisfaction in career and business",
            5: "In its own sign here (Jupiter rules the 5th), brings "
               "real success in education and children; its aspects "
               "bring advancement in fortune, good income, and some "
               "dissatisfaction around a partner and business, though "
               "real comfort through the Lagna",
            6: "Debilitated here — brings some difficulty from rivals, "
               "and difficulty around education and children, worsened "
               "by expense-driven worry; its aspects bring some "
               "difficulty and success mixed with father and business, "
               "and heavy expense offset by modest gain from distant connections",
            7: "Enemy's sign brings friction with a spouse and worry "
               "in daily business, though ordinary success in "
               "education and children, and growing longevity; its "
               "aspects bring good income, growing physical beauty and "
               "personal presence, and some difference with siblings "
               "alongside growing personal drive",
            8: "In its own sign here (Jupiter rules the 8th), brings "
               "growing longevity, though some difficulty around "
               "children and education; its aspects bring heavy "
               "expense offset by gain through distant connections, "
               "real gain through wealth and family achieved through "
               "effort, and some flawed but real comfort through "
               "mother, home and property",
            9: "Friend's sign brings real advancement in fortune, and "
               "growing longevity too; its aspects bring real comfort, "
               "presence and morale, some dissatisfaction around "
               "siblings, and good gain through education and children "
               "despite some difficulty (Jupiter rules the 8th here)",
            10: "Enemy's sign brings some loss around father, though "
                "real standing through career; its aspects bring "
                "wealth and family comfort, comfort through mother and "
                "home, and some concern from rivals and health, with "
                "some difficulty in daily life",
            11: "Friend's sign brings growing income and longevity "
                "too; its aspects bring some difference with siblings "
                "alongside growing personal drive, good gain through "
                "education and children, and some difficulty around a "
                "partner and daily business",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, and real growth in "
                "education and children too; its aspects bring comfort "
                "through mother, home and property, some difficulty "
                "from rivals, and some growth in longevity",
        },
        "Venus": {
            1: "Enemy's sign brings real beauty, elegance and fame, "
               "though some friction with siblings and father; its "
               "aspect on the 7th (own sign) brings real success "
               "around a partner and daily business",
            2: "Debilitated here — brings some deficiency in wealth "
               "and family comfort, and some difference with father, "
               "career and personal drive; its aspect on the 8th "
               "(exalted) brings growing longevity and inheritance "
               "gains, though an indulgent lifestyle nonetheless",
            3: "In its own sign here (Venus rules the 3rd), brings "
               "real growth in personal drive and sibling comfort, and "
               "gain through father and career too; its aspect on the "
               "9th brings advancement in fortune through the native's "
               "own effort — clever, capable and hard-working",
            4: "Brings some ordinary difference with the mother, "
               "though gain through land and property; its aspect on "
               "the 10th (own sign) brings real gain, success and fame "
               "through father, career and business",
            5: "Brings real success in education and children; its "
               "aspect on the 11th brings good income through the "
               "native's own capability, and self-respect through learning",
            6: "Friend's sign brings real influence over rivals, and "
               "comfort through good fortune; its aspect on the 12th "
               "brings heavy expense offset by gain through distant "
               "connections, achieved through secretive method",
            7: "Friend's sign brings real success around a partner and "
               "business, comfort through siblings and father too, and "
               "real skill running a household and gaining fame; its "
               "aspect on the Lagna brings growing physical strength, "
               "presence, morale and courage — commanding and authoritative",
            8: "Exalted here — brings growing longevity and "
               "inheritance gains, and some flawed but real comfort "
               "through siblings and father, with real influence in "
               "daily affairs and success in career too; its aspect on "
               "the 2nd brings some deficiency in wealth and family comfort",
            9: "Brings real success, comfort and honour through "
               "father, career and business; its aspect on the 3rd "
               "(own sign) brings real growth in sibling comfort and "
               "personal drive",
            10: "In its own sign here (Venus rules the 10th), brings "
                "real success, comfort, fame and gain through father, "
                "career and business, and ample sibling comfort too; "
                "its aspect on the 4th brings comfort through mother, "
                "home and property",
            11: "Friend's sign brings growing income, and real comfort "
                "through siblings and father too; its aspect on the "
                "5th brings real gain through education and children",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, with some difference "
                "around father and siblings; its aspect on the 6th "
                "brings influence over rivals through cleverness, and "
                "real victory in disputes",
        },
        "Saturn": {
            1: "Enemy's sign brings real physical hardship and "
               "illness, though some influence over rivals; its "
               "aspects bring growing sibling comfort and personal "
               "drive, some difficulty though real comfort around a "
               "partner and business, and gain, fame and comfort "
               "through father, career and business",
            2: "Friend's sign brings some flawed but real success in "
               "education and children, and an intelligent spouse; its "
               "aspects bring some deficiency in sibling comfort, some "
               "loss to fortune and religion, and heavy expense "
               "causing hardship",
            3: "Friend's sign brings real growth in influence and "
               "personal drive, victory over rivals and comfort "
               "through a partner; its aspects bring some worry over "
               "longevity, some loss to fortune and religion, and "
               "heavy expense causing hardship",
            4: "Enemy's sign brings some flawed but real success "
               "through mother, home and property, and some "
               "dissatisfaction around a partner and daily business; "
               "its aspects bring influence over rivals, real honour "
               "and success through father and career, and some "
               "illness and deficiency in beauty",
            5: "Enemy's sign brings some difficulty around education "
               "and children, though real comfort through a partner; "
               "its aspects bring growing longevity, gain through "
               "wealth and family, and real success in education "
               "despite some difficulty",
            6: "In its own sign here (Saturn rules the 6th), brings "
               "real influence over rivals and through the maternal "
               "line, despite some difficulty around daily business "
               "and a partner; its aspects bring moderate gain through "
               "longevity alongside some unease in income, heavy "
               "expense causing hardship, and growing personal drive "
               "and sibling comfort",
            7: "In its own sign here (Saturn rules the 7th), brings "
               "real difficulty around a partner and daily business "
               "despite genuine influence over rivals; its aspects "
               "bring some loss to fortune and fame, diminished beauty "
               "and mental vigour, and some deficiency in home comfort",
            8: "Enemy's sign brings friction with rivals and the "
               "maternal line, and some difficulty and gain mixed with "
               "a partner and business; its aspects bring some "
               "difficulty around father and career, some difference "
               "in income, and mixed success in education and children",
            9: "Enemy's sign brings real difficulty to fortune's "
               "advance and some loss in fame; its aspects bring good "
               "growth in income, deficiency in beauty, and growing "
               "personal drive and sibling comfort",
            10: "Friend's sign brings real gains and honour through "
                "father, career and business; its aspects bring heavy "
                "expense causing hardship, some difference in family "
                "comfort, and some deficiency in home comfort",
            11: "Friend's sign brings real growth in income; its "
                "aspects bring deficiency in beauty and mental vigour, "
                "growing personal drive and sibling comfort, and some "
                "difficulty around education and children",
            12: "Debilitated here — brings heavy expense causing real "
                "hardship, and difficulty through foreign connections; "
                "its aspects bring real growth in family comfort "
                "achieved through effort, some difficulty around home "
                "comfort, and real influence over rivals despite "
                "ongoing worry",
        },
        "Rahu": {
            1: "Brings some deficiency in beauty and comfort, with "
               "occasional severe suffering; the native advances "
               "through secretive method and courage, though troubled "
               "by inner anxiety",
            2: "Brings some difficulty though real success in wealth "
               "and family comfort, with occasional severe hardship "
               "and debt, alongside occasional sudden windfalls; "
               "clever and cunning, working hard toward wealth",
            3: "Brings real growth in personal drive, with some "
               "hardship from siblings; bold, patient and hard-working, "
               "pursuing self-interest seriously and secretively, and "
               "resolute in character",
            4: "Brings distress through the maternal line and "
               "obstacles to land and property comfort, often forcing "
               "life abroad; the native gathers comfort and endures "
               "crises through courage, secretive method and patience",
            5: "Debilitated here — brings distress through children "
               "and diminished learning; the native tries to conceal "
               "incompetence through cleverness, though lacking in "
               "politeness, refinement and truthfulness, and pursues "
               "self-interest through secretive method",
            6: "Brings victory over rivals through cleverness, despite "
               "occasional serious harassment from them; bold, brave, "
               "patient and courageous, displaying valour in conflict, "
               "though some loss through the maternal line",
            7: "Brings distress through a partner, and further "
               "difficulties in daily business, though met with great "
               "courage and patience; occasionally besieged by crises, "
               "but overcome through secretive method",
            8: "Brings repeated severe crises through life, a disorder "
               "in the lower abdomen, constant worry and anxiety, and "
               "loss around inheritance",
            9: "Brings repeated obstacles to fortune's advance and "
               "ongoing trouble, with little interest in religious "
               "observance; the native relies on many strategies for "
               "advancement, and — being patient, bold and courageous "
               "— achieves some success clearing away troubles",
            10: "Brings some deficiency in comfort through father, and "
                "difficulty in career and business, though the native "
                "overcomes many difficulties through secretive method "
                "and achieves some advancement",
            11: "Brings real growth in income, with occasional sudden "
                "windfalls; the native grows gains through courage, "
                "effort and secretive method, though occasionally "
                "suffers loss too",
            12: "Brings constant worry over managing expenses, and "
                "occasional severe crises, with loss through foreign "
                "connections too; some success comes through secretive "
                "method, effort and courage",
        },
        "Ketu": {
            1: "Brings some deficiency in health and beauty, and "
               "occasional external injury leaving a permanent mark on "
               "the body; the native remains inwardly anxious and "
               "works hard for comfort",
            2: "Brings some deficiency in savings, bringing many "
               "difficulties and worries; the native works hard to "
               "grow wealth and tries to build standing through "
               "secretive method, though never gaining full family comfort",
            3: "Brings some distress through siblings, though growing "
               "personal drive; fearless, courageous, hard-working, "
               "clever and capable, though stubborn and somewhat "
               "careless, accomplishing much through sheer strength of arm",
            4: "Brings some deficiency in mother's comfort, domestic "
               "unrest, and limited comfort through land and property, "
               "often forcing life abroad; the native works hard and "
               "relies on secretive method, though remains largely troubled",
            5: "Exalted here — brings strength through children though "
               "occasional hardship too; despite effort, education "
               "brings limited success, and the native considers "
               "themself wise, though their words carry little real influence",
            6: "Brings victory over rivals achieved through hard "
               "effort; bold and patient, advancing steadily through "
               "secretive method and inner courage without fear of "
               "trouble, though some loss through the maternal line",
            7: "Brings some difficulty around a partner and business; "
               "the native runs a household through courage, patience "
               "and secretive method, occasionally caught in serious "
               "trouble but never abandoning patience and courage, "
               "eventually succeeding — with some possibility of a "
               "reproductive-organ complaint",
            8: "Brings repeated severe crises through life and loss "
               "around inheritance; the native remains constantly "
               "anxious, yet never abandons patience or courage, "
               "overcoming difficulties through effort and secretive "
               "method, with some disorder in the lower abdomen",
            9: "Brings obstacles to fortune's advance and some "
               "weakness in religious observance; despite hard effort "
               "the native does not achieve fame, and occasionally "
               "faces severe crises, though patience, courage and "
               "secretive method bring some success and strength even "
               "without good fortune",
            10: "Brings some difficulty through father, requiring real "
                "effort for success in career and business; the native "
                "advances through courage, boldness, cleverness, "
                "discernment and hard work, overcoming difficulties "
                "and prospering",
            11: "Brings a particular hardship felt around shortage of "
                "wealth, met with hard effort and struggle to grow "
                "income; the native does not distinguish proper from "
                "improper means for gain, overcoming difficulties "
                "through secretive method and courage",
            12: "Brings real difficulty managing expenses, with "
                "constant worry and distress; the native faces "
                "repeated crises and losses, though wins through "
                "hidden courage, cleverness, effort and boldness, "
                "managing to get by despite it all",
        },
    },
    # VIRGO (Kanya) LAGNA — complete, all 108 entries, no documented gap.
    "Virgo": {
        "Sun": {
            1: "In its own sign and as Lagna-lord's own dispositor's "
               "seat here, brings a frail build, free spending, and "
               "gain through distant connections, though expense-driven "
               "worry; its aspect on the 7th brings some loss and "
               "dissatisfaction around a partner and business",
            2: "Debilitated here — brings loss to wealth and family, "
               "and limited gain from distant connections amid worry "
               "over expenses; its aspect on the 8th brings gains "
               "around longevity and inheritance",
            3: "Friend's sign brings growing personal drive though "
               "diminished sibling comfort, and real success through "
               "one's own effort — bold and influential; its aspect on "
               "the 9th brings some deficiency in fortune and "
               "religious practice",
            4: "Friend's sign brings some deficiency in home comfort, "
               "with both gain and expense through distant connections; "
               "its aspect on the 10th (own sign) brings some "
               "dissatisfaction with father, career and business",
            5: "Enemy's sign brings some deficiency in education and "
               "children, and mental strain over expenses; its aspect "
               "on the 11th brings ordinary income",
            6: "Enemy's sign brings real trouble from rivals, though "
               "influence achieved through spending; its aspect on the "
               "12th (own sign) brings heavy expense",
            7: "Friend's sign brings some loss around a partner and "
               "business, with both gain and loss through distant "
               "connections; its aspect on the Lagna brings a frail "
               "build, restlessness, a hot temper and worry over money",
            8: "Exalted here — brings real growth in longevity and "
               "inheritance despite some difficulty, and heavy expense "
               "offset by gain through distant connections; its aspect "
               "on the 2nd (debilitated) brings loss of wealth and "
               "family comfort",
            9: "Enemy's sign brings some indifference to religious "
               "practice, often marking irreligiousness, alongside "
               "gain from distant connections; its aspect on the 3rd "
               "brings some deficiency in sibling comfort and personal drive",
            10: "Friend's sign brings difficulty through father, "
                "career and business, and heavy expense offset by gain "
                "through distant connections; its aspect on the 4th "
                "brings some deficiency in home comfort",
            11: "Friend's sign brings real income despite worry over "
                "expenses, and honour and comfort from distant "
                "connections; its aspect on the 5th brings weak "
                "education and difficulty with children",
            12: "In its own sign here (Sun rules the 12th), brings "
                "heavy expense offset by gain and honour through "
                "distant connections; its aspect on the 6th brings "
                "real trouble from rivals and illness, overcome "
                "through spending",
        },
        "Moon": {
            1: "Friend's sign brings real beauty, contentment and "
               "morale, and gains wealth and fame through effort; its "
               "aspect on the 7th brings an attractive spouse and "
               "ample gain through a partner and business",
            2: "Friend's sign brings real growth in wealth and family, "
               "and real savings; its aspect on the 8th brings growth "
               "in longevity and inheritance",
            3: "Debilitated here — brings some diminished personal "
               "drive and sibling comfort, along with financial "
               "hardship and worry; its aspect on the 9th (exalted) "
               "brings advancement in fortune through effort and real "
               "interest in religious practice",
            4: "Friend's sign brings ample comfort through mother, "
               "home and property, and a contented mind; its aspect on "
               "the 10th brings real honour, standing, success and "
               "influence through father, career and business",
            5: "Enemy's sign brings some deficiency in wealth "
               "accumulation despite gain, and worry over education "
               "and children; its own-sign aspect on the 11th brings "
               "real growth in income",
            6: "Enemy's sign brings mental unrest through rivals "
               "though victory achieved through humility; its aspect "
               "on the 12th brings heavy expense offset by gain "
               "through distant connections",
            7: "Friend's sign brings a beautiful spouse, comfort in "
               "daily life, and real success in business; its aspect "
               "on the Lagna brings real physical beauty, health, "
               "vigour and cheer",
            8: "Friend's sign brings real gains in longevity and "
               "inheritance, though some difficulty; its aspect on the "
               "2nd brings real wealth and family comfort",
            9: "Brings real wealth, unexpected windfalls and good "
               "fortune; its aspect on the 3rd brings some diminished "
               "sibling comfort and personal drive",
            10: "Friend's sign brings real standing, comfort and "
                "honour through father, career and business; its "
                "aspect on the 4th brings ample comfort through "
                "mother, home and property",
            11: "In its own sign here (Moon rules the 11th), brings "
                "real income gained through personal willpower; its "
                "aspect on the 5th brings some weakness in education "
                "and difference with children",
            12: "Friend's sign brings heavy expense offset by real "
                "gain through distant connections; its aspect on the "
                "6th brings some worry, though real success and "
                "honour achieved through humility and spending",
        },
        "Mars": {
            1: "Friend's sign brings some deficiency in physical "
               "beauty, though growing sibling comfort and personal "
               "drive; its aspects bring some deficiency in home "
               "comfort, some difficulty around a partner and "
               "business, and growth in longevity",
            2: "Enemy's sign brings some loss to sibling comfort "
               "though real gain in wealth; its aspects bring success "
               "through effort in education and children, growth in "
               "longevity and inheritance, and some difficulty to "
               "fortune and religious practice",
            3: "In its own sign here (Mars rules the 3rd), brings real "
               "growth in personal drive despite some loss to sibling "
               "comfort; its aspects bring influence over rivals, "
               "advancement in fortune and religion, and some "
               "difficulty through father, career and business despite effort",
            4: "Friend's sign brings some deficiency in home and "
               "sibling comfort alike, though gain through personal "
               "drive; its aspects bring some difficulty around a "
               "partner and business, some difference with father "
               "alongside real advancement, and good growth in income",
            5: "Enemy's sign brings some difficulty around a partner, "
               "and real gains in education through effort; its "
               "aspects bring real growth in longevity, good income, "
               "and some difficulty around wealth and family",
            6: "Enemy's sign brings real success through humility and "
               "financial strength; its aspects bring advancement in "
               "fortune through wit, heavy expense causing hardship, "
               "and real growth in courage and personal drive",
            7: "Friend's sign brings some flawed but real success "
               "around a partner and business; its aspects bring "
               "cooperation and success through father and career, and "
               "good growth in income",
            8: "In its own sign here (Mars rules the 8th), brings some "
               "difficulty though real gains in longevity and "
               "inheritance; its aspects bring good growth in income, "
               "real wealth grown through secretive method, and "
               "growing personal drive and sibling comfort",
            9: "Enemy's sign brings real advancement in fortune "
               "despite some difficulty; its aspects bring heavy "
               "expense offset by gain through distant connections, "
               "some difference with siblings alongside growing "
               "personal drive, and some deficiency in home comfort",
            10: "Friend's sign brings cooperation, success and "
                "standing through father, career and business; its "
                "aspects bring some deficiency in physical beauty and "
                "home comfort, and some flawed but real success in "
                "education and children",
            11: "Friend's sign brings real growth in income; its "
                "aspects bring real wealth through effort, mixed "
                "success in education and children, and growing "
                "influence over rivals",
            12: "Friend's sign brings heavy expense causing real "
                "hardship; its aspects bring growing personal drive "
                "and sibling comfort, real influence over rivals, and "
                "some difficulty around a partner and business",
        },
        "Mercury": {
            1: "In its own sign and as Lagna-lord here, brings real "
               "physical beauty, and standing, comfort and success "
               "through father, career and business; its aspect on "
               "the 7th brings some deficiency in a partner and daily income",
            2: "Friend's sign brings real growth in wealth and family "
               "comfort, and standing, comfort and success through "
               "father and career too; its aspect on the 8th brings "
               "growth in longevity",
            3: "Friend's sign brings growing personal drive and "
               "sibling comfort, and standing through father, career "
               "and business too; its aspect on the 9th brings "
               "advancement in fortune and religion",
            4: "Friend's sign brings real comfort through mother, home "
               "and property, and physical wellbeing; its aspect on "
               "the 10th (own sign) brings gain and success in career, "
               "father and business",
            5: "Friend's sign brings real success in education, "
               "children and a high position; its aspect on the 11th "
               "brings good income despite some difficulty, and "
               "standing through father and career too",
            6: "Friend's sign brings success over rivals through "
               "discernment, and gain through the maternal line, "
               "though some deficiency in beauty and career standing; "
               "its aspect on the 12th brings heavy expense offset by "
               "gain through distant connections",
            7: "Friend's sign brings a real sense of inadequacy before "
               "a capable spouse, though real advancement through "
               "effort, and standing through father and career too; "
               "its aspect on the Lagna (own sign) brings some "
               "deficiency in beauty and peace of mind",
            8: "Friend's sign brings some deficiency in beauty, and "
               "difficulty through father, career and business; its "
               "aspect on the 2nd brings growth in wealth through "
               "secretive method and family affection",
            9: "Friend's sign brings real advancement in fortune, "
               "religion, and standing through father and career; its "
               "aspect on the 3rd brings growing personal drive and "
               "sibling comfort",
            10: "In its own sign here (Mercury rules the 10th), brings "
                "real standing, success and honour through father, "
                "career and business; its aspect on the 4th brings "
                "ample comfort through mother, home and property",
            11: "Friend's sign brings real income and standing through "
                "father, career and business, and growing beauty and "
                "morale; its aspect on the 5th brings real advancement "
                "in education, intellect and children",
            12: "Friend's sign brings heavy expense offset by standing "
                "and gain through distant connections, though some "
                "dissatisfaction through father and career; its "
                "aspect on the 6th brings success over rivals through "
                "discernment",
        },
        "Jupiter": {
            1: "Friend's sign brings real physical beauty and health, "
               "and comfort through mother, home and property; its "
               "aspects bring some difficulty around education and "
               "children, real comfort in daily business and "
               "partnership (own sign), and some obstacles to fortune "
               "and religion despite real integrity",
            2: "Brings real wealth and family comfort though some "
               "difficulty around mother and a partner, alongside "
               "career advancement; its aspects bring influence over "
               "rivals, growth in longevity, and gain, fame and "
               "honour through father, career and business",
            3: "Friend's sign brings growing personal drive and "
               "sibling comfort, and comfort through mother and home "
               "too; its aspects bring real success around a partner "
               "and business with a lovely spouse, advancement in "
               "fortune despite some hindrance, and very good income",
            4: "In its own sign here (Jupiter rules the 4th), brings "
               "real comfort through mother, home and property, and "
               "success around a partner and business too; its "
               "aspects bring growth in longevity, standing through "
               "father, career and business, and heavy expense offset "
               "by gain through distant connections",
            5: "Debilitated here — brings distress through children "
               "and diminished learning, and some weakness through the "
               "maternal line; its aspects bring some ordinary "
               "advancement in fortune and religion, growth in income, "
               "and real physical strength, honour and skill",
            6: "In its own sign here (Jupiter rules the 6th), brings "
               "humility used successfully against rivals, with some "
               "deficiency in home comfort; its aspects bring "
               "standing, comfort and success through father, career "
               "and business, heavy expense offset by gain through "
               "distant connections, and ordinary comfort through family",
            7: "In its own sign here (Jupiter rules the 7th), brings "
               "real comfort and gain through a partner and business, "
               "and ample comfort through mother and home; its "
               "aspects bring very good income, real comfort through "
               "physical health and standing, and growing sibling "
               "comfort and personal drive",
            8: "Friend's sign brings real gains through longevity and "
               "inheritance, though some deficiency around a partner "
               "and business; its aspects bring heavy expense offset "
               "by gain through distant connections, real effort "
               "needed to grow wealth, and comfort through mother and "
               "home achieved through some difficulty",
            9: "Brings some difficulty though real advancement in "
               "fortune, and some deficiency around a partner and "
               "business; its aspects bring real comfort, honour and "
               "pleasure in daily affairs, growing personal drive and "
               "sibling comfort, and some deficiency in education and children",
            10: "Friend's sign brings real gains through father, "
                "career and business, and an attractive, capable "
                "spouse; its aspects bring wealth and family comfort, "
                "real comfort through mother and home, and influence "
                "over rivals through peace-making",
            11: "Friend's sign brings real growth in income and "
                "comfort through mother and home too; its aspects "
                "bring growing personal drive and sibling comfort, "
                "some difficulty around education and children, and "
                "real success in daily business with a beautiful, "
                "capable spouse",
            12: "Friend's sign brings heavy expense offset by standing "
                "and gain through distant connections; its aspects "
                "bring ordinary comfort through mother and home, real "
                "success against rivals through cautious effort, and "
                "growth in longevity",
        },
        "Venus": {
            1: "Debilitated here — brings some deficiency in wealth "
               "and family comfort, and an inclination toward earning "
               "through improper means; its aspect on the 7th "
               "(exalted) brings a fortunate, beautiful spouse and "
               "real success in business and pleasure",
            2: "In its own sign here (Venus rules the 2nd), brings "
               "real growth in wealth and family comfort, righteousness "
               "and fame; its aspect on the 8th brings growth in "
               "longevity and inheritance too",
            3: "Enemy's sign brings good comfort through siblings, and "
               "growing personal drive and family comfort; its aspect "
               "on the 9th (own sign) brings real advancement in "
               "fortune and religion",
            4: "Enemy's sign brings real gain through mother, home and "
               "property, and family wealth; its aspect on the 10th "
               "brings standing, comfort and gain through father, "
               "career and business, alongside true religious observance",
            5: "Friend's sign brings real strength through children, "
               "and growth in wealth, fortune and religion through "
               "wit; its aspect on the 11th brings income and "
               "advancement grown through the native's own wit and effort",
            6: "Friend's sign brings some difficulty in fortune and "
               "family comfort, and indifference to religious "
               "practice, though real advancement through cleverness "
               "and success over rivals through effort; its aspect on "
               "the 12th brings heavy expense offset by gain through "
               "distant connections",
            7: "Exalted here — brings an attractive, fortunate spouse "
               "and real success in business too; its aspect on the "
               "Lagna brings some deficiency in physical beauty",
            8: "Enemy's sign brings some difficulty to fortune and "
               "wealth, and incomplete religious observance, though "
               "real gains around longevity; its aspect on the 2nd "
               "(own sign) brings wealth grown through secretive "
               "method and hard effort",
            9: "In its own sign here (Venus rules the 9th), brings "
               "real fortune and devotion, and growth in wealth, "
               "honour and fame; its aspect on the 3rd brings growing "
               "personal drive and family comfort",
            10: "Friend's sign brings real standing, comfort and gain "
                "through father, career and business, and a righteous "
                "character; its aspect on the 4th brings real comfort "
                "through mother, home and property",
            11: "Enemy's sign brings real success in education and "
                "children, and gain from distant connections offset by "
                "hardship; its aspect on the 5th brings good growth in "
                "income through wit",
            12: "Enemy's sign brings heavy expense from distant "
                "connections, loss to savings, and some difficulty to "
                "fortune's advance; its aspect on the 6th brings real "
                "success over rivals through disputes and litigation",
        },
        "Saturn": {
            1: "Friend's sign brings an illness-prone body, and some "
               "difference with children though real success in "
               "education and with children generally, and victory "
               "over rivals; its aspects bring some diminished sibling "
               "comfort, some difference with a partner though real "
               "effort brings success in business (own sign), and "
               "ordinary difficulty through father though success through career",
            2: "Friend's sign brings real success in education and "
               "children, though some difference with children too; "
               "its aspects bring some deficiency in home comfort, "
               "some loss to longevity and inheritance, and income "
               "achieved through struggle and effort",
            3: "Enemy's sign brings friction with rivals though real "
               "success and growing personal drive; its aspects bring "
               "real success in education though ordinary difficulty "
               "with children (own sign), advancement in fortune "
               "through effort, and some difficulty in managing expenses",
            4: "Friend's sign brings some deficiency in home comfort "
               "and difficulty around children, though real gain in "
               "education; its aspects bring real influence over "
               "rivals and mixed fortune from disputes (own sign), "
               "success in career through effort, and some physical "
               "unease alongside real effort and influence",
            5: "In its own sign here (Saturn rules the 5th), brings "
               "some difficulty though real gain in education and "
               "children; its aspects bring some difficulty around a "
               "partner and business, income through secretive method, "
               "and wealth grown through real effort",
            6: "In its own sign here (Saturn rules the 6th), brings "
               "success over rivals through wit despite some "
               "difficulty around education and children; its aspects "
               "bring repeated crises around longevity, expense-driven "
               "hardship and unpleasant foreign ties, and some "
               "difficulty from siblings though growing personal drive",
            7: "Enemy's sign brings difficulty around a partner and "
               "business, some reproductive-organ complaint, and "
               "difficulty with children too, though real success over "
               "rivals; its aspects bring advancement in fortune "
               "through effort, real illness alongside growing "
               "influence, and some difference through mother, home "
               "and property",
            8: "Friend's sign brings repeated crises around longevity, "
               "and difficulty through father and career, though "
               "ordinary success in business through wit; its aspects "
               "bring wealth grown through hard effort and some "
               "difficulty around children (own sign)",
            9: "Friend's sign brings advancement in fortune through "
               "wit and ordinary religious observance, though real "
               "difficulty growing income; its aspects bring real "
               "success against rivals, some difference with siblings "
               "alongside growing personal drive, and real difficulty "
               "from disputes despite eventual success (own sign)",
            10: "Friend's sign brings some difficulty through father, "
                "though real standing and gain through career, and "
                "comfort through education and children; its aspects "
                "bring expense-driven dissatisfaction and unpleasant "
                "foreign ties, some deficiency in home comfort, and "
                "some difficulty around a partner and business",
            11: "Enemy's sign brings real growth in income, though "
                "some illness; its aspects bring some illness, real "
                "strength through education and children, and some "
                "loss to longevity and inheritance",
            12: "Enemy's sign brings heavy expense and unpleasant "
                "foreign ties; its aspects bring growth in wealth and "
                "family comfort achieved through real effort, real "
                "influence over rivals despite some illness (own "
                "sign), and advancement in fortune and religion through wit",
        },
        "Rahu": {
            1: "Brings real physical strength, firm resolve and "
               "self-respect, though occasional physical suffering; "
               "deeply thoughtful and hard-working, advancing despite "
               "inner worry through great courage",
            2: "Brings deep distress over wealth and family, though "
               "the native saves some through secretive method and "
               "hard effort, at times regarded as wealthy despite the "
               "strain, with occasional sudden gains and losses alike",
            3: "Brings real growth in personal drive despite trouble "
               "from siblings; the native achieves success through "
               "secretive method and courage, pursuing self-interest "
               "without regard for right or wrong",
            4: "Brings good comfort through the mother, though some "
               "deficiency in home comfort, occasionally causing "
               "severe domestic crises; life abroad brings comfort "
               "where the homeland brings distress",
            5: "Brings distress through children and difficulty in "
               "education; the native is clever in speech despite "
               "limited real learning, unconcerned with truth in the "
               "effort to prove themself, and often anxious",
            6: "Brings real influence over rivals, maintained through "
               "courage and patience even in crisis, never revealing "
               "weakness, and mastering difficulties through secretive method",
            7: "Brings distress through a partner and difficulty in "
               "business, along with some reproductive-organ "
               "complaint; the native manages through secretive method "
               "and hard effort",
            8: "Brings repeated severe suffering through life, along "
               "with a stomach ailment; the native advances through "
               "secretive method, courage and patience, though "
               "constantly beset by worry and distress",
            9: "Brings hard effort required for fortune's advance, and "
               "imperfect religious observance, with occasional severe "
               "crises around fortune; only modest advancement is "
               "achieved through secretive method, courage and patience",
            10: "Brings real advancement through struggle with the "
                "father; standing and success in career and business "
                "come through secretive method and cleverness, with "
                "occasional crises resolving themselves in time",
            11: "Brings real growth in income, alongside real "
                "difficulty; the native experiences both great gain "
                "and great loss, advancing through secretive method, "
                "courage, patience and hard effort, though occasionally deceived",
            12: "Brings real difficulty managing expenses, and trouble "
                "through foreign connections too; the native manages "
                "through secretive method, courage, patience and hard "
                "effort, with occasional sudden windfalls",
        },
        "Ketu": {
            1: "Brings physical distress and worry, sometimes a deep "
               "scar or illness, and some deficiency in physical "
               "beauty; bold, patient and somewhat blunt in manner, "
               "relying on secretive method",
            2: "Brings some deficiency in wealth and family comfort, "
               "with occasional sudden loss as well as occasional "
               "sudden gain; the native works tirelessly to grow "
               "wealth, remaining constantly troubled",
            3: "Brings real growth in personal drive despite trouble "
               "from siblings; the native never loses courage even in "
               "crisis, trusting their own strength of arm, and is "
               "hard-working besides",
            4: "Exalted here — brings comfort through mother, home and "
               "property, and a well-appointed domestic life achieved "
               "through real effort, alternating between domestic "
               "crisis and domestic prosperity",
            5: "Brings worry over children and difficulty attaining "
               "education; the native feels this deficiency personally, "
               "yet presents themself as capable and wise, and is "
               "notably quick in conversation",
            6: "Brings real, particular influence over rivals, though "
               "some difficulty from the maternal line; bold, patient, "
               "fearless and somewhat blunt, succeeding through these "
               "very qualities",
            7: "Brings distress through a partner and real difficulty "
               "in business, worked through with secretive method, "
               "patience and courage; married life succeeds only with "
               "real difficulty, with some possibility of a "
               "reproductive-organ complaint",
            8: "Brings repeated life-threatening crises and loss "
               "around inheritance, along with a stomach ailment; the "
               "native is hard-working, quick-tempered, patient, "
               "courageous and swift to act",
            9: "Brings some deficiency in religious observance and "
               "severe crises to fortune's advance; the native "
               "protects themselves from crisis through cleverness, "
               "secretive method, discernment and courage, "
               "occasionally passing through especially troubling circumstances",
            10: "Brings loss through the father, and limited real "
                "influence in career and business; the native suffers "
                "loss of standing and wealth, often caught up in "
                "disputes and difficulties",
            11: "Brings growth in income alongside real mental "
                "distress; the native experiences both crisis and loss "
                "as well as occasional sudden gain, remaining patient "
                "and hard-working throughout",
            12: "Brings many worries and difficulties over managing "
                "expenses, with foreign connections proving troublesome "
                "too; the native occasionally falls into crisis, "
                "though escapes through patience and secretive method "
                "as best they can",
        },
    },
    "Libra": {
        "Sun": {
            1: "Debilitated in an enemy's sign brings a frail build "
               "and diminished shine, a dislike of servitude, and some "
               "deficiency in courage; its aspect on the 7th (exalted) "
               "brings gain through a partner, a beautiful spouse, and "
               "growth in domestic pleasure and business",
            2: "Friend's sign brings ample wealth and family comfort, "
               "prosperity and influence; its aspect on the 8th brings "
               "some deficiency in longevity and inheritance",
            3: "Friend's sign brings growing sibling comfort and "
               "personal drive, with real confidence in one's own "
               "strength; its aspect on the 9th brings advancement in "
               "fortune and religious practice, and good income",
            4: "Enemy's sign brings full comfort through mother, home "
               "and land, despite some accompanying difficulty; its "
               "aspect on the 10th brings comfort, success, fame and "
               "honour through father, career and business",
            5: "Enemy's sign brings unsatisfying gain through "
               "children, and education achieved only with real "
               "difficulty; its aspect on the 11th (own sign) brings "
               "intellectual pleasure and income through hard work, "
               "though some mental strain",
            6: "Friend's sign brings victory over rivals and gain "
               "through enemies, with good income; its aspect on the "
               "12th brings heavy expense offset by gain through "
               "distant connections",
            7: "Friend's sign brings a beautiful spouse and real gain "
               "through a partner and business; its aspect on the "
               "Lagna (debilitated) brings diminished physical beauty "
               "and health, and a troubled mind",
            8: "Enemy's sign — Sun as 11th lord here — brings wealth "
               "through hard work and gain from distant connections, "
               "and growth in longevity though some loss to "
               "inheritance; its aspect on the 2nd brings effort "
               "toward wealth and family comfort",
            9: "Friend's sign brings growing fortune and religious "
               "practice, with adequate wealth and comfort; its aspect "
               "on the 3rd brings growth in sibling comfort and "
               "personal drive",
            10: "Friend's sign brings comfort, honour and success "
                "through father, career and business, with strong "
                "growth in income; its aspect on the 4th brings some "
                "deficiency in comfort through mother, land and home",
            11: "In its own sign here (Sun rules the 11th), brings "
                "strong growth in income; its aspect on the 5th brings "
                "some dissatisfaction with children and deficiency in "
                "education, and gives sharp, forceful speech",
            12: "Friend's sign brings heavy expense offset by comfort, "
                "success and gain through distant connections; its "
                "aspect on the 6th brings friendship struck with "
                "rivals, gain through disputes, and growing influence",
        },
        "Moon": {
            1: "Friend's sign brings real physical beauty, health and "
               "an influential presence, along with respect in public "
               "life; its aspect on the 7th brings a beautiful spouse "
               "and gain through business",
            2: "Debilitated despite a friend's sign — brings some "
               "difficulty in wealth and family comfort, with "
               "secretive method needed for saving; its aspect on the "
               "8th brings gain in longevity and inheritance",
            3: "Friend's sign brings sibling comfort, growing personal "
               "drive, and success through father, career and "
               "business, along with gain in inheritance; its aspect "
               "on the 9th brings growth in fortune and religious "
               "practice, and gives a bold, courageous nature",
            4: "Enemy's sign brings comfort through mother, land and "
               "home, though with some flaw; its aspect on the 10th "
               "brings comfort, cooperation, success and honour "
               "through father, career and business",
            5: "Enemy's sign brings success in children, education "
               "and growth, along with gain through career and "
               "business, and gives sharp intelligence; its aspect on "
               "the 11th brings real growth in income and prosperity",
            6: "Friend's sign brings success over rivals through wit, "
               "morale and a calm temperament, though some obstruction "
               "through father, career and business; its aspect on "
               "the 12th brings heavy expense offset by gain through "
               "distant connections",
            7: "Friend's sign brings great success in business, with "
               "advancement and influence gained through the spouse, "
               "and fame and gain through father, career and "
               "business; its aspect on the Lagna brings real physical "
               "beauty, health, influence and standing",
            8: "Exalted, though in only a friend's sign — brings "
               "growth in longevity and inheritance and a joyful daily "
               "life, though some loss through the father, only "
               "ordinary standing with authority, and gain through "
               "career and business only with some difficulty; its "
               "aspect on the 2nd brings weak wealth and family comfort",
            9: "Friend's sign brings growth in fortune and religious "
               "practice, along with fame, cooperation and honour "
               "through father, career and business; its aspect on "
               "the 3rd brings sibling comfort and growth in personal "
               "drive",
            10: "In its own sign here (Moon rules the 10th), brings "
                "comfort, cooperation, honour, fame and gain through "
                "father, career and business, and gives a "
                "self-respecting, socially well-regarded nature; its "
                "aspect on the 4th brings some deficiency in comfort "
                "through mother, land and home",
            11: "Friend's sign brings continual opportunities for "
                "gain, and success, honour and fame through father, "
                "career and business; its aspect on the 5th brings "
                "some dissatisfaction with children, though real gain "
                "in education, and gives a clever, capable, somewhat "
                "self-serving nature",
            12: "Friend's sign brings heavy expense offset by gain "
                "and advancement through distant connections, though "
                "some loss through father, career and business, and "
                "diminished standing; its aspect on the 6th brings "
                "success over rivals through strength and skill",
        },
        "Mars": {
            1: "Friend's sign brings physical comfort and personal "
               "standing, along with domestic happiness; its aspects "
               "bring special comfort through mother, land and home "
               "(exalted), comfort through a spouse and advancement in "
               "business (own sign), and growth in longevity and "
               "inheritance alongside some digestive trouble",
            2: "In its own sign here (Mars rules the 2nd), brings "
               "ample wealth and family comfort; its aspects bring "
               "gain in children and education though with some "
               "difficulty, growing strength in longevity and "
               "inheritance, and growth in fortune and religious "
               "practice",
            3: "Friend's sign brings sibling comfort, growing personal "
               "drive, real wealth, and success with a spouse; its "
               "aspects bring victory over rivals, growth in fortune "
               "and religious practice, and some obstruction through "
               "father, career and business (debilitated)",
            4: "Enemy's sign, though exalted, brings full comfort "
               "through mother, land and home; its aspects bring "
               "comfort through a spouse and business (own sign), some "
               "obstruction to comfort through father and to "
               "advancement in career, and strong growth in income and "
               "prosperity",
            5: "Enemy's sign brings success in children and education "
               "only with real difficulty, some discord with family "
               "and spouse, and success in business through "
               "intelligence; its aspects bring some difficulty around "
               "longevity, good income, and heavy expense offset by "
               "gain through distant connections",
            6: "Friend's sign brings strong influence over rivals, "
               "some deficiency in savings, and success around a "
               "spouse and business only with real difficulty; its "
               "aspects bring growth in fortune and religious "
               "practice, heavy expense offset by gain through distant "
               "connections, and diminished physical beauty alongside "
               "gain through disputes and litigation",
            7: "Own sign here (Mars rules the 7th) brings some "
               "restraint through the spouse though ample domestic "
               "pleasure, and good daily business; its aspects bring "
               "some deficiency through father, career and business "
               "(debilitated), heat or blood disorders in the body, "
               "and good wealth and family comfort (own sign)",
            8: "Enemy's sign brings some difficulty around a spouse "
               "and daily business, with gain through distant business "
               "and inheritance; its aspects bring strong income, "
               "wealth and family comfort gained through effort (own "
               "sign), and ordinary sibling comfort alongside growth "
               "in personal drive",
            9: "Friend's sign brings real advancement in fortune and "
               "religious observance, with a fortunate spouse who "
               "brings real gain after marriage; its aspects bring "
               "heavy expense offset by gain through distant "
               "connections, sibling comfort and growth in personal "
               "drive, and full comfort through mother, land and home "
               "(exalted)",
            10: "Friend's sign, though debilitated, brings difficulty "
                "through father, career and business, and some "
                "deficiency in family and spousal comfort; its aspects "
                "bring physical weakness alongside real respect and "
                "honour, comfort through mother, land and home "
                "(exalted), and discord with children with some "
                "deficiency in education",
            11: "Friend's sign brings ample wealth, along with comfort "
                "and gain through a spouse; its aspects bring wealth "
                "and family comfort (own sign), some dissatisfaction "
                "with children and deficiency in education, and some "
                "difficulty around a spouse offset by gain through "
                "distant business",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, along with loss and "
                "dissatisfaction in wealth, family, spouse and "
                "business; its aspects bring sibling comfort and "
                "growth in personal drive, success over rivals, and "
                "gain in business through distant connections "
                "alongside some deficiency with a spouse (own sign)",
        },
        "Mercury": {
            1: "Friend's sign brings a frail body, gain through "
               "distant connections though heavy spending, and though "
               "fortune is modest the native is seen as fortunate, "
               "upholding religious duty; its aspect on the 7th brings "
               "success with a spouse and in daily business",
            2: "Friend's sign brings some deficiency in wealth and "
               "family comfort, with heavy spending and religious duty "
               "followed mainly out of self-interest; its aspect on "
               "the 8th brings real gain in longevity and inheritance, "
               "and the native is generally considered wealthy",
            3: "Friend's sign brings sibling comfort and growth in "
               "personal drive, and gain through distant connections, "
               "though with some obstacle to fortune; its aspect on "
               "the 9th (own sign) brings growth in fortune and "
               "religious observance, marking a contented, wealthy, "
               "righteous and glorious nature",
            4: "Friend's sign brings comfort through mother, land and "
               "home, real gain through distant connections, and heavy "
               "spending; its aspect on the 10th brings honour, "
               "cooperation, standing, fame and gain through father, "
               "career and business",
            5: "Friend's sign brings strength through children, gain "
               "in education alongside prosperity, growth in fortune "
               "through distant connections, and heavy spending; its "
               "aspect on the 11th brings strong income, marking a "
               "righteous, well-regarded, fortunate nature",
            6: "Debilitated in Jupiter's sign brings difficulty from "
               "rivals and expenses managed only with hardship, along "
               "with weakness in fortune and religious practice, "
               "though offset by gain through distant connections; its "
               "aspect on the 12th (own sign) brings heavy expense",
            7: "Friend's sign — Mercury as 12th lord here — brings "
               "some difficulty around a spouse and business though "
               "real success achieved, well-managed household expense, "
               "religious observance, and gain through distant "
               "connections; its aspect on the Lagna brings physical "
               "comfort and standing, and the native is seen as "
               "fortunate",
            8: "Friend's sign brings strength in longevity and "
               "inheritance though weakness in fortune and religious "
               "practice; gain through distant connections comes only "
               "with difficulty, and expenses prove troublesome; its "
               "aspect on the 2nd brings growth in wealth despite "
               "difficulty, though with little accompanying fame",
            9: "In its own sign here (Mercury rules the 9th), brings "
               "growth in fortune and religious duty, heavy spending, "
               "and real gain through distant connections; its aspect "
               "on the 3rd brings sibling comfort and growing personal "
               "drive despite some difficulty",
            10: "Enemy's sign brings difficulty advancing through "
                "father, career and business, with little religious "
                "observance and limited growth in fortune; its aspect "
                "on the 4th brings full comfort through mother, land "
                "and home, and the native is considered wealthy",
            11: "Friend's sign brings strong income, marking a "
                "righteous, fortunate nature; its aspect on the 5th "
                "brings success in children and education, and real "
                "advancement through intelligence and eloquence, "
                "though as 12th lord some difficulty persists in every "
                "sphere",
            12: "Exalted in its own sign here (Mercury rules the "
                "12th), brings heavy expense offset by comfort and "
                "gain through distant connections despite some "
                "difficulty; its aspect on the 6th brings trouble from "
                "rivals overcome by secretive, sometimes improper "
                "method, marking a wealthy, contented nature",
        },
        "Jupiter": {
            1: "Enemy's sign brings physical vigour, valour and "
               "standing, though some deficiency in sibling comfort, "
               "and influence established over rivals through courage; "
               "its aspects bring discord over children though gain "
               "in education, gain through a spouse and business, and "
               "growth in fortune and religious practice",
            2: "Friend's sign brings wealth grown through personal "
               "effort, though some deficiency in sibling comfort; its "
               "aspects bring victory over rivals through the strength "
               "of one's wealth (own sign), growth in longevity with "
               "only ordinary gain in inheritance, and fame, comfort, "
               "honour and gain through father, career and state "
               "affairs (exalted)",
            3: "In its own sign here (Jupiter rules the 3rd), brings "
               "growth in personal drive though some deficiency in "
               "sibling comfort, and influence established over "
               "rivals; its aspects bring success with a spouse and in "
               "business, growth in fortune and religious practice, "
               "and strong success in income, marking a contented, "
               "wealthy, righteous and fortunate nature",
            4: "Enemy's sign, debilitated, brings deficiency in "
               "comfort through mother, land and home, and trouble "
               "from rivals; its aspects bring some gain in longevity "
               "and inheritance, real success through father, career "
               "and business, and heavy expense offset by gain through "
               "distant connections",
            5: "Enemy's sign brings success in education and children "
               "only with some difficulty, growing influence over "
               "rivals, and some discord with siblings; its aspects "
               "bring growth in fortune and religion through personal "
               "effort, strong income, and physical strength and "
               "standing though some deficiency in health",
            6: "In its own sign here (Jupiter rules the 6th), brings "
               "influence over rivals, some discord with siblings, "
               "and some deficiency in personal drive; its aspects "
               "bring real honour and success through father, career "
               "and business (exalted), heavy expense offset by gain "
               "through distant connections, and growth in wealth "
               "despite some discord with family",
            7: "Friend's sign brings advancement in business through "
               "personal effort and strength gained through the "
               "spouse, though some discord with her; its aspects "
               "bring real earning through effort, some trouble in the "
               "body though growing influence, and sibling comfort "
               "with some deficiency alongside real growth in personal "
               "drive (own sign)",
            8: "Enemy's sign brings growth in longevity and "
               "inheritance, though some deficiency in sibling comfort "
               "and personal drive, and trouble from rivals; its "
               "aspects bring growth in wealth and family comfort, "
               "some deficiency in comfort through mother, land and "
               "home (debilitated), and heavy expense offset by gain "
               "through distant connections",
            9: "Friend's sign brings growth in fortune and religious "
               "practice, and a celebrated, fortunate nature, though "
               "some difficulty to fortune's advance through rivalry; "
               "its aspects bring some bodily weakness alongside "
               "growing influence, sibling comfort and growth in "
               "personal drive (own sign), and some discord over "
               "children alongside real success in education and "
               "intelligence",
            10: "Friend's sign brings success through father, career "
                "and business, and sibling comfort though with some "
                "discord; its aspects bring wealth and family comfort, "
                "some deficiency in comfort through mother, land and "
                "home (debilitated), and influence established over "
                "rivals (own sign)",
            11: "Friend's sign brings growth in wealth and prosperity "
                "through hard work, with gain even from rivals; its "
                "aspects bring sibling comfort and growth in personal "
                "drive, some discord over children and education "
                "alongside real growth in intelligence, and success "
                "with a spouse and in business",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, and some deficiency in "
                "sibling comfort alongside growing personal drive; its "
                "aspects bring success over rivals through secretive "
                "method (own sign), and some difficulty alongside gain "
                "in inheritance and longevity",
        },
        "Venus": {
            1: "In its own sign here (Venus is Lagna-lord), brings "
               "real growth in physical and mental strength and "
               "influence, and gain in longevity and inheritance, "
               "though as 8th lord some occasional bodily trouble; its "
               "aspect on the 7th brings some deficiency in spousal "
               "comfort and calls for real effort in advancing business",
            2: "Enemy's sign brings family comfort though real effort "
               "is needed to save wealth, with occasional difficulty; "
               "its aspect on the 8th (own sign) brings strength in "
               "longevity and inheritance, marking a life of comfort "
               "and luxury",
            3: "Enemy's sign brings some discord with siblings though "
               "growth in personal drive, along with gain in longevity "
               "and inheritance; its aspect on the 9th brings growth "
               "in fortune and religious practice, marking an "
               "influential life",
            4: "Friend's sign brings comfort through mother, land and "
               "home with some deficiency, along with gain in "
               "longevity and inheritance; its aspect on the 10th "
               "brings comfort, honour, gain and cooperation through "
               "father, career and business",
            5: "Friend's sign brings success in education though some "
               "deficiency regarding children, along with excellent "
               "gain in longevity and inheritance; its aspect on the "
               "11th brings good gain in income, and advancement "
               "through intelligence",
            6: "Exalted, though in an enemy's sign, brings strong "
               "influence over rivals and victory over even great "
               "difficulty, with ordinary gain in longevity and "
               "inheritance too; its aspect on the 12th brings some "
               "trouble through expenses and distant connections, "
               "marking a life of comfortable, easy living",
            7: "Enemy's sign brings some difficulty around the spouse "
               "though real strength gained through her, success in "
               "daily business through physical effort, and gain in "
               "longevity and inheritance; its aspect on the Lagna "
               "(own sign) brings physical beauty, self-respect and "
               "influence",
            8: "In its own sign here (Venus rules the 8th), brings "
               "gain in longevity and inheritance, though some "
               "deficiency in physical beauty and health; its aspect "
               "on the 2nd brings wealth requiring cleverness to save, "
               "with some discord in the family",
            9: "Friend's sign brings growth in fortune and religious "
               "practice though with some deficiency, along with "
               "strength in longevity and inheritance, and physical "
               "beauty and good character; its aspect on the 3rd "
               "brings growth in personal drive, alongside ordinary "
               "discord with siblings",
            10: "Enemy's sign brings success through father, career "
                "and business achieved only with some difficulty, "
                "largely through skill and physical effort; its "
                "aspect on the 4th brings full comfort through mother, "
                "land and home",
            11: "Enemy's sign brings real gain achieved through "
                "physical effort and skill, along with strength in "
                "longevity and inheritance; its aspect on the 5th "
                "brings success with children achieved with some "
                "difficulty, though real growth in the power of "
                "education and speech",
            12: "Debilitated, though in a friend's sign, brings "
                "difficulty managing expenses and trouble through "
                "distant connections, along with some deficiency in "
                "longevity, inheritance and physical vitality; its "
                "aspect on the 6th (exalted) brings strong influence "
                "over rivals and success in disputes through courage "
                "and cleverness",
        },
        "Saturn": {
            1: "Friend's sign brings a heavy build and an influential "
               "presence, along with excellent comfort through "
               "mother, land, home, children and education; its "
               "aspects bring some discord with siblings and personal "
               "drive gained only with difficulty, some discord with "
               "a spouse and difficulty in business (debilitated), "
               "and reduced comfort through father alongside success "
               "through career and state affairs",
            2: "Enemy's sign brings difficulty saving wealth and "
               "discord with family, along with some deficiency "
               "regarding children though gain in education; its "
               "aspects bring full comfort through mother, land and "
               "home (own sign), gain in longevity and inheritance, "
               "and income that grows well only with some difficulty",
            3: "Enemy's sign brings real growth in personal drive "
               "though some discord with siblings, along with "
               "strength gained through the mother; its aspects bring "
               "real success in education and children though some "
               "discord regarding children (own sign), growth in "
               "fortune, and heavy expense offset by gain through "
               "distant connections",
            4: "In its own sign here (Saturn rules the 4th), brings "
               "excellent comfort through mother, land and home, and "
               "success in children and education; its aspects bring "
               "strong influence over rivals, reduced comfort through "
               "father despite real gain and success through career "
               "and state affairs, and growth in physical beauty and "
               "health (exalted), marking a contented, famous, "
               "wealthy and influential nature",
            5: "In its own sign here (Saturn rules the 5th), brings "
               "success in children, education and growth, along with "
               "comfort through mother, land and home; its aspects "
               "bring discord with a spouse and difficulty in daily "
               "business (debilitated), difficulty in income before "
               "eventual success, and difficulty saving wealth "
               "alongside discord with family",
            6: "Enemy's sign brings success over rivals through "
               "intelligence, though comfort through mother, land and "
               "home and success in education and children come only "
               "with difficulty; its aspects bring growth in "
               "longevity and inheritance, heavy expense offset by "
               "gain through distant connections, and some discord "
               "with siblings alongside growth in personal drive",
            7: "Enemy's sign, debilitated, brings difficulty and "
               "disturbance around a spouse, household and business, "
               "along with weakness regarding children and education; "
               "its aspects bring growth in fortune and religious "
               "practice, a tall build and physical comfort "
               "(exalted), and comfort through mother, land and home "
               "gained through real effort",
            8: "Friend's sign brings good gain in longevity and "
               "inheritance, though deficiency regarding mother, "
               "land, home, children and education; its aspects bring "
               "difficulty through father, career and business, "
               "difficulty saving wealth alongside disturbance to "
               "family comfort, and ordinary success with children "
               "through education (own sign)",
            9: "Friend's sign brings advancement in fortune through "
               "intelligence and religious observance, along with "
               "good comfort through education, children, land, home "
               "and mother; its aspects bring obstacles to income, "
               "discord with siblings alongside growth in personal "
               "drive, and victory over rivals through intelligence",
            10: "Enemy's sign brings success through father, career "
                "and business, and renown for learning, though "
                "discord regarding children; its aspects bring heavy "
                "expense offset by gain through distant connections, "
                "comfort through mother, land and home, and some "
                "deficiency in spousal comfort alongside difficulty "
                "in business (debilitated)",
            11: "Enemy's sign brings income that grows well despite "
                "some difficulty, along with excellent comfort "
                "through mother, land and home; its aspects bring "
                "growth in physical strength and presence (exalted), "
                "success in education, intelligence and children, and "
                "growing strength in longevity and inheritance",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, along with deficiency "
                "in comfort through mother, land and home; its "
                "aspects bring difficulty saving wealth alongside "
                "discord with family, ordinary influence maintained "
                "over rivals, and growth in fortune and religious "
                "practice, though with somewhat blunted intelligence "
                "and speech",
        },
        "Rahu": {
            1: "Brings physical weakness and inner distress; the "
               "native leans on secretive method and hard work to "
               "advance, and though facing serious difficulty at "
               "times, wins through by wit and cleverness eventually",
            2: "Brings real difficulty accumulating wealth — sometimes "
               "sudden gain, sometimes sudden financial crisis; the "
               "native manages through secretive method, and faces "
               "some trouble from family too",
            3: "Brings some diminished personal drive, made up for "
               "through cunning and even improper means; trouble from "
               "siblings and other serious crises arise in life, "
               "overcome only through wit, cleverness and personal "
               "effort",
            4: "Brings some deficiency in comfort through mother, "
               "land and home, though the native wins through over "
               "wealth-related crises by secretive method, boldness "
               "and resolve; life remains full of struggle",
            5: "Brings trouble regarding children and difficulty in "
               "education; the native stays perpetually anxious, "
               "pursuing self-interest without much regard for "
               "propriety, working through secretive method while "
               "outwardly projecting great resolve",
            6: "Brings victory over rivals achieved even through "
               "difficulty; the native is bold, courageous, and "
               "skilled in secretive method, succeeding in "
               "establishing personal influence",
            7: "Brings crises regarding the spouse and difficulty in "
               "daily business, sometimes serious; the native "
               "overcomes these obstacles through secretive method, "
               "patience and resolve",
            8: "Brings real setbacks to longevity — though not death "
               "— and loss to inheritance; daily life carries many "
               "struggles, worries and troubles",
            9: "Brings advancement in fortune through secretive "
               "method and continued religious observance, though "
               "obstacles arise from time to time; these too are "
               "overcome through cleverness, effort and secretive "
               "method",
            10: "Brings reduced comfort through father, difficulty in "
                "advancing through career and state affairs, and "
                "crises in business; success comes only after "
                "clearing away every obstacle to advancement",
            11: "Brings difficulty in the path of income, overcome "
                "through secretive method, cleverness, patience and "
                "courage, with continued advancement; occasionally "
                "serious crises must be faced too",
            12: "Brings heavy expense and occasional serious crises, "
                "though also some gain through distant connections; "
                "the native is discerning, principled, hard-working, "
                "patient and courageous",
        },
        "Ketu": {
            1: "Brings occasional serious physical crises, overcome "
               "through secretive daring and courage; despite inner "
               "weakness, the native appears outwardly bold and "
               "resolute",
            2: "Brings serious obstacles to gaining and saving "
               "wealth; earning is achieved only through secretive "
               "method, leaving the native perpetually anxious, with "
               "some trouble from family too, though the native "
               "remains bold and patient",
            3: "Brings great growth in personal drive and real "
               "sibling comfort, though siblings sometimes bring "
               "trouble too; the native is bold, hard-working and "
               "patient",
            4: "Brings some deficiency in comfort through mother, "
               "land and home, and much domestic strife; even so, the "
               "native overcomes difficulty through patience, courage "
               "and secretive method, achieving some success",
            5: "Brings trouble regarding children and difficulty in "
               "education; the native gains only modest success in "
               "education, intelligence and children after many "
               "difficulties, with crises persisting",
            6: "Brings success over disputes, illness and rivals "
               "achieved through real boldness, courage and patience, "
               "without ever losing nerve; the native's maternal-side "
               "connections tend to remain weak",
            7: "Brings real trouble regarding the spouse and serious "
               "difficulty in daily income; the native draws on "
               "patience, courage, effort and secretive method to "
               "achieve some success with the spouse and in business",
            8: "Brings repeated crises to longevity and loss to "
               "inheritance, with some stomach trouble; the native "
               "remains perpetually anxious, yet achieves some "
               "success through courage, patience and secretive "
               "method",
            9: "Brings many obstacles to the advancement of fortune, "
               "and occasionally severe crises; faith in religion "
               "also weakens, and the native does not hesitate to act "
               "against dharma or use improper means for "
               "self-interest, sometimes earning disrepute",
            10: "Brings trouble through the father, difficulty from "
                "state authority, and obstacles in business, with "
                "many ups and downs through life",
            11: "Brings difficulty in the path of income, overcome "
                "through patience, hard work and secretive method to "
                "achieve success; sometimes loss is suffered instead "
                "of gain, and success comes only after weathering "
                "many crises",
            12: "Brings heavy expense offset by some gain through "
                "distant connections; the native manages expenses "
                "through discernment and hard work, though remains "
                "occasionally prone to serious difficulty, achieving "
                "success ultimately",
        },
    },
    "Scorpio": {
        "Sun": {
            1: "Friend's sign brings physical vigour, self-respect, a "
               "quick temper, influence and boldness, along with "
               "comfort, cooperation and honour through father, state "
               "and business; the native is fond of fine clothing and "
               "ornaments, and achieves real fame; its aspect on the "
               "7th brings discord with a spouse and some difficulty "
               "in daily business",
            2: "Friend's sign brings wealth through the father's side "
               "and family comfort, along with gain through state "
               "affairs and business, though some deficiency in "
               "comfort through father; its aspect on the 8th brings "
               "growth in longevity and inheritance, marking a happy, "
               "influential daily life",
            3: "Enemy's sign brings growth in personal drive, though "
               "some deficiency in sibling comfort, along with real "
               "success through father, state and business; its "
               "aspect on the 9th brings growth in fortune and "
               "religious practice, marking a glorious, industrious "
               "nature",
            4: "Enemy's sign brings discord with society, some "
               "deficiency in comfort through land and home, and some "
               "flaws in domestic happiness; its aspect on the 10th "
               "(own sign) brings cooperation, honour, gain and "
               "success through state, father and business, and real "
               "advancement through personal effort",
            5: "Friend's sign brings real success in education, "
               "intelligence and children, along with honour, "
               "cooperation and gain through state, father and "
               "business, and advancement in political life; its "
               "aspect on the 11th brings excellent gain in income, "
               "marking a life lived at a high standard",
            6: "Friend's sign brings victory over rivals and success "
               "through state and business, though some discord with "
               "mother and father; its aspect on the 12th "
               "(debilitated) brings trouble managing expenses, offset "
               "by gain through distant connections",
            7: "Friend's sign brings contentment and strength through "
               "the spouse, along with success in daily business; its "
               "aspect on the Lagna brings a beautiful body and an "
               "influential presence, marking a generous, hard-working, "
               "ever-advancing nature",
            8: "Friend's sign brings growth in longevity and "
               "inheritance, along with success, fame and gain "
               "through father, state and business; its aspect on the "
               "2nd brings real growth in wealth through hard work, "
               "family comfort, and connections extending to distant "
               "places",
            9: "Friend's sign brings advancement in fortune and "
               "religious practice, along with success through "
               "father, state and business; its aspect on the 3rd "
               "brings some discord with siblings, though ordinary "
               "growth in personal drive, marking an untroubled life "
               "overall",
            10: "In its own sign here (Sun rules the 10th), brings "
                "success, cooperation, gain and honour through "
                "father, state and business, and the native strives "
                "to build standing even at some cost to health; its "
                "aspect on the 4th brings discord with mother, and "
                "some deficiency in comfort through land and home",
            11: "Friend's sign brings excellent gain through the "
                "father, along with honour, wealth, gain and "
                "cooperation through state and business; its aspect "
                "on the 5th brings excellent gain through children, "
                "intelligence and education, marking a self-respecting, "
                "quick-tempered, well-regarded and famous nature",
            12: "Debilitated in an enemy's sign brings great "
                "difficulty earning a living, and trouble through "
                "distant connections, along with difficulty through "
                "father, state and business; its aspect on the 6th "
                "(exalted) brings influence established over rivals, "
                "and gain through disputes and litigation",
        },
        "Moon": {
            1: "Friend's sign brings some physical weakness, and fame "
               "achieved only with difficulty; its aspect on the 7th "
               "(exalted) brings a beautiful, agreeable spouse, and "
               "ongoing success in daily business",
            2: "Friend's sign brings success in saving wealth and "
               "family comfort, though religious duty is not properly "
               "kept; its aspect on the 8th brings gain in inheritance "
               "and growth in longevity, marking a wealthy, contented, "
               "fortunate life",
            3: "Enemy's sign brings growth in personal drive, though "
               "some deficiency in sibling comfort, and gives strong "
               "mental power; its aspect on the 9th (own sign) brings "
               "advancement in fortune and religious practice, and "
               "real fame and fortune through personal effort",
            4: "Enemy's sign brings excellent comfort through mother, "
               "land and home despite some dissatisfaction, and "
               "religious observance kept, with fortune advancing "
               "through devotion; its aspect on the 10th brings "
               "comfort, honour, gain and success through father, "
               "state and business",
            5: "Friend's sign brings good success in children, "
               "intelligence and education, and gives a gentle, "
               "humble, sweet-spoken, religious nature that advances "
               "fortune through intelligence; its aspect on the 11th "
               "brings growth in fortune and strong ongoing gain",
            6: "Friend's sign brings success over rivals through a "
               "peaceable policy, though some unrest over wealth "
               "caused by rivals; its aspect on the 12th brings "
               "expenses managed on the strength of fortune, and gain "
               "and success through distant connections",
            7: "Exalted, though in only a friend's sign — brings a "
               "beautiful, fortunate spouse, a joyful domestic life, "
               "success in daily business, and growing fortune and "
               "fame through high morale; its aspect on the Lagna "
               "(debilitated) brings some bodily weakness, and some "
               "deficiency in fortune and religious practice",
            8: "Friend's sign brings growth in longevity and gain in "
               "inheritance; its aspect on the 2nd brings real gain in "
               "wealth and family comfort, marking a calm, wealthy, "
               "cheerful, famous nature",
            9: "In its own sign here (Moon rules the 9th), brings "
               "real advancement in fortune and religious practice, "
               "marking a famous, wealthy life; its aspect on the 3rd "
               "brings flawed comfort through siblings, though great "
               "growth in personal drive",
            10: "Friend's sign brings great success through father, "
                "state and business, marking a righteous, fortunate "
                "nature; its aspect on the 4th brings some deficiency "
                "in comfort through mother, land and home, though the "
                "native remains happy, famous, content and wealthy "
                "overall",
            11: "Friend's sign brings excellent, ongoing gain, "
                "marking a righteous, fortunate, contented, famous "
                "nature; its aspect on the 5th brings excellent gain "
                "through education, intelligence and children, "
                "forceful speech, and high morale",
            12: "Friend's sign brings heavy expense, though not felt "
                "as a real burden, along with strong gain through "
                "distant connections, and fortune that stays weak at "
                "home though it improves abroad; its aspect on the "
                "6th brings success over rivals achieved through "
                "strength, and advancement through the power of "
                "fortune over difficulty",
        },
        "Mars": {
            1: "In its own sign here (Mars is Lagna-lord and rules "
               "the 6th), brings growth in physical strength and "
               "success over rivals; its aspects bring some "
               "deficiency in comfort through mother, land and home, "
               "success with a spouse and in business achieved with "
               "some difficulty, and growth in longevity and "
               "inheritance",
            2: "Friend's sign brings wealth earned through physical "
               "labour and family comfort despite some worry, though "
               "some deficiency in physical beauty and health, with "
               "influence maintained over rivals; its aspects bring "
               "success in education and children, growth in "
               "longevity and inheritance, and loss to fortune and "
               "religious observance with diminished fame (debilitated)",
            3: "Enemy's sign, exalted, brings growth in personal "
               "drive, though ordinary discord with siblings; its "
               "aspects bring victory over rivals (own sign), "
               "religious duty not properly kept with greater reliance "
               "on personal effort than on fortune (debilitated), and "
               "comfort, cooperation, gain and honour through father, "
               "state and business",
            4: "Enemy's sign brings some deficiency in comfort "
               "through mother, land and home; its aspects bring some "
               "discord-tinged comfort through a spouse though "
               "success in daily business, comfort, success, gain and "
               "fame through father, state and business, and "
               "excellent income",
            5: "Friend's sign brings success in education and "
               "children achieved with some difficulty, and calls for "
               "deep strategy to prevail over rivals; its aspects "
               "bring growth in longevity and inheritance, strong "
               "income, and heavy expense offset by gain through "
               "distant connections despite difficulty",
            6: "In its own sign here (Mars rules the 6th), brings "
               "success over rivals; its aspects bring loss to "
               "fortune and religion with diminished standing "
               "(debilitated), heavy expense offset by gain through "
               "distant connections, and growth of physical vigour "
               "and self-confidence (own sign)",
            7: "Enemy's sign brings some trouble around the spouse, "
               "disorder of the reproductive organs, and some "
               "difficulty in daily business; its aspects bring "
               "comfort, honour and success through father, state and "
               "business, growth of physical vigour and a developed "
               "personality (own sign), and family and wealth comfort "
               "gained through effort, marking a generally comfortable "
               "life",
            8: "Friend's sign brings some deficiency in physical "
               "beauty and comfort, some loss in longevity and "
               "inheritance, stomach trouble, and some trouble from "
               "rivals; its aspects bring good income, wealth and "
               "family comfort gained through special effort, and "
               "strong sibling comfort with growth in personal drive "
               "(exalted)",
            9: "Friend's sign, debilitated, brings some loss to "
               "fortune and religion, with fortune's advance "
               "disturbed by conflict with rivals though the native "
               "is generally wealthy; its aspects bring heavy expense "
               "offset by gain through distant connections, growth in "
               "personal drive and sibling comfort (exalted), and "
               "some deficiency in comfort through mother, land and "
               "home",
            10: "Friend's sign brings success, cooperation, gain and "
                "honour through father, state and business achieved "
                "with some difficulty, and victory over rivals; its "
                "aspects bring strong physical vigour (own sign), "
                "some deficiency in comfort through mother, land and "
                "home, and success in education, intelligence and "
                "children",
            11: "Friend's sign brings real gain through physical "
                "effort, though some trouble from rivals and "
                "occasional illness; its aspects bring growth in "
                "wealth and family comfort, success in education, "
                "intelligence and children achieved with some "
                "difficulty, and victory over rivals with gain from "
                "maternal-side connections (own sign)",
            12: "Enemy's sign brings heavy expense, offset by comfort "
                "and peace through distant connections; its aspects "
                "bring growth in sibling comfort and personal drive "
                "(exalted), victory over rivals (own sign), and some "
                "discord with a spouse though comfort achieved, with "
                "some difficulty though gain in daily business",
        },
        "Mercury": {
            1: "Friend's sign brings growth in physical presence, and "
               "gain in longevity and strength; its aspect on the 7th "
               "brings some difficulty though real cooperation gained "
               "through a spouse, and success in daily business "
               "achieved only through effort",
            2: "Friend's sign brings excellent comfort through wealth "
               "and family; its aspect on the 8th brings growth in "
               "longevity and gain in inheritance, marking a life "
               "lived with pomp and grandeur",
            3: "Friend's sign brings growth in personal drive and "
               "sibling comfort, along with gain in longevity and "
               "inheritance; its aspect on the 9th brings advancement "
               "in fortune and religious practice through one's own "
               "discernment, marking a happy, wealthy, righteous and "
               "courageous life",
            4: "Friend's sign brings comfort through mother, land and "
               "home, along with growth in longevity and inheritance; "
               "its aspect on the 10th brings comfort, success, gain "
               "and fame through father, state and business, achieved "
               "with some difficulty",
            5: "Debilitated in a friend's sign brings trouble "
               "regarding education, intelligence and children though "
               "real gain through one's own discernment, along with "
               "some trouble around longevity and only modest gain in "
               "inheritance; its aspect on the 11th (own sign, "
               "exalted) brings excellent income, marking a life full "
               "of comfort",
            6: "Friend's sign brings victory over rivals, income "
               "that grows with some difficulty, and gain in "
               "longevity and inheritance; its aspect on the 12th "
               "brings heavy expense offset by gain through distant "
               "connections",
            7: "Friend's sign brings success with a spouse and in "
               "daily business, along with gain in longevity and "
               "inheritance; its aspect on the Lagna (own sign) "
               "brings growth of physical strength and influence, "
               "marking a life lived with pomp and grandeur",
            8: "In its own sign here (Mercury rules the 8th), brings "
               "growth in longevity and gain in inheritance; its "
               "aspect on the 2nd brings wealth saved through one's "
               "own discernment and family comfort, marking a life of "
               "comfort and luxury",
            9: "Friend's sign brings advancement in fortune and "
               "religious practice, along with gain in longevity and "
               "inheritance; its aspect on the 3rd brings sibling "
               "comfort with some deficiency, and growth in personal "
               "drive, marking a generally happy, fortunate life",
            10: "Friend's sign brings success, honour and standing "
                "through father, state and business achieved with "
                "some difficulty, along with gain in longevity and "
                "inheritance; its aspect on the 4th brings comfort "
                "through mother, land and home achieved with some "
                "difficulty",
            11: "Exalted, in its own sign here (Mercury rules the "
                "11th), brings excellent income, along with growth in "
                "longevity and gain in inheritance; its aspect on the "
                "5th brings success in education, intelligence and "
                "children achieved with some difficulty, though gives "
                "a somewhat blunt temperament",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, along with growing "
                "strength in longevity and inheritance; its aspect on "
                "the 6th brings success over rivals achieved through "
                "discernment and humility, though the mind stays "
                "somewhat restless and life remains wandering",
        },
        "Jupiter": {
            1: "Friend's sign brings physical strength and standing; "
               "its aspects bring excellent success in education, "
               "intelligence and children (own sign), some discord "
               "with a spouse though ordinary difficulty in daily "
               "business gives way to gain in time, and real "
               "advancement in fortune and religious practice "
               "(exalted)",
            2: "In its own sign here (Jupiter rules the 2nd), brings "
               "wealth and family comfort, though some deficiency "
               "regarding children; its aspects bring success over "
               "rivals through intelligence, growth in longevity and "
               "inheritance, and success, honour and fame through "
               "state, father and business",
            3: "Enemy's sign brings trouble in sibling comfort and "
               "some deficiency in personal drive, education, wealth "
               "and family comfort; its aspects bring some discord "
               "with a spouse and success in business achieved only "
               "with difficulty, advancement in fortune and religion "
               "(exalted), and excellent growth in income",
            4: "Enemy's sign brings some discord with mother, comfort "
               "through land and home, and success in education and "
               "children achieved with some difficulty; its aspects "
               "bring gain in longevity and inheritance, gain, "
               "cooperation, honour and success through father, state "
               "and business, and heavy expense with only ordinary "
               "gain through distant connections",
            5: "In its own sign here (Jupiter rules the 5th), brings "
               "excellent success in education, intelligence and "
               "children, along with wealth and family comfort; its "
               "aspects bring real advancement in fortune and "
               "religion (exalted), excellent income, and growth of "
               "physical beauty, strength, honour, standing and fame",
            6: "Friend's sign brings success over rivals through "
               "intelligence, though caught up in disputes over "
               "wealth and family, along with deficiency regarding "
               "education and children; its aspects bring gain, "
               "comfort and honour through father, state and "
               "business, heavy expense offset by gain through "
               "distant connections, and growth in wealth and family "
               "despite some discord (own sign)",
            7: "Enemy's sign brings excellent comfort through a "
               "spouse despite ordinary discord, along with success "
               "in business; its aspects bring excellent income, "
               "growth of physical beauty, strength, honour, standing "
               "and fame (own sign), and some deficiency in sibling "
               "comfort and personal drive (debilitated)",
            8: "Friend's sign brings excellent gain in longevity and "
               "inheritance, though deficiency in education, "
               "intelligence, children, wealth and family comfort; "
               "its aspects bring heavy expense with some gain "
               "through distant connections, growth in wealth and "
               "family comfort (own sign), and comfort through "
               "mother, land and home achieved with some difficulty",
            9: "Exalted in a friend's sign, brings advancement in "
               "fortune and religious practice, along with wealth and "
               "family comfort; its aspects bring growth of physical "
               "presence and honour, some deficiency in sibling "
               "comfort and personal drive (debilitated), and real "
               "advancement for children and education (own sign), "
               "marking a famous life",
            10: "Friend's sign brings comfort, gain, success and "
                "fame through father, state and business; its "
                "aspects bring growth in wealth and family comfort, "
                "some dissatisfaction in comfort through mother, land "
                "and home, and success and victory over rivals "
                "through intelligence",
            11: "Friend's sign brings growth in income, along with "
                "wealth and family comfort; its aspects bring some "
                "deficiency in sibling comfort and personal drive "
                "(debilitated), real advancement for education, "
                "intelligence and children (own sign), and some "
                "discord-tinged gain through a spouse with some "
                "difficulty though success in daily business",
            12: "Enemy's sign brings heavy expense, weak distant "
                "connections, and some deficiency in wealth, family, "
                "education and children; its aspects bring some "
                "deficiency in comfort through mother, land and home, "
                "success over rivals through cleverness, and good "
                "strength in longevity and inheritance; the native "
                "generally keeps an unsettled mind",
        },
        "Venus": {
            1: "Enemy's sign brings some physical weakness, though "
               "growth in influence, cleverness and skill; its aspect "
               "on the 7th (own sign) brings comfort through a spouse "
               "and ongoing success in daily business, though as 12th "
               "lord some ordinary difficulty persists in these "
               "spheres too",
            2: "Enemy's sign brings some trouble regarding wealth and "
               "family comfort, though gain in wealth is achieved "
               "too; its aspect on the 8th brings growth in longevity "
               "though only modest gain in inheritance, marking a "
               "generally wealthy, clever nature",
            3: "Friend's sign brings some deficiency in sibling "
               "comfort and personal drive, heavy expense offset by "
               "gain through distant connections, and some deficiency "
               "regarding the spouse; its aspect on the 9th brings "
               "some deficiency in fortune's advance, with religious "
               "duty kept only in small measure",
            4: "Friend's sign brings some deficiency in comfort "
               "through mother, land and home, and some weakness "
               "regarding the spouse, along with comfort through "
               "distant connections and smoothly managed expenses; "
               "its aspect on the 10th brings gain, comfort, fame and "
               "success through father, state and business achieved "
               "after some difficulty",
            5: "Exalted, though in an enemy's sign, brings success in "
               "education and children achieved with some deficiency, "
               "though the native masters some particular skill, "
               "lives under a spouse's influence, and is eloquent, "
               "with strength and gain through distant connections "
               "too; its aspect on the 11th (debilitated) brings some "
               "difficulty in the path of income",
            6: "Enemy's sign brings victory over rivals through "
               "peaceable means, though some difficulty running the "
               "household; its aspect on the 12th (own sign) brings "
               "ordinary gain through hard work via distant "
               "connections, along with heavy expense",
            7: "In its own sign here (Venus rules the 7th), brings "
               "excellent success with a spouse and in daily "
               "business, with distant connections helping manage "
               "expenses, and gives a highly intelligent nature; its "
               "aspect on the Lagna brings some physical weakness, "
               "though the native remains famous, influential and "
               "capable",
            8: "Friend's sign brings crisis and difficulty regarding "
               "longevity and inheritance, and the same for a spouse "
               "and business, though success comes through secretive "
               "skill and hard work; its aspect on the 2nd brings "
               "difficulty saving wealth and in family comfort, and "
               "the native protects their standing only through great "
               "cleverness",
            9: "Enemy's sign brings difficulty advancing fortune and "
               "keeping religious duty, and trouble regarding the "
               "spouse, though the native manages through great "
               "cleverness and gains from distant connections; its "
               "aspect on the 3rd brings an unsatisfying state "
               "regarding siblings and personal drive",
            10: "Enemy's sign brings success through father, state "
                "and business achieved with some difficulty, along "
                "with some deficiency regarding the spouse and daily "
                "business; its aspect on the 4th brings comfort and "
                "cooperation through mother, land and home",
            11: "Debilitated in a friend's sign brings diminished "
                "income and an unsatisfying state regarding the "
                "spouse and daily business, though distant "
                "connections bring some gain through cleverness; its "
                "aspect on the 5th (exalted) brings strength in "
                "education and intelligence, though some weakness "
                "regarding children",
            12: "In its own sign here (Venus rules the 12th), brings "
                "heavy expense offset by gain through distant "
                "connections, along with some trouble regarding the "
                "spouse and daily business; its aspect on the 6th "
                "brings some difficulty over rivals before eventual "
                "success",
        },
        "Saturn": {
            1: "Enemy's sign brings a temperament that is both calm "
               "and fierce by turns, along with ordinary comfort "
               "through mother, land and home; its aspects bring "
               "growth in personal drive and sibling comfort (own "
               "sign), success with a spouse and in daily business, "
               "and discord with the father alongside success through "
               "state and business achieved only after difficulty",
            2: "Enemy's sign brings ordinary wealth and family "
               "comfort, though some deficiency in sibling comfort; "
               "its aspects bring comfort through mother, land and "
               "home (own sign), growth in longevity and inheritance, "
               "and excellent growth in income, marking a happy, "
               "wealthy life",
            3: "In its own sign here (Saturn rules the 3rd), brings "
               "sibling comfort, growth in personal drive, and "
               "comfort through mother, land and home; its aspects "
               "bring success in children and education achieved "
               "with some difficulty, advancement in fortune achieved "
               "with some difficulty and religious duty kept despite "
               "some discord, and expenses running smoothly offset by "
               "gain through distant connections (exalted)",
            4: "In its own sign here (Saturn rules the 4th), brings "
               "excellent comfort through mother, land and home, and "
               "growth in sibling comfort and personal drive; its "
               "aspects bring some trouble from rivals (debilitated), "
               "some discord with father though real comfort gained "
               "and success through state and business, and growth "
               "of physical beauty and health",
            5: "Enemy's sign brings comfort through children though "
               "with some discord, adequate education, discord with "
               "mother, and only ordinary comfort through land and "
               "home; its aspects bring full comfort and success "
               "through a spouse and business, good income, and "
               "discord in the family with no real savings despite "
               "great effort",
            6: "Enemy's sign brings success over rivals achieved "
               "through strategy, though only slight comfort through "
               "mother, land and home; its aspects bring gain in "
               "longevity and inheritance, heavy expense offset by "
               "gain through distant connections (exalted), and "
               "growth in personal drive though some strain in "
               "family comfort (own sign)",
            7: "Friend's sign brings success and comfort through a "
               "spouse and in daily business; its aspects bring "
               "advancement in fortune and religion achieved with "
               "some difficulty, some deficiency in physical beauty "
               "and heavier labour required, and full comfort through "
               "mother, land and home (own sign), marking an "
               "influential, cheerful daily life",
            8: "Friend's sign brings gain in longevity and "
               "inheritance, though real deficiency in comfort "
               "through father, land, home and siblings; its aspects "
               "bring discord with father alongside loss through "
               "state and business, difficulty saving wealth and "
               "discord with family, and an incomplete state "
               "regarding education, intelligence and children",
            9: "Enemy's sign brings advancement in fortune achieved "
               "with some difficulty and religious duty kept despite "
               "some difficulty, along with comfort through mother, "
               "land and home; its aspects bring excellent income and "
               "good gain in wealth, sibling comfort and growth in "
               "personal drive, and trouble from rivals with weak "
               "maternal-side connections (debilitated)",
            10: "Enemy's sign brings success, cooperation and honour "
                "through father, state and business achieved with "
                "some difficulty, along with some deficiency in "
                "sibling comfort though growth in personal drive; its "
                "aspects bring heavy expense offset by gain through "
                "distant connections, some discord with mother though "
                "comfort through land and home (own sign), and real "
                "success through a spouse and business, marking a "
                "comfortable domestic life",
            11: "Friend's sign brings excellent growth in income, "
                "along with excellent comfort through siblings, "
                "mother, land and home, and growth in personal drive; "
                "its aspects bring some diminishment of physical "
                "beauty, some difficulty around education and "
                "children, and long life with gain in inheritance",
            12: "Exalted in a friend's sign, brings heavy expense "
                "offset by comfort and gain through distant "
                "connections, along with some deficiency in comfort "
                "through siblings, mother and home; its aspects bring "
                "difficulty saving wealth alongside discord with "
                "family, trouble from rivals (debilitated), and gain "
                "in longevity and inheritance; the native is not "
                "especially wealthy, though lives in comfortable style",
        },
        "Rahu": {
            1: "Brings some hidden trouble or anxiety in the body, "
               "and occasionally affliction serious enough to "
               "threaten life; the native works hard for advancement "
               "and relies on secretive method, and has a sharp "
               "temperament, is somewhat selfish, and attractive in "
               "appearance",
            2: "Brings real difficulty earning wealth, and constant "
               "worry regarding family; despite many secretive "
               "strategies the native remains in debt, and worries "
               "are never fully resolved",
            3: "Brings great growth in personal drive and real "
               "sibling comfort, though accompanied by constant "
               "worry over siblings; the native is clever, "
               "courageous, patient, unusually daring and hard-working",
            4: "Brings some deficiency in comfort through mother, "
               "land and home, and occasional family crises resolved "
               "only through secretive method, courage and patience; "
               "the native is discerning and hard-working",
            5: "Brings difficulty in education and regarding "
               "children, with some success following later; the "
               "native is clever, skilled in secretive method, and "
               "constantly anxious though never revealing their "
               "troubles to others",
            6: "Brings a strong hold over rivals and victory over "
               "them; the native prevails over every kind of "
               "difficulty through secretive skill, patience, "
               "courage, hard work and strategy, and never loses nerve",
            7: "Brings difficulty regarding a spouse and business, "
               "sometimes serious crises through either; the native "
               "overcomes all such difficulty through courage, "
               "strategy, cleverness and patience",
            8: "Brings gain in inheritance and growth in longevity; "
               "a life full of energy and enthusiasm, lived in style, "
               "though occasional loss must be borne; the native "
               "achieves real fame",
            9: "Brings great obstacles to the advancement of "
               "fortune, and little faith in religious observance; "
               "the native is beset by mental anxiety and sometimes "
               "falls into despair, gaining only modest success in "
               "the end after much hardship",
            10: "Brings trouble through the father, and difficulty "
                "through state and business too; the native "
                "sometimes falls into deep despair, though "
                "ultimately achieves some advancement through "
                "patience, courage and cleverness",
            11: "Brings great success in the field of income, though "
                "the native gives no thought to propriety in pursuit "
                "of greater profit; the native is fearful yet "
                "selfish and clever, sometimes gaining suddenly, "
                "sometimes suffering sudden heavy loss",
            12: "Brings heavy expense and resulting trouble, along "
                "with some gain through distant connections despite "
                "difficulty; the native suffers both sudden gain and "
                "sudden loss of wealth, and various other hardships "
                "too",
        },
        "Ketu": {
            1: "Brings repeated injury to the body and some "
               "diminishment of physical beauty; the native has a "
               "fierce temperament, a weak mind, and undertakes hard "
               "physical labour, often left with a lasting mark or "
               "scar from injury",
            2: "Brings effort toward earning wealth, with occasional "
               "sudden gain too; some deficiency in family comfort; "
               "the native stays constantly alert to protect their "
               "standing",
            3: "Brings great growth in personal drive, though some "
               "trouble through siblings; success is achieved in "
               "disputes and conflicts; the native is bold, "
               "hard-working, patient and courageous",
            4: "Brings trouble through the mother, and some "
               "deficiency in comfort through land and home; the mind "
               "stays restless; some peace comes only after hard "
               "effort, and moving abroad brings some comfort, though "
               "the home itself stays somewhat unsettled",
            5: "Brings difficulty in education and trouble regarding "
               "children; the native is bold, resolute, skilled in "
               "secretive method, patient and fearless, never "
               "revealing hidden worries to others",
            6: "Brings a strong hold over rivals; the native "
               "prevails over quarrels and difficulties through "
               "courage, secretive skill, patience, hard work and "
               "daring, though maternal-side connections stay weak",
            7: "Brings real trouble regarding a spouse, with many "
               "crises in domestic life and real difficulty in daily "
               "business; the native manages to resolve these "
               "difficulties only through secretive skill, patience "
               "and courage",
            8: "Brings repeated affliction serious enough to "
               "threaten life, and loss to inheritance; the native "
               "works hard for a livelihood and relies on secretive "
               "method, though finds no clean solution to these "
               "crises",
            9: "Brings great obstacles to the advancement of "
               "fortune, and loss to religious standing; the native "
               "lives in constant anxiety and occasionally faces "
               "severe crises, and even secretive method and hard "
               "work bring no real success to fortune",
            10: "Brings trouble through the father, loss of standing "
                "in state affairs, and severe crises in business; the "
                "native ultimately gains some relief through "
                "patience, courage and secretive method, though life "
                "is never lived in real comfort",
            11: "Brings good income, with occasional sudden gain and "
                "occasional crisis too; the native is clever, "
                "selfish, sharp and self-interested, never satisfied "
                "with their earnings",
            12: "Brings heavy expense, offset by gain through "
                "distant connections; the native manages expenses "
                "through secretive skill, cleverness and hard work, "
                "though occasionally faces severe crises, never "
                "abandoning their patience regardless",
        },
    },
    "Sagittarius": {
        "Sun": {
            1: "Friend's sign, at the Lagna itself, brings an "
               "excellent, powerful body, and gives a fortunate, "
               "devout, religious-minded nature; its aspect on the "
               "7th brings the cooperation of a beautiful spouse, "
               "domestic happiness, and gain in daily business",
            2: "Enemy's sign brings excellent success in "
               "accumulating wealth despite some difficulty, and "
               "family comfort despite some discord, and the native "
               "keeps religious duty mainly for self-interest; its "
               "aspect on the 8th brings growth in longevity and "
               "gain in inheritance, marking good fortune overall",
            3: "Enemy's sign brings sibling comfort with some "
               "dissatisfaction, and real growth in personal drive; "
               "its aspect on the 9th (own sign) brings great "
               "advancement in fortune through personal effort, along "
               "with religious observance, marking a bold, famous "
               "nature",
            4: "Friend's sign brings abundant comfort through "
               "mother, and comfort through land and home too, along "
               "with advancement in fortune and religious practice; "
               "its aspect on the 10th brings ongoing opportunities "
               "for cooperation, honour, gain and success through "
               "father, state and business",
            5: "Exalted in a friend's sign, brings excellent gain "
               "through children, education and intelligence, "
               "marking a learned, religious, wise, intelligent "
               "nature; its aspect on the 11th (debilitated) brings "
               "difficulty in the field of income, and limits real "
               "advancement despite eloquence, courtesy and decency",
            6: "Enemy's sign brings a strong hold over rivals and "
               "gain through disputes, though little real interest "
               "in religious observance; its aspect on the 12th "
               "brings heavy expense offset by gain through distant "
               "connections, which in turn helps fortune along",
            7: "Friend's sign brings comfort through a spouse and "
               "ongoing success in daily business, marking a "
               "fortunate, devout nature; its aspect on the Lagna "
               "brings excellent physical comfort and an influential "
               "presence, though gives the spouse a somewhat hot "
               "temper",
            8: "Friend's sign brings growth in longevity and gain in "
               "inheritance, and an influential daily life, though "
               "many obstacles to fortune's advance; its aspect on "
               "the 2nd brings some deficiency in accumulating wealth "
               "and in family comfort",
            9: "In its own sign here (Sun rules the 9th), brings "
               "great advancement in fortune and religious practice, "
               "marking a famous, influential nature; its aspect on "
               "the 3rd brings some deficiency in personal drive, and "
               "some discord with siblings, and gives a "
               "fortune-dependent temperament",
            10: "Friend's sign brings excellent cooperation through "
                "the father, and success through state and business, "
                "marking a fortunate nature inclined to financial "
                "thinking; its aspect on the 4th brings ample comfort "
                "through mother, land and home, and real fame and "
                "standing",
            11: "Debilitated in an enemy's sign brings good growth "
                "in income despite some difficulty; its aspect on "
                "the 5th (exalted, and a friend's sign) brings ample "
                "success in education, intelligence and children, "
                "marking a virtuous, learned, gentle, sweet-spoken, "
                "contented nature",
            12: "Friend's sign brings heavy expense offset by "
                "success and gain through distant connections after "
                "some delay, with little interest in religious duty "
                "though the native spends generously on charity; its "
                "aspect on the 6th brings a strong hold over rivals, "
                "and victory and gain through disputes and litigation",
        },
        "Moon": {
            1: "Friend's sign, as 8th lord, brings growth in "
               "longevity and gain in inheritance, along with a "
               "beautiful, healthy body; its aspect on the 7th brings "
               "comfort through a spouse achieved with some "
               "difficulty, and some difficulty regarding daily income",
            2: "Enemy's sign brings difficulty saving wealth, and "
               "some deficiency in family comfort, though the native "
               "lives in a dignified style; its aspect on the 8th "
               "brings growth in longevity and inheritance, along "
               "with some restlessness of mind",
            3: "Enemy's sign brings some deficiency in sibling "
               "comfort, calling for special effort to grow one's "
               "personal drive, along with gain in longevity and "
               "inheritance; its aspect on the 9th brings growth in "
               "fortune and religious practice achieved with some "
               "difficulty, marking a generally fortunate though "
               "struggle-filled life",
            4: "Friend's sign brings some deficiency in comfort "
               "through mother, sometimes requiring the native to "
               "live away from their native land, along with gain in "
               "longevity and inheritance, and an influential daily "
               "life; its aspect on the 10th brings success through "
               "father, state and business achieved with some "
               "difficulty",
            5: "In Mars's sign, as 8th lord, brings some difficulty "
               "in education, intelligence and children, along with "
               "gain in longevity and inheritance, though the mind "
               "stays anxious; its aspect on the 11th brings only "
               "ordinary success in income after real difficulty",
            6: "Exalted, though in an enemy's sign, brings a strong "
               "hold over rivals, along with gain in longevity and "
               "inheritance; its aspect on the 12th (debilitated) "
               "brings trouble over expenses, and distant connections "
               "proving unhelpful, with some mental strain caused by "
               "rivals",
            7: "Friend's sign brings gain in longevity and "
               "inheritance, some difficulty regarding a spouse, and "
               "some difficulty in daily business, along with a "
               "generally pleasant daily life; its aspect on the "
               "Lagna brings growth in physical beauty, though not "
               "robust health, and low stamina for exertion",
            8: "In its own sign here (Moon rules the 8th), brings "
               "growth in longevity and ample gain in inheritance, "
               "marking a grand daily life; its aspect on the 3rd "
               "brings worry over wealth, and some deficiency in "
               "family comfort",
            9: "Friend's sign brings some trouble in fortune's "
               "advance and diminished fame, with religious duty not "
               "fully kept, though gain in longevity and inheritance; "
               "its aspect on the 3rd brings some discord with "
               "siblings, and personal drive that does not grow as it "
               "should, marking an otherwise ordinary life",
            10: "Friend's sign brings some difficulty through "
                "father, state and business, though gain in longevity "
                "and inheritance which keeps life comfortable "
                "overall; its aspect on the 4th brings some "
                "deficiency and trouble in comfort through mother, "
                "land and home",
            11: "Enemy's sign brings gain achieved along with some "
                "difficulty, and excellent strength in longevity and "
                "inheritance, along with a joyful daily life; its "
                "aspect on the 5th brings some deficiency in "
                "education, intelligence and children, and a mind "
                "full of worry",
            12: "Friend's sign, debilitated, brings great difficulty "
                "regarding expenses, and trouble through distant "
                "connections, along with loss to longevity and "
                "inheritance, and an unsettled daily life; its aspect "
                "on the 6th (exalted) brings a strong hold over "
                "rivals, and real victory in disputes and litigation",
        },
        "Mars": {
            1: "Friend's sign brings good physical strength and an "
               "industrious nature, along with gain through "
               "education, children and distant connections; its "
               "aspects bring some deficiency in comfort through "
               "mother, land and home, some deficiency though gain "
               "through a spouse and business, and a weak field of "
               "longevity and inheritance (debilitated)",
            2: "Enemy's sign brings ordinary savings and some "
               "deficiency in family comfort; its aspects bring "
               "strength in education and children (own sign), some "
               "deficiency in longevity and inheritance (debilitated), "
               "and some advancement in fortune achieved after real "
               "difficulty, with religious duty kept only partly",
            3: "Enemy's sign brings growth in personal drive, though "
               "some deficiency in sibling comfort, education and "
               "children; its aspects bring victory over rivals, "
               "advancement in fortune and religious practice, and "
               "variable, moderate success through father, state and "
               "business, marking a life of real ups and downs",
            4: "Friend's sign brings loss to comfort through mother, "
               "land and home, along with weak education and "
               "children; its aspects bring some difficulty around a "
               "spouse and daily business, some deficiency though "
               "success through father, state and business, and "
               "income grown through intelligence offset by gain "
               "through distant connections",
            5: "In its own sign here (Mars rules the 12th), brings "
               "some success in education and children only after "
               "difficulty; its aspects bring some deficiency in "
               "longevity along with stomach trouble (debilitated), "
               "some success in income through intelligence, and "
               "heavy expense offset by real gain through distant "
               "connections (own sign)",
            6: "Enemy's sign brings success over rivals, though weak "
               "children and education; its aspects bring "
               "advancement in fortune and religious practice "
               "achieved with some difficulty, heavy expense and "
               "difficulty through distant connections, and some "
               "deficiency in physical beauty and health with mental "
               "strain",
            7: "Friend's sign brings trouble regarding a spouse, and "
               "loss in business, though good distant connections "
               "keep expenses manageable; its aspects bring ordinary "
               "success through father, state and business, some "
               "physical weakness, and good wealth and family comfort "
               "(exalted)",
            8: "Friend's sign, debilitated, brings some deficiency "
               "in longevity and inheritance, stomach trouble, mental "
               "strain, trouble regarding children, and weak "
               "education; its aspects bring growth in income through "
               "hard work, ordinary wealth and family comfort "
               "(exalted), and growth in personal drive alongside "
               "conflict with siblings",
            9: "Friend's sign brings advancement in fortune and "
               "religious practice, along with some deficiency though "
               "success in education and children; its aspects bring "
               "heavy expense managed through distant connections, "
               "conflict with siblings alongside diminished personal "
               "drive, and comfort through mother, land and home "
               "achieved with some deficiency",
            10: "Friend's sign brings success through state affairs "
                "achieved through intelligence, though loss through "
                "father and business; its aspects bring some "
                "deficiency in physical beauty and health, comfort "
                "through mother, land and home achieved with some "
                "deficiency, and excellent gain in education and "
                "intelligence though weak children (own sign)",
            11: "Enemy's sign brings real growth in income, along "
                "with heavy expense offset by gain from distant "
                "connections after some difficulty; its aspects "
                "bring wealth saved through hard work with family "
                "comfort gained, gain through education and children "
                "(own sign), and influence over rivals with gain and "
                "victory through disputes",
            12: "In its own sign here (Mars rules the 12th), brings "
                "heavy expense offset by gain through distant "
                "connections, along with some physical weakness; its "
                "aspects bring conflict with siblings alongside "
                "growth in personal drive, victory over rivals with "
                "gain through disputes, and trouble regarding a "
                "spouse with difficulty in business",
        },
        "Mercury": {
            1: "Friend's sign brings excellent physical presence and "
               "sound judgement, along with success through father, "
               "state and business; its aspect on the 7th (own sign) "
               "brings a beautiful spouse, wealth through in-laws, "
               "and excellent daily income",
            2: "Friend's sign brings excellent comfort through "
               "wealth and family, along with gain through father, "
               "state and business, though some deficiency regarding "
               "a spouse; its aspect on the 8th brings gain in "
               "longevity and inheritance, marking a joyful, grand "
               "daily life",
            3: "Friend's sign brings growth in personal drive and "
               "excellent sibling comfort, and success in every "
               "sphere through personal effort; its aspect on the 9th "
               "brings ongoing growth in fortune and religious "
               "practice",
            4: "Debilitated in a friend's sign brings some "
               "deficiency in comfort through mother, land and home, "
               "along with difficulty regarding a spouse and domestic "
               "happiness; its aspect on the 10th (own sign, exalted) "
               "brings strength and success through father, state and "
               "business achieved with some difficulty",
            5: "Friend's sign brings excellent gain through "
               "education, intelligence and children, with "
               "advancement through spouse, home, father, state and "
               "business too; its aspect on the 11th brings excellent "
               "income, marking a clever, intelligent, famous "
               "conversationalist",
            6: "Friend's sign brings success over rivals, though "
               "loss through father, state and business, with gain "
               "from maternal-side connections; its aspect on the "
               "12th brings heavy expense offset by gain through "
               "distant connections",
            7: "In its own sign here (Mercury rules the 7th), brings "
               "a beautiful spouse and gain through her, along with "
               "success in daily business, and cooperation and "
               "honour through state and education; its aspect on "
               "the Lagna brings growth in physical beauty and "
               "influence",
            8: "Enemy's sign brings strength in longevity and "
               "inheritance, though occasional heavy loss and "
               "difficulty through father, state and business, with "
               "a generally grand lifestyle; its aspect on the 2nd "
               "brings special effort needed for wealth and family "
               "growth",
            9: "Friend's sign brings an unusually fortunate, "
               "religious nature, and real success through father, "
               "state, business and a spouse alike, marking excellent "
               "wealth and honour earned through discernment; its "
               "aspect on the 3rd brings excellent sibling comfort "
               "and great growth in personal drive",
            10: "Exalted in its own sign here (Mercury rules the "
                "10th), brings great success through father, state "
                "and business, and ample fame, wealth and honour; its "
                "aspect on the 4th brings some deficiency in comfort "
                "through mother, land and home",
            11: "Friend's sign brings excellent income, along with "
                "ample comfort, fame, wealth, gain and honour through "
                "father, state, business and a spouse; its aspect on "
                "the 5th brings excellent comfort through education, "
                "intelligence and children, marking a wealthy, happy, "
                "learned, famous nature",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, though loss of comfort "
                "through father, state and a spouse, and loss in "
                "business conducted from one's native place; its "
                "aspect on the 6th brings success over rivals and in "
                "disputes and litigation",
        },
        "Jupiter": {
            1: "In its own sign here (Jupiter is Lagna-lord), brings "
               "excellent physical comfort and beauty, along with "
               "comfort through land and home; its aspects bring "
               "success in education, intelligence and children, "
               "comfort through a spouse and in business, and "
               "advancement in fortune and religious practice, "
               "marking a learned, capable, handsome, wealthy, "
               "righteous, sweet-spoken, decent and cheerful nature",
            2: "Enemy's sign brings loss to wealth and family "
               "comfort, and some deficiency in physical comfort and "
               "beauty, along with weak comfort through mother, land "
               "and home; its aspects bring influence over rivals "
               "with success in disputes through intelligence, gain "
               "in longevity and inheritance (exalted), and comfort, "
               "honour, fame and success through father, state and "
               "business",
            3: "Enemy's sign brings some deficiency though real gain "
               "in sibling comfort, along with weak education and "
               "children; its aspects bring a beautiful spouse with "
               "comfort and success through her and in business, "
               "advancement in fortune and religious practice, and "
               "some success in income achieved despite difficulty",
            4: "In its own sign here (Jupiter rules the 4th), brings "
               "excellent comfort through mother, land and home, "
               "along with physical beauty and influence; its aspects "
               "bring growth in longevity and inheritance (exalted), "
               "comfort through father, honour through state and gain "
               "through business, and expenses running smoothly aided "
               "by distant connections",
            5: "Friend's sign brings success in education and "
               "children, along with advancement in fortune and "
               "religious practice; its aspects bring further "
               "advancement in fortune, income that grows with some "
               "difficulty, and physical beauty, health, standing and "
               "influence (own sign)",
            6: "Enemy's sign brings trouble from rivals and illness, "
               "resolved through intelligence, along with some "
               "deficiency in physical beauty, health, and comfort "
               "through mother, land and home; its aspects bring "
               "gain, comfort and honour through father, state and "
               "business, heavy expense offset by comfort through "
               "distant connections, and trouble regarding wealth and "
               "family from siblings' side (debilitated)",
            7: "Friend's sign brings comfort and beauty through a "
               "spouse, and success in business; its aspects bring "
               "some dissatisfaction in the field of income, physical "
               "beauty, health and self-respect (own sign), and "
               "dissatisfaction with siblings alongside some "
               "diminishment of personal drive",
            8: "Friend's sign brings excellent strength in longevity "
               "and inheritance, though some deficiency in physical "
               "beauty and health; its aspects bring heavy expense "
               "offset by gain through distant connections, some "
               "deficiency in wealth and family comfort (debilitated), "
               "and comfort through mother, land and home achieved "
               "with some deficiency (own sign)",
            9: "Friend's sign brings great growth in fortune and "
               "religious observance kept, along with comfort through "
               "mother, land and home; its aspects bring physical "
               "beauty, health and fame (own sign), some deficiency "
               "in sibling comfort and personal drive, and comfort "
               "through children with growth in education and "
               "intelligence",
            10: "Friend's sign brings comfort, gain, honour and "
                "cooperation through father, state and business, "
                "along with physical beauty and self-respect; its "
                "aspects bring dissatisfaction regarding wealth and "
                "family (debilitated), comfort through mother, land "
                "and home (own sign), and influence established over "
                "rivals through cleverness",
            11: "Enemy's sign brings growth in income through "
                "physical effort, along with comfort through mother, "
                "land and home; its aspects bring dissatisfaction "
                "with siblings and diminished personal drive, gain "
                "through education, intelligence and children, and "
                "gain through business and a spouse",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, along with some "
                "physical weakness; its aspects bring comfort through "
                "mother, land and home (own sign), influence "
                "established over rivals through intelligence, and "
                "growth in longevity and inheritance (exalted), "
                "marking a generally comfortable daily life",
        },
        "Venus": {
            1: "Enemy's sign brings some weakness of health, though "
               "the native is hard-working and clever; victory is "
               "achieved over rivals, marking a famous nature; its "
               "aspect on the 7th brings some discord-tinged comfort "
               "through a spouse, and gain achieved in daily business "
               "through cleverness",
            2: "Friend's sign brings real strength in wealth, though "
               "some discord with family, along with gain from and "
               "influence over rivals; its aspect on the 8th brings "
               "growth in strength in longevity and inheritance, "
               "marking an influential, well-regarded nature",
            3: "Friend's sign brings growth in personal drive though "
               "some deficiency and difficulty in sibling comfort, "
               "along with weak education and children; its aspect "
               "on the 9th brings some difficulty advancing fortune, "
               "with little particular interest in religious duty",
            4: "Exalted in an enemy's sign, brings excellent comfort "
               "through mother, land and home, and good income, "
               "along with victory over rivals; its aspect on the "
               "10th (debilitated) brings loss through father, and "
               "failure in matters of state, with many obstacles in "
               "the path of business",
            5: "Enemy's sign brings excellent success in education "
               "and intelligence, though some difficulty regarding "
               "children, and gives the power of speech, cleverness "
               "and artistic skill; its aspect on the 11th (own sign) "
               "brings growth in income through education and "
               "intelligence, and victory over rivals",
            6: "In its own sign here (Venus rules the 6th), brings "
               "success over rivals with heavy influence in disputes, "
               "along with gain in wealth and income through effort, "
               "and gain from maternal-side connections; its aspect "
               "on the 12th brings heavy expense offset by some gain "
               "through distant connections despite difficulty",
            7: "Friend's sign brings some discord-tinged gain "
               "regarding a spouse, and gain in business achieved "
               "with some difficulty, along with influence over "
               "rivals, though some possibility of disorder in the "
               "reproductive organs; its aspect on the Lagna brings "
               "growth of physical strength and influence",
            8: "Enemy's sign brings growth in longevity and "
               "inheritance, though difficulty in the path of income, "
               "with gain through distant connections achieved "
               "through hard work, and some trouble from rivals; its "
               "aspect on the 2nd brings family cooperation gained, "
               "though special effort is needed for wealth to grow",
            9: "Enemy's sign brings special effort needed for "
               "fortune to advance, with little faith in religious "
               "observance, along with gain from rivals achieved "
               "through cleverness; its aspect on the 3rd brings "
               "sibling comfort and growth in personal drive",
            10: "Debilitated in a friend's sign brings difficulty "
                "through father, state and business, along with "
                "obstacles in fortune's advance caused by rivals; its "
                "aspect on the 4th (exalted) brings comfort through "
                "mother, land and home, and influence maintained at "
                "home",
            11: "In its own sign here (Venus rules the 11th), brings "
                "growth in income, along with special gain from "
                "rivals; its aspect on the 5th (enemy's sign) brings "
                "success in education and intelligence achieved only "
                "with some difficulty, developing over time into real "
                "skill and learning, though flawed comfort regarding "
                "children",
            12: "Enemy's sign brings heavy expense offset by gain "
                "through distant connections, along with some trouble "
                "from disputes and rivals, though cleverness brings "
                "gain too; its aspect on the 6th (own sign) brings "
                "full influence established over rivals",
        },
        "Saturn": {
            1: "Enemy's sign brings some deficiency in physical "
               "beauty, along with wealth and family comfort gained "
               "through effort; its aspects bring growth in personal "
               "drive and sibling comfort (own sign), success with a "
               "spouse and in daily business, and some benefit "
               "through father and state affairs",
            2: "In its own sign here (Saturn rules the 2nd), brings "
               "ample wealth and family comfort, though some "
               "deficiency in sibling comfort; its aspects bring only "
               "slight comfort through mother, land and home, growth "
               "in longevity and inheritance, and excellent income "
               "with occasional sudden gain (exalted)",
            3: "In its own sign here (Saturn rules the 3rd), brings "
               "real growth in personal drive, though sibling comfort "
               "gained with some deficiency; its aspects bring "
               "trouble regarding children with weak education and "
               "intelligence (debilitated), advancement in fortune "
               "and fame though little faith kept in religion, and "
               "heavy expense with unhelpful distant connections",
            4: "Enemy's sign brings some deficiency regarding "
               "mother, ordinary comfort through land and home, and "
               "dissatisfying family and sibling comfort; its aspects "
               "bring influence over rivals with gain through "
               "disputes, advancement through father, state and "
               "business, and growth in physical beauty and health "
               "(exalted)",
            5: "Enemy's sign, debilitated, brings trouble regarding "
               "children, and weak education and intelligence; its "
               "aspects bring success with a spouse and in business, "
               "excellent income (exalted), and family comfort "
               "achieved through secretive method with only ordinary "
               "success in wealth (own sign)",
            6: "Friend's sign brings heavy influence over rivals "
               "with gain through disputes, though some discord with "
               "family; its aspects bring growth in longevity though "
               "only modest gain in inheritance, heavy expense with "
               "loss through distant connections, and some discord "
               "with siblings alongside growth in personal drive (own "
               "sign)",
            7: "Friend's sign brings gain through a spouse though "
               "little real comfort, real gain in daily business, and "
               "good relations with siblings and family; its aspects "
               "bring obstacles to fortune and religious practice, "
               "some bodily trouble, and some deficiency in comfort "
               "through mother, land and home along with living away "
               "from one's native place",
            8: "Enemy's sign brings growth in longevity and "
               "inheritance, though some deficiency in daily comfort, "
               "savings and sibling comfort; its aspects bring "
               "success through father, state and business, only "
               "ordinary wealth and family comfort, and some "
               "deficiency regarding education, intelligence and "
               "children (debilitated)",
            9: "Enemy's sign brings obstacles to fortune and "
               "religious observance, along with only ordinary wealth "
               "and family comfort; its aspects bring excellent "
               "income with occasional sudden gain (exalted), growth "
               "in sibling comfort and personal drive, and victory "
               "over rivals with gain through disputes",
            10: "Friend's sign brings cooperation through the "
                "father, honour through state affairs, gain through "
                "business, and growth in sibling comfort and personal "
                "drive; its aspects bring heavy expense with "
                "unsatisfying distant connections, some deficiency in "
                "comfort through mother, land and home, and comfort "
                "through a spouse with success in daily business",
            11: "Friend's sign brings real growth in income with "
                "occasional sudden gain, along with growth in family "
                "and sibling comfort and personal drive; its aspects "
                "bring some deficiency in physical beauty and health, "
                "trouble regarding children with weak education "
                "(debilitated), and growth in longevity and "
                "inheritance though a troubled daily life",
            12: "Enemy's sign brings heavy expense, unsatisfying "
                "distant connections, and loss to wealth, family and "
                "sibling comfort; its aspects bring only ordinary "
                "family comfort, influence over rivals through "
                "secretive method, and obstacles to fortune's advance "
                "with religious duty not fully kept",
        },
        "Rahu": {
            1: "Brings some deficiency in physical beauty and "
               "health, and occasionally severe physical hardship; "
               "the native appears decent and genteel outwardly, "
               "though inwardly cunning",
            2: "Brings some deficiency in wealth and family comfort, "
               "and occasionally serious crises through family "
               "matters; the native often has to rely on borrowed "
               "money, working to overcome difficulty through "
               "secretive method",
            3: "Brings great courage and boldness, though relations "
               "with siblings are not comfortable; the native "
               "occasionally faces severe crises, but bears them "
               "quietly, being patient and daring",
            4: "Brings great loss of comfort through mother, with "
               "loss of land and home too; occasionally severe "
               "trouble arises, which the native faces through "
               "patience and secretive method",
            5: "Brings trouble regarding children, and real "
               "difficulty and deficiency in education, with a "
               "somewhat harsh manner of speech; the native manages "
               "through patience and secretive method, though remains "
               "surrounded by worry",
            6: "Brings a strong hold over rivals, overcome through "
               "cleverness and secretive method; the native does some "
               "harm to the maternal side too",
            7: "Brings unusual strength regarding a spouse, possibly "
               "more than one marriage; the native resorts to many "
               "methods to grow daily income, and lives a wealthy, "
               "comfortable life",
            8: "Brings repeated crises to life, occasionally serious "
               "enough to threaten it, along with stomach trouble and "
               "loss to inheritance; the native remains beset by "
               "troubles",
            9: "Brings severe obstacles to the advancement of "
               "fortune, and little faith in religion; the native, "
               "though often irreligious, works hard for advancement "
               "and relies on secretive method",
            10: "Brings trouble through the father, crisis through "
                "state affairs, and loss in business; the native "
                "tries to advance through courage and secretive "
                "method, though without much success",
            11: "Brings ample growth in income, with occasional "
                "difficulty too; the native never loses patience, and "
                "prevails over difficulty through courage",
            12: "Brings heavy expense, and trouble through distant "
                "connections too; the native, being bold, does not "
                "lose composure and keeps working to overcome crises",
        },
        "Ketu": {
            1: "Brings growth in physical strength and stature, "
               "though some diminishment of physical beauty; the "
               "native has a stubborn, obstinate temperament, and "
               "faces every difficulty with courage, being "
               "hard-working and patient",
            2: "Brings some deficiency in family comfort, and real "
               "effort needed to save wealth; the native occasionally "
               "faces serious financial crisis, often relying on "
               "borrowed money, though remains bold and patient",
            3: "Brings great growth in personal drive, though some "
               "deficiency and trouble in sibling comfort; the native "
               "relies on secretive method, and is daring and "
               "hard-working",
            4: "Brings great loss of comfort through mother, "
               "including separation from one's native land, and "
               "loss of comfort through land and home too; even so, "
               "the native is hard-working, courageous, patient and "
               "contented",
            5: "Brings great trouble regarding children, and only "
               "modest success in education achieved after real "
               "difficulty; the native is intensely hard-working, "
               "stubborn, and relies on secretive method, remaining "
               "ever anxious",
            6: "Brings victory over rivals, and gain through "
               "disputes and litigation too; the native never loses "
               "composure even facing great crisis, and prevails "
               "through boldness",
            7: "Brings real trouble regarding a spouse, and serious "
               "difficulty in the field of daily income; the native "
               "tries to bring happiness to domestic life through "
               "patience and courage, though with only modest success",
            8: "Brings serious crises to life, occasionally severe "
               "enough to threaten it, with stomach trouble too; "
               "daily life is full of worry, and loss to inheritance "
               "follows, with little comfort even after great effort",
            9: "Brings great obstacles to the advancement of "
               "fortune, which the native tries to overcome through "
               "secretive method and hard work, achieving only "
               "partial success; faith in religion and God stays weak "
               "too",
            10: "Brings ordinary gain, success, comfort, fame, "
                "cooperation and honour through father, state and "
                "business, despite some deficiency; even great effort "
                "and reliance on secretive method bring no special "
                "further advancement",
            11: "Brings great growth in income, with occasional "
                "crisis too, though the native prevails through "
                "secretive method and hard work, though never fully "
                "satisfied",
            12: "Brings heavy expense causing real trouble and "
                "crisis, along with difficulty through distant "
                "connections; the native tries to overcome difficulty "
                "through secretive method, hard work, patience and "
                "courage, though without great success",
        },
    },
    "Capricorn": {
        "Sun": {
            1: "Enemy's sign brings some deficiency in physical "
               "beauty and health, and occasionally special physical "
               "hardship, though growth in longevity and inheritance; "
               "its aspect on the 7th brings ordinary difficulty "
               "regarding a spouse, and some trouble in daily business",
            2: "Enemy's sign brings difficulty saving wealth, and "
               "ongoing trouble in family comfort; its aspect on the "
               "8th brings growth in longevity and gain in "
               "inheritance, marking a life lived lavishly, with "
               "spending to match",
            3: "Friend's sign brings great growth in personal drive, "
               "though some deficiency in sibling comfort, along "
               "with strength in longevity and inheritance; its "
               "aspect on the 9th brings some obstacles to fortune's "
               "advance, and some deficiency in religious practice",
            4: "Exalted in a friend's sign, brings excellent comfort "
               "through mother, land and home, and some gain in "
               "longevity and inheritance, marking a lavish daily "
               "life; its aspect on the 10th brings some deficiency "
               "in comfort through father, and obstacles to "
               "advancement through state and business",
            5: "Enemy's sign brings trouble regarding children, and "
               "difficulty in education, with weak intelligence and "
               "an anxious, quick-tempered nature, though gain in "
               "longevity and inheritance; its aspect on the 11th "
               "brings success in income only through special effort",
            6: "Friend's sign brings ongoing victory over rivals, "
               "along with gain in longevity and inheritance; its "
               "aspect on the 12th brings heavy expense, and some "
               "dissatisfaction through distant connections",
            7: "Friend's sign brings difficulty regarding a spouse "
               "and business, occasionally serious loss, though gain "
               "in longevity and inheritance; its aspect on the "
               "Lagna brings some deficiency in physical beauty and "
               "health, with occasional affliction",
            8: "In its own sign here (Sun rules the 8th), brings "
               "special strength in longevity and inheritance, "
               "marking a self-respecting, glorious, fearless, brave "
               "nature, with an influential daily life; its aspect "
               "on the 2nd brings trouble saving wealth, and "
               "obstacles to family comfort",
            9: "Friend's sign brings some obstacles to fortune's "
               "advance, with some flaw in religious practice and "
               "some mental unrest, though growth in longevity and "
               "inheritance, marking a grand daily life; its aspect "
               "on the 3rd brings less than proper growth in sibling "
               "comfort and personal drive",
            10: "Debilitated in an enemy's sign brings severe "
                "trouble through the father's side, diminished "
                "standing through state affairs, and obstacles in "
                "business, along with some loss to longevity and "
                "inheritance; its aspect on the 4th brings only "
                "ordinary comfort through mother, land and home",
            11: "Friend's sign brings growth in income despite "
                "occasional difficulty, along with special strength "
                "in longevity and inheritance; its aspect on the 5th "
                "brings trouble regarding children, and difficulty "
                "in education, and gives a fierce temperament",
            12: "Friend's sign brings difficulty over expenses and "
                "distant connections, along with some stomach "
                "trouble and some loss to longevity and inheritance; "
                "its aspect on the 6th brings success over rivals "
                "achieved with some difficulty, and disputes that "
                "tend to resolve themselves",
        },
        "Moon": {
            1: "Enemy's sign brings growth in physical beauty, and "
               "gives a jovial, self-respecting, famous, artistic "
               "nature; its aspect on the 7th brings a beautiful, "
               "capable, self-respecting spouse, and some measure of "
               "success in daily business",
            2: "Enemy's sign brings growth in wealth and family, "
               "though some trouble caused by a spouse; its aspect "
               "on the 8th brings growth in longevity and "
               "inheritance, marking a lavish lifestyle",
            3: "Friend's sign brings excellent sibling comfort and "
               "growth in personal drive, along with good comfort "
               "through a spouse, business and family; its aspect on "
               "the 9th brings growth in fortune and religious "
               "practice, marking a wealthy, famous, happy, "
               "prosperous nature",
            4: "Friend's sign brings excellent comfort through "
               "mother, land and home, a joyful domestic atmosphere, "
               "a beautiful spouse and success in business; its "
               "aspect on the 10th brings ongoing fame, standing, "
               "cooperation, wealth and other gain through father, "
               "state and lasting business",
            5: "Exalted, though in only a friend's sign — brings "
               "special success in education, intelligence and "
               "children, along with comfort through a spouse and in "
               "business; its aspect on the 11th (debilitated) "
               "brings some obstacles in the path of income, and "
               "gives a cheerful, quick-witted nature",
            6: "Friend's sign brings success over rivals through "
               "cleverness, though discord with a spouse and "
               "difficulty in business; its aspect on the 12th "
               "brings heavy expense, offset by gain through distant "
               "connections",
            7: "In its own sign here (Moon rules the 7th), brings a "
               "beautiful spouse and ample comfort through her, and "
               "complete success in business, marking a joyful "
               "domestic life; its aspect on the Lagna brings some "
               "dissatisfaction despite growth in influence, and "
               "some dissatisfaction regarding fame and business",
            8: "Friend's sign brings excellent gain in longevity and "
               "inheritance, though difficulty regarding a spouse "
               "and business, with weak domestic happiness and an "
               "unsettled mind; its aspect on the 2nd brings wealth "
               "and family comfort achieved with some difficulty, "
               "though a lavish daily life overall",
            9: "Friend's sign brings special advancement in "
               "fortune, and a strong interest in religious "
               "practice, marking a wealthy, famous, honest, "
               "righteous nature; its aspect on the 3rd brings "
               "sibling comfort and growth in personal drive",
            10: "Friend's sign brings cooperation through the "
                "father, standing through state affairs, and gain "
                "through business, high morale, a beautiful, "
                "self-respecting spouse, and a joyful domestic life; "
                "its aspect on the 4th brings ample comfort through "
                "mother, land and home, marking a happy, wealthy, "
                "fortunate nature",
            11: "Friend's sign, debilitated, brings some deficiency "
                "in income, and only slight comfort regarding a "
                "spouse and business, with anxiety caused by "
                "domestic matters; its aspect on the 5th (exalted) "
                "brings ample comfort through education, "
                "intelligence and children",
            12: "Friend's sign brings heavy expense, offset by gain "
                "through distant connections, along with some "
                "deficiency regarding a spouse and difficulty in "
                "daily business, leaving the mind anxious and "
                "unsettled; its aspect on the 6th brings success "
                "over rivals and in disputes achieved through humility",
        },
        "Mars": {
            1: "Exalted in an enemy's sign brings growth in physical "
               "beauty and strength; its aspects bring good comfort "
               "through mother, land and home (own sign), difficulty "
               "regarding a spouse and business, and strength in "
               "longevity and inheritance",
            2: "Enemy's sign brings wealth and family comfort "
               "achieved amid some ordinary dissatisfaction, though "
               "some deficiency in comfort through mother; its "
               "aspects bring advancement in education, intelligence "
               "and children, growing strength in longevity and "
               "inheritance, and advancement in fortune and "
               "religious practice achieved through effort",
            3: "Friend's sign brings growth in personal drive and "
               "sibling comfort, along with comfort through mother, "
               "land and home; its aspects bring influence over "
               "rivals, advancement in fortune and religious "
               "practice, and moderate success through father, state "
               "and business",
            4: "In its own sign here (Mars rules the 4th), brings "
               "special comfort through mother, land and home; its "
               "aspects bring some deficiency in comfort through a "
               "spouse and difficulty in daily business, excellent "
               "income with the means of gain coming easily, and "
               "cooperation, standing and success through father, "
               "state and business",
            5: "In only a friend's sign, brings gain through "
               "education and children, along with comfort through "
               "mother, land and home; its aspects bring growing "
               "strength in longevity and inheritance, good income, "
               "and heavy expense offset by gain through distant "
               "connections",
            6: "In Mercury's sign, brings a strong hold over rivals "
               "and gain through disputes, though some deficiency in "
               "comfort through mother, land and home, and some "
               "difficulty in the path of income; its aspects bring "
               "advancement in fortune and religion, heavy expense "
               "offset by gain through distant connections, and "
               "growth of physical beauty, health and influence "
               "(exalted)",
            7: "Friend's sign brings some deficiency in a spouse and "
               "domestic comfort, and weak comfort through mother, "
               "land and home, along with business difficulty; its "
               "aspects bring some gain through father, state and "
               "business, growth of physical beauty, influence and "
               "standing, and difficulty saving wealth alongside "
               "only ordinary family comfort (debilitated)",
            8: "Friend's sign brings excellent strength in longevity "
               "and inheritance, though only ordinary comfort "
               "through mother, land and home; its aspects bring "
               "excellent income, some difficulty though success in "
               "saving wealth with ordinary family comfort, and "
               "growth in sibling comfort and personal drive",
            9: "Friend's sign brings advancement in fortune and "
               "religious practice, marking a righteous, famous, "
               "just nature; its aspects bring heavy expense offset "
               "by gain through distant connections, growth in "
               "sibling comfort and personal drive, and ample "
               "comfort through mother, land and home, marking a "
               "wealthy, famous, capable, courageous, cheerful nature",
            10: "In an ordinary enemy's sign, brings success through "
                "father, state and business; its aspects bring "
                "growth of physical beauty, health and influence, "
                "comfort through mother, land and home, and comfort "
                "through children with growth in education and "
                "intelligence",
            11: "In its own sign here (Mars rules the 11th), brings "
                "excellent growth in income, along with ample "
                "comfort through mother, land and home; its aspects "
                "bring wealth and family comfort achieved with some "
                "deficiency, excellent comfort through education, "
                "intelligence and children, and a strong hold over "
                "rivals with gain through disputes",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, though some deficiency "
                "in comfort through mother, land and home; its "
                "aspects bring sibling comfort with growth in "
                "personal drive, an ongoing hold over rivals, and "
                "some deficiency in a spouse's comfort with some "
                "loss in business",
        },
        "Mercury": {
            1: "Friend's sign brings growth in physical influence "
               "and standing, and the native establishes influence "
               "over rivals through discernment; its aspect on the "
               "7th brings success with a spouse and in business, "
               "though occasional difficulty in business too",
            2: "Friend's sign brings growth in wealth and family "
               "comfort, along with interest in honour, standing and "
               "religious practice; its aspect on the 8th brings "
               "gain in longevity and inheritance, though occasional "
               "difficulty in fortune's advance",
            3: "Friend's sign brings some deficiency in sibling "
               "comfort and personal drive, and difficulty in "
               "fortune's advance and religious practice, along with "
               "some trouble from rivals; its aspect on the 9th (own "
               "sign) brings advancement in fortune and religious "
               "practice through one's own discernment",
            4: "Friend's sign brings comfort through mother, land "
               "and home, along with advancement in fortune, though "
               "some disturbance to domestic peace; its aspect on "
               "the 10th brings success through father, state and "
               "business, and victory over rivals",
            5: "Friend's sign brings success in children, education "
               "and intelligence achieved with some difficulty, and "
               "the native advances income and religious practice "
               "through personal effort, with success over rivals "
               "too; its aspect on the 11th brings ample growth in "
               "fortune",
            6: "In its own sign here (Mercury rules the 6th), brings "
               "victory over rivals, with some difficulty in fortune "
               "and religion at first that later resolves; its "
               "aspect on the 12th brings heavy expense, offset by "
               "gain and comfort through distant connections",
            7: "Enemy's sign brings advancement in fortune through "
               "discernment and success in business, though unrest "
               "caused by a spouse, and occasional illness; its "
               "aspect on the Lagna brings growth in physical "
               "influence and fame",
            8: "Friend's sign brings growth in longevity and gain in "
               "inheritance, though many obstacles to fortune's "
               "advance and some diminished fame; its aspect on the "
               "2nd brings wealth and family comfort achieved with "
               "some difficulty, alongside an influential daily life",
            9: "Exalted in its own sign here (Mercury rules the "
               "9th), brings special advancement in fortune and "
               "religious practice, along with success over rivals "
               "and gain through disputes; its aspect on the 3rd "
               "brings discord with brothers and some deficiency in "
               "sibling comfort, with personal drive somewhat subdued",
            10: "Friend's sign brings gain, standing, cooperation "
                "and fame through father, state and business, along "
                "with victory over rivals and success in earning "
                "wealth; its aspect on the 4th brings comfort "
                "through mother, land and home, though obstacles to "
                "further advancement",
            11: "Friend's sign brings excellent growth in income and "
                "success over rivals, along with advancement in "
                "fortune achieved through discernment and hard work; "
                "its aspect on the 5th brings some difficulty though "
                "success regarding children, along with special "
                "advancement in education",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, though some obstacles "
                "to fortune's advance and some diminished fame; its "
                "aspect on the 6th brings success over rivals "
                "achieved with some difficulty, resolved in time",
        },
        "Jupiter": {
            1: "Enemy's sign brings a frail body, diminished sibling "
               "comfort and limited valour, along with difficulty "
               "managing expenses and unsatisfying distant "
               "connections; its aspects bring flawed success in "
               "education and intelligence with a mixed experience "
               "through children, success with a spouse and in "
               "business (exalted), and abundant growth in fortune "
               "and religious practice",
            2: "Enemy's sign brings loss to savings and trouble from "
               "family, along with heavy expenses offset by gain "
               "through distant connections; its aspects bring "
               "influence over rivals through wit, some gain in "
               "longevity and inheritance, and ordinary success "
               "through father, state and business",
            3: "In its own sign here (Jupiter rules the 3rd), brings "
               "sibling comfort though some deficiency in personal "
               "drive, along with smoothly managed expenses and gain "
               "from distant connections; its aspects bring a "
               "beautiful spouse and success in daily business "
               "(exalted), ups and downs in fortune and religious "
               "practice, and excellent income",
            4: "Friend's sign brings some deficiency in comfort "
               "through mother, land and home, along with weakened "
               "sibling comfort; its aspects bring ordinary gain in "
               "longevity and inheritance, some deficiency though "
               "success through father, state and business, and "
               "heavy expense offset by gain through distant "
               "connections gained without much trouble",
            5: "Enemy's sign brings uneven gain regarding children "
               "and some deficiency in education, along with "
               "expenses managed through wit and gain via distant "
               "connections, ordinary comfort with siblings, and "
               "growth in personal drive; its aspects bring ordinary "
               "growth in fortune and religion, good income, and "
               "some deficiency in physical beauty and health "
               "(debilitated)",
            6: "Friend's sign brings influence over rivals "
               "established through cleverness in managing expenses, "
               "along with some ordinary discord with siblings and "
               "weakened valour; its aspects bring some difficulty "
               "through father, state and business, heavy expense "
               "offset by gain through distant connections (own "
               "sign), and great effort for wealth and family "
               "comfort bringing only hardship",
            7: "Exalted in a friend's sign, brings a beautiful "
               "spouse and comfort through her and in business, "
               "along with gain via distant connections though heavy "
               "expense; its aspects bring good income, some "
               "deficiency in physical beauty and health "
               "(debilitated), and sibling comfort with growth in "
               "personal drive (own sign)",
            8: "Friend's sign brings some loss to longevity and "
               "inheritance; its aspects bring heavy expense offset "
               "by gain through distant connections (own sign), some "
               "deficiency in wealth and family comfort, and some "
               "flawed success regarding mother, land and home",
            9: "Friend's sign brings some weakness in fortune and "
               "religious practice, along with some gain via distant "
               "connections that helps sustain expenses; its aspects "
               "bring some deficiency in physical beauty and health "
               "along with unsettled wealth (debilitated), ordinary "
               "growth in sibling comfort and personal drive (own "
               "sign), and success over rivals through discernment",
            10: "Enemy's sign brings some deficiency through father, "
                "state and business, though growth in sibling "
                "comfort and valour that eases expenses, along with "
                "gain from distant connections; its aspects bring "
                "difficulty saving wealth alongside family trouble, "
                "some deficiency regarding mother though comfort "
                "through land and home gained through spending, and "
                "influence established over rivals through cleverness",
            11: "Friend's sign brings good income, along with gain "
                "via distant connections that lightens expenses; its "
                "aspects bring sibling comfort with growth in "
                "personal drive, dissatisfaction regarding children "
                "though growth in education and intelligence, and "
                "comfort through a spouse with success in business "
                "(exalted)",
            12: "In its own sign here (Jupiter rules the 12th), "
                "brings heavy expense offset by gain through distant "
                "connections, along with some deficiency in sibling "
                "comfort and valour; its aspects bring only ordinary "
                "comfort through mother, land and home, influence "
                "established over rivals through cleverness, and "
                "gain in longevity and inheritance despite some "
                "deficiency",
        },
        "Venus": {
            1: "Friend's sign brings physical beauty, influence and "
               "honour, along with success through father, state and "
               "business, and standing in society, and gain through "
               "children, education and intelligence too; its aspect "
               "on the 7th brings a beautiful, capable spouse, and "
               "ongoing gain in daily business",
            2: "Friend's sign brings ample wealth and family "
               "comfort, along with gain through father, business "
               "and state affairs, though some difficulty regarding "
               "children; its aspect on the 8th brings some "
               "deficiency in longevity and inheritance, marking a "
               "wealthy, famous, though anxious nature",
            3: "Exalted, though in only a friend's sign, brings "
               "special growth in valour, along with some deficiency "
               "in sibling comfort, and gain through education and "
               "children, with success through father, state and "
               "business too; its aspect on the 9th brings some "
               "deficiency in fortune's advance and religious "
               "practice, and diminished fame",
            4: "In only a friend's sign, brings comfort through "
               "mother, land and home, along with good income gained "
               "through discernment; its aspect on the 10th brings "
               "cooperation, success, fame, gain and honour through "
               "father, state and business",
            5: "In its own sign here (Venus rules the 5th), brings "
               "ample gain through children and education, along "
               "with success through father, state and business, "
               "marking a native who favours order and discipline; "
               "its aspect on the 9th brings ample income, and "
               "continuous advancement",
            6: "Friend's sign brings a hold over rivals, along with "
               "strength gained through the father despite some "
               "discord, and honour through state affairs, though "
               "weak children and education; its aspect on the 12th "
               "brings heavy expense, offset by gain through distant "
               "connections, along with a somewhat anxious mind",
            7: "Enemy's sign brings a beautiful, capable spouse, "
               "along with comfort through father, state, business, "
               "children and education, and a joyful domestic life; "
               "its aspect on the Lagna brings physical beauty and "
               "influence, along with honour in state and social life",
            8: "Enemy's sign brings strength in longevity and "
               "inheritance, though trouble through father and "
               "children, with a flawed field in state affairs and "
               "education; its aspect on the 2nd brings wealth and "
               "family comfort, achieved through effort and "
               "secretive method",
            9: "Debilitated in a friend's sign brings obstacles to "
               "fortune's advance and religious practice, along with "
               "flawed success through father, state, business, "
               "children and education; its aspect on the 3rd brings "
               "growth in sibling comfort and personal drive "
               "achieved through effort",
            10: "In its own sign here (Venus rules the 10th), brings "
                "excellent cooperation, honour and gain through "
                "father, state and business, along with a strong "
                "field in children and education; its aspect on the "
                "4th brings comfort through mother, land and home, "
                "and a joyful domestic life",
            11: "Enemy's sign brings growth in income, and success "
                "through father, state and business; its aspect on "
                "the 5th brings excellent gain through children and "
                "education",
            12: "Enemy's sign brings heavy expense, offset by gain "
                "through distant connections, along with loss "
                "through father, trouble regarding children, and "
                "diminished education, with an anxious mind; its "
                "aspect on the 6th brings influence over rivals "
                "achieved through cleverness, though it comes only "
                "after some delay",
        },
        "Saturn": {
            1: "In its own sign here (Saturn is Lagna-lord), brings "
               "growth in physical beauty and influence, marking a "
               "self-respecting, famous nature; its aspects bring "
               "growth in valour though sibling discord, discontent "
               "regarding a spouse alongside effort to grow the "
               "business, and success, cooperation, fame and honour "
               "through father, state and business (exalted)",
            2: "In its own sign here (Saturn rules the 2nd), brings "
               "ample gain in savings and family comfort; its "
               "aspects bring some deficiency in comfort through "
               "mother, land and home (debilitated), some loss to "
               "longevity and inheritance, and growth in income "
               "achieved with some difficulty",
            3: "Enemy's sign brings sibling comfort achieved with "
               "some difficulty, along with great growth in valour, "
               "and wealth and family comfort through personal "
               "effort; its aspects bring special success in "
               "children and education, growth in fortune and "
               "religious practice, and heavy expense offset by gain "
               "through distant connections achieved with some "
               "difficulty",
            4: "Enemy's sign, debilitated, brings some deficiency in "
               "comfort through mother, land and home, along with "
               "weak physical beauty and some deficiency in wealth "
               "and family comfort; its aspects bring victory over "
               "rivals with gain through disputes, success through "
               "father, state and business (exalted), and a "
               "beautiful body with abundant self-confidence (own "
               "sign)",
            5: "Friend's sign brings special gain through children, "
               "education and intelligence, along with physical "
               "beauty, eloquence and capability; its aspects bring "
               "some discontent regarding a spouse though real "
               "attachment to her with some flawed success in "
               "business, difficulty in the field of income, and "
               "growth in wealth and family comfort (own sign)",
            6: "Friend's sign brings some deficiency in physical "
               "beauty and health, along with growing influence over "
               "rivals, ordinary discord with family, and some "
               "deficiency in savings; its aspects bring no great "
               "gain in longevity and inheritance, heavy expense "
               "with distant connections proving unhelpful, and some "
               "discord with siblings alongside growth in valour",
            7: "Enemy's sign brings strength and closeness gained "
               "through a spouse, advancement in business through "
               "effort, and comfort through wealth and children; its "
               "aspects bring advancement in fortune and religious "
               "practice, growth in physical beauty with "
               "self-respect and influence gained, and some "
               "deficiency in comfort through mother, land and home "
               "(debilitated)",
            8: "Enemy's sign brings gain in longevity and "
               "inheritance, though some deficiency in physical "
               "beauty and health, along with loss to wealth and "
               "family; its aspects bring success through father, "
               "state and business (exalted), only slight wealth and "
               "family comfort, and growth in education, "
               "intelligence and children",
            9: "Friend's sign brings ample advancement in fortune "
               "and religious practice, along with physical "
               "influence, honour and family comfort; its aspects "
               "bring some obstacles in the path of income, some "
               "deficiency in sibling comfort though growth in "
               "valour, and victory over rivals through wealth and "
               "physical strength",
            10: "Exalted in a friend's sign, brings excellent "
                "comfort, cooperation, honour and success through "
                "father, state and business, along with wealth and "
                "family comfort; its aspects bring heavy expense "
                "with dissatisfying distant connections, some "
                "deficiency in comfort through mother, land and home "
                "(debilitated), and some deficiency in a spouse's "
                "comfort with some trouble in business",
            11: "Enemy's sign brings great growth in income, along "
                "with wealth and family comfort; its aspects bring "
                "physical beauty, fame, honour, self-confidence and "
                "influence (own sign), ample success in children and "
                "education, and some worry over longevity though "
                "gain in inheritance",
            12: "Enemy's sign brings heavy expense offset by gain "
                "through distant connections, along with loss to "
                "wealth, family and physical comfort; its aspects "
                "bring constant effort needed just to earn wealth, "
                "influence established over rivals with victory in "
                "disputes, and advancement in fortune and religious "
                "practice",
        },
        "Rahu": {
            1: "Brings some deficiency in physical beauty and "
               "health, with occasional injury, and sometimes a "
               "particular ailment; the native is bold, clever, "
               "alert, and grows their influence through strategy",
            2: "Brings anxiety and hardship over wealth and family, "
               "sometimes requiring borrowed money; though outwardly "
               "appearing wealthy, real wealth stays scarce, until "
               "the native later secures their finances through "
               "secretive method",
            3: "Brings trouble through siblings, though great growth "
               "in valour; though inwardly feeling weak, the native "
               "appears outwardly bold, and prevails over difficulties",
            4: "Brings some deficiency in comfort through mother, "
               "land and home, sometimes requiring separation from "
               "one's native land; the native eventually grows "
               "comfort and influence through secretive method, "
               "being bold and patient",
            5: "Brings trouble regarding children, and difficulty "
               "acquiring education, though the native is "
               "sharp-witted; the native is clever and skilled in "
               "secretive method, and eventually finds success in "
               "both children and education",
            6: "Brings a strong hold over rivals, and success in "
               "disputes; the native is a skilled strategist, "
               "discerning, sharp-witted and versed in secretive "
               "method, and is rarely ill",
            7: "Brings great trouble regarding a spouse, and "
               "difficulty in business, along with disorder in the "
               "reproductive organs; the native achieves some "
               "victory over these difficulties through secretive "
               "method",
            8: "Brings serious crises to life, occasionally severe "
               "enough to threaten it, along with loss to "
               "inheritance and disorders of the stomach and lower "
               "body; the native manages to get by however they can "
               "through secretive method",
            9: "Brings continuous obstacles to fortune's advance, "
               "occasionally severe, along with weak religious "
               "observance; the native achieves modest advancement "
               "through hard struggle, effort and secretive method",
            10: "Brings obstacles through father, state and "
                "business, though the native overcomes them through "
                "secretive method and advances their fortune, "
                "despite frequently facing crisis",
            11: "Brings special gain through effort and secretive "
                "method, though occasionally great loss too, "
                "alongside special gain at other times, marking a "
                "life of continuous ups and downs",
            12: "Brings great difficulty managing expenses, and "
                "trouble through distant connections too; being "
                "bold, the native does not let their difficulties "
                "show, and works hard to resolve them",
        },
        "Ketu": {
            1: "Brings some deficiency in physical beauty and "
               "health, with the possibility of a serious injury; "
               "the native has a fierce, obstinate temperament, and "
               "resorts to secretive method to grow their influence",
            2: "Brings serious crises regarding wealth and family, "
               "though the native remains ready to resolve financial "
               "difficulty through boldness and secretive method",
            3: "Brings trouble and crisis regarding siblings, though "
               "great growth in valour; the native tries to keep "
               "life influential through courage, patience, effort "
               "and secretive method",
            4: "Brings loss of comfort through mother, and trouble "
               "caused by her specifically, with a quarrelsome "
               "domestic life, and sometimes separation from one's "
               "native land; eventually, hard work and secretive "
               "method bring some modest success in securing comfort",
            5: "Brings a loss in the field of children and "
               "education, and hidden worry in the mind, though the "
               "native has sharp intelligence and uses cleverness to "
               "work through their difficulties",
            6: "Brings entanglement in difficulty caused by rivals, "
               "though the native prevails through secretive "
               "strength, finding success in disputes; the maternal "
               "side suffers some loss",
            7: "Brings various kinds of trouble regarding a spouse, "
               "with a troubled domestic life, and difficulty in "
               "whatever business is undertaken; the native "
               "eventually achieves due success through secretive "
               "method and hard effort",
            8: "Brings repeated crises to life, occasionally severe "
               "enough to threaten it, along with stomach trouble; "
               "the native works hard for a livelihood, and while "
               "inwardly anxious, presents an outward show of "
               "influence, generally living a life full of struggle",
            9: "Brings difficulty to fortune's advance, though the "
               "native prevails through boldness, effort and "
               "secretive method, achieving advancement in fortune "
               "and observance of religious duty; occasionally "
               "severe crises to fortune must be overcome too",
            10: "Brings trouble through the father, difficulty "
                "through state affairs, and crisis in business, "
                "though the native prevails through secretive "
                "method; such a life carries real struggle and "
                "frequent change",
            11: "Brings great growth in income, through secretive "
                "method, boldness and hard work; obstacles that do "
                "arise are overcome successfully",
            12: "Brings very heavy expense, offset by gain through "
                "distant connections; the native faces difficulty "
                "with courage and ultimately prevails, being "
                "hard-working, patient, skilled in secretive method, "
                "and bold",
        },
    },
    "Aquarius": {
        "Sun": {
            1: "Enemy's sign brings some deficiency in physical "
               "beauty and health, though growth in influence and "
               "strength, and gives a fierce, restlessly active "
               "temperament; its aspect on the 7th (own sign) brings "
               "special comfort through a spouse, and success in "
               "daily income through personal effort, marking a "
               "joyful domestic life",
            2: "Friend's sign brings growth in wealth and family "
               "comfort, though some particular deficiency regarding "
               "a spouse; its aspect on the 8th brings growth in "
               "longevity and inheritance, along with an influential "
               "daily life",
            3: "Exalted in a friend's sign, brings ample sibling "
               "comfort and great growth in personal drive, along "
               "with success through business in other spheres too; "
               "its aspect on the 9th (debilitated) brings some "
               "obstacles to fortune's advance and religious "
               "observance, and diminished honour",
            4: "Enemy's sign brings comfort through mother, land and "
               "home achieved with some difficulty, along with "
               "trouble in business; its aspect on the 10th brings "
               "success and gain through father, state and business, "
               "with growing standing",
            5: "Friend's sign brings success in education, "
               "intelligence and children, along with comfort "
               "through a spouse and in business; its aspect on the "
               "11th brings good income through intelligence, "
               "marking a happy, wealthy, influential nature",
            6: "Friend's sign brings victory over rivals and gain "
               "through disputes, along with success in business "
               "achieved with some difficulty; its aspect on the "
               "12th brings heavy expense, and some difficulty "
               "through distant connections",
            7: "In its own sign here (Sun rules the 7th), brings "
               "ample comfort through a spouse, and success in "
               "business, along with gain through in-laws and a "
               "joyful domestic life; its aspect on the Lagna brings "
               "some deficiency in physical beauty",
            8: "Friend's sign brings growth in longevity and "
               "inheritance, along with some trouble regarding a "
               "spouse and difficulty in business, though some gain "
               "through distant connections; its aspect on the 2nd "
               "brings wealth accumulated through hard effort, and "
               "family comfort",
            9: "Debilitated in an enemy's sign brings some "
               "deficiency in fortune and religious practice, along "
               "with difficulty regarding a spouse and business, and "
               "gives little regard for propriety in pursuit of "
               "self-interest; its aspect on the 3rd (exalted) "
               "brings special growth in sibling comfort and "
               "personal drive, marking a bold, courageous, daring "
               "nature",
            10: "Friend's sign brings gain through father, state and "
                "business, along with special strength through a "
                "spouse; its aspect on the 4th brings some "
                "deficiency in comfort through mother, land and home",
            11: "Friend's sign brings good income through business, "
                "along with special gain through a spouse; its "
                "aspect on the 5th brings special advancement in "
                "education, intelligence and children, and comfort too",
            12: "Enemy's sign brings difficulty over heavy expenses, "
                "along with gain through distant connections offset "
                "by loss in local business, and much deficiency in a "
                "spouse's comfort; its aspect on the 6th brings "
                "influence over rivals, and gain through disputes",
        },
        "Moon": {
            1: "Enemy's sign brings an unhealthy body and an anxious "
               "mind, though the native succeeds in establishing "
               "influence over rivals and winning disputes; its "
               "aspect on the 7th brings some discord regarding a "
               "spouse, and worries and difficulty in daily business",
            2: "Friend's sign brings wealth accumulated through hard "
               "effort, along with growth in family comfort; despite "
               "trouble from rivals, the native gains through "
               "disputes; its aspect on the 8th brings some trouble "
               "regarding longevity and inheritance",
            3: "Friend's sign brings growth in morale and valour, "
               "though some discord with siblings; its aspect on "
               "the 9th brings growth in fortune and religious "
               "practice after some difficulty",
            4: "Exalted, though in only a friend's sign — brings "
               "comfort through mother, land and home, along with a "
               "hold over rivals and gain through disputes; its "
               "aspect on the 10th brings difficulty through father, "
               "state and business",
            5: "Friend's sign brings success in education, "
               "intelligence and children achieved with some "
               "difficulty, along with a hold over rivals; its "
               "aspect on the 11th brings growth in income despite "
               "some difficulty, achieved through secretive method",
            6: "In its own sign here (Moon rules the 6th), brings a "
               "strong hold over rivals and success in disputes, "
               "though some worry over wealth; its aspect on the "
               "12th brings difficulty over expenses, and trouble "
               "through distant connections",
            7: "Friend's sign brings trouble through illness "
               "regarding a spouse, with success in business "
               "achieved only after difficulty, along with a hold "
               "over rivals; its aspect on the Lagna brings the body "
               "prone to illness and worry, though growing morale",
            8: "Friend's sign brings difficulty regarding longevity "
               "and inheritance, along with a hold over rivals "
               "established only after real difficulty, constant "
               "worry, and weak maternal-side connections; its "
               "aspect on the 2nd brings special effort needed for "
               "wealth and family growth",
            9: "In only a friend's sign, brings some difficulty in "
               "fortune's advance and diminished fame, along with a "
               "hold over rivals and gain through disputes; its "
               "aspect on the 3rd brings some difficulty regarding "
               "sibling comfort, though special growth in personal "
               "drive",
            10: "Friend's sign, debilitated, brings difficulty "
                "through father, state and business, along with "
                "great trouble from rivals; its aspect on the 4th "
                "brings only ordinary comfort through mother, land "
                "and home",
            11: "Friend's sign brings growth in income through "
                "morale and physical effort, along with a hold over "
                "rivals and gain through disputes; its aspect on the "
                "5th brings ample gain through education and "
                "intelligence, though some worry regarding children",
            12: "Enemy's sign brings difficulty managing expenses, "
                "and trouble through distant connections, along with "
                "mental worry caused by rivals; its aspect on the "
                "6th brings influence established over rivals "
                "through humility, and success",
        },
        "Mars": {
            1: "Enemy's sign brings physical beauty and an "
               "influential presence, along with growth in sibling "
               "comfort and valour; its aspects bring comfort "
               "through mother, land and home, comfort through a "
               "spouse and in business, and growth in longevity and "
               "inheritance",
            2: "Friend's sign brings wealth and family comfort "
               "achieved with some difficulty, along with some "
               "deficiency in sibling comfort and comfort through "
               "father; its aspects bring success in education, "
               "intelligence and children, growth in longevity and "
               "inheritance, and special advancement in fortune and "
               "religious practice, with gain in fame",
            3: "In its own sign here (Mars rules the 3rd), brings "
               "sibling comfort and special growth in valour; its "
               "aspects bring trouble from rivals with loss to "
               "maternal-side connections (debilitated), advancement "
               "in fortune and religious practice, and special "
               "success through father, state and business (own sign)",
            4: "In only a friend's sign, brings comfort through "
               "mother, land and home achieved with some deficiency; "
               "its aspects bring success with a spouse and in "
               "business through effort, advancement through father, "
               "state and business (own sign), and excellent income",
            5: "Friend's sign brings excellent comfort through "
               "education, intelligence and children, along with "
               "comfort through siblings and father and gain through "
               "state and business; its aspects bring growth in "
               "longevity and inheritance, strong income, and heavy "
               "expense offset by good gain through distant "
               "connections (exalted)",
            6: "Friend's sign brings success over rivals achieved "
               "with some difficulty, along with some discord with "
               "siblings and father and diminished standing in state "
               "affairs; its aspects bring advancement in fortune "
               "and religion through hard effort, heavy expense "
               "offset by ample gain through distant connections "
               "(exalted), and some deficiency in physical beauty "
               "though growing influence",
            7: "Friend's sign brings special success with a spouse "
               "and in daily business, along with sibling strength; "
               "its aspects bring gain through father, state and "
               "business (own sign), some deficiency in physical "
               "beauty though growth in influence and honour, and "
               "excellent wealth and family comfort",
            8: "Friend's sign brings growth in longevity and "
               "inheritance, along with some difficulty through "
               "father, state and business, and some deficiency in "
               "sibling comfort and valour; its aspects bring good "
               "income, wealth and family comfort, and growth in "
               "valour with sibling comfort (own sign)",
            9: "In only a friend's sign, brings advancement in "
               "fortune and religious practice, along with comfort "
               "through father, state and business; its aspects "
               "bring heavy expense offset by good gain through "
               "distant connections (exalted), growth in valour with "
               "sibling comfort (own sign), and excellent comfort "
               "through mother, land and home",
            10: "In its own sign here (Mars rules the 10th), brings "
                "cooperation, honour and success through father, "
                "state and business, along with growth in valour and "
                "sibling comfort; its aspects bring some deficiency "
                "in physical beauty though growth in honour, "
                "standing and influence, only ordinary comfort "
                "through mother, land and home, and growth in "
                "education, intelligence and children",
            11: "Friend's sign brings good income, along with gain "
                "through father, state and business, and growth in "
                "wealth, sibling comfort and valour; its aspects "
                "bring good savings with family comfort, excellent "
                "gain through children and education, and trouble "
                "from rivals with weak maternal-side connections "
                "(debilitated)",
            12: "Exalted in an enemy's sign, brings heavy expense "
                "offset by ample gain through distant connections, "
                "along with loss through state, father and business, "
                "though the native prospers living abroad; its "
                "aspects bring growth in sibling comfort and valour "
                "(own sign), weak standing against rivals with weak "
                "maternal-side connections (debilitated), and "
                "comfort through a spouse with success in business",
        },
        "Mercury": {
            1: "Friend's sign brings some deficiency in physical "
               "beauty and health, though gain in longevity, "
               "inheritance and children, and growth in influence "
               "and honour; its aspect on the 7th brings comfort "
               "through a spouse and gain in daily business, "
               "achieved with some difficulty",
            2: "Debilitated in a friend's sign brings inability to "
               "save wealth, and discord with family, with weak "
               "education and children; its aspect on the 8th (own "
               "sign) brings excellent strength in longevity, though "
               "incomplete gain in inheritance, achieved through "
               "discernment and learning",
            3: "Friend's sign brings trouble through siblings, and "
               "difficulty regarding children, along with valour, "
               "education and intelligence gained with some "
               "difficulty; its aspect on the 9th brings advancement "
               "in fortune and religion achieved with some difficulty",
            4: "Friend's sign brings comfort through land and home "
               "achieved with some difficulty, though some "
               "deficiency regarding mother, along with comfort "
               "through children, and growth in longevity and "
               "education too; its aspect on the 10th brings "
               "advancement in business",
            5: "In its own sign here (Mercury rules the 5th), brings "
               "comfort through children achieved with some "
               "difficulty, and excellent gain in education, marking "
               "an intelligent, discerning nature rich in eloquence; "
               "its aspect on the 11th brings special success in "
               "income through discernment",
            6: "Enemy's sign brings unrest from rivals, with success "
               "in disputes achieved only through discernment, and "
               "weak education, children, longevity and inheritance, "
               "along with real trouble; its aspect on the 12th "
               "brings heavy expense offset by gain through distant "
               "connections",
            7: "Friend's sign brings success with a spouse and in "
               "business achieved after some difficulty, along with "
               "gain in education, longevity and inheritance; its "
               "aspect on the Lagna brings some physical trouble, "
               "though growth in influence and honour",
            8: "Exalted in its own sign here (Mercury rules the "
               "8th), brings special gain in longevity and "
               "inheritance, and an influential daily life, with "
               "abundant discernment and eloquence, though some "
               "deficiency in education and children; its aspect on "
               "the 2nd (debilitated) brings difficulty saving "
               "wealth and in family comfort",
            9: "Friend's sign brings special advancement in fortune "
               "and religious practice, along with good gain in "
               "children, education, longevity and inheritance; its "
               "aspect on the 3rd brings a somewhat flawed gain in "
               "sibling comfort and valour, marking a wealthy, "
               "contented nature",
            10: "Friend's sign brings some difficulty through "
                "father, state and business, though ample gain in "
                "children, education, longevity and inheritance; its "
                "aspect on the 4th brings comfort through mother, "
                "land and home achieved with some deficiency, along "
                "with growth in fame and discernment",
            11: "Friend's sign brings excellent income, along with "
                "gain in longevity and inheritance, and a joyful "
                "daily life; its aspect on the 5th brings success in "
                "education, intelligence and children achieved with "
                "some difficulty",
            12: "Friend's sign brings heavy expense, along with some "
                "gain through distant connections, and loss to "
                "longevity and inheritance, with some deficiency in "
                "children and education; its aspect on the 6th "
                "brings success over rivals achieved through "
                "cleverness, and gain through discernment",
        },
        "Jupiter": {
            1: "Enemy's sign brings physical strength, honour and "
               "influence, along with wealth and family comfort; its "
               "aspects bring success in education, intelligence and "
               "children, success through a spouse and business, and "
               "advancement in fortune and religious practice",
            2: "In its own sign here (Jupiter rules the 2nd), brings "
               "ample wealth and family comfort; its aspects bring "
               "influence established over rivals through gain from "
               "disputes, growth in longevity and inheritance, and "
               "ample success through father, state and business",
            3: "Friend's sign brings growth in valour, along with "
               "ample gain in wealth and family comfort; its aspects "
               "bring a beautiful spouse with success in daily "
               "business and gain from in-laws, advancement in "
               "fortune through hard effort though some obstacles, "
               "and ample success through father, state and business",
            4: "In only an ordinary enemy's sign, brings some "
               "deficiency regarding mother though some gain through "
               "her, along with good comfort through land and home, "
               "and growth in wealth and family; its aspects bring "
               "growth in longevity and inheritance, success through "
               "father, state and business, and expenses managed "
               "with difficulty though ultimately fine",
            5: "Friend's sign brings excellent gain through "
               "education, intelligence and children, along with "
               "wealth and family comfort; its aspects bring "
               "advancement in fortune achieved with some "
               "difficulty, good gain in income, and growth of "
               "physical influence, fame and honour",
            6: "Friend's sign brings a heavy hold over rivals with "
               "gain through disputes, along with strong "
               "maternal-side connections, though some family "
               "trouble and difficulty in savings; its aspects bring "
               "ample gain through father, state and business, heavy "
               "expense with dissatisfying distant connections "
               "(debilitated), and growth in wealth and family "
               "through some difficulty (own sign)",
            7: "Friend's sign brings a beautiful spouse with wealth "
               "and comfort through her, and excellent gain in "
               "business, along with maintained family comfort; its "
               "aspects bring strong income (own sign), some "
               "deficiency in physical beauty though growth in "
               "honour and influence, and growth in valour with "
               "sibling comfort",
            8: "Friend's sign brings growth in longevity and "
               "inheritance, though loss to accumulated wealth and "
               "some deficiency in family comfort; its aspects bring "
               "heavy expense with trouble through distant "
               "connections, growth in wealth through special effort "
               "with family comfort, and some deficiency regarding "
               "mother though only ordinary comfort through land and "
               "home",
            9: "Enemy's sign brings special advancement in fortune "
               "and religious observance, along with ample wealth "
               "and family comfort; its aspects bring growth of "
               "physical influence, growth in sibling comfort and "
               "valour, and excellent gain through education, "
               "intelligence and children",
            10: "Friend's sign brings ample success through father, "
                "state and business, marking a grand, fortunate "
                "life; its aspects bring growth in wealth and "
                "family, ample comfort through mother, land and "
                "home, and a strong hold established over rivals "
                "through gain from disputes",
            11: "In its own sign here (Jupiter rules the 11th), "
                "brings ample growth in income, with occasional "
                "sudden gain; its aspects bring growth in valour and "
                "sibling comfort, success in children and education, "
                "and complete comfort through a spouse with ample "
                "success in daily business",
            12: "Enemy's sign brings heavy expense, trouble through "
                "distant connections, loss to accumulated wealth, "
                "and some deficiency in family comfort; its aspects "
                "bring some deficiency in comfort through mother, "
                "land and home, influence established over rivals "
                "with gain through disputes, and growth in fortune "
                "and religious observance",
        },
        "Venus": {
            1: "Friend's sign brings physical comfort, beauty and "
               "influence, along with comfort through mother, land "
               "and home, and strong religious and social standing; "
               "its aspect on the 7th brings comfort through a "
               "spouse though some difficulty in business",
            2: "Exalted, though in only a friend's sign, brings "
               "special comfort through wealth and family, and "
               "abundant comfort through mother, land and home, "
               "marking a wealthy, famous, respected nature; its "
               "aspect on the 8th brings some deficiency in "
               "longevity and inheritance, and some worry in daily "
               "life",
            3: "In only a friend's sign, brings sibling comfort and "
               "special growth in valour, along with comfort through "
               "mother, land and home; its aspect on the 9th brings "
               "great advancement in fortune, with religious duty "
               "properly kept, marking a courageous, wealthy, happy, "
               "righteous nature",
            4: "In its own sign here (Venus rules the 4th), brings "
               "comfort through mother, land and home, along with "
               "advancement in fortune and religion; its aspect on "
               "the 10th brings success through father, state and "
               "business, marking a happy, fortunate nature",
            5: "Friend's sign brings success in education and "
               "children, along with comfort through mother, land "
               "and home, and continuous advancement in fortune; its "
               "aspect on the 11th brings good gain through "
               "cleverness",
            6: "Enemy's sign brings success over rivals and gain "
               "through disputes, though some deficiency regarding "
               "mother and possible separation from one's native "
               "land, with weak land, home, fortune and religious "
               "standing; its aspect on the 12th brings heavy "
               "expense offset by success through distant connections",
            7: "Enemy's sign brings some discontent-tinged comfort "
               "through a spouse, and success in business achieved "
               "through real effort, along with ample comfort "
               "through mother and home, and effort toward fortune "
               "and religious practice; its aspect on the Lagna "
               "brings physical beauty, comfort, honour and influence",
            8: "Debilitated in a friend's sign brings an unsettled "
               "life, some deficiency in longevity and inheritance, "
               "and real weakness regarding land, home and mother; "
               "its aspect on the 2nd (exalted, and an ordinary "
               "friend's sign) brings growth in wealth and family "
               "comfort through effort",
            9: "In its own sign here (Venus rules the 9th), brings "
               "great advancement in fortune, with religious duty "
               "properly kept, along with ample comfort through "
               "mother, land and home; its aspect on the 3rd brings "
               "growth in valour, with excellent sibling comfort",
            10: "In only an ordinary friend's sign, brings ample "
                "success through father, state and business, marking "
                "a righteous, famous, respected nature; its aspect "
                "on the 4th brings ample comfort through mother, "
                "land and home",
            11: "In only an ordinary friend's sign, brings ample "
                "growth in income, marking a wealthy, just, clever, "
                "righteous, famous nature, along with excellent "
                "comfort through mother, land and home; its aspect "
                "on the 5th brings comfort through children, and "
                "good advancement in education",
            12: "Friend's sign brings heavy expense offset by gain "
                "through distant connections, and religious duty "
                "kept, though separation from parents comes at a "
                "young age, with some diminished fame; its aspect on "
                "the 6th brings victory over rivals through "
                "cleverness, and gain through disputes",
        },
        "Saturn": {
            1: "In its own sign here (Saturn is Lagna-lord), brings "
               "growth in physical beauty and influence, marking a "
               "famous, prosperous nature; its aspects bring some "
               "deficiency in sibling comfort and valour "
               "(debilitated), dissatisfaction regarding a spouse "
               "with trouble in daily business, and obstacles "
               "through father, state and business",
            2: "Enemy's sign brings savings achieved through hard "
               "effort, some deficiency in wealth and family "
               "comfort, heavy expense, standing gained through "
               "distant connections, and some deficiency in physical "
               "beauty; its aspects bring comfort through mother, "
               "land and home though some deficiency in domestic "
               "happiness, gain in longevity and inheritance, and "
               "obstacles in the path of income",
            3: "Enemy's sign brings some deficiency in valour, along "
               "with trouble through siblings, and some deficiency "
               "in physical beauty and health; its aspects bring "
               "growth in comfort through education, intelligence "
               "and children, advancement in fortune and religious "
               "practice (exalted), and trouble over expenses offset "
               "by gain through distant connections (own sign)",
            4: "Friend's sign brings full comfort through mother, "
               "land and home; its aspects bring protection from "
               "rivals through physical strength and outward "
               "security, trouble through father, state and "
               "business, and growth of physical beauty and "
               "influence (own sign)",
            5: "Friend's sign brings success in education, "
               "intelligence and children, freedom from worry, and "
               "gain through distant connections; its aspects bring "
               "difficulty regarding a spouse and business, "
               "obstacles in the path of income, and worry over "
               "wealth and family",
            6: "Enemy's sign brings growth in influence through "
               "effort and victory over rivals, though some "
               "deficiency in physical beauty; its aspects bring "
               "growth in longevity and inheritance, heavy expense "
               "offset by gain through distant connections (own "
               "sign), and some deficiency in sibling comfort and "
               "valour (debilitated)",
            7: "Enemy's sign brings trouble regarding a spouse, "
               "difficulty in business, and heavy expense; its "
               "aspects bring special advancement in fortune and "
               "religious practice (exalted), growth of physical "
               "beauty, fame, honour and influence (own sign), and "
               "comfort through mother, land and home",
            8: "Friend's sign brings growth in longevity though some "
               "loss in inheritance, along with trouble regarding "
               "the physical body and expenses, though gain through "
               "distant connections; its aspects bring discord with "
               "father alongside obstacles to advancement through "
               "state and business, flawed wealth and family "
               "comfort, and comfort through children with gain "
               "through education achieved with some deficiency",
            9: "Exalted in a friend's sign, brings ample advancement "
               "in fortune and wealth, a beautiful and healthy body, "
               "and gain through distant connections; its aspects "
               "bring some difficulty though success in the path of "
               "income, some deficiency in sibling comfort and "
               "valour (debilitated), and special effort needed to "
               "establish influence over rivals",
            10: "Enemy's sign brings success through father, state "
                "and business achieved with some difficulty; its "
                "aspects bring heavy expense offset by gain through "
                "distant connections (own sign), comfort through "
                "mother, land and home, and dissatisfaction "
                "regarding a spouse with difficulty in daily income",
            11: "Enemy's sign brings excellent growth in income "
                "along with heavy expense, offset by gain through "
                "distant connections; its aspects bring growth of "
                "physical beauty, influence and fame (own sign), "
                "ample success in education and intelligence with "
                "some flawed gain regarding children, and growth in "
                "longevity and inheritance",
            12: "In its own sign here (Saturn rules the 12th), "
                "brings heavy expense offset by special gain through "
                "distant connections, along with frequent travel; "
                "its aspects bring special effort needed for wealth "
                "and family growth, some trouble from rivals at "
                "first though influence established later, and "
                "religious duty kept with growth in fortune",
        },
        "Rahu": {
            1: "Brings injury to the body somewhere, and some "
               "deficiency in health and beauty; the native is "
               "beset by hidden worry, though establishes influence "
               "through mental strength",
            2: "Brings some deficiency in wealth and family comfort, "
               "and occasionally a severe financial crisis; the "
               "native eventually accumulates wealth through "
               "secretive method and hard effort, and comes to be "
               "regarded as wealthy and fortunate, being quite bold",
            3: "Brings great growth in valour, though discord with "
               "siblings; the native achieves success and comfort "
               "through cleverness and secretive method, and earns a "
               "respected place in society",
            4: "Brings great trouble through the mother's side, an "
               "unsettled domestic life, and some deficiency in "
               "comfort through land and home, though after much "
               "struggle the native achieves real success",
            5: "Brings some initial trouble regarding children that "
               "later turns to comfort, along with special gain in "
               "education and intelligence; the native is skilled at "
               "hiding their inner weaknesses, and is influential "
               "and sweet-spoken",
            6: "Brings a heavy hold over rivals, and success in "
               "disputes and quarrels through intelligence; though "
               "inwardly troubled, the native never abandons "
               "patience and courage, and ultimately prevails over "
               "every difficulty",
            7: "Brings great trouble regarding a spouse, and "
               "difficulty in the field of daily income, though the "
               "native ultimately prevails over every difficulty "
               "through patience, courage and hard effort",
            8: "Brings many crises to life, and loss to inheritance, "
               "with disorder in the lower body, though the native "
               "lives a long life and manages it capably through "
               "discernment and intelligence",
            9: "Brings obstacles to fortune's advance, and improper "
               "observance of religious duty, though the native "
               "ultimately prevails over every difficulty through "
               "sharp wit, and does not let their weaknesses show",
            10: "Brings trouble through the father, difficulty "
                "through state affairs, and loss in business, though "
                "the native struggles through with effort and "
                "cleverness and ultimately achieves success",
            11: "Brings great difficulty in the path of income, "
                "though the native achieves some victory through the "
                "power of intelligence, never letting their "
                "difficulties show to others",
            12: "Brings great difficulty over expenses, though some "
                "gain through distant connections; the native must "
                "work hard to manage their spending",
        },
        "Ketu": {
            1: "Brings a mark or scar somewhere on the body, and "
               "some diminishment of physical beauty; the native is "
               "bold, capable, skilled in secretive method and "
               "hard-working, and earns respect through these very "
               "qualities",
            2: "Brings trouble regarding wealth and family comfort, "
               "with constant new upheaval in the family; the native "
               "tries to earn wealth through patience, hard effort "
               "and honest means, and ultimately achieves some success",
            3: "Brings great growth in valour, though some "
               "deficiency in sibling comfort; the native is bold, "
               "patient, hard-working, industrious and skilled in "
               "secretive method, and ultimately advances their life "
               "through these very qualities",
            4: "Brings loss or deficiency in comfort through mother, "
               "including separation from one's native land, and "
               "some deficiency in comfort through land and home "
               "too, though the native later achieves some success "
               "in resolving these deficiencies through secretive "
               "method",
            5: "Brings difficulty gaining comfort through children, "
               "requiring painful effort and secretive method, and "
               "even then only slight comfort results; real "
               "difficulty in education too, with an unsettled mind "
               "and somewhat diminished character and discernment",
            6: "Brings unrest caused by rivals, though the native "
               "succeeds in establishing influence and achieving "
               "victory over them; outwardly the native appears bold "
               "and fearless despite inner fear, being patient, "
               "hard-working and skilled in secretive method",
            7: "Brings special trouble regarding a spouse, and "
               "crises in business, along with disorder in the "
               "reproductive organs; the native ultimately achieves "
               "ordinary success through effort and secretive method",
            8: "Brings growth in longevity, though occasionally "
               "severe crises threatening life; ordinary gain in "
               "inheritance, with occasional loss too, though the "
               "native ultimately manages to resolve difficulties "
               "through secretive method",
            9: "Brings obstacles to fortune's advance, and no "
               "special advancement in religious practice, though "
               "the native advances their fortune through secretive "
               "method, patience and hard effort, never growing "
               "discouraged despite repeated setbacks",
            10: "Brings great trouble through the father, difficulty "
                "through state affairs, and loss in business, though "
                "the native ultimately prevails over these setbacks "
                "through righteousness, courage and cleverness",
            11: "Brings great growth in income, with occasional "
                "sudden gain too; the native strives for advancement "
                "and earns great wealth through honest means, living "
                "happily",
            12: "Brings heavy expense causing difficulty, though the "
                "native prevails through secretive method, never "
                "losing courage even amid despair; some gain through "
                "distant connections comes too",
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
