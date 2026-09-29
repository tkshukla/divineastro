# Manual UAT checklist — real-money release

CI (`.github/workflows/ci.yml`) exercises every payment code path against the
`test` and `upi_manual` gateways, but a real PayU transaction cannot be
automated — see DIVASTRO-72. Run this checklist once, by hand, against
production for **any release that touches billing, gateways, or the checkout
flow**, before considering the release done.

## Before you start

- [ ] Confirm production is running the build you're about to test
      (`GET https://divineastro.org/api/health`).
- [ ] Have the PayU merchant dashboard open in another tab.
- [ ] Use a real card/UPI app you control — the smallest priced product in
      the catalogue (currently the cheapest question pack).

## 1. A correctly signed payment grants credit

- [ ] Sign in to <https://divineastro.org>, note the current question credit balance.
- [ ] Buy the cheapest product. Confirm the PayU checkout page opens with no
      browser console errors and no CSP violation reports (devtools → Console
      and Network, filter for `securitypolicyviolation`).
- [ ] Complete the payment with a real card/UPI.
- [ ] Confirm the browser lands back on divineastro.org showing the order as
      paid, and the credit balance increased by the right amount.
- [ ] In the PayU dashboard, find the matching transaction — amount, order id
      and status must match what the site shows.
- [ ] In `/admin` → orders, confirm the order row shows `paid` with the same
      PayU transaction reference.

## 2. A tampered or replayed return grants nothing

- [ ] Copy the return URL the browser landed on after step 1 (or capture it
      from the Network tab before the page redirects).
- [ ] Open it again in a new tab/incognito window.
- [ ] Confirm no second credit grant happens (check the balance again) and
      the order status does not change.
- [ ] If comfortable doing so safely, alter one query parameter (e.g. the
      amount or status field) and load the modified URL. Confirm it is
      rejected (order stays as it was, no credit granted) rather than 500ing
      or silently accepting it.

## 3. Refund/cancel path (if this release touched it)

- [ ] Cancel or refund the test order via the PayU dashboard.
- [ ] Confirm `/admin` reflects the refunded status.
- [ ] Confirm the credit granted in step 1 is not silently left active if the
      release's intent was for a refund to revoke it (check current product
      behaviour before assuming either way — note the actual result here).

## After

- [ ] Record the result (pass/fail, PayU transaction id, order id) as a
      comment on the release's Jira ticket.
- [ ] If anything failed, do not consider the release complete — file a
      ticket and roll back if the failure is in the payment path itself.
