/* Free Vedic tools: Kundali Milan, Panchang, and Muhurat Finder.
 *
 * Deliberately self-contained. The birth form in app.js has its own place
 * autocomplete wired to specific element ids; generalising it would have meant
 * editing the one flow that already works and earns money. A small local picker
 * costs a few lines and risks nothing.
 *
 * Depends on app.js only for `showStage`, `t` and `escapeHtml`, all globals.
 */
'use strict';

(() => {
  const q = (s, r = document) => r.querySelector(s);
  const qa = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = (s) => (typeof escapeHtml === 'function' ? escapeHtml(s)
    : String(s ?? '').replace(/[&<>"']/g, (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])));
  const tr = (k, fallback) => {
    try { const v = t(k); return v && v !== k ? v : fallback; } catch { return fallback; }
  };

  // DIVASTRO-103: "today" is the calendar date at the chosen place (India by
  // default), not the UTC date — toISOString() showed yesterday 00:00-05:30 IST.
  // A function declaration (hoisted), so every tool below can use it.
  function todayIn(tz) {
    try {
      return new Intl.DateTimeFormat('en-CA', { timeZone: tz || 'Asia/Kolkata' }).format(new Date());
    } catch (_) {
      return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata' }).format(new Date());
    }
  }
  // 'YYYY-MM-DD' plus n days, in pure calendar arithmetic (no timezone involved).
  function addDaysIso(iso, n) {
    const d = new Date(`${iso}T00:00:00Z`);
    d.setUTCDate(d.getUTCDate() + n);
    return d.toISOString().slice(0, 10);
  }

  // Read a response as JSON WITHOUT surfacing the browser's own parse error. When the
  // server fails with a plain-text "Internal Server Error", `await res.json()` used to
  // throw `Unexpected token 'I', "Internal S"... is not valid JSON` straight into the
  // page. A failed request now yields a readable message instead; a *successful*
  // response that isn't JSON is a genuine fault and throws.
  async function readJson(res) {
    const text = await res.text();
    try { return text ? JSON.parse(text) : {}; } catch { /* not JSON */ }
    if (res.ok) throw new Error('The server sent a reply this page could not read. Please try again.');
    return { detail: `The server ran into a problem (error ${res.status}). Please try again in a moment.` };
  }

  // The server labels an unnamed person "—", which is truthy, so `name || 'Groom'`
  // never fell back and the Mangal section read "—: Not Manglik".
  const named = (n) => (n && n.trim() && n.trim() !== '—' ? n.trim() : '');

  /* ---------------------------------------------------------- place picker */
  function placePicker(input, list, chosenEl) {
    let chosen = null;
    let timer = null;

    const hide = () => { list.hidden = true; list.innerHTML = ''; };

    input.addEventListener('input', () => {
      chosen = null;
      if (chosenEl) chosenEl.hidden = true;
      clearTimeout(timer);
      const term = input.value.trim();
      if (term.length < 2) { hide(); return; }
      timer = setTimeout(async () => {
        let places = [];
        try {
          const res = await fetch(`/api/places?q=${encodeURIComponent(term)}`);
          places = (await res.json()).results || [];
        } catch { hide(); return; }
        if (!places.length) { hide(); return; }
        list.innerHTML = places.map((p, i) =>
          `<li data-i="${i}">${esc(p.label)}<span>${esc(p.timezone)}</span></li>`).join('');
        list.hidden = false;
        qa('li', list).forEach((li) => {
          li.onclick = () => {
            chosen = places[Number(li.dataset.i)];
            input.value = chosen.label;
            if (chosenEl) {
              chosenEl.textContent = `${chosen.latitude.toFixed(4)}, ` +
                `${chosen.longitude.toFixed(4)} · ${chosen.timezone}`;
              chosenEl.hidden = false;
            }
            hide();
            input.dispatchEvent(new CustomEvent('place:chosen', { detail: chosen }));
          };
        });
      }, 180);
    });

    document.addEventListener('click', (e) => {
      if (e.target !== input && !list.contains(e.target)) hide();
    });

    return () => chosen;
  }

  /* ------------------------------------------------------------- navigation */
  q('#open-milan')?.addEventListener('click', () => showStage('stage-milan'));
  q('#open-panchang')?.addEventListener('click', () => {
    showStage('stage-panchang');
    if (!q('#panchang-result').innerHTML) loadPanchang();
  });
  q('#open-muhurat')?.addEventListener('click', () => {
    showStage('stage-muhurat');
    initMuhuratDates();
  });

  /* ---------------------------------------------------------- kundali milan */
  const sides = {};
  qa('.milan-card').forEach((form) => {
    const side = form.dataset.side;
    sides[side] = {
      form,
      get: placePicker(q('[data-f="place"]', form), q('[data-f="results"]', form),
                       q('[data-f="chosen"]', form)),
    };
  });

  function readSide(side) {
    const { form, get } = sides[side];
    const val = (f) => q(`[data-f="${f}"]`, form).value;
    const place = get();
    const known = !q('[data-f="unknown"]', form).checked;
    if (!val('date')) throw new Error(tr('milanNeedDate', 'Both dates of birth are needed.'));
    if (!place) throw new Error(tr('milanNeedPlace',
      'Pick both birth places from the suggestions so the coordinates are exact.'));
    return {
      name: val('name').trim(), date: val('date'),
      time: known ? (val('time') || '12:00') : '12:00',
      time_known: known,
      place: place.label, latitude: place.latitude, longitude: place.longitude,
      timezone: place.timezone,
    };
  }

  q('#milan-go')?.addEventListener('click', async () => {
    const btn = q('#milan-go');
    const err = q('#milan-error');
    err.hidden = true;
    let payload;
    try {
      const currentLang = (typeof state !== 'undefined' && state.lang) ? state.lang : 'en';
      payload = { groom: readSide('groom'), bride: readSide('bride'), lang: currentLang };
    } catch (ex) { err.textContent = ex.message; err.hidden = false; return; }

    btn.disabled = true; btn.classList.add('busy');
    try {
      const res = await fetch('/api/match', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await readJson(res);
      if (!res.ok) throw new Error(data.detail || 'Could not match those charts.');
      renderMilan(data);
    } catch (ex) {
      err.textContent = ex.message; err.hidden = false;
    } finally {
      btn.disabled = false; btn.classList.remove('busy');
    }
  });

  function renderMilan(d) {
    const ak = d.ashtakoot;
    const pct = Math.round((ak.total / ak.maximum) * 100);
    const tone = ak.total >= 25 ? 'good' : ak.total >= 18 ? 'ok' : 'poor';

    const rows = ak.kootas.map((k) => `
      <tr>
        <td class="kt-name">${esc(k.label)}</td>
        <td class="kt-score ${k.score === 0 ? 'zero' : ''}">${k.score} / ${k.max}</td>
        <td class="kt-note">${esc(k.note || '')}</td>
      </tr>`).join('');

    const manglik = (who, m) => {
      if (!m) return '';
      const refs = (m.references || []).filter(r => r.afflicted).map(r => r.reference);
      const isAff = m.manglik;
      return `<li><b>${esc(who)}:</b> ${
        isAff
          ? `Manglik (${esc(m.severity || 'mild')})`
          : 'Not Manglik'}${m.summary ? ` — ${esc(m.summary)}` : ''}</li>`;
    };

    const cancellations = (ak.cancellations_applied || []).map(c => typeof c === 'object' ? `${c.koota}: ${c.reason}` : c).join('; ');

    q('#milan-result').innerHTML = `
      <div class="milan-score ${tone}">
        <div class="ms-num">${ak.total}<span>/ ${ak.maximum}</span></div>
        <div class="ms-meta">
          <div class="ms-verdict">${esc(ak.verdict || '')}</div>
          <div class="ms-bar"><i style="width:${pct}%"></i></div>
          ${cancellations
            ? `<div class="ms-note">${esc(ak.total_before_cancellation)} ${tr('beforeCancellation', 'before cancellation')} — ${esc(cancellations)}</div>` : ''}
        </div>
      </div>

      <table class="koota-table"><tbody>${rows}</tbody></table>

      <div class="card milan-extra">
        <h3>${esc(tr('mangalTitle', 'Mangal Dosha Analysis'))}</h3>
        <ul style="line-height: 1.6; font-size: 13.5px; padding-left: 18px; margin: 10px 0;">
          ${manglik(named(ak.groom.name) || 'Groom (वर)', d.mangal.groom)}
          ${manglik(named(ak.bride.name) || 'Bride (कन्या)', d.mangal.bride)}
        </ul>
        ${d.mangal.pair?.note ? `<p style="margin-top: 10px; color: var(--gold);">${esc(d.mangal.pair.note)}</p>` : ''}
        ${d.mangal.pair?.tradition_note ? `<p class="muted-line" style="margin-top: 6px; font-size: 12px;">${esc(d.mangal.pair.tradition_note)}</p>` : ''}
      </div>

      ${d.caveat ? `<p class="warn-line">${esc(d.caveat)}</p>` : ''}
      <p class="muted-line">${esc(ak.band_note || '')} ${esc(ak.convention_note || '')}</p>`;
    q('#milan-result').hidden = false;
    q('#milan-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ---------------------------------------------------------------- panchang */
  const paPick = placePicker(q('#pa-place'), q('#pa-results'), q('#pa-chosen'));
  let paPlace = null;

  q('#pa-place')?.addEventListener('place:chosen', (e) => {
    paPlace = e.detail;
    loadPanchang();
  });
  q('#pa-date')?.addEventListener('change', () => loadPanchang());

  async function loadPanchang() {
    const err = q('#panchang-error');
    err.hidden = true;
    const place = paPlace || paPick() ||
      { latitude: 28.6139, longitude: 77.2090, timezone: 'Asia/Kolkata', label: 'New Delhi, India' };
    const params = new URLSearchParams({
      latitude: place.latitude, longitude: place.longitude, timezone: place.timezone || '',
    });
    const date = q('#pa-date').value;
    if (date) params.set('date', date);

    try {
      const res = await fetch(`/api/panchang?${params}`);
      const data = await readJson(res);
      if (!res.ok) throw new Error(data.detail || 'Could not compute the panchang.');
      renderPanchang(data, place.label);
    } catch (ex) {
      err.textContent = ex.message; err.hidden = false;
    }
  }

  const hhmm = (iso) => (iso ? String(iso).slice(11, 16) : '—');
  const span = (w) => (w ? `${hhmm(w.start)} – ${hhmm(w.end)}` : '—');

  function renderPanchang(p, label) {
    const limb = (rows, key) => (rows || []).map((r) =>
      `<div class="limb-line"><b>${esc(r.label || r.name)}</b> ` +
      `<span>${esc(tr('until', 'until'))} ${hhmm(r.ends)}</span></div>`).join('') || '—';

    q('#panchang-result').innerHTML = `
      <div class="card pa-card">
        <div class="pa-head">
          <div>
            <h2>${esc(p.summary.vara)} · ${esc(p.date)}</h2>
            <p class="muted-line">${esc(label || '')} ${
              p.reckoned_from === 'sunrise' ? '' : `(${esc(p.reckoned_from)})`}</p>
          </div>
          <div class="pa-sun">
            <div>☀ ${hhmm(p.sun.rise)} – ${hhmm(p.sun.set)}</div>
            <div>☾ ${hhmm(p.moon.rise)} – ${hhmm(p.moon.set)}</div>
          </div>
        </div>

        <div class="pa-limbs">
          <div><h4>${esc(tr('tithiL', 'Tithi'))}</h4>${limb(p.tithi)}</div>
          <div><h4>${esc(tr('nakL', 'Nakshatra'))}</h4>${limb(p.nakshatra)}</div>
          <div><h4>${esc(tr('yogaL', 'Yoga'))}</h4>${limb(p.yoga)}</div>
          <div><h4>${esc(tr('karanaL', 'Karana'))}</h4>${limb(p.karana)}</div>
        </div>
      </div>

      <div class="card pa-card">
        <h3>${esc(tr('timingsL', 'Timings'))}</h3>
        <div class="pa-times">
          <div class="bad"><span>Rahu Kaal</span><b>${span(p.muhurta.rahu_kaal)}</b></div>
          <div class="bad"><span>Yamaganda</span><b>${span(p.muhurta.yamaganda)}</b></div>
          <div class="bad"><span>Gulika Kaal</span><b>${span(p.muhurta.gulika_kaal)}</b></div>
          <div class="good"><span>Abhijit Muhurta</span><b>${
            p.muhurta.abhijit ? span(p.muhurta.abhijit) : esc(tr('none', 'none today'))}</b></div>
        </div>
      </div>

      ${(p.notes || []).length
        ? `<p class="muted-line">${esc(p.notes.join(' '))}</p>` : ''}`;
    q('#panchang-result').hidden = false;
  }

  /* ------------------------------------------------- home: the Today strip */
  // DIVASTRO-101. Of ~23 real visitors in a week, ~21 left the home screen without
  // tapping anything: nothing on it was worth having by itself. Today's tithi,
  // nakshatra and Rahu Kaal are what people check daily, cost no LLM tokens, and
  // come from the same /api/panchang the Panchang tool above already calls, so
  // there is no second computation to keep in step with this one.
  //
  // It lives here rather than in app.js because it reuses this file's place picker
  // and opens the Panchang tool with the same city already chosen.
  const TODAY_KEY = 'astro.todayCity';
  const DELHI = { latitude: 28.6139, longitude: 77.2090, timezone: 'Asia/Kolkata', label: 'New Delhi, India' };
  // The API speaks English names; Hindi visitors get the names they actually use.
  // Same tables as app/astro/muhurat.py.
  const PAKSHA_HI = { Shukla: 'शुक्ल', Krishna: 'कृष्ण' };
  const TITHI_HI = {
    Pratipada: 'प्रतिपदा', Dwitiya: 'द्वितीया', Tritiya: 'तृतीया', Chaturthi: 'चतुर्थी',
    Panchami: 'पंचमी', Shashthi: 'षष्ठी', Saptami: 'सप्तमी', Ashtami: 'अष्टमी',
    Navami: 'नवमी', Dashami: 'दशमी', Ekadashi: 'एकादशी', Dwadashi: 'द्वादशी',
    Trayodashi: 'त्रयोदशी', Chaturdashi: 'चतुर्दशी', Purnima: 'पूर्णिमा', Amavasya: 'अमावस्या',
  };
  const NAK_HI = {
    Ashwini: 'अश्विनी', Bharani: 'भरणी', Krittika: 'कृत्तिका', Rohini: 'रोहिणी',
    Mrigashira: 'मृगशिरा', Ardra: 'आर्द्रा', Punarvasu: 'पुनर्वसु', Pushya: 'पुष्य',
    Ashlesha: 'आश्लेषा', Magha: 'मघा', 'Purva Phalguni': 'पूर्वा फाल्गुनी',
    'Uttara Phalguni': 'उत्तरा फाल्गुनी', Hasta: 'हस्त', Chitra: 'चित्रा', Swati: 'स्वाति',
    Vishakha: 'विशाखा', Anuradha: 'अनुराधा', Jyeshtha: 'ज्येष्ठा', Mula: 'मूल',
    'Purva Ashadha': 'पूर्वाषाढ़ा', 'Uttara Ashadha': 'उत्तराषाढ़ा', Shravana: 'श्रवण',
    Dhanishta: 'धनिष्ठा', Shatabhisha: 'शतभिषा', 'Purva Bhadrapada': 'पूर्व भाद्रपद',
    'Uttara Bhadrapada': 'उत्तर भाद्रपद', Revati: 'रेवती',
  };

  const todayStrip = q('#today-strip');
  let todayPlace = DELHI;
  let todayData = null;
  let todaySeq = 0;                       // a slow reply for an old city must not overwrite a newer one

  // Anything in storage was written by an older page (or by hand): use it only if it
  // still looks like a place, else quietly fall back to Delhi.
  try {
    const saved = JSON.parse(localStorage.getItem(TODAY_KEY) || 'null');
    if (saved && Number.isFinite(saved.latitude) && Number.isFinite(saved.longitude)
        && typeof saved.label === 'string') todayPlace = saved;
  } catch { /* private mode or bad JSON: Delhi */ }

  // The panchang lists every tithi/nakshatra that touches the day; "today's" is the
  // one running now, not the one at sunrise (they differ for much of the day).
  const current = (rows) => {
    const now = Date.now();
    return (rows || []).find((r) => Date.parse(r.starts) <= now && now < Date.parse(r.ends))
      || (rows || [])[0] || null;
  };

  function renderTodayStrip() {
    if (!todayStrip) return;
    const hi = typeof state !== 'undefined' && state.lang === 'hi';
    const set = (sel, text) => { const el = q(sel); if (el) el.textContent = text; };
    set('#today-title', tr('todayTitle', 'Today'));
    set('#today-tithi-l', tr('todayTithi', 'Tithi'));
    set('#today-nak-l', tr('todayNak', 'Nakshatra'));
    set('#today-rahu-l', tr('todayRahu', 'Rahu Kaal'));
    set('#today-city-name', String(todayPlace.label).split(',')[0]);
    q('#today-city')?.setAttribute('aria-label', `${tr('todayChange', 'Change city')}: ${todayPlace.label}`);
    q('#today-place')?.setAttribute('placeholder', tr('todayCityPh', 'Start typing a city…'));
    if (!todayData) return;               // still loading: the skeleton stays

    const ti = current(todayData.tithi);
    const nk = current(todayData.nakshatra);
    const rk = todayData.muhurta && todayData.muhurta.rahu_kaal;
    const tithi = ti ? (hi ? `${PAKSHA_HI[ti.paksha] || ti.paksha} ${TITHI_HI[ti.name] || ti.name}`
                           : (ti.label || ti.name)) : '—';
    const nak = nk ? (hi ? NAK_HI[nk.name] || nk.name : nk.name) : '—';
    const now = Date.now();
    const inRahu = !!(rk && Date.parse(rk.start) <= now && now < Date.parse(rk.end));
    const rahu = rk ? `${hhmm(rk.start)}–${hhmm(rk.end)}` : '—';
    set('#today-tithi', tithi);
    set('#today-nak', nak);
    set('#today-rahu', inRahu ? `${rahu} · ${tr('todayNow', 'now')}` : rahu);
    q('#today-rahu')?.parentElement.classList.toggle('now', inRahu);
    q('#today-open')?.setAttribute('aria-label',
      `${tr('todayOpen', "Open today's full panchang")}. ${tr('todayTithi', 'Tithi')}: ${tithi}. ` +
      `${tr('todayNak', 'Nakshatra')}: ${nak}. ${tr('todayRahu', 'Rahu Kaal')}: ${rahu}.`);
  }
  // app.js calls this from applyLanguage, so the strip follows the EN / हिं switch.
  window.renderTodayStrip = renderTodayStrip;

  async function loadToday() {
    if (!todayStrip) return;
    const seq = ++todaySeq;
    todayData = null;
    todayStrip.classList.add('loading');
    renderTodayStrip();
    const params = new URLSearchParams({
      latitude: todayPlace.latitude, longitude: todayPlace.longitude, timezone: todayPlace.timezone || '',
    });
    try {
      const res = await fetch(`/api/panchang?${params}`);
      if (!res.ok) throw new Error(String(res.status));
      const data = await res.json();
      if (seq !== todaySeq) return;
      todayData = data;
      todayStrip.classList.remove('loading');
      renderTodayStrip();
    } catch {
      // A home screen that shows a broken box is worse than one without it.
      if (seq === todaySeq) todayStrip.hidden = true;
    }
  }

  if (todayStrip) {
    const picker = q('#today-picker');
    const cityBtn = q('#today-city');
    placePicker(q('#today-place'), q('#today-results'), null);
    const closePicker = () => { picker.hidden = true; cityBtn.setAttribute('aria-expanded', 'false'); };
    cityBtn.addEventListener('click', () => {
      picker.hidden = !picker.hidden;
      cityBtn.setAttribute('aria-expanded', String(!picker.hidden));
      if (!picker.hidden) { q('#today-place').value = ''; q('#today-place').focus(); }
    });
    q('#today-place').addEventListener('keydown', (e) => { if (e.key === 'Escape') closePicker(); });
    q('#today-place').addEventListener('place:chosen', (e) => {
      const p = e.detail;
      todayPlace = { latitude: p.latitude, longitude: p.longitude, timezone: p.timezone, label: p.label };
      try { localStorage.setItem(TODAY_KEY, JSON.stringify(todayPlace)); } catch { /* private mode */ }
      closePicker();
      loadToday();
    });
    // The strip is the way in to the full Panchang, for the same city.
    q('#today-open').addEventListener('click', () => {
      showStage('stage-panchang');
      paPlace = todayPlace;
      q('#pa-place').value = todayPlace.label;
      q('#pa-chosen').hidden = true;
      q('#pa-date').value = '';            // the strip is about today
      loadPanchang();
    });
    loadToday();
  }

  /* ---------------------------------------------------------------- muhurat */
  const muPick = placePicker(q('#mu-place'), q('#mu-results'), q('#mu-chosen'));
  let muPlace = null;

  function initMuhuratDates() {
    const today = todayIn((muPlace || muPick())?.timezone);
    if (!q('#mu-from').value) q('#mu-from').value = today;
    if (!q('#mu-to').value) q('#mu-to').value = addDaysIso(today, 30);
  }

  q('#mu-place')?.addEventListener('place:chosen', (e) => {
    muPlace = e.detail;
  });

  q('#muhurat-go')?.addEventListener('click', async () => {
    const btn = q('#muhurat-go');
    const err = q('#muhurat-error');
    err.hidden = true;

    const event = q('#mu-event').value;
    const fromDate = q('#mu-from').value;
    const toDate = q('#mu-to').value;
    if (!fromDate || !toDate) {
      err.textContent = 'Please choose both from and to dates.';
      err.hidden = false;
      return;
    }

    const place = muPlace || muPick() ||
      { latitude: 28.6139, longitude: 77.2090, timezone: 'Asia/Kolkata', label: 'New Delhi, India' };

    const lang = (typeof state !== 'undefined' && state.lang) ? state.lang : 'en';
    const params = new URLSearchParams({
      event,
      from_date: fromDate,
      to_date: toDate,
      latitude: place.latitude,
      longitude: place.longitude,
      timezone: place.timezone || '',
      language: lang,
    });

    btn.disabled = true; btn.classList.add('busy');
    try {
      const res = await fetch(`/api/muhurat?${params}`);
      const data = await readJson(res);
      if (!res.ok) throw new Error(data.detail || 'Could not calculate muhurat.');
      renderMuhurat(data, place.label);
    } catch (ex) {
      err.textContent = ex.message; err.hidden = false;
    } finally {
      btn.disabled = false; btn.classList.remove('busy');
    }
  });

  function renderMuhurat(data, placeLabel) {
    const days = data.days || [];
    if (!days.length) {
      q('#muhurat-result').innerHTML = '<div class="card"><p>No dates found for this range.</p></div>';
      q('#muhurat-result').hidden = false;
      return;
    }

    const rows = days.map((d) => `
      <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
        <td style="padding: 10px 8px; white-space: nowrap;">
          <b>${esc(d.date)}</b><br/>
          <span style="font-size: 12px; color: var(--ink-dim);">${esc(d.vara)}</span>
        </td>
        <td style="padding: 10px 8px;">
          <span class="badge ${esc(d.badge)}" style="font-size: 12px;">${esc(d.verdict)}</span>
        </td>
        <td style="padding: 10px 8px; font-size: 12.5px;">
          <b>${esc(d.tithi)}</b> · ${esc(d.nakshatra)}<br/>
          <span style="font-size: 12px; color: var(--ink-dim);">${esc(d.yoga)}</span>
        </td>
        <td style="padding: 10px 8px; font-size: 12px; color: var(--gold);">
          ${d.abhijit ? `Abhijit: ${esc(d.abhijit)}` : '—'}
        </td>
        <td style="padding: 10px 8px; font-size: 12px;">
          ${(d.reasons || []).map(r => `<span style="display:block;">• ${esc(r)}</span>`).join('') || '—'}
        </td>
      </tr>
    `).join('');

    q('#muhurat-result').innerHTML = `
      <div class="card" style="margin-top: 20px; overflow-x: auto;">
        <h3 style="margin-bottom: 12px; color: var(--gold);">
          ${esc(tr('muhuratResultsTitle', 'Auspicious Dates Summary'))} — ${esc(placeLabel)}
        </h3>
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
          <thead>
            <tr style="border-bottom: 1px solid var(--line); color: var(--ink-dim);">
              <th style="padding: 8px;">Date / Day</th>
              <th style="padding: 8px;">Verdict</th>
              <th style="padding: 8px;">Tithi &amp; Nakshatra</th>
              <th style="padding: 8px;">Abhijit</th>
              <th style="padding: 8px;">Evaluation / Reasons</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
    q('#muhurat-result').hidden = false;
    q('#muhurat-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // --------------------------------------------------------------------------
  // Choghadiya
  // --------------------------------------------------------------------------

  const choPlaceInput = q('#cho-place');
  const choResults = q('#cho-results');
  const choChosen = q('#cho-chosen');

  // These three lines used to call show(), suggest() and window.APP_STATE, none of
  // which exist: the home-page card did nothing (ReferenceError), typing a place
  // threw on every keystroke, and Hindi users always got English. Found by the
  // browser audit in tests/e2e/test_mobile_screens.py.
  const getChoPlace = choPlaceInput ? placePicker(choPlaceInput, choResults, choChosen) : () => null;

  q('#open-choghadiya')?.addEventListener('click', () => {
    showStage('stage-choghadiya');
    if (!q('#cho-date').value) {
      q('#cho-date').value = todayIn(getChoPlace()?.timezone);
    }
  });

  q('#choghadiya-go')?.addEventListener('click', async () => {
    const err = q('#choghadiya-error');
    err.hidden = true; err.textContent = '';
    const btn = q('#choghadiya-go');
    const place = getChoPlace() || {
      label: 'New Delhi, India',
      latitude: 28.6139,
      longitude: 77.2090,
      timezone: 'Asia/Kolkata',
    };
    const targetDate = q('#cho-date').value || todayIn(place.timezone);
    const lang = (typeof state !== 'undefined' && state.lang) ? state.lang : 'en';

    const params = new URLSearchParams({
      date: targetDate,
      latitude: place.latitude,
      longitude: place.longitude,
      timezone: place.timezone || '',
      language: lang,
    });

    btn.disabled = true; btn.classList.add('busy');
    try {
      const res = await fetch(`/api/choghadiya?${params}`);
      const data = await readJson(res);
      if (!res.ok) throw new Error(data.detail || 'Could not calculate Choghadiya.');
      renderChoghadiya(data, place.label, lang);
    } catch (ex) {
      err.textContent = ex.message; err.hidden = false;
    } finally {
      btn.disabled = false; btn.classList.remove('busy');
    }
  });

  function renderChoghadiya(data, placeLabel, lang) {
    const isHi = lang === 'hi';
    const act = data.active_slot;
    const badgeColor = {
      auspicious: 'var(--green)',
      neutral: 'var(--gold)',
      inauspicious: 'var(--rose)',
    };

    function renderSlots(slots) {
      return slots.map(s => {
        const bg = s.is_current ? 'background: rgba(212, 175, 55, 0.15); border-left: 3px solid var(--gold);' : '';
        const dotColor = badgeColor[s.quality] || '#999';
        return `
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.04); ${bg}">
            <td style="padding: 10px 8px; font-weight: bold;">
              ${esc(s.start)} – ${esc(s.end)}
              ${s.is_current ? `<span style="margin-left: 6px; font-size: 12px; color: var(--gold); border: 1px solid var(--gold); border-radius: 4px; padding: 1px 4px;">${isHi ? 'वर्तमान' : 'NOW'}</span>` : ''}
            </td>
            <td style="padding: 10px 8px;">
              <b>${esc(s.name_label)}</b><br/>
              <span style="font-size: 12px; color: var(--ink-dim);">${isHi ? 'स्वामी: ' : 'Lord: '}${esc(s.ruler_label)}</span>
            </td>
            <td style="padding: 10px 8px;">
              <span style="display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; color: ${dotColor};">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: ${dotColor};"></span>
                ${esc(s.quality_label)}
              </span>
            </td>
            <td style="padding: 10px 8px; font-size: 12px; color: var(--ink-dim);">
              ${esc(s.description)}
            </td>
          </tr>
        `;
      }).join('');
    }

    q('#choghadiya-result').innerHTML = `
      <div class="card" style="margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 16px;">
          <div>
            <h3 style="color: var(--gold); margin: 0;">
              ${isHi ? 'दैनिक चौघड़िया चक्र' : 'Choghadiya Muhurta Schedule'} — ${esc(placeLabel)}
            </h3>
            <p style="margin: 4px 0 0 0; font-size: 12.5px; color: var(--ink-dim);">
              ${esc(isHi ? data.weekday_hi : data.weekday)} · ${esc(data.date)} · ${isHi ? 'सूर्योदय' : 'Sunrise'}: ${esc(data.sunrise)} · ${isHi ? 'सूर्यास्त' : 'Sunset'}: ${esc(data.sunset)}
            </p>
          </div>
          ${act ? `
            <div style="padding: 8px 14px; border-radius: 8px; background: rgba(212, 175, 55, 0.1); border: 1px solid var(--gold); text-align: right;">
              <span style="font-size: 12px; color: var(--gold); text-transform: uppercase;">${isHi ? 'वर्तमान सक्रिय मुहूर्त' : 'Active Muhurta Now'}</span>
              <div style="font-size: 16px; font-weight: bold; color: var(--ink);">
                ${esc(act.name_label)} (${esc(act.start)} – ${esc(act.end)})
              </div>
            </div>
          ` : ''}
        </div>

        <h4 style="margin: 18px 0 8px 0; color: var(--gold); font-size: 14px; border-bottom: 1px solid var(--line); padding-bottom: 4px;">
          ☀️ ${isHi ? 'दिन का चौघड़िया (सूर्योदय से सूर्यास्त)' : 'Day Choghadiya (Sunrise to Sunset)'}
        </h4>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; margin-bottom: 16px;">
            <thead>
              <tr style="border-bottom: 1px solid var(--line); color: var(--ink-dim);">
                <th style="padding: 6px 8px;">${isHi ? 'समय' : 'Time'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'चौघड़िया / स्वामी' : 'Muhurta / Lord'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'प्रकृति' : 'Nature'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'उपयुक्त कार्य व परामर्श' : 'Recommended Activities'}</th>
              </tr>
            </thead>
            <tbody>
              ${renderSlots(data.day_slots)}
            </tbody>
          </table>
        </div>

        <h4 style="margin: 18px 0 8px 0; color: var(--gold); font-size: 14px; border-bottom: 1px solid var(--line); padding-bottom: 4px;">
          🌙 ${isHi ? 'रात्रि का चौघड़िया (सूर्यास्त से सूर्योदय)' : 'Night Choghadiya (Sunset to Next Sunrise)'}
        </h4>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
            <thead>
              <tr style="border-bottom: 1px solid var(--line); color: var(--ink-dim);">
                <th style="padding: 6px 8px;">${isHi ? 'समय' : 'Time'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'चौघड़िया / स्वामी' : 'Muhurta / Lord'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'प्रकृति' : 'Nature'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'उपयुक्त कार्य व परामर्श' : 'Recommended Activities'}</th>
              </tr>
            </thead>
            <tbody>
              ${renderSlots(data.night_slots)}
            </tbody>
          </table>
        </div>
      </div>
    `;
    q('#choghadiya-result').hidden = false;
    q('#choghadiya-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ------------------------------------------------------------- deep links */
  // The server-rendered /panchang, /rahu-kaal, /choghadiya and /kundali-milan
  // pages (app/seo_pages.py) link here as /?open=<tool>. Clicking the home card
  // reuses exactly what a visitor's own tap would do, then the parameter is
  // dropped so a reload or a shared link of the address bar starts clean.
  const DEEP_LINKS = {
    panchang: '#open-panchang', 'rahu-kaal': '#open-panchang',
    choghadiya: '#open-choghadiya', muhurat: '#open-muhurat',
    milan: '#open-milan', 'kundali-milan': '#open-milan',
  };
  const deepParams = new URLSearchParams(location.search);
  const deepTarget = DEEP_LINKS[deepParams.get('open')];
  if (deepTarget) {
    q(deepTarget)?.click();
    deepParams.delete('open');
    history.replaceState({}, '', location.pathname +
      (deepParams.toString() ? `?${deepParams}` : ''));
  }
})();
