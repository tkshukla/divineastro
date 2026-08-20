"""Legal and policy pages.

Every Indian payment gateway checks for these before activating a live account:
Terms, Privacy, Refund/Cancellation, and a reachable Contact page with a real
address. They are served from here so the wording lives in version control
next to the behaviour it describes.

**These are a working draft, not legal advice.** Have a lawyer read them before
you go live — particularly the refund terms and the astrology disclaimer, which
are the two that actually get tested.
"""

from __future__ import annotations

import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

BRAND = os.environ.get("ASTRO_BRAND", "Divine Astro")
SITE = os.environ.get("ASTRO_SITE_URL", "https://divineastro.org")
EMAIL = os.environ.get("ASTRO_SUPPORT_EMAIL", "support@divineastro.org")
LEGAL_NAME = os.environ.get(
    "ASTRO_LEGAL_NAME", "Yavi Info Solutions and Consultants")
ADDRESS = os.environ.get(
    "ASTRO_ADDRESS", "B1-1402 Leisure Park, Greater Noida, Uttar Pradesh, India")
PHONE = os.environ.get("ASTRO_SUPPORT_PHONE", "+91 87226 23794")

# Statutory registrations. Each is rendered only when set, so an unfilled value
# never shows a blank row or a placeholder to a customer or an underwriter.
UDYAM = os.environ.get("ASTRO_UDYAM_NUMBER", "")
UDYAM_DATE = os.environ.get("ASTRO_UDYAM_DATE", "")
UDYAM_TYPE = os.environ.get("ASTRO_UDYAM_TYPE", "")      # Micro | Small | Medium
GSTIN = os.environ.get("ASTRO_GSTIN", "")
PAN = os.environ.get("ASTRO_PAN", "")


def _registration_items() -> list[tuple[str, str]]:
    """Whichever statutory registrations are configured, in a sensible order."""
    items: list[tuple[str, str]] = []
    if UDYAM:
        value = UDYAM + (f" ({UDYAM_TYPE} Enterprise)" if UDYAM_TYPE else "")
        items.append(("Udyam Registration Number", value))
    if UDYAM_DATE:
        items.append(("Udyam Registration Date", UDYAM_DATE))
    if GSTIN:
        items.append(("GSTIN", GSTIN))
    if PAN:
        items.append(("PAN", PAN))
    return items


def _registration_block(heading: str = "Business registration") -> str:
    """A boxed registration panel, or nothing at all when none is configured.

    Rendering nothing rather than an empty box matters: a half-filled
    'Registration: —' row reads worse to a payment underwriter than no claim.
    """
    items = _registration_items()
    if not items:
        return ""
    rows = "".join(f"<p><strong>{k}</strong><br/>{v}</p>" for k, v in items)
    return f'<h2>{heading}</h2><div class="box">{rows}</div>'


def registration_inline() -> str:
    """One-line form for the site footer."""
    return " · ".join(f"{k}: {v}" for k, v in _registration_items())
ASTROLOGER = os.environ.get("ASTRO_ASTROLOGER", "Pandit Shukla")
TURNAROUND = os.environ.get("ASTRO_TURNAROUND_DAYS", "10")
SOURCE_URL = os.environ.get("ASTRO_SOURCE_URL", "")

_SHELL = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title} — {brand}</title>
<link rel="stylesheet" href="/static/styles.css"/>
<style>
  body {{ overflow: auto; }}
  .legal {{ max-width: 780px; margin: 0 auto; padding: 60px 24px 90px; position: relative; z-index: 1; }}
  .legal h1 {{ font-family: var(--serif); font-weight: 400; font-size: 34px;
               color: var(--gold-soft); margin: 0 0 6px; }}
  .legal .updated {{ color: var(--ink-faint); font-size: 12.5px; margin-bottom: 34px;
                     font-family: var(--mono); }}
  .legal h2 {{ font-family: var(--serif); font-weight: 400; font-size: 20px;
               color: var(--gold); margin: 34px 0 10px; }}
  .legal p, .legal li {{ color: var(--ink-dim); font-size: 15px; line-height: 1.75; }}
  .legal li {{ margin-bottom: 8px; }}
  .legal strong {{ color: var(--ink); }}
  .legal a {{ color: var(--cyan); }}
  .legal .back {{ display: inline-block; margin-bottom: 26px; color: var(--ink-faint);
                  font-size: 13px; text-decoration: none; }}
  .legal .back:hover {{ color: var(--gold); }}
  .legal .box {{ border: 1px solid var(--line); border-radius: 14px; padding: 18px 20px;
                 background: rgba(8,10,24,0.5); margin: 20px 0; }}
</style></head>
<body>
<div class="legal">
  <a class="back" href="/">&larr; {brand}</a>
  <h1>{title}</h1>
  <p class="updated">Last updated: {updated}</p>
  {body}
</div></body></html>"""

UPDATED = "16 August 2026"


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(_SHELL.format(
        title=title, brand=BRAND, updated=UPDATED, body=body))


DISCLAIMER = f"""
<div class="box">
  <p><strong>Please read this first.</strong> {BRAND} provides astrological
  readings for guidance, reflection and entertainment. Astrology is not a
  science, and nothing on this site is a prediction of fact.</p>
  <p>Our readings are <strong>not</strong> medical, legal, financial,
  psychiatric or matrimonial advice, and must not be used in place of a
  qualified professional. If you are unwell, in distress, or making a decision
  with real consequences, please consult someone qualified to help.</p>
</div>"""


@router.get("/api/site")
def site_details() -> dict:
    """Business details for the public footer.

    Served from the same constants as the legal pages, so the footer can never
    drift out of step with Terms and Contact.
    """
    return {
        "brand": BRAND,
        "legal_name": LEGAL_NAME,
        "address": ADDRESS,
        "email": EMAIL,
        "phone": PHONE,
        "registrations": [{"label": k, "value": v} for k, v in _registration_items()],
        "registration_line": registration_inline(),
    }


@router.get("/terms", response_class=HTMLResponse)
def terms() -> HTMLResponse:
    return _page("Terms of Service", f"""
{DISCLAIMER}
<h2>1. Who we are</h2>
<p>{BRAND} ("we", "us") is operated by {LEGAL_NAME}, {ADDRESS}. You can reach us
at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
{_registration_block()}

<h2>2. Your account</h2>
<p>You sign in using a Google, Microsoft or Apple account. You are responsible
for keeping that account secure. You must be at least 18 years old to buy
anything from us. One person, one account — creating multiple accounts to claim
the free question allowance more than once may result in suspension.</p>

<h2>3. Questions and credits</h2>
<ul>
  <li>New accounts receive a number of <strong>free questions</strong> as a
      trial. The current allowance is shown when you sign in.</li>
  <li>Further questions are bought as <strong>credit packs</strong>. One
      question consumes one credit.</li>
  <li>A credit is deducted only when an answer is successfully produced. If our
      system fails, you are not charged.</li>
  <li>Credits are tied to your account, do not expire, and cannot be
      transferred or exchanged for cash.</li>
</ul>

<h2>4. Hand-written kundali</h2>
<p>Hand-written kundalis are prepared personally by {ASTROLOGER} and delivered
as a <strong>scanned PDF</strong> to your account. The usual turnaround is about
{TURNAROUND} days from payment. No physical copy is posted unless separately
agreed in writing.</p>

<h2>5. Accuracy of your birth details</h2>
<p>A chart is only as good as the birth data behind it. You are responsible for
the accuracy of the date, time and place you enter. An incorrect birth time
changes the ascendant and every house-based judgement, and is not grounds for a
refund.</p>

<h2>6. Acceptable use</h2>
<p>Do not use {BRAND} to harass anyone, to make decisions on someone else's
behalf without their knowledge, or to seek guidance on unlawful activity. We may
suspend an account that does.</p>

<h2>7. Availability</h2>
<p>We aim to keep the service available but do not guarantee uninterrupted
access. We may change features, prices or pack contents; changes apply to future
purchases, never retrospectively to credits you already hold.</p>

<h2>8. Liability</h2>
<p>To the fullest extent permitted by law, our total liability to you for any
claim is limited to the amount you paid us in the twelve months before the
claim. We are not liable for decisions you take based on a reading.</p>

<h2>9. Governing law</h2>
<p>These terms are governed by the laws of India, and the courts of India shall
have exclusive jurisdiction.</p>
{_source_note()}""")


@router.get("/privacy", response_class=HTMLResponse)
def privacy() -> HTMLResponse:
    return _page("Privacy Policy", f"""
<p>This policy explains what {BRAND} collects, why, and what you can ask us to
do about it. It is written to meet the Digital Personal Data Protection Act,
2023.</p>

<h2>What we collect</h2>
<ul>
  <li><strong>Account details</strong> — your name, email address and profile
      picture, as supplied by Google, Microsoft or Apple when you sign in. We
      never receive your password.</li>
  <li><strong>Birth details</strong> — the date, time and place of birth you
      enter, for yourself or anyone whose chart you save. This is the sensitive
      part, and we treat it as such.</li>
  <li><strong>Your questions and our answers</strong>, so you can revisit and
      download them.</li>
  <li><strong>Payment records</strong> — what you bought, when, and the
      gateway's transaction reference. <strong>We never see or store your card,
      UPI or bank details</strong>; those go directly to the payment gateway.</li>
  <li><strong>Basic technical logs</strong> — IP address and browser, kept
      briefly for security and abuse prevention.</li>
</ul>

<h2>Why we collect it</h2>
<p>To calculate your chart, answer your questions, deliver what you have paid
for, keep an accurate record of credits, and meet our tax and accounting
obligations.</p>

<h2>Who we share it with</h2>
<ul>
  <li><strong>The payment gateway</strong>, to take payment.</li>
  <li><strong>{ASTROLOGER}</strong>, who receives the birth details needed to
      write a hand-written kundali you have ordered — and nothing more.</li>
  <li><strong>Our hosting provider</strong>, which stores the data on our behalf.</li>
</ul>
<p>If you enable AI-assisted narration, the text of your reading is sent to the
selected provider to be rewritten. You choose whether to use it; local-only
narration and plain rule-based wording are always available.
<strong>We do not sell your data, and we do not use your birth details for
advertising.</strong></p>

<h2>How long we keep it</h2>
<p>For as long as your account is open. Delete your account and we remove your
birth profiles, questions and answers within 30 days, except records we are
legally required to keep for tax purposes.</p>

<h2>Your rights</h2>
<p>You may ask us to show you your data, correct it, delete it, or export it.
Write to <a href="mailto:{EMAIL}">{EMAIL}</a> and we will respond within 30
days. You can delete an individual saved birth profile yourself at any time.</p>

<h2>Cookies</h2>
<p>We use one cookie to keep you signed in and one short-lived cookie during
sign-in. We do not use advertising or third-party tracking cookies.</p>

<h2>Children</h2>
<p>{BRAND} is not intended for anyone under 18 and we do not knowingly collect
their data.</p>""")


@router.get("/refund", response_class=HTMLResponse)
def refund() -> HTMLResponse:
    return _page("Refund &amp; Cancellation Policy", f"""
<p>We would rather resolve a problem than argue about it. If something has gone
wrong, write to <a href="mailto:{EMAIL}">{EMAIL}</a> and tell us what happened.</p>

<h2>Question credits</h2>
<ul>
  <li><strong>Unused credits are fully refundable for 7 days</strong> from
      purchase. We refund the unused portion at the price you paid per credit.</li>
  <li>Credits already spent on answered questions are not refundable — the
      service has been delivered.</li>
  <li>If our system fails and no answer is produced, the credit is not
      deducted. If it is deducted in error, tell us and we will restore it.</li>
</ul>

<h2>Hand-written kundali</h2>
<ul>
  <li><strong>Cancel any time before work begins</strong> for a full refund.
      Because each kundali is written by hand for one person, we cannot refund
      once {ASTROLOGER} has started writing.</li>
  <li>If we miss the stated turnaround of about {TURNAROUND} days by more than
      7 days without telling you, you may cancel for a full refund.</li>
  <li>If the delivered scan is illegible or incomplete, we will redo it at no
      charge.</li>
</ul>

<h2>What we cannot refund</h2>
<p>We cannot refund because you disagree with a reading, or because a prediction
did not come to pass. Astrology is interpretive, and this is stated clearly
before you buy.</p>

<h2>How refunds are made</h2>
<p>Refunds go back to the original payment method within <strong>5–7 working
days</strong> of approval. The gateway may take a further few days to show it on
your statement.</p>""")


@router.get("/contact", response_class=HTMLResponse)
def contact() -> HTMLResponse:
    return _page("Contact Us", f"""
<p>We are a small team and we read everything.</p>
<div class="box">
  <p><strong>{LEGAL_NAME}</strong><br/>{ADDRESS}</p>
  <p><strong>Email</strong> <a href="mailto:{EMAIL}">{EMAIL}</a><br/>
     <strong>Phone</strong> {PHONE}</p>
  <p><strong>Astrologer</strong> {ASTROLOGER} — hand-written kundali,
     about {TURNAROUND} days</p>
</div>
{_registration_block("Business registration")}
<h2>Response times</h2>
<p>Email is answered within 2 working days. Refund requests are processed within
5–7 working days of approval.</p>
<h2>Grievance Officer</h2>
<p>For complaints about how your personal data has been handled, write to
<a href="mailto:{EMAIL}">{EMAIL}</a> with "Grievance" in the subject line.</p>""")


def _source_note() -> str:
    """AGPL §13: users of a network service must be offered the source."""
    if not SOURCE_URL:
        return ("<h2>10. Source code</h2><p>This service is built on "
                "AGPL-3.0-licensed software. The complete corresponding source "
                "code is available on request from "
                f'<a href="mailto:{EMAIL}">{EMAIL}</a>.</p>')
    return ("<h2>10. Source code</h2><p>This service is built on AGPL-3.0-licensed "
            "software. In accordance with the licence, the complete corresponding "
            f'source code is published at <a href="{SOURCE_URL}">{SOURCE_URL}</a>.</p>')
