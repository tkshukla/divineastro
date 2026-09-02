"""Single-question paid reports: gating and delivery.

Buy a sq_career report, confirm the PDF is refused before payment, pay for
it (test mode), then confirm the PDF actually generates and is scoped to
the career topic. Also checks that a single-question order is refused
without a birth_id (the report has nowhere to be scoped without one), and
that a different chart's paid order does not unlock this one's PDF.

Requires a running dev server (`.\\run.ps1`) with `ASTRO_GATEWAY=test`.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_single_question
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


BIRTH = {
    "name": "Test Native", "date": "1990-05-15", "time": "14:30",
    "place": "Delhi", "latitude": 28.6139, "longitude": 77.2090,
    "timezone": "Asia/Kolkata", "zodiac": "sidereal", "ayanamsa": "lahiri",
    "house_system": "Whole Sign",
}


def sign_in() -> requests.Session:
    s = requests.Session()
    email = f"sq{random.randint(10000, 99999)}@example.com"
    s.post(f"{BASE}/api/auth/dev", json={"email": email}, timeout=30).raise_for_status()
    return s


def cast_and_save(s: requests.Session, *, date: str = BIRTH["date"]) -> tuple[str, int]:
    """Returns (session_id, birth_id) — a cast chart, saved as a birth profile.

    /api/births deliberately deduplicates identical birth data (so recasting
    the same chart doesn't create a duplicate saved row) — pass a distinct
    `date` when the test actually needs two different charts, or two calls
    with the default date collapse onto the same birth_id.
    """
    payload = {**BIRTH, "date": date}
    chart = s.post(f"{BASE}/api/chart", json=payload, timeout=30)
    chart.raise_for_status()
    sid = chart.json()["session_id"]

    saved = s.post(f"{BASE}/api/births", json={**payload, "label": f"Test {date}"}, timeout=30)
    saved.raise_for_status()
    return sid, saved.json()["birth"]["id"]


def main() -> int:
    print("\n1. Gateway is test mode")
    gw = requests.get(f"{BASE}/api/products", timeout=20).json()["payment"]["gateway"]
    check("active gateway is test", gw == "test", gw)

    print("\n2. A single-question order needs a birth_id")
    buyer = sign_in()
    _sid, birth_id = cast_and_save(buyer)
    no_birth = buyer.post(f"{BASE}/api/orders", json={"sku": "sq_career"}, timeout=30)
    check("order without birth_id is refused", no_birth.status_code == 400, no_birth.text[:160])

    print("\n3. The PDF is refused before payment")
    sid, birth_id = cast_and_save(buyer)
    before = buyer.get(f"{BASE}/api/pdf/single-question/{sid}",
                       params={"sku": "sq_career", "birth_id": birth_id}, timeout=30)
    check("PDF refused (402) before any order exists", before.status_code == 402, str(before.status_code))

    print("\n4. Buy and pay (test mode)")
    order = buyer.post(f"{BASE}/api/orders",
                       json={"sku": "sq_career", "birth_id": birth_id}, timeout=30)
    check("order created", order.status_code == 200, order.text[:160])
    oid = order.json()["order"]["id"]
    check("order carries no question credits (single_question kind)",
          order.json()["order"]["credits"] == 0, str(order.json()["order"]))

    confirm = buyer.post(f"{BASE}/api/orders/confirm",
                         json={"order_id": oid, "payload": {}}, timeout=30).json()
    check("payment confirmed", confirm.get("ok") is True, str(confirm)[:160])

    print("\n5. The PDF now generates and looks like a real PDF")
    after = buyer.get(f"{BASE}/api/pdf/single-question/{sid}",
                      params={"sku": "sq_career", "birth_id": birth_id}, timeout=60)
    check("PDF served (200) after payment", after.status_code == 200, str(after.status_code))
    check("content-type is a PDF", after.headers.get("content-type", "").startswith("application/pdf"),
          after.headers.get("content-type"))
    check("body starts with the PDF magic bytes", after.content[:5] == b"%PDF-", str(after.content[:20]))
    check("a real document was produced, not a stub", len(after.content) > 5000, str(len(after.content)))

    print("\n6. A different, unpaid chart is NOT unlocked by this order")
    other_sid, other_birth_id = cast_and_save(buyer, date="1985-01-01")
    check("the second chart really is a different birth_id",
          other_birth_id != birth_id, f"{other_birth_id} vs {birth_id}")
    blocked = buyer.get(f"{BASE}/api/pdf/single-question/{other_sid}",
                        params={"sku": "sq_career", "birth_id": other_birth_id}, timeout=30)
    check("a second, unpaid chart still gets 402", blocked.status_code == 402, str(blocked.status_code))

    print("\n7. Buying twice does not grant a second PDF for free — "
          "each order is scoped to one birth_id, and a second sku is separately gated")
    unpaid_sku = buyer.get(f"{BASE}/api/pdf/single-question/{sid}",
                           params={"sku": "sq_money", "birth_id": birth_id}, timeout=30)
    check("a different sku on the same paid chart is still gated separately",
          unpaid_sku.status_code == 402, str(unpaid_sku.status_code))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("single-question paid reports — all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
