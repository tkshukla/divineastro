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

/* PayU's return is a real browser POST that the server already verified and
   acted on (see /api/payu/return) before redirecting here — unlike
   resumeHostedCheckout() above, there is nothing left to confirm, only the
   result to reflect. */
async function resumePayuReturn() {
  const params = new URLSearchParams(location.search);
  if (!params.has("payu")) return;
  const ok = params.get("payu") === "ok";

  params.delete("payu"); params.delete("order");
  history.replaceState({}, "", location.pathname +
    (params.toString() ? `?${params}` : ""));

  if (!ok) { toast(at("payFailed") || "Payment could not be confirmed.", true); return; }

  try {
    const fresh = await (await fetch("/api/me")).json();
    if (fresh.user) { acct.user = fresh.user; renderAccountBar(); }
  } catch { /* the credit will still show on the next normal load */ }
  toast(`${at("paid")} ✓`);
}

function renderAccountBar() {
  const bar = document.querySelector("#account-bar");
  if (!bar) return;
  document.body.classList.toggle("signed-in", !!acct.user);
  if (typeof renderFreeBadge === "function") renderFreeBadge();
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
function openSignIn(onDone) {
  window.daTrack?.("signin_open");
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
  const freeLine = acct.freeKnown && acct.freeQuestions > 0
    ? ` <b>${escapeHtml(at("signInFree").replace("{n}", acct.freeQuestions))}</b>` : "";

  const back = modal(`
    <h2 class="modal-title">${escapeHtml(at("signInTitle"))}</h2>
    <p class="modal-sub">${escapeHtml(at("signInSub"))}${freeLine}</p>
    <div id="signin-choices">
      <div class="oauth-list" id="oauth-list">
        ${buttons}
        ${emailOn ? `<button type="button" class="oauth-btn" id="email-open">
            ${PROVIDER_MARK.email}<span>${escapeHtml(at("emailContinue"))}</span></button>` : ""}
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

function packCard(p) {
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
    <h4>${escapeHtml(loc(p, "title"))}</h4>
    ${price}
    ${unit}
    <p class="pack-blurb">${escapeHtml(loc(p, "blurb"))}</p>
    <button class="primary buy-btn" data-sku="${p.sku}">${label}</button>
  </div>`;
}

function openStore(outOfCredits = false) {
  if (!acct.user) return openSignIn(() => openStore(outOfCredits));
  window.daTrack?.("store_open", outOfCredits ? "credits" : "browse");
  acct.coupon = null;
  const packs = acct.products.filter((p) => p.kind === "questions");
  const singleReports = acct.products.filter((p) => p.kind === "single_question");
  const lifeBooks = acct.products.filter((p) => p.kind === "kundali_book");
  const kundalis = acct.products.filter((p) => p.kind === "kundali");

  const back = modal(`
    <h2 class="modal-title">${escapeHtml(outOfCredits ? at("outTitle") : at("buyMore"))}</h2>
    <p class="modal-sub">${escapeHtml(outOfCredits ? at("outSub") : "")}</p>
    ${acct.live ? "" : `<p class="test-banner">${escapeHtml(at("testMode"))}</p>`}
    
    <div class="packs" data-kind="questions">${packs.map(packCard).join("")}</div>

    ${singleReports.length ? `
      <h3 class="store-h">${escapeHtml(at("singleQuestionTitle"))}</h3>
      <p class="modal-sub">${escapeHtml(at("singleQuestionSub"))}</p>
      <div class="packs" data-kind="single_question">${singleReports.map(packCard).join("")}</div>
    ` : ""}

    ${lifeBooks.length ? `
      <h3 class="store-h" style="color:var(--gold);">${escapeHtml(at("lifeBookTitle"))}</h3>
      <p class="modal-sub">${escapeHtml(at("lifeBookSub"))}</p>
      <div class="packs" data-kind="kundali_book">${lifeBooks.map(packCard).join("")}</div>
    ` : ""}

    ${kundalis.length ? `
      <h3 class="store-h">${escapeHtml(at("kundaliTitle"))}</h3>
      <p class="modal-sub">${escapeHtml(at("kundaliSub"))}${
        acct.astrologer ? ` ${escapeHtml(acct.astrologer)} · ~${acct.turnaround} days.` : ""}</p>
      <div class="packs" data-kind="kundali">${kundalis.map(packCard).join("")}</div>
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
    const qPacks = back.querySelector('.packs[data-kind="questions"]');
    if (qPacks) qPacks.innerHTML = packs.map(packCard).join("");
    const sqPacks = back.querySelector('.packs[data-kind="single_question"]');
    if (sqPacks) sqPacks.innerHTML = singleReports.map(packCard).join("");
    const lbPacks = back.querySelector('.packs[data-kind="kundali_book"]');
    if (lbPacks) lbPacks.innerHTML = lifeBooks.map(packCard).join("");
    const kPacks = back.querySelector('.packs[data-kind="kundali"]');
    if (kPacks) kPacks.innerHTML = kundalis.map(packCard).join("");
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
function openUpiInstructions(orderId, c, back) {
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
      const res = await fetch("/api/orders/upi-claim", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId, utr_last5: body.querySelector("#utr-last5").value }),
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
  renderAccountBar();
  closeModal();
  if (!data.pending) window.daTrack?.("paid", acct.checkoutSku || "");

  if (data.pending) {
    toast(data.message || "Payment is being confirmed…");
    // The webhook grants a moment later; poll briefly so the balance updates.
    for (let i = 0; i < 10; i++) {
      await new Promise((r) => setTimeout(r, 3000));
      const fresh = await (await fetch("/api/me")).json();
      if (fresh.user && fresh.user.credits !== data.credits) {
        acct.user = fresh.user; renderAccountBar();
        window.daTrack?.("paid", acct.checkoutSku || "");
        toast(`${at("paid")} ✓`); break;
      }
    }
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
        <div class="hist-meta">${escapeHtml(o.created_at)} · ${escapeHtml(statusText(o.status))}${
          o.fulfilment !== "not_applicable" ? " · " + escapeHtml(statusText(o.fulfilment)) : ""}</div>
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
  if (status === 401) {
    // Sign-in reloads the page; keep the question so it is asked when they are back.
    if (typeof parkQuestion === "function") parkQuestion(question);
    openSignIn();
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

loadAccount();
