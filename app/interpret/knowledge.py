"""Delineation vocabulary.

The numbers come from the ephemeris; the meaning comes from here. Entries are
written as reusable *ingredients* (a planet's verb, a sign's style, a house's
field) which the engine composes into sentences, so that every statement in an
answer is traceable to a specific placement rather than to boilerplate.

Sources are mainstream traditional/modern synthesis: Ptolemy and Lilly for
dignity and sect, Hellenistic house significations, and standard modern
psychological delineation for the outer planets.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Planets
# --------------------------------------------------------------------------

PLANETS: dict[str, dict] = {
    "Sun": {
        "core": "your sense of purpose and the self you are becoming",
        "verb": "shines, leads and takes credit",
        "gift": "vitality, confidence, a centre of gravity others orient around",
        "shadow": "pride, over-identification with being seen, burnout from carrying everything",
        "body": "heart, spine, general vitality",
        "careers": ["leadership", "public-facing roles", "anything you can put your name on"],
        "keywords": ["identity", "will", "recognition", "father", "authority"],
    },
    "Moon": {
        "core": "your instincts, needs and inner weather",
        "verb": "feels, absorbs and seeks safety",
        "gift": "emotional intelligence, memory, the ability to care and be cared for",
        "shadow": "moodiness, clinging to what is familiar rather than what is good",
        "body": "stomach, fluids, sleep, the breasts",
        "careers": ["care work", "food", "property", "public mood", "anything nurturing"],
        "keywords": ["needs", "habits", "home", "mother", "the public"],
    },
    "Mercury": {
        "core": "how you think, learn and make yourself understood",
        "verb": "connects, analyses and negotiates",
        "gift": "quick perception, articulacy, skill with systems and language",
        "shadow": "overthinking, nervous scattering, cleverness in place of conviction",
        "body": "nerves, lungs, hands, speech",
        "careers": ["writing", "teaching", "trade", "analysis", "software", "advisory work"],
        "keywords": ["mind", "communication", "siblings", "commerce", "skill"],
    },
    "Venus": {
        "core": "what you value, enjoy and want to be close to",
        "verb": "attracts, harmonises and appraises",
        "gift": "charm, taste, the ability to make peace and make things beautiful",
        "shadow": "conflict-avoidance, indulgence, valuing being liked over being honest",
        "body": "kidneys, throat, skin, hormonal balance",
        "careers": ["design", "art", "luxury", "diplomacy", "hospitality", "relationships"],
        "keywords": ["love", "money", "beauty", "pleasure", "agreement"],
    },
    "Mars": {
        "core": "your drive, courage and capacity to fight for something",
        "verb": "cuts, competes and acts",
        "gift": "initiative, physical courage, the willingness to be disliked",
        "shadow": "temper, impatience, force applied where finesse was needed",
        "body": "muscles, blood, inflammation, injuries and surgery",
        "careers": ["engineering", "surgery", "military and police", "sport", "entrepreneurship"],
        "keywords": ["action", "anger", "desire", "risk", "conflict"],
    },
    "Jupiter": {
        "core": "where you grow, trust and are given room",
        "verb": "expands, blesses and believes",
        "gift": "optimism, opportunity, generosity, the long view",
        "shadow": "overreach, complacency, promising more than can be delivered",
        "body": "liver, thighs, growth, weight",
        "careers": ["law", "academia", "publishing", "finance", "religion", "consulting"],
        "keywords": ["luck", "growth", "wisdom", "abundance", "teachers"],
    },
    "Saturn": {
        "core": "where you must earn it slowly, and what you become by doing so",
        "verb": "limits, tests and consolidates",
        "gift": "discipline, endurance, authority that is actually deserved",
        "shadow": "fear, rigidity, self-denial mistaken for virtue",
        "body": "bones, teeth, skin, knees, chronic conditions",
        "careers": ["administration", "civil service", "construction", "law", "long institutions"],
        "keywords": ["structure", "time", "duty", "restriction", "mastery"],
    },
    "Uranus": {
        "core": "where you break the pattern and refuse to be standard",
        "verb": "disrupts, liberates and shocks",
        "gift": "originality, independence, sudden clarity",
        "shadow": "restlessness, contrarianism, blowing up what could have been repaired",
        "body": "nervous system, spasms, circulation",
        "careers": ["technology", "research", "activism", "startups", "anything unprecedented"],
        "keywords": ["change", "freedom", "invention", "rupture"],
    },
    "Neptune": {
        "core": "where you dissolve boundaries — through imagination, faith or illusion",
        "verb": "blurs, inspires and idealises",
        "gift": "compassion, artistry, spiritual receptivity",
        "shadow": "confusion, escapism, deceiving yourself before anyone else does",
        "body": "immune system, feet, sensitivities, reactions to substances",
        "careers": ["art", "film", "music", "healing", "spiritual and charitable work"],
        "keywords": ["dreams", "faith", "illusion", "sacrifice", "the unseen"],
    },
    "Pluto": {
        "core": "where you are remade, usually not gently",
        "verb": "buries, intensifies and transforms",
        "gift": "psychological depth, resilience, real power",
        "shadow": "control, obsession, power struggles you did not admit to entering",
        "body": "reproductive system, elimination, deep-seated conditions",
        "careers": ["psychology", "research", "surgery", "finance", "crisis work", "investigation"],
        "keywords": ["power", "death and rebirth", "obsession", "the hidden"],
    },
    "Chiron": {
        "core": "the wound you cannot fully heal in yourself but can heal in others",
        "verb": "aches, teaches and mends",
        "gift": "hard-won wisdom, the ability to help people in exactly your kind of pain",
        "shadow": "picking at the wound, defining yourself by what hurt you",
        "body": "chronic aches, old injuries",
        "careers": ["therapy", "mentoring", "alternative medicine", "teaching"],
        "keywords": ["wound", "healing", "mentorship"],
    },
    "North Node": {
        "core": "the direction of growth — unfamiliar, uncomfortable, and correct",
        "verb": "pulls forward",
        "gift": "development into something you were not born already good at",
        "shadow": "avoidance, retreating to the South Node's easy competence",
        "body": "",
        "careers": [],
        "keywords": ["destiny", "growth edge", "the unfamiliar"],
    },
    "South Node": {
        "core": "innate competence that is comfortable and quietly limiting",
        "verb": "pulls back",
        "gift": "talent that arrives without training",
        "shadow": "over-reliance on an old strength instead of building a new one",
        "body": "",
        "careers": [],
        "keywords": ["the past", "ease", "release"],
    },
}

# stellium names the true node "True Node"; treat it as the North Node.
PLANETS["True Node"] = PLANETS["North Node"]

# --------------------------------------------------------------------------
# Signs
# --------------------------------------------------------------------------

SIGNS: dict[str, dict] = {
    "Aries": {
        "style": "directly and impatiently, wanting to move first",
        "drive": "to prove itself through action",
        "shadow": "starts more than it finishes; heat without aim",
        "keywords": ["bold", "competitive", "pioneering", "blunt"],
    },
    "Taurus": {
        "style": "steadily and physically, refusing to be hurried",
        "drive": "to build something solid and keep it",
        "shadow": "stubbornness, inertia, comfort chosen over growth",
        "keywords": ["patient", "sensual", "reliable", "immovable"],
    },
    "Gemini": {
        "style": "quickly and curiously, gathering options",
        "drive": "to know a little about everything and stay free to change",
        "shadow": "scattered attention, talk substituting for depth",
        "keywords": ["versatile", "witty", "restless", "clever"],
    },
    "Cancer": {
        "style": "protectively and indirectly, moving through feeling",
        "drive": "to build safety for itself and the people it claims",
        "shadow": "defensiveness, holding on long past the point of use",
        "keywords": ["caring", "loyal", "guarded", "tenacious"],
    },
    "Leo": {
        "style": "warmly and visibly, wanting the effort to be seen",
        "drive": "to matter to people, and to do it with style",
        "shadow": "pride, needing the audience more than the work",
        "keywords": ["generous", "dramatic", "loyal", "proud"],
    },
    "Virgo": {
        "style": "precisely and usefully, improving as it goes",
        "drive": "to be genuinely good at something that helps",
        "shadow": "self-criticism, perfectionism that delays the finish",
        "keywords": ["exacting", "practical", "modest", "analytical"],
    },
    "Libra": {
        "style": "diplomatically and comparatively, weighing both sides",
        "drive": "to be in fair, elegant relationship with others",
        "shadow": "indecision, appeasement, losing itself in the other person",
        "keywords": ["fair", "charming", "relational", "hesitant"],
    },
    "Scorpio": {
        "style": "intensely and privately, all-in or not at all",
        "drive": "to get to the truth underneath and survive it",
        "shadow": "control, suspicion, grudges kept in cold storage",
        "keywords": ["deep", "magnetic", "strategic", "unforgiving"],
    },
    "Sagittarius": {
        "style": "expansively and frankly, aiming past the horizon",
        "drive": "to find meaning worth travelling for",
        "shadow": "restlessness, tactlessness, allergy to the fine print",
        "keywords": ["adventurous", "honest", "philosophical", "impatient"],
    },
    "Capricorn": {
        "style": "seriously and strategically, playing the long game",
        "drive": "to build something that outlasts and earns respect",
        "shadow": "coldness, workaholism, delaying life until the goal is met",
        "keywords": ["ambitious", "disciplined", "responsible", "austere"],
    },
    "Aquarius": {
        "style": "coolly and unconventionally, from a step outside",
        "drive": "to improve the system and stay unowned by it",
        "shadow": "detachment, principle preferred to people",
        "keywords": ["original", "independent", "humane", "aloof"],
    },
    "Pisces": {
        "style": "fluidly and empathically, without hard edges",
        "drive": "to dissolve into something larger than itself",
        "shadow": "boundarylessness, drift, escape when reality presses",
        "keywords": ["compassionate", "imaginative", "impressionable", "elusive"],
    },
}

# --------------------------------------------------------------------------
# Houses
# --------------------------------------------------------------------------

HOUSES: dict[int, dict] = {
    1: {"field": "your body, temperament and the way you arrive in a room",
        "topics": ["self", "vitality", "appearance", "outlook", "beginnings"]},
    2: {"field": "your earned money, possessions and sense of worth",
        "topics": ["income", "savings", "resources", "self-worth", "food"]},
    3: {"field": "your immediate world — siblings, short trips, daily communication",
        "topics": ["siblings", "communication", "learning", "neighbours", "local travel"]},
    4: {"field": "home, family, roots and the private base you return to",
        "topics": ["home", "family", "parents", "property", "endings", "old age"]},
    5: {"field": "children, romance, creativity and play",
        "topics": ["children", "romance", "creativity", "pleasure", "speculation"]},
    6: {"field": "daily work, health, routine and service",
        "topics": ["health", "work", "routine", "colleagues", "illness", "pets"]},
    7: {"field": "marriage, partnership and open dealings with others",
        "topics": ["marriage", "partnership", "contracts", "clients", "open enemies"]},
    8: {"field": "shared resources, debt, crisis and what transforms you",
        "topics": ["inheritance", "debt", "other people's money", "crisis", "intimacy", "the occult"]},
    9: {"field": "belief, higher study, long journeys and the foreign",
        "topics": ["higher education", "philosophy", "religion", "foreign travel", "law", "teachers"]},
    10: {"field": "career, standing, reputation and public role",
         "topics": ["career", "reputation", "authority", "achievement", "employers"]},
    11: {"field": "friends, networks, gains and what you hope for",
         "topics": ["friends", "networks", "gains", "hopes", "communities", "patrons"]},
    12: {"field": "solitude, the unconscious, loss and what happens behind the scenes",
         "topics": ["isolation", "hidden enemies", "spirituality", "institutions", "self-undoing", "foreign lands"]},
}

# --------------------------------------------------------------------------
# Aspects
# --------------------------------------------------------------------------

ASPECTS: dict[str, dict] = {
    "conjunction": {"nature": "fusing",
                    "verb": "fuses with", "note": "the two act as one; the stronger colours the weaker"},
    "opposition": {"nature": "hard",
                   "verb": "opposes", "note": "a tug-of-war usually externalised onto other people"},
    "square": {"nature": "hard",
               "verb": "squares", "note": "friction that forces development; the most productive difficulty"},
    "trine": {"nature": "harmonious",
              "verb": "trines", "note": "easy flow, so easy it is often taken for granted"},
    "sextile": {"nature": "harmonious",
                "verb": "sextiles", "note": "an opportunity that has to be picked up deliberately"},
    "quincunx": {"nature": "minor", "verb": "is quincunx",
                 "note": "two drives that cannot be reconciled, only alternated"},
    "semisextile": {"nature": "minor", "verb": "is semisextile", "note": "a mild, adjacent tension"},
    "semisquare": {"nature": "minor", "verb": "is semisquare", "note": "a low-grade irritation"},
    "sesquiquadrate": {"nature": "minor", "verb": "is sesquiquadrate", "note": "delayed friction"},
    "quintile": {"nature": "minor", "verb": "quintiles", "note": "a talent with an idiosyncratic flavour"},
}

# --------------------------------------------------------------------------
# Condition modifiers
# --------------------------------------------------------------------------

DIGNITY_TEXT = {
    "domicile": "in its own sign, fully able to act on its own terms",
    "rulership": "in its own sign, fully able to act on its own terms",
    "exaltation": "exalted — honoured, given more than it strictly earned",
    "triplicity": "in its own triplicity, well supported",
    "term": "in its own bounds, with modest working strength",
    "face": "in its own face, with minimal but real footing",
    "decan": "in its own decan, with minimal but real footing",
    "detriment": "in detriment — working against the grain of the sign",
    "fall": "in fall — undervalued, its efforts landing badly",
    "peregrine": "peregrine — no essential dignity, so it borrows its footing from elsewhere",
}

SOLAR_PHASE_TEXT = {
    "cazimi": "cazimi (exactly with the Sun) — hidden in plain sight and unusually potent",
    "combust": "combust — burnt up by the Sun, its agenda hard to see clearly or act on freely",
    "under the beams": "under the Sun's beams — somewhat obscured",
    "free": "free of the Sun",
    "n/a": "",
}

PLACEMENT_TEXT = {
    "angular": "angular, so it acts fast and visibly",
    "succedent": "succedent, so it accumulates and holds rather than initiates",
    "cadent": "cadent, so it works indirectly, behind the scenes or through preparation",
}

# --------------------------------------------------------------------------
# Hand-written delineations for the three most consequential placements
# --------------------------------------------------------------------------

RISING = {
    "Aries": "You come at life head-first. People read you as direct, energetic and a little combative "
             "before you have said anything. Your life tends to be structured around challenges you pick.",
    "Taurus": "You present as calm, solid and unhurried. People find you steadying and occasionally "
              "immovable. Your life organises itself around comfort, security and things you can touch.",
    "Gemini": "You present as quick, curious and conversational. People underestimate your seriousness. "
              "Your life is organised around information, mobility and keeping options open.",
    "Cancer": "You present as warm but guarded, and people sense there is more underneath. Your life is "
              "organised around belonging — building a base and defending it.",
    "Leo": "You present with warmth and presence; rooms notice you. Your life is organised around "
           "doing something worth being recognised for, and around your own dignity.",
    "Virgo": "You present as competent, observant and a little reserved. Your life is organised around "
             "being useful and getting the details right — including on yourself.",
    "Libra": "You present as pleasant, well-mannered and socially fluent. Your life is organised around "
             "other people — partnership, fairness, and the constant weighing of options.",
    "Scorpio": "You present as controlled and hard to read, and people feel the intensity anyway. Your "
               "life is organised around depth, privacy and periodic total transformation.",
    "Sagittarius": "You present as open, blunt and optimistic. Your life is organised around expansion — "
                   "travel, study, belief, and the freedom to go where the meaning is.",
    "Capricorn": "You present as serious, capable and older than you are. Your life is organised around "
                 "building something real, slowly, and being taken seriously for it.",
    "Aquarius": "You present as friendly but detached, clearly your own person. Your life is organised "
                "around independence and around systems and groups you want to improve.",
    "Pisces": "You present as gentle, receptive and slightly hard to pin down. Your life is organised "
              "around sensitivity, imagination and a pull towards something beyond the ordinary.",
}

SUN_SIGN = {
    "Aries": "you become yourself by initiating and competing",
    "Taurus": "you become yourself by building steadily and holding your ground",
    "Gemini": "you become yourself by learning, connecting and communicating",
    "Cancer": "you become yourself by caring for and protecting what is yours",
    "Leo": "you become yourself by creating something you can be proud of in public",
    "Virgo": "you become yourself by mastering a craft and making it useful",
    "Libra": "you become yourself through relationship, fairness and taste",
    "Scorpio": "you become yourself by going all the way down and coming back changed",
    "Sagittarius": "you become yourself by seeking meaning and refusing to be fenced in",
    "Capricorn": "you become yourself by taking on responsibility and earning authority",
    "Aquarius": "you become yourself by thinking independently and serving something collective",
    "Pisces": "you become yourself by dissolving the ego into compassion, art or faith",
}

MOON_SIGN = {
    "Aries": "you need action and autonomy; you settle by doing something, not by talking",
    "Taurus": "you need physical steadiness — routine, comfort, and not being rushed",
    "Gemini": "you need mental stimulation and someone to talk it through with",
    "Cancer": "you need closeness and a safe base; feelings run deep and are well remembered",
    "Leo": "you need to be appreciated, warmly and specifically, by people who matter to you",
    "Virgo": "you need order and usefulness; anxiety shows up as fixing and tidying",
    "Libra": "you need harmony and company; conflict costs you more than it costs most people",
    "Scorpio": "you need emotional truth and privacy; you feel things at full intensity or not at all",
    "Sagittarius": "you need room, honesty and something to look forward to",
    "Capricorn": "you need competence and control; you self-soothe by getting on with the work",
    "Aquarius": "you need space and perspective; you process feelings at a slight remove",
    "Pisces": "you need beauty, quiet and permeable boundaries; you absorb the mood of the room",
}


# Melothesia — the classical body-zone rulership of the signs, used when a
# question is about health rather than as general-purpose symbolism.
SIGN_BODY = {
    "Aries": "head, face and eyes; fevers and inflammation",
    "Taurus": "throat, neck and thyroid",
    "Gemini": "lungs, arms, shoulders and the nervous system",
    "Cancer": "stomach, chest and digestion; fluid retention",
    "Leo": "heart, spine and upper back",
    "Virgo": "intestines, gut and the assimilation of food",
    "Libra": "kidneys, lower back and the acid–alkaline balance",
    "Scorpio": "reproductive and eliminative organs",
    "Sagittarius": "hips, thighs, liver and the sciatic nerve",
    "Capricorn": "knees, bones, joints, teeth and skin",
    "Aquarius": "calves, ankles and the circulation",
    "Pisces": "feet, lymphatic system and immune sensitivity",
}


def planet(name: str) -> dict:
    return PLANETS.get(name, {
        "core": name, "verb": "operates", "gift": "", "shadow": "",
        "body": "", "careers": [], "keywords": [],
    })


def sign(name: str) -> dict:
    return SIGNS.get(name, {"style": "", "drive": "", "shadow": "", "keywords": []})


def house(number: int) -> dict:
    return HOUSES.get(number, {"field": f"house {number}", "topics": []})


def aspect(name: str) -> dict:
    return ASPECTS.get(name.lower(), {"nature": "minor", "verb": "aspects", "note": ""})
