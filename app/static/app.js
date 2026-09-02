/* ============================================================
   Astro — front end
   No frameworks, no CDN. Everything below runs offline.
   ============================================================ */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const state = {
  place: null,
  sessionId: null,
  chart: null,
  busy: false,
  lang: localStorage.getItem("astro.lang") || "en",
  // Empty means "the visitor has never chosen" — the server decides in that
  // case (GET /api/llm -> default), so turning Claude on needs no client change.
  //
  // Deliberately a NEW key. The old "astro.provider" was rewritten on every
  // page load, so every existing visitor had "off" pinned into storage and
  // would have stayed on the rule-engine wording forever, whatever the server
  // recommended. Only an explicit change to the picker writes this one.
  provider: localStorage.getItem("astro.narration") || "",
  providers: [],
  // "north" (Vedic diamond) | "south" (Vedic square) | "wheel" (Western SVG)
  chartStyle: localStorage.getItem("astro.chartStyle") || "north",
  wheelSvg: "",
  now: null,
  dasha: null,
  dashaCheck: null,
  births: [],            // saved charts; only ever filled for a signed-in user
  birthMax: 5,           // the server's cap, echoed by GET /api/births
  // Which saved birth profile (if any) the on-screen chart came from, so
  // chat history can be scoped to just this chart's questions. Set when the
  // "load a saved chart" dropdown fires, cleared the moment any birth-form
  // field is hand-edited afterward (see the #birth-form guard listener) so
  // an edited-then-cast chart never gets attributed to the wrong profile.
  selectedBirthId: null,
  currentBirthId: null,
};

/* ------------------------------------------------------------
   i18n — UI chrome and chart vocabulary. Fully offline.
   The narrative itself is translated by the LLM layer when enabled.
   ------------------------------------------------------------ */
const I18N = {
  en: {
    tagline: "Swiss-Ephemeris precision, Vedic judgement — your chart read properly.",
    name: "Name", optional: "optional", namePh: "Who is this chart for?",
    dob: "Date of birth", tob: "Time of birth",
    unknownTime: "I don't know the exact time",
    unknownHint: "— houses and the ascendant become unreliable; noon is used",
    pob: "Place of birth", pobPh: "Start typing a city…",
    advanced: "Advanced settings", zodiac: "Zodiac", houseSystem: "House system",
    tropical: "Tropical (Western)", sidereal: "Sidereal (Vedic / Jyotish)",
    ayanamsa: "Ayanamsa", cast: "Cast the chart", casting: "Consulting the ephemeris…",
    footnote: "Nothing leaves this computer. Birth data is held in memory only.",
    pickPlace: "Pick a birth place from the suggestions so the coordinates and timezone are exact.",
    narration: "Narration",
    chartStyle: "Chart style",
    styleNorth: "North Indian", styleSouth: "South Indian", styleWheel: "Western wheel",
    styleNorthFull: "North Indian (Vedic diamond)",
    styleSouthFull: "South Indian (Vedic square)",
    styleWheelFull: "Western wheel",
    rashiChart: "Rashi (D-1)", lagnaLbl: "Lagna",
    wholeSignNote: "Whole-sign rashi chart — houses counted from the Lagna.",
    mahadashaTable: "Vimshottari mahadasha", antardashaTable: "Antardasha",
    dashaLord: "Lord", dashaFrom: "From", dashaTo: "To",
    running: "running now", yrs: "yrs",
    balanceAtBirth: "balance at birth", atBirth: "at birth",
    expandHint: "Open a mahadasha to see its antardashas.",
    noDasha: "Vimshottari dasha needs a sidereal (Vedic) chart. Recast with the sidereal zodiac to see mahadashas and antardashas.",
    moonAt: "Moon at",
    placements: "Placements", houses: "Houses", aspects: "Aspects", now: "Now",
    askPh: "Ask about career, money, love, health, timing…",
    reading: "Reading the chart…", writing: "Writing it out…",
    responseTruncated: "The response may have been cut short — ask a follow-up to continue it.",
    responseStopped: "Stopped.",
    responseDropped: "Connection dropped — this answer may be incomplete.",
    elemental: "Elemental balance", patterns: "Patterns", cusps: "cusps",
    angular: "Angular", succedent: "Succedent", cadent: "Cadent",
    annualProfection: "Annual profection", lordOfYear: "lord of the year",
    monthly: "Monthly", releasing: "Zodiacal releasing", firdaria: "Firdaria",
    dasha: "Vimshottari dasha", mahadasha: "mahadasha", antardasha: "antardasha",
    nakshatra: "Moon in", pada: "pada", asOf: "As of", age: "age",
    reasoningOne: "The reasoning —", reasoningTwo: "chart factors weighed",
    score: "Weighted verdict score", routedTo: "routed to", intent: "intent",
    savedTitle: "Your saved charts", savedSlots: "saved",
    savedSub: "Open one with a tap, or cast a new chart below.",
    castAnother: "+ Cast a new chart",
    homeCta: "Get my kundali reading",
    homeBlurb: "Your kundali cast to the exact minute, with dashas, North and "
             + "South Indian charts, and straight answers to your questions in "
             + "Hindi or English.",
    birthTitle: "Your birth details",
    birthSub: "Exact time and place — the chart is only as good as these.",
    point1: "Swiss Ephemeris — the same data professional astrologers use",
    point2: "Vimshottari dashas, transits and timing windows",
    point3: "Answers in plain language, in Hindi or English",
    gender: "Gender", genderNone: "Prefer not to say",
    genderFemale: "Female", genderMale: "Male", genderOther: "Other",
    savedFullHint: "That is the lot — delete one to make room for a new chart.",
    savedRename: "Rename", savedDelete: "Delete",
    savedRenamePrompt: "What should this chart be called?",
    savedDeleteConfirm: "Delete this saved chart? You can always cast it again.",
    savedFullOne: "You are already keeping all", savedFullTwo:
      "saved charts, so this one was not saved. Delete one to make room.",
    savedFailed: "That chart could not be opened.",
    newChart: "New chart", asc: "Asc / Lagna", sun: "Sun", moon: "Moon",
    sect: "Sect", diurnal: "Diurnal", nocturnal: "Nocturnal",
    housesLbl: "Houses", zodiacLbl: "Zodiac",
    polishedBy: "Rewritten by", engineText: "The engine's own wording",
    llmFailed: "Narration failed — showing the engine's wording",
    starters: [
      "What am I actually like?",
      "How is my career looking?",
      "When will I get married?",
      "Will money improve in the next two years?",
      "What is happening in my life right now?",
      "Where are my health vulnerabilities?",
      "Should I move abroad?",
      "What are my biggest strengths and blind spots?",
      "I got married in 2012 — what was my chart doing?",
    ],
    mangalTitle: "Mangal Dosha", milanNeedDate: "Both dates of birth are needed.",
    milanNeedPlace: "Pick both birth places from the suggestions so the coordinates are exact.",
    until: "until", tithiL: "Tithi", nakL: "Nakshatra", yogaL: "Yoga", karanaL: "Karana",
    timingsL: "Timings", none: "none today",
  },
  hi: {
    tagline: "स्विस एफ़ेमेरिस की सटीकता, वैदिक विवेचन — आपकी कुंडली, सही ढंग से।",
    name: "नाम", optional: "वैकल्पिक", namePh: "यह कुंडली किसकी है?",
    dob: "जन्म तिथि", tob: "जन्म समय",
    unknownTime: "मुझे सही समय नहीं पता",
    unknownHint: "— भाव और लग्न अविश्वसनीय हो जाएँगे; दोपहर का समय लिया जाएगा",
    pob: "जन्म स्थान", pobPh: "शहर का नाम लिखना शुरू करें…",
    advanced: "विस्तृत सेटिंग्स", zodiac: "राशि पद्धति", houseSystem: "भाव पद्धति",
    tropical: "सायन (पाश्चात्य)", sidereal: "निरयन (वैदिक / ज्योतिष)",
    ayanamsa: "अयनांश", cast: "कुंडली बनाएँ", casting: "पंचांग देखा जा रहा है…",
    footnote: "कोई भी जानकारी इस कंप्यूटर से बाहर नहीं जाती। जन्म-विवरण केवल मेमोरी में रहता है।",
    pickPlace: "सुझावों में से जन्म स्थान चुनें ताकि अक्षांश-देशांतर और समय-क्षेत्र सही रहें।",
    narration: "वर्णन",
    chartStyle: "कुंडली शैली",
    styleNorth: "उत्तर भारतीय", styleSouth: "दक्षिण भारतीय", styleWheel: "पाश्चात्य चक्र",
    styleNorthFull: "उत्तर भारतीय (वैदिक)",
    styleSouthFull: "दक्षिण भारतीय (वैदिक)",
    styleWheelFull: "पाश्चात्य चक्र",
    rashiChart: "राशि चक्र (D-1)", lagnaLbl: "लग्न",
    wholeSignNote: "पूर्ण-राशि (चलित रहित) राशि कुंडली — भाव लग्न से गिने गए हैं।",
    mahadashaTable: "विंशोत्तरी महादशा", antardashaTable: "अंतर्दशा",
    dashaLord: "स्वामी", dashaFrom: "आरंभ", dashaTo: "समाप्ति",
    running: "वर्तमान", yrs: "वर्ष",
    balanceAtBirth: "जन्म के समय शेष", atBirth: "जन्म पर",
    expandHint: "अंतर्दशा देखने के लिए किसी महादशा पर क्लिक करें।",
    noDasha: "विंशोत्तरी दशा के लिए निरयन (वैदिक) कुंडली आवश्यक है। महादशा और अंतर्दशा देखने हेतु निरयन राशि पद्धति चुनकर कुंडली दोबारा बनाएँ।",
    moonAt: "चंद्र",
    placements: "ग्रह स्थिति", houses: "भाव", aspects: "दृष्टि", now: "वर्तमान",
    askPh: "करियर, धन, विवाह, स्वास्थ्य, समय — कुछ भी पूछें…",
    reading: "कुंडली पढ़ी जा रही है…", writing: "उत्तर लिखा जा रहा है…",
    responseTruncated: "उत्तर अधूरा रह गया हो सकता है — जारी रखने के लिए अगला प्रश्न पूछें।",
    responseStopped: "रोक दिया गया।",
    responseDropped: "कनेक्शन टूट गया — यह उत्तर अधूरा हो सकता है।",
    elemental: "तत्व संतुलन", patterns: "योग", cusps: "आरंभ",
    angular: "केन्द्र", succedent: "पणफर", cadent: "आपोक्लिम",
    annualProfection: "वार्षिक प्रोफ़ेक्शन", lordOfYear: "वर्षेश",
    monthly: "मासिक", releasing: "ज़ोडिएकल रिलीज़िंग", firdaria: "फ़िरदारिया",
    dasha: "विंशोत्तरी दशा", mahadasha: "महादशा", antardasha: "अंतर्दशा",
    nakshatra: "चंद्र नक्षत्र", pada: "पाद", asOf: "दिनांक", age: "आयु",
    reasoningOne: "तर्क —", reasoningTwo: "कुंडली-तत्वों का आकलन",
    score: "भारित निर्णय अंक", routedTo: "विषय", intent: "प्रश्न-प्रकार",
    savedTitle: "आपकी सहेजी कुंडलियाँ", savedSlots: "सहेजी गईं",
    savedSub: "किसी पर क्लिक करके पढ़ें, या नीचे नई कुंडली बनाएँ।",
    castAnother: "+ नई कुंडली बनाएँ",
    homeCta: "मेरी कुंडली पढ़ें",
    homeBlurb: "आपकी कुंडली सटीक मिनट पर बनाई जाती है — दशाएँ, उत्तर और दक्षिण "
             + "भारतीय चार्ट, और आपके प्रश्नों के सीधे उत्तर, हिन्दी या अंग्रेज़ी में।",
    birthTitle: "आपका जन्म विवरण",
    birthSub: "सटीक समय और स्थान — कुंडली इन्हीं पर निर्भर करती है।",
    point1: "स्विस एफ़ेमेरिस — वही गणना जो पेशेवर ज्योतिषी उपयोग करते हैं",
    point2: "विंशोत्तरी दशा, गोचर और समय-अवधि",
    point3: "सरल भाषा में उत्तर, हिन्दी या अंग्रेज़ी में",
    gender: "लिंग", genderNone: "बताना नहीं चाहते",
    genderFemale: "स्त्री", genderMale: "पुरुष", genderOther: "अन्य",
    savedFullHint: "सीमा पूरी — नई कुंडली के लिए जगह बनाने हेतु एक हटाएँ।",
    savedRename: "नाम बदलें", savedDelete: "हटाएँ",
    savedRenamePrompt: "इस कुंडली को क्या नाम दें?",
    savedDeleteConfirm: "यह सहेजी कुंडली हटाएँ? आप इसे दोबारा बना सकते हैं।",
    savedFullOne: "आपके पास पहले से पूरी", savedFullTwo:
      "कुंडलियाँ सहेजी हैं, इसलिए यह सहेजी नहीं गई। जगह बनाने के लिए एक हटाएँ।",
    savedFailed: "यह कुंडली नहीं खुल सकी।",
    newChart: "नई कुंडली", asc: "लग्न", sun: "सूर्य", moon: "चंद्र",
    sect: "पक्ष", diurnal: "दिवा", nocturnal: "रात्रि",
    housesLbl: "भाव", zodiacLbl: "राशि",
    polishedBy: "पुनर्लेखन:", engineText: "इंजन का मूल पाठ",
    llmFailed: "वर्णन विफल — इंजन का मूल पाठ दिखाया जा रहा है",
    starters: [
      "मेरा स्वभाव कैसा है?",
      "मेरा करियर कैसा रहेगा?",
      "मेरा विवाह कब होगा?",
      "अगले दो वर्षों में धन की स्थिति सुधरेगी?",
      "अभी मेरे जीवन में क्या चल रहा है?",
      "मेरे स्वास्थ्य की कमज़ोरियाँ क्या हैं?",
      "क्या मुझे विदेश जाना चाहिए?",
      "मेरी सबसे बड़ी शक्तियाँ और कमियाँ क्या हैं?",
      "मेरा विवाह 2012 में हुआ — तब कुंडली में क्या था?",
    ],
    mangalTitle: "मंगल दोष", milanNeedDate: "दोनों की जन्म तिथियाँ आवश्यक हैं।",
    milanNeedPlace: "सुझावों में से दोनों के जन्म स्थान चुनें ताकि निर्देशांक सटीक हों।",
    until: "तक", tithiL: "तिथि", nakL: "नक्षत्र", yogaL: "योग", karanaL: "करण",
    timingsL: "समय", none: "आज नहीं",
  },
};

const PLANET_NAME_HI = {
  Sun: "सूर्य", Moon: "चंद्र", Mercury: "बुध", Venus: "शुक्र", Mars: "मंगल",
  Jupiter: "गुरु", Saturn: "शनि", Uranus: "यूरेनस", Neptune: "नेप्च्यून",
  Pluto: "प्लूटो", Chiron: "काइरन", "True Node": "राहु", "North Node": "राहु",
  "South Node": "केतु", Rahu: "राहु", Ketu: "केतु",
  ASC: "लग्न", MC: "दशम", DSC: "सप्तम", IC: "चतुर्थ",
  "Part of Fortune": "भाग्य बिंदु",
};
const SIGN_NAME_HI = {
  Aries: "मेष", Taurus: "वृषभ", Gemini: "मिथुन", Cancer: "कर्क", Leo: "सिंह",
  Virgo: "कन्या", Libra: "तुला", Scorpio: "वृश्चिक", Sagittarius: "धनु",
  Capricorn: "मकर", Aquarius: "कुम्भ", Pisces: "मीन",
};
const ELEMENT_HI = { Fire: "अग्नि", Earth: "पृथ्वी", Air: "वायु", Water: "जल" };

const t = (key) => (I18N[state.lang] || I18N.en)[key] ?? I18N.en[key] ?? key;
const tPlanet = (n) => (state.lang === "hi" ? PLANET_NAME_HI[n] || n : n);
const tSign = (n) => (state.lang === "hi" ? SIGN_NAME_HI[n] || n : n);
const tElement = (n) => (state.lang === "hi" ? ELEMENT_HI[n] || n : n);

const GLYPH = {
  Sun: "☉", Moon: "☽", Mercury: "☿", Venus: "♀", Mars: "♂", Jupiter: "♃",
  Saturn: "♄", Uranus: "♅", Neptune: "♆", Pluto: "♇", Chiron: "⚷",
  "True Node": "☊", "North Node": "☊", "South Node": "☋",
  ASC: "Asc", MC: "MC", DSC: "Dsc", IC: "IC",
};
const SIGN_GLYPH = {
  Aries: "♈", Taurus: "♉", Gemini: "♊", Cancer: "♋", Leo: "♌", Virgo: "♍",
  Libra: "♎", Scorpio: "♏", Sagittarius: "♐", Capricorn: "♑", Aquarius: "♒", Pisces: "♓",
};

/* ============================================================
   VEDIC CHARTS — North Indian (diamond) and South Indian (square)
   ------------------------------------------------------------
   Both are drawn here in the browser as inline SVG from state.chart, because
   the backend only returns the Western wheel. They are rashi (D-1) charts and
   therefore whole-sign: a graha's house is counted from the Lagna's sign,
   never from the Placidus cusps.
   ============================================================ */

const SIGN_ORDER = [
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
];
const signIndex = (s) => SIGN_ORDER.indexOf(s);

/* The nine grahas, in the traditional recital order, with the abbreviations
   Indian users expect in a kundali cell. */
const GRAHAS = [
  ["Sun", "Su", "सू"], ["Moon", "Mo", "चं"], ["Mars", "Ma", "मं"],
  ["Mercury", "Me", "बु"], ["Jupiter", "Ju", "गु"], ["Venus", "Ve", "शु"],
  ["Saturn", "Sa", "श"], ["True Node", "Ra", "रा"], ["South Node", "Ke", "के"],
];

const DEVANAGARI_DIGITS = ["०", "१", "२", "३", "४", "५", "६", "७", "८", "९"];
const numeral = (n) =>
  state.lang === "hi"
    ? String(n).split("").map((d) => DEVANAGARI_DIGITS[+d] ?? d).join("")
    : String(n);

/* Grahas grouped by the sign they occupy, plus the Lagna's sign index. */
function vedicPlacement(c) {
  const ascSign = c.objects.ASC
    ? signIndex(c.objects.ASC.sign)
    : signIndex(c.houses.signs[0]);
  const bySign = Array.from({ length: 12 }, () => []);
  for (const [name, en, hi] of GRAHAS) {
    const o = c.objects[name];
    if (!o) continue;
    const si = signIndex(o.sign);
    if (si < 0) continue;
    bySign[si].push({
      name,
      abbr: state.lang === "hi" ? hi : en,
      // Rahu and Ketu are retrograde by definition — flagging them adds noise.
      retro: !!o.retrograde && o.kind !== "node",
      deg: o.dms || "",
      sign: o.sign,
    });
  }
  return { ascSign: ascSign < 0 ? 0 : ascSign, bySign };
}

const svgEsc = (s) => String(s).replace(/[&<>]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch]));

/* Lay a list of grahas out as centred lines of text around a block centre.
   `box` is the usable rectangle inside the house: {per, maxW, maxH}. Rows are
   added first, then the font is shrunk until the block fits — so even a chart
   with every graha stacked in one sign stays inside its own house. */
const GRAHA_EM = 1.75;                    // approx. width of "Xx " per font unit
function grahaLines(list, cx, cy, box, baseSize) {
  if (!list.length) return "";
  let per = box.per;
  let rows = Math.ceil(list.length / per);
  const maxRows = 3;
  while (rows > maxRows && per < 5) { per += 1; rows = Math.ceil(list.length / per); }

  const fs = Math.max(2.4, Math.min(
    baseSize,
    box.maxW / (per * GRAHA_EM),
    box.maxH / (rows * 1.28),
  ));
  const lh = fs * 1.28;

  const lines = [];
  for (let i = 0; i < list.length; i += per) lines.push(list.slice(i, i + per));
  const top = cy - ((lines.length - 1) * lh) / 2;

  return lines.map((row, r) => {
    const inner = row.map((g) =>
      `<tspan>${svgEsc(g.abbr)}${g.retro ? `<tspan class="vc-rx" font-size="${(fs * 0.72).toFixed(2)}" dy="${(-fs * 0.28).toFixed(2)}">℞</tspan><tspan dy="${(fs * 0.28).toFixed(2)}"> </tspan>` : "<tspan> </tspan>"}</tspan>`
    ).join("");
    return `<text class="vc-graha" x="${cx}" y="${(top + r * lh).toFixed(2)}"
      font-size="${fs.toFixed(2)}" text-anchor="middle" dominant-baseline="middle">${inner}</text>`;
  }).join("");
}

/* ---------- North Indian ----------------------------------------------------
   Fixed square with both diagonals and the inner diamond joining the edge
   midpoints. Twelve regions in a 100x100 box; houses are fixed on screen and
   run ANTICLOCKWISE from the top-centre rhombus, while the SIGN NUMBERS rotate
   with the Lagna. numPos is the rashi number, blockPos the graha stack.        */
const NORTH_HOUSES = [
  { h: 1,  numPos: [50, 46],   blockPos: [50, 24],   per: 3, maxW: 30, maxH: 22 },
  { h: 2,  numPos: [25, 20],   blockPos: [25, 9],    per: 2, maxW: 22, maxH: 13 },
  { h: 3,  numPos: [19.5, 25], blockPos: [9, 25],    per: 2, maxW: 15, maxH: 15 },
  { h: 4,  numPos: [44, 50],   blockPos: [21, 50],   per: 3, maxW: 30, maxH: 22 },
  { h: 5,  numPos: [19.5, 75], blockPos: [9, 75],    per: 2, maxW: 15, maxH: 15 },
  { h: 6,  numPos: [25, 80.5], blockPos: [25, 91],   per: 2, maxW: 22, maxH: 13 },
  { h: 7,  numPos: [50, 56],   blockPos: [50, 76],   per: 3, maxW: 30, maxH: 22 },
  { h: 8,  numPos: [75, 80.5], blockPos: [75, 91],   per: 2, maxW: 22, maxH: 13 },
  { h: 9,  numPos: [80, 75],   blockPos: [91, 75],   per: 2, maxW: 15, maxH: 15 },
  { h: 10, numPos: [56, 50],   blockPos: [79, 50],   per: 3, maxW: 30, maxH: 22 },
  { h: 11, numPos: [80, 25],   blockPos: [91, 25],   per: 2, maxW: 15, maxH: 15 },
  { h: 12, numPos: [75, 20],   blockPos: [75, 9],    per: 2, maxW: 22, maxH: 13 },
];

function northChartSvg(c) {
  const { ascSign, bySign } = vedicPlacement(c);

  const cells = NORTH_HOUSES.map((g) => {
    const si = (ascSign + g.h - 1) % 12;          // whole-sign: house 1 = Lagna sign
    const list = bySign[si];
    return `<g>
      <text class="vc-num" x="${g.numPos[0]}" y="${g.numPos[1]}" font-size="3.4"
        text-anchor="middle" dominant-baseline="middle">${numeral(si + 1)}</text>
      ${grahaLines(list, g.blockPos[0], g.blockPos[1], g, 4.5)}
    </g>`;
  }).join("");

  return `<svg class="vchart north" viewBox="-2 -2 104 104" xmlns="http://www.w3.org/2000/svg"
      role="img" aria-label="${svgEsc(t("styleNorthFull"))}">
    <polygon class="vc-lagna" points="25,25 50,0 75,25 50,50"/>
    <g class="vc-line" fill="none">
      <rect x="0" y="0" width="100" height="100"/>
      <path d="M0 0 L100 100 M100 0 L0 100"/>
      <path d="M50 0 L100 50 L50 100 L0 50 Z"/>
    </g>
    ${cells}
  </svg>`;
}

/* ---------- South Indian ----------------------------------------------------
   Fixed 4x4 frame. The SIGNS are nailed to the screen — Pisces top-left, then
   clockwise Aries, Taurus, Gemini across the top, Cancer/Leo/Virgo down the
   right, Libra/Scorpio/Sagittarius back along the bottom, Capricorn/Aquarius up
   the left — and the Lagna is marked in whichever cell it falls in.            */
const SOUTH_CELL = [ // index = sign index (Aries=0) -> [col, row]
  [1, 0], [2, 0], [3, 0],          // Aries, Taurus, Gemini
  [3, 1], [3, 2], [3, 3],          // Cancer, Leo, Virgo
  [2, 3], [1, 3], [0, 3],          // Libra, Scorpio, Sagittarius
  [0, 2], [0, 1], [0, 0],          // Capricorn, Aquarius, Pisces
];

const SOUTH_BOX = { per: 2, maxW: 22, maxH: 15 };

function southChartSvg(c) {
  const { ascSign, bySign } = vedicPlacement(c);
  const S = 25; // cell side in the 100x100 box

  const cells = SOUTH_CELL.map(([col, row], si) => {
    const x = col * S, y = row * S;
    const isLagna = si === ascSign;
    const marker = isLagna
      ? `<rect class="vc-lagna" x="${x}" y="${y}" width="${S}" height="${S}"/>
         <path class="vc-line" d="M${x} ${y + 9} L${x + 9} ${y}"/>`
      : "";
    return `<g>
      ${marker}
      <text class="vc-num" x="${x + 2.6}" y="${y + 4.4}" font-size="3.5"
        text-anchor="start" dominant-baseline="middle">${numeral(si + 1)}</text>
      ${isLagna ? `<text class="vc-asc" x="${x + S - 2.6}" y="${y + 4.4}" font-size="3.5"
        text-anchor="end" dominant-baseline="middle">${svgEsc(t("lagnaLbl"))}</text>` : ""}
      ${grahaLines(bySign[si], x + S / 2, y + S / 2 + 1.6, SOUTH_BOX, 4.4)}
    </g>`;
  }).join("");

  const ascName = SIGN_ORDER[ascSign];
  return `<svg class="vchart south" viewBox="-2 -2 104 104" xmlns="http://www.w3.org/2000/svg"
      role="img" aria-label="${svgEsc(t("styleSouthFull"))}">
    <g class="vc-line" fill="none">
      <rect x="0" y="0" width="100" height="100"/>
      <rect x="25" y="25" width="50" height="50"/>
      <path d="M25 0 L25 25 M50 0 L50 25 M75 0 L75 25
               M25 75 L25 100 M50 75 L50 100 M75 75 L75 100
               M0 25 L25 25 M0 50 L25 50 M0 75 L25 75
               M75 25 L100 25 M75 50 L100 50 M75 75 L100 75"/>
    </g>
    ${cells}
    <text class="vc-centre" x="50" y="45" font-size="5" text-anchor="middle"
      dominant-baseline="middle">${svgEsc(t("rashiChart"))}</text>
    <text class="vc-centre dim" x="50" y="56" font-size="4.4" text-anchor="middle"
      dominant-baseline="middle">${svgEsc(t("lagnaLbl"))} · ${svgEsc(tSign(ascName))}</text>
  </svg>`;
}

/* ---------- style switcher ------------------------------------------------ */
function paintChart() {
  const host = $("#wheel");
  if (!host) return;
  const c = state.chart;
  if (!c) { host.innerHTML = ""; return; }

  if (state.chartStyle === "north")      host.innerHTML = northChartSvg(c);
  else if (state.chartStyle === "south") host.innerHTML = southChartSvg(c);
  else {
    host.innerHTML = state.wheelSvg || "";
    const svg = $("#wheel svg");
    if (svg) { svg.removeAttribute("width"); svg.removeAttribute("height"); }
  }
  host.classList.toggle("vedic", state.chartStyle !== "wheel");

  const note = $("#chart-note");
  if (note) {
    note.textContent = state.chartStyle === "wheel" ? "" : t("wholeSignNote");
    note.hidden = state.chartStyle === "wheel";
  }
}

function renderChartSwitch() {
  $$(".cstyle").forEach((b) => {
    const key = { north: "styleNorth", south: "styleSouth", wheel: "styleWheel" }[b.dataset.style];
    b.textContent = t(key);
    b.title = t({ north: "styleNorthFull", south: "styleSouthFull", wheel: "styleWheelFull" }[b.dataset.style]);
    b.classList.toggle("active", b.dataset.style === state.chartStyle);
    b.setAttribute("aria-pressed", String(b.dataset.style === state.chartStyle));
  });
}

$$(".cstyle").forEach((b) => {
  b.onclick = () => {
    state.chartStyle = b.dataset.style;
    localStorage.setItem("astro.chartStyle", state.chartStyle);
    renderChartSwitch();
    paintChart();
  };
});

/* ============================================================
   VIMSHOTTARI DASHA — full table, computed here
   ------------------------------------------------------------
   The API only reports the currently running maha/antardasha, so the whole
   120-year cycle is rebuilt in the browser from the sidereal Moon longitude
   and the birth moment, exactly as the backend does it. verifyDasha() then
   checks the reconstruction against what the API said.
   ============================================================ */
const DASHA_SEQ = [
  ["Ketu", 7], ["Venus", 20], ["Sun", 6], ["Moon", 10], ["Mars", 7],
  ["Rahu", 18], ["Jupiter", 16], ["Saturn", 19], ["Mercury", 17],
];
const DAY_MS = 86400000;
const YEAR_MS = 365.25 * DAY_MS;            // the sidereal year the backend uses
const MONTH_EN = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];
const MON_ABBR_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MON_ABBR_HI = ["जन", "फ़र", "मार्च", "अप्रै", "मई", "जून",
  "जुल", "अग", "सित", "अक्तू", "नव", "दिस"];

/* "16 August 1990, 14:30" / "16 August 2026" -> epoch ms, wall clock read as
   UTC so no browser timezone or DST shift can creep into the arithmetic. */
function parseServerMoment(s, defaultHour = 12) {
  if (!s) return null;
  const m = String(s).match(/^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})(?:,\s*(\d{1,2}):(\d{2}))?$/);
  if (!m) return null;
  const mi = MONTH_EN.indexOf(m[2]);
  if (mi < 0) return null;
  return Date.UTC(+m[3], mi, +m[1], m[4] ? +m[4] : defaultHour, m[5] ? +m[5] : 0);
}

const fmtDate = (ms) => {
  const d = new Date(ms);
  const mon = (state.lang === "hi" ? MON_ABBR_HI : MON_ABBR_EN)[d.getUTCMonth()];
  return `${numeral(d.getUTCDate())} ${mon} ${numeral(d.getUTCFullYear())}`;
};
/* The backend prints periods with strftime("%b %Y") — match that for verification. */
const fmtMonthYear = (ms) => {
  const d = new Date(ms);
  return `${MON_ABBR_EN[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
};

function antardashas(lord, majorYears, start) {
  const li = DASHA_SEQ.findIndex(([l]) => l === lord);
  const out = [];
  let cursor = start;
  for (let j = 0; j < 9; j++) {
    const [sub, subYears] = DASHA_SEQ[(li + j) % 9];
    // antardasha length = maha_years * antar_years / 120
    const end = cursor + (majorYears * subYears / 120) * YEAR_MS;
    out.push({ lord: sub, start: cursor, end });
    cursor = end;
  }
  return out;
}

function buildDasha(c, now) {
  if (!c || c.meta.zodiac !== "sidereal") return null;
  const moon = c.objects.Moon;
  const birth = parseServerMoment(c.meta.local_time);
  if (!moon || birth == null || typeof moon.longitude !== "number") return null;

  const span = 360 / 27;                      // 13°20' per nakshatra
  const lon = ((moon.longitude % 360) + 360) % 360;
  const idx = Math.floor(lon / span) % 27;
  const frac = (lon % span) / span;           // how far through the nakshatra
  const startLord = idx % 9;

  // The birth-nakshatra lord's period is already partly spent at birth.
  let cursor = birth - frac * DASHA_SEQ[startLord][1] * YEAR_MS;
  const majors = [];
  for (let i = 0; i < 9; i++) {
    const [lord, years] = DASHA_SEQ[(startLord + i) % 9];
    const end = cursor + years * YEAR_MS;
    majors.push({ lord, years, start: cursor, end, subs: antardashas(lord, years, cursor) });
    cursor = end;
  }

  const when = parseServerMoment(now && now.date) ?? Date.now();
  const current = majors.find((m) => m.start <= when && when < m.end) || null;
  const currentSub = current
    ? current.subs.find((s) => s.start <= when && when < s.end) || null
    : null;

  return {
    majors, current, currentSub, when, birth,
    balanceMs: majors[0].end - birth,
    pada: Math.floor(frac * 4) + 1,
  };
}

/* Cross-check the reconstruction against the API's own answer. */
function verifyDasha(d, v) {
  if (!d || !v || !v.mahadasha) return null;
  const checks = [
    ["mahadasha lord", d.current && d.current.lord, v.mahadasha.lord],
    ["mahadasha start", d.current && fmtMonthYear(d.current.start), v.mahadasha.start],
    ["mahadasha end", d.current && fmtMonthYear(d.current.end), v.mahadasha.end],
  ];
  if (v.antardasha) checks.push(
    ["antardasha lord", d.currentSub && d.currentSub.lord, v.antardasha.lord],
    ["antardasha start", d.currentSub && fmtMonthYear(d.currentSub.start), v.antardasha.start],
    ["antardasha end", d.currentSub && fmtMonthYear(d.currentSub.end), v.antardasha.end],
  );
  const bad = checks.filter(([, mine, theirs]) => mine !== theirs);
  const report = { ok: !bad.length, checks, mismatches: bad };
  if (!report.ok) {
    console.warn("Vimshottari reconstruction disagrees with the API:", bad);
  }
  return report;
}

function dashaTableHtml(d, v) {
  const head =
    `<div class="dasha-head"><span>${escapeHtml(t("dashaLord"))}</span>
       <span>${escapeHtml(t("dashaFrom"))}</span><span>${escapeHtml(t("dashaTo"))}</span></div>`;

  const rows = d.majors.map((m, i) => {
    const isNow = d.current === m;
    const subs = m.subs.map((s) => {
      const subNow = isNow && d.currentSub === s;
      return `<div class="antar${subNow ? " current" : ""}">
        <span class="d-lord">${escapeHtml(tPlanet(s.lord))}</span>
        <span class="d-date">${escapeHtml(fmtDate(s.start))}</span>
        <span class="d-date">${escapeHtml(fmtDate(s.end))}</span>
      </div>`;
    }).join("");

    const balance = i === 0
      ? ` <em>${escapeHtml(t("balanceAtBirth"))} ${escapeHtml(humanSpan(d.balanceMs))}</em>`
      : "";

    return `<details class="maha${isNow ? " current" : ""}"${isNow ? " open" : ""}>
      <summary>
        <span class="d-lord">${escapeHtml(tPlanet(m.lord))}
          <em>${numeral(m.years)} ${escapeHtml(t("yrs"))}</em>${balance}</span>
        <span class="d-date">${escapeHtml(fmtDate(m.start))}</span>
        <span class="d-date">${escapeHtml(fmtDate(m.end))}</span>
        ${isNow ? `<span class="d-now">${escapeHtml(t("running"))}</span>` : ""}
      </summary>
      <p class="antar-title">${escapeHtml(t("antardashaTable"))}</p>
      <div class="antars">${subs}</div>
    </details>`;
  }).join("");

  const nak = v && v.nakshatra
    ? `<p class="kv">${escapeHtml(t("nakshatra"))} <b>${escapeHtml(v.nakshatra)}</b>
        ${escapeHtml(t("pada"))} ${numeral(v.pada)}${v.moon_position ? ` · ${escapeHtml(t("moonAt"))} ${escapeHtml(v.moon_position)}` : ""}</p>`
    : "";

  return `<p class="mini-title">${escapeHtml(t("mahadashaTable"))}</p>
    ${nak}
    <div class="dasha">${head}${rows}</div>
    <p class="kv hint-line">${escapeHtml(t("expandHint"))}</p>`;
}

function humanSpan(ms) {
  const totalMonths = Math.max(0, Math.round(ms / (YEAR_MS / 12)));
  const y = Math.floor(totalMonths / 12), mo = totalMonths % 12;
  if (state.lang === "hi") {
    return `${numeral(y)} वर्ष ${numeral(mo)} माह`;
  }
  return `${y}y ${mo}m`;
}

/* ------------------------------------------------------------
   Starfield
   ------------------------------------------------------------ */
(function sky() {
  const canvas = $("#sky");
  const ctx = canvas.getContext("2d");
  let stars = [];

  function seed() {
    const { innerWidth: w, innerHeight: h } = window;
    canvas.width = w * devicePixelRatio;
    canvas.height = h * devicePixelRatio;
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    const count = Math.min(260, Math.round((w * h) / 7000));
    stars = Array.from({ length: count }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      r: Math.random() * 1.15 + 0.25,
      a: Math.random() * 0.6 + 0.15,
      speed: Math.random() * 0.0009 + 0.0003,
      phase: Math.random() * Math.PI * 2,
    }));
  }

  function draw(t) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const s of stars) {
      const twinkle = s.a + Math.sin(t * s.speed + s.phase) * 0.28;
      ctx.globalAlpha = Math.max(0.04, Math.min(1, twinkle));
      ctx.fillStyle = s.r > 1.1 ? "#ffe0a3" : "#dfe4ff";
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(draw);
  }

  seed();
  addEventListener("resize", seed);
  requestAnimationFrame(draw);
})();

/* ------------------------------------------------------------
   Minimal markdown -> HTML (headings, lists, bold, italic, quote)
   ------------------------------------------------------------ */
function escapeHtml(s) {
  return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function markdown(src) {
  // Only a blank line starts a new paragraph — a lone "\n" inside a run of
  // prose (a soft wrap, or a model that breaks mid-sentence while streaming)
  // is joined with a space instead of becoming its own <p>. Without this,
  // ordinary streamed prose fragments into a string of short, choppy blocks.
  const lines = escapeHtml(src).split("\n");
  const out = [];
  let list = null;
  let para = [];

  const inline = (s) =>
    s
      // An unclosed "**"/"*" left dangling at the end of the still-streaming
      // buffer (the closing marker just hasn't arrived yet) is held back as
      // plain text rather than shown as a literal asterisk for one frame.
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>")
      .replace(/\*\*[^*]*$/, "")
      .replace(/(^|[^*])\*[^*\n]*$/, "$1");

  const closeList = () => {
    if (list) { out.push(`</${list}>`); list = null; }
  };
  const flushPara = () => {
    if (para.length) { out.push(`<p>${inline(para.join(" "))}</p>`); para = []; }
  };

  for (const raw of lines) {
    const line = raw.replace(/\s+$/, "");
    if (!line.trim()) { flushPara(); closeList(); continue; }

    const head = line.match(/^###\s+(.*)$/);
    if (head) { flushPara(); closeList(); out.push(`<h3>${inline(head[1])}</h3>`); continue; }

    const quote = line.match(/^>\s?(.*)$/);
    if (quote) { flushPara(); closeList(); out.push(`<blockquote>${inline(quote[1])}</blockquote>`); continue; }

    const bullet = line.match(/^(\s*)[-*]\s+(.*)$/);
    if (bullet) {
      flushPara();
      if (!list) { list = "ul"; out.push("<ul>"); }
      out.push(`<li>${inline(bullet[2])}</li>`);
      continue;
    }

    closeList();
    para.push(line);
  }
  flushPara();
  closeList();
  return out.join("");
}

/* ------------------------------------------------------------
   Language + narration engine
   ------------------------------------------------------------ */
function applyLanguage() {
  document.documentElement.lang = state.lang;
  document.body.classList.toggle("lang-hi", state.lang === "hi");
  $$(".lang").forEach((b) => b.classList.toggle("active", b.dataset.lang === state.lang));

  const set = (sel, text) => { const el = $(sel); if (el) el.textContent = text; };
  const ph = (sel, text) => { const el = $(sel); if (el) el.placeholder = text; };

  // Home screen
  set("#home-tagline", t("tagline"));
  set("#home-blurb", t("homeBlurb"));
  set("#home-cta", t("homeCta"));
  const pts = $$("#home-points li");
  [t("point1"), t("point2"), t("point3")].forEach((txt, i) => {
    if (pts[i]) pts[i].textContent = txt;
  });
  // Birth screen
  set("#birth-title", t("birthTitle"));
  set("#birth-sub", t("birthSub"));
  set(".footnote", t("footnote"));
  $("#birth-form").querySelector('label[for="f-name"]').innerHTML =
    `${escapeHtml(t("name"))} <span class="opt">${escapeHtml(t("optional"))}</span>`;
  set('label[for="f-date"]', t("dob"));
  set('label[for="f-time"]', t("tob"));
  $('label[for="f-unknown"]').innerHTML =
    `${escapeHtml(t("unknownTime"))} <span class="hint">${escapeHtml(t("unknownHint"))}</span>`;
  set('label[for="f-place"]', t("pob"));
  const genderLabel = $('label[for="f-gender"]');
  if (genderLabel) {
    genderLabel.innerHTML =
      `${escapeHtml(t("gender"))} <span class="opt">${escapeHtml(t("optional"))}</span>`;
  }
  // Translate the options in place so the visitor's current choice survives a
  // language switch — rebuilding the <select> would reset it.
  const genderSel = $("#f-gender");
  if (genderSel) {
    const labels = { "": "genderNone", female: "genderFemale",
                     male: "genderMale", other: "genderOther" };
    $$("option", genderSel).forEach((o) => { o.textContent = t(labels[o.value]); });
  }
  set("#cast .label", t("cast"));
  set('[data-i18n="narration"]', t("narration"));
  ph("#f-name", t("namePh"));
  ph("#f-place", t("pobPh"));
  ph("#q", t("askPh"));

  $$(".tab").forEach((tab) => { tab.textContent = t(tab.dataset.tab); });
  $("#back").title = state.sessionId ? "Back to Dashboard" : t("newChart");

  renderChartSwitch();
  if (state.chart) {
    renderPlacements(state.chart);
    renderHouses(state.chart);
    renderAspects(state.chart);
    renderNow(state.now, state.chart);
    renderChips(state.chart);
    paintChart();          // graha abbreviations and rashi numerals are localised
  }
  renderStarters();
  renderSavedCharts();
  describeProvider();   // the Hindi caveat depends on the active language
  localStorage.setItem("astro.lang", state.lang);
}

$$(".lang").forEach((btn) => {
  btn.onclick = () => { state.lang = btn.dataset.lang; applyLanguage(); };
});

async function loadProviders() {
  const select = $("#f-provider");
  if (!select) return;                 // picker is optional — never on the landing page
  try {
    const { providers, default: fallback } = await (await fetch("/api/llm")).json();
    state.providers = providers;
    select.innerHTML = providers
      .map((p) => `<option value="${p.key}"${p.available ? "" : " disabled"}>${escapeHtml(p.label)}${p.available ? "" : " —"}</option>`)
      .join("");
    // An unchosen or no-longer-available provider falls back to whatever the
    // server recommends, not to "off" — otherwise configuring Claude would
    // leave every existing visitor on the rule-engine wording.
    if (!providers.find((p) => p.key === state.provider && p.available)) {
      state.provider = fallback || "off";
    }
    select.value = state.provider;
  } catch {
    select.innerHTML = `<option value="off">Off (deterministic)</option>`;
  }
  describeProvider();
}

function describeProvider() {
  const p = state.providers.find((x) => x.key === state.provider);
  const note = $("#engine-note");
  if (!note) return;
  if (!p) { note.textContent = ""; return; }

  const hindiRisk = state.lang === "hi" && p.key !== "off" && !p.hindi_ok;
  note.textContent = hindiRisk
    ? `${p.detail}  ⚠ This model garbles Devanagari — for Hindi, use Claude or pull a Qwen/Gemma model.`
    : p.detail;
  // Warn both when a model is bad at Hindi and when the choice leaves the machine.
  note.classList.toggle("warn", hindiRisk || (!p.local && p.key !== "off"));
  // NOT persisted here: this runs on every load, and writing on load is exactly
  // what pinned everyone to "off". Only the change handler below persists.
}

$("#f-provider")?.addEventListener("change", (e) => {
  state.provider = e.target.value;
  localStorage.setItem("astro.narration", state.provider);
  describeProvider();
});

// Retire the old key so a browser that still holds it stops being consulted.
localStorage.removeItem("astro.provider");

// Close the narration popover on an outside click, like any small settings menu.
document.addEventListener("click", (e) => {
  const box = $("#engine-settings");
  if (box && box.open && !box.contains(e.target)) box.open = false;
});

/* ------------------------------------------------------------
   Stage 1 — birth data
   ------------------------------------------------------------ */
const placeInput = $("#f-place");
const placeResults = $("#place-results");
const placeChosen = $("#place-chosen");

let placeTimer = null;
let activeIndex = -1;

placeInput.addEventListener("input", () => {
  state.place = null;
  placeChosen.hidden = true;
  clearTimeout(placeTimer);
  const q = placeInput.value.trim();
  if (q.length < 2) { hideSuggestions(); return; }
  placeTimer = setTimeout(() => lookupPlace(q), 180);
});

placeInput.addEventListener("keydown", (e) => {
  const items = $$("li", placeResults);
  if (!items.length || placeResults.hidden) return;
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    e.preventDefault();
    activeIndex = (activeIndex + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
    items.forEach((li, i) => li.classList.toggle("active", i === activeIndex));
  } else if (e.key === "Enter" && activeIndex >= 0) {
    e.preventDefault();
    items[activeIndex].click();
  } else if (e.key === "Escape") {
    hideSuggestions();
  }
});

document.addEventListener("click", (e) => {
  if (!placeResults.contains(e.target) && e.target !== placeInput) hideSuggestions();
});

function hideSuggestions() {
  placeResults.hidden = true;
  placeResults.innerHTML = "";
  activeIndex = -1;
}

async function lookupPlace(q) {
  try {
    const res = await fetch(`/api/places?q=${encodeURIComponent(q)}`);
    const { results } = await res.json();
    if (!results.length) { hideSuggestions(); return; }
    placeResults.innerHTML = "";
    results.forEach((p) => {
      const li = document.createElement("li");
      li.innerHTML = `<span>${escapeHtml(p.label)}</span><span class="meta">${p.timezone}</span>`;
      li.onclick = () => choosePlace(p);
      placeResults.append(li);
    });
    placeResults.hidden = false;
    activeIndex = -1;
  } catch { hideSuggestions(); }
}

function choosePlace(p) {
  state.place = p;
  placeInput.value = p.label;
  placeChosen.hidden = false;
  placeChosen.textContent =
    `${p.latitude.toFixed(4)}°, ${p.longitude.toFixed(4)}° · ${p.timezone}`;
  hideSuggestions();
}

$("#f-unknown").addEventListener("change", (e) => {
  const t = $("#f-time");
  t.disabled = e.target.checked;
  if (e.target.checked) t.value = "12:00";
});

$("#birth-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const err = $("#birth-error");
  err.hidden = true;

  if (!state.place) {
    err.textContent = t("pickPlace");
    err.hidden = false;
    return;
  }

  const btn = $("#cast");
  btn.disabled = true;
  btn.classList.add("busy");
  $(".label", btn).textContent = t("casting");

  const payload = {
    name: $("#f-name").value.trim(),
    date: $("#f-date").value,
    time: $("#f-time").value || "12:00",
    place: state.place.label,
    latitude: state.place.latitude,
    longitude: state.place.longitude,
    timezone: state.place.timezone,
    // One chart type, always. A tropical chart silently loses every Jyotish
    // feature that depends on the sidereal Moon — Vimshottari dasha, the
    // nakshatra, the vargas — so the reading answers "when" with nothing to
    // answer it from. Offering the choice only let people pick the broken one.
    zodiac: "sidereal",
    ayanamsa: "lahiri",
    house_system: "Whole Sign",
    time_known: !$("#f-unknown").checked,
    gender: $("#f-gender")?.value || "",
  };

  try {
    await castChart(payload);
    saveBirth(payload);
  } catch (ex) {
    err.textContent = ex.message;
    err.hidden = false;
  } finally {
    btn.disabled = false;
    btn.classList.remove("busy");
    $(".label", btn).textContent = t("cast");
  }
});

async function castChart(payload) {
  const res = await fetch("/api/chart", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Could not build the chart.");
  const data = await res.json();
  state.sessionId = data.session_id;
  state.chart = data.chart;
  state.currentBirthData = payload;
  state.currentBirthId = state.selectedBirthId;
  renderReading(data);
  loadAndShowDashboard();
}

/* ------------------------------------------------------------
   Saved charts — a signed-in visitor never types their birth
   details twice. Signed out, none of this runs at all.
   ------------------------------------------------------------ */
const savedBox = $("#saved-charts");

/* Most people cast a chart BEFORE they sign in — they only sign in when the
   paywall asks. saveBirth used to return silently in that case, and OAuth then
   reloads the page, so the chart they had just cast vanished and they landed on
   an empty home screen. Parking the payload here lets us save it the moment an
   account exists. One slot: the chart they were last looking at. */
const PENDING_BIRTH = "astro.pendingBirth";

/* The reading is already on screen by the time this runs: saving is a
   convenience for the next visit and must never hold up or break a cast. */
async function saveBirth(payload) {
  if (!acct.user) {
    try { localStorage.setItem(PENDING_BIRTH, JSON.stringify(payload)); } catch { /* private mode */ }
    return;
  }
  try {
    const res = await fetch("/api/births", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, label: payload.name || payload.place }),
    });
    if (res.status === 409) {
      toast(`${t("savedFullOne")} ${numeral(state.birthMax)} ${t("savedFullTwo")}`);
      return;
    }
    if (res.ok) loadSavedCharts();
  } catch { /* nothing worth interrupting the reading for */ }
}

/* Called once an account exists. Rescues the chart cast before signing in. */
async function claimPendingBirth() {
  if (!acct.user) return;
  let payload = null;
  try {
    const raw = localStorage.getItem(PENDING_BIRTH);
    if (raw) payload = JSON.parse(raw);
  } catch { /* unreadable — nothing to rescue */ }
  if (!payload) return;
  // Clear first: a chart that cannot be saved (at the cap, say) must not be
  // retried on every single page load forever.
  try { localStorage.removeItem(PENDING_BIRTH); } catch { /* ignore */ }
  await saveBirth(payload);
}

async function loadSavedCharts() {
  if (!savedBox) return;
  if (!acct.user) { state.births = []; renderSavedCharts(); return; }
  try {
    const data = await (await fetch("/api/births")).json();
    state.births = data.births || [];
    state.birthMax = data.max || state.birthMax;
  } catch { state.births = []; }
  renderSavedCharts();
  updateSaveButton();
}

/* Someone who already has charts saved should not be met by a blank birth form
   every single visit — that was the whole point of saving them. When there are
   saved charts the form collapses behind a "cast a new chart" button; with none
   saved (or signed out) the form is the landing page exactly as before. */
/* Screens are plain siblings; exactly one carries .active. Everything routes
   through here so there is one place that decides what is on screen. */
const STAGES = ["stage-home", "stage-birth", "stage-chat",
                "stage-milan", "stage-panchang", "stage-dashboard"];

function showStage(id) {
  STAGES.forEach((s) => {
    const el = document.getElementById(s);
    if (el) el.classList.toggle("active", s === id);
  });
  // Reset BOTH: body is the flex shell and scrolls independently of the
  // document element, so scrolling only the window leaves the header hidden.
  window.scrollTo({ top: 0 });
  document.body.scrollTop = 0;
}

// Home is reachable from the brand mark in the header, on every screen.
$("#go-home")?.addEventListener("click", () => {
  if (state.sessionId) {
    showStage("stage-dashboard");
  } else {
    showStage("stage-home");
  }
});
$("#home-cta")?.addEventListener("click", () => showStage("stage-birth"));

function renderSavedCharts() {
  if (!savedBox) return;
  const rows = state.births;

  const quickSelect = $("#f-quick-saved");
  const quickContainer = $("#quick-saved-container");
  if (quickSelect && quickContainer) {
    if (rows.length > 0) {
      quickSelect.innerHTML = `<option value="">-- Choose a saved chart --</option>` +
        rows.map(b => `<option value="${b.id}">${escapeHtml(b.label || b.name || b.place)} (${b.date})</option>`).join("");
      quickContainer.style.display = "block";
    } else {
      quickContainer.style.display = "none";
    }
  }

  if (!rows.length) { savedBox.hidden = true; savedBox.innerHTML = ""; return; }

  const full = rows.length >= state.birthMax;
  savedBox.innerHTML = `
    <div class="saved-head">
      <h2>${escapeHtml(t("savedTitle"))}</h2>
      <span class="saved-count${full ? " full" : ""}">${numeral(rows.length)}/${numeral(state.birthMax)}
        ${escapeHtml(t("savedSlots"))}</span>
    </div>
    <p class="saved-sub">${escapeHtml(full ? t("savedFullHint") : t("savedSub"))}</p>
    ${rows.map((b) => `
      <div class="saved-row" data-id="${b.id}">
        <button type="button" class="saved-open" data-act="open">
          <span class="saved-name">${escapeHtml(b.label || b.name || b.place)}</span>
          <span class="saved-meta">${escapeHtml(b.date)}${
            b.time_known ? ` · ${escapeHtml(b.time)}` : ""} · ${escapeHtml(b.place)}</span>
        </button>
        <button type="button" class="ghost-btn" data-act="rename">${escapeHtml(t("savedRename"))}</button>
        <button type="button" class="ghost-btn" data-act="delete">${escapeHtml(t("savedDelete"))}</button>
      </div>`).join("")}`;
  savedBox.hidden = false;

  $$(".saved-row", savedBox).forEach((row) => {
    const birth = rows.find((b) => b.id === Number(row.dataset.id));
    $$("button", row).forEach((btn) => {
      btn.onclick = () => {
        if (btn.dataset.act === "open") openSavedChart(birth);
        else if (btn.dataset.act === "rename") renameSavedChart(birth);
        else deleteSavedChart(birth);
      };
    });
  });

}

async function openSavedChart(b) {
  const err = $("#birth-error");
  err.hidden = true;
  try {
    await castChart({
      name: b.name, date: b.date, time: b.time, place: b.place,
      latitude: b.latitude, longitude: b.longitude, timezone: b.timezone,
      zodiac: b.zodiac, ayanamsa: b.ayanamsa, house_system: b.house_system,
      time_known: b.time_known, gender: b.gender || "",
    });
  } catch (ex) {
    err.textContent = ex.message || t("savedFailed");
    err.hidden = false;
  }
}

async function renameSavedChart(b) {
  const label = prompt(t("savedRenamePrompt"), b.label || b.name || b.place);
  if (label === null || !label.trim()) return;
  await fetch(`/api/births/${b.id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ label: label.trim() }),
  });
  loadSavedCharts();
}

async function deleteSavedChart(b) {
  if (!confirm(t("savedDeleteConfirm"))) return;
  await fetch(`/api/births/${b.id}`, { method: "DELETE" });
  loadSavedCharts();
}

function updateSaveButton() {
  const btn = $("#save-chart-btn");
  if (!btn) return;
  if (!acct.user || !state.currentBirthData) {
    btn.style.display = "none";
    return;
  }
  const isSaved = state.births.some(b =>
    b.date === state.currentBirthData.date &&
    b.time === state.currentBirthData.time &&
    Math.abs(b.latitude - state.currentBirthData.latitude) < 1e-4 &&
    Math.abs(b.longitude - state.currentBirthData.longitude) < 1e-4
  );
  btn.style.display = "inline-flex";
  if (isSaved) {
    btn.classList.add("saved");
    btn.innerHTML = "&#9733;"; // Filled star
    btn.title = t("chartSaved") || "Chart Saved";
  } else {
    btn.classList.remove("saved");
    btn.innerHTML = "&#9734;"; // Empty star
    btn.title = t("saveChart") || "Save Chart";
  }
}

$("#save-chart-btn")?.addEventListener("click", async () => {
  const btn = $("#save-chart-btn");
  if (btn.classList.contains("saved") || !state.currentBirthData) return;
  btn.disabled = true;
  await saveBirth(state.currentBirthData);
  btn.disabled = false;
  updateSaveButton();
});

// Any hand-edit after picking a saved chart means the cast payload may no
// longer match that profile, so the birth_id sent to chat must not either.
$("#birth-form")?.addEventListener("input", (e) => {
  if (e.target.id !== "f-quick-saved") state.selectedBirthId = null;
});

$("#f-quick-saved")?.addEventListener("change", (e) => {
  const val = e.target.value;
  if (!val) return;
  const b = state.births.find(x => x.id === Number(val));
  if (!b) return;
  state.selectedBirthId = b.id;

  $("#f-name").value = b.name || "";
  $("#f-date").value = b.date || "";
  if (b.time) {
    $("#f-time").value = b.time;
  }
  $("#f-gender").value = b.gender || "";
  $("#f-unknown").checked = !b.time_known;
  $("#f-time").disabled = !b.time_known;

  choosePlace({
    label: b.place,
    latitude: b.latitude,
    longitude: b.longitude,
    timezone: b.timezone
  });
});

/* ------------------------------------------------------------
   Stage 2 — reading
   ------------------------------------------------------------ */
function renderReading(data) {
  const c = data.chart;
  const meta = c.meta;

  showStage("stage-chat");

  $("#who-name").textContent = meta.name;
  $("#who-detail").textContent =
    `${meta.local_time} · ${meta.place} · ${meta.timezone} (UTC${meta.utc_offset.slice(0, 3)}:${meta.utc_offset.slice(3)})`;

  state.now = data.now;
  renderChips(c);

  state.wheelSvg = data.svg || "";
  state.dasha = buildDasha(c, data.now);
  state.dashaCheck = verifyDasha(state.dasha, data.now && data.now.vimshottari);
  renderChartSwitch();
  paintChart();

  renderPlacements(c);
  renderHouses(c);
  renderAspects(c);
  renderNow(data.now, c);
  renderStarters();

  $("#thread").innerHTML = "";
  addBot(openingRead(c), null, false);
  // preventScroll matters: the composer sits at the bottom of a full-height
  // shell, so a plain focus() scrolls the body to reveal it and drags the site
  // header up off the top of the screen.
  $("#q").focus({ preventScroll: true });
  updateSaveButton();
}

function renderChips(c) {
  const meta = c.meta;
  const asc = c.objects.ASC, sun = c.objects.Sun, moon = c.objects.Moon;
  const chips = [
    [t("asc"), `${SIGN_GLYPH[asc.sign]} ${tSign(asc.sign)} ${asc.dms}`],
    [t("sun"), `${SIGN_GLYPH[sun.sign]} ${tSign(sun.sign)} · H${sun.house}`],
    [t("moon"), `${SIGN_GLYPH[moon.sign]} ${tSign(moon.sign)} · H${moon.house}`],
    [t("sect"), meta.sect === "day" ? t("diurnal") : t("nocturnal")],
    [t("housesLbl"), meta.house_system],
    [t("zodiacLbl"), meta.zodiac === "sidereal" ? `${t("sidereal")} (${meta.ayanamsa})` : t("tropical")],
  ];
  $("#chips").innerHTML = chips
    .map(([k, v]) => `<span class="chip"><b>${escapeHtml(k)}</b> ${escapeHtml(v)}</span>`)
    .join("");
}

function openingRead(c) {
  const meta = c.meta;
  const asc = c.objects.ASC, sun = c.objects.Sun, moon = c.objects.Moon;
  const d = c.distribution;
  return (
    `**${meta.name}** — chart cast for ${meta.local_time}, ${meta.place}.\n\n` +
    `Ascendant **${asc.sign} ${asc.dms}**, Sun in **${sun.sign}** (${ordinal(sun.house)} house), ` +
    `Moon in **${moon.sign}** (${ordinal(moon.house)} house). ` +
    `This is a **${meta.sect === "day" ? "day" : "night"} chart**, dominantly **${d.dominant_element}** ` +
    `and **${d.dominant_modality}**, with ${c.aspects.length} aspects in orb.\n\n` +
    (c.house_note ? `> ${c.house_note}\n\n` : "") +
    `Ask me anything — career, money, relationships, health, study, timing. ` +
    `Every answer names the placements it is built on, and you can open *the reasoning* under each one.`
  );
}

function ordinal(n) {
  const s = ["th", "st", "nd", "rd"], v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

function renderPlacements(c) {
  const order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "Chiron", "True Node", "South Node",
    "ASC", "MC", "Part of Fortune"];
  const rows = order
    .filter((n) => c.objects[n])
    .map((n) => {
      const o = c.objects[n];
      const dign = (o.dignities || []).filter((d) => d !== "peregrine");
      const tag = dign.length ? `<em>${dign[0]}</em>` : "";
      return `<li>
        <span class="glyph">${GLYPH[n] || "•"}</span>
        <span class="name">${escapeHtml(tPlanet(n))}${tag}${o.retrograde ? ' <span class="rx">℞</span>' : ""}</span>
        <span class="pos">${SIGN_GLYPH[o.sign] || ""} ${o.dms}${o.kind !== "angle" ? " · " + o.house : ""}</span>
      </li>`;
    })
    .join("");

  const d = c.distribution;
  const total = Object.values(d.elements).reduce((a, b) => a + b, 0) || 1;
  const colours = { Fire: "#f0708c", Earth: "#6fd39a", Air: "#56d4dd", Water: "#8b7bf0" };
  const bars = Object.entries(d.elements)
    .map(([k, v]) =>
      `<p class="kv"><b>${escapeHtml(tElement(k))}</b> — ${v}</p>
       <div class="bar"><span style="width:${(v / total) * 100}%;background:${colours[k]}"></span></div>`)
    .join("");

  $("#pane-placements").innerHTML =
    `<ul class="plist">${rows}</ul>
     <p class="mini-title">${escapeHtml(t("elemental"))}</p>${bars}
     <p class="kv">${escapeHtml(t("angular"))} <b>${d.houses.angular}</b> · ${escapeHtml(t("succedent"))} <b>${d.houses.succedent}</b> · ${escapeHtml(t("cadent"))} <b>${d.houses.cadent}</b></p>`;
}

function renderHouses(c) {
  const h = c.houses;
  const rows = h.signs.map((sign, i) =>
    `<li>
       <span class="glyph">${i + 1}</span>
       <span class="name">${SIGN_GLYPH[sign]} ${escapeHtml(tSign(sign))}<em>${escapeHtml(tPlanet(h.rulers[i]))}</em></span>
       <span class="pos">${h.labels[i].replace(sign + " ", "")}</span>
     </li>`).join("");
  $("#pane-houses").innerHTML =
    `<p class="mini-title">${escapeHtml(h.system)} ${escapeHtml(t("cusps"))}</p><ul class="plist">${rows}</ul>`;
}

function renderAspects(c) {
  const rows = c.aspects.slice(0, 28).map((a) => {
    const colour = a.nature === "harmonious" ? "var(--green)"
      : a.nature === "hard" ? "var(--rose)" : "var(--gold)";
    return `<li>
      <span class="glyph" style="color:${colour}">${GLYPH[a.a] || "•"}</span>
      <span class="name">${escapeHtml(tPlanet(a.a))} ${a.type.toLowerCase()} ${escapeHtml(tPlanet(a.b))}
        <em>${a.applying ? "applying" : "separating"}</em></span>
      <span class="pos">${a.orb.toFixed(2)}°</span>
    </li>`;
  }).join("");
  const pat = (c.patterns || []).length
    ? `<p class="mini-title">${escapeHtml(t("patterns"))}</p>` +
      c.patterns.map((p) => `<p class="kv"><b>${p.name}</b> — ${p.planets.map(tPlanet).join(", ")}</p>`).join("")
    : "";
  $("#pane-aspects").innerHTML = `<ul class="plist">${rows}</ul>${pat}`;
}

function renderNow(now, c) {
  if (!now) { $("#pane-now").innerHTML = ""; return; }
  const asOf = parseServerMoment(now.date);
  const bits = [`<p class="mini-title">${escapeHtml(t("asOf"))} ${escapeHtml(asOf == null ? now.date : fmtDate(asOf))} · ${escapeHtml(t("age"))} ${numeral(Math.floor(now.age))}</p>`];

  const p = now.profection;
  if (p && !p.error) {
    bits.push(
      `<p class="kv">${escapeHtml(t("annualProfection"))} — <b>${ordinal(p.house)}</b> ${escapeHtml(t("housesLbl"))}, ${escapeHtml(tSign(p.sign))},
       ${escapeHtml(t("lordOfYear"))} <b>${escapeHtml(tPlanet(p.lord_of_year))}</b> (${ordinal(p.lord_house)}, ${p.lord_position}).</p>`,
      `<p class="kv">${escapeHtml(t("monthly"))} — ${ordinal(p.monthly_house)}, <b>${escapeHtml(tPlanet(p.monthly_lord))}</b>.</p>`);
  }

  const zr = now.zodiacal_releasing;
  if (zr && zr.l1) {
    bits.push(`<p class="mini-title">${escapeHtml(t("releasing"))} (${escapeHtml(zr.lot)})</p>`,
      `<p class="kv">L1 <b>${escapeHtml(tSign(zr.l1.sign))}</b> ${zr.l1.start}–${zr.l1.end} · ${escapeHtml(tPlanet(zr.l1.ruler))}</p>`,
      `<p class="kv">L2 <b>${escapeHtml(tSign(zr.l2.sign))}</b> ${zr.l2.start}–${zr.l2.end} · ${escapeHtml(tPlanet(zr.l2.ruler))}</p>`);
  }

  if (now.firdaria) {
    bits.push(`<p class="mini-title">${escapeHtml(t("firdaria"))}</p>`,
      `<p class="kv"><b>${escapeHtml(tPlanet(now.firdaria.major))}</b> → ${now.firdaria.major_until}` +
      (now.firdaria.sub ? ` · <b>${escapeHtml(tPlanet(now.firdaria.sub))}</b>` : "") + `</p>`);
  }

  // ---- Vimshottari: the full mahadasha table, antardashas on expand --------
  const v = now.vimshottari;
  if (c && c.meta.zodiac !== "sidereal") {
    bits.push(`<p class="mini-title">${escapeHtml(t("dasha"))}</p>`,
      `<p class="kv note-line">${escapeHtml(t("noDasha"))}</p>`);
  } else {
    if (!state.dasha) state.dasha = buildDasha(c, now);
    if (state.dasha) {
      bits.push(dashaTableHtml(state.dasha, v));
    } else if (v && v.mahadasha) {
      // Fallback: the API's one-liner, if the table could not be reconstructed.
      bits.push(`<p class="mini-title">${escapeHtml(t("dasha"))}</p>`,
        `<p class="kv"><b>${escapeHtml(tPlanet(v.mahadasha.lord))}</b> ${escapeHtml(t("mahadasha"))} ${escapeHtml(v.mahadasha.start)}–${escapeHtml(v.mahadasha.end)}</p>`,
        v.antardasha ? `<p class="kv"><b>${escapeHtml(tPlanet(v.antardasha.lord))}</b> ${escapeHtml(t("antardasha"))} ${escapeHtml(v.antardasha.start)}–${escapeHtml(v.antardasha.end)}</p>` : "");
    }
  }
  $("#pane-now").innerHTML = bits.filter(Boolean).join("");
}

$$(".tab").forEach((tab) => {
  tab.onclick = () => {
    $$(".tab").forEach((t) => t.classList.toggle("active", t === tab));
    $$(".pane").forEach((p) => p.classList.toggle("active", p.id === `pane-${tab.dataset.tab}`));
  };
});

function renderStarters() {
  // A fresh chart (or a language switch) gets the chips back — they're only
  // meant to disappear once *this* conversation has actually started.
  $("#starters").hidden = false;
  $("#starters").innerHTML = t("starters")
    .map((s) => `<button class="starter" type="button">${escapeHtml(s)}</button>`)
    .join("");
  $$(".starter").forEach((b) => {
    b.onclick = () => { $("#q").value = b.textContent; $("#ask-form").requestSubmit(); };
  });
}

/* ------------------------------------------------------------
   Chat
   ------------------------------------------------------------ */
function addUser(text) {
  const el = document.createElement("div");
  el.className = "msg user";
  el.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
  $("#thread").append(el);
  scrollThread(true);
}

function verdictClass(score) {
  if (score >= 0.15) return "v-pos";
  if (score <= -0.15) return "v-neg";
  return "v-mid";
}

function reasoningHtml(result) {
  if (!result?.evidence?.length) return "";
  const rows = result.evidence.map((e) => {
    const cls = e.score > 0.2 ? "f-plus" : e.score < -0.2 ? "f-minus" : "f-zero";
    const sign = e.score > 0 ? "+" : "";
    return `<div class="factor">
      <span class="f-name">${escapeHtml(e.factor)}</span>
      <span class="f-detail">${escapeHtml(e.detail || "")}</span>
      <span class="f-score ${cls}">${sign}${e.score.toFixed(2)}</span>
    </div>`;
  }).join("");
  return `<details class="reasoning">
    <summary>${escapeHtml(t("reasoningOne"))} ${result.evidence.length} ${escapeHtml(t("reasoningTwo"))}</summary>
    ${rows}
    <p class="kv" style="margin-top:10px">${escapeHtml(t("score"))}
      <b>${result.score >= 0 ? "+" : ""}${result.score.toFixed(2)}</b> ·
      ${escapeHtml(t("routedTo"))} <b>${escapeHtml(result.topic)}</b> ·
      ${escapeHtml(t("intent"))} <b>${escapeHtml(result.intent)}</b></p>
  </details>`;
}

function verdictHtml(result) {
  // A verdict on the natal disposition is meaningless when the question was
  // "which year was it" — the answer is a date, not a judgement.
  if (!result || ["search", "review"].includes(result.intent)) return "";
  return `<span class="verdict-tag ${verdictClass(result.score)}">${escapeHtml(result.verdict)} · ${escapeHtml(result.topic_label)}</span>`;
}

function addBot(md, result, withReasoning = true) {
  const el = document.createElement("div");
  el.className = "msg bot";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = verdictHtml(result) + markdown(md) +
    (withReasoning ? reasoningHtml(result) : "");
  el.append(bubble);
  $("#thread").append(el);
  scrollThread(true);
  return bubble;
}

function addThinking() {
  const el = document.createElement("div");
  el.className = "msg bot thinking-msg";
  el.innerHTML = `<div class="bubble"><div class="thinking">
    <i></i><i></i><i></i><span style="margin-left:6px">Reading the chart…</span></div></div>`;
  $("#thread").append(el);
  scrollThread(true);
  return el;
}

// `force` snaps to the bottom unconditionally — right for a message the
// visitor's own action just produced (their question, a fresh bot bubble).
// Without it (the default, used for in-progress streaming deltas), a token
// arriving mid-stream only pulls the view down if it was already at the
// bottom, so scrolling up to reread earlier text isn't yanked back down.
function scrollThread(force = false) {
  const t = $("#thread");
  const nearBottom = t.scrollHeight - t.scrollTop - t.clientHeight < 80;
  if (force || nearBottom) t.scrollTop = t.scrollHeight;
}

/* Streams the reading: the engine's verdict lands immediately, then the
   narration model's rewrite arrives token by token over the top of it. */
let askAbort = null;

$("#stop").addEventListener("click", () => {
  askAbort?.abort();
});

$("#ask-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = $("#q");
  const question = input.value.trim();
  if (!question || state.busy) return;

  state.busy = true;
  input.disabled = true;
  $("#send").disabled = true;
  $("#send").hidden = true;
  $("#stop").hidden = false;
  // Once a conversation is under way the starter chips are no longer the
  // point — leaving them up permanently just crowds the space between the
  // thread and the composer for the rest of the session.
  $("#starters").hidden = true;
  input.value = "";
  addUser(question);
  const pending = addThinking();

  let bubble = null;
  let result = null;
  let polished = "";
  let truncated = false;

  const paint = () => {
    if (!bubble) return;
    // No "Rewritten by …" tag and no raw-engine disclosure. Which model wrote
    // the sentences, and what the rule engine's own phrasing was, are our
    // implementation showing through — a customer reads them as the reading
    // being second-hand or unfinished. "The reasoning" stays: that one is
    // about their chart, not about our plumbing.
    bubble.innerHTML = verdictHtml(result) + markdown(polished) + reasoningHtml(result);
    scrollThread();
  };

  askAbort = new AbortController();
  try {
    const res = await fetch("/api/ask/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: askAbort.signal,
      body: JSON.stringify({
        session_id: state.sessionId, question,
        birth_id: state.currentBirthId,
        language: state.lang, provider: state.provider,
      }),
    });
    if (res.status === 401 || res.status === 402) {
      // Not signed in, or out of questions — account.js takes over from here.
      pending.remove();
      const body = await res.json().catch(() => ({}));
      handleAskRejection(res.status, body.detail, question);
      return;
    }
    if (!res.ok) throw new Error(((await res.json()).detail) || "Something went wrong.");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let split;
      while ((split = buffer.indexOf("\n\n")) !== -1) {
        const frame = buffer.slice(0, split);
        buffer = buffer.slice(split + 2);
        const type = (frame.match(/^event: (.*)$/m) || [])[1];
        const payload = (frame.match(/^data: (.*)$/m) || [])[1];
        if (!type || !payload) continue;
        const data = JSON.parse(payload);

        if (type === "analysis") {
          result = data;
          pending.remove?.();
          if (state.provider === "off") {
            addBot(result.answer_engine, result);
          } else {
            bubble = addBot("", result, false);
            bubble.innerHTML =
              `<div class="thinking"><i></i><i></i><i></i>
               <span style="margin-left:6px">${escapeHtml(t("writing"))}</span></div>`;
          }
          // `acct` is a top-level const in account.js — reachable through the
          // shared global scope, but never a property of `window`.
          if (typeof result.credits === "number" &&
              typeof acct !== "undefined" && acct.user) {
            acct.user.credits = result.credits;
            renderAccountBar();
          }
        } else if (type === "delta" && bubble) {
          polished += data.text;
          paint();
        } else if (type === "truncated" && bubble) {
          truncated = true;
        } else if (type === "error" && bubble) {
          // Narration failed; the engine's reading is still valid — show that,
          // without announcing the failure. The reading is complete and correct
          // either way, and a red "narration failed" banner only tells the
          // customer that something they cannot act on went wrong.
          polished = result.answer_engine;
          bubble.innerHTML =
            verdictHtml(result) + markdown(polished) + reasoningHtml(result);
          bubble = null;
          console.warn("narration:", data.error);
        }
      }
    }
    paint();
    if (truncated && bubble) {
      bubble.insertAdjacentHTML("beforeend",
        `<p class="incomplete-note">${escapeHtml(t("responseTruncated"))}</p>`);
    }
  } catch (ex) {
    pending.remove();
    if (ex.name === "AbortError") {
      // The visitor pressed Stop. The reading so far (verdict + whatever
      // narration streamed in) is still correct — leave it on screen marked
      // as intentionally stopped, not as a failure.
      if (bubble) {
        bubble.classList.add("bubble-incomplete");
        bubble.insertAdjacentHTML("beforeend",
          `<p class="incomplete-note">${escapeHtml(t("responseStopped"))}</p>`);
      }
    } else if (bubble) {
      // A network drop mid-stream: the partial reading is still worth
      // keeping on screen, marked as cut short, rather than buried under a
      // second, unrelated-looking error bubble.
      bubble.classList.add("bubble-incomplete");
      bubble.insertAdjacentHTML("beforeend",
        `<p class="incomplete-note">${escapeHtml(t("responseDropped"))} ${escapeHtml(ex.message)}</p>`);
    } else {
      addBot(`I could not complete that reading — ${ex.message}`, null, false);
    }
  } finally {
    askAbort = null;
    state.busy = false;
    input.disabled = false;
    $("#send").disabled = false;
    $("#send").hidden = false;
    $("#stop").hidden = true;
    input.focus({ preventScroll: true });
  }
});

function providerLabel() {
  const p = state.providers.find((x) => x.key === state.provider);
  return p ? p.label : state.provider;
}

$("#back").addEventListener("click", () => {
  if (state.sessionId) {
    showStage("stage-dashboard");
  } else {
    showStage("stage-home");
  }
});

/* ------------------------------------------------------------
   Mobile view switch — chart and reading share the screen below 980px.
   ------------------------------------------------------------ */
$$(".vview").forEach((btn) => {
  btn.onclick = () => {
    const view = btn.dataset.view;
    $(".workspace").dataset.view = view;
    $$(".vview").forEach((b) => b.classList.toggle("active", b === btn));
    // A chart drawn while its pane was hidden has no box to size against,
    // so redraw it once it is actually on screen.
    if (view === "chart" && state.chart) paintChart();
  };
});

/* sensible default date so the picker does not open in 2026 */
$("#f-date").max = new Date().toISOString().slice(0, 10);

/* Business details for the footer — statutory registrations are only shown
   once they are actually configured, never as an empty placeholder. */
(async () => {
  try {
    const site = await (await fetch("/api/site")).json();
    const entity = $("#footer-entity");
    if (entity && site.legal_name) {
      entity.innerHTML =
        `${escapeHtml(site.legal_name)} · ${escapeHtml(site.address)} · ` +
        `<a href="mailto:${escapeHtml(site.email)}">${escapeHtml(site.email)}</a>` +
        (site.phone ? ` · ${escapeHtml(site.phone)}` : "");
    }
    // Both footers — the home screen carries its own copy, and the two must
    // never drift apart or the legal pages contradict each other.
    $$("#footer-registration, #footer-registration-home").forEach((reg) => {
      if (site.registration_line) {
        reg.textContent = site.registration_line;
        reg.hidden = false;
      }
    });
  } catch { /* the footer's static fallback text stands */ }
})();

applyLanguage();
loadProviders();

/* ============================================================
   Cosmic Dashboard & Details Modals Logic
   ============================================================ */
async function loadAndShowDashboard() {
  if (!state.sessionId) return;
  
  // Update name and details in header
  const meta = state.chart.meta;
  $("#dash-name").textContent = meta.name || "Native";
  $("#dash-birth-details").textContent = 
    `${meta.local_time} · ${meta.place} · ${meta.timezone}`;
    
  showStage("stage-dashboard");
  
  try {
    const dash = await (await fetch(`/api/dashboard/${state.sessionId}`)).json();
    
    // Populate Panchang
    $("#dash-tithi").textContent = dash.panchang.tithi || "—";
    $("#dash-nakshatra").textContent = dash.panchang.nakshatra || "—";
    $("#dash-yoga").textContent = dash.panchang.yoga || "—";
    $("#dash-karana").textContent = dash.panchang.karana || "—";
    
    // Populate Muhurtha
    $("#dash-abhijit").textContent = dash.panchang.muhurtha.abhijit.start ? 
      `${dash.panchang.muhurtha.abhijit.start.slice(11, 16)} - ${dash.panchang.muhurtha.abhijit.end.slice(11, 16)}` : "None today";
    $("#dash-rahu-kalam").textContent = dash.panchang.muhurtha.rahu_kaal.start ? 
      `${dash.panchang.muhurtha.rahu_kaal.start.slice(11, 16)} - ${dash.panchang.muhurtha.rahu_kaal.end.slice(11, 16)}` : "—";
    $("#dash-sunrise").textContent = dash.panchang.sunrise ? dash.panchang.sunrise.slice(11, 16) : "—";
    $("#dash-sunset").textContent = dash.panchang.sunset ? dash.panchang.sunset.slice(11, 16) : "—";
    
    // Populate Dasha
    $("#dash-mahadasha-lord").textContent = dash.dasha.mahadasha.lord;
    $("#dash-mahadasha-dates").textContent = `${dash.dasha.mahadasha.start} - ${dash.dasha.mahadasha.end}`;
    $("#dash-antardasha-lord").textContent = dash.dasha.antardasha.lord;
    $("#dash-antardasha-dates").textContent = `${dash.dasha.antardasha.start} - ${dash.dasha.antardasha.end}`;
    
    // Populate Daily Forecast
    const badge = $("#transit-badge");
    badge.className = `badge ${dash.daily_transit.score.toLowerCase()}`;
    badge.textContent = dash.daily_transit.score;
    $("#transit-advice").textContent = dash.daily_transit.advice;
    
    // Render visual timeline
    const timelineContainer = $("#timeline-visual");
    if (timelineContainer && dash.dasha.ladder && dash.dasha.ladder.length > 0) {
      const totalYears = dash.dasha.ladder.reduce((sum, item) => sum + parseFloat(item[1]), 0);
      
      let blocksHtml = '<div class="timeline-row">';
      dash.dasha.ladder.forEach((item) => {
        const lord = item[0];
        const years = parseFloat(item[1]);
        const start = item[2];
        const end = item[3];
        const status = item[4]; // 'past', 'current', or 'ahead'
        const pct = (years / totalYears) * 100;
        
        blocksHtml += `
          <div class="timeline-block ${status}" style="width: ${pct}%;" 
               data-lord="${escapeHtml(lord)}" data-years="${years}" 
               data-start="${escapeHtml(start)}" data-end="${escapeHtml(end)}" data-status="${status}">
            <span class="block-lord">${escapeHtml(lord.slice(0, 3))}</span>
            <span class="block-years">${years}y</span>
          </div>
        `;
      });
      blocksHtml += '</div>';
      
      const currentDasha = dash.dasha.ladder.find(item => item[4] === "current") || dash.dasha.ladder[0];
      blocksHtml += `
        <div class="timeline-detail-box" id="timeline-detail-box" style="margin-top: 10px;">
          Selected period: <b>${escapeHtml(currentDasha[0])} Mahadasha</b> (${currentDasha[1]} years)<br/>
          Duration: <b>${escapeHtml(currentDasha[2])}</b> to <b>${escapeHtml(currentDasha[3])}</b> (${currentDasha[4].toUpperCase()})
        </div>
      `;
      timelineContainer.innerHTML = blocksHtml;
      
      $$(".timeline-block", timelineContainer).forEach(block => {
        const updateBox = () => {
          const dBox = $("#timeline-detail-box");
          if (!dBox) return;
          const lord = block.dataset.lord;
          const years = block.dataset.years;
          const start = block.dataset.start;
          const end = block.dataset.end;
          const status = block.dataset.status;
          dBox.innerHTML = `
            Selected period: <b>${escapeHtml(lord)} Mahadasha</b> (${years} years)<br/>
            Duration: <b>${escapeHtml(start)}</b> to <b>${escapeHtml(end)}</b> (${status.toUpperCase()})
          `;
        };
        block.addEventListener("mouseenter", updateBox);
        block.addEventListener("click", updateBox);
      });
    }
  } catch (ex) {
    console.error("Failed to load dashboard:", ex);
  }
}

// Remedies Modal
$("#dash-nav-remedies")?.addEventListener("click", async () => {
  const modal = $("#remedies-modal");
  if (!modal) return;
  modal.style.display = "flex";
  
  try {
    const data = await (await fetch(`/api/remedies/${state.sessionId}`)).json();
    
    // Gemstones
    const gemsList = $("#gems-list");
    gemsList.innerHTML = Object.values(data.gemstones).map(g => `
      <div class="gem-card">
        <div class="gem-left">
          <h4>${escapeHtml(g.role)}</h4>
          <p>${escapeHtml(g.name)}</p>
        </div>
        <div class="gem-right">
          Metal: <b>${escapeHtml(g.metal)}</b><br/>
          Wear on: <b>${escapeHtml(g.finger)}</b>
        </div>
      </div>
    `).join("");
    
    // Remedies
    $("#dasha-remedies-content").innerHTML = `
      <p>Your current Mahadasha is ruled by <b>${escapeHtml(data.dasha_remedies.mahadasha_lord)}</b>.</p>
      <p><b>Recommended Mantra:</b><br/>
         <span style="font-size: 14px; color: var(--gold); display: block; margin-top: 6px; font-family: monospace;">${escapeHtml(data.dasha_remedies.mantra)}</span>
      </p>
      <p><b>Charity &amp; Fasting:</b><br/>
         ${escapeHtml(data.dasha_remedies.charity)}
      </p>
    `;
  } catch (ex) {
    console.error(ex);
  }
});

$("#close-remedies-modal")?.addEventListener("click", () => {
  $("#remedies-modal").style.display = "none";
});

// Doshas Modal
$("#dash-nav-doshas")?.addEventListener("click", async () => {
  const modal = $("#doshas-modal");
  if (!modal) return;
  modal.style.display = "flex";
  
  try {
    const data = await (await fetch(`/api/doshas/${state.sessionId}`)).json();
    
    const content = $("#doshas-content");
    
    // Manglik
    const m = data.manglik;
    const manglikBadge = m.is_manglik ? '<span class="badge caution">Manglik</span>' : 
      (m.is_cancelled ? '<span class="badge neutral">Manglik (Cancelled)</span>' : '<span class="badge excellent">Non-Manglik</span>');
      
    let cancellationsHtml = "";
    if (m.cancellations && m.cancellations.length > 0) {
      cancellationsHtml = `
        <ul class="dosha-list-items">
          ${m.cancellations.map(c => `<li>✓ ${escapeHtml(c)}</li>`).join("")}
        </ul>
      `;
    }
    
    // Sade Sati
    const ss = data.sade_sati;
    const ssBadge = ss.running ? '<span class="badge caution">Sade Sati Active</span>' : '<span class="badge excellent">Sade Sati Inactive</span>';
    
    let ssPhasesHtml = "";
    if (ss.periods && ss.periods.length > 0) {
      ssPhasesHtml = `
        <h4 style="margin-top: 16px; color: var(--gold); font-size: 13.5px; margin-bottom: 8px;">Sade Sati Phase Breakdown</h4>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
            <thead>
              <tr style="border-bottom: 1px solid var(--line); color: var(--ink-dim);">
                <th style="padding: 6px 4px;">Phase</th>
                <th style="padding: 6px 4px;">Sign</th>
                <th style="padding: 6px 4px;">Start Date</th>
                <th style="padding: 6px 4px;">End Date</th>
                <th style="padding: 6px 4px;">Status</th>
              </tr>
            </thead>
            <tbody>
              ${ss.periods.flatMap(p => p.phases || []).map(ph => `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); color: ${ph.status === 'current' ? 'var(--gold)' : 'var(--ink)'}">
                  <td style="padding: 8px 4px;"><b>${escapeHtml(ph.name)}</b></td>
                  <td style="padding: 8px 4px;">${escapeHtml(ph.sign)}</td>
                  <td style="padding: 8px 4px;">${ph.start ? ph.start.slice(0, 10) : '—'}</td>
                  <td style="padding: 8px 4px;">${ph.end ? ph.end.slice(0, 10) : '—'}</td>
                  <td style="padding: 8px 4px;">
                    <span class="badge ${ph.status === 'current' ? 'caution' : (ph.status === 'past' ? 'excellent' : 'neutral')}" style="padding: 2px 6px; font-size: 9px;">
                      ${ph.status}
                    </span>
                  </td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      `;
    }

    // Kaal Sarp
    const ks = data.kaal_sarp;
    const ksBadge = ks.forms ? `<span class="badge caution">Kaal Sarp formed (${escapeHtml(ks.type?.name ?? "")})</span>` : '<span class="badge excellent">No Kaal Sarp</span>';

    content.innerHTML = `
      <div class="dosha-group">
        <h3>Manglik Dosha Report</h3>
        <div class="dosha-badge-row">
          ${manglikBadge}
          <span style="font-size:12px; color:var(--ink-dim);">Score: <b>${m.score}</b></span>
        </div>
        <p>${escapeHtml(m.description)}</p>
        <p style="margin-top: 6px;">Mars is placed in House <b>${m.houses.from_lagna}</b> from Lagna, House <b>${m.houses.from_moon}</b> from Moon, and House <b>${m.houses.from_venus}</b> from Venus.</p>
        ${cancellationsHtml}
      </div>
      
      <hr style="border: none; border-top: 1px solid var(--line); margin: 20px 0;"/>
      
      <div class="dosha-group">
        <h3>Sade Sati Report</h3>
        <div class="dosha-badge-row">
          ${ssBadge}
        </div>
        <p>Saturn transiting the 12th, 1st, or 2nd houses from your natal Moon creates Sade Sati. Currently, Saturn is ${ss.running ? "transiting your Moon's transit zone." : "outside the Sade Sati zone."}</p>
        ${ss.current_period ? `<p style="margin-top:6px; color:var(--gold);">Active phase: <b>${escapeHtml(ss.phase ? ss.phase.name : "Active")}</b> (${ss.current_period.start.slice(0, 10)} to ${ss.current_period.end.slice(0, 10)})</p>` : ""}
        ${ssPhasesHtml}
      </div>

      <hr style="border: none; border-top: 1px solid var(--line); margin: 20px 0;"/>

      <div class="dosha-group">
        <h3>Kaal Sarp Dosha Report</h3>
        <div class="dosha-badge-row">
          ${ksBadge}
        </div>
        <p>Forms when all seven classical planets are hemmed between Rahu and Ketu. ${ks.forms ? `Your chart forms the <b>${escapeHtml(ks.type?.name ?? "")}</b> type of Kaal Sarp (Rahu in house ${ks.type?.rahu_house ?? "?"}).` : "Your planets are distributed freely, forming no Kaal Sarp alignment."}</p>
      </div>
    `;
  } catch (ex) {
    console.error(ex);
  }
});

$("#close-doshas-modal")?.addEventListener("click", () => {
  $("#doshas-modal").style.display = "none";
});

// Switch profile CTA
$("#dash-change-profile")?.addEventListener("click", () => {
  showStage("stage-birth");
});

// Navigate to Chat
$("#dash-nav-chat")?.addEventListener("click", () => {
  showStage("stage-chat");
});

// Navigate to Milan
$("#dash-nav-milan")?.addEventListener("click", () => {
  showStage("stage-milan");
});

// PDF Downloads and Modals
$("#download-remedies-pdf")?.addEventListener("click", () => {
  if (state.sessionId) {
    window.location.href = `/api/pdf/remedies/${state.sessionId}`;
  }
});

$("#dash-download-pdf")?.addEventListener("click", () => {
  const modal = $("#kundali-pdf-modal");
  if (modal) modal.style.display = "flex";
});

$("#close-kundali-pdf-modal")?.addEventListener("click", () => {
  $("#kundali-pdf-modal").style.display = "none";
});

$("#generate-pdf-en")?.addEventListener("click", () => {
  if (state.sessionId) {
    window.location.href = `/api/pdf/chart/${state.sessionId}?lang=en`;
    $("#kundali-pdf-modal").style.display = "none";
  }
});

$("#generate-pdf-hi")?.addEventListener("click", () => {
  if (state.sessionId) {
    window.location.href = `/api/pdf/chart/${state.sessionId}?lang=hi`;
    $("#kundali-pdf-modal").style.display = "none";
  }
});
