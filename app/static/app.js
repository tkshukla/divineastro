/* ============================================================
   Astro — front end
   No frameworks, no CDN. Everything below runs offline.
   ============================================================ */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

/* DIVASTRO-121: the languages, from the registry main.py inlines (app/i18n.py).
   The fallback list only matters if the page was served without it. */
const LANGS = (window.DA_LANGS && window.DA_LANGS.length) ? window.DA_LANGS
  : ["en", "hi", "kn", "te", "ta", "ml", "bn", "or", "pa", "ne", "as", "mr", "gu"].map((code) => ({ code, native: code, htmlLang: code }));
const LANG_CODES = LANGS.map((l) => l.code);
const langInfo = (code) => LANGS.find((l) => l.code === code) || LANGS[0];
function storedLang() { try { return localStorage.getItem("astro.lang"); } catch { return null; } }
// The first known code among the candidates, else English.
function pickLang(...candidates) {
  for (const c of candidates) {
    const code = String(c || "").trim().toLowerCase();
    if (LANG_CODES.includes(code)) return code;
  }
  return "en";
}

const state = {
  place: null,
  sessionId: null,
  chart: null,
  busy: false,
  // ?lang=<code> comes from the server pages' links (seo_pages.py and the language
  // picker) and wins over the stored choice; applyLanguage() then stores it.
  lang: pickLang(new URLSearchParams(location.search).get("lang"), storedLang()),
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
/* DIVASTRO-121: the strings live in app/static/i18n/<code>.json, one file per
   language. English and Hindi arrive inline with the page (main.py _page puts
   them in window.DA_I18N), so the first paint never waits on a fetch; the other
   languages are fetched the first time they are chosen (loadLang) and cached.
   Any key a language lacks falls back to English, per key — a half-translated
   language shows English for the rest, never a blank or a raw key. */
const I18N = Object.assign({ en: {}, hi: {} }, window.DA_I18N || {});
const I18N_LOADING = {};
function loadLang(code) {
  if (I18N[code] || !LANG_CODES.includes(code)) return Promise.resolve();
  if (!I18N_LOADING[code]) {
    I18N_LOADING[code] = fetch(`/static/i18n/${code}.json?v=${encodeURIComponent(window.DA_I18N_V || "")}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((table) => { I18N[code] = table && typeof table === "object" ? table : {}; })
      .catch(() => { delete I18N_LOADING[code]; });   // English meanwhile; retried on the next switch
  }
  return I18N_LOADING[code];
}

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

const t = (key) => {
  const own = (I18N[state.lang] || {})[key];
  if (own) return own;
  const en = I18N.en[key];
  return en == null ? key : en;
};
/* A field of an API object in the reader's language: obj.name_kn, else (Hindi) the
   existing name_hi, else the English obj.name. The server adds name_<code> as each
   language's tables land (app/astro/names_<code>.py), and this picks them up as-is. */
const loc = (obj, field, lang = state.lang) => {
  if (!obj) return "";
  if (lang && lang !== "en") {
    const v = obj[`${field}_${lang}`];
    if (v) return v;
  }
  return obj[field] ?? obj[`${field}_en`] ?? "";
};
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
/* DIVASTRO-121: the script's web font, for the active language only — never all
   eight. Google's CSS splits each family by unicode-range and uses
   font-display: swap, so text shows at once in a system font. The family is
   named in styles.css (html[lang=xx] --sans/--serif). */
const FONTS_LOADED = new Set();
function loadFont(code) {
  const url = langInfo(code).font;
  if (!url || FONTS_LOADED.has(code)) return;
  FONTS_LOADED.add(code);
  if (!document.querySelector('link[rel="preconnect"][href="https://fonts.gstatic.com"]')) {
    const pc = document.createElement("link");
    pc.rel = "preconnect"; pc.href = "https://fonts.gstatic.com"; pc.crossOrigin = "";
    document.head.appendChild(pc);
  }
  const link = document.createElement("link");
  link.rel = "stylesheet"; link.href = url; link.dataset.langFont = code;
  document.head.appendChild(link);
}

/* The header picker (written by main.py from app/i18n.py picker()): its button
   shows the current language's native name, its menu marks the current one. */
function renderLangPicker() {
  const info = langInfo(state.lang);
  $$(".lang-picker").forEach((det) => {
    det.dataset.current = state.lang;
    const cur = $(".lp-cur", det);
    if (cur) { cur.textContent = info.native; cur.setAttribute("lang", state.lang); }
    $("summary", det)?.setAttribute("aria-label", `${t("hdrLang")}: ${info.native}`);
    $$(".lp-menu a[data-lang]", det).forEach((a) => {
      if (a.dataset.lang === state.lang) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  });
}

/* Switch language in place (langpick.js calls this instead of following the link). */
window.daSetLang = (code) => {
  const next = pickLang(code);
  if (next === state.lang && I18N[next]) { renderLangPicker(); return; }
  state.lang = next;
  applyLanguage();
};
window.daGetLang = () => state.lang;

function applyLanguage() {
  // A language whose strings have not arrived yet renders in English now and
  // again, translated, the moment its JSON lands (only if still selected).
  if (!I18N[state.lang]) {
    const wanted = state.lang;
    loadLang(wanted).then(() => { if (state.lang === wanted && I18N[wanted]) applyLanguage(); });
  }
  document.documentElement.lang = state.lang;
  LANG_CODES.forEach((c) => document.body.classList.toggle(`lang-${c}`, c === state.lang));
  loadFont(state.lang);
  renderLangPicker();

  const set = (sel, text) => { const el = $(sel); if (el) el.textContent = text; };
  const ph = (sel, text) => { const el = $(sel); if (el) el.placeholder = text; };

  // Home screen
  set("#home-tagline", t("homeHeadline"));
  set("#home-blurb", t("homeBlurb"));
  set("#home-cta", t("homeCta"));
  set("#home-promise", t("homePromise"));
  set("#tools-head", t("homeToolsHead"));
  for (let i = 1; i <= 6; i++) set(`#feat-${i}`, t(`feat${i}`));
  renderFreeBadge();
  renderHomeValue();      // DIVASTRO-101 block at the end of this file

  // Tools buttons
  set("#tool-milan-name", t("toolMilanName"));
  set("#tool-milan-sub", t("toolMilanSub"));
  set("#tool-panchang-name", t("toolPanchangName"));
  set("#tool-panchang-sub", t("toolPanchangSub"));
  set("#tool-muhurat-name", t("toolMuhuratName"));
  set("#tool-muhurat-sub", t("toolMuhuratSub"));
  set("#tool-choghadiya-name", t("toolChoghadiyaName"));
  set("#tool-choghadiya-sub", t("toolChoghadiyaSub"));
  set("#tool-vrat-name", t("toolVratName"));
  set("#tool-vrat-sub", t("toolVratSub"));
  const vratCard = document.querySelector("#open-vrat");
  // The server pages live under /<code>/ (an untranslated one shows English with a notice).
  if (vratCard) vratCard.setAttribute("href", state.lang === "en" ? "/vrat-tyohar" : `/${state.lang}/vrat-tyohar`);
  set("#tool-katha-name", t("toolKathaName"));
  set("#tool-katha-sub", t("toolKathaSub"));
  const kathaCard = document.querySelector("#open-katha");
  // Katha is Hindi-canonical (/katha) with an English twin; no other language yet.
  if (kathaCard) kathaCard.setAttribute("href", state.lang === "hi" ? "/katha" : "/en/katha");

  // Muhurat stage
  set("#muhurat-title", t("muhuratTitle"));
  set("#muhurat-sub", t("muhuratSub"));
  set("#lbl-muhurat-event", t("lblMuhuratEvent"));
  set("#lbl-muhurat-place", t("lblMuhuratPlace"));
  set("#lbl-muhurat-from", t("lblMuhuratFrom"));
  set("#lbl-muhurat-to", t("lblMuhuratTo"));
  set("#btn-muhurat-search", t("btnMuhuratSearch"));

  // Choghadiya stage
  set("#choghadiya-title", t("choghadiyaTitle"));
  set("#choghadiya-sub", t("choghadiyaSub"));
  set("#lbl-choghadiya-date", t("lblChoghadiyaDate"));
  set("#lbl-choghadiya-place", t("lblChoghadiyaPlace"));
  set("#btn-choghadiya-check", t("btnChoghadiyaCheck"));

  // Panel Tabs
  const vargasTab = $('button.tab[data-tab="vargas"]');
  if (vargasTab) vargasTab.textContent = t("tabVargas");
  const ashtakaTab = $('button.tab[data-tab="ashtakavarga"]');
  if (ashtakaTab) ashtakaTab.textContent = t("tabAshtakavarga");
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
  set("#fs-label", t("textSize"));
  set("#time-hint", t("midnightHint"));
  set("#jump-latest-label", t("jumpLatest"));
  $("#chips-toggle")?.setAttribute("title", t("chartDetails"));
  $("#chips-toggle")?.setAttribute("aria-label", t("chartDetails"));
  $("#panel-toggle")?.setAttribute("title", t("hidePanel"));
  $("#panel-toggle")?.setAttribute("aria-label", t("hidePanel"));
  $$(".msg-actions [data-act='copy']").forEach((b) => { b.textContent = t("copyAns"); });
  $$(".msg-actions [data-act='share']").forEach((b) => { b.textContent = t("shareAns"); });

  // Dashboard screen elements
  set("#dash-download-pdf-label", t("dashDownloadPdf"));
  set("#dash-change-profile", t("dashChangeProfile"));
  set("#dash-forecast-title", t("dashForecastTitle"));
  set("#dash-panchang-title", t("dashPanchangTitle"));
  set("#lbl-tithi", t("dashTithi"));
  set("#lbl-nakshatra", t("dashNakshatra"));
  set("#lbl-yoga", t("dashYoga"));
  set("#lbl-karana", t("dashKarana"));
  set("#dash-muhurtha-title", t("dashMuhurthaTitle"));
  set("#lbl-abhijit", t("dashAbhijit"));
  set("#lbl-rahu-kalam", t("dashRahuKalam"));
  set("#lbl-sunrise", t("dashSunrise"));
  set("#lbl-sunset", t("dashSunset"));
  set("#dash-dasha-title", t("dashDashaTitle"));
  set("#lbl-md-lord", t("dashMdLord"));
  set("#lbl-md-dur", t("dashDuration"));
  set("#lbl-ad-lord", t("dashAdLord"));
  set("#lbl-ad-dur", t("dashDuration"));
  set("#dash-timeline-title", t("dashTimelineTitle"));
  set("#dash-timeline-desc", t("dashTimelineDesc"));
  set("#dash-explore-title", t("dashExploreTitle"));
  set("#nav-chat-title", t("dashNavChatTitle"));
  set("#nav-chat-desc", t("dashNavChatDesc"));
  set("#nav-remedies-title", t("dashNavRemediesTitle"));
  set("#nav-remedies-desc", t("dashNavRemediesDesc"));
  set("#nav-doshas-title", t("dashNavDoshasTitle"));
  set("#nav-doshas-desc", t("dashNavDoshasDesc"));
  set("#nav-milan-title", t("dashNavMilanTitle"));
  set("#nav-milan-desc", t("dashNavMilanDesc"));

  // Modals
  set("#modal-remedies-title", t("modalRemediesTitle"));
  set("#modal-remedies-gems-title", t("modalRemediesGemsTitle"));
  set("#modal-remedies-dasha-title", t("modalRemediesDashaTitle"));
  set("#modal-remedies-pdf-btn", t("modalRemediesPdfBtn"));

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
  try { localStorage.setItem("astro.lang", state.lang); } catch { /* private mode */ }
  // tools.js: Panchang / Muhurat / Choghadiya labels, and any result already on
  // screen, follow the switch (tools.js loads after this file, hence the check).
  if (typeof window.applyToolsLanguage === "function") window.applyToolsLanguage();
  // DIVASTRO-111: the header's Sign in / account menu (account.js, which loads after
  // this file) and its own labels follow the switch too — they used to stay in the
  // language the page was loaded in.
  $("#go-home")?.setAttribute("aria-label", t("hdrHome"));
  $("#theme-toggle")?.setAttribute("aria-label", t("hdrTheme"));
  $("#theme-toggle")?.setAttribute("title", t("hdrThemeTitle"));
  renderLangPicker();                    // its aria-label is t("hdrLang") + the native name
  if (typeof renderAccountBar === "function") renderAccountBar();
  if (typeof renderPlans === "function") renderPlans();      // DIVASTRO-149: the home Plans section
  if (typeof renderDashReports === "function") renderDashReports();   // DIVASTRO-150

  if (state.sessionId) {
    loadAndShowDashboard();
  }
}

/* The "first N questions FREE" badge. N is what the server says (ASTRO_FREE_QUESTIONS,
   via /api/me) — never a number typed into the page. Until /api/me has answered, the
   badge stays hidden, so it can never claim something the server has not confirmed.
   Signed in, it shows what the person actually has left instead. */
function renderFreeBadge() {
  const box = $("#free-badge");
  if (!box) return;
  // Known = the server has told us: either the free allowance (signed out) or this
  // person's own balance (signed in). Anything else stays hidden.
  if (typeof acct === "undefined" || !(acct.user || acct.freeKnown)) { box.hidden = true; return; }
  const signedIn = !!acct.user;
  if (signedIn && !(acct.user.credits > 0)) { box.hidden = true; return; }
  const n = signedIn ? acct.user.credits : acct.freeQuestions;
  $("#free-badge-main").textContent = t(signedIn ? "freeBadgeIn" : "freeBadge").replace("{n}", n);
  $("#free-badge-sub").textContent = t(signedIn ? "freeBadgeInSub" : "freeBadgeSub");
  // A button needs a name a screen reader can say: the whole message, not just the number.
  box.setAttribute("aria-label", `${$("#free-badge-main").textContent}. ${$("#free-badge-sub").textContent}`);
  box.classList.toggle("promo", !signedIn);     // festival lights are for the sign-up promise only
  box.hidden = false;
}

/* Tapping the box. Signed out, it is the sign-up button. Signed in, it takes the person
   straight to the AI chat: the chart they already have open, else their first saved
   chart, else the birth form (a reading needs a chart before anything can be asked). */
async function goToChat() {
  if (state.sessionId && state.chart) { showStage("stage-chat"); return; }
  const first = (state.births || [])[0];
  if (first) {
    await openSavedChart(first);          // casts the chart; that ends on the dashboard...
    if (state.sessionId) { showStage("stage-chat"); return; }   // ...so put the chat back in front
  }
  showStage("stage-birth");
}
$("#free-badge")?.addEventListener("click", () => {
  if (typeof acct !== "undefined" && acct.user) goToChat();
  else if (typeof openSignIn === "function") openSignIn();
});

function initTheme() {
  const saved = localStorage.getItem("astro.theme");
  const prefersLight = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches;
  const theme = saved || (prefersLight ? "light" : "dark");
  applyTheme(theme);

  $$(".theme-toggle, #theme-toggle").forEach((btn) => {
    btn.onclick = () => {
      const current = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
      const next = current === "light" ? "dark" : "light";
      applyTheme(next);
      localStorage.setItem("astro.theme", next);
    };
  });
}

function applyTheme(theme) {
  if (theme === "light") {
    document.documentElement.setAttribute("data-theme", "light");
    document.body.classList.add("theme-light");
    $$(".theme-icon").forEach((el) => { el.textContent = "🌙"; });
  } else {
    document.documentElement.removeAttribute("data-theme");
    document.body.classList.remove("theme-light");
    $$(".theme-icon").forEach((el) => { el.textContent = "☀️"; });
  }
}
initTheme();

// The language picker's clicks are wired by langpick.js, which calls window.daSetLang.

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

  // DIVASTRO-124: every non-English language is written by the model now, so a
  // model that garbles Indian scripts is a risk for all of them, not just Hindi.
  const scriptRisk = state.lang !== "en" && p.key !== "off" && !p.hindi_ok;
  note.textContent = scriptRisk
    ? `${p.detail}  ${t("engineScriptRisk").replace("{lang}", langInfo(state.lang).native)}`
    : p.detail;
  // Warn both when a model is bad at Indian scripts and when the choice leaves the machine.
  note.classList.toggle("warn", scriptRisk || (!p.local && p.key !== "off"));
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

/* The "born after midnight" note only matters for a night or early-morning birth,
   so it appears only then (it used to sit between the fields for everyone). */
function updateTimeHint() {
  const v = $("#f-time").value;                 // "HH:MM", empty while being edited
  const early = /^\d{2}:\d{2}$/.test(v) && v < "06:00" && !$("#f-unknown").checked;
  $("#time-hint").hidden = !early;
}
$("#f-time").addEventListener("input", updateTimeHint);
$("#f-time").addEventListener("change", updateTimeHint);
$("#f-unknown").addEventListener("change", updateTimeHint);

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
  window.daTrack?.("chart_cast");
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

/* The same problem for the QUESTION. Signing in is a full-page redirect to the
   provider and back, so a question typed before the sign-in wall used to vanish
   with the page: the newcomer came back to a blank home screen at the exact moment
   they had decided to ask. Park it (with a time limit, so an old one is never asked
   out of the blue) and ask it for them when they return. */
const PENDING_QUESTION = "astro.pendingQuestion";
const PENDING_QUESTION_TTL_MS = 2 * 60 * 60 * 1000;

function parkQuestion(question) {
  try {
    localStorage.setItem(PENDING_QUESTION, JSON.stringify({ q: String(question || "").slice(0, 600), at: Date.now() }));
  } catch { /* private mode: the question is simply not remembered */ }
}

function takeParkedQuestion() {
  let out = "";
  try {
    const raw = localStorage.getItem(PENDING_QUESTION);
    localStorage.removeItem(PENDING_QUESTION);          // one shot, whatever happens next
    const v = raw ? JSON.parse(raw) : null;
    if (v && typeof v.q === "string" && Date.now() - Number(v.at) < PENDING_QUESTION_TTL_MS) out = v.q.trim();
  } catch { /* unreadable: nothing to ask */ }
  return out;
}

/* Where a person lands right after signing in (the OAuth redirect reloads the
   page, so nothing is on screen). A returning or just-claimed chart goes straight
   into the reading, with the question they were about to ask; someone with no chart
   yet goes to the birth form, not the plain home page. Called from account.js once
   the account and saved charts are loaded. */
async function resumeAfterSignIn() {
  if (typeof acct === "undefined" || !acct.user) return;
  const question = takeParkedQuestion();
  if (!(state.births || []).length) { showStage("stage-birth"); return; }
  await goToChat();
  if (question && state.sessionId && $("#stage-chat").classList.contains("active")) {
    qBox.value = question;
    autosizeQ();
    $("#ask-form").requestSubmit();
  }
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
const STAGES = [
  "stage-home", "stage-birth", "stage-chat",
  "stage-milan", "stage-panchang", "stage-muhurat",
  "stage-choghadiya", "stage-dashboard"
];

function showStage(id) {
  STAGES.forEach((s) => {
    const el = document.getElementById(s);
    if (el) el.classList.toggle("active", s === id);
  });
  document.body.classList.toggle("in-reading", id === "stage-chat");
  window.daTrack?.("screen", id.replace("stage-", ""));
  // On a phone the reading and the chart share one screen, switched by the
  // Reading / Chart & Dashas buttons. Arriving at the chat always means "ask a
  // question", so never inherit the chart side from an earlier visit: it has no
  // question box at all.
  if (id === "stage-chat") setWorkspaceView("chat");
  window.scrollTo({ top: 0, behavior: "instant" });
  document.documentElement.scrollTop = 0;
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
$("#home-cta")?.addEventListener("click", () => {
  window.daTrack?.("home_cta");     // DIVASTRO-134: the one primary button
  showStage("stage-birth");
});

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
  updateTimeHint();
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
  if (state.sessionId) {
    renderVargas(state.sessionId);
    renderAshtakavarga(state.sessionId);
    renderJaimini(state.sessionId);
    renderSudarshana(state.sessionId);
  }
  renderStarters();

  $("#thread").innerHTML = "";
  addBot(openingRead(c), null, false);
  // preventScroll matters: the composer sits at the bottom of a full-height
  // shell, so a plain focus() scrolls the body to reveal it and drags the site
  // header up off the top of the screen.
  // On a phone, focusing here opens the keyboard the moment a chart is cast,
  // covering the very reading the visitor came for. Only a keyboard-and-mouse
  // device auto-focuses.
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    $("#q").focus({ preventScroll: true });
  }
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

async function renderVargas(sessionId) {
  const pane = $("#pane-vargas");
  if (!pane) return;
  pane.innerHTML = `<p class="mini-title">${escapeHtml(t("vargaLoading"))}</p>`;
  try {
    const res = await fetch(`/api/vargas/${sessionId}?lang=${state.lang}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Could not load vargas');
    const vargas = data.vargas;
    const codes = data.available_codes || Object.keys(vargas);
    
    let activeCode = "D9";
    function drawVargaContent(code) {
      const v = vargas[code];
      if (!v) return;
      const selectHtml = `
        <div style="margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
          <label style="font-size: 12px; color: var(--gold); font-weight: bold;">${escapeHtml(t("vargaSelect"))}</label>
          <select id="varga-select" style="padding: 4px 8px; border-radius: 6px; background: rgba(255,255,255,0.06); color: var(--ink); border: 1px solid var(--line);">
            ${codes.map(c => `<option value="${c}" ${c === code ? 'selected' : ''}>${c}: ${escapeHtml(vargas[c].title)}</option>`).join('')}
          </select>
        </div>
      `;

      const headerHtml = `
        <div style="padding: 8px 10px; border-radius: 6px; background: rgba(212, 175, 55, 0.08); border: 1px solid var(--line); margin-bottom: 12px;">
          <div style="font-weight: bold; color: var(--gold); font-size: 13px;">${escapeHtml(v.title)} (${v.code})</div>
          <div style="font-size: 12px; color: var(--ink-dim);">${escapeHtml(v.purpose)} · ${escapeHtml(t("vargaAsc"))} <b>${escapeHtml(v.ascendant_label)}</b></div>
        </div>
      `;

      const rows = (v.placements || []).map(p => `
        <li>
          <span class="glyph">${p.house}</span>
          <span class="name"><b>${escapeHtml(p.planet_label)}</b><em>${escapeHtml(p.sign_label)}</em></span>
          <span class="pos">${escapeHtml(t("houseN").replace("{n}", p.house))}</span>
        </li>
      `).join('');

      pane.innerHTML = selectHtml + headerHtml + `<ul class="plist">${rows}</ul>`;

      const sel = $("#varga-select");
      if (sel) {
        sel.onchange = (e) => {
          activeCode = e.target.value;
          drawVargaContent(activeCode);
        };
      }
    }

    drawVargaContent(activeCode);
  } catch (err) {
    pane.innerHTML = `<p class="mini-title" style="color:var(--rose);">${escapeHtml(err.message)}</p>`;
  }
}

async function renderAshtakavarga(sessionId) {
  const pane = $("#pane-ashtakavarga");
  if (!pane) return;
  pane.innerHTML = `<p class="mini-title">${escapeHtml(t("avLoading"))}</p>`;
  try {
    const res = await fetch(`/api/ashtakavarga/${sessionId}?lang=${state.lang}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Could not load Ashtakavarga');

    const tbl = data.table;
    const note = data.financial_note;
    const rows = (tbl.rows || []).map(r => {
      const savScore = Number(r[r.length - 1]);
      let colorClass = 'var(--green)'; // Strong >= 28
      if (savScore < 25) colorClass = 'var(--rose)';
      else if (savScore < 28) colorClass = 'var(--gold)';

      const cells = r.map((c, idx) => {
        if (idx === 0) return `<td style="padding: 6px 4px; font-weight: bold;">${escapeHtml(String(c))}</td>`;
        if (idx === r.length - 1) return `<td style="padding: 6px 4px; font-weight: bold; color: ${colorClass}; text-align: center;">${c}</td>`;
        return `<td style="padding: 6px 3px; text-align: center; color: var(--ink-dim);">${c}</td>`;
      }).join('');
      return `<tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">${cells}</tr>`;
    }).join('');

    const headers = (tbl.headers || []).map((h, idx) => `
      <th style="padding: 6px 3px; font-size: 12px; text-align: ${idx === 0 ? 'left' : 'center'}; color: var(--gold);">${escapeHtml(h)}</th>
    `).join('');

    pane.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 12px; font-weight: bold; color: var(--gold);">${escapeHtml(t("avSarvaTitle"))}</span>
        <span style="font-size: 12px; color: var(--ink-dim);">${escapeHtml(t("avLegend"))}</span>
      </div>
      <div style="overflow-x: auto; margin-bottom: 12px;">
        <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
          <thead><tr style="border-bottom: 1px solid var(--line);">${headers}</tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      ${note ? `
        <div style="padding: 8px 10px; border-radius: 6px; background: rgba(212, 175, 55, 0.08); border-left: 3px solid var(--gold); font-size: 12px; color: var(--ink-dim); line-height: 1.4;">
          ${escapeHtml(note)}
        </div>
      ` : ''}
    `;
  } catch (err) {
    pane.innerHTML = `<p class="mini-title" style="color:var(--rose);">${escapeHtml(err.message)}</p>`;
  }
}

async function renderJaimini(sessionId) {
  const pane = $("#pane-jaimini");
  if (!pane) return;
  pane.innerHTML = `<p class="mini-title">${escapeHtml(t("jmLoading"))}</p>`;
  try {
    const res = await fetch(`/api/jaimini/${sessionId}?lang=${state.lang}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Could not load Jaimini');

    const karakas = data.karakas || [];
    const arudhas = data.arudhas || [];
    const kl = data.karakamsha;

    const karakaRows = karakas.map(k => `
      <li>
        <span class="glyph" style="font-size: 12px; font-weight:bold; color:var(--gold);">${escapeHtml(k.code)}</span>
        <span class="name">
          <b>${escapeHtml(k.planet_label)}</b> <em>${escapeHtml(k.sign_label)} (${k.degree})</em>
          <div style="font-size: 12px; color:var(--ink-dim);">${escapeHtml(k.title)} · ${escapeHtml(k.role)}</div>
        </span>
        <span class="pos" style="font-size: 12px;">D9: ${escapeHtml(k.navamsha_label)}</span>
      </li>
    `).join('');

    const arudhaRows = arudhas.map(a => `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.03); font-size: 12px;">
        <div>
          <b>${escapeHtml(a.code)} (${escapeHtml(a.title)})</b>: ${escapeHtml(a.sign_label)}
          <div style="font-size: 12px; color:var(--ink-dim);">${escapeHtml(a.area)}</div>
        </div>
        <span class="badge neutral" style="font-size: 12px;">${escapeHtml(t("houseShortN").replace("{n}", a.arudha_house))}</span>
      </div>
    `).join('');

    pane.innerHTML = `
      <div style="padding: 8px 10px; border-radius: 6px; background: rgba(212, 175, 55, 0.08); border-left: 3px solid var(--gold); margin-bottom: 12px; font-size: 12px; line-height: 1.4;">
        <b>${escapeHtml(t("jmKarakamsha"))}</b> ${escapeHtml(kl.sign_label)} (${escapeHtml(kl.atmakaraka_label)})<br/>
        ${escapeHtml(kl.summary)}
      </div>
      <p class="mini-title">${escapeHtml(t("jmKarakasTitle"))}</p>
      <ul class="plist" style="margin-bottom:14px;">${karakaRows}</ul>
      <p class="mini-title">${escapeHtml(t("jmArudhaTitle"))}</p>
      <div>${arudhaRows}</div>
    `;
  } catch (err) {
    pane.innerHTML = `<p class="mini-title" style="color:var(--rose);">${escapeHtml(err.message)}</p>`;
  }
}

async function renderSudarshana(sessionId) {
  const pane = $("#pane-sudarshana");
  if (!pane) return;
  pane.innerHTML = `<p class="mini-title">${escapeHtml(t("sdLoading"))}</p>`;
  try {
    const res = await fetch(`/api/sudarshana/${sessionId}?lang=${state.lang}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Could not load Sudarshana Chakra');

    const lagnas = data.lagnas;
    const houses = data.houses || [];
    const highlights = data.convergence_highlights || [];

    const lagnaHeader = `
      <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; margin-bottom:12px; text-align:center;">
        <div style="padding:6px; border-radius:6px; background:rgba(255,255,255,0.03); border:1px solid var(--line);">
          <div style="font-size: 12px; color:var(--ink-dim);">${escapeHtml(t("sdJanma"))}</div>
          <div style="font-weight:bold; color:var(--gold); font-size:12px;">${escapeHtml(lagnas.janma.sign_label)}</div>
        </div>
        <div style="padding:6px; border-radius:6px; background:rgba(255,255,255,0.03); border:1px solid var(--line);">
          <div style="font-size: 12px; color:var(--ink-dim);">${escapeHtml(t("sdChandra"))}</div>
          <div style="font-weight:bold; color:#56d4dd; font-size:12px;">${escapeHtml(lagnas.chandra.sign_label)}</div>
        </div>
        <div style="padding:6px; border-radius:6px; background:rgba(255,255,255,0.03); border:1px solid var(--line);">
          <div style="font-size: 12px; color:var(--ink-dim);">${escapeHtml(t("sdSurya"))}</div>
          <div style="font-weight:bold; color:#f0c674; font-size:12px;">${escapeHtml(lagnas.surya.sign_label)}</div>
        </div>
      </div>
    `;

    const highlightHtml = highlights.length ? `
      <div style="padding: 8px 10px; border-radius: 6px; background: rgba(34, 197, 94, 0.08); border-left: 3px solid #22c55e; margin-bottom: 12px; font-size: 12px; line-height: 1.4;">
        <b>${escapeHtml(t("sdConvergence"))}</b><br/>
        ${highlights.map(h => `<div>• ${escapeHtml(h)}</div>`).join('')}
      </div>
    ` : '';

    const houseRows = houses.map(h => {
      const badgeClass = h.verdict_code === 'strong' ? 'excellent' : (h.verdict_code === 'average' ? 'neutral' : 'caution');
      return `
        <div style="padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.04);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span style="font-size:12px; font-weight:bold;">${escapeHtml(t("houseN").replace("{n}", h.house))}: ${escapeHtml(h.title)}</span>
            <span class="badge ${badgeClass}" style="font-size:9.5px;">${escapeHtml(h.verdict)} (${h.score}/5)</span>
          </div>
          <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:4px; font-size:10.5px; color:var(--ink-dim);">
            <div>L: <b>${escapeHtml(h.janma_tier.sign_label)}</b> ${h.janma_tier.planets.length ? `(${escapeHtml(h.janma_tier.planets.join(','))})` : ''}</div>
            <div>M: <b>${escapeHtml(h.chandra_tier.sign_label)}</b> ${h.chandra_tier.planets.length ? `(${escapeHtml(h.chandra_tier.planets.join(','))})` : ''}</div>
            <div>S: <b>${escapeHtml(h.surya_tier.sign_label)}</b> ${h.surya_tier.planets.length ? `(${escapeHtml(h.surya_tier.planets.join(','))})` : ''}</div>
          </div>
        </div>
      `;
    }).join('');

    pane.innerHTML = lagnaHeader + highlightHtml + `<div style="margin-top:6px;">${houseRows}</div>`;
  } catch (err) {
    pane.innerHTML = `<p class="mini-title" style="color:var(--rose);">${escapeHtml(err.message)}</p>`;
  }
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

// DIVASTRO-124: the server sends `fallback_note` ("Answer shown in English", in
// the reader's language) for kn/te/ta/ml/bn/or. It belongs above the engine's
// English only — never above the AI's answer in their language.
function fallbackNoteHtml(result) {
  const note = result && result.fallback_note;
  return note ? `<p class="incomplete-note lang-fallback-note">${escapeHtml(note)}</p>` : "";
}

function addBot(md, result, withReasoning = true) {
  const el = document.createElement("div");
  el.className = "msg bot";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = verdictHtml(result) + markdown(md) +
    (withReasoning ? reasoningHtml(result) : "");
  el.append(bubble);
  el.append(answerActions(bubble));
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
  // Reader has scrolled up while a long answer keeps arriving: offer a way back.
  $("#jump-latest").hidden = force || nearBottom;
}

/* ------------------------------------------------------------
   Reading-screen ergonomics (DIVASTRO-73/74): a question box that grows,
   a phone keyboard that does not cover the answer, text size, copy/share.
   ------------------------------------------------------------ */
const qBox = $("#q");
const hasKeyboardAndMouse = window.matchMedia("(hover: hover) and (pointer: fine)");

function autosizeQ() {
  qBox.style.height = "auto";
  // CSS max-height clamps this; beyond it the box scrolls inside itself.
  qBox.style.height = `${qBox.scrollHeight + 2}px`;
}
qBox.addEventListener("input", autosizeQ);

// Keyboard and mouse: Enter sends, Shift+Enter is a new line. Touch keyboards:
// Enter is a new line (nobody wants half a thought sent) and the button sends.
qBox.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing && hasKeyboardAndMouse.matches) {
    e.preventDefault();
    $("#ask-form").requestSubmit();
  }
});

// While typing on a phone the chrome steps aside (see body.kbd in styles.css).
qBox.addEventListener("focus", () => {
  if (!hasKeyboardAndMouse.matches) document.body.classList.add("kbd");
});
qBox.addEventListener("blur", () => {
  document.body.classList.remove("kbd");
  // The keyboard just closed: some browsers leave the page scrolled down, with the
  // question box under the bottom edge. Put the page back.
  setTimeout(resetWindowScroll, 120);
  setTimeout(resetWindowScroll, 450);
});

/* The reading screen is exactly one screen tall and never scrolls as a page, so any
   page scroll is a browser side-effect (keyboard, focus, in-app toolbar) that pushes
   the question box out of sight. Undo it, but never while the box is being typed in
   (the browser is deliberately scrolling to keep it above the keyboard then). */
function resetWindowScroll() {
  if (!document.body.classList.contains("in-reading") || document.activeElement === qBox) return;
  if (window.scrollY || document.documentElement.scrollTop || document.body.scrollTop) {
    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  }
}
if (window.visualViewport) {
  window.visualViewport.addEventListener("scroll", resetWindowScroll);
  window.visualViewport.addEventListener("resize", resetWindowScroll);
}
window.addEventListener("scroll", resetWindowScroll, { passive: true });

/* Old Android WebViews (and some in-app browsers) do not know 100dvh and fall back to
   100vh, which counts the area under the toolbar - the box sits below the screen. Where
   dvh is missing, size the reading screen from the real window height instead. */
if (!(window.CSS && CSS.supports && CSS.supports("height", "100dvh"))) {
  const sizeToWindow = () => {
    document.documentElement.style.setProperty("--app-h", `${window.innerHeight}px`);
    document.body.classList.add("js-height");
  };
  sizeToWindow();
  window.addEventListener("resize", sizeToWindow);
  window.addEventListener("orientationchange", () => setTimeout(sizeToWindow, 200));
}

// The on-screen keyboard: the page is told to RESIZE for it (interactive-widget=
// resizes-content in the viewport meta tag), so 100dvh is the visible height and
// the question box simply sits above the keyboard. An earlier version of this
// resized the page from visualViewport as well; on Android Chrome the browser had
// already scrolled the visible window down to show the box, and shrinking the page
// on top of that moved the box back OUT of that window - what was typed vanished
// behind the keyboard until it was dismissed. One mechanism only.
qBox.addEventListener("focus", () => {
  // Once the keyboard has finished opening, keep the latest answer in view.
  setTimeout(() => scrollThread(true), 350);
});

$("#jump-latest").addEventListener("click", () => scrollThread(true));
$("#thread").addEventListener("scroll", () => {
  const t = $("#thread");
  if (t.scrollHeight - t.scrollTop - t.clientHeight < 80) $("#jump-latest").hidden = true;
}, { passive: true });

// Chart chips (phone) and chart panel (wide screens) fold away on request.
$("#chips-toggle").addEventListener("click", () => {
  const open = $("#chips").classList.toggle("open");
  $("#chips-toggle").setAttribute("aria-expanded", String(open));
});
(() => {
  const ws = $(".workspace"), btn = $("#panel-toggle");
  let hidden = false;
  try { hidden = localStorage.getItem("da_panel_hidden") === "1"; } catch { /* private mode */ }
  const apply = () => {
    ws.classList.toggle("panel-hidden", hidden);
    btn.setAttribute("aria-expanded", String(!hidden));
  };
  apply();
  btn.addEventListener("click", () => {
    hidden = !hidden;
    try { localStorage.setItem("da_panel_hidden", hidden ? "1" : "0"); } catch { /* ignore */ }
    apply();
  });
})();

// Text size for the answers: A- / A+, remembered.
(() => {
  const STEPS = [0.9, 1, 1.1, 1.2, 1.35];
  let i = 1;
  try {
    const saved = parseFloat(localStorage.getItem("da_read_scale") || "1");
    if (STEPS.includes(saved)) i = STEPS.indexOf(saved);
  } catch { /* private mode */ }
  const apply = () => {
    document.documentElement.style.setProperty("--read-scale", String(STEPS[i]));
    try { localStorage.setItem("da_read_scale", String(STEPS[i])); } catch { /* ignore */ }
    $("#fs-down").disabled = i === 0;
    $("#fs-up").disabled = i === STEPS.length - 1;
  };
  $("#fs-down").addEventListener("click", () => { i = Math.max(0, i - 1); apply(); });
  $("#fs-up").addEventListener("click", () => { i = Math.min(STEPS.length - 1, i + 1); apply(); });
  apply();
})();

// Copy / Share under each answer. Share uses the phone's own share sheet when
// there is one (WhatsApp is right there); otherwise it opens WhatsApp directly.
function answerActions(bubble) {
  const row = document.createElement("div");
  row.className = "msg-actions";
  row.innerHTML =
    `<button type="button" data-act="copy">${escapeHtml(t("copyAns"))}</button>` +
    `<button type="button" data-act="share">${escapeHtml(t("shareAns"))}</button>`;
  const text = () => `${bubble.innerText.trim()}\n\n— Divine Astro · divineastro.org`;
  row.querySelector("[data-act=copy]").onclick = async () => {
    try {
      await navigator.clipboard.writeText(text());
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text(); document.body.append(ta); ta.select();
      try { document.execCommand("copy"); } catch { /* nothing more to try */ }
      ta.remove();
    }
    if (typeof toast === "function") toast(t("copiedMsg"));
  };
  row.querySelector("[data-act=share]").onclick = () => {
    // Long readings are trimmed for the URL form; the share sheet takes it all.
    const full = text();
    if (navigator.share) { navigator.share({ text: full }).catch(() => {}); return; }
    const short = full.length > 1400 ? `${full.slice(0, 1400)}…\n\n— Divine Astro · divineastro.org` : full;
    window.open(`https://wa.me/?text=${encodeURIComponent(short)}`, "_blank", "noopener");
  };
  return row;
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
  autosizeQ();
  addUser(question);
  const pending = addThinking();

  let bubble = null;
  let answerEl = null;       // the answer's bubble, for the offer card under it (DIVASTRO-149)
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
  window.daTrack?.("ask_sent");
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
            const b = addBot(result.answer_engine, result);
            answerEl = b;
            b.insertAdjacentHTML("afterbegin", fallbackNoteHtml(result));
          } else {
            bubble = addBot("", result, false);
            answerEl = bubble;
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
          bubble.innerHTML = fallbackNoteHtml(result) +
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
    // DIVASTRO-149: a quiet offer under the finished answer (account.js decides
    // whether one is due: signed in, questions left, not shown before this session).
    if (answerEl && result && typeof maybeOfferAfterAnswer === "function") {
      maybeOfferAfterAnswer(result, answerEl);
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
    // A desktop keeps the cursor in the box for the next question. A phone must NOT:
    // focusing pops the keyboard unasked, and on iOS and in-app browsers (WhatsApp,
    // Facebook) that scrolls the page and can leave the question box below the screen
    // when the keyboard goes away. The reader taps the box when they want to ask.
    if (hasKeyboardAndMouse.matches) input.focus({ preventScroll: true });
    else resetWindowScroll();
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
function setWorkspaceView(view) {
  $(".workspace").dataset.view = view;
  $$(".vview").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
  // A chart drawn while its pane was hidden has no box to size against,
  // so redraw it once it is actually on screen.
  if (view === "chart" && state.chart) paintChart();
}
$$(".vview").forEach((btn) => {
  btn.onclick = () => setWorkspaceView(btn.dataset.view);
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
    const dash = await (await fetch(`/api/dashboard/${state.sessionId}?language=${state.lang}`)).json();
    
    // Populate Panchang
    $("#dash-tithi").textContent = dash.panchang.tithi || "—";
    $("#dash-nakshatra").textContent = dash.panchang.nakshatra || "—";
    $("#dash-yoga").textContent = dash.panchang.yoga || "—";
    $("#dash-karana").textContent = dash.panchang.karana || "—";
    
    // Populate Muhurtha
    $("#dash-abhijit").textContent = dash.panchang.muhurtha.abhijit.start ? 
      `${dash.panchang.muhurtha.abhijit.start.slice(11, 16)} - ${dash.panchang.muhurtha.abhijit.end.slice(11, 16)}` : t("noneToday");
    $("#dash-rahu-kalam").textContent = dash.panchang.muhurtha.rahu_kaal.start ? 
      `${dash.panchang.muhurtha.rahu_kaal.start.slice(11, 16)} - ${dash.panchang.muhurtha.rahu_kaal.end.slice(11, 16)}` : "—";
    $("#dash-sunrise").textContent = dash.panchang.sunrise ? dash.panchang.sunrise.slice(11, 16) : "—";
    $("#dash-sunset").textContent = dash.panchang.sunset ? dash.panchang.sunset.slice(11, 16) : "—";
    
    // Populate Dasha
    $("#dash-mahadasha-lord").textContent = dash.dasha.mahadasha ? (tPlanet(dash.dasha.mahadasha.lord) || dash.dasha.mahadasha.lord) : "—";
    $("#dash-mahadasha-dates").textContent = dash.dasha.mahadasha ? `${dash.dasha.mahadasha.start} - ${dash.dasha.mahadasha.end}` : "—";
    $("#dash-antardasha-lord").textContent = dash.dasha.antardasha ? (tPlanet(dash.dasha.antardasha.lord) || dash.dasha.antardasha.lord) : "—";
    $("#dash-antardasha-dates").textContent = dash.dasha.antardasha ? `${dash.dasha.antardasha.start} - ${dash.dasha.antardasha.end}` : "—";
    
    // Populate Daily Forecast
    const badge = $("#transit-badge");
    const scoreText = dash.daily_transit.score || "";
    let badgeClass = "neutral";
    if (scoreText.includes("Excellent") || scoreText.includes("उत्तम")) badgeClass = "excellent";
    else if (scoreText.includes("Caution") || scoreText.includes("सावधानी")) badgeClass = "caution";
    badge.className = `badge ${badgeClass}`;
    badge.textContent = scoreText;
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
        const status = item[4]; // 'past', 'current', or 'ahead' (or localized)
        const pct = (years / totalYears) * 100;
        const normStatus = (status === 'सक्रिय' || status === 'current') ? 'current' : ((status === 'गत काल' || status === 'past') ? 'past' : 'ahead');
        
        blocksHtml += `
          <div class="timeline-block ${normStatus}" style="width: ${pct}%;" 
               data-lord="${escapeHtml(lord)}" data-years="${years}" 
               data-start="${escapeHtml(start)}" data-end="${escapeHtml(end)}" data-status="${status}">
            <span class="block-lord">${escapeHtml(lord.slice(0, 3))}</span>
            <span class="block-years">${years}y</span>
          </div>
        `;
      });
      blocksHtml += '</div>';
      
      const currentDasha = dash.dasha.ladder.find(item => item[4] === "current" || item[4] === "सक्रिय") || dash.dasha.ladder[0];
      const periodStatus = currentDasha[4];
      blocksHtml += `
        <div class="timeline-detail-box" id="timeline-detail-box" style="margin-top: 10px;">
          ${t("selectedPeriod")} <b>${escapeHtml(currentDasha[0])} ${t("mahadashaWord")}</b> (${currentDasha[1]} ${t("yearsWord")})<br/>
          ${t("durationWord")} <b>${escapeHtml(currentDasha[2])}</b> ${t("toWord")} <b>${escapeHtml(currentDasha[3])}</b> (${String(periodStatus).toUpperCase()})
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
            ${t("selectedPeriod")} <b>${escapeHtml(lord)} ${t("mahadashaWord")}</b> (${years} ${t("yearsWord")})<br/>
            ${t("durationWord")} <b>${escapeHtml(start)}</b> ${t("toWord")} <b>${escapeHtml(end)}</b> (${String(status).toUpperCase()})
          `;
        };
        block.addEventListener("mouseenter", updateBox);
        block.addEventListener("click", updateBox);
      });
    }
    if (typeof offerDashboard === "function") offerDashboard();     // DIVASTRO-149
    if (typeof renderDashReports === "function") renderDashReports();   // DIVASTRO-150
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
    const data = await (await fetch(`/api/remedies/${state.sessionId}?language=${state.lang}`)).json();
    
    // Gemstones
    const gemsList = $("#gems-list");
    gemsList.innerHTML = Object.values(data.gemstones).map(g => `
      <div class="gem-card">
        <div class="gem-left">
          <h4>${escapeHtml(g.role)}</h4>
          <p>${escapeHtml(g.name)}</p>
        </div>
        <div class="gem-right">
          ${t("metalLabel")} <b>${escapeHtml(g.metal)}</b><br/>
          ${t("wearOnLabel")} <b>${escapeHtml(g.finger)}</b>
        </div>
      </div>
    `).join("");
    
    // Remedies
    $("#dasha-remedies-content").innerHTML = `
      <p>${t("currentMDRuled")} <b>${escapeHtml(data.dasha_remedies.mahadasha_lord)}</b>.</p>
      <p><b>${t("recommendedMantra")}</b><br/>
         <span style="font-size: 14px; color: var(--gold); display: block; margin-top: 6px; font-family: monospace;">${escapeHtml(data.dasha_remedies.mantra)}</span>
      </p>
      <p><b>${t("charityFasting")}</b><br/>
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
                    <span class="badge ${ph.status === 'current' ? 'caution' : (ph.status === 'past' ? 'excellent' : 'neutral')}" style="padding: 2px 6px; font-size: 12px;">
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
    const ksTypeName = ks.type?.name ?? "Formed";
    const ksBadge = ks.forms ? `<span class="badge caution">Kaal Sarp formed (${escapeHtml(ksTypeName)})</span>` : '<span class="badge excellent">No Kaal Sarp</span>';

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
        <p>Forms when all seven classical planets are hemmed between Rahu and Ketu. ${ks.forms ? `Your chart forms the <b>${escapeHtml(ks.type?.name ?? "Kaal Sarp")}</b> type of Kaal Sarp (Rahu in house ${escapeHtml(ks.type?.rahu_house ?? "—")}).` : "Your planets are distributed freely, forming no Kaal Sarp alignment."}</p>
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

// DIVASTRO-124: one button per language the server can print a kundali PDF in
// (window.DA_PDF_LANGS, from pdf_report.pdf_languages(): en, hi and each
// regional language whose script font is installed). The English and Hindi
// buttons are in index.html; the others are added here, after them.
function renderPdfLangButtons() {
  const box = $("#generate-pdf-en")?.parentElement;
  if (!box) return;
  const codes = (window.DA_PDF_LANGS && window.DA_PDF_LANGS.length) ? window.DA_PDF_LANGS : ["en", "hi"];
  box.style.flexWrap = "wrap";
  for (const code of codes) {
    let btn = $(`#generate-pdf-${code}`);
    if (!btn) {
      const L = langInfo(code);
      btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn";
      btn.id = `generate-pdf-${code}`;
      btn.style.minWidth = "120px";
      btn.lang = L.htmlLang || code;
      btn.textContent = L.english && L.english !== L.native ? `${L.native} (${L.english})` : L.native;
      box.append(btn);
    }
    btn.addEventListener("click", () => {
      if (state.sessionId) {
        window.location.href = `/api/pdf/chart/${state.sessionId}?lang=${code}`;
        $("#kundali-pdf-modal").style.display = "none";
      }
    });
  }
}
renderPdfLangButtons();

/* ============================================================
   DIVASTRO-101 — home screen: show value before the first tap.
   In a week of real traffic ~21 of ~23 visitors left the home screen without
   doing anything. Kept as one self-contained block (plus one call in
   applyLanguage) so the parallel analytics, SEO and sign-in work merges cleanly.
   The Today strip's data and city picker live in tools.js beside the Panchang
   tool, whose API and place search they reuse; this block owns the sample
   question's copy and its call to action.
   ============================================================ */
function renderHomeValue() {
  const set = (sel, text) => { const el = $(sel); if (el) el.textContent = text; };
  set("#sample-qa-tag", t("sampleTag"));
  set("#sample-q", t("sampleQ"));
  set("#sample-a", t("sampleA"));
  set("#sample-note", t("sampleNote"));
  set("#sample-ask-label", t("sampleAsk"));
  // tools.js loads after this file, so on the very first call it is not there yet;
  // it renders itself once loaded, and every later language switch reaches it here.
  if (typeof window.renderTodayStrip === "function") window.renderTodayStrip();
}

// "Ask your own question" goes exactly where the free-questions box goes: signed out
// it opens sign-in; signed in it opens the chat (goToChat sends someone with no chart
// yet to the birth form first, since an answer needs a chart).
$("#sample-ask")?.addEventListener("click", () => {
  if (typeof acct !== "undefined" && acct.user) goToChat();
  else if (typeof openSignIn === "function") openSignIn();
});
