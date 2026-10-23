/* ============================================================
   GrahDrishti — accounts, credits and checkout.
   Kept separate from app.js so the money path can be read on its own.
   ============================================================ */

const acct = {
  user: null,
  products: [],
  // The free allowance comes from the server (/api/me free_questions) and nothing is
  // shown until it has answered (freeKnown), so this is never a number on screen.
  freeQuestions: 0,
  guestFree: 0,            // DIVASTRO-154: answers a signed-out visitor may get (server setting)
  guestLeft: 0,            // ...and how many THIS browser can still get (0 or 1)
  live: false,
  keyId: "",
  pendingQuestion: null,   // re-fired after a successful purchase
};

/* DIVASTRO-121: the account/checkout strings live in app/static/i18n/<code>.json
   under "acct.<key>" (same files as app.js's, English fallback per key). A few
   values are structured (acct.upiHelpApps is a list, acct.errors / acct.status
   are maps) — a translation keeps the same shape. */
const at = (k) => {
  const key = `acct.${k}`;
  const own = (I18N[state.lang] || {})[key];
  if (own != null && own !== "") return own;
  return I18N.en[key] ?? k;
};


/* A sign-in error as the reader should see it. The email endpoints already answer
   in the sheet's language; the username and phone ones answer in English, so in
   Hindi a known message is translated and any other English one becomes the
   generic Hindi failure line (undefined -> showErr's own fallback). */
function authErr(detail) {
  if (typeof detail !== "string") return undefined;
  if (state.lang !== "hi" || /[ऀ-ॿ]/.test(detail)) return detail;
  const known = (at("errors") || {})[detail];
  if (known) return known;
  const m = /^Password must be at least (\d+) characters\.$/.exec(detail);
  return m ? at("pwMinLen").replace("{n}", m[1]) : undefined;
}
const statusText = (s) => (at("status") || {})[s] || s;

/* ---------- generic modal ---------- */
function modal(html, { dismissable = true } = {}) {
  document.querySelector(".modal-backdrop")?.remove();
  const back = document.createElement("div");
  back.className = "modal-backdrop";
  back.innerHTML = `<div class="modal" role="dialog" aria-modal="true">
    ${dismissable ? `<button class="modal-x" aria-label="${escapeHtml(at("close"))}">&times;</button>` : ""}
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
    acct.freeKnown = typeof data.free_questions === "number";
    acct.guestFree = data.guest_free || 0;
    acct.guestLeft = data.user ? 0 : (data.guest_answers || 0);
  } catch { acct.user = null; }

  try {
    const p = await (await fetch("/api/products", { cache: "no-store" })).json();
    acct.products = p.products || [];
    acct.payment = p.payment || { gateway: "test", live: false };
    acct.live = !!acct.payment.live;
    acct.astrologer = p.astrologer || "";
    acct.turnaround = p.turnaround_days || 10;
    acct.emailMinutes = p.email_answer_minutes || 30;     // DIVASTRO-155: the Starter's promise
    acct.guestSkus = p.guest_checkout || [];               // DIVASTRO-158: buyable without signing in
  } catch { /* catalogue is optional for rendering the app */ }

  try {
    const a = await (await fetch("/api/auth/providers")).json();
    acct.authProviders = a.providers || [];
    acct.devLogin = !!a.dev_login;
  } catch { acct.authProviders = []; }

  renderAccountBar();
  renderPlans();
  // Rescue a chart cast before signing in, THEN list. Order matters: claiming
  // calls loadSavedCharts itself on success, so the panel shows it immediately
  // rather than only on the visit after.
  const chartsReady = claimPendingBirth().finally(loadSavedCharts);

  // A fresh OAuth round-trip lands back here with ?welcome=1
  const params = new URLSearchParams(location.search);
  if (params.has("welcome")) {
    if (params.get("welcome") === "1" && acct.user) {
      toast(`${at("welcome")} ${acct.user.credits} ${at("freeQs")}`);
    }
    // Just signed in: take them where they were going, not to a blank home page.
    if (acct.user && typeof resumeAfterSignIn === "function") chartsReady.then(resumeAfterSignIn);
    params.delete("welcome");
    history.replaceState({}, "", location.pathname +
      (params.toString() ? `?${params}` : ""));
  }

  await resumeHostedCheckout();
  await resumePayuReturn();
  resumeGuestLink();
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
  const guestToken = sessionStorage.getItem("da_pending_guest") || "";   // DIVASTRO-158
  sessionStorage.removeItem("da_pending_guest");

  ["payment_id", "payment_request_id", "payment_status"].forEach((k) => params.delete(k));
  history.replaceState({}, "", location.pathname +
    (params.toString() ? `?${params}` : ""));

  if (guestToken) {
    await guestConfirm(guestToken, { payment_id: paymentId, payment_request_id: requestId });
    return;
  }

  try {
    await confirmPayment(orderId || null, {
      payment_id: paymentId, payment_request_id: requestId,
    });
  } catch (ex) {
    toast(ex.message || "We could not confirm that payment yet.");
  }
}

/* PayU's return is a real browser POST that the server already verified and
   acted on (see /api/payu/return) before redirecting here — unlike
   resumeHostedCheckout() above, there is nothing left to confirm, only the
   result to reflect. */
async function resumePayuReturn() {
  const params = new URLSearchParams(location.search);
  if (!params.has("payu")) return;
  const ok = params.get("payu") === "ok";
  const orderId = Number(params.get("order") || 0);
  // DIVASTRO-158: a guest order. The server adds its token only to a verified return of
  // a paid order, so its presence is what opens the order page (a failed payment has
  // none and ends with the usual "could not be confirmed").
  const guestToken = params.get("gt") || "";

  params.delete("payu"); params.delete("order"); params.delete("gt");
  history.replaceState({}, "", location.pathname +
    (params.toString() ? `?${params}` : ""));

  if (guestToken && !acct.user) {
    if (ok) window.daTrack?.("paid", (guestParked(orderId) || {}).sku || "");
    openGuestOrder(guestToken);
    return;
  }
  if (!ok) { toast(at("payFailed") || "Payment could not be confirmed.", true); return; }

  try {
    const fresh = await (await fetch("/api/me")).json();
    if (fresh.user) { acct.user = fresh.user; renderAccountBar(); }
  } catch { /* the credit will still show on the next normal load */ }
  toast(`${at("paid")} ✓`);

  // The page was reloaded by PayU's redirect: no chart is open any more, so the
  // ready screen offers the saved ones.
  acct.paid = null;
  if (orderId) {
    try {
      const { orders } = await (await fetch("/api/orders")).json();
      const o = (orders || []).find((x) => x.id === orderId);
      if (o && o.status === "paid" && isReportSku(o.sku)) showReportReady(o);
      if (o && o.status === "paid" && o.sku === STARTER_SKU) showStarterBought(o.credits);
    } catch { /* the order is in My orders either way */ }
  }
}

function renderAccountBar() {
  const bar = document.querySelector("#account-bar");
  if (!bar) return;
  document.body.classList.toggle("signed-in", !!acct.user);
  if (typeof renderFreeBadge === "function") renderFreeBadge();
  renderGuestLine();
  if (!acct.user) {
    bar.innerHTML = `<button class="ghost-btn" id="btn-signin">${escapeHtml(at("signIn"))}</button>`;
    bar.querySelector("#btn-signin").onclick = () => openSignIn();
    return;
  }
  const c = acct.user.credits;
  bar.innerHTML = `
    <button class="credit-pill${c <= 2 ? " low" : ""}" id="btn-credits"
            aria-label="${c} ${escapeHtml(at("credits"))}">
      <b>${c}</b>
      <span class="pl-full">${escapeHtml(at("credits"))}</span><span class="pl-short">${escapeHtml(at("creditsShort"))}</span>
    </button>
    ${acct.user.email_credits > 0 ? `<button class="mail-pill" id="btn-mail"
      aria-label="${escapeHtml(at("emailCredits").replace("{n}", acct.user.email_credits))}"
      title="${escapeHtml(at("emailCredits").replace("{n}", acct.user.email_credits))}">&#9993; <b>${acct.user.email_credits}</b></button>` : ""}
    <button class="ghost-btn" id="btn-buy">${escapeHtml(at("buyMore"))}</button>
    <div class="acct-menu">
      <!-- The caret matters: without it this reads as a label, and customers
           could not find Sign out or the admin panel hidden behind it. -->
      <button class="ghost-btn has-menu" id="btn-acct" aria-haspopup="menu" aria-expanded="false">${escapeHtml(
        acct.user.name || (acct.user.email || "").split("@")[0]
        || acct.user.login_label || at("account"))}<span class="caret">&#9662;</span></button>
      <div class="acct-drop" hidden>
        <button data-act="history">${escapeHtml(at("history"))}</button>
        <button data-act="orders">${escapeHtml(at("orders"))}</button>
        <a class="drop-link" href="/feedback">${escapeHtml(at("feedback"))}</a>
        ${acct.user.is_admin
          ? `<button data-act="coupons">${escapeHtml(at("coupons"))}</button>
             <a class="drop-link" href="/admin">${escapeHtml(at("adminPanel"))}</a>` : ""}
        <button class="only-narrow" data-act="theme">${escapeHtml(at("themeToggle"))}</button>
        <button data-act="logout">${escapeHtml(at("signOut"))}</button>
      </div>
    </div>`;
  bar.querySelector("#btn-credits").onclick = () => openStore();
  bar.querySelector("#btn-buy").onclick = () => openStore();
  const mailBtn = bar.querySelector("#btn-mail");
  if (mailBtn) mailBtn.onclick = () => openHistory();
  const drop = bar.querySelector(".acct-drop");
  const acctBtn = bar.querySelector("#btn-acct");
  acctBtn.onclick = () => {
    drop.hidden = !drop.hidden;
    acctBtn.setAttribute("aria-expanded", String(!drop.hidden));
  };
  // Clicking anywhere else closes it, as any menu should. One listener, replaced on
  // each render: the bar is re-rendered on every EN / हिं switch now.
  if (acct.closeMenuOnClick) document.removeEventListener("click", acct.closeMenuOnClick);
  acct.closeMenuOnClick = (e) => {
    if (!bar.contains(e.target) && !drop.hidden) {
      drop.hidden = true;
      acctBtn.setAttribute("aria-expanded", "false");
    }
  };
  document.addEventListener("click", acct.closeMenuOnClick);
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
      } else if (b.dataset.act === "theme") {
        // On a 320px phone the header has no room for the theme switch; the same
        // control lives here and simply presses the real one. (The language picker
        // never moves in here: DIVASTRO-121 keeps it visible in the header.)
        document.querySelector("#theme-toggle")?.click();
      }
      else if (b.dataset.act === "history") { openHistory(); }
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
  phone: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18h2"/></svg>`,
  email: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/></svg>`,
  password: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="15" r="4"/><path d="M10.8 12.2 20 3M17 6l3 3M15 8l2 2"/></svg>`,
};

/* The sheet offers every way in side by side: the redirect providers (Google…),
   a code by email when the server advertises "email" (mail is configured),
   phone by SMS code when it advertises "phone", and a username/password
   account — the last needs no configuration, so it is always there. The "first
   N free" line uses the number /api/me reported (acct.freeQuestions), and is left
   out until the server has said it, exactly like the home page's free badge. */
/* ctx "ask": opened because a signed-out visitor just sent a question (DIVASTRO-129).
   They are mid-task, so say the question is kept, and put the email-code route first:
   it needs no redirect and no password, and the parked question is asked on return. */
function openSignIn(onDone, ctx) {
  window.daTrack?.("signin_open", ctx || "");
  acct.afterLogin = onDone || null;
  const provs = acct.authProviders || [];
  // Inline providers complete inside this sheet; only the rest are redirects.
  const buttons = provs.filter((p) => !p.inline).map((p) => `
    <button class="oauth-btn" data-provider="${escapeHtml(p.key)}">
      ${PROVIDER_MARK[p.key] || ""}
      <span>${escapeHtml(at("continueWith"))} ${escapeHtml(p.label)}</span>
    </button>`).join("");
  const phoneOn = provs.some((p) => p.key === "phone");
  const emailOn = provs.some((p) => p.key === "email");
  const asking = ctx === "ask";
  // DIVASTRO-154: the question after a guest's free answer. The title then says what
  // signing in gets them ("Sign in to keep asking — N more questions free").
  const keepAsking = asking && guestAnswerUsed() && acct.freeKnown && acct.freeQuestions > 0;
  const freeLine = acct.freeKnown && acct.freeQuestions > 0 && !keepAsking
    ? ` <b>${escapeHtml(at("signInFree").replace("{n}", acct.freeQuestions))}</b>` : "";
  const title = keepAsking ? at("signInKeepTitle").replace("{n}", acct.freeQuestions)
    : at(asking ? "signInAskTitle" : "signInTitle");

  // DIVASTRO-158: after the free answer (or the sign-up card under it), the Starter can be
  // bought right here with only an email address; signing in stays below as the alternative.
  // Not before the visitor has read an answer: a first question is never met with a price.
  const gp = (asking || ctx === "guest") && guestAnswerUsed() && state.sessionId
    ? guestProduct(STARTER_SKU) : null;
  const guestPay = gp ? `<div class="guest-pay-offer">
      <p class="guest-pay-line"><b>${escapeHtml(at("starterTitle"))}</b> · ${money(gp.rupees)}</p>
      <button type="button" class="primary" id="guest-pay-open">${escapeHtml(at("guestPayBtn")).replace("{price}", money(gp.rupees))}</button>
    </div>
    <p class="signin-or"><span>${escapeHtml(at("orDivider"))}</span></p>` : "";
  const emailBtn = emailOn ? `<button type="button" class="oauth-btn${asking ? " primary-choice" : ""}" id="email-open">
            ${PROVIDER_MARK.email}<span>${escapeHtml(at("emailContinue"))}</span></button>` : "";
  const back = modal(`
    <h2 class="modal-title">${escapeHtml(title)}</h2>
    <p class="modal-sub">${escapeHtml(at(asking ? "signInAskSub" : "signInSub"))}${freeLine}</p>
    <div id="signin-choices">
      ${guestPay}
      <div class="oauth-list" id="oauth-list">
        ${asking ? emailBtn : ""}
        ${buttons}
        ${asking ? "" : emailBtn}
        ${phoneOn ? `<button type="button" class="oauth-btn" id="phone-open">
            ${PROVIDER_MARK.phone}<span>${escapeHtml(at("phoneContinue"))}</span></button>` : ""}
        ${acct.devLogin ? `<button class="oauth-btn dev" data-provider="dev">
            ${PROVIDER_MARK.dev}<span>${escapeHtml(at("devLogin"))}</span></button>` : ""}
      </div>
      ${buttons || emailOn || phoneOn || acct.devLogin
        ? `<p class="signin-or"><span>${escapeHtml(at("orDivider"))}</span></p>` : ""}
      <div class="oauth-list">
        <button type="button" class="oauth-btn" id="toggle-password-auth">
          ${PROVIDER_MARK.password}<span>${escapeHtml(at("orUsername"))}</span></button>
      </div>
      <button type="button" class="link-btn" id="toggle-password-login">${escapeHtml(at("haveOneLogIn"))}</button>
    </div>
    <div id="password-auth" hidden>
      <div class="field">
        <label for="pa-username">${escapeHtml(at("usernameLabel"))}</label>
        <input id="pa-username" type="text" autocomplete="username" />
      </div>
      <div class="field">
        <label for="pa-password">${escapeHtml(at("passwordLabel"))}</label>
        <input id="pa-password" type="password" autocomplete="current-password" />
      </div>
      <p class="field-note" id="pa-note">${escapeHtml(at("noRecoveryNote"))}</p>
      <button type="button" class="primary" id="pa-submit">${escapeHtml(at("createAccount"))}</button>
      <button type="button" class="link-btn" id="pa-mode-toggle">${escapeHtml(at("haveAccount"))}</button>
      <button type="button" class="link-btn" id="pa-back">${escapeHtml(at("backToProviders"))}</button>
    </div>
    <div id="phone-auth" hidden>
      <div id="ph-step-number">
        <div class="field">
          <label for="ph-number">${escapeHtml(at("phoneLabel"))}</label>
          <div class="phone-row"><span class="phone-cc">+91</span>
            <input id="ph-number" type="tel" inputmode="tel" autocomplete="tel-national"
                   placeholder="98765 43210" maxlength="16" /></div>
        </div>
        <p class="field-note">${escapeHtml(at("phoneHint"))}</p>
        <button type="button" class="primary" id="ph-send">${escapeHtml(at("phoneSend"))}</button>
      </div>
      <div id="ph-step-code" hidden>
        <p class="field-note" id="ph-sent-to" role="status"></p>
        <div class="field">
          <label for="ph-code">${escapeHtml(at("phoneCodeLabel"))}</label>
          <input id="ph-code" type="text" inputmode="numeric" autocomplete="one-time-code"
                 pattern="[0-9]*" maxlength="6" />
        </div>
        <button type="button" class="primary" id="ph-verify">${escapeHtml(at("phoneVerify"))}</button>
        <button type="button" class="link-btn" id="ph-resend" disabled></button>
        <button type="button" class="link-btn" id="ph-change">${escapeHtml(at("phoneChange"))}</button>
      </div>
      <button type="button" class="link-btn" id="ph-back">${escapeHtml(at("backToProviders"))}</button>
    </div>
    <div id="email-auth" hidden>
      <div id="em-step-address">
        <div class="field">
          <label for="em-address">${escapeHtml(at("emailLabel"))}</label>
          <input id="em-address" type="email" inputmode="email" autocomplete="email"
                 autocapitalize="off" spellcheck="false" placeholder="${escapeHtml(at("emailPlaceholder"))}" maxlength="128" />
        </div>
        <p class="field-note">${escapeHtml(at("emailHint"))}</p>
        <button type="button" class="primary" id="em-send">${escapeHtml(at("emailSend"))}</button>
      </div>
      <div id="em-step-code" hidden>
        <p class="field-note" id="em-sent-to" role="status"></p>
        <div class="field">
          <label for="em-code">${escapeHtml(at("emailCodeLabel"))}</label>
          <input id="em-code" type="text" inputmode="numeric" autocomplete="one-time-code"
                 pattern="[0-9]*" maxlength="6" />
        </div>
        <button type="button" class="primary" id="em-verify">${escapeHtml(at("emailVerify"))}</button>
        <button type="button" class="link-btn" id="em-resend" disabled></button>
        <button type="button" class="link-btn" id="em-change">${escapeHtml(at("emailChange"))}</button>
      </div>
      <button type="button" class="link-btn" id="em-back">${escapeHtml(at("backToProviders"))}</button>
    </div>
    <p class="modal-error" hidden></p>
    <p class="legal-line">${escapeHtml(at("legalLine"))
      .replace("{terms}", `<a href="/terms">${escapeHtml(at("terms"))}</a>`)
      .replace("{privacy}", `<a href="/privacy">${escapeHtml(at("privacy"))}</a>`)}</p>`);

  const errBox = back.querySelector(".modal-error");
  const showErr = (msg) => { errBox.textContent = authErr(msg) || at("signInFailed"); errBox.hidden = false; };
  const choices = back.querySelector("#signin-choices");
  const gpBtn = back.querySelector("#guest-pay-open");
  if (gpBtn) {
    window.daTrack?.("starter_shown", "guest");
    gpBtn.onclick = () => openGuestCheckout(STARTER_SKU, { onSignIn: () => openSignIn(onDone, ctx) });
  }

  back.querySelectorAll(".oauth-btn[data-provider]").forEach((b) => {
    b.onclick = async () => {
      const provider = b.dataset.provider;
      if (provider === "dev") {
        const email = prompt(at("devEmailPrompt"), "dev@example.com");
        if (!email) return;
        const res = await fetch("/api/auth/dev", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        });
        const data = await res.json();
        if (!res.ok) { showErr(data.detail); return; }
        finishInPageSignIn(data, onDone);
        return;
      }
      // Full-page redirect: OAuth cannot complete inside fetch(). A question
      // parked by handleAskRejection survives in localStorage and is asked on return.
      const next = encodeURIComponent(location.pathname + location.search);
      location.href = `/api/auth/${provider}/start?next=${next}`;
    };
  });

  /* ---------- username/password: no identity revealed ---------- */
  let paMode = "register";
  const paBox = back.querySelector("#password-auth");
  const paSubmit = back.querySelector("#pa-submit");
  const paModeToggle = back.querySelector("#pa-mode-toggle");
  const paNote = back.querySelector("#pa-note");

  function renderPaMode() {
    paSubmit.textContent = paMode === "register" ? at("createAccount") : at("logIn");
    paModeToggle.textContent = paMode === "register" ? at("haveAccount") : at("needAccount");
    paNote.hidden = paMode !== "register";
    back.querySelector("#pa-password").autocomplete =
      paMode === "register" ? "new-password" : "current-password";
  }
  const openPassword = (mode) => {
    paMode = mode; renderPaMode();
    choices.hidden = true; paBox.hidden = false; errBox.hidden = true;
    back.querySelector("#pa-username").focus();
  };
  back.querySelector("#toggle-password-auth").onclick = () => openPassword("register");
  back.querySelector("#toggle-password-login").onclick = () => openPassword("login");
  back.querySelector("#pa-back").onclick = () => {
    paBox.hidden = true; choices.hidden = false; errBox.hidden = true;
  };
  paModeToggle.onclick = () => {
    paMode = paMode === "register" ? "login" : "register";
    renderPaMode();
  };
  paSubmit.onclick = async () => {
    const username = back.querySelector("#pa-username").value.trim();
    const password = back.querySelector("#pa-password").value;
    errBox.hidden = true;
    if (!username || !password) { showErr(`${at("usernameLabel")} / ${at("passwordLabel")}`); return; }
    const url = paMode === "register" ? "/api/auth/register" : "/api/auth/login";
    const res = await fetch(url, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) { showErr(data.detail); return; }
    finishInPageSignIn(data, onDone);
  };

  /* ---------- one-time codes: email, and phone by SMS (only when advertised) ----------
     Both are the same two steps — an address, then the 6-digit code sent to
     it — against the same server machinery (app/otp.py), so they share one
     wiring and differ only in ids, wording and endpoint. */
  if (emailOn) {
    wireCodeSignIn(back, showErr, choices, onDone, {
      p: "em", open: "#email-open", box: "#email-auth", first: "address",
      api: "/api/auth/email", field: "email", k: "email",
      need: "emailNeedAddress", sentTo: (d) => at("emailSentTo").replace("{e}", d.email),
    });
  }
  if (phoneOn) {
    wireCodeSignIn(back, showErr, choices, onDone, {
      p: "ph", open: "#phone-open", box: "#phone-auth", first: "number",
      api: "/api/auth/phone", field: "number", k: "phone",
      need: "phoneNeedNumber", sentTo: (d) => at("phoneSentTo").replace("{n}", d.number),
    });
  }
}

/* The address -> code steps of an in-page code sign-in. `o.p` is the id prefix
   (#<p>-<first>, #<p>-send, #<p>-code, …), `o.k` the i18n prefix (<k>Send,
   <k>Verify, …), and `o.field` the request key the address travels under. The
   sheet's language goes along too: the email endpoints answer in it (the phone
   ones ignore it). */
function wireCodeSignIn(back, showErr, choices, onDone, o) {
  const $ = (suffix) => back.querySelector(`#${o.p}-${suffix}`);
  const errBox = back.querySelector(".modal-error");
  const box = back.querySelector(o.box);
  const addrIn = $(o.first);
  const codeIn = $("code");
  const sendBtn = $("send");
  const verifyBtn = $("verify");
  const resendBtn = $("resend");
  const t = (key) => at(o.k + key);
  let cooldown = null;

  const showStep = (step) => {
    $(`step-${o.first}`).hidden = step !== "address";
    $("step-code").hidden = step !== "code";
    (step === "address" ? addrIn : codeIn).focus();
  };
  // The server enforces its own cooldown; this only keeps the button honest.
  const startCooldown = (seconds) => {
    clearInterval(cooldown);
    let left = seconds;
    const tick = () => {
      // The sheet may have been closed mid-countdown.
      if (!document.body.contains(resendBtn)) { clearInterval(cooldown); return; }
      resendBtn.disabled = left > 0;
      resendBtn.textContent = left > 0 ? t("ResendIn").replace("{s}", left) : t("Resend");
      left -= 1;
      if (left < 0) clearInterval(cooldown);
    };
    tick();
    cooldown = setInterval(tick, 1000);
  };
  const post = (path, extra) => fetch(`${o.api}/${path}`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ [o.field]: addrIn.value.trim(), lang: state.lang, ...extra }),
  });

  async function sendCode() {
    errBox.hidden = true;
    if (!addrIn.value.trim()) { showErr(at(o.need)); return; }
    sendBtn.disabled = true; sendBtn.textContent = t("Sending");
    try {
      const res = await post("start", {});
      const data = await res.json().catch(() => ({}));
      // 503 is email's "busy" (daily cap): its message already points to
      // Google and the username account, which are one tap away via Back.
      if (!res.ok) { showErr(data.detail); return; }
      $("sent-to").textContent = o.sentTo(data);
      codeIn.value = "";
      showStep("code");
      startCooldown(data.resend_after || 30);
    } catch { showErr(); }
    finally { sendBtn.disabled = false; sendBtn.textContent = t("Send"); }
  }

  back.querySelector(o.open).onclick = () => {
    choices.hidden = true; box.hidden = false; errBox.hidden = true;
    showStep("address");
  };
  $("back").onclick = () => {
    clearInterval(cooldown);
    box.hidden = true; choices.hidden = false; errBox.hidden = true;
  };
  $("change").onclick = () => { errBox.hidden = true; showStep("address"); };
  sendBtn.onclick = sendCode;
  resendBtn.onclick = sendCode;
  addrIn.onkeydown = (e) => { if (e.key === "Enter") sendCode(); };
  codeIn.onkeydown = (e) => { if (e.key === "Enter") verifyBtn.click(); };
  verifyBtn.onclick = async () => {
    const code = codeIn.value.replace(/\D/g, "");
    errBox.hidden = true;
    if (code.length !== 6) { showErr(t("NeedCode")); return; }
    verifyBtn.disabled = true; verifyBtn.textContent = t("Verifying");
    try {
      const res = await post("verify", { code });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) { showErr(data.detail); return; }
      clearInterval(cooldown);
      finishInPageSignIn(data, onDone);
    } catch { showErr(); }
    finally { verifyBtn.disabled = false; verifyBtn.textContent = t("Verify"); }
  };
}

/* Every in-page sign-in (dev, username, email, phone) ends here, so they all behave like
   the OAuth round-trip does on its ?welcome= reload (loadAccount): rescue a chart
   cast while signed out, then either carry on with what the caller wanted, or ask
   the question parked at the sign-in wall. Before this, an in-page sign-in left
   that parked question sitting in localStorage until some later page load. */
function finishInPageSignIn(data, onDone) {
  acct.user = data.user;
  renderAccountBar();
  closeModal();
  if (data.created) toast(`${at("welcome")} ${data.user.credits} ${at("freeQs")}`);
  const ready = (typeof claimPendingBirth === "function" ? claimPendingBirth() : Promise.resolve())
    .finally(loadSavedCharts);
  if (onDone) { onDone(data.user); return; }
  let parked = false;
  try { parked = typeof PENDING_QUESTION !== "undefined" && !!localStorage.getItem(PENDING_QUESTION); }
  catch { /* private mode: nothing was parked */ }
  if (parked && typeof resumeAfterSignIn === "function") ready.then(resumeAfterSignIn);
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

/* A whole number of rupees as people read it: 351, 1,100. (The server sends
   rupees as an integer; paise only ever appear in coupon previews.) */
const money = (r) => `₹${Number(r).toLocaleString("en-IN")}`;
/* Per-question price with two decimals: ₹11.10, ₹7.02, ₹6.51. */
const perQuestion = (p) => `₹${Number(p.per_question).toFixed(2)}`;

/* ---------- DIVASTRO-152: the Diwali offer, shown only while the API says it is live ----------
   Every figure below is read from /api/products, never typed or computed here, except the
   "Save N%" badge, which is arithmetic on the two real prices. When offer.active is false the
   API sends list_amount_paise = null and every helper returns the plain price: no strike, no
   label, no banner. After the end instant nothing in this file needs to change. */
const offerOn = (p) => !!(p && p.offer && p.offer.active
  && Number.isInteger(p.list_amount_paise) && p.list_amount_paise > p.amount_paise);

/* The live offer as the catalogue reports it: { name, ends_at } or null. */
function liveOffer() {
  const p = (acct.products || []).find((x) => x.offer && x.offer.active && x.offer.ends_at);
  return p ? p.offer : null;
}

/* The end date in the page language, in India time (the offer ends at 23:59:59 IST).
   Languages whose Intl data is missing fall back to English. */
function offerDate(iso, long = false) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const lang = state.lang || "en";
  const opts = { day: "numeric", month: lang === "en" && !long ? "short" : "long",
    timeZone: "Asia/Kolkata", numberingSystem: "latn" };
  if (long) opts.year = "numeric";
  for (const loc of lang === "en" ? ["en-IN"] : [`${lang}-IN`, "en-IN"]) {
    try {
      if (loc !== "en-IN" && !Intl.DateTimeFormat.supportedLocalesOf([loc]).length) continue;
      return new Intl.DateTimeFormat(loc, opts).format(d);
    } catch { /* try the next locale */ }
  }
  return String(iso).slice(0, 10);
}

/* "Diwali offer · ends 15 Nov" */
function offerPill() {
  const o = liveOffer();
  return o ? `<span class="offer-pill" data-offer-pill>${escapeHtml(at("offerPill").replace("{date}", offerDate(o.ends_at)))}</span>` : "";
}

/* The one sentence of urgency there is: the real end date. Top of Plans and of the store. */
function offerBanner() {
  const o = liveOffer();
  if (!o) return "";
  return `<p class="offer-banner" data-offer-banner>${offerPill()}
    <span class="offer-banner-text">${escapeHtml(at("offerBanner").replace("{date}", offerDate(o.ends_at, true)))}</span></p>`;
}

/* <s>₹199</s>, with the words a screen reader needs. */
const wasHtml = (paise) => `<s class="was"><span class="sr-only">${escapeHtml(at("wasPrice"))} </span>${money(paise / 100)}</s>`;
/* The price as one run: "₹199 ₹111" (strike + current) while the offer is live, else "₹111". */
function priceHtml(p) {
  return offerOn(p)
    ? `${wasHtml(p.list_amount_paise)}<span class="sr-only">, ${escapeHtml(at("nowPrice"))} </span>${money(p.rupees)}`
    : money(p.rupees);
}
/* "Save 44%": arithmetic on the two real prices. */
function saveBadge(p) {
  if (!offerOn(p)) return "";
  const n = Math.round((1 - p.amount_paise / p.list_amount_paise) * 100);
  return n > 0 ? `<span class="save-badge">${escapeHtml(at("savePct").replace("{n}", n))}</span>` : "";
}
/* "₹11.10 per question", with the regular per-question price struck through while live. */
function perQuestionHtml(p) {
  const was = offerOn(p) && p.list_per_question
    ? `<s class="was"><span class="sr-only">${escapeHtml(at("wasPrice"))} </span>₹${Number(p.list_per_question).toFixed(2)}</s> ` : "";
  return `${was}${perQuestion(p)} ${escapeHtml(at("perQ"))}`;
}

/* The catalogue again, with the clock of the server. Called when the store opens so a page that
   stayed open past the end of the offer shows (and charges) the regular price. */
async function refreshProducts() {
  try {
    const res = await fetch("/api/products", { cache: "no-store" });
    if (!res.ok) return false;
    const p = await res.json();
    const before = JSON.stringify(acct.products);
    acct.products = p.products || acct.products;
    return JSON.stringify(acct.products) !== before;
  } catch { return false; }
}

/* DIVASTRO-151: the four reports that are written by the engine have a free sample PDF
   (/samples/<sku>.pdf, Hindi with ?lang=hi). The hand-written kundali products do not,
   and are not listed here: no automatic sample can exist for them. */
const SAMPLE_SKUS = new Set(["sq_career", "sq_marriage_timing", "sq_wealth_business", "life_book",
  "milan_report"]);
const sampleHref = (sku) => `/samples/${sku}.pdf${state.lang === "hi" ? "?lang=hi" : ""}`;

/* ---------- DIVASTRO-155: the Starter (3 detailed answers by email, once per account) ----------
   The server decides whether this account may still buy it (/api/me user.starter.available:
   not bought, no UPI claim pending, an email address to send to, switched on). */
const STARTER_SKU = "starter_email3";
function starterOffer() {
  const p = productBySku(STARTER_SKU);
  return p && acct.user && acct.user.starter && acct.user.starter.available ? p : null;
}
const starterText = (key) => at(key).replace("{minutes}", acct.emailMinutes || 30);

/* After paying for the Starter: what they now have and what happens next. */
function showStarterBought(n) {
  document.querySelectorAll("#thread .starter-inline").forEach((e) => e.remove());
  const back = modal(`<h2 class="modal-title">${escapeHtml(at("starterBoughtTitle"))}</h2>
    <p class="modal-sub starter-bought">${escapeHtml(starterText("starterBought").replace("{n}", n || 3))}</p>
    <button type="button" class="primary" id="starter-ok">${escapeHtml(at("gotIt"))}</button>`);
  back.querySelector(".modal").classList.add("starter-done");
  back.querySelector("#starter-ok").onclick = () => {
    back.remove();
    // If the paywall interrupted a question, it is asked now: it will be answered by email.
    if (acct.pendingQuestion) {
      const q = acct.pendingQuestion;
      acct.pendingQuestion = null;
      // The unanswered copy the paywall left in the thread: the question is asked again now.
      const last = [...document.querySelectorAll("#thread .msg.user")].pop();
      if (last && last.textContent.trim() === q.trim()) last.remove();
      const box = document.querySelector("#q");
      if (box) { box.value = q; document.querySelector("#ask-form").requestSubmit(); }
    }
  };
}

/* The chat card for a question that will be answered by email (the "queued" event). */
function renderQueuedAnswer(data) {
  if (acct.user) {
    if (typeof data.credits === "number") acct.user.credits = data.credits;
    if (typeof data.email_credits === "number") acct.user.email_credits = data.email_credits;
    renderAccountBar();
  }
  const history = at("history");
  const text = data.email
    ? at("queuedText").replace("{minutes}", data.minutes || acct.emailMinutes || 30)
        .replace("{history}", history)
    : at("queuedNoEmail").replace("{minutes}", data.minutes || acct.emailMinutes || 30)
        .replace("{history}", history);
  const el = document.createElement("div");
  el.className = "msg bot";
  // {email} becomes the address in bold; everything else is escaped text.
  const html = escapeHtml(text).replace("{email}", () => `<b class="q-email">${escapeHtml(data.email || "")}</b>`);
  el.innerHTML = `<div class="bubble queued-card" role="status" data-job="${Number(data.job_id) || ""}">
    <div class="queued-head"><span class="queued-icon" aria-hidden="true">&#9993;</span>
      <b>${escapeHtml(at("queuedTitle"))}</b></div>
    <p class="queued-text">${html}</p>
    ${typeof data.email_credits === "number" ? `<p class="queued-left">${escapeHtml(at("queuedLeft").replace("{n}", data.email_credits))}</p>` : ""}
    <button type="button" class="offer-go queued-open">${escapeHtml(history)}</button>
  </div>`;
  el.querySelector(".queued-open").onclick = () => openHistory();
  document.querySelector("#thread")?.append(el);
  if (typeof scrollThread === "function") scrollThread(true);
  return el;
}

function packCard(p) {
  if (p.kind === "email_answers") return starterCard(p);
  if (p.kind === MILAN_SKU) return milanStoreCard(p);
  const cp = couponFor(p.sku);
  const applied = !!acct.coupon;

  let price = `<div class="pack-price"><span class="pp-line">${priceHtml(p)}</span>${saveBadge(p)}</div>`;
  let unit = p.per_question
    ? `<div class="pack-unit">${perQuestionHtml(p)}</div>` : "";
  let label = `${escapeHtml(at("buy"))} ${money(p.rupees)}`;

  if (cp && cp.discount > 0) {
    price = offerOn(p)
      ? `<div class="pack-price">${wasHtml(p.list_amount_paise)}<span class="sr-only">, ${escapeHtml(at("nowPrice"))} </span>₹${rupees(cp.final)}</div>`
      : `<div class="pack-price">
      <s style="opacity:.45;font-size:.6em">${money(p.rupees)}</s> ₹${rupees(cp.final)}</div>`;
    unit = `<div class="pack-unit" style="color:var(--green)">
      −₹${rupees(cp.discount)} ${escapeHtml(acct.coupon.code)}</div>`;
    label = `${escapeHtml(at("buy"))} ₹${rupees(cp.final)}`;
  } else if (cp && cp.bonus_credits > 0) {
    unit = `<div class="pack-unit" style="color:var(--green)">
      +${cp.bonus_credits} ${escapeHtml(at("bonusQs"))} · ${escapeHtml(acct.coupon.code)}</div>`;
  } else if (applied) {
    unit = `<div class="pack-unit">${escapeHtml(at("couponNotHere"))}</div>`;
  }

  // "Most popular" is the question pack that is flagged (50). The reports, the
  // book and the kundali carry the same catalogue flag, but nothing in the code
  // says they sell best, so they do not wear the label.
  const flagged = p.highlight && p.kind === "questions";
  const focus = acct.storeFocus === p.sku;
  return `<div class="pack${flagged ? " featured" : ""}${focus ? " focus" : ""}${offerOn(p) ? " has-offer" : ""}" data-sku="${p.sku}">
    ${flagged ? `<span class="pack-flag">${escapeHtml(at("popular"))}</span>` : ""}
    <h4>${escapeHtml(loc(p, "title"))}</h4>
    ${price}
    ${unit}
    <p class="pack-blurb">${escapeHtml(loc(p, "blurb"))}</p>
    <button class="primary buy-btn" data-sku="${p.sku}">${label}</button>
    ${SAMPLE_SKUS.has(p.sku) ? `<a class="pack-sample" href="${sampleHref(p.sku)}" target="_blank" rel="noopener"
      data-sample="${p.sku}" title="${escapeHtml(at("sampleNote"))}">${escapeHtml(at("sampleView"))}</a>` : ""}
  </div>`;
}

/* The Starter in the store: one fixed price (never struck through, no coupon), its promise,
   and that it is once per account. */
function starterCard(p) {
  const focus = acct.storeFocus === p.sku;
  return `<div class="pack starter-pack featured${focus ? " focus" : ""}" data-sku="${p.sku}">
    <span class="pack-flag">${escapeHtml(at("starterFlag"))}</span>
    <h4>${escapeHtml(at("starterTitle"))}</h4>
    <div class="pack-price"><span class="pp-line">${money(p.rupees)}</span></div>
    <p class="pack-blurb">${escapeHtml(starterText("starterSub"))}</p>
    <button class="primary buy-btn" data-sku="${p.sku}">${escapeHtml(at("buy"))} ${money(p.rupees)}</button>
  </div>`;
}

/* The line under the store title: what is true of checkout in production. The
   gateway's name is only claimed when a real gateway is configured; in test mode
   the banner below says so instead. */
function trustLine() {
  const pay = acct.payment || {};
  const parts = [];
  if (acct.live) {
    parts.push(escapeHtml(pay.gateway === "upi_manual"
      ? at("trustUpi") : at("trustGateway").replace("{gateway}", pay.label || "")));
  }
  parts.push(`<a href="/refund" target="_blank" rel="noopener">${escapeHtml(at("trustRefund"))}</a>`);
  parts.push(`<a href="/terms" target="_blank" rel="noopener">${escapeHtml(at("terms"))}</a>`);
  return `<p class="store-trust">${parts.join(" · ")}</p>`;
}

/* focusSku: scroll the store to one product and highlight it (the in-app offers
   open the store this way). Its section is opened first if it was collapsed. */
function focusStoreProduct(back, sku) {
  const card = back.querySelector(`.pack[data-sku="${sku}"]`);
  if (!card) return;
  const sec = card.closest("details");
  if (sec) sec.open = true;
  card.classList.add("focus");
  card.scrollIntoView({ block: "center" });
}

function openStore(outOfCredits = false, focusSku = null, from = null) {
  // DIVASTRO-158: a product sold without signing in opens its guest checkout instead.
  if (!acct.user && focusSku && guestProduct(focusSku)) return openGuestCheckout(focusSku);
  if (!acct.user) return openSignIn(() => openStore(outOfCredits, focusSku, from));
  window.daTrack?.("store_open", outOfCredits ? "credits" : "browse");
  acct.coupon = null;
  acct.storeFocus = focusSku || null;
  const packs = acct.products.filter((p) => p.kind === "questions");
  const singleReports = acct.products.filter((p) => p.kind === "single_question");
  const lifeBooks = acct.products.filter((p) => p.kind === "kundali_book");
  const milanReports = acct.products.filter((p) => p.kind === MILAN_SKU);      // DIVASTRO-156
  const kundalis = acct.products.filter((p) => p.kind === "kundali");
  // DIVASTRO-155: the Starter is offered once the free/instant questions are used up (the
  // paywall, or the store opened at 0 left), and leads the sheet then; also when the
  // one-question-left nudge opens the store at it. Otherwise the store is unchanged.
  const outNow = outOfCredits || !(acct.user.credits > 0);
  const starter = outNow || focusSku === STARTER_SKU ? starterOffer() : null;
  // `from` "inline": opened by the Starter line under a free answer (DIVASTRO-157).
  const starterCtx = outOfCredits ? "paywall" : focusSku === STARTER_SKU ? (from || "nudge") : "store";

  // The three ₹111 reports are the easiest first purchase, so they come first;
  // then the question packs, the Life Book and the hand-written kundali. The first
  // two sections start open, the rest fold away so the sheet stays short.
  const sections = [
    { kind: "single_question", items: singleReports, title: at("singleQuestionTitle"),
      sub: at("singleQuestionSub"), open: true },
    { kind: "questions", items: packs, title: at("packsTitle"), sub: "", open: true },
    { kind: MILAN_SKU, items: milanReports, title: at("milanRptSection"), sub: "",
      open: focusSku === MILAN_SKU || !!window.daMilanPair },
    { kind: "kundali_book", items: lifeBooks, title: at("lifeBookTitle"),
      sub: at("lifeBookSub"), open: false },
    { kind: "kundali", items: kundalis, title: at("kundaliTitle"),
      sub: at("kundaliSub") + (acct.astrologer ? ` ${acct.astrologer} · ~${acct.turnaround} days.` : "") + " " + at("hwNote"),
      open: false },
  ].filter((s) => s.items.length);
  if (starter) {
    const sec = { kind: "email_answers", items: [starter], title: at("starterSection"), sub: "", open: true };
    sections.splice(0, 0, sec);
  }

  const sectionHtml = (s) => `
    <details class="store-sec" data-sec="${s.kind}"${s.open || s.items.some((p) => p.sku === focusSku) ? " open" : ""}>
      <summary class="store-h">${escapeHtml(s.title)}</summary>
      ${s.sub ? `<p class="modal-sub">${escapeHtml(s.sub)}</p>` : ""}
      <div class="packs" data-kind="${s.kind}"></div>
    </details>`;

  const back = modal(`
    <h2 class="modal-title">${escapeHtml(outOfCredits ? at("outTitle") : at("buyMore"))}</h2>
    ${outOfCredits ? `<p class="modal-sub">${escapeHtml(at("outSub"))}</p>` : ""}
    <div id="store-offer">${offerBanner()}</div>
    ${trustLine()}
    ${acct.live ? "" : `<p class="test-banner">${escapeHtml(at("testMode"))}</p>`}
    ${sections.map(sectionHtml).join("")}
    <details class="store-sec" data-sec="coupon">
      <summary class="store-h">${escapeHtml(at("couponLabel"))}</summary>
      <div class="coupon-row">
        <input id="coupon-code" type="text" autocomplete="off" spellcheck="false"
               style="flex:1;margin-bottom:0;text-transform:uppercase"
               placeholder="${escapeHtml(at("couponPlaceholder"))}">
        <button class="ghost-btn" id="coupon-apply">${escapeHtml(at("couponApply"))}</button>
        <button class="ghost-btn" id="coupon-clear" hidden>${escapeHtml(at("couponRemove"))}</button>
      </div>
      <p class="coupon-msg modal-sub" style="margin:10px 0 0" hidden></p>
    </details>
    <p class="modal-error" hidden></p>`);
  back.querySelector(".modal").classList.add("store");

  const input = back.querySelector("#coupon-code");
  const applyBtn = back.querySelector("#coupon-apply");
  const clearBtn = back.querySelector("#coupon-clear");
  const msg = back.querySelector(".coupon-msg");

  const repaint = () => {
    const slot = back.querySelector("#store-offer");
    if (slot) slot.innerHTML = offerBanner();
    sections.forEach((s) => {
      const box = back.querySelector(`.packs[data-kind="${s.kind}"]`);
      if (box) box.innerHTML = acct.products.filter((p) => p.kind === s.kind).map(packCard).join("");
    });
    back.querySelectorAll(".buy-btn").forEach((b) => {
      b.onclick = () => {
        if (b.dataset.sku === STARTER_SKU) window.daTrack?.("starter_click", starterCtx);
        if (b.dataset.sku === MILAN_SKU) {
          window.daTrack?.("milan_report_click", "store");
          // DIVASTRO-156: no match on screen, so nothing to write the report for yet: go and match.
          if (b.dataset.open === "milan" || !window.daMilanPair) {
            closeModal();
            if (typeof showStage === "function") showStage("stage-milan");
            return;
          }
          return startCheckout(MILAN_SKU, back, { milan: window.daMilanPair });
        }
        startCheckout(b.dataset.sku, back);
      };
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
  if (focusSku) focusStoreProduct(back, focusSku);
  // (Opened from the nudge: that card already reported starter_shown "nudge"; from the
  // line under an answer: that one reported starter_inline_shown.)
  if (starter && starterCtx !== "nudge" && starterCtx !== "inline") window.daTrack?.("starter_shown", starterCtx);

  // DIVASTRO-152: read the catalogue again with the server's clock. A page left open past the end
  // of the offer then shows the regular prices (what checkout charges) instead of the stale ones.
  // Skipped once a coupon is applied: its preview was priced against the list already on screen.
  refreshProducts().then((changed) => {
    if (!changed || !back.isConnected || acct.coupon) return;
    repaint();
    if (focusSku) focusStoreProduct(back, focusSku);
    renderPlans();
  });
}

async function startCheckout(sku, back, extra = null) {
  const err = back.querySelector(".modal-error");
  const buttons = back.querySelectorAll(".buy-btn");
  buttons.forEach((b) => { b.disabled = true; });
  err.hidden = true;

  // Only send the code for a sku it is actually valid on — the server
  // re-validates regardless and would reject the order outright.
  const body = { sku, ...(extra || {}) };
  if (couponFor(sku)) body.coupon_code = acct.coupon.code;

  try {
    const res = await fetch("/api/orders", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not create the order.");
    acct.checkoutSku = sku;
    window.daTrack?.("checkout_start", sku);

    const c = data.checkout;
    if (c.mode === "test") {
      await confirmPayment(data.order.id, {});
    } else if (c.mode === "razorpay") {
      await openRazorpay(data.order.id, c);
    } else if (c.mode === "cashfree") {
      await openCashfree(data.order.id, c);
    } else if (c.mode === "paytm") {
      await openPaytm(data.order.id, c);
    } else if (c.mode === "payu") {
      // A real hosted form POST — the whole site is left. PayU's own return
      // POST is verified and acted on server-side (see /api/payu/return);
      // resumePayuReturn() in loadAccount() picks the result back up.
      openPayu(c);
      return;
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
function openUpiInstructions(orderId, c, back, claim = null) {
  const body = back.querySelector(".modal") || back;
  body.innerHTML = `
    <button class="modal-x" aria-label="${escapeHtml(at("close"))}">&times;</button>
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
      <label for="utr-last5">${escapeHtml(at("upiUtr"))}</label>
      <input id="utr-last5" required maxlength="5" placeholder="e.g. 78901" autocomplete="off" />
      <details class="utr-help">
        <summary>${escapeHtml(at("upiHelpTitle"))}</summary>
        <ul>
          ${at("upiHelpApps").map(a => `<li><b>${escapeHtml(a.app)}</b> — ${escapeHtml(a.how)}</li>`).join("")}
        </ul>
        <p class="utr-help-fallback">${escapeHtml(at("upiHelpFallback"))}</p>
      </details>
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
      const utr = body.querySelector("#utr-last5").value;
      // DIVASTRO-158: a guest order claims with its token instead of the session.
      const res = claim ? await claim(utr) : await fetch("/api/orders/upi-claim", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId, utr_last5: utr }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error((data.detail && data.detail.message) || data.detail || at("upiFailed"));
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

/* PayU's classic hosted checkout: a real HTML form auto-submitted to their
   payment page, not a fetch. This navigates the whole page away, exactly
   like the Instamojo branch above — nothing here returns. */
function openPayu(c) {
  const form = document.createElement("form");
  form.method = "POST";
  form.action = c.action;
  form.style.display = "none";
  for (const [name, value] of Object.entries(c.fields)) {
    const input = document.createElement("input");
    input.type = "hidden"; input.name = name; input.value = value ?? "";
    form.append(input);
  }
  document.body.append(form);
  form.submit();
}

async function confirmPayment(orderId, payload) {
  const res = await fetch("/api/orders/confirm", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order_id: orderId, payload }),
  });
  const data = await res.json();
  if (!res.ok) { toast(data.detail || at("payFailed"), true); return; }

  acct.user.credits = data.credits;
  if (typeof data.email_credits === "number") acct.user.email_credits = data.email_credits;
  const starterOrder = data.order && data.order.sku === STARTER_SKU;
  if (starterOrder && acct.user.starter) acct.user.starter = { available: false, reason: data.pending ? "pending" : "bought" };
  renderAccountBar();
  closeModal();
  acct.paid = null;          // re-read the paid orders before offering a report again
  if (!data.pending) window.daTrack?.("paid", acct.checkoutSku || "");

  if (data.pending && data.order && isReportSku(data.order.sku)) {
    toast(data.message || "Payment is being confirmed…");
    const settled = await waitForReportOrder(data.order.id);
    if (settled) { toast(`${at("paid")} ✓`); showReportReady(settled); renderDashReports(); }
    return;
  }

  if (data.pending) {
    toast(data.message || "Payment is being confirmed…");
    // The webhook grants a moment later; poll briefly so the balance updates.
    for (let i = 0; i < 10; i++) {
      await new Promise((r) => setTimeout(r, 3000));
      const fresh = await (await fetch("/api/me")).json();
      if (fresh.user && (fresh.user.credits !== data.credits
          || (fresh.user.email_credits || 0) !== (data.email_credits || 0))) {
        acct.user = fresh.user; renderAccountBar();
        window.daTrack?.("paid", acct.checkoutSku || "");
        if (starterOrder) showStarterBought(data.order.credits);
        else toast(`${at("paid")} ✓`);
        break;
      }
    }
    return;
  }

  const added = data.order?.credits || 0;
  if (starterOrder) {
    // Emailed answers, not instant questions: say so, and what happens next.
    showStarterBought(added);
    return;
  }
  toast(`${at("paid")} ${added ? `${added} ${at("added")}` : "✓"}`);

  // A report or the Life Book is delivered here and now, not just listed.
  if (data.order && data.order.status === "paid" && isReportSku(data.order.sku)) {
    showReportReady(data.order);
    renderDashReports();
  }

  // If the customer hit the paywall mid-question, ask it for them now.
  if (acct.pendingQuestion && added) {
    const q = acct.pendingQuestion;
    acct.pendingQuestion = null;
    const box = document.querySelector("#q");
    if (box) { box.value = q; document.querySelector("#ask-form").requestSubmit(); }
  }
}

/* ---------- DIVASTRO-150: delivering what was bought ----------
   A report or the Life Book is a PDF written from one chart, on demand:
   /api/pdf/single-question/<session>?sku=&lang=  and  /api/pdf/life-book/<session>?lang=
   (both answer 402 until the account has paid). Everything here fetches that URL
   itself, rather than navigating to it, so a 402 or a 500 becomes a message the
   person can read and a Try again button, never a blank JSON page. */

const REPORT_SKUS = ["sq_career", "sq_marriage_timing", "sq_wealth_business", "life_book"];
/* DIVASTRO-156: the Kundali Milan report is delivered too, but from the ORDER (both people's
   birth details are on it), not from a chart: see the milan block below. */
const isReportSku = (sku) => REPORT_SKUS.includes(sku) || sku === MILAN_SKU;
/* The server prints reports in English or Hindi; any other app language gets the
   English one, and the panel says so. */
const reportLangFor = (lang) => (lang === "hi" ? "hi" : "en");

function reportUrl(sku, sid, lang) {
  const q = `lang=${encodeURIComponent(lang)}`;
  return sku === "life_book"
    ? `/api/pdf/life-book/${encodeURIComponent(sid)}?${q}`
    : `/api/pdf/single-question/${encodeURIComponent(sid)}?sku=${encodeURIComponent(sku)}&${q}`;
}

function sameBirth(a, b) {
  return !!a && !!b && a.date === b.date && a.time === b.time &&
    Math.abs(a.latitude - b.latitude) < 1e-4 && Math.abs(a.longitude - b.longitude) < 1e-4;
}

/* The charts a report could be written for: the one on screen first, then the
   saved ones (minus the one already on screen). */
function reportCharts() {
  const out = [];
  const open = state.sessionId ? state.currentBirthData : null;
  if (state.sessionId) {
    const meta = state.chart?.meta || {};
    out.push({ open: true, label: meta.name || open?.name || at("rptThisChart"),
               sub: meta.local_time || "", sid: state.sessionId });
  }
  for (const b of state.births || []) {
    if (open && sameBirth(b, open)) continue;
    out.push({ open: false, label: b.label || b.name || b.place,
               sub: `${b.date}${b.time_known ? " · " + b.time : ""}`, birth: b });
  }
  return out;
}

function reportErrorText(status) {
  if (status === 402) return at("rptNotPaid");
  if (status === 401) return at("rptSignIn");
  if (status === 404) return at("rptChartGone");
  if (status >= 500) return at("rptFailed");
  return at("rptFailed");
}

function saveBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.hidden = true;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}

/* Fetch one report and hand it to the browser. Resolves to {ok: true} or
   {ok: false, message}. A chart that is not the open one is cast first, through
   the same castChart the saved-charts list uses. */
async function downloadReport(sku, chart, lang) {
  let sid = chart.sid;
  if (!chart.open) {
    const b = chart.birth;
    try {
      await castChart({
        name: b.name, date: b.date, time: b.time, place: b.place,
        latitude: b.latitude, longitude: b.longitude, timezone: b.timezone,
        zodiac: b.zodiac, ayanamsa: b.ayanamsa, house_system: b.house_system,
        time_known: b.time_known, gender: b.gender || "",
      });
      sid = state.sessionId;
    } catch { return { ok: false, message: at("rptCastFailed") }; }
  }
  let res;
  try { res = await fetch(reportUrl(sku, sid, lang)); }
  catch { return { ok: false, message: at("rptNetwork") }; }
  if (!res.ok) {
    window.daTrack?.("report_download_failed", `${sku}:${res.status}`);
    return { ok: false, status: res.status, message: reportErrorText(res.status) };
  }
  const blob = await res.blob();
  const cd = res.headers.get("Content-Disposition") || "";
  const m = /filename="?([^";]+)"?/i.exec(cd);
  saveBlob(blob, m ? m[1] : `${sku}.pdf`);
  window.daTrack?.("report_downloaded", sku);
  return { ok: true };
}

/* The download panel for one report: a language choice, one row per chart with a
   Download PDF button, and a status line that always says what happened.
   `autostart` downloads at once when there is exactly one chart to use. */
function mountReportDownload(host, sku, { autostart = false } = {}) {
  const charts = reportCharts();
  let lang = reportLangFor(state.lang);
  host.classList.add("rpt-panel");
  host.dataset.sku = sku;

  const paint = () => {
    const note = !["en", "hi"].includes(state.lang)
      ? `<p class="rpt-note">${escapeHtml(at("rptOnlyEnHi"))}</p>` : "";
    const langs = `<div class="rpt-langs" role="group" aria-label="${escapeHtml(at("rptLangLabel"))}">
        ${["en", "hi"].map((c) => `<button type="button" class="ghost-btn rpt-lang" data-lang="${c}"
          aria-pressed="${c === lang}" lang="${c}">${c === "en" ? "English" : "हिन्दी"}</button>`).join("")}
      </div>`;
    let rows;
    if (!charts.length) {
      rows = `<p class="rpt-msg rpt-guide">${escapeHtml(at("rptNoChart"))}</p>
        <button type="button" class="offer-go rpt-new">${escapeHtml(at("rptNewChart"))}</button>`;
    } else {
      rows = `${charts.length > 1 ? `<p class="rpt-pick">${escapeHtml(at("rptPick"))}</p>` : ""}
        ${charts.map((c, i) => `<div class="rpt-row">
          <span class="rpt-chart"><b>${escapeHtml(c.label)}</b>${c.sub ? ` <small>${escapeHtml(c.sub)}</small>` : ""}${
            c.open && charts.length > 1 ? ` <small class="rpt-open">· ${escapeHtml(at("rptOpenNow"))}</small>` : ""}</span>
          <button type="button" class="offer-go rpt-dl" data-i="${i}">${escapeHtml(at("rptDownload"))}</button>
        </div>`).join("")}`;
    }
    host.innerHTML = `${note}${charts.length ? langs : ""}${rows}
      <p class="rpt-msg" role="status" aria-live="polite" hidden></p>`;

    host.querySelectorAll(".rpt-lang").forEach((b) => {
      b.onclick = () => { lang = b.dataset.lang; host.querySelectorAll(".rpt-lang").forEach(
        (x) => x.setAttribute("aria-pressed", String(x === b))); };
    });
    host.querySelector(".rpt-new")?.addEventListener("click", () => {
      closeModal();
      if (typeof showStage === "function") showStage("stage-birth");
    });
    host.querySelectorAll(".rpt-dl").forEach((b) => { b.onclick = () => run(Number(b.dataset.i), b); });
  };

  const say = (text, bad = false) => {
    const el = host.querySelector(".rpt-msg:not(.rpt-guide)");
    if (!el) return;
    el.hidden = !text; el.textContent = text || "";
    el.classList.toggle("rpt-bad", bad);
  };

  async function run(i, btn) {
    const all = [...host.querySelectorAll(".rpt-dl")];
    all.forEach((b) => { b.disabled = true; });
    say(at("rptWorking"));
    const out = await downloadReport(sku, charts[i], lang);
    all.forEach((b) => { b.disabled = false; });
    if (out.ok) {
      say(at("rptDone"));
    } else {
      say(out.message, true);
      if (btn) btn.textContent = at("rptRetry");
      else all[0] && (all[0].textContent = at("rptRetry"));
    }
  }

  paint();
  if (autostart && charts.length === 1) run(0, host.querySelector(".rpt-dl"));
}

/* Right after a purchase of a report or the Life Book. */
async function showReportReady(order) {
  if (!order || !isReportSku(order.sku)) return;
  if (order.sku === MILAN_SKU) return showMilanReady(order);
  if (acct.user && !(state.births || []).length) { try { await loadSavedCharts(); } catch { /* none saved */ } }
  const p = productBySku(order.sku);
  const title = p ? loc(p, "title") : order.title;
  const back = modal(`<div class="rpt-ready" data-sku="${escapeHtml(order.sku)}">
      <h2 class="modal-title rpt-ready-title">${escapeHtml(at("rptReadyTitle").replace("{title}", title))}</h2>
      <p class="modal-sub">${escapeHtml(state.sessionId ? at("rptReadyLead") : at("rptReadyNoChart"))}</p>
      <div class="rpt-host"></div>
      <p class="rpt-orders"><button type="button" class="ghost-btn rpt-orders-link">${escapeHtml(at("orders"))}</button></p>
    </div>`);
  window.daTrack?.("report_ready", order.sku);
  mountReportDownload(back.querySelector(".rpt-host"), order.sku);
  back.querySelector(".rpt-orders-link").onclick = () => { closeModal(); openOrders(); };
}

/* ---------- DIVASTRO-156: the detailed Kundali Milan report (₹51) ----------
   Sold under a match result (tools.js calls mountMilanReport with the two people exactly as the
   matching form posted them). The order carries both birth details, so the PDF is written from
   the ORDER: /api/pdf/milan/<order id>?lang=, any time, from My orders; it is also emailed to the
   order's address. Price, struck list price and Save N% come from /api/products only. */
const MILAN_SKU = "milan_report";

/* The two people of the match on screen ({groom, bride, lang}) or null. Set by mountMilanReport. */
window.daMilanPair = window.daMilanPair || null;

function milanPairLabel(pair) {
  const n = [pair?.groom?.name, pair?.bride?.name].map((x) => (x || "").trim()).filter(Boolean);
  return n.join(" & ");
}

/* The report in the store: it can only be bought for a match, so with none on screen its Buy
   button takes the person to Kundali Milan (data-open), where the card under the result sells it. */
function milanStoreCard(p) {
  const focus = acct.storeFocus === p.sku;
  const pair = window.daMilanPair;
  const who = milanPairLabel(pair);
  const action = pair
    ? `${who ? `<p class="pack-unit mr-for">${escapeHtml(at("milanRptForPair").replace("{pair}", who))}</p>` : ""}
       <button class="primary buy-btn" data-sku="${p.sku}">${escapeHtml(at("buy"))} ${money(p.rupees)}</button>`
    : `<p class="pack-unit mr-for">${escapeHtml(at("milanRptStore"))}</p>
       <button class="primary buy-btn" data-sku="${p.sku}" data-open="milan"
         title="${escapeHtml(at("milanRptOpen"))}">${escapeHtml(at("buy"))} ${money(p.rupees)}</button>`;
  return `<div class="pack milan-pack${focus ? " focus" : ""}${offerOn(p) ? " has-offer" : ""}" data-sku="${p.sku}">
    <h4>${escapeHtml(loc(p, "title"))}</h4>
    <div class="pack-price"><span class="pp-line">${priceHtml(p)}</span>${saveBadge(p)}</div>
    <p class="pack-blurb">${escapeHtml(loc(p, "blurb"))}</p>
    ${action}
    <a class="pack-sample" href="${sampleHref(p.sku)}" target="_blank" rel="noopener"
      data-sample="${p.sku}" title="${escapeHtml(at("sampleNote"))}">${escapeHtml(at("sampleView"))}</a>
  </div>`;
}

/* The card under the match result: "Detailed matching report — guna by guna, Manglik dosh,
   compatibility — ₹51" (struck list price while the offer is live), a sample link, and Buy. */
async function mountMilanReport(host, pair) {
  if (!host || !pair) return;
  window.daMilanPair = pair;
  if (!productBySku(MILAN_SKU)) await refreshProducts();
  const p = productBySku(MILAN_SKU);
  if (!p || !host.isConnected) return;
  const mail = acct.user && acct.user.email_deliverable && acct.user.email
    ? ` ${at("milanRptMail").replace("{email}", acct.user.email)}` : "";
  host.innerHTML = `<div class="card milan-rpt" data-sku="${MILAN_SKU}">
      <p class="mr-head"><b>${escapeHtml(at("milanRptTitle"))}</b> — ${escapeHtml(at("milanRptSub"))} —
        <span class="mr-price">${priceHtml(p)}</span>${saveBadge(p)}</p>
      <p class="mr-how">${escapeHtml(at("milanRptHow"))}</p>
      <div class="mr-actions">
        <button type="button" class="primary buy-btn" data-sku="${MILAN_SKU}">${escapeHtml(at("milanRptBuy"))} ${money(p.rupees)}</button>
        <a class="pack-sample" href="${sampleHref(MILAN_SKU)}" target="_blank" rel="noopener"
          data-sample="${MILAN_SKU}" title="${escapeHtml(at("sampleNote"))}">${escapeHtml(at("sampleView"))}</a>
      </div>
      <p class="mr-kept">${escapeHtml(at("milanRptKept") + mail)}</p>
      <p class="modal-error" hidden></p>
    </div>`;
  const card = host.querySelector(".milan-rpt");
  window.daTrack?.("milan_report_shown", "app");
  card.querySelector(".buy-btn").onclick = () => {
    window.daTrack?.("milan_report_click", "app");
    const go = () => startCheckout(MILAN_SKU, card, { milan: pair });
    if (!acct.user) return openSignIn(go, "milan_report");
    go();
  };
}
window.mountMilanReport = mountMilanReport;

/* Fetch the report of one paid order and hand it to the browser: {ok} or {ok: false, message}. */
async function downloadMilan(orderId, lang) {
  let res;
  try { res = await fetch(`/api/pdf/milan/${encodeURIComponent(orderId)}?lang=${encodeURIComponent(lang)}`); }
  catch { return { ok: false, message: at("rptNetwork") }; }
  if (!res.ok) {
    window.daTrack?.("report_download_failed", `${MILAN_SKU}:${res.status}`);
    return { ok: false, status: res.status, message: reportErrorText(res.status) };
  }
  const blob = await res.blob();
  const m = /filename="?([^";]+)"?/i.exec(res.headers.get("Content-Disposition") || "");
  saveBlob(blob, m ? m[1] : "kundali-milan-report.pdf");
  window.daTrack?.("report_downloaded", MILAN_SKU);
  return { ok: true };
}

/* English / हिन्दी and one Download PDF button for one order. */
function mountMilanDownload(host, orderId, { autostart = false } = {}) {
  if (!host) return;
  let lang = reportLangFor(state.lang);
  host.classList.add("rpt-panel");
  host.dataset.sku = MILAN_SKU;
  const note = !["en", "hi"].includes(state.lang) ? `<p class="rpt-note">${escapeHtml(at("rptOnlyEnHi"))}</p>` : "";
  host.innerHTML = `${note}<div class="rpt-langs" role="group" aria-label="${escapeHtml(at("rptLangLabel"))}">
      ${["en", "hi"].map((c) => `<button type="button" class="ghost-btn rpt-lang" data-lang="${c}"
        aria-pressed="${c === lang}" lang="${c}">${c === "en" ? "English" : "हिन्दी"}</button>`).join("")}
    </div>
    <div class="rpt-row"><button type="button" class="offer-go rpt-dl">${escapeHtml(at("rptDownload"))}</button></div>
    <p class="rpt-msg" role="status" aria-live="polite" hidden></p>`;
  const msg = host.querySelector(".rpt-msg");
  const btn = host.querySelector(".rpt-dl");
  host.querySelectorAll(".rpt-lang").forEach((b) => {
    b.onclick = () => { lang = b.dataset.lang; host.querySelectorAll(".rpt-lang").forEach(
      (x) => x.setAttribute("aria-pressed", String(x === b))); };
  });
  const run = async () => {
    btn.disabled = true; msg.hidden = false; msg.classList.remove("rpt-bad"); msg.textContent = at("rptWorking");
    const out = await downloadMilan(orderId, lang);
    btn.disabled = false;
    msg.classList.toggle("rpt-bad", !out.ok);
    msg.textContent = out.ok ? at("rptDone") : out.message;
    if (!out.ok) btn.textContent = at("rptRetry");
  };
  btn.onclick = run;
  if (autostart) run();
}

/* Right after paying for it. */
function showMilanReady(order) {
  const p = productBySku(MILAN_SKU);
  const title = p ? loc(p, "title") : order.title;
  const back = modal(`<div class="rpt-ready" data-sku="${MILAN_SKU}">
      <h2 class="modal-title rpt-ready-title">${escapeHtml(at("rptReadyTitle").replace("{title}", title))}</h2>
      <p class="modal-sub">${escapeHtml(at("milanRptReady"))}${order.pair ? ` <b>${escapeHtml(order.pair)}</b>` : ""}</p>
      <div class="rpt-host"></div>
      <p class="rpt-orders"><button type="button" class="ghost-btn rpt-orders-link">${escapeHtml(at("orders"))}</button></p>
    </div>`);
  window.daTrack?.("report_ready", MILAN_SKU);
  mountMilanDownload(back.querySelector(".rpt-host"), order.id);
  back.querySelector(".rpt-orders-link").onclick = () => { closeModal(); openOrders(); };
}

/* The reports the signed-in person owns (paid orders), in catalogue order. */
async function ownedReports() {
  const paid = await paidSkus();
  return REPORT_SKUS.filter((s) => paid.has(s));
}

/* Dashboard row: "Your reports" with a Download PDF per report owned. Hidden when
   there are none. The dashboard only shows with a chart open, so each button
   downloads for that chart. */
async function renderDashReports() {
  const row = document.getElementById("dash-reports");
  if (!row) return;
  let owned = [];
  try { owned = acct.user ? await ownedReports() : []; } catch { owned = []; }
  if (!owned.length || !state.sessionId) { row.hidden = true; row.innerHTML = ""; return; }
  row.innerHTML = `<h3 class="rpt-yours">${escapeHtml(at("rptYours"))}</h3>
    <div class="rpt-chips">${owned.map((sku) => {
      const p = productBySku(sku);
      return `<button type="button" class="ghost-btn rpt-chip" data-sku="${sku}"
        aria-label="${escapeHtml(`${at("rptDownload")}: ${p ? loc(p, "title") : sku}`)}">
        <span class="rpt-chip-title">${escapeHtml(p ? loc(p, "title") : sku)}</span>
        <span class="rpt-chip-go">${escapeHtml(at("rptDownload"))}</span></button>`;
    }).join("")}</div>
    <p class="rpt-msg" role="status" aria-live="polite" hidden></p>`;
  row.hidden = false;
  row.setAttribute("aria-label", at("rptYours"));
  const msg = row.querySelector(".rpt-msg");
  row.querySelectorAll(".rpt-chip").forEach((b) => {
    b.onclick = async () => {
      const chart = reportCharts().find((c) => c.open);
      if (!chart) return;
      b.disabled = true; msg.hidden = false; msg.classList.remove("rpt-bad"); msg.textContent = at("rptWorking");
      const out = await downloadReport(b.dataset.sku, chart, reportLangFor(state.lang));
      b.disabled = false;
      msg.classList.toggle("rpt-bad", !out.ok);
      msg.textContent = out.ok ? at("rptDone") : out.message;
      if (!out.ok) b.querySelector(".rpt-chip-go").textContent = at("rptRetry");
    };
  });
}

/* A paid report order that was not confirmed in the browser (the gateway's
   webhook settles it later): poll the orders list a few times, then show the
   ready state. */
async function waitForReportOrder(orderId) {
  for (let i = 0; i < 10; i++) {
    await new Promise((r) => setTimeout(r, 3000));
    try {
      const { orders } = await (await fetch("/api/orders")).json();
      const o = (orders || []).find((x) => x.id === orderId);
      if (o && o.status === "paid") { acct.paid = null; return o; }
    } catch { /* keep trying */ }
  }
  return null;
}

/* ---------- history & orders ---------- */
/* A time the person reads in their own clock: "11 Oct, 14:32" (DIVASTRO-155). */
function localTime(iso) {
  const d = new Date(iso);
  if (!iso || Number.isNaN(d.getTime())) return "";
  const lang = state.lang || "en";
  const opts = { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", hour12: false,
    numberingSystem: "latn" };
  for (const loc of lang === "en" ? ["en-IN"] : [`${lang}-IN`, "en-IN"]) {
    try {
      if (loc !== "en-IN" && !Intl.DateTimeFormat.supportedLocalesOf([loc]).length) continue;
      return new Intl.DateTimeFormat(loc, opts).format(d);
    } catch { /* next */ }
  }
  return d.toISOString().slice(0, 16).replace("T", " ");
}

function emailedMeta(e) {
  if (!e) return "";
  if (e.status === "done") return at("histEmailDone").replace("{time}", localTime(e.delivered));
  if (e.status === "failed") return at("histEmailFailed");
  return at("histEmailPending").replace("{time}", localTime(e.due));
}

async function openHistory() {
  const { questions } = await (await fetch("/api/history")).json();
  const row = (q) => {
    const e = q.emailed;
    const meta = e ? `<div class="hist-meta hist-mail" data-mail="${escapeHtml(e.status)}">&#9993; ${escapeHtml(emailedMeta(e))}</div>`
      : `<div class="hist-meta">${escapeHtml(q.asked_at)} · ${escapeHtml(q.verdict || q.topic)}</div>`;
    const read = e && e.status === "done" && q.answer
      ? `<details class="hist-answer"><summary>${escapeHtml(at("histRead"))}</summary>
          <div class="hist-answer-body">${typeof markdown === "function" ? markdown(q.answer) : escapeHtml(q.answer)}</div></details>`
      : "";
    return `
      <div class="hist-row${e ? " emailed" : ""}">
        <div class="hist-q">${escapeHtml(q.question)}</div>
        ${meta}${read}
      </div>`;
  };
  modal(`<h2 class="modal-title">${escapeHtml(at("history"))}</h2>
    <div class="hist">${questions.length ? questions.map(row).join("") : "<p class='modal-sub'>—</p>"}</div>`);
}

async function openOrders() {
  const { orders } = await (await fetch("/api/orders")).json();
  if (acct.user && !(state.births || []).length) { try { await loadSavedCharts(); } catch { /* none saved */ } }
  const rowHtml = (o) => {
    const p = productBySku(o.sku);
    const title = (p ? loc(p, "title") : o.title) + (o.pair ? ` · ${o.pair}` : "");
    const paid = o.status === "paid";
    const hand = o.fulfilment !== "not_applicable";      // a hand-written kundali: an astrologer fulfils it
    const meta = [escapeHtml(o.created_at), escapeHtml(statusText(o.status))];
    let extra = "";
    if (paid && hand) {
      extra = `<div class="hist-meta ord-hand">${escapeHtml(at("orderHandNote").replace("{status}", statusText(o.fulfilment)))}</div>`;
    } else if (paid && o.sku === MILAN_SKU) {
      extra = `<button type="button" class="offer-go ord-milan">${escapeHtml(at("rptDownload"))}</button>
        <div class="ord-host"></div>`;
    } else if (paid && isReportSku(o.sku)) {
      extra = `<button type="button" class="offer-go ord-dl">${escapeHtml(at("rptDownload"))}</button>
        <div class="ord-host"></div>`;
    }
    return `<div class="hist-row ord-row" data-order="${o.id}" data-sku="${escapeHtml(o.sku)}" data-status="${escapeHtml(o.status)}">
        <div class="hist-q">${escapeHtml(title)} — ₹${o.amount}</div>
        <div class="hist-meta">${meta.join(" · ")}</div>${extra}
      </div>`;
  };
  const back = modal(`<h2 class="modal-title">${escapeHtml(at("orders"))}</h2>
    <div class="hist">${orders.length ? orders.map(rowHtml).join("") : "<p class='modal-sub'>—</p>"}</div>`);
  back.querySelectorAll(".ord-row").forEach((row) => {
    const mb = row.querySelector(".ord-milan");
    if (mb) mb.onclick = () => mountMilanDownload(row.querySelector(".ord-host"), Number(row.dataset.order), { autostart: true });
    const btn = row.querySelector(".ord-dl");
    if (!btn) return;
    // Only the chart already on screen is used without asking; any other case
    // (none open, or several to choose from) shows the picker first.
    btn.onclick = () => {
      const charts = reportCharts();
      mountReportDownload(row.querySelector(".ord-host"), row.dataset.sku,
        { autostart: charts.length === 1 && charts[0].open });
    };
  });
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
    // Deleted coupons are kept by the server (history, restore) but managed in
    // the /admin panel's Deleted list — they don't belong in this quick view.
    const coupons = (await res.json()).coupons.filter((c) => !c.deleted);
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
          <input class="ed-value" type="number" min="1"
                 value="${c.kind === "flat" ? c.value / 100 : c.value}"
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
                  value: coupon.kind === "flat"
                    ? Math.round(Number(row.querySelector(".ed-value").value) * 100)
                    : Number(row.querySelector(".ed-value").value),
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

  // Say which unit the number is in — flat is rupees, percent is %, bonus is a count.
  const ncKind = back.querySelector("#nc-kind");
  ncKind.onchange = () => {
    const unit = { percent: " (%)", flat: " (₹)", extra_credits: "" }[ncKind.value] || "";
    back.querySelector('label[for="nc-value"]').textContent = at("cValue") + unit;
  };
  ncKind.onchange();

  back.querySelector("#nc-create").onclick = async () => {
    err.hidden = true;
    const maxOff = num("#nc-max");
    const body = {
      code: back.querySelector("#nc-code").value.trim().toUpperCase(),
      description: back.querySelector("#nc-desc").value.trim(),
      kind: back.querySelector("#nc-kind").value,
      // Flat discounts are held in paise; the field is entered in rupees.
      value: back.querySelector("#nc-kind").value === "flat"
        ? Math.round(num("#nc-value", 0) * 100) : num("#nc-value", 0),
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

/* ---------- plans and in-app offers (DIVASTRO-149) ----------
   Prices were only reachable after sign-in; these put them where the visitor is.

   Plans: the compact section on the home screen, for everyone (signed out too),
   built from the same /api/products list the store uses, so a price can never
   differ between the two.

   Offers: small, quiet cards for signed-in users with questions left. Each is
   dismissible and shown at most once per browser session (sessionStorage), never
   on the sign-in wall, and never at 0 questions left (the paywall opens the store
   by itself then). Tapping one opens the store scrolled to that product. */

const productBySku = (sku) => acct.products.find((p) => p.sku === sku);

/* The topic the ENGINE routed the question to (interpret/topics.py, sent in the
   'analysis' event as result.topic) -> the report that matches it. Any other
   topic gets the Life Book. Nothing here reads the question text. */
const OFFER_REPORT_FOR_TOPIC = { career: "sq_career", love: "sq_marriage_timing", money: "sq_wealth_business" };
const LOW_CREDITS_AT = 3;

const offersSeen = new Set();
try { JSON.parse(sessionStorage.getItem("da_offers") || "[]").forEach((k) => offersSeen.add(k)); }
catch { /* private mode: the offers are then limited to this page load */ }
function markOfferSeen(key) {
  offersSeen.add(key);
  try { sessionStorage.setItem("da_offers", JSON.stringify([...offersSeen])); } catch { /* ignore */ }
}

/* The report and book SKUs this person has already paid for: they are not offered
   again. Fetched once, and again after a purchase. */
async function paidSkus() {
  if (acct.paid) return acct.paid;
  try {
    const { orders } = await (await fetch("/api/orders")).json();
    acct.paid = new Set((orders || []).filter((o) => o.status === "paid").map((o) => o.sku));
  } catch { acct.paid = new Set(); }
  return acct.paid;
}

function offerCard({ key, detail, text, button, focus, priceOf }) {
  const el = document.createElement("div");
  el.className = "offer-card";
  el.setAttribute("role", "note");
  el.dataset.offer = detail;
  // `text` and `button` are templates with an optional {price}; it becomes the price run
  // (struck regular price + current price while the offer is live, DIVASTRO-152).
  const fill = (t, p) => escapeHtml(t).replace("{price}", () => (p ? priceHtml(p) : ""));
  el.innerHTML = `<p class="offer-text">${fill(text, priceOf)}</p>
    <button type="button" class="offer-go">${fill(button, priceOf)}</button>
    <button type="button" class="offer-x" aria-label="${escapeHtml(at("close"))}">&times;</button>`;
  el.querySelector(".offer-go").onclick = () => {
    window.daTrack?.("offer_click", detail);
    el.remove();
    openStore(false, focus);
  };
  el.querySelector(".offer-x").onclick = () => el.remove();
  markOfferSeen(key);
  window.daTrack?.("offer_shown", detail);
  return el;
}

const offerAllowed = () => !!acct.user && acct.user.credits > 0;

/* After an answer has finished streaming. At most one card per answer: the
   "few questions left" nudge when 3 or fewer remain, otherwise the report that
   matches the topic of the question. */
async function maybeOfferAfterAnswer(result, bubble) {
  try {
    // DIVASTRO-157: a free answer carries the Starter line, and then nothing else.
    if (starterInlineAfterAnswer(result, bubble)) return;
    if (!offerAllowed() || !bubble) return;
    const msg = bubble.closest(".msg") || bubble;
    let card = null;

    const left = acct.user.credits;
    const pack = productBySku("q50");
    // DIVASTRO-155: one question left and the Starter still available: it is the next step.
    const starter = starterOffer();
    if (left === 1 && starter && !offersSeen.has("starter_nudge")) {
      card = offerCard({
        key: "starter_nudge", detail: "starter", focus: STARTER_SKU, priceOf: starter,
        text: starterText("offerStarterLow"), button: at("offerStarterBtn"),
      });
      window.daTrack?.("starter_shown", "nudge");
    }
    if (!card && left <= LOW_CREDITS_AT && pack && !offersSeen.has("low_credits")) {
      card = offerCard({
        key: "low_credits", detail: "low_credits", focus: "q50", button: at("buyMore"), priceOf: pack,
        text: at("offerLow").replace("{n}", left).replace("{pack}", loc(pack, "title")),
      });
    }
    if (!card) {
      const sku = OFFER_REPORT_FOR_TOPIC[result?.topic] || "life_book";
      const p = productBySku(sku);
      if (p && !offersSeen.has(sku) && !(await paidSkus()).has(sku)) {
        card = offerCard({
          key: sku, detail: sku, focus: sku, priceOf: p,
          text: at(sku === "life_book" ? "offerBook" : "offerReport").replace("{title}", loc(p, "title")),
          button: at("offerBtn"),
        });
      }
    }
    if (!card) return;
    if (!msg.isConnected || msg.nextElementSibling?.classList.contains("offer-card")) return;
    msg.after(card);
    if (typeof scrollThread === "function") scrollThread();
  } catch (ex) { console.warn("offer:", ex); }
}

/* ---------- DIVASTRO-157: the Starter under a free answer ----------
   One compact line under every answer from the free allowance (and under the guest
   answer), in the words of that question's topic: "Want the full picture on your
   marriage timing? Get 3 detailed answers by email for ₹21." The server decides when
   it is due (result.starter_inline: a free answer, the Starter still buyable) and the
   topic (result.offer_topic, from the engine's routing). Only one is ever on screen:
   the previous one goes whenever a new answer arrives. Tapping it opens the same
   store the other Starter offers open (sign-in first when signed out). */
const STARTER_INLINE_TOPICS = ["marriage", "career", "money", "health", "timing", "general"];

function starterInlineAfterAnswer(result, bubble) {
  document.querySelectorAll("#thread .starter-inline").forEach((e) => e.remove());
  try {
    if (!result || !result.starter_inline || !bubble) return false;
    const p = productBySku(STARTER_SKU);
    if (!p) return false;
    // Bought (or claimed) in this page since the answer was written: not again.
    if (acct.user && !(acct.user.starter && acct.user.starter.available)) return false;
    const topic = STARTER_INLINE_TOPICS.includes(result.offer_topic) ? result.offer_topic : "general";
    const msg = bubble.closest(".msg") || bubble;
    if (!msg.isConnected) return false;
    const el = document.createElement("div");
    el.className = "offer-card starter-inline";
    el.setAttribute("role", "note");
    el.dataset.offer = "starter_inline";
    el.dataset.topic = topic;
    const text = escapeHtml(at(`starterInline_${topic}`)).replace("{price}", () => `<b>${money(p.rupees)}</b>`);
    el.innerHTML = `<p class="offer-text">${text}</p>
      <button type="button" class="offer-go">${escapeHtml(at("offerStarterBtn"))}</button>
      <button type="button" class="offer-x" aria-label="${escapeHtml(at("close"))}">&times;</button>`;
    el.querySelector(".offer-go").onclick = () => {
      window.daTrack?.("starter_inline_click", topic);
      el.remove();
      openStore(false, STARTER_SKU, "inline");
    };
    el.querySelector(".offer-x").onclick = () => el.remove();
    // Under the answer, or under the guest's sign-up line when there is one.
    const after = msg.nextElementSibling?.classList.contains("guest-cta") ? msg.nextElementSibling : msg;
    after.after(el);
    window.daTrack?.("starter_inline_shown", topic);
    if (typeof scrollThread === "function") scrollThread();
    return true;
  } catch (ex) { console.warn("starter line:", ex); return false; }
}

/* After a chart is cast and the dashboard opens: one line about the Life Book. */
async function offerDashboard() {
  try {
    const slot = document.getElementById("dash-offer");
    const p = productBySku("life_book");
    if (!slot || !p || !offerAllowed() || offersSeen.has("life_book")) return;
    if ((await paidSkus()).has("life_book") || slot.querySelector(".offer-card")) return;
    slot.replaceChildren(offerCard({
      key: "life_book", detail: "life_book_dashboard", focus: "life_book", priceOf: p,
      text: at("offerDash").replace("{title}", loc(p, "title")),
      button: at("offerBtn"),
    }));
  } catch (ex) { console.warn("offer:", ex); }
}

/* DIVASTRO-153: the hand-written kundali strip under the Plans cards. The price is the
   lowest kundali product in the catalogue; the sentence is scoped to hand-written readings. */
function handwrittenStrip(page) {
  const ks = acct.products.filter((p) => p.kind === "kundali");
  if (!ks.length) return "";
  const low = ks.reduce((m, p) => (p.rupees < m.rupees ? p : m), ks[0]);
  return `
    <a class="plan-hw" href="${page}#handwritten" data-plans="handwritten">
      <span class="plan-hw-head">${escapeHtml(at("hwFrom")).replace("{price}", () => priceHtml(low))}</span>
      <span class="plan-hw-text">${escapeHtml(at("hwTexts"))}</span>
      <span class="plan-hw-go">${escapeHtml(at("hwLink"))} &rsaquo;</span>
    </a>`;
}

/* The ₹21 Starter at the top of the home Plans section, for whoever can still buy it:
   a signed-out visitor (it opens the pay-without-signing-in sheet) or an account the
   server says may still buy it (/api/me user.starter.available). */
let homeStarterSeen = false;
function homeStarter() {
  const p = acct.user ? starterOffer() : (typeof guestProduct === "function" ? guestProduct(STARTER_SKU) : null);
  if (!p) return "";
  if (!homeStarterSeen) { homeStarterSeen = true; window.daTrack?.("starter_shown", "home"); }
  const btn = acct.user ? at("offerStarterBtn") : at("guestPayBtn").replace("{price}", money(p.rupees));
  return `
    <a class="plan-starter" href="#" data-plans="starter">
      <span class="plan-starter-head">${escapeHtml(at("starterTitle"))} · <b>${money(p.rupees)}</b></span>
      <span class="plan-starter-text">${escapeHtml(starterText("starterSub"))}</span>
      <span class="plan-starter-go">${escapeHtml(btn)} &rsaquo;</span>
    </a>`;
}

/* The home screen's Plans section. */
const PLAN_PICKS = ["sq_career", "q10", "q50", "life_book"];
let plansSeen = false;

function renderPlans() {
  const box = document.getElementById("plans");
  if (!box) return;
  const picks = PLAN_PICKS.map(productBySku).filter(Boolean);
  if (!picks.length) { box.hidden = true; return; }
  const page = `${state.lang === "en" ? "" : "/" + state.lang}/pricing`;
  const line = (p) => (p.kind === "questions" ? perQuestionHtml(p)
    : escapeHtml(p.kind === "kundali_book" ? at("plansBookLine") : at("plansReportLine")));
  box.innerHTML = `
    <h2 class="plans-title" id="plans-title">${escapeHtml(at("plansTitle"))}</h2>
    ${offerBanner()}
    ${acct.freeKnown ? `<p class="plans-free">${escapeHtml(at(acct.guestFree > 0 ? "plansFreeGuest" : "plansFree").replace("{n}", acct.freeQuestions))}</p>` : ""}
    ${homeStarter()}
    <div class="plans-grid">${picks.map((p) => `
      <div class="plan-cell">
      <a class="plan${p.sku === "q50" ? " featured" : ""}${SAMPLE_SKUS.has(p.sku) ? " has-sample" : ""}" href="${page}#${p.sku}" data-plans="${p.sku}">
        ${p.sku === "q50" ? `<span class="plan-flag">${escapeHtml(at("popular"))}</span>` : ""}
        <span class="plan-name">${escapeHtml(loc(p, "title"))}</span>
        <span class="plan-price">${priceHtml(p)}</span>
        ${saveBadge(p)}
        <span class="plan-line">${line(p)}</span>
      </a>${SAMPLE_SKUS.has(p.sku) ? `
      <a class="plan-sample" href="${sampleHref(p.sku)}" target="_blank" rel="noopener" data-sample="${p.sku}"
         title="${escapeHtml(at("sampleNote"))}">${escapeHtml(at("sampleShort"))}</a>` : ""}
      </div>`).join("")}
    </div>
    <a class="plans-all" href="${page}" data-plans="all">${escapeHtml(at("plansAll"))} &rsaquo;</a>${handwrittenStrip(page)}`;
  box.hidden = false;
  box.setAttribute("aria-labelledby", "plans-title");

  if (!box.dataset.wired) {
    box.dataset.wired = "1";
    box.addEventListener("click", (e) => {
      const a = e.target.closest("[data-plans]");
      if (a) window.daTrack?.("plans_click", a.dataset.plans);
      // DIVASTRO-160: the Starter strip opens its own sheet (guest checkout when signed out).
      if (a && a.dataset.plans === "starter") {
        e.preventDefault();
        window.daTrack?.("starter_click", "home");
        openStore(false, STARTER_SKU, "home");
        return;
      }
      // Signed in: the hand-written strip opens the store at that product; signed out: /pricing#handwritten.
      if (a && a.dataset.plans === "handwritten" && acct.user) {
        e.preventDefault();
        openStore(false, (acct.products.find((p) => p.kind === "kundali") || {}).sku || "k3");
      }
    });
    // "Saw the prices": counted once, when the section is actually on screen.
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((entries) => {
        if (plansSeen || !entries.some((x) => x.isIntersecting)) return;
        plansSeen = true;
        io.disconnect();
        window.daTrack?.("pricing_view", "home");
      }, { threshold: 0.4 });
      io.observe(box);
    }
  }
}

/* A tap on any "sample" link is counted (sample_view, detail = the sku). One listener for the
   home Plans section and the store; the link itself opens the PDF in a new tab. */
document.addEventListener("click", (e) => {
  const a = e.target.closest?.("a[data-sample]");
  if (a) window.daTrack?.("sample_view", a.dataset.sample);
});

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

/* ---------- DIVASTRO-154: one answer without signing in ----------
   The server decides (app/guest.py) and says so in /api/me (guest_answers) and on the
   answer itself (result.guest). Nothing here grants anything; it only words it. */
const GUEST_USED = "astro.guestUsed";
const GUEST_ANSWER = "astro.guestAnswer";      // sessionStorage: survives the OAuth round trip
const GUEST_ANSWER_TTL_MS = 2 * 60 * 60 * 1000;

function guestAnswerUsed() {
  if (acct.guestUsed) return true;
  try { return localStorage.getItem(GUEST_USED) === "1"; } catch { return false; }
}

/* "Ask your first question free — no sign-in needed", above the question box. */
function renderGuestLine() {
  const el = document.getElementById("guest-line");
  if (!el) return;
  const show = !acct.user && acct.guestLeft > 0;
  el.textContent = show ? t("guestAskFree") : "";
  el.hidden = !show;
}

/* Under the guest's answer: "Sign up to ask N more free questions". Called by app.js
   once the answer has finished; `text` is what the guest read, kept (this tab only)
   so it is still on screen after a sign-in that leaves the page (Google). */
function guestAfterAnswer(result, bubble, question, text) {
  acct.guestUsed = true;
  acct.guestLeft = 0;
  try { localStorage.setItem(GUEST_USED, "1"); } catch { /* private mode */ }
  try {
    const keep = { q: question, text, at: Date.now(), result: {
      verdict: result.verdict, topic: result.topic, topic_label: result.topic_label, intent: result.intent,
      score: result.score, evidence: result.evidence || [] } };
    sessionStorage.setItem(GUEST_ANSWER, JSON.stringify(keep));
  } catch { /* storage full or blocked: the answer just is not restored */ }
  renderGuestLine();
  const n = result.free_questions ?? acct.freeQuestions;
  if (!bubble || !(n > 0)) return;
  const msg = bubble.closest(".msg") || bubble;
  const el = document.createElement("div");
  el.className = "offer-card guest-cta";
  el.setAttribute("role", "note");
  el.innerHTML = `<p class="offer-text">${escapeHtml(at("guestMore").replace("{n}", n))}</p>
    <button type="button" class="offer-go">${escapeHtml(at("guestSignUp"))}</button>`;
  el.querySelector(".offer-go").onclick = () => openSignIn(null, "guest");
  msg.after(el);
  starterInlineAfterAnswer(result, bubble);      // DIVASTRO-157: under the sign-up line
  if (typeof scrollThread === "function") scrollThread();
}

/* After signing in: the guest's answer, if it is no longer on screen (a full-page
   sign-in reloaded the app). One shot, and only within a couple of hours. */
function restoreGuestAnswer() {
  let v = null;
  try {
    v = JSON.parse(sessionStorage.getItem(GUEST_ANSWER) || "null");
    sessionStorage.removeItem(GUEST_ANSWER);
  } catch { return; }
  if (!v || typeof v.q !== "string" || typeof v.text !== "string"
      || !(Date.now() - Number(v.at) < GUEST_ANSWER_TTL_MS)) return;
  const shown = [...document.querySelectorAll("#thread .msg.user .bubble")].some((b) => b.textContent === v.q);
  if (shown || typeof addUser !== "function") return;
  try {
    addUser(v.q);
    addBot(v.text, v.result || null);
  } catch (ex) { console.warn("guest answer:", ex); }   // never in the way of the parked question
}

/* Called by app.js when /api/ask returns 401 or 402. */
function handleAskRejection(status, detail, question) {
  acct.pendingQuestion = question;
  if (status === 401) {
    // Sign-in reloads the page; keep the question so it is asked when they are back.
    if (typeof parkQuestion === "function") parkQuestion(question);
    openSignIn(null, "ask");
    return true;
  }
  if (status === 402) {
    if (acct.user) acct.user.credits = 0;
    renderAccountBar();
    openStore(true);
    return true;
  }
  return false;
}

/* ---------- DIVASTRO-158: buying without signing in ----------
   A product in /api/products guest_checkout (the Starter) can be paid for with only an
   email address. The server (app/guest_checkout.py) attaches the order to the account
   that address already has, or keeps it under that address until the first sign-in
   with it, and never signs anyone in. After payment the order is reached with its
   signed token (never its id): this tab keeps it for the PayU round trip, PayU's
   verified return carries it, and the buyer is emailed a link with it (?gt=...). */
const GUEST_PARK = "da_guest_order";        // sessionStorage: {token, orderId, sku, q}
const GUEST_EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function guestProduct(sku) {
  if (acct.user || !(acct.guestSkus || []).includes(sku)) return null;
  return productBySku(sku) || null;
}

function guestParked(orderId) {
  try {
    const v = JSON.parse(sessionStorage.getItem(GUEST_PARK) || "null");
    return v && (!orderId || v.orderId === orderId) ? v : null;
  } catch { return null; }
}

/* The server answers {detail: {code, message}}; the code is worded here. */
function guestErrText(detail) {
  const code = detail && typeof detail === "object" ? detail.code : "";
  const words = {
    email: at("guestErrEmail"), typo: at("guestErrTypo").replace("{s}", (detail && detail.s) || ""),
    phone: at("guestErrPhone"), rate: at("guestErrRate"), refused: at("guestErrRefused"),
    unavailable: at("guestErrUnavailable"), gateway: at("guestErrGateway"), chart: at("guestNeedChart"),
    token: at("guestErrToken"), used: at("guestErrUsed"), too_long: at("guestErrTooLong"),
    no_questions: at("guestErrNoQuestions"),
  };
  return words[code] || (typeof detail === "string" ? detail : at("guestErrGeneric"));
}

async function guestPost(url, body) {
  const res = await fetch(url, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  let data = {};
  try { data = await res.json(); } catch { /* not JSON */ }
  if (!res.ok) throw new Error(guestErrText(data.detail));
  return data;
}

/* The sheet: email (required), phone (optional), pay; "Sign in instead" below. */
function openGuestCheckout(sku, { onSignIn = null } = {}) {
  const p = guestProduct(sku);
  if (!p) return openSignIn();
  window.daTrack?.("starter_click", "guest");
  const legal = escapeHtml(at("legalLine"))
    .replace("{terms}", `<a href="/terms" target="_blank" rel="noopener">${escapeHtml(at("terms"))}</a>`)
    .replace("{privacy}", `<a href="/privacy" target="_blank" rel="noopener">${escapeHtml(at("privacy"))}</a>`);
  const needChart = p.kind === "email_answers" && !state.sessionId;
  const back = modal(`
    <h2 class="modal-title">${escapeHtml(at("starterTitle"))}</h2>
    <p class="modal-sub">${escapeHtml(starterText("starterSub"))} <b>${money(p.rupees)}</b></p>
    ${acct.live ? "" : `<p class="test-banner">${escapeHtml(at("testMode"))}</p>`}
    ${needChart ? `<p class="modal-sub">${escapeHtml(at("guestNeedChart"))}</p>
      <button type="button" class="primary" id="gp-chart">${escapeHtml(at("guestMakeChart"))}</button>` : `
    <form id="gp-form" novalidate>
      <div class="field">
        <label for="gp-email">${escapeHtml(at("emailLabel"))}</label>
        <input id="gp-email" type="email" inputmode="email" autocomplete="email" required
               autocapitalize="off" spellcheck="false" maxlength="128" placeholder="${escapeHtml(at("emailPlaceholder"))}" />
      </div>
      <p class="field-note">${escapeHtml(at("guestEmailHint"))}</p>
      <div class="field">
        <label for="gp-phone">${escapeHtml(at("guestPhoneLabel"))}</label>
        <input id="gp-phone" type="tel" inputmode="tel" autocomplete="tel" maxlength="20" />
      </div>
      <button type="submit" class="primary" id="gp-pay">${escapeHtml(at("guestPayBtn")).replace("{price}", money(p.rupees))}</button>
      <p class="modal-error" hidden></p>
    </form>`}
    <p class="signin-or"><span>${escapeHtml(at("orDivider"))}</span></p>
    <button type="button" class="ghost-btn guest-signin" id="gp-signin">${escapeHtml(at("guestSignInInstead"))}</button>
    <p class="legal-line">${legal}</p>`);
  back.querySelector(".modal").classList.add("guest-pay");
  back.querySelector("#gp-signin").onclick = () => (onSignIn ? onSignIn() : openSignIn(null, "guest_pay"));
  const chartBtn = back.querySelector("#gp-chart");
  if (chartBtn) {
    chartBtn.onclick = () => { closeModal(); if (typeof showStage === "function") showStage("stage-birth"); };
    return back;
  }
  const form = back.querySelector("#gp-form");
  const err = form.querySelector(".modal-error");
  const pay = form.querySelector("#gp-pay");
  const showErr = (m) => { err.textContent = m; err.hidden = false; };
  form.onsubmit = async (ev) => {
    ev.preventDefault();
    err.hidden = true;
    const email = form.querySelector("#gp-email").value.trim();
    const phone = form.querySelector("#gp-phone").value.trim();
    if (!GUEST_EMAIL_RE.test(email)) { showErr(at("guestErrEmail")); form.querySelector("#gp-email").focus(); return; }
    if (phone && !/^\+?[0-9\s\-()]{7,20}$/.test(phone)) { showErr(at("guestErrPhone")); return; }
    pay.disabled = true;
    try {
      const data = await guestPost("/api/guest/checkout", {
        sku, email, phone, session_id: state.sessionId || "", lang: state.lang,
      });
      try {
        sessionStorage.setItem(GUEST_PARK, JSON.stringify({
          token: data.token, orderId: data.order.id, sku, q: acct.pendingQuestion || "" }));
      } catch { /* private mode: PayU's return still carries the token */ }
      window.daTrack?.("checkout_start", sku);
      await guestPay(data, back);
    } catch (ex) {
      showErr(ex.message);
      pay.disabled = false;
    }
  };
  setTimeout(() => form.querySelector("#gp-email")?.focus(), 50);
  return back;
}

/* Open the gateway for a guest order (the same modes as startCheckout). */
async function guestPay(data, back) {
  const c = data.checkout;
  const token = data.token;
  if (c.mode === "test") return guestConfirm(token, {});
  if (c.mode === "razorpay") {
    await loadScript("https://checkout.razorpay.com/v1/checkout.js");
    return new Promise((resolve) => {
      const rz = new window.Razorpay({
        key: c.key_id, amount: c.amount, currency: c.currency, name: "Divine Astro",
        order_id: c.order_id, prefill: c.prefill, theme: { color: "#f0c674" },
        handler: async (resp) => { await guestConfirm(token, resp); resolve(); },
        modal: { ondismiss: () => resolve() },
      });
      rz.on("payment.failed", () => toast(at("payFailed"), true));
      rz.open();
    });
  }
  if (c.mode === "cashfree") {
    await loadScript("https://sdk.cashfree.com/js/v3/cashfree.js");
    const cf = window.Cashfree({ mode: c.sandbox ? "sandbox" : "production" });
    await cf.checkout({ paymentSessionId: c.payment_session_id, redirectTarget: "_modal" });
    return guestConfirm(token, { order_id: c.order_id });
  }
  if (c.mode === "payu") { openPayu(c); return; }      // PayU's return lands back on /?payu=...&gt=...
  if (c.mode === "instamojo") {
    sessionStorage.setItem("da_pending_guest", token);
    location.assign(c.url);
    return;
  }
  if (c.mode === "upi_manual") {
    return openUpiInstructions(data.order.id, c, back,
      (utr) => fetch("/api/guest/upi-claim", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, utr_last5: utr }),
      }));
  }
  throw new Error(at("guestErrGateway"));
}

async function guestConfirm(token, payload) {
  try {
    const data = await guestPost("/api/guest/confirm", { token, payload });
    if (data.paid) window.daTrack?.("paid", (data.order && data.order.sku) || "");
    openGuestOrder(token, data);
  } catch (ex) { toast(ex.message, true); }
}

/* The emailed link (/?gt=<token>) opens the order page. */
function resumeGuestLink() {
  const params = new URLSearchParams(location.search);
  const token = params.get("gt");
  if (!token) return;
  params.delete("gt");
  history.replaceState({}, "", location.pathname + (params.toString() ? `?${params}` : ""));
  openGuestOrder(token);
}

/* The order page: payment status, then the questions (up to the number bought) and how
   each one is getting on. Only this order is ever shown; the answers go by email. */
async function openGuestOrder(token, data = null, polls = 0) {
  if (!data) {
    try { data = await guestPost("/api/guest/order", { token }); }
    catch (ex) { toast(ex.message, true); return; }
  }
  const parked = guestParked(data.order && data.order.id) || {};
  const email = data.email || "";
  const mins = data.minutes || acct.emailMinutes || 30;
  const left = data.questions_left || 0;
  const asked = data.questions || [];
  const emailHtml = `<b class="q-email">${escapeHtml(email)}</b>`;
  const fill = (key) => escapeHtml(at(key)).replace("{n}", left).replace("{minutes}", mins)
    .replace("{email}", () => emailHtml);
  const statusOf = (q) => (q.status === "done" ? at("histEmailDone").replace("{time}", localTime(q.delivered))
    : q.status === "failed" ? at("guestQFailed")
      : at("histEmailPending").replace("{time}", localTime(q.due)));
  const fields = [];
  for (let i = 0; i < left; i++) {
    fields.push(`<div class="field">
      <label for="gq-${i}">${escapeHtml(at("guestQLabel")).replace("{i}", i + 1)}</label>
      <textarea id="gq-${i}" class="gq" rows="2" maxlength="1000"
        placeholder="${escapeHtml(at("guestQPlaceholder"))}">${i === 0 && !asked.length ? escapeHtml(parked.q || "") : ""}</textarea>
    </div>`);
  }
  const body = !data.paid ? `
      <h2 class="modal-title">${escapeHtml(at("guestWaitingTitle"))}</h2>
      <p class="modal-sub" role="status">${fill("guestWaiting")}</p>
      <button type="button" class="primary" id="gq-refresh">${escapeHtml(at("guestRefresh"))}</button>`
    : `
      <h2 class="modal-title">${escapeHtml(at(left ? "guestPaidTitle" : "guestSentTitle"))}</h2>
      <p class="modal-sub" role="status">${fill(left ? "guestPaidSub" : "guestSent")}</p>
      ${data.chart && data.chart.name ? `<p class="field-note">${escapeHtml(at("guestChart")).replace("{name}", escapeHtml(data.chart.name))}</p>` : ""}
      ${asked.length ? `<ol class="guest-asked">${asked.map((q) => `<li><span class="gq-text">${escapeHtml(q.question)}</span>
        <span class="gq-status">${escapeHtml(statusOf(q))}</span></li>`).join("")}</ol>` : ""}
      ${left ? `<form id="gq-form">${fields.join("")}
        <button type="submit" class="primary" id="gq-send">${escapeHtml(at("guestSend"))}</button>
        <p class="modal-error" hidden></p></form>` : ""}
      <p class="field-note">${escapeHtml(at("guestLinkNote"))}</p>
      <p class="field-note guest-keep">${fill("guestKeep")}</p>
      <button type="button" class="ghost-btn guest-signin" id="gq-signin">${escapeHtml(at("signIn"))}</button>`;
  const back = modal(body);
  back.querySelector(".modal").classList.add("guest-order");
  const refresh = back.querySelector("#gq-refresh");
  if (refresh) refresh.onclick = () => openGuestOrder(token);
  const signin = back.querySelector("#gq-signin");
  if (signin) signin.onclick = () => openSignIn(null, "guest_order");
  const form = back.querySelector("#gq-form");
  if (form) {
    const err = form.querySelector(".modal-error");
    form.onsubmit = async (ev) => {
      ev.preventDefault();
      err.hidden = true;
      const questions = [...form.querySelectorAll(".gq")].map((t) => t.value.trim()).filter(Boolean);
      if (!questions.length) { err.textContent = at("guestErrNoQuestions"); err.hidden = false; return; }
      const btn = form.querySelector("#gq-send");
      btn.disabled = true;
      try {
        const fresh = await guestPost("/api/guest/questions", { token, questions, lang: state.lang });
        acct.pendingQuestion = null;
        // The question the sign-in sheet parked is asked now: never again after a sign-in.
        if (typeof takeParkedQuestion === "function") takeParkedQuestion();
        try {
          const v = guestParked();
          if (v) { v.q = ""; sessionStorage.setItem(GUEST_PARK, JSON.stringify(v)); }
        } catch { /* ignore */ }
        openGuestOrder(token, fresh);
      } catch (ex) {
        err.textContent = ex.message; err.hidden = false;
        btn.disabled = false;
      }
    };
  }
  // Still being confirmed (a webhook or the UPI check settles it): look again shortly.
  if (!data.paid && data.pending && polls < 24) {
    setTimeout(async () => {
      if (!back.isConnected) return;
      try {
        const fresh = await guestPost("/api/guest/order", { token });
        if (back.isConnected) openGuestOrder(token, fresh, polls + 1);
      } catch { /* the button still works */ }
    }, 5000);
  }
  return back;
}

loadAccount();
