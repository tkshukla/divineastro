/* ============================================================
   GrahDrishti — accounts, credits and checkout.
   Kept separate from app.js so the money path can be read on its own.
   ============================================================ */

const acct = {
  user: null,
  products: [],
  freeQuestions: 10,
  live: false,
  keyId: "",
  pendingQuestion: null,   // re-fired after a successful purchase
};

const A_I18N = {
  en: {
    signIn: "Sign in", signOut: "Sign out",
    signInTitle: "Sign in to Divine Astro",
    signInSub: "One tap. No password to remember, nothing to verify by SMS.",
    continueWith: "Continue with",
    noProviders: "Sign-in is not configured yet. Add OAuth credentials to enable it.",
    devLogin: "Developer sign-in",
    welcome: "Welcome. You have", freeQs: "free questions to start.",
    credits: "questions left", buyMore: "Buy more",
    adminPanel: "Admin panel",
    upiTitle: "Pay by UPI",
    upiSub: "Scan the code or pay to the ID below, then tell us the reference number. "
          + "Your questions are added once we've matched it against our bank statement — "
          + "usually within a few hours.",
    upiRef: "Quote this reference:", upiOpenApp: "Open a UPI app",
    upiUtr: "UPI reference / UTR number from your payment app",
    upiSubmit: "I've paid", upiFailed: "That reference was not accepted.",
    upiThanks: "Thank you. We'll confirm and add your questions shortly.",
    outTitle: "You've used all your questions",
    outSub: "Choose a pack to continue. Your charts and history stay saved.",
    perQ: "per question", buy: "Buy", popular: "Most popular",
    kundaliTitle: "Hand-written Kundali",
    kundaliSub: "Written by hand by our astrologer and delivered as a scanned PDF.",
    singleQTitle: "Single-Topic Reports",
    singleQSub: "A focused PDF on one area of your chart — instant, no waiting.",
    singleQNeedChart: "Open or save a chart first, then come back here to buy a report for it.",
    reportReadyTitle: "Your report is ready",
    reportDownload: "Download PDF",
    pages: "pages", plusQs: "questions included",
    processing: "Opening payment…", paid: "Payment received —", added: "questions added.",
    payFailed: "Payment could not be completed.",
    testMode: "Test mode — no real payment will be taken.",
    history: "My questions", orders: "My orders", close: "Close",
    dev: "Development mode — your code is",
    couponLabel: "Have a coupon?", couponPlaceholder: "Coupon code",
    couponApply: "Apply", couponRemove: "Remove", couponChecking: "Checking…",
    couponInvalid: "That coupon cannot be used.",
    couponNotHere: "Not valid for this item",
    bonusQs: "bonus questions",
    coupons: "Coupons", couponsTitle: "Coupon administration",
    couponsSub: "Codes, limits and usage. Changes take effect immediately.",
    newCoupon: "New coupon", cCode: "Code", cKind: "Type", cValue: "Value",
    cDesc: "Description", cApplies: "Applies to", cMinOrder: "Min order (₹)",
    cMaxOff: "Max discount (₹)", cTotalLimit: "Total limit",
    cPerUser: "Per user", cExpires: "Expires (YYYY-MM-DD)",
    cCreate: "Create", cSave: "Save", cActivate: "Activate",
    cDeactivate: "Deactivate", cDelete: "Delete", cUsed: "used",
    cUnlimited: "unlimited", cActive: "Active", cInactive: "Inactive",
    cNone: "No coupons yet.", cBlank: "blank = unlimited",
    kPercent: "Percent off", kFlat: "Flat ₹ off", kExtra: "Bonus credits",
    cConfirmDelete: "Delete this coupon? If it has been used it is only deactivated.",
  },
  hi: {
    signIn: "साइन इन", signOut: "साइन आउट",
    signInTitle: "Divine Astro में साइन इन करें",
    signInSub: "एक क्लिक। न पासवर्ड, न SMS सत्यापन।",
    continueWith: "जारी रखें",
    noProviders: "साइन-इन अभी कॉन्फ़िगर नहीं है।",
    devLogin: "डेवलपर साइन-इन",
    welcome: "स्वागत है। आपके पास", freeQs: "निःशुल्क प्रश्न हैं।",
    credits: "प्रश्न शेष", buyMore: "और खरीदें",
    adminPanel: "एडमिन पैनल",
    upiTitle: "UPI से भुगतान करें",
    upiSub: "क्यूआर स्कैन करें या नीचे दी गई UPI आईडी पर भुगतान करें, फिर हमें रेफ़रेंस नंबर बताएं। "
          + "बैंक स्टेटमेंट से मिलान होते ही आपके प्रश्न जुड़ जाएंगे — आमतौर पर कुछ घंटों में।",
    upiRef: "यह रेफ़रेंस लिखें:", upiOpenApp: "UPI ऐप खोलें",
    upiUtr: "आपके भुगतान ऐप का UPI रेफ़रेंस / UTR नंबर",
    upiSubmit: "मैंने भुगतान कर दिया", upiFailed: "यह रेफ़रेंस स्वीकार नहीं हुआ।",
    upiThanks: "धन्यवाद। पुष्टि के बाद आपके प्रश्न शीघ्र जोड़ दिए जाएंगे।",
    outTitle: "आपके सभी प्रश्न समाप्त हो गए",
    outSub: "जारी रखने के लिए पैक चुनें। आपकी कुंडली और इतिहास सुरक्षित रहेंगे।",
    perQ: "प्रति प्रश्न", buy: "खरीदें", popular: "सर्वाधिक लोकप्रिय",
    kundaliTitle: "हस्तलिखित कुंडली",
    kundaliSub: "हमारे ज्योतिषी द्वारा हाथ से लिखी, स्कैन की गई PDF के रूप में।",
    singleQTitle: "एकल-विषय रिपोर्ट",
    singleQSub: "आपकी कुंडली के एक क्षेत्र पर केंद्रित PDF — तुरंत, बिना प्रतीक्षा के।",
    singleQNeedChart: "पहले कोई कुंडली खोलें या सहेजें, फिर उसके लिए रिपोर्ट खरीदने यहाँ लौटें।",
    reportReadyTitle: "आपकी रिपोर्ट तैयार है",
    reportDownload: "PDF डाउनलोड करें",
    pages: "पृष्ठ", plusQs: "प्रश्न शामिल",
    processing: "भुगतान खोला जा रहा है…", paid: "भुगतान प्राप्त —", added: "प्रश्न जोड़े गए।",
    payFailed: "भुगतान पूरा नहीं हो सका।",
    testMode: "परीक्षण मोड — कोई वास्तविक भुगतान नहीं लिया जाएगा।",
    history: "मेरे प्रश्न", orders: "मेरे ऑर्डर", close: "बंद करें",
    dev: "डेवलपमेंट मोड — आपका कोड है",
    couponLabel: "कूपन है?", couponPlaceholder: "कूपन कोड",
    couponApply: "लागू करें", couponRemove: "हटाएँ", couponChecking: "जाँच हो रही है…",
    couponInvalid: "यह कूपन उपयोग नहीं किया जा सकता।",
    couponNotHere: "इस वस्तु पर मान्य नहीं",
    bonusQs: "बोनस प्रश्न",
    coupons: "कूपन", couponsTitle: "कूपन प्रबंधन",
    couponsSub: "कोड, सीमाएँ और उपयोग। परिवर्तन तुरंत लागू होते हैं।",
    newCoupon: "नया कूपन", cCode: "कोड", cKind: "प्रकार", cValue: "मान",
    cDesc: "विवरण", cApplies: "किस पर लागू", cMinOrder: "न्यूनतम ऑर्डर (₹)",
    cMaxOff: "अधिकतम छूट (₹)", cTotalLimit: "कुल सीमा",
    cPerUser: "प्रति उपयोगकर्ता", cExpires: "समाप्ति (YYYY-MM-DD)",
    cCreate: "बनाएँ", cSave: "सहेजें", cActivate: "सक्रिय करें",
    cDeactivate: "निष्क्रिय करें", cDelete: "हटाएँ", cUsed: "उपयोग",
    cUnlimited: "असीमित", cActive: "सक्रिय", cInactive: "निष्क्रिय",
    cNone: "अभी कोई कूपन नहीं।", cBlank: "खाली = असीमित",
    kPercent: "प्रतिशत छूट", kFlat: "निश्चित ₹ छूट", kExtra: "बोनस क्रेडिट",
    cConfirmDelete: "यह कूपन हटाएँ? यदि इसका उपयोग हुआ है तो केवल निष्क्रिय होगा।",
  },
};

const at = (k) => (A_I18N[state.lang] || A_I18N.en)[k] ?? A_I18N.en[k] ?? k;

/* ---------- generic modal ---------- */
function modal(html, { dismissable = true } = {}) {
  document.querySelector(".modal-backdrop")?.remove();
  const back = document.createElement("div");
  back.className = "modal-backdrop";
  back.innerHTML = `<div class="modal" role="dialog" aria-modal="true">
    ${dismissable ? '<button class="modal-x" aria-label="Close">&times;</button>' : ""}
    <div class="modal-body">${html}</div></div>`;
  document.body.append(back);
  if (dismissable) {
    back.querySelector(".modal-x").onclick = () => back.remove();
    back.onclick = (e) => { if (e.target === back) back.remove(); };
  }
  return back;
}
const closeModal = () => document.querySelector(".modal-backdrop")?.remove();

/* ---------- session ---------- */
async function loadAccount() {
  try {
    const data = await (await fetch("/api/me")).json();
    acct.user = data.user;
    acct.freeQuestions = data.free_questions ?? acct.freeQuestions;
  } catch { acct.user = null; }

  try {
    const p = await (await fetch("/api/products")).json();
    acct.products = p.products || [];
    acct.payment = p.payment || { gateway: "test", live: false };
    acct.live = !!acct.payment.live;
    acct.astrologer = p.astrologer || "";
    acct.turnaround = p.turnaround_days || 10;
  } catch { /* catalogue is optional for rendering the app */ }

  try {
    const a = await (await fetch("/api/auth/providers")).json();
    acct.authProviders = a.providers || [];
    acct.devLogin = !!a.dev_login;
  } catch { acct.authProviders = []; }

  renderAccountBar();
  // Rescue a chart cast before signing in, THEN list. Order matters: claiming
  // calls loadSavedCharts itself on success, so the panel shows it immediately
  // rather than only on the visit after.
  claimPendingBirth().finally(loadSavedCharts);

  // A fresh OAuth round-trip lands back here with ?welcome=1
  const params = new URLSearchParams(location.search);
  if (params.has("welcome")) {
    if (params.get("welcome") === "1" && acct.user) {
      toast(`${at("welcome")} ${acct.user.credits} ${at("freeQs")}`);
    }
    params.delete("welcome");
    history.replaceState({}, "", location.pathname +
      (params.toString() ? `?${params}` : ""));
  }

  await resumeHostedCheckout();
  return acct.user;
}

/* Gateways that take the customer away to their own page (Instamojo) send the
   browser back with the payment reference in the query string. The order id
   itself is not in that redirect, so it is parked in sessionStorage on the way
   out. Nothing here is trusted: the server re-checks the payment with the
   gateway before a single credit moves. */
async function resumeHostedCheckout() {
  const params = new URLSearchParams(location.search);
  const paymentId = params.get("payment_id");
  const requestId = params.get("payment_request_id");
  if (!paymentId || !requestId) return;

  const orderId = Number(sessionStorage.getItem("da_pending_order") || 0);
  sessionStorage.removeItem("da_pending_order");

  ["payment_id", "payment_request_id", "payment_status"].forEach((k) => params.delete(k));
  history.replaceState({}, "", location.pathname +
    (params.toString() ? `?${params}` : ""));

  try {
    await confirmPayment(orderId || null, {
      payment_id: paymentId, payment_request_id: requestId,
    });
  } catch (ex) {
    toast(ex.message || "We could not confirm that payment yet.");
  }
}

function renderAccountBar() {
  const bar = document.querySelector("#account-bar");
  if (!bar) return;
  if (!acct.user) {
    bar.innerHTML = `<button class="ghost-btn" id="btn-signin">${escapeHtml(at("signIn"))}</button>`;
    bar.querySelector("#btn-signin").onclick = () => openSignIn();
    return;
  }
  const c = acct.user.credits;
  bar.innerHTML = `
    <button class="credit-pill${c <= 2 ? " low" : ""}" id="btn-credits">
      <b>${c}</b> ${escapeHtml(at("credits"))}
    </button>
    <button class="ghost-btn" id="btn-buy">${escapeHtml(at("buyMore"))}</button>
    <div class="acct-menu">
      <!-- The caret matters: without it this reads as a label, and customers
           could not find Sign out or the admin panel hidden behind it. -->
      <button class="ghost-btn has-menu" id="btn-acct" aria-haspopup="menu" aria-expanded="false">${escapeHtml(
        acct.user.name || (acct.user.email || "").split("@")[0] || "Account")}<span class="caret">&#9662;</span></button>
      <div class="acct-drop" hidden>
        <button data-act="history">${escapeHtml(at("history"))}</button>
        <button data-act="orders">${escapeHtml(at("orders"))}</button>
        ${acct.user.is_admin
          ? `<button data-act="coupons">${escapeHtml(at("coupons"))}</button>
             <a class="drop-link" href="/admin">${escapeHtml(at("adminPanel"))}</a>` : ""}
        <button data-act="logout">${escapeHtml(at("signOut"))}</button>
      </div>
    </div>`;
  bar.querySelector("#btn-credits").onclick = () => openStore();
  bar.querySelector("#btn-buy").onclick = () => openStore();
  const drop = bar.querySelector(".acct-drop");
  const acctBtn = bar.querySelector("#btn-acct");
  acctBtn.onclick = () => {
    drop.hidden = !drop.hidden;
    acctBtn.setAttribute("aria-expanded", String(!drop.hidden));
  };
  // Clicking anywhere else closes it, as any menu should.
  document.addEventListener("click", (e) => {
    if (!bar.contains(e.target) && !drop.hidden) {
      drop.hidden = true;
      acctBtn.setAttribute("aria-expanded", "false");
    }
  });
  drop.querySelectorAll("button").forEach((b) => {
    b.onclick = async () => {
      drop.hidden = true;
      if (b.dataset.act === "logout") {
        await fetch("/api/auth/logout", { method: "POST" });
        acct.user = null;
        renderAccountBar();
        loadSavedCharts();
        // Signing out from the reading screen must not leave someone looking at
        // a chart they no longer have an account for. Always land on home.
        closeModal();
        if (typeof showStage === "function") showStage("stage-home");
      } else if (b.dataset.act === "history") { openHistory(); }
      else if (b.dataset.act === "coupons") { openCouponAdmin(); }
      else { openOrders(); }
    };
  });

}
/* The old measureAccountBar() lived here. It published the bar's width so the
   reading header could pad around a floating overlay. The bar is now inside
   .site-header in normal flow, so there is nothing to measure and nothing to
   dodge — the whole mechanism, and the class of bugs it patched, is gone. */

/* ---------- sign in (social) ---------- */
const PROVIDER_MARK = {
  google: `<svg viewBox="0 0 48 48" width="18" height="18"><path fill="#4285F4" d="M45 24c0-1.6-.1-2.7-.4-3.9H24v7.1h12c-.2 1.9-1.5 4.7-4.4 6.6l6.7 5.2C42.2 35.3 45 30.1 45 24z"/><path fill="#34A853" d="M24 46c5.9 0 10.9-2 14.5-5.3l-6.9-5.4c-1.9 1.3-4.4 2.2-7.6 2.2-5.8 0-10.7-3.8-12.5-9.1l-7.1 5.5C8.1 41 15.5 46 24 46z"/><path fill="#FBBC05" d="M11.5 28.4c-.5-1.4-.7-2.9-.7-4.4s.3-3 .7-4.4l-7.1-5.5C2.9 17 2 20.4 2 24s.9 7 2.4 9.9l7.1-5.5z"/><path fill="#EA4335" d="M24 10.5c4.1 0 6.9 1.8 8.5 3.2l6.2-6C34.9 4.2 29.9 2 24 2 15.5 2 8.1 7 4.4 14.1l7.1 5.5C13.3 14.3 18.2 10.5 24 10.5z"/></svg>`,
  microsoft: `<svg viewBox="0 0 23 23" width="17" height="17"><path fill="#f25022" d="M1 1h10v10H1z"/><path fill="#7fba00" d="M12 1h10v10H12z"/><path fill="#00a4ef" d="M1 12h10v10H1z"/><path fill="#ffb900" d="M12 12h10v10H12z"/></svg>`,
  apple: `<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M16.4 12.8c0-2.6 2.1-3.8 2.2-3.9-1.2-1.8-3.1-2-3.8-2-1.6-.2-3.1.9-3.9.9s-2-.9-3.4-.9c-1.7 0-3.3 1-4.2 2.6-1.8 3.1-.5 7.7 1.3 10.2.9 1.2 1.9 2.6 3.3 2.6 1.3-.1 1.8-.9 3.4-.9s2 .9 3.4.8c1.4 0 2.3-1.2 3.2-2.5 1-1.4 1.4-2.8 1.4-2.9-.1 0-2.7-1-2.7-4zM13.9 4.5c.7-.9 1.2-2.1 1.1-3.3-1.1 0-2.4.7-3.1 1.6-.7.8-1.3 2-1.1 3.2 1.2.1 2.4-.6 3.1-1.5z"/></svg>`,
  dev: `<span style="font-size:15px">🛠</span>`,
};

function openSignIn(onDone) {
  acct.afterLogin = onDone || null;
  const provs = acct.authProviders || [];
  const buttons = provs.map((p) => `
    <button class="oauth-btn" data-provider="${escapeHtml(p.key)}">
      ${PROVIDER_MARK[p.key] || ""}
      <span>${escapeHtml(at("continueWith"))} ${escapeHtml(p.label)}</span>
    </button>`).join("");

  const back = modal(`
    <h2 class="modal-title">${escapeHtml(at("signInTitle"))}</h2>
    <p class="modal-sub">${escapeHtml(at("signInSub"))}</p>
    <div class="oauth-list">
      ${buttons || `<p class="test-banner">${escapeHtml(at("noProviders"))}</p>`}
      ${acct.devLogin ? `<button class="oauth-btn dev" data-provider="dev">
          ${PROVIDER_MARK.dev}<span>${escapeHtml(at("devLogin"))}</span></button>` : ""}
    </div>
    <p class="modal-error" hidden></p>
    <p class="legal-line">By continuing you accept our
      <a href="/terms">Terms</a> and <a href="/privacy">Privacy Policy</a>.</p>`);

  back.querySelectorAll(".oauth-btn").forEach((b) => {
    b.onclick = async () => {
      const provider = b.dataset.provider;
      if (provider === "dev") {
        const email = prompt("Developer sign-in — email:", "dev@example.com");
        if (!email) return;
        const res = await fetch("/api/auth/dev", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        });
        const data = await res.json();
        if (!res.ok) {
          const err = back.querySelector(".modal-error");
          err.textContent = data.detail || "Sign-in failed."; err.hidden = false;
          return;
        }
        acct.user = data.user;
        renderAccountBar();
        loadSavedCharts();
        closeModal();
        if (data.created) toast(`${at("welcome")} ${data.user.credits} ${at("freeQs")}`);
        onDone?.(data.user);
        return;
      }
      // Full-page redirect: OAuth cannot complete inside fetch().
      const next = encodeURIComponent(location.pathname + location.search);
      location.href = `/api/auth/${provider}/start?next=${next}`;
    };
  });
}

/* ---------- store / paywall ---------- */

/* Money crosses the wire in paise, exactly as the server holds it. Rupees are
   produced only at the moment of display, so nothing rounds on the way in. */
const rupees = (paise) => (paise / 100).toFixed(2).replace(/\.00$/, "");

/* The coupon the customer has applied in this store session, plus the priced
   preview for every sku it covers. Cleared whenever the store is reopened. */
acct.coupon = null;

function couponFor(sku) {
  const r = acct.coupon?.results?.[sku];
  return r && r.valid ? r : null;
}

function packCard(p) {
  const hi = state.lang === "hi";
  const cp = couponFor(p.sku);
  const applied = !!acct.coupon;

  let price = `<div class="pack-price">₹${p.rupees}</div>`;
  let unit = p.per_question
    ? `<div class="pack-unit">₹${p.per_question} ${escapeHtml(at("perQ"))}</div>` : "";
  let label = `${escapeHtml(at("buy"))} ₹${p.rupees}`;

  if (cp && cp.discount > 0) {
    price = `<div class="pack-price">
      <s style="opacity:.45;font-size:.6em">₹${p.rupees}</s> ₹${rupees(cp.final)}</div>`;
    unit = `<div class="pack-unit" style="color:var(--green)">
      −₹${rupees(cp.discount)} ${escapeHtml(acct.coupon.code)}</div>`;
    label = `${escapeHtml(at("buy"))} ₹${rupees(cp.final)}`;
  } else if (cp && cp.bonus_credits > 0) {
    unit = `<div class="pack-unit" style="color:var(--green)">
      +${cp.bonus_credits} ${escapeHtml(at("bonusQs"))} · ${escapeHtml(acct.coupon.code)}</div>`;
  } else if (applied) {
    unit = `<div class="pack-unit">${escapeHtml(at("couponNotHere"))}</div>`;
  }

  return `<div class="pack${p.highlight ? " featured" : ""}">
    ${p.highlight ? `<span class="pack-flag">${escapeHtml(at("popular"))}</span>` : ""}
    <h4>${escapeHtml(hi ? p.title_hi : p.title)}</h4>
    ${price}
    ${unit}
    <p class="pack-blurb">${escapeHtml(hi ? p.blurb_hi : p.blurb)}</p>
    <button class="primary buy-btn" data-sku="${p.sku}">${label}</button>
  </div>`;
}

function openStore(outOfCredits = false) {
  if (!acct.user) return openSignIn(() => openStore(outOfCredits));
  acct.coupon = null;
  const packs = acct.products.filter((p) => p.kind === "questions");
  const kundalis = acct.products.filter((p) => p.kind === "kundali");
  const singleQ = acct.products.filter((p) => p.kind === "single_question");
  // A single-question report is scoped to one chart, so it needs a birth_id
  // — unlike question packs and kundali orders, which don't. Only offer it
  // once a saved chart is actually loaded (state.currentBirthId), same
  // birth-id-tracking the chat's own per-chart history filter relies on.
  const haveBirth = typeof state !== "undefined" && state.currentBirthId;

  const back = modal(`
    <h2 class="modal-title">${escapeHtml(outOfCredits ? at("outTitle") : at("buyMore"))}</h2>
    <p class="modal-sub">${escapeHtml(outOfCredits ? at("outSub") : "")}</p>
    ${acct.live ? "" : `<p class="test-banner">${escapeHtml(at("testMode"))}</p>`}
    <div class="packs" data-kind="questions">${packs.map(packCard).join("")}</div>
    <h3 class="store-h">${escapeHtml(at("kundaliTitle"))}</h3>
    <p class="modal-sub">${escapeHtml(at("kundaliSub"))}${
      acct.astrologer ? ` ${escapeHtml(acct.astrologer)} · ~${acct.turnaround} days.` : ""}</p>
    <div class="packs" data-kind="kundali">${kundalis.map(packCard).join("")}</div>
    ${singleQ.length ? `
    <h3 class="store-h">${escapeHtml(at("singleQTitle"))}</h3>
    <p class="modal-sub">${escapeHtml(at("singleQSub"))}</p>
    ${haveBirth
      ? `<div class="packs" data-kind="single_question">${singleQ.map(packCard).join("")}</div>`
      : `<p class="modal-sub">${escapeHtml(at("singleQNeedChart"))}</p>`}
    ` : ""}

    <h3 class="store-h">${escapeHtml(at("couponLabel"))}</h3>
    <div style="display:flex;gap:10px;align-items:center">
      <input id="coupon-code" type="text" autocomplete="off" spellcheck="false"
             style="flex:1;margin-bottom:0;text-transform:uppercase"
             placeholder="${escapeHtml(at("couponPlaceholder"))}">
      <button class="ghost-btn" id="coupon-apply">${escapeHtml(at("couponApply"))}</button>
      <button class="ghost-btn" id="coupon-clear" hidden>${escapeHtml(at("couponRemove"))}</button>
    </div>
    <p class="coupon-msg modal-sub" style="margin:10px 0 0" hidden></p>
    <p class="modal-error" hidden></p>`);

  const input = back.querySelector("#coupon-code");
  const applyBtn = back.querySelector("#coupon-apply");
  const clearBtn = back.querySelector("#coupon-clear");
  const msg = back.querySelector(".coupon-msg");

  const repaint = () => {
    back.querySelector('.packs[data-kind="questions"]').innerHTML =
      packs.map(packCard).join("");
    back.querySelector('.packs[data-kind="kundali"]').innerHTML =
      kundalis.map(packCard).join("");
    back.querySelectorAll(".buy-btn").forEach((b) => {
      b.onclick = () => startCheckout(b.dataset.sku, back);
    });
  };

  const setMsg = (text, bad) => {
    msg.textContent = text;
    msg.className = bad ? "coupon-msg modal-error" : "coupon-msg modal-sub";
    msg.style.margin = "10px 0 0";
    msg.hidden = !text;
  };

  async function applyCoupon() {
    const code = input.value.trim();
    if (!code) return;
    applyBtn.disabled = true;
    setMsg(at("couponChecking"), false);

    // Priced per sku, because a coupon may cover only one product family.
    const skus = [...packs, ...kundalis].map((p) => p.sku);
    const results = {};
    await Promise.all(skus.map(async (sku) => {
      try {
        const res = await fetch("/api/coupons/preview", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, sku }),
        });
        if (res.ok) results[sku] = await res.json();
      } catch { /* one sku failing must not sink the rest */ }
    }));
    applyBtn.disabled = false;

    const good = Object.values(results).filter((r) => r.valid);
    if (!good.length) {
      acct.coupon = null;
      clearBtn.hidden = true;
      repaint();
      const first = Object.values(results)[0];
      setMsg(first?.message || at("couponInvalid"), true);
      return;
    }
    acct.coupon = { code: good[0].code, results };
    clearBtn.hidden = false;
    repaint();
    setMsg(good[0].message, false);
  }

  applyBtn.onclick = applyCoupon;
  input.onkeydown = (e) => { if (e.key === "Enter") { e.preventDefault(); applyCoupon(); } };
  clearBtn.onclick = () => {
    acct.coupon = null;
    input.value = "";
    clearBtn.hidden = true;
    setMsg("", false);
    repaint();
  };

  repaint();
}

async function startCheckout(sku, back) {
  const err = back.querySelector(".modal-error");
  const buttons = back.querySelectorAll(".buy-btn");
  buttons.forEach((b) => { b.disabled = true; });
  err.hidden = true;

  // Only send the code for a sku it is actually valid on — the server
  // re-validates regardless and would reject the order outright.
  const body = { sku };
  if (couponFor(sku)) body.coupon_code = acct.coupon.code;
  const product = acct.products.find((p) => p.sku === sku);
  if (product?.kind === "single_question" && typeof state !== "undefined") {
    body.birth_id = state.currentBirthId;
  }

  try {
    const res = await fetch("/api/orders", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not create the order.");

    const c = data.checkout;
    if (c.mode === "test") {
      await confirmPayment(data.order.id, {});
    } else if (c.mode === "razorpay") {
      await openRazorpay(data.order.id, c);
    } else if (c.mode === "cashfree") {
      await openCashfree(data.order.id, c);
    } else if (c.mode === "paytm") {
      await openPaytm(data.order.id, c);
    } else if (c.mode === "instamojo") {
      // Hosted page: leave the site entirely. resumeHostedCheckout() picks the
      // thread back up when Instamojo redirects the customer home.
      sessionStorage.setItem("da_pending_order", String(data.order.id));
      location.assign(c.url);
      return;
    } else if (c.mode === "upi_manual") {
      openUpiInstructions(data.order.id, c, back);
    } else {
      throw new Error(`Unsupported payment mode '${c.mode}'.`);
    }
  } catch (ex) {
    err.textContent = ex.message; err.hidden = false;
    buttons.forEach((b) => { b.disabled = false; });
  }
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if ([...document.scripts].some((s) => s.src === src)) return resolve();
    const s = document.createElement("script");
    s.src = src;
    s.onload = resolve;
    s.onerror = () => reject(new Error("Could not load the payment page."));
    document.head.append(s);
  });
}

/* Each gateway's checkout script is fetched on demand, so a visitor who never
   opens the store never loads a third-party script. */
async function openRazorpay(orderId, c) {
  await loadScript("https://checkout.razorpay.com/v1/checkout.js");
  return new Promise((resolve) => {
    const rz = new window.Razorpay({
      key: c.key_id, amount: c.amount, currency: c.currency,
      name: "Divine Astro", order_id: c.order_id, prefill: c.prefill,
      theme: { color: "#f0c674" },
      handler: async (resp) => { await confirmPayment(orderId, resp); resolve(); },
      modal: { ondismiss: () => resolve() },
    });
    rz.on("payment.failed", () => toast(at("payFailed"), true));
    rz.open();
  });
}

async function openCashfree(orderId, c) {
  await loadScript("https://sdk.cashfree.com/js/v3/cashfree.js");
  const cf = window.Cashfree({ mode: c.sandbox ? "sandbox" : "production" });
  await cf.checkout({
    paymentSessionId: c.payment_session_id,
    redirectTarget: "_modal",
  });
  // Cashfree's return is unsigned, so this only asks the server to look —
  // the webhook is what actually grants the credits.
  await confirmPayment(orderId, { order_id: c.order_id });
}

/* Manual UPI. There is no gateway and no callback: the customer pays into the
   VPA, tells us the UTR, and a human matches it against the bank statement.
   Submitting the reference grants nothing — the admin panel does. */
function openUpiInstructions(orderId, c, back) {
  const body = back.querySelector(".modal") || back;
  body.innerHTML = `
    <button class="modal-x" aria-label="Close">&times;</button>
    <h3>${escapeHtml(at("upiTitle"))}</h3>
    <p class="modal-sub">${escapeHtml(at("upiSub"))}</p>
    <div class="upi-box">
      <img class="upi-qr" src="${c.qr}" alt="UPI QR code" />
      <div class="upi-meta">
        <div class="upi-amt">₹${(c.amount / 100).toLocaleString("en-IN")}</div>
        <div class="upi-vpa"><code>${escapeHtml(c.vpa)}</code></div>
        <div class="upi-ref">${escapeHtml(at("upiRef"))}
          <code>${escapeHtml(c.reference)}</code></div>
        <a class="upi-app" href="${escapeHtml(c.link)}">${escapeHtml(at("upiOpenApp"))}</a>
      </div>
    </div>
    <form class="upi-claim">
      <label for="utr">${escapeHtml(at("upiUtr"))}</label>
      <input id="utr" required placeholder="e.g. 412345678901" autocomplete="off" />
      <button type="submit" class="primary">${escapeHtml(at("upiSubmit"))}</button>
      <p class="modal-error" hidden></p>
    </form>`;

  body.querySelector(".modal-x").onclick = closeModal;
  const err = body.querySelector(".modal-error");

  body.querySelector(".upi-claim").onsubmit = async (ev) => {
    ev.preventDefault();
    err.hidden = true;
    const btn = ev.target.querySelector("button");
    btn.disabled = true;
    try {
      const res = await fetch("/api/orders/upi-claim", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId, utr: body.querySelector("#utr").value }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || at("upiFailed"));
      closeModal();
      toast(at("upiThanks"));
    } catch (ex) {
      err.textContent = ex.message; err.hidden = false;
      btn.disabled = false;
    }
  };
}

async function openPaytm(orderId, c) {
  // Paytm needs a server-side initiateTransaction call to mint a txnToken
  // before its JS checkout can open. Until that leg is wired to live
  // credentials, fail loudly rather than pretend the payment happened.
  throw new Error(
    "Paytm checkout needs live MID credentials to mint a transaction token. " +
    "Add PAYTM_MID and PAYTM_MERCHANT_KEY, or use Cashfree/Razorpay.");
}

async function confirmPayment(orderId, payload) {
  const res = await fetch("/api/orders/confirm", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order_id: orderId, payload }),
  });
  const data = await res.json();
  if (!res.ok) { toast(data.detail || at("payFailed"), true); return; }

  acct.user.credits = data.credits;
  renderAccountBar();
  closeModal();

  if (data.pending) {
    toast(data.message || "Payment is being confirmed…");
    // The webhook grants a moment later; poll briefly so the balance updates.
    for (let i = 0; i < 10; i++) {
      await new Promise((r) => setTimeout(r, 3000));
      const fresh = await (await fetch("/api/me")).json();
      if (fresh.user && fresh.user.credits !== data.credits) {
        acct.user = fresh.user; renderAccountBar();
        toast(`${at("paid")} ✓`); break;
      }
    }
    return;
  }

  // A single-question report grants no question credits — its "you're done"
  // moment is a direct download link, not the generic credits toast below.
  const paidProduct = acct.products.find((p) => p.sku === data.order?.sku);
  if (paidProduct?.kind === "single_question" && typeof state !== "undefined" && state.sessionId) {
    const link = `/api/pdf/single-question/${state.sessionId}` +
      `?sku=${encodeURIComponent(paidProduct.sku)}&birth_id=${encodeURIComponent(state.currentBirthId)}`;
    modal(`
      <h2 class="modal-title">${escapeHtml(at("reportReadyTitle"))}</h2>
      <p class="modal-sub">${escapeHtml(paidProduct.title)}</p>
      <a class="primary" style="display:block;text-align:center;margin-top:14px" href="${link}">
        ${escapeHtml(at("reportDownload"))}</a>`);
    return;
  }

  const added = data.order?.credits || 0;
  toast(`${at("paid")} ${added ? `${added} ${at("added")}` : "✓"}`);

  // If the customer hit the paywall mid-question, ask it for them now.
  if (acct.pendingQuestion && added) {
    const q = acct.pendingQuestion;
    acct.pendingQuestion = null;
    const box = document.querySelector("#q");
    if (box) { box.value = q; document.querySelector("#ask-form").requestSubmit(); }
  }
}

/* ---------- history & orders ---------- */
async function openHistory() {
  const { questions } = await (await fetch("/api/history")).json();
  modal(`<h2 class="modal-title">${escapeHtml(at("history"))}</h2>
    <div class="hist">${questions.length ? questions.map((q) => `
      <div class="hist-row">
        <div class="hist-q">${escapeHtml(q.question)}</div>
        <div class="hist-meta">${escapeHtml(q.asked_at)} · ${escapeHtml(q.verdict || q.topic)}</div>
      </div>`).join("") : "<p class='modal-sub'>—</p>"}</div>`);
}

async function openOrders() {
  const { orders } = await (await fetch("/api/orders")).json();
  modal(`<h2 class="modal-title">${escapeHtml(at("orders"))}</h2>
    <div class="hist">${orders.length ? orders.map((o) => `
      <div class="hist-row">
        <div class="hist-q">${escapeHtml(o.title)} — ₹${o.amount}</div>
        <div class="hist-meta">${escapeHtml(o.created_at)} · ${escapeHtml(o.status)}${
          o.fulfilment !== "not_applicable" ? " · " + escapeHtml(o.fulfilment) : ""}</div>
      </div>`).join("") : "<p class='modal-sub'>—</p>"}</div>`);
}

/* ---------- admin: coupons ----------
   Deliberately plain: a table of rows with inline controls, built from the
   same .modal / .hist-row / .ghost-btn vocabulary as everything else, so it
   needs no stylesheet of its own. */

const KIND_LABEL = () => ({
  percent: at("kPercent"), flat: at("kFlat"), extra_credits: at("kExtra"),
});

function couponSummary(c) {
  if (c.kind === "percent") {
    return `${c.value}%` + (c.max_discount_paise
      ? ` (max ₹${rupees(c.max_discount_paise)})` : "");
  }
  if (c.kind === "flat") return `₹${rupees(c.value)}`;
  return `+${c.value}`;
}

async function openCouponAdmin() {
  const back = modal(`
    <h2 class="modal-title">${escapeHtml(at("couponsTitle"))}</h2>
    <p class="modal-sub">${escapeHtml(at("couponsSub"))}</p>
    <div id="coupon-list" class="hist">…</div>
    <h3 class="store-h">${escapeHtml(at("newCoupon"))}</h3>
    <div class="row">
      <div class="field">
        <label for="nc-code">${escapeHtml(at("cCode"))}</label>
        <input id="nc-code" type="text" style="text-transform:uppercase" placeholder="DIWALI25">
      </div>
      <div class="field">
        <label for="nc-kind">${escapeHtml(at("cKind"))}</label>
        <select id="nc-kind" style="padding:10px">
          <option value="percent">${escapeHtml(at("kPercent"))}</option>
          <option value="flat">${escapeHtml(at("kFlat"))}</option>
          <option value="extra_credits">${escapeHtml(at("kExtra"))}</option>
        </select>
      </div>
    </div>
    <div class="row">
      <div class="field">
        <label for="nc-value">${escapeHtml(at("cValue"))}</label>
        <input id="nc-value" type="number" min="1" value="10">
      </div>
      <div class="field">
        <label for="nc-applies">${escapeHtml(at("cApplies"))}</label>
        <select id="nc-applies" style="padding:10px">
          <option value="all">all</option>
          <option value="questions">questions</option>
          <option value="kundali">kundali</option>
          ${(acct.products || []).map((p) =>
            `<option value="${escapeHtml(p.sku)}">${escapeHtml(p.sku)}</option>`).join("")}
        </select>
      </div>
    </div>
    <div class="row">
      <div class="field">
        <label for="nc-min">${escapeHtml(at("cMinOrder"))}</label>
        <input id="nc-min" type="number" min="0" value="0">
      </div>
      <div class="field">
        <label for="nc-max">${escapeHtml(at("cMaxOff"))}</label>
        <input id="nc-max" type="number" min="0" placeholder="${escapeHtml(at("cBlank"))}">
      </div>
    </div>
    <div class="row">
      <div class="field">
        <label for="nc-total">${escapeHtml(at("cTotalLimit"))}</label>
        <input id="nc-total" type="number" min="1" placeholder="${escapeHtml(at("cBlank"))}">
      </div>
      <div class="field">
        <label for="nc-user">${escapeHtml(at("cPerUser"))}</label>
        <input id="nc-user" type="number" min="0" value="1">
      </div>
    </div>
    <div class="row">
      <div class="field">
        <label for="nc-expires">${escapeHtml(at("cExpires"))}</label>
        <input id="nc-expires" type="text" placeholder="2026-12-31">
      </div>
      <div class="field">
        <label for="nc-desc">${escapeHtml(at("cDesc"))}</label>
        <input id="nc-desc" type="text">
      </div>
    </div>
    <button class="primary" id="nc-create">${escapeHtml(at("cCreate"))}</button>
    <p class="modal-error" hidden></p>`);

  const err = back.querySelector(".modal-error");
  const list = back.querySelector("#coupon-list");
  const fail = (message) => { err.textContent = message; err.hidden = false; };

  async function refresh() {
    const res = await fetch("/api/admin/coupons");
    if (!res.ok) { list.innerHTML = `<p class="modal-sub">${escapeHtml(at("couponInvalid"))}</p>`; return; }
    const { coupons } = await res.json();
    if (!coupons.length) {
      list.innerHTML = `<p class="modal-sub">${escapeHtml(at("cNone"))}</p>`;
      return;
    }
    const labels = KIND_LABEL();
    list.innerHTML = coupons.map((c) => `
      <div class="hist-row" data-id="${c.id}">
        <div class="hist-q">
          <b>${escapeHtml(c.code)}</b> — ${escapeHtml(labels[c.kind] || c.kind)}
          ${escapeHtml(couponSummary(c))}
          <span style="color:${c.active ? "var(--green)" : "var(--ink-faint)"}">
            · ${escapeHtml(c.active ? at("cActive") : at("cInactive"))}</span>
        </div>
        <div class="hist-meta">
          ${escapeHtml(c.applies_to)} ·
          ${c.redemptions}/${c.max_redemptions ?? "∞"} ${escapeHtml(at("cUsed"))} ·
          ${escapeHtml(at("cPerUser"))} ${c.max_per_user || "∞"} ·
          ${escapeHtml(at("cMinOrder"))} ${rupees(c.min_amount_paise)} ·
          −₹${rupees(c.total_discount_paise)} ${escapeHtml(at("cUsed"))} ·
          ${c.expires_at ? escapeHtml(c.expires_at.slice(0, 10)) : "—"}
        </div>
        <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
          <input class="ed-value" type="number" min="1" value="${c.value}"
                 style="width:90px;margin-bottom:0" aria-label="${escapeHtml(at("cValue"))}">
          <input class="ed-total" type="number" min="1" value="${c.max_redemptions ?? ""}"
                 placeholder="${escapeHtml(at("cTotalLimit"))}"
                 style="width:120px;margin-bottom:0" aria-label="${escapeHtml(at("cTotalLimit"))}">
          <button class="ghost-btn" data-act="save">${escapeHtml(at("cSave"))}</button>
          <button class="ghost-btn" data-act="toggle">${escapeHtml(
            c.active ? at("cDeactivate") : at("cActivate"))}</button>
          <button class="ghost-btn" data-act="del">${escapeHtml(at("cDelete"))}</button>
        </div>
      </div>`).join("");

    list.querySelectorAll(".hist-row").forEach((row) => {
      const id = row.dataset.id;
      const coupon = coupons.find((c) => String(c.id) === id);
      row.querySelectorAll("button[data-act]").forEach((b) => {
        b.onclick = async () => {
          err.hidden = true;
          if (b.dataset.act === "del") {
            if (!confirm(at("cConfirmDelete"))) return;
            const res = await fetch(`/api/admin/coupons/${id}`, { method: "DELETE" });
            if (!res.ok) return fail((await res.json()).detail || "Failed.");
          } else {
            const patch = b.dataset.act === "toggle"
              ? { active: !coupon.active }
              : {
                  value: Number(row.querySelector(".ed-value").value),
                  max_redemptions: row.querySelector(".ed-total").value === ""
                    ? null : Number(row.querySelector(".ed-total").value),
                };
            const res = await fetch(`/api/admin/coupons/${id}`, {
              method: "PATCH", headers: { "Content-Type": "application/json" },
              body: JSON.stringify(patch),
            });
            if (!res.ok) return fail((await res.json()).detail || "Failed.");
          }
          await refresh();
        };
      });
    });
  }

  const num = (sel, fallback = null) => {
    const raw = back.querySelector(sel).value.trim();
    return raw === "" ? fallback : Number(raw);
  };

  back.querySelector("#nc-create").onclick = async () => {
    err.hidden = true;
    const maxOff = num("#nc-max");
    const body = {
      code: back.querySelector("#nc-code").value.trim().toUpperCase(),
      description: back.querySelector("#nc-desc").value.trim(),
      kind: back.querySelector("#nc-kind").value,
      value: num("#nc-value", 0),
      min_amount_paise: Math.round(num("#nc-min", 0) * 100),
      max_discount_paise: maxOff === null ? null : Math.round(maxOff * 100),
      applies_to: back.querySelector("#nc-applies").value,
      max_redemptions: num("#nc-total"),
      max_per_user: num("#nc-user", 1),
      expires_at: back.querySelector("#nc-expires").value.trim() || null,
    };
    const res = await fetch("/api/admin/coupons", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) return fail((await res.json()).detail || "Failed.");
    back.querySelector("#nc-code").value = "";
    await refresh();
  };

  refresh();
}

/* ---------- toast ---------- */
function toast(message, bad = false) {
  document.querySelector(".toast")?.remove();
  const el = document.createElement("div");
  el.className = "toast" + (bad ? " bad" : "");
  el.textContent = message;
  document.body.append(el);
  setTimeout(() => el.classList.add("in"), 10);
  setTimeout(() => { el.classList.remove("in"); setTimeout(() => el.remove(), 300); }, 4200);
}

/* Called by app.js when /api/ask returns 401 or 402. */
function handleAskRejection(status, detail, question) {
  acct.pendingQuestion = question;
  if (status === 401) { openSignIn(); return true; }
  if (status === 402) {
    if (acct.user) acct.user.credits = 0;
    renderAccountBar();
    openStore(true);
    return true;
  }
  return false;
}

loadAccount();
